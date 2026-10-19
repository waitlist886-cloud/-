# 用法：python -I -X utf8 lens.py 文件 —— 逐节打印每行字数，标出近失（差一两字）、叠字、禁词
import sys, re
t = open(sys.argv[1], encoding='utf-8').read()
BAN = ['整整','一遍遍','一下一下','新月','满月','残月','月牙','弦月','月亮','月光','厄洛伽','说来也怪','从那以后','驿','名簿','龛','三川','诸侯','朝廷']
ALLOW_AA = set('人天年处个回家常往偏刚稍渐')
for st in re.split(r'\n\s*\n', t.strip()):
    lines = [l for l in st.split('\n') if l.strip()]
    if not lines or lines[0].startswith('#'): 
        print(lines[0] if lines else ''); continue
    L = [len(l) for l in lines]
    flag = ''
    for a, b in zip(L, L[1:]):
        if 0 < abs(a - b) <= 2: flag = '  !!近失'
    for l in lines:
        print('%3d %s' % (len(l), l))
    s = re.sub(r'「[^」]*」', '', st)
    red = set(m.group(0) for m in re.finditer(r'([一-鿿])\1', s) if m.group(1) not in ALLOW_AA)
    red |= set(m.group(0) for m in re.finditer(r'([一-鿿])一\1', s))
    bad = [w for w in BAN if w in st]
    if flag or red or bad: print('    ', flag, '叠字:' + '、'.join(red) if red else '', '禁词:' + '、'.join(bad) if bad else '')
    print()
