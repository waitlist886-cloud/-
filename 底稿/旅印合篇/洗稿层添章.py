# 山铜纪与迷宫纪合篇（11-08 照倾向写入）：底卡洗稿层 #151、十兆十条、#57、#3 照方向稿第八节、第十一节、第十二节第4条添。
# 只动洗稿文本（````围栏里那一段），底本哈希不动。用法：python -I -X utf8 底稿/旅印合篇/洗稿层添章.py . [--apply]
import os, re, sys

ROOT = sys.argv[1]
APPLY = '--apply' in sys.argv
D = os.path.join(ROOT, '底卡洗稿')

ZHAO = [  # 条号, 章, 大潮的任务名
    (1370, '序章', None), (1371, '第一章', '井向城中生长'), (1373, '第二章', '浮空城醒来之时'), (1374, '第三章', '与英灵并肩'),
    (1375, '第四章', '乱季的终曲'), (1376, '第五章', '人与龙的盟约'), (1377, '第六章', '门后的光'), (1378, '第七章', '七座圣火'),
    (1379, '第八章', '天伤'), (1380, '终章', None),
]
DACHAO1 = '群兽向灯火而来'

S151 = ('**世界主线的部、章与任务。** 世界主线奥尔德兰的旅印分上中下三部，山铜纪是上部，迷宫纪前传是中部，迷宫纪1001年以后的十兆是下部（★）。'
        '下部一兆一章，兆一·魔兽离巢是序章，兆二到兆九依次是第一到第八章，兆十和十兆终局并作终章，章名照兆名，终章照十兆终局那一条的题，叫黎明壁垒与灰雨远征军。'
        '一兆里三个主线节点和一回大潮是这一章的四个任务，节点照原来方括号里的名字，大潮的任务名写在各兆那一条大潮那一段的头一行。'
        '终章六个任务，集结联军，守卫六大地区，黑日列车出发，终末迷宫，归还门的另一面，世界之门，归还门的另一面走到那一步才报。'
        '一个任务开场的头一回合，叙述的头一行照上面的前缀表单占一行，下一行写部和章，比如下部·序章《魔兽离巢》，这一局头一回走进这一章的，再下一行照那一兆开头那一段写一句。'
        '上部、中部的任务只在山铜纪和前传的局里报，迷宫纪的局里讲起那些年的事，只当史书和老人嘴里的事，任务名不报（★）。')
S57 = ('章：下部·终章《黎明壁垒与灰雨远征军》｜终章六个任务，集结联军，守卫六大地区，黑日列车出发，终末迷宫，归还门的另一面，世界之门。'
       '归还门的另一面就是最终战，从归还门反过来走进去，三阶段的名号照这一条的锁，这个任务名走到那一步才报（★）。')
S3 = ('**上中两部埋下的种（只给 AI）。** 世界主线的上部（山铜纪）、中部（迷宫纪前传）里，几条主线已经埋了种，1001年以后的局里只当史书和老人嘴里的事，不报那些任务名（★）。'
      '主线一大迷宫与吞界之心埋在间章那四个任务里（山铜纪947年地开的前夜，垂暮的年月的空着的环、无谬之城、星形钥印），也埋在中部五章里，井这一条暗线一路通到终章的归还门。'
      '主线四双王两种答案埋在上部序章到第三章（篮中的婴儿、灰之魔女、破晓在她手边），第五章维拉瑟，还有中部先报全名、车上的两个王、门为回家的人开（两个王站在路的两边）。'
      '主线五龙权与神骸埋在上部第二章赤手入山（山里那一块神骸），第四章空碗（最后一尊），龙君之章七重龙门。'
      '主线三原初造世埋在银白之章根上的旧字（衔枝纪的残叶）。'
      '主线二、主线六在上中两部里的种这一回不点。')


def first_sentence(text):
    m = re.match(r'([^。]*。)', text)
    return m.group(1) if m else text


def blocks(path):
    s = open(path, encoding='utf-8').read()
    return s


changed = {}


def edit(n, fn):
    for f in sorted(os.listdir(D)):
        if not f.endswith('.md'):
            continue
        p = os.path.join(D, f)
        s = changed.get(p) or open(p, encoding='utf-8').read()
        m = re.search(r'^## #%d [^\n]*\n' % n, s, re.M)
        if not m:
            continue
        a = s.index('````\n', m.end()) + 5
        b = s.index('\n````', a)
        body = s[a:b]
        new = fn(body)
        if new == body:
            print('#%d 没变（已经添过？）' % n)
            return
        changed[p] = s[:a] + new + s[b:]
        print('#%d 改了（%s）' % (n, f))
        return
    print('#%d 没找到' % n)


def zhao(n, ch, task):
    def fn(body):
        L = body.split('\n')
        if any(l.startswith('章：下部·') for l in L):
            return body
        title = L[0]
        assert title.startswith('# 兆'), title
        name = re.match(r'# 兆[一二三四五六七八九十]+·([^（]+)', title).group(1)
        desc = first_sentence(L[1])
        if ch == '终章':
            line = '章：下部·终章《黎明壁垒与灰雨远征军》｜%s' % desc
        else:
            line = '章：下部·%s《%s》｜%s' % (ch, name, desc)
        L.insert(1, line)
        t = DACHAO1 if n == 1370 else task
        if t:
            k = next(i for i, l in enumerate(L) if l.startswith('## 大潮'))
            L.insert(k + 1, '任务名：【%s】' % t)
        return '\n'.join(L)
    return fn


for n, ch, task in ZHAO:
    edit(n, zhao(n, ch, task))
edit(151, lambda body: body if '**世界主线的部、章与任务。**' in body else body.rstrip('\n') + '\n\n' + S151)
edit(57, lambda body: body if '章：下部·终章' in body else body.split('\n', 1)[0] + '\n' + S57 + '\n' + body.split('\n', 1)[1])
edit(3, lambda body: body if '**上中两部埋下的种' in body else body.rstrip('\n') + '\n\n' + S3)
if APPLY:
    for p, s in changed.items():
        open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('改了的文件', len(changed), '（' + ('写了' if APPLY else '没写，加 --apply') + '）')
