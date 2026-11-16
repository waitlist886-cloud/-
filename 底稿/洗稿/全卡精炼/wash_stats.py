# 全卡精炼洗稿：量几样证据。只读卡，不改东西。
#   python -I -X utf8 wash_stats.py
# 1. 口癖每万字多少处（四纪各一行、底卡一行，对照原神武器和圣遗物文本）
# 2. 一字不差重复最多的整句
# 3. 麦伦的来历在几个条目里各讲了多少字
# 4. 焚原一幕里一轮叫醒多少条、多少字（照日里一条消息一条消息分开算）
import collections
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = 'E:/aldran_art/'
card = json.load(open(ROOT + 'out/发布卡_四纪大框/奥尔德兰_四纪大框.json', encoding='utf-8'))
lb = card['prompt']['lorebook']
ERAS = ['月银纪', '纷争纪', '山铜纪', '迷宫纪']
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))


def fno(e):
    m = re.match(r'\s*(\d+)', e.get('folder') or '')
    return int(m.group(1)) if m else -1


def era_of(e):
    f = e.get('folder') or ''
    if fno(e) >= 40:
        for x in ERAS:
            if x in f:
                return x
    return '底卡'


def body(e):
    if e.get('contentMethod') == 'weighted':
        return '\n'.join(c.get('content') or '' for c in e.get('contents') or [])
    return e.get('content') or ''


TICS = [('那一', r'那一'), ('这一', r'这一'), ('往后', r'往后'), ('照旧', r'照旧'), ('头一', r'头一'),
        ('一X一X', r'一([个道条根块座把件枚袋车桶碗步夜天年代垄])一\1'), ('不裁定', r'不裁定'),
        ('照…那一条', r'照[^，。\n]{1,14}那一条'), ('没有说话/没说话', r'没有?说话|没回头|没有回头|没有应|没应'),
        ('的那一个', r'的那一个'), ('这一局', r'这一局'), ('玩家在场', r'玩家在场')]
txt = collections.defaultdict(list)
for e in lb:
    txt[era_of(e)].append(body(e))
print('== 一、口癖，每万字多少处')
print('%-8s %8s  ' % ('', '万字') + '  '.join('%s' % n for n, _ in TICS))
rows = [(k, '\n'.join(txt[k])) for k in ERAS + ['底卡']]
for name in ['原神武器文本.md', '原神圣遗物文本.md']:
    try:
        rows.append((name[:6], open(ROOT + '语料/' + name, encoding='utf-8').read()))
    except OSError:
        pass
for k, s in rows:
    w = han(s) / 1e4
    print('%-8s %8.1f  ' % (k, w) + '  '.join('%5.1f' % (len(re.findall(p, s)) / w) for _, p in TICS))

print('\n== 二、一字不差重复最多的整句（四纪加底卡，十二个字以上，出现三十回以上）')
cnt = collections.Counter()
for e in lb:
    seen = set()
    for sent in re.split(r'[。\n]', body(e)):
        s = sent.strip(' -·　')
        if han(s) >= 12 and s not in seen:
            seen.add(s)
            cnt[s] += 1
for s, n in cnt.most_common(40):
    if n < 30:
        break
    print('  %4d 回  %s' % (n, s[:70]))
rep = sum(len(s.encode('utf-8')) * (n - 1) for s, n in cnt.items() if n >= 5)
print('  出现五回以上的整句，多出来的遍数合计 %.2f MB' % (rep / 1e6))

print('\n== 三、麦伦认得焚原这一层来历，各条目里讲了多少')
KEY = re.compile(r'眠山村|纳贡的那一户|八个秋天|舔过|旧名字|红土线')
tot = 0
for e in lb:
    c = body(e)
    if '麦伦' in c and KEY.search(c):
        hits = [m.start() for m in KEY.finditer(c)]
        sents = set()
        for sent in re.split(r'[。\n]', c):
            if KEY.search(sent) and ('麦伦' in c):
                sents.add(sent)
        n = sum(han(s) for s in sents)
        tot += n
        print('  %5d 字  %s' % (n, c.split('\n', 1)[0].lstrip('# ')[:44]))
