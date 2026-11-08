#!/usr/bin/env python3
# 查子任务写的史诗战、神明显像提示词（11-07）。
#   python epic_check.py <份>        份：moon strife_god1 strife_god2 strife_other bronze maze gods_zheng gods_mo
# 查：键齐不齐、次序、prev 对不对、person 是不是候选里的、design_ref 指得到、长短、有没有中文、写了不该写的词（中式、仙侠、月、血、字）。
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, 'epic', 'in')
PR = os.path.join(HERE, 'epic', 'prompts')
CJK = re.compile(r'[㐀-鿿＀-￯]')
BAN = [(r'\bmoon', 'moon'), (r'crescent', 'crescent'), (r'\blunar\b', 'lunar'), (r'(?<!hooded )\brobes?\b', 'robe（要写写 hooded robe 或 habit）'),
       (r'\bsash(es)?\b', 'sash'), (r'\btassels?\b', 'tassel'), (r'\bjade\b', 'jade'), (r'silk ribbons?', 'silk ribbon'), (r'\bhairpins?\b', 'hairpin'),
       (r'\btopknot', 'topknot'), (r'\blotus', 'lotus'), (r'\bpagoda', 'pagoda'), (r'temple roof', 'temple roof'), (r'cloud scroll', 'cloud scroll'),
       (r'celestial maiden', 'celestial maiden'), (r'\bhanfu\b', 'hanfu'), (r'\bkimono', 'kimono'), (r'\bchinese\b', 'Chinese'), (r'\boriental\b', 'oriental'),
       (r'\basian\b', 'Asian'), (r'\bblood(y|ied)?\b', 'blood'), (r'\bgore\b|\bgory\b', 'gore'), (r'\bletters?\b', 'letters'), (r'\btext\b', 'text'),
       (r'\bxianxia\b', 'xianxia'), (r'\bimmortals\b', 'immortals'), (r'\bqi\b', 'qi')]
BOSS_REF = {'boss:fenyuan1', 'boss:yamon1', 'boss:gemoen1'}


def words(s):
    return len(re.findall(r"[A-Za-z][A-Za-z'\-]*", s or ''))


def text_issues(where, s, lo, hi):
    out = []
    if not s or not s.strip():
        return ['%s 空的' % where]
    n = words(s)
    if n < lo or n > hi:
        out.append('%s 词数 %d（该在 %d 到 %d）' % (where, n, lo, hi))
    if CJK.search(s):
        out.append('%s 有中文：%s' % (where, CJK.findall(s)[:6]))
    low = s.lower()
    for rx, name in BAN:
        if re.search(rx, low):
            out.append('%s 写了 %s' % (where, name))
    return out


def all_first_keys():
    keys = set()
    for f in os.listdir(IN):
        if f.endswith('.json') and not f.startswith('gods_'):
            for b in json.load(open(os.path.join(IN, f), encoding='utf-8')):
                keys.add(b['phases'][0]['key'])
                keys.update(p['key'] for p in b['phases'])
    return keys


def check_boss(part):
    src = json.load(open(os.path.join(IN, part + '.json'), encoding='utf-8'))
    out = json.load(open(os.path.join(PR, part + '.json'), encoding='utf-8'))
    probs = []
    if len(out) != len(src):
        probs.append('块数 %d，输入是 %d' % (len(out), len(src)))
    refs = all_first_keys() | BOSS_REF
    for i, (s, o) in enumerate(zip(src, out)):
        w = '第%d块 %s' % (i + 1, s['block'][:20])
        if o.get('block') != s['block']:
            probs.append('%s 块名对不上：%s' % (w, str(o.get('block'))[:20]))
        probs += text_issues(w + ' design', o.get('design'), 25, 120)
        cands = {c['key'] for c in s.get('person_candidates', [])}
        if o.get('person') and o['person'] not in cands:
            probs.append('%s person %s 不在候选里' % (w, o['person']))
        if o.get('design_ref') and o['design_ref'] not in refs:
            probs.append('%s design_ref %s 指不到' % (w, o['design_ref']))
        sk = [p['key'] for p in s['phases']]
        ok = [p.get('key') for p in o.get('phases', [])]
        if sk != ok:
            probs.append('%s 阶的键对不上：%s / %s' % (w, sk, ok))
            continue
        for j, p in enumerate(o['phases']):
            pw = '%s %s' % (w, p['key'])
            want = None if j == 0 else sk[j - 1]
            restart = p.get('prev') is None and p.get('design_ref')   # 同一块里的另一场，重新起头，样子照 design_ref
            if p.get('prev') != want and not restart:
                probs.append('%s prev 是 %s，该是 %s' % (pw, p.get('prev'), want))
            if p.get('design_ref') and p['design_ref'] not in refs:
                probs.append('%s design_ref %s 指不到' % (pw, p['design_ref']))
            if not isinstance(p.get('dead'), bool):
                probs.append('%s dead 不是 true/false' % pw)
            probs += text_issues(pw + ' prompt', p.get('prompt'), 30, 160)
    return probs, sum(len(b['phases']) for b in out)


def check_gods(part):
    src = json.load(open(os.path.join(IN, part + '.json'), encoding='utf-8'))
    out = json.load(open(os.path.join(PR, part + '.json'), encoding='utf-8'))
    probs = []
    sk = [g['key'] for g in src]
    ok = [g.get('key') for g in out]
    if sk != ok:
        probs.append('键对不上（次序照输入）：少 %s 多 %s' % (sorted(set(sk) - set(ok))[:8], sorted(set(ok) - set(sk))[:8]))
    refs = all_first_keys()
    for g in out:
        w = '%s %s' % (g.get('key'), g.get('name', ''))
        probs += text_issues(w, g.get('prompt'), 60, 180)
        if g.get('design_ref') and g['design_ref'] not in refs:
            probs.append('%s design_ref %s 指不到' % (w, g['design_ref']))
    return probs, len(out)


def merge(part):
    """分几次写的（epic/prompts/<份>.part1.json、part2…，每个是一个数组）按序号接成 <份>.json。"""
    import glob
    fs = sorted(glob.glob(os.path.join(PR, part + '.part*.json')), key=lambda p: int(re.search(r'\.part(\d+)\.json$', p).group(1)))
    out = []
    for f in fs:
        out += json.load(open(f, encoding='utf-8'))
    json.dump(out, open(os.path.join(PR, part + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('接了 %d 个分文件，%d 条' % (len(fs), len(out)))


if __name__ == '__main__':
    part = sys.argv[1]
    if '--merge' in sys.argv:
        merge(part)
    if not os.path.exists(os.path.join(PR, part + '.json')):
        sys.exit('还没有 epic/prompts/%s.json' % part)
    probs, n = (check_gods if part.startswith('gods_') else check_boss)(part)
    for p in probs:
        print(p)
    print('== %s：%d 条，问题 %d' % (part, n, len(probs)))
