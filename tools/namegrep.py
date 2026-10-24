# 新名字在整个仓库里逐字查一遍：各纪的页、补卷、底稿、底卡 src/rili_v7.json、介绍页，语料/ 在的话也查原神
# collide.py 只扫底卡、三批旧稿和月银纪那几处，纷争纪、山铜纪拼好的页它不扫，起名以后两样都跑
# 用法（在仓库根目录下）：python3 -I -X utf8 tools/namegrep.py 名字1 名字2 …
# 报出来的是逐字撞上的，近音（莫尔嘉和莫尔加、茹丝和茹娜这一类）还得自己看
import sys, glob, os, collections
root = os.getcwd()
files = [f for f in glob.glob(os.path.join(root, '**', '*.md'), recursive=True)
         if os.sep + '语料' + os.sep not in f and os.sep + '.claude' + os.sep not in f]
files += [os.path.join(root, 'src', 'rili_v7.json'), os.path.join(root, 'src', 'intro_v7.html')]
texts = []
for f in files:
    try:
        texts.append((os.path.relpath(f, root), open(f, encoding='utf-8', errors='ignore').read()))
    except OSError:
        pass
corp = ''
for g in glob.glob(os.path.join(root, '语料', '*')):
    try:
        corp += open(g, encoding='utf-8', errors='ignore').read()
    except OSError:
        pass
for n in sys.argv[1:]:
    hits, ex = collections.Counter(), ''
    for f, s in texts:
        k = s.count(n)
        if k:
            hits[f.split(os.sep)[0]] += k
            if not ex:
                i = s.find(n)
                ex = s[max(0, i - 12):i + len(n) + 12].replace('\n', ' ')
    g = corp.count(n)
    print(n, '：', dict(hits) if hits else '无', ('原神%d' % g) if g else '', ('「%s」' % ex) if ex else '')
