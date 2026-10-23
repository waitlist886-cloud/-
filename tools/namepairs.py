# 用法：python -X utf8 tools/namepairs.py —— 把各页（月银纪三卷、纷争纪、山铜纪拼好的页）的旅伴、人物名和第三批的人物名两两比一遍，报出太像的（同一个名字换了一个字、头两个字相同、头尾两个字相同）
import sys, os, re, glob, itertools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
names = {}
for sub in ['月银纪史诗', '诸国期', '萨尔维斯', '纷争纪', '山铜纪']:
    for p in glob.glob(os.path.join(ROOT, sub, '*.md')):
        s = open(p, encoding='utf-8').read()
        for m in re.finditer(r'^## 旅途同行：(.+?)（', s, re.M):
            names.setdefault(m.group(1).split('·')[0], set()).add(sub)
        for m in re.finditer(r'固定锚定：[^\n]*?简称 ([^｜]+)｜', s):
            names.setdefault(m.group(1).split('·')[0], set()).add(sub)
for p in glob.glob(os.path.join(ROOT, 'moon', 'batch3', '*.md')):
    for m in re.finditer(r'^=== 人物｜([^，\n]+)', open(p, encoding='utf-8').read(), re.M):
        names.setdefault(re.split(r'[，与]', m.group(1))[0], set()).add('第三批')
extra = sys.argv[1:]
for n in extra:
    names.setdefault(n, set()).add('新')
L = sorted(names)
SIM = [set('宾碧'), set('瑟泽'), set('蕾兰')]
def near(a, b):
    if len(a) != len(b):
        return False
    diff = [(x, y) for x, y in zip(a, b) if x != y]
    return len(diff) == 1 and any({diff[0][0], diff[0][1]} <= s for s in SIM)
for a, b in itertools.combinations(L, 2):
    if near(a, b) or (len(a) >= 3 and len(b) >= 3 and a[:2] == b[:2]) or (a[0] == b[0] and a[-1] == b[-1] and abs(len(a) - len(b)) <= 1):
        print('%s（%s） ~ %s（%s）' % (a, '、'.join(sorted(names[a])), b, '、'.join(sorted(names[b]))))
print('一共比了 %d 个名字' % len(L))
