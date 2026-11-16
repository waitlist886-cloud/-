# 全卡精炼洗稿：照各类条目留几成，估洗完以后卡多大、一轮叫醒多少字。只读卡，不改东西。
#   python -I -X utf8 底稿/洗稿/全卡精炼/wash_estimate.py [卡.json]
# KEEP 是正文留下的比例（方向稿第四节那张表），触发词、黑名单、键名这些照原样算。
# 主线按幕拆出来的那几百段洗完以后撤掉（一条主线三千字上下，不用拆）。
import collections
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH = sys.argv[1] if len(sys.argv) > 1 else 'E:/aldran_art/out/发布卡_四纪大框/奥尔德兰_四纪大框.json'
card = json.load(open(PATH, encoding='utf-8'))
lb = card['prompt']['lorebook']
B = lambda o: len(json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
u8 = lambda s: len(s.encode('utf-8'))
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))
ERAS = ['月银纪', '纷争纪', '山铜纪', '迷宫纪']


def fno(e):
    m = re.match(r'\s*(\d+)', e.get('folder') or '')
    return int(m.group(1)) if m else -1


def text(e):
    if e.get('contentMethod') == 'weighted':
        return ''.join(c.get('content') or '' for c in e.get('contents') or [])
    return e.get('content') or ''


def inject(e):
    """一轮真正进提示词的字：加权条目只抽一条，算平均。"""
    if e.get('contentMethod') == 'weighted':
        cs = e.get('contents') or []
        return sum(han(c.get('content') or '') for c in cs) / max(1, len(cs))
    return han(e.get('content') or '')


SEG = re.compile(r'主线[｜|][^\n]{0,40}·(?:一幕|二幕|三幕|收束|幕间)\s*$')


def kind(e):
    n = fno(e)
    t = text(e).split('\n', 1)[0]
    f = e.get('folder') or ''
    if n < 40:
        return '底卡'
    if n >= 90:
        return '功能与骰表'
    if n == 41:
        return '主线拆出来的段' if SEG.search(t.strip()) else '主线'
    if n == 47:
        return '旅伴背景与旅伴之间' if ('背景' in t[:14] or '旅伴之间' in t[:14]) else '旅伴'
    return {40: '常驻与总纲', 42: '规则', 43: '迷宫遗迹案子与兽', 44: '城邦与城区', 45: '地点', 46: '人物', 48: '势力与国史',
            49: '命星', 50: '史诗碑牌委托', 51: '传奇', 52: '战役与帝国史', 53: '魔法', 54: '风土', 55: '战役与帝国史', 56: '支线',
            57: '羁绊', 58: '神谱', 59: '装备与名器'}.get(n, '别的')


MAIN_HAN = 3200  # 洗完以后一条主线多少字（现在整条八千字上下，拆成骨架加几段）
# 正文留几成
KEEP = {'主线': 0.48, '主线拆出来的段': 0.0, '旅伴': 0.5, '旅伴背景与旅伴之间': 0.7, '羁绊': 0.5, '命星': 0.5, '人物': 0.6, '地点': 0.58,
        '城邦与城区': 0.6, '支线': 0.55, '传奇': 0.65, '势力与国史': 0.7, '迷宫遗迹案子与兽': 0.6, '风土': 0.7, '常驻与总纲': 0.85,
        '神谱': 0.65, '史诗碑牌委托': 1.0, '战役与帝国史': 0.6, '规则': 0.8, '魔法': 0.7, '装备与名器': 0.6, '底卡': 0.85, '功能与骰表': 1.0, '别的': 0.8}
# 这张表照样稿（第七歌一组）实际留下的比例定的：主线 48%、旅伴 52%、背景 73%、命星 46% 到 57%、羁绊 51%、地点 58%

tot = collections.Counter()
con = collections.Counter()
cnt = collections.Counter()
hz = collections.Counter()
for e in lb:
    k = kind(e)
    tot[k] += B(e)
    con[k] += u8(text(e))
    cnt[k] += 1
    hz[k] += han(text(e))
