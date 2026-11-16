# 全卡精炼洗稿：样稿跟源稿对一遍。只读，不改东西。
#   python -I -X utf8 底稿/洗稿/全卡精炼/check_sample.py
# 1. 每一条改前改后多少字
# 2. 受保护的行（标题、条目设置、固定锚定、底座、体态数据、题、篇）是不是一个字没动
# 3. 样稿里的数（年份、人数、道数、等级、百分数）是不是都出自源稿
# 4. 口癖每万字多少处，跟源稿同一组比
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = 'E:/aldran_art/'
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))
rd = lambda p: open(ROOT + p, encoding='utf-8').read().replace('\r\n', '\n')

NEW = rd('底稿/洗稿/全卡精炼/样稿_第七歌一组.md')
PAGE = rd('月银纪史诗/第七歌_焚原断刃.md')
BOND = rd('月银纪补卷/羁绊_06.md')
PLACE = rd('月银纪补卷/地点_06_万兽诸地.md')


def cut(s, head, stops):
    """从 head 那一行起，取到下一处 stops 里的行首为止。"""
    i = s.index(head)
    j = len(s)
    for st in stops:
        for m in re.finditer(st, s[i + len(head):], re.M):
            j = min(j, i + len(head) + m.start())
            break
    return s[i:j].rstrip() + '\n'


PAIRS = [
    ('主线｜万兽·焚原', '## 月银纪·主线｜万兽·焚原（第二稿）', PAGE, [r'^## 旅途同行']),
    ('旅伴｜麦伦', '## 旅途同行：麦伦（月银纪·焚原断刃）', PAGE, [r'^## 旅途同行·背景']),
    ('旅伴背景｜麦伦', '## 旅途同行·背景：麦伦', PAGE, [r'^## ']),
    ('命星｜不折之腰', '### 不折之腰 (Special | Legend)', PAGE, [r'^### ']),
    ('命星｜眠山血脉', '### 眠山血脉 (Passive | Legend)', PAGE, [r'^### ']),
    ('命星｜刈穗', '### 刈穗 (Art | Rare)', PAGE, [r'^### ', r'^> 条目设置', r'^## ']),
    ('羁绊｜弯腰之章', '## 月银纪·羁绊｜弯腰之章·带禾捆回来', BOND, [r'^## ']),
    ('地点｜霜渡', '## 月银纪·地点｜霜渡与三座平顶的山', PLACE, [r'^## ']),
]
PROT = re.compile(r'^(?:#{2,3} |> 条目设置|固定锚定：|底座：|体态数据｜|题：|篇：)')
NUM = re.compile(r'\d+(?:\.\d+)?')
CN = '一二三四五六七八九十百千万两'
TICS = [('那一', r'那一'), ('这一', r'这一'), ('往后', r'往后'), ('照旧', r'照旧'), ('头一', r'头一')]

print('%-14s %7s %7s %6s' % ('条目', '改前字', '改后字', '留'))
tb = ta = 0
olds = []
news = []
for name, head, src, stops in PAIRS:
    old = cut(src, head, stops)
    new = cut(NEW, head, stops + [r'^## '] if not head.startswith('## ') else stops)
    olds.append(old)
    news.append(new)
    a, b = han(old), han(new)
    tb += a
    ta += b
    print('%-14s %7d %7d %5.0f%%' % (name, a, b, 100 * b / a))
    # 受保护的行
    po = [l for l in old.split('\n') if PROT.match(l)]
    pn = [l for l in new.split('\n') if PROT.match(l)]
    lost = [l for l in po if l not in pn and not l.startswith('### ') or (l.startswith('### ') and l not in pn and head.startswith('## 旅途同行：'))]
    added = [l for l in pn if l not in po]
    for l in added:
        print('    多出来的受保护行：', l[:60])
    for l in po:
        if l not in pn:
            print('    源稿有、样稿没有的受保护行：', l[:60])
    # 数
    so = set(NUM.findall(old))
    for n in sorted(set(NUM.findall(new)) - so, key=lambda x: float(x)):
        print('    样稿里多出来的数：', n)
print('%-14s %7d %7d %5.0f%%' % ('合计', tb, ta, 100 * ta / tb))

print('\n口癖每万字多少处（同一组，改前｜改后）')
O = '\n'.join(olds)
N = '\n'.join(news)
for nm, p in TICS:
    print('  %s  %5.1f｜%5.1f' % (nm, len(re.findall(p, O)) / (han(O) / 1e4), len(re.findall(p, N)) / (han(N) / 1e4)))

print('\n禁用标点：', {c: N.count(c) for c in '—；…！' if N.count(c)} or '没有')
bad = [l for l in N.split('\n') if re.match(r'^\s*(?:- )?[^：\n“”]{9,}：', l) and not l.startswith('>') and '｜' not in l.split('：')[0]]
for l in bad[:10]:
    print('  冒号前过八个字：', l[:50])