print('  合计 %d 字' % tot)


def rx(t):
    m = re.match(r'^/([\s\S]*)/([a-z]*)$', t)
    if not m:
        return None
    fl = 0
    for ch in m.group(2):
        fl |= {'i': re.I, 'm': re.M, 's': re.S}.get(ch, 0)
    try:
        return re.compile(m.group(1), fl)
    except re.error:
        return None


RX = {}


def hit(words, typ, msg):
    if not words:
        return False
    res = []
    for w in words:
        if w not in RX:
            RX[w] = rx(w) if w.startswith('/') else None
        r = RX[w]
        res.append(bool(r.search(msg)) if r else (w in msg))
    return all(res) if typ == 'AND' else any(res)


def woke(msgs):
    """msgs：从旧到新 [(role, text)]。照扫描深度圈最近 N 条，按范围挑，一条一条单独判。"""
    out = []
    for e in lb:
        if not e.get('enabled', True):
            continue
        d = e.get('scanDepth', 1) or 1
        rng = e.get('triggerRange') or []
        ok = False
        for role, t in msgs[-d:]:
            if role not in rng:
                continue
            if hit(e.get('triggerWords'), e.get('triggerWordsType', 'OR'), t) and not hit(e.get('blackListWords'), e.get('blackListWordsType', 'OR'), t):
                ok = True
                break
        if ok:
            out.append(e)
    return out


def kind(e):
    t = body(e).split('\n', 1)[0]
    f = e.get('folder') or ''
    for k in ['主线', '旅途同行·背景', '旅途同行', '羁绊', '人物', '地点', '城邦', '城区', '支线', '凡世至强', '史诗', '规则', '风土', '灾祸之兽']:
        if k in t[:24]:
            return k
    m = re.match(r'\s*(\d+)·?([^｜|]*)', f)
    if m and int(m.group(1)) == 49:
        return '命星'
    return '底卡' if fno(e) < 40 else (f.split('｜')[-1] or '别的')


HUD = '§底座｜纪元：月银纪1690年·坠叶月·上旬三日 · 18:40 · 千穗国·双虹城·南桥河滩 · 万兽·焚原·一幕 · 防抢话：开 · 档位：长'
OPEN = '纪元：月银纪｜开局时段：万兽·焚原\n\n命途已确认，请为我降下旅印。\n\n【一·灵魂形态】\n降临之魂'
REPLY_LIGHT = HUD + '\n§正文\n河滩上的火堆一堆挨着一堆。南桥门楼边的木板上钉着一张悬赏，领主哈罗德站在门楼底下。城门边坐着一个种麦的，拿镰刀尖往半截仓签上刻道。风里有焦麦的气味，逃过来的人只说三个字，一声王。'
REPLY_HEAVY = REPLY_LIGHT + '罗南在南门的门楼里磨枪，霍布把粮车赶过河滩，菲娅和她父亲睡在城墙外头。灰岭的奥斯温带着十二盾下了高地，拉格娜光着脚跟在后头。麦伦没有抬头。远处的天是红的，那是焚原。\n§推演｜3｜麦伦（锚定源：旅伴）｜罗南（锚定源：旅伴）｜哈罗德（锚定源：人物）'
USER2 = '我走到城门边，在那个刻仓签的人旁边坐下，问他刻的是什么。'
for label, reply in [('回复里只提到两三个人', REPLY_LIGHT), ('回复里七个旅伴都写到了', REPLY_HEAVY)]:
    w = woke([('user', OPEN), ('assistant', reply), ('user', USER2)])
    by = collections.Counter()
    n = collections.Counter()
    for e in w:
        by[kind(e)] += han(body(e))
        n[kind(e)] += 1
    print('\n== 四、焚原一幕第二轮（%s）：叫醒 %d 条，正文 %.1f 万字' % (label, len(w), sum(by.values()) / 1e4))
    print('   ' + '，'.join('%s %d 条 %.1f 万' % (k, n[k], v / 1e4) for k, v in by.most_common(14)))
