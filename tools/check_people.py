# -*- coding: utf-8 -*-
"""人设样稿的卡面文字检查：标点、冒号、「」引用、语域词、篇幅。用法：python3 -I check_people.py doc.md /home/claude/aldran"""
import sys, re, json, glob, os
doc, root = sys.argv[1], sys.argv[2]
s = open(doc, encoding='utf-8').read()
CARD_KEYS = ['奥斯温，', '英嘉，', '霍布，', '三个人的命星', '伊妮德，', '安瑟姆', '雷米，', '这一批的命星']
secs = re.split(r'(?m)^## ', s)
titles = set()
d = json.load(open(os.path.join(root, 'src/rili_v7.json'), encoding='utf-8'))
for e in d['prompt']['lorebook']:
    c = (e.get('content') or '').lstrip()
    m = re.match(r'#+\s*([^\n]+)', c)
    if m:
        t = m.group(1).strip(); titles.add(t); titles.add(t.split('｜')[0])
for f in glob.glob(os.path.join(root, 'moon/batch*/*.md')):
    if '_backup' in f: continue
    for m in re.finditer(r'(?m)^=== (.+)$', open(f, encoding='utf-8').read()):
        t = m.group(1).strip(); titles.add(t); titles.add(t.split('｜')[0])
BAN_P = ['——', '—', '；', '…', '！', '...']
BAN_W = ['学宫', '客栈', '朝廷', '门客', '时辰', '掌柜', '客官', '百官', '丫头', '宗门', '长老', '功法', '镖局', '一丝', '一抹', '嘴角勾起', '玩味', '命运的齿轮', '不禁']
label = re.compile(r'^(- )?[^，。：]{1,8}：')
problems = 0
for sec in secs[1:]:
    head = sec.split('\n', 1)[0]
    if not any(k in head for k in CARD_KEYS):
        continue
    body = [ln for ln in sec.split('\n')[1:] if not ln.startswith('>')]
    text = '\n'.join(body)
    han = len(re.findall(r'[一-鿿]', text))
    print('==', head, '| 汉字', han)
    for p in BAN_P:
        if p in text:
            problems += 1; print('  标点', p, text.count(p))
    for w in BAN_W:
        if w in text:
            problems += 1; print('  词', w, text.count(w))
    for ln in body:
        if ('：' in ln or ':' in ln) and not label.match(ln) and not ln.startswith('#'):
            problems += 1; print('  冒号', ln[:60])
    for ref in re.findall(r'「([^」]+)」', text):
        if ref not in titles:
            problems += 1; print('  引用不存在', ref)
    n = len(re.findall(r'不是[^。，]{0,12}，是|不是[^。]{0,20}而是', text))
    if n: print('  不是…是', n)
print('问题合计', problems, '| 全文字节', len(s.encode()))
