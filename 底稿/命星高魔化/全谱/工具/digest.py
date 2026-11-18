# -*- coding: utf-8 -*-
"""给全谱和旅伴表备料：一段几页，出两份摘要。
用法：python -I -X utf8 digest.py <输出目录> <段名> <页.md> [<页.md> …]
"""
import io, re, sys, os, csv

OUT = sys.argv[1]
SEG = sys.argv[2]
PAGES = sys.argv[3:]
HERE = os.path.dirname(os.path.abspath(__file__))

mai = {}
p = os.path.join(HERE, 'mai.tsv')
if os.path.exists(p):
    for r in csv.reader(io.open(p, encoding='utf-8'), delimiter='\t'):
        if len(r) >= 7 and r[0] != '编号':
            mai.setdefault(r[1], []).append((r[2], r[6][:40]))

def clean(s, n):
    s = re.sub(r'\s+', ' ', s).strip()
    return s if len(s) <= n else s[:n] + '…'

def field(body, label, n):
    m = re.search(r'(?m)^- %s：(.+)$' % re.escape(label), body)
    return clean(m.group(1), n) if m else ''

art_out, comp_out = [], []
for path in PAGES:
    text = io.open(path, encoding='utf-8').read().replace('\r\n', '\n')
    page = os.path.basename(path)[:-3]
    # 旅伴
    comps = []
    for sec in re.split(r'(?m)^(?=## )', text):
        m = re.match(r'## 旅途同行：(.+?)\n', sec)
        if not m:
            continue
        title = m.group(1).strip()
        if re.search(r'的背景|旅伴之间', title):
            continue
        dz = re.search(r'(?m)^底座：(.+)$', sec)
        nl = re.search(r'(?m)^能力：(.+)$', sec)
        sf = re.search(r'(?m)^身份：(.+)$', sec)
        gd = re.search(r'(?m)^固定锚定：(.+)$', sec)
        xc = re.search(r'### 正史里的下场\n+(.+?)(?:\n\n|\n###|\n【|\Z)', sec, re.S)
        comps.append((title, dz.group(1) if dz else '', nl.group(1) if nl else '', sf.group(1) if sf else '',
                      gd.group(1) if gd else '', xc.group(1) if xc else ''))
    comp_out.append('\n# 页：%s（旅伴 %d 条）\n' % (page, len(comps)))
    for i, (title, dz, nl, sf, gd, xc) in enumerate(comps, 1):
        comp_out.append('## %d. %s' % (i, title))
        comp_out.append('- 固定锚定：' + clean(gd, 200))
        comp_out.append('- 底座：' + clean(dz, 260))
        comp_out.append('- 身份：' + clean(sf, 220))
        comp_out.append('- 能力：' + clean(nl, 330))
        xcs = re.sub(r'\s+', ' ', xc).strip()
        if len(xcs) > 640:
            xcs = xcs[:330] + ' …… ' + xcs[-300:]
        comp_out.append('- 下场：' + xcs)
        comp_out.append('')
    # 技艺
    arts = []
    for m in re.finditer(r'(?m)^### (.+?) [（(]Art ?[|｜] ?(\w+)[)）]\s*$', text):
        name, tier = m.group(1).strip(), m.group(2)
        start = m.end()
        nxt = re.search(r'(?m)^(?:### |## )', text[start:])
        body = text[start:start + nxt.start()] if nxt else text[start:start + 4000]
        first = ''
        for para in body.split('\n'):
            para = para.strip()
            if para.startswith('【' + name + '】') or (para.startswith('【') and '】是' in para[:len(name) + 6]):
                first = para
                break
        holders = [t for (t, dz, nl, sf, gd, xc) in comps if ('【%s】' % name) in nl]
        arts.append((name, tier, first, body, holders))
    art_out.append('\n# 页：%s（技艺 %d 条）\n' % (page, len(arts)))
    for i, (name, tier, first, body, holders) in enumerate(arts, 1):
        art_out.append('## %d. %s〔现阶 %s〕' % (i, name, tier))
        art_out.append('- 持有的旅伴：' + ('、'.join(h.split('（')[0] for h in holders) if holders else '（能力行里没对上，多半是人物条或传奇条里的）'))
        if name in mai:
            art_out.append('- 传承表原归的脉：' + '；'.join('%s·%s' % (a, b) for a, b in mai[name][:3]))
        art_out.append('- 首段：' + clean(first, 300))
        for lab, n in [('定位', 330), ('修行重点', 90), ('修行关联', 90), ('限制', 150), ('传承', 260)]:
            v = field(body, lab, n)
            if v:
                art_out.append('- %s：%s' % (lab, v))
        art_out.append('')

os.makedirs(OUT, exist_ok=True)
io.open(os.path.join(OUT, SEG + '_技艺料.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(art_out))
io.open(os.path.join(OUT, SEG + '_旅伴料.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(comp_out))
print(SEG, '技艺料', sum(len(x) for x in art_out), '字；旅伴料', sum(len(x) for x in comp_out), '字')
