# 潮汐格写漏一个点也认（11-26，玩家反馈：月银纪 1 年祭火·第一堆火，妮欧贝成了卖杂物的店主、旅伴读不到）。
# 玩家用的模型把潮汐格写成「祭火·第一堆火一幕」，主线名和幕中间的「·」没写。全卷一千八百来处触发、黑名单认的是「主线名·」，
# 后头少了那个点，主线条目、纪元钟、旅伴、命星从第三轮起就叫不醒了（头两轮靠凭证里的开局时段醒着），模型只好自己编。
# 这一支把正则里紧跟在名字后头、后面就是 | ) / 的那个「·」放宽成「· 或 一幕到十九幕、幕间、收束」。不加量词，风月的 RE2 也认。
# make_four_era_card.py 在 gate_1125 以后套。
import re

ALT = '(?:·|[一二三四五六七八九十]幕|十[一二三四五六七八九]幕|幕间|收束)'
# 名字后头的「·」：前一个字是汉字或者右括号，后一个字是 | 或 ) 或正则末尾的 /
PAT = re.compile(r'(?<=[一-鿿)])·(?=[|)]|/$)')


def _in_class(s, k):
    """第 k 个字是不是在 [...] 里头"""
    depth, esc = False, False
    for ch in s[:k]:
        if esc:
            esc = False
        elif ch == '\\':
            esc = True
        elif ch == '[' and not depth:
            depth = True
        elif ch == ']' and depth:
            depth = False
    return depth


def widen(w):
    if not (isinstance(w, str) and len(w) > 2 and w.startswith('/') and w.endswith('/')):
        return w
    out, last = [], 0
    for m in PAT.finditer(w):
        if _in_class(w, m.start()):
            continue
        out.append(w[last:m.start()])
        out.append(ALT)
        last = m.end()
    if not out:
        return w
    out.append(w[last:])
    s = ''.join(out)
    re.compile(s[1:-1])
    return s


def apply(lorebook):
    n_e, n_w = 0, 0
    for e in lorebook:
        hit = False
        for k in ('triggerWords',):   # 黑名单不放宽：漏挡只是多醒一回，风月要把黑名单改写成钥匙，放宽了钥匙长到七千字
            ws = e.get(k) or []
            new = [widen(w) for w in ws]
            d = sum(a != b for a, b in zip(ws, new))
            if d:
                e[k] = new
                n_w += d
                hit = True
        n_e += hit
    return n_e, n_w


# ---- 头一轮叫醒这一条主线的旅伴（11-26，同一回反馈：希尔妲头一轮的面板是模型自己编的，20 岁、守火猎手 Rare，卡里是 15 岁、Unique 永燃之心）
# 旅伴条要「纪元」和「名字」同在一条消息里才醒，头一轮只有凭证，凭证里没有旅伴的名字，所以头一轮一个旅伴也醒不了，模型只看得见主线里的一句介绍。
# 照写作口径，主线「碰得上的人」头一条点的就是这一条的旅伴：把这几位旅伴条名字那一格添上这条主线的「开局时段：…」，凭证里纪元和开局时段同在，头一轮就醒。
TITLE = re.compile(r'^# 旅途同行：([^（\n]{2,20})（')


def _opens(e):
    """主线条目触发里「开局时段：…」那几支，原样抠出来（带括号的整组）"""
    out = []
    for w in e.get('triggerWords') or []:
        if not (w.startswith('/') and w.endswith('/')):
            continue
        body = w[1:-1]
        for m in re.finditer(r'开局时段：(?:\(\?:[^()]*\)|[^|()/]+)', body):
            out.append(m.group(0))
    return out


def _first_people(c):
    i = c.find('碰得上的人：')
    if i < 0:
        return ''
    m = re.search(r'\n- ([^\n]+)', c[i:])
    return m.group(1) if m else ''


