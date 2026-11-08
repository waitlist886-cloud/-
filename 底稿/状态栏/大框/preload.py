# 11-08 底层推演加强（底层推演加强_方向稿.md 第二节，用户：三个方向稿都按倾向写入）：回复最后一行 §预载｜名、名…，下一轮叫醒那几条。
# 底卡只扫玩家的 830 条里，世界里的东西（城市据点、自然地理、聚落支线、大型自然区、高危区域、主城三幕、羁绊、人物、同行、凡世至强、公会迷宫、怪物）
# 和隐藏真相那一组（第六节第2件：让 AI 预载，只认回复那一侧的预载行）照丙改成两边都扫，触发换成两支正则，正文不动：
#   回复那一侧只认预载行：/§预载｜[^\n]{0,400}(?:名1|名2|…)/ ，正文里顺口提到不算，不会连锁；
#   玩家那一侧照旧认裸词，只认不是回复的消息：/^(?![\s\S]{0,4000}(?:§底座|§推演|hud-meta|<details))[\s\S]{0,3000}(?:名1|名2|…)/
#   平台一条消息一条消息分开扫，^ 认得出消息开头（10-13 探针三 R12 那一条就是这么写的，canon/README.md）。
# 规则类（数值、命路、种族、历史、职业、货币、势力、神祇……）照甲不动。打包时拿每条的条目名写进一行 §预载 试一遍，叫不醒的列出来。
import re

FOLDERS = ['13·城市、据点与设施', '14·自然地理与遗址', '24·地方聚落支线', '25·大型自然区探索', '26·高危区域探索主线', '23·主城三幕主线',
           '27·人物羁绊剧情', '15·人物与旅途同行', '15·同行、旅伴与队伍', '16·凡世至强与传奇', '17·公会、迷宫与探索', '18·怪物生态与史诗战',
           '03·隐藏真相与终局']
NOT_REPLY = r'(?![\s\S]{0,4000}(?:§底座|§推演|hud-meta|<details))'
SPECIAL = set('\\^$.|?*+()[]{}/')


def esc(w):
    return ''.join('\\' + ch if ch in SPECIAL else ch for ch in w)


def title_of(content):
    first = (content or '').lstrip().split('\n', 1)[0]
    t = re.sub(r'^#+\s*', '', first).strip()
    t = re.sub(r'（[^）]*）|\([^)]*\)', '', t).strip()
    t = t.split('｜')[-1].strip()
    return t if 1 < len(t) <= 16 else ''


def names_of(content):
    """条目名和它用「·」分开的几段（迷宫都市·阿卡迪亚 → 迷宫都市·阿卡迪亚、迷宫都市、阿卡迪亚），模型写预载多半写短的那一段"""
    t = title_of(content)
    if not t:
        return []
    out = [t] + [x for x in re.split(r'[·]', t) if len(x) >= 2]
    return list(dict.fromkeys(out))


def apply(lb, nb):
    """改触发，返回（只扫玩家改成两边扫的条数，两边扫的添了一支预载的条数）"""
    n = n2 = 0
    for i in range(nb):
        e = lb[i]
        if e.get('folder') not in FOLDERS or (e.get('triggerWordsType') or 'OR') != 'OR':
            continue
        words = [w for w in e.get('triggerWords') or [] if w]
        if not words or any(w.startswith('/§预载') for w in words):
            continue
        names = [x for x in names_of(e.get('content')) if x not in words]
        if e.get('triggerRange') == ['user'] and not any(w.startswith('/') for w in words):
            alt = '|'.join(esc(w) for w in words)
            ralt = '|'.join(esc(w) for w in words + names)
            e['triggerWords'] = [r'/§预载｜[^\n]{0,400}(?:%s)/' % ralt, r'/^%s[\s\S]{0,3000}(?:%s)/' % (NOT_REPLY, alt)]
            e['triggerRange'] = ['user', 'assistant']
            e['scanDepth'] = max(int(e.get('scanDepth') or 1), 2)
            n += 1
        elif 'assistant' in (e.get('triggerRange') or []) and names and len(words) < 20:
            # 本来就两边扫、可是认的是「X是什么」这类问句的（几座大城），添一支只认预载行的
            e['triggerWords'] = words + [r'/§预载｜[^\n]{0,400}(?:%s)/' % '|'.join(esc(x) for x in names)]
            e['scanDepth'] = max(int(e.get('scanDepth') or 1), 2)
            n2 += 1
    return n, n2


def _rx(w):
    m = re.match(r'^/(.*)/([a-z]*)$', w, re.S)
    if not m:
        return None
    fl = 0
    for ch in m.group(2):
        fl |= {'i': re.I, 'm': re.M, 's': re.S}.get(ch, 0)
    return re.compile(m.group(1).replace('\\/', '/'), fl)


def hit(w, text):
    r = _rx(w)
    return bool(r.search(text)) if r else (w in text)


def fires(e, text, role):
    if role not in (e.get('triggerRange') or []):
        return False
    tw = [w for w in e.get('triggerWords') or [] if w]
    if not tw:
        return False
    ok = all(hit(w, text) for w in tw) if e.get('triggerWordsType') == 'AND' else any(hit(w, text) for w in tw)
    if not ok:
        return False
    bl = [w for w in e.get('blackListWords') or [] if w]
    if bl:
        blocked = all(hit(w, text) for w in bl) if e.get('blackListWordsType') == 'AND' else any(hit(w, text) for w in bl)
        if blocked:
            return False
    return True


BASE_REPLY = '§底座｜纪元：迷宫纪1001年·春·萌芽月·中旬三日 · 09:20 上午 · 晨曦帝国·金鸢城·外城 · 第一兆·魔兽离巢·起潮 · 防抢话 开 · 档位 很长\n§环境｜晴｜钟声\n§正文｜金鸢城\n她把信收好。\n'


def simulate(lb, nb):
    """底卡里两边都扫的条目，拿条目名写进一行 §预载，叫不醒的列出来；改过的那几条另核：正文里提到不醒、玩家的话照旧醒"""
    miss, checked = [], 0
    leak = []
    for i in range(nb):
        e = lb[i]
        if 'assistant' not in (e.get('triggerRange') or []):
            continue
        t = title_of(e.get('content'))
        if not t:
            continue
        checked += 1
        if not fires(e, BASE_REPLY + '§预载｜%s\n' % t, 'assistant'):
            miss.append((i, e.get('folder'), t))
        tw = e.get('triggerWords') or []
        if len(tw) == 2 and tw[0].startswith('/§预载｜'):
            w0 = re.search(r'\(\?:([^)]*)\)/$', tw[1]).group(1).split('|')[0].replace('\\', '')
            if fires(e, BASE_REPLY + w0 + '。\n', 'assistant'):
                leak.append((i, '回复正文里提到也醒了', w0))
            if not fires(e, '我想去看看' + w0 + '。', 'user'):
                leak.append((i, '玩家的话叫不醒', w0))
    return checked, miss, leak
