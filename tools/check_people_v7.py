# -*- coding: utf-8 -*-
"""旅伴页的卡面文字检查（第七版）。用法：python3 -I check_people_v7.py page.md /home/claude/aldran
硬问题计入合计：禁用标点、禁词、冒号、「」引用、月相、科技词、引号不配对。
其余是密度提示：不点名指代、否定式留白、制度词、不是…是、句长单调、单句成段。"""
import sys, re, json, glob, os
page, root = sys.argv[1], sys.argv[2]
s = open(page, encoding='utf-8').read()
titles = set()
d = json.load(open(os.path.join(root, 'src/rili_v7.json'), encoding='utf-8'))
for e in d['prompt']['lorebook']:
    c = (e.get('content') or '').lstrip()
    m = re.match(r'#+\s*([^\n]+)', c)
    if m:
        t = m.group(1).strip(); titles.add(t); titles.add(t.split('｜')[0])
for f in glob.glob(os.path.join(root, 'moon/batch*/*.md')):
    if '_backup' in f:
        continue
    for m in re.finditer(r'(?m)^=== (.+)$', open(f, encoding='utf-8').read()):
        t = m.group(1).strip(); titles.add(t); titles.add(t.split('｜')[0])
BAN_P = ['——', '—', '；', '…', '！', '...']
BAN_W = ['学宫', '客栈', '朝廷', '门客', '时辰', '掌柜', '客官', '百官', '丫头', '宗门', '长老', '功法', '镖局',
         '一丝', '一抹', '嘴角勾起', '玩味', '命运的齿轮', '历史的车轮', '山雨欲来', '不禁', '深不可测', '恐怖如斯', '威压', '修为',
         '封锁令', '军令', '除籍', '审批', '登记', '编制', '条例', '抚恤', '核验', '流程', '资质', '注册', '合规', '晋升']
MOON = ['新月', '满月', '残月', '月牙', '弦月', '月亮', '月光']
TECH = ['量子', '熵', '坐标', '频率', '能量', '系统']
label = re.compile(r'^(- )?[^，。：]{1,8}：')
secs = re.split(r'(?m)^## ', s)
hard = 0
tot = {'不点名': 0, '否定留白': 0, '不是…是': 0, '单调段': 0, '单句段': 0}
for sec in secs[1:]:
    head = sec.split('\n', 1)[0]
    if head.startswith('设计备注'):
        continue
    body = [ln for ln in sec.split('\n')[1:] if not ln.startswith('>')]
    text = '\n'.join(body)
    han = len(re.findall(r'[一-鿿]', text))
    out = []
    for p in BAN_P:
        if p in text:
            hard += text.count(p); out.append(f'标点 {p}×{text.count(p)}')
    for w in BAN_W + MOON + TECH:
        if w in text:
            hard += 1; out.append(f'词 {w}')
    for ln in body:
        if ('：' in ln or ':' in ln) and not label.match(ln) and not ln.startswith('#'):
            hard += 1; out.append('冒号 ' + ln[:40])
    for ref in re.findall(r'「([^」]+)」', text):
        if ref not in titles:
            hard += 1; out.append('引用不存在 ' + ref)
    for para in [p for p in text.split('\n') if p.strip()]:
        if para.count('“') != para.count('”'):
            hard += 1; out.append('引号不配对 ' + para[:30])
    a = len(re.findall(r'那一位|有样东西|有东西从|有一国|某一|某个|某种|某样', text))
    b = len(re.findall(r'没有一个人|谁也没|从来没|说不上来|说不清', text))
    c = len(re.findall(r'不是[^。，]{0,12}，是|不是[^。]{0,20}而是', text))
    tot['不点名'] += a; tot['否定留白'] += b; tot['不是…是'] += c
    mono = 0; single = 0
    for para in [p for p in text.split('\n') if p.strip() and not p.startswith(('#', '-', '【', '“'))]:
        sents = [x for x in re.split(r'[。？]', para) if len(re.findall(r'[一-鿿]', x)) > 0]
        lens = [len(re.findall(r'[一-鿿]', x)) for x in sents]
        if len(lens) >= 4 and max(lens) - min(lens) < 8:
            mono += 1
        if len(lens) == 1 and lens[0] < 25:
            single += 1
    tot['单调段'] += mono; tot['单句段'] += single
    info = f'不点名{a} 否定{b} 不是…是{c} 单调段{mono} 单句段{single}'
    print('==', head[:28], '| 汉字', han, '|', info, ('| ' + '；'.join(out)) if out else '')
print('硬问题合计', hard, '| 提示合计', tot, '| 全文字节', len(s.encode()))