print('%-12s %6s %8s %8s %6s %8s' % ('类', '条', '现在MB', '正文万字', '留', '洗后MB'))
new_total = 0
for k, v in sorted(tot.items(), key=lambda kv: -kv[1]):
    rest = v - con[k]
    if k == '主线拆出来的段':
        nv = 0
    elif k == '主线':
        nv = rest + cnt[k] * MAIN_HAN * 3  # 拆段撤掉以后，一条主线整条写回来，三千字出头
    else:
        nv = rest + con[k] * KEEP[k]
    new_total += nv
    print('%-12s %6d %8.2f %8.1f %6.2f %8.2f' % (k, cnt[k], v / 1e6, hz[k] / 1e4, KEEP[k], nv / 1e6))
old_wb = sum(tot.values())
other = B(card) - B(lb)
print('世界书 现在 %.1f MB，洗后 %.1f MB；世界书以外（样式、规则、提示词、介绍页）%.1f MB' % (old_wb / 1e6, new_total / 1e6, other / 1e6))
MECH = 2.4  # 时段钥匙改短 1.9、旧 HTML 锚 0.3、样式里图地址前缀 0.2（拼装_计划.md 第四节第 7 小节）
print('整张卡 现在 %.1f MB，洗后 %.1f MB，再做机械瘦身（时段钥匙、旧锚、图地址）%.1f MB' % (B(card) / 1e6, (new_total + other) / 1e6, (new_total + other) / 1e6 - MECH))
print('四纪加底卡的正文 现在 %.0f 万字，洗后 %.0f 万字上下' % (sum(hz.values()) / 1e4, (sum(hz[k] * KEEP[k] for k in hz if k != '主线') + cnt['主线'] * MAIN_HAN) / 1e4))


# 一轮叫醒多少字：焚原一幕第二轮
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
    out = []
    for e in lb:
        if not e.get('enabled', True):
            continue
        d = e.get('scanDepth', 1) or 1
        rng = e.get('triggerRange') or []
        for role, t in msgs[-d:]:
            if role in rng and hit(e.get('triggerWords'), e.get('triggerWordsType', 'OR'), t) and not hit(e.get('blackListWords'), e.get('blackListWordsType', 'OR'), t):
                out.append(e)
                break
    return out


HUD = '§底座｜纪元：月银纪1690年·坠叶月·上旬三日 · 18:40 · 千穗国·双虹城·南桥河滩 · 万兽·焚原·一幕 · 防抢话：开 · 档位：长'
OPEN = '纪元：月银纪｜开局时段：万兽·焚原\n\n命途已确认，请为我降下旅印。\n\n【一·灵魂形态】\n降临之魂'
LIGHT = HUD + '\n§正文\n河滩上的火堆一堆挨着一堆。南桥门楼边的木板上钉着一张悬赏，领主哈罗德站在门楼底下。城门边坐着一个种麦的，拿镰刀尖往半截仓签上刻道。风里有焦麦的气味，逃过来的人只说三个字，一声王。'
HEAVY = LIGHT + '罗南在南门的门楼里磨枪，霍布把粮车赶过河滩，菲娅和她父亲睡在城墙外头。灰岭的奥斯温带着十二盾下了高地，拉格娜光着脚跟在后头。麦伦没有抬头。远处的天是红的，那是焚原。\n§推演｜3｜麦伦（锚定源：旅伴）｜罗南（锚定源：旅伴）｜哈罗德（锚定源：人物）'
USER2 = '我走到城门边，在那个刻仓签的人旁边坐下，问他刻的是什么。'
sysp = han(card['prompt'].get('systemPrompt') or '')
print('\n一轮进提示词的字（焚原一幕第二轮，主提示词另有 %.1f 万字）：' % (sysp / 1e4))
for label, reply in [('回复里只写到两三个人', LIGHT), ('回复里七个旅伴都写到了', HEAVY)]:
    w = woke([('user', OPEN), ('assistant', reply), ('user', USER2)])
    a = collections.Counter()
    b = collections.Counter()
    for e in w:
        k = kind(e)
        a[k] += inject(e)
        b[k] += MAIN_HAN if k == '主线' else inject(e) * KEEP[k]
    print('  %s：叫醒 %d 条，现在 %.1f 万字，洗后 %.1f 万字上下' % (label, len(w), sum(a.values()) / 1e4, sum(b.values()) / 1e4))
    print('     ' + '，'.join('%s %.2f→%.2f' % (k, v / 1e4, b[k] / 1e4) for k, v in a.most_common(9)))
