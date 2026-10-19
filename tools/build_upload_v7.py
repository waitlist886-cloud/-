# usage: python3 -I build.py poem_v6.md poem_v7.md outdir
# v6 -> v7 at doc rev 62. 1:1 stanza changes go as single-block replaces with ifHash;
# deletions and insertions ride on a neighbouring block; WHOLE sections are replaced in one multi-block op.
import sys, json, hashlib, re, difflib

v6src, v7src, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
P = 'mkec4ksctvv.'
REV = 62
ids = json.load(open(outdir + '/ids_rev62.json', encoding='utf-8'))
BQ_ID, BQ_HASH = ids['BQ'], '85a1bdc2'
SECS = [(n, l) for n, l in ids['sections']]
H2 = {'序歌': 209, '第一歌 火': 748, '第二歌 枝': 1985, '第三歌 砧': 3003, '第四歌 鳞': 3641, '第五歌 灯': 4027,
      '第六歌 海': 4469, '第七歌 冠': 5212, '第八歌 炉': 7548, '第九歌 刀': 8587, '第十歌 弓': 9739,
      '第十一歌 盐': 10671, '第十二歌 歌': 11575, '第十三歌 结': 12516, '第十四歌 日': 13103, '尾歌': 14183}
WHOLE = {'第七歌 冠'}
BUDGET, MAXOPS = 21000, 60

def h8(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()[:8]

def parse(path):
    text = open(path, encoding='utf-8').read()
    blocks = [b.strip('\n') for b in re.split(r'\n\s*\n', text) if b.strip()]
    assert blocks[0] == '# 天亮以前'
    sec, order, cur = {'BQ': blocks[1]}, [], None
    for b in blocks[2:]:
        if b.startswith('## '):
            cur = b[3:]; order.append(cur); sec[cur] = []
        else:
            lines = b.split('\n')
            for l in lines:
                assert not l.endswith('\\') and not l.startswith(('#', '>', '-', '*', '+')), l
                assert l.count('“') == l.count('”'), l
            sec[cur].append(lines)
    return sec, order

old, oorder = parse(v6src)
new, norder = parse(v7src)
assert oorder == [n for n, _ in SECS], oorder
assert len(oorder) == len(norder)
for name, l in SECS:
    assert len(old[name]) == len(l), (name, len(old[name]), len(l))

md = lambda sts: '\n\n'.join('\\\n'.join(x) for x in sts)
def rep(idl, content, ifhash=None):
    o = {'op': 'replace', 'target': {'kind': 'blocks', 'ids': [P + str(i) for i in idl]}, 'ifRev': REV,
         'with': {'as': 'markdown', 'from': {'kind': 'inline', 'content': content}}}
    if ifhash:
        o['ifHash'] = ifhash
    return o

ops, log = [], []
if new['BQ'] != old['BQ']:
    ops.append(('BQ', rep([BQ_ID], new['BQ'], BQ_HASH))); log.append('BQ')
for (oname, idl), nname in zip(SECS, norder):
    if oname != nname:
        ops.append((oname, rep([H2[oname]], '## ' + nname, h8(oname)))); log.append('%s heading -> %s' % (oname, nname))
    a, b = old[oname], new[nname]
    if oname in WHOLE:
        ops.append((oname, rep(idl, md(b)))); log.append('%s whole %d -> %d' % (oname, len(a), len(b)))
        continue
    sm = difflib.SequenceMatcher(a=[''.join(x) for x in a], b=[''.join(x) for x in b], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        if tag == 'replace' and i2 - i1 == j2 - j1:
            for k in range(i2 - i1):
                ops.append((oname, rep([idl[i1 + k]], md([b[j1 + k]]), h8(''.join(a[i1 + k])))))
            log.append('%s replace %d' % (oname, i2 - i1))
        elif tag == 'insert':
            assert a[i1 - 1] == b[j1 - 1]
            ops.append((oname, rep([idl[i1 - 1]], md(b[j1 - 1:j2]), h8(''.join(a[i1 - 1])))))
            log.append('%s insert %d after %d' % (oname, j2 - j1, idl[i1 - 1]))
        elif tag == 'delete':
            assert i2 < len(a) and a[i2] == b[j1]
            ops.append((oname, rep(idl[i1:i2 + 1], md([b[j1]])))); log.append('%s delete %s' % (oname, idl[i1:i2]))
        else:
            ops.append((oname, rep(idl[i1:i2], md(b[j1:j2])))); log.append('%s multi %d -> %d' % (oname, i2 - i1, j2 - j1))

expect = [('H1', h8('天亮以前'), '天亮以前'), ('BQ', h8(new['BQ'][2:]), new['BQ'][2:14])]
for name in norder:
    expect.append(('H2', h8(name), name))
    for st in new[name]:
        expect.append((name, h8(''.join(st)), st[0][:12]))

calls, curc, size = [], [], 0
for name, o in ops:
    n = len(json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
    if curc and (size + n > BUDGET or len(curc) >= MAXOPS):
        calls.append(curc); curc, size = [], 0
    curc.append((name, o)); size += n
calls.append(curc)
for k, c in enumerate(calls):
    s = json.dumps({'ops': [o for _, o in c]}, ensure_ascii=False, separators=(',', ':'))
    open('%s/call%d.json' % (outdir, k + 1), 'w', encoding='utf-8').write(s)
    print('call%d: %d ops, %d bytes' % (k + 1, len(c), len(s.encode('utf-8'))))
with open('%s/expect.tsv' % outdir, 'w', encoding='utf-8') as f:
    for e in expect:
        f.write('\t'.join(e) + '\n')
print('\n'.join(log)); print('ops', len(ops), 'expected blocks', len(expect))
