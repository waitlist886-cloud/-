"""Verify a subset install of TavernWeave skills against the source checkout.

usage: python3 -I tools/verify_tavernweave.py <source repo> <installed skills root> <receipt.json> skill [skill ...]
"""
import hashlib, json, os, re, sys

src, dst, receipt_path, skills = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def files(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root).replace(os.sep, '/')] = p
    return out


manifest = json.load(open(os.path.join(src, 'tavernweave-install-manifest.json'), encoding='utf-8'))
listed = set(manifest['skills'])
ok = True
receipt = {'package': manifest['package'], 'version': manifest['version'],
           'sourceCommit': os.popen(f'git -C "{src}" rev-parse HEAD').read().strip(),
           'manifestSkillCount': manifest['skillCount'], 'installedSkills': {}}

print(f"source {manifest['package']} {manifest['version']}  manifest skills {manifest['skillCount']}")
for s in skills:
    if s not in listed:
        print(f'  !! {s} not in the install manifest'); ok = False
    a, b = files(os.path.join(src, 'skills', s)), files(os.path.join(dst, s))
    missing, extra = sorted(set(a) - set(b)), sorted(set(b) - set(a))
    diff = [r for r in sorted(set(a) & set(b)) if sha(a[r]) != sha(b[r])]
    same = len(set(a) & set(b)) - len(diff)
    print(f'  {s}: {same}/{len(a)} files identical, missing {len(missing)}, extra {len(extra)}, differing {len(diff)}')
    for r in missing[:5] + extra[:5] + diff[:5]:
        print('     ', r)
    ok &= not (missing or extra or diff)
    receipt['installedSkills'][s] = {r: sha(b[r]) for r in sorted(b)}

req = [p for p in manifest['requiredPaths'] if any(p.startswith(f'skills/{s}/') for s in skills)]
req_missing = [p for p in req if not os.path.exists(os.path.join(dst, p[len('skills/'):]))]
print(f'required paths inside the installed skills: {len(req) - len(req_missing)}/{len(req)} present')
ok &= not req_missing

lib = 'consult-tavernweave-library'
if lib in skills:
    lm = json.load(open(os.path.join(dst, lib, 'references', 'library-manifest.json'), encoding='utf-8'))
    good = bad = 0
    for e in lm['documents']:
        p = os.path.join(dst, lib, e['path'])
        if os.path.exists(p) and sha(p) == e['targetHash'] and os.path.getsize(p) == e['bytes']:
            good += 1
        else:
            bad += 1; print('   doc hash mismatch', e['path'])
    for e in lm['assets']:
        p = os.path.join(dst, lib, e['path'])
        if os.path.exists(p) and sha(p) == e['hash'] and os.path.getsize(p) == e['bytes']:
            good += 1
        else:
            bad += 1; print('   asset hash mismatch', e['path'])
    print(f'library-manifest published hashes: {good}/{good + bad} match')
    ok &= bad == 0

# relative links from the installed markdown
link = re.compile(r'\]\((?!https?:|#|mailto:)([^)\s#]+)')
inside, outside, broken = 0, {}, []
for s in skills:
    for r, p in files(os.path.join(dst, s)).items():
        if not r.endswith('.md'):
            continue
        for m in link.finditer(open(p, encoding='utf-8').read()):
            target = os.path.normpath(os.path.join(os.path.dirname(p), m.group(1)))
            rel = os.path.relpath(target, dst).replace(os.sep, '/')
            top = rel.split('/')[0]
            if os.path.exists(target):
                inside += 1
            elif top in listed and top not in skills:
                outside.setdefault(top, set()).add(f'{s}/{r}')
            else:
                broken.append(f'{s}/{r} -> {m.group(1)}')
print(f'relative links resolving inside the install: {inside}')
print('links into skills deliberately not installed:')
for k in sorted(outside):
    print(f'   {k}  (from {len(outside[k])} file(s))')
print(f'links broken for other reasons: {len(broken)}')
for b in broken[:10]:
    print('   ', b)
receipt['linksIntoSkippedSkills'] = {k: sorted(v) for k, v in sorted(outside.items())}
receipt['otherBrokenLinks'] = broken
json.dump(receipt, open(receipt_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('RESULT', 'VERIFIED' if ok else 'FAILED', f'{len(skills)}/{len(skills)} selected skills' if ok else '')