def opening_companions(lorebook):
    comp = {}   # (纪, 名) → [条目]
    for e in lorebook:
        f = e.get('folder') or ''
        m = TITLE.match(e.get('content') or '')
        if m and '旅伴' in f and (e.get('triggerWordsType') or 'OR') == 'AND':
            era = f.split('·', 1)[1].split('｜')[0] if '·' in f else ''
            comp.setdefault((era, m.group(1)), []).append(e)
    n_line, n_comp, adds = 0, 0, {}
    for e in lorebook:
        f = e.get('folder') or ''
        if '时段主线' not in f:
            continue
        era = f.split('·', 1)[1].split('｜')[0]
        ops = _opens(e)
        bullet = _first_people(e.get('content') or '')
        if not ops or not bullet:
            continue
        hit = False
        for (ce, name), es in comp.items():
            if ce != era:
                continue
            short = name.split('·')[0]
            if name in bullet or (len(short) >= 2 and short in bullet):
                for x in es:
                    adds.setdefault(id(x), (x, []))[1].extend(ops)
                hit = True
        n_line += hit
    for x, ops in adds.values():
        name = TITLE.match(x['content']).group(1)
        short = name.split('·')[0]
        tw = list(x['triggerWords'])
        k = next((j for j, w in enumerate(tw) if w.startswith('/') and w.endswith('/') and (name in w or short in w)), None)
        if k is None:
            continue
        new = [o for o in dict.fromkeys(ops) if o not in tw[k]]
        if not new:
            continue
        tw[k] = tw[k][:-1] + '|' + '|'.join(new) + '/'
        re.compile(tw[k][1:-1])
        x['triggerWords'] = tw
        n_comp += 1
    return n_line, n_comp


# ---- 入局那两轮（11-26，首轮入局分成入局和推开门扉两轮；本地干跑 底稿/收尾_11-26/入局干跑.md）----
# 1. 推开门扉那一轮凭证已经是往回第三条消息，建档那一层（冒险初心、誓心、六维、位阶、数值机制、装备换算、命路倾向、种族、通用 Skill、
#    降临者、各纪建档的种族……）只扫玩家、深度 1 或 2 的叫不醒。凭证叫得醒的这一批扫描深度提到 3：入局、推开门扉两轮都扫得到凭证，再往后就扫不到了。
#    挑法：文件夹 09 以前（加各纪「规则｜建档的种族」），扫玩家，深度 1、2，拿 gate_1125 那四百多种凭证试，醒过一回的。首轮入局驱动、目录条不动。
# 2. 死之执政·若娜瓦：入局是祂在殿里念前半生，凭证进来那一条要醒（认命途已确认）。
def ruju(lb, root):
    import gate_1125 as G25
    creds = [c for _, _, c, _ in G25.creds(root)]

    def fno(e):
        m = re.match(r'(\d+)·', e.get('folder') or '')
        return int(m.group(1)) if m else -1
    deep = 0
    for e in lb:
        head = (e.get('content') or '')[:40]
        if not ((0 < fno(e) <= 9 or '规则｜建档的种族' in head) and 'user' in (e.get('triggerRange') or []) and (e.get('scanDepth') or 1) in (1, 2)):
            continue
        if head.startswith('# 首轮入局驱动') or '目录' in head[:12]:
            continue
        if any(G25._woke(e, c, 'user') for c in creds):
            e['scanDepth'] = 3
            deep += 1
    rn = 0
    for e in lb:
        if (e.get('content') or '').startswith('## 四执政：死之执政·若娜瓦'):
            if '命途已确认' not in e['triggerWords']:
                e['triggerWords'] = e['triggerWords'] + ['命途已确认']
            # 不挂「入局：直接开场」的黑名单：风月把黑名单改写成行内否定，这一条一改连裸打祂的名字都醒不了（11-26 对账）；直接开场的局头一轮多带祂一回
            rn += 1
    assert rn == 1, rn
    return deep


if __name__ == '__main__':
    for t in ['/ · 祭火·|纪元：月银纪(?:\\d{1,3}|1000)年/', '/祭火·第一堆火·|开局时段：祭火·第一堆火/', '/诸国·(?:王道|长冬)·/', '/[甲·]/']:
        w = widen(t)
        print(w)
        r = re.compile(w[1:-1])
        print('  ', bool(r.search('潮汐 祭火·第一堆火一幕')), bool(r.search('祭火·第一堆火·一幕')), bool(r.search('诸国·王道二幕')))
