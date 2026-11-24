#!/usr/bin/env python3
# 大图书馆打数据（11-24，门面第二轮）。只用标准库。
#   python -I -X utf8 底稿/门面/共用/build_lib.py            读 底稿/门面/第二轮/大图书馆/书稿/*.md，出 共用/data/lib/index.json 和一本一份 <书键>.json，末尾自查
#   python -I -X utf8 底稿/门面/共用/build_lib.py --check    只自查，不写盘
# 书稿体例见 大图书馆/派活说明_头一批.md 第三节，剧透三种写法见 收稿记录_第二批.md 第四节末，怎么接进门面见 大图书馆/门面接入_说明.md。
#   厅：照文件名前缀（圆厅_→yuan……），廊_往前往后.md 拆成 past、future 两处，只进 index.json（书抽不出来，没有单本）。
#   书键：厅键加书名的拼音首字母（GB2312 一级字按拼音排，取得到首字母；二级字和别的字记 x），撞了加两位哈希。书名不改，键就不变。
#   971 上中下合成一本三册（目录分册，注号各册分开），大兽志五本、两本神谱各自一本，带 set、seq 挨着放。
#   〔正文取自 <路径> 「<标题>」，……〕：从源稿取那一条（照写明的栏，【调用】、锁、条目设置、只给 AI 起头的行、作者记号都不取，写明不取的句子拿掉）；
#   〔正文取自卡里……〕（不带路径的）后头已经抄了正文，只把这一行指针拿掉。设计备注不进。
import hashlib
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, '底稿', '门面', '第二轮', '大图书馆', '书稿')
CAT = [os.path.join(ROOT, '底稿', '门面', '第二轮', '大图书馆_书目_第二版.md'), os.path.join(ROOT, '底稿', '门面', '第二轮', '大图书馆_书目_第三版.md')]
OUT = os.path.join(HERE, 'data', 'lib')

# 厅：键、文件名前缀、名字、拱门上那一句题记（门面的字，咏唱的口气，不点执政的名）
HALLS = [
    ('yuan', '圆厅', '圆厅', '进门先数一遍。七纪的年数，摊在一张长桌上'),
    ('ming', '命路厅', '命路厅', '二十三条路，一路一卷。怎么握，怎么站，死在哪里'),
    ('shen', '神与魔神厅', '神与魔神厅', '坐过坛的，倒在墙下的，一位一位都记了名'),
    ('moon', '月银纪廊', '月银纪廊', '兽皮缝的册子，月银粉写的字，暗处发冷白的光'),
    ('strife', '纷争纪廊', '纷争纪廊', '炭笔写在战报纸上，有的页上溅着泥和血'),
    ('bronze', '山铜纪廊', '山铜纪廊', '碑拓裱成册，黑底白字，背面的名字一个一个都是人'),
    ('maze', '迷宫纪廊', '迷宫纪廊', '委托单穿绳装订，越往后纸越好，字越密'),
    ('arcane', '奥法与工程厅', '奥法与工程厅', '先算，再做。做出第二台，才算真的'),
    ('crown', '星冠圣堂厅', '星冠圣堂厅', '七十二殿的祷书，描金的羊皮纸，一殿一卷'),
    ('craft', '行当的歌', '行当的歌', '抡锤的，放绳的，吹号的，干活时嘴里哼的那几句'),
    ('child', '孩子的一架', '孩子的一架', '书角都卷着，是翻得最多的那几本'),
    ('stage', '戏台与说书', '戏台与说书', '往事上了台，唱大了，也唱远了'),
    ('past', '', '往前的廊', '书脊是烫的，抽不出来'),
    ('future', '', '往后的廊', '书脊一格比一格白，最末一格空着'),
]
HALL_DEFAULT_PAPER = {'yuan': 'bone', 'ming': 'print', 'shen': 'vellum', 'moon': 'hide', 'strife': 'report', 'bronze': 'ledger',
                      'maze': 'print', 'arcane': 'type', 'crown': 'vellum', 'craft': 'hide', 'child': 'kid', 'stage': 'bill'}
# 装帧那一行里的字 → 纸（先看到哪一样算哪一样，排在前头的优先）
PAPER_KEYS = [('bill', ['戏单', '彩印', '戏本']), ('type', ['打字机']), ('rubbing', ['碑拓', '拓片', '拓本', '拓下', '拓的']),
              ('report', ['战报纸', '炭笔']), ('form', ['委托单']), ('annal', ['编年院']), ('vellum', ['羊皮纸', '描金']), ('hide', ['兽皮', '鞣过的', '鹿皮']),
              ('ledger', ['账本', '账簿', '账页', '账纸', '格子纸']), ('print', ['铅印', '印刷', '钢版']), ('bone', ['骨白'])]
SETS = {'dashou': '大兽志', 'shenpu': '神谱'}

NUM = '[一二三四五六七八九十百零〇两0-9]+'
CN = {'〇': 0, '零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}


def cnum(s):
    if s.isdigit():
        return int(s)
    tot, cur = 0, 0
    for ch in s:
        if ch in CN:
            cur = CN[ch]
        elif ch == '十':
            tot += (cur or 1) * 10; cur = 0
        elif ch == '百':
            tot += (cur or 1) * 100; cur = 0
    return tot + cur


# ---------- 书键：拼音首字母（GB2312 一级字是照拼音排的） ----------
_BOUND = [(0xB0A1, 'a'), (0xB0C5, 'b'), (0xB2C1, 'c'), (0xB4EE, 'd'), (0xB6EA, 'e'), (0xB7A2, 'f'), (0xB8C1, 'g'), (0xB9FE, 'h'), (0xBBF7, 'j'),
          (0xBFA6, 'k'), (0xC0AC, 'l'), (0xC2E8, 'm'), (0xC4C3, 'n'), (0xC5B6, 'o'), (0xC5BE, 'p'), (0xC6DA, 'q'), (0xC8BB, 'r'), (0xC8F6, 's'),
          (0xCBFA, 't'), (0xCDDA, 'w'), (0xCEF4, 'x'), (0xD1B9, 'y'), (0xD4D1, 'z'), (0xD7FA, None)]


def initial(ch):
    if ch.isascii():
        return ch.lower() if ch.isalnum() else ''
    try:
        b = ch.encode('gb2312')
    except UnicodeEncodeError:
        return 'x'
    if len(b) != 2:
        return ''
    code = b[0] << 8 | b[1]
    if code < 0xB0A1 or code >= 0xD7FA:
        return 'x' if code >= 0xD7FA else ''
    last = 'a'
    for c, l in _BOUND:
        if code < c:
            return last
        last = l
    return 'x'


def book_key(hall, title, used):
    base = re.sub(r'[（(][上中下][)）]$', '', title)
    k = hall + '-' + (''.join(initial(c) for c in base)[:14] or 'b')
    if k in used:
        k = k + hashlib.sha1(title.encode('utf-8')).hexdigest()[:2]
    used.add(k)
    return k


# ---------- 作者记号（照 out/进卡_v12/tools/build_v12.py 的 strip_marks） ----------
AUTHOR_MARK = re.compile(r'（[★#][^）]*）')
AUTHOR_TAIL = re.compile(r'（([^（）]*?)[，、]\s*★）')
AUTHORISH = re.compile(r'(?:页[一二三四五六七八九十]|第[一二三四五六七八九十]+[页歌份]|歌|[^（）]*的年月|介绍页|碑第一版|台词试稿|总表[^（）]*|方向[^（）]*|计划[^（）]*|接?底卡[^（）]*|[^（）]*#\d[^（）]*)')
PAGE_REF = re.compile(r'（(?:(?:页[一二三四五六七八九十]+|第[一二三四五六七八九十]+[页歌](?:第\d+行)?|总表|介绍页)[、，]?)+）')


def _author_tail(m):
    inner = m.group(1).strip()
    if not inner or AUTHORISH.fullmatch(inner):
        return ''
    return '（' + inner + '）'


def strip_marks(t):
    t = AUTHOR_TAIL.sub(_author_tail, t)
    t = PAGE_REF.sub('', t)
    return AUTHOR_MARK.sub('', t).replace('★', '')


def strip_star(t):          # 书稿自己的字：只拿掉（★）和★
    return AUTHOR_MARK.sub('', t).replace('★', '')


ISSUES = []        # (书, 级别, 话)


def issue(book, lvl, msg):
    ISSUES.append((book, lvl, msg))


# ---------- 〔正文取自 …〕 ----------
SRC_CACHE = {}


def src_lines(rel):
    p = os.path.join(ROOT, rel.replace('/', os.sep))
    if p not in SRC_CACHE:
        SRC_CACHE[p] = open(p, encoding='utf-8').read().split('\n') if os.path.exists(p) else None
    return SRC_CACHE[p]


def find_entry(lines, title):
    hs = [(i, len(m.group(1)), m.group(2).strip()) for i, l in enumerate(lines) for m in [re.match(r'^(#{1,6})\s+(.*)$', l)] if m]
    tail = title.split('｜')[-1]
    hit = None
    for i, lv, h in hs:
        if h == title:
            hit = (i, lv); break
    if not hit:
        for i, lv, h in hs:
            if h.split('｜')[-1] == tail:
                hit = (i, lv); break
    if not hit:
        return None
    i, lv = hit
    end = len(lines)
    for j, lv2, _ in hs:
        if j > i and lv2 <= lv:
            end = j; break
    return lines[i + 1:end]


def clean_entry(body):
    """拿掉【调用】那一段、条目设置、只给 AI 起头的行。"""
    out, skip = [], False
    for l in body:
        s = l.strip()
        if s.startswith('【调用】'):
            skip = True; continue
        if skip:
            if not s:
                skip = False
            continue
        if s.startswith('> 条目设置') or s.startswith('条目设置：'):
            continue
        if re.match(r'^(?:[-*>]\s*)?只给\s*AI', s):
            continue
        out.append(l.rstrip())
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def parse_fields(body):
    """源稿一条里的栏：顶格的「- 名：……」（下面缩进的接着算），和「### 名」小节。按出现的先后。"""
    fields, cur = [], None
    i = 0
    while i < len(body):
        l = body[i]
        m = re.match(r'^- ([^：｜\s]{1,12})[：｜]\s?(.*)$', l)
        h = re.match(r'^#{3,4}\s+(.*)$', l)
        if m:
            cur = {'name': m.group(1), 'kind': 'li', 'lines': [m.group(2)]}; fields.append(cur)
        elif h:
            cur = {'name': h.group(1).strip(), 'kind': 'h', 'lines': []}; fields.append(cur)
        elif cur is not None:
            if cur['kind'] == 'li':
                if l.startswith((' ', '\t')):
                    cur['lines'].append(l)
                elif not l.strip():
                    nxt = next((x for x in body[i + 1:] if x.strip()), '')
                    if nxt.startswith((' ', '\t')):
                        cur['lines'].append('')
                    else:
                        cur = None
                else:
                    cur = None
            else:
                cur['lines'].append(l)
        i += 1
    for f in fields:
        while f['lines'] and not f['lines'][-1].strip():
            f['lines'].pop()
        while f['kind'] == 'h' and f['lines'] and not f['lines'][0].strip():
            f['lines'].pop(0)
    return fields


QUOTE = re.compile(r'“([^”]*)”')


def expand_pointer(book, line):
    m = re.search(r'〔正文取自\s*(\S+?\.md)\s*「([^」]+)」(.*)〕\s*$', line)
    if not m:
        return None
    rel, title, spec = m.group(1), m.group(2), m.group(3).lstrip('，, ')
    lines = src_lines(rel)
    if lines is None:
        issue(book, '错', '取文：源稿不在 %s' % rel); return ['〔此处正文缺页〕']
    body = find_entry(lines, title)
    if body is None:
        issue(book, '错', '取文：%s 里找不到「%s」' % (rel, title)); return ['〔此处正文缺页〕']
    before, _, after = spec.partition('一字不改')
    before = before.rstrip('，, ')
    body = [strip_marks(l) for l in clean_entry(body)]
    drop_lock = '锁不取' in after or '锁、' in after
    if not before:
        out = []
        fields = parse_fields(body)
        lock_names = {'锁', '裁定锁'}
        skip = False
        for l in body:
            if drop_lock and (re.match(r'^- (?:裁定)?锁[：｜]', l) or re.match(r'^#{2,4}\s*裁定锁', l)):
                skip = True; continue
            if skip:
                if l.startswith((' ', '\t')) or (not l.strip()):
                    continue
                skip = False
            out.append(re.sub(r'^(#{3,5})\s', lambda mm: '#' * min(6, len(mm.group(1)) + 1) + ' ', l))
        parts = [{'name': '', 'kind': 'raw', 'lines': out}]
    else:
        fields = parse_fields(body)
        names = [f['name'] for f in fields]
        rng = re.match(r'^(.+?)到(.+?)的?[一二三四五六七八九十两]+[栏样]$', before)
        if rng:
            a, b = rng.group(1), rng.group(2)
            a = a if a in names or a + '的' not in names else a + '的'
            b = b if b in names or b + '的' not in names else b + '的'
            if a in names and b in names:
                want = names[names.index(a):names.index(b) + 1]
            else:
                want = []; issue(book, '错', '取文：「%s」栏的范围 %s 到 %s 对不上（有 %s）' % (title, a, b, '、'.join(names)))
        else:
            lst = re.sub(r'的?[一二三四五六七八九十两]+[栏样]$', '', before)
            want = [x.strip() for x in lst.split('、') if x.strip()]
            want = [w if w in names or w + '的' not in names else w + '的' for w in want]
            for w in want:
                if w not in names:
                    issue(book, '错', '取文：「%s」没有「%s」这一栏（有 %s）' % (title, w, '、'.join(names)))
        parts = [f for f in fields if f['name'] in want]
    # 写明不取的句子
    qs = list(QUOTE.finditer(after))
    for k, q in enumerate(qs):
        tail = after[q.end():q.end() + 6]
        if tail.startswith('里“') or tail.startswith('一句里“'):
            continue          # 这一句是外头那一层，拿掉的是里头那一截
        x = q.group(1)
        trunc = after[max(0, q.start() - 1):q.start()] == '自' and re.match(r'^起到[^，。“]*末尾', after[q.end():])
        done = False
        for f in parts:
            for li, l in enumerate(f['lines']):
                if x in l:
                    if trunc:
                        f['lines'][li] = l[:l.index(x)].rstrip()
                        f['lines'][li + 1:] = []
                    else:
                        f['lines'][li] = l.replace(x, '', 1)
                    done = True; break
            if done:
                break
        if not done:
            issue(book, '错', '取文：「%s」里没找到要拿掉的“%s”' % (title, x[:30]))
    out = []
    for f in parts:
        ls = [re.sub(r'[ \t]+$', '', re.sub(r'(?<=[。，、])\s+(?=\S)', '', l)) for l in f['lines']]
        ls = [l.replace('。。', '。').replace('，。', '。') for l in ls]
        if f['kind'] == 'raw':
            out += ls
        elif f['kind'] == 'li':
            if not ''.join(ls).strip():
                continue
            out.append('- %s｜%s' % (f['name'], ls[0].strip()) if ls[0].strip() else '- %s｜' % f['name'])
            out += ls[1:]
        else:
            if out:
                out.append('')
            out.append('#### ' + f['name'])
            out.append('')
            out += ls
            out.append('')
    text = strip_marks('\n'.join(out))
    for w in ('只给 AI', '只给AI', 'NPC', '【调用】', '条目设置', '不裁定', 'AI 不', '叙述不'):
        if w in text:
            issue(book, '提醒', '取文：「%s」取出来的字里还有“%s”' % (title, w))
    return text.split('\n')


# ---------- 行内 ----------
PLATE_LABEL = re.compile(r'^((?:扉页|附卷|末[一二三四五六七八九十]?|往下[一二三四五六七八九十]+|第[一二三四五六七八九十百]+页|[上下])?(?:图|谱|纸环|木刻|半幅|插页|幅|钱|页)[一二三四五六七八九十百零〇0-9之]*)：(.+)$')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


class Ctx:
    def __init__(self, book):
        self.book = book
        self.part = ''          # 971 三册各自的注号前缀
        self.refs = []          # (注 id)
        self.notes = {}


def note_id(ctx, mark):
    return (ctx.part or 'n') + str(cnum(mark))


def il(ctx, s, inline_spoil=True):
    """一段字变成 html。〔注N〕上标，〔剧透〕（行中）以后这一截是剧透，〔涂黑〕画一道黑，别的〔……〕是书里的记号。"""
    s = strip_star(s)
    if inline_spoil and '〔剧透〕' in s:
        i = s.index('〔剧透〕')
        a, b = s[:i], s[i + 4:]
        return il(ctx, a, False) + '<span class="lx-isp"><span class="lx-ispc">' + il(ctx, b, False) + '</span></span>' if b.strip() else il(ctx, a, False)
    out, pos = [], 0
    for m in re.finditer(r'〔([^〔〕]*)〕|\*\*([^*]+)\*\*', s):
        out.append(esc(s[pos:m.start()]))
        pos = m.end()
        if m.group(2) is not None:
            out.append('<b>' + il(ctx, m.group(2), False) + '</b>'); continue
        inner = m.group(1)
        nm = re.fullmatch('注(' + NUM + ')', inner)
        if nm:
            nid = note_id(ctx, nm.group(1)); ctx.refs.append(nid)
            out.append('<sup class="lx-fn" data-n="%s">%s</sup>' % (nid, esc(inner)))
        elif inner == '涂黑':
            out.append('<span class="lx-blk" title="涂黑"></span>')
        elif inner == '剧透':
            continue
        elif PLATE_LABEL.match(inner):
            out.append('<span class="lx-mk lx-fig">〔' + esc(inner) + '〕</span>')
        else:
            out.append('<span class="lx-mk">〔' + esc(inner) + '〕</span>')
    out.append(esc(s[pos:]))
    return ''.join(out)


def li_html(ctx, s):
    s2 = s
    sp = False
    if re.match(r'^(?:〔注' + NUM + '〕)*〔剧透〕', s2):
        sp = True; s2 = s2.replace('〔剧透〕', '', 1)
    m = re.match(r'^([^｜：。，“”〔]{1,14})｜(.*)$', s2)
    if m:
        h = '<b class="lx-lb">' + il(ctx, m.group(1)) + '</b>' + il(ctx, m.group(2))
    else:
        h = il(ctx, s2)
    return h, sp


def lead_spoil(s):
    """段首写〔剧透〕（前头可以有注号、加粗）：这一段整段是剧透。返回 (去掉记号的字, 是不是)"""
    m = re.match(r'^((?:〔注' + NUM + r'〕|\*\*)*)〔剧透〕', s)
    if m:
        return s[:m.end(1)] + s[m.end():], True
    return s, False


# ---------- 一节正文 → 块 ----------
def to_blocks(ctx, lines):
    blocks = []
    scope = []          # 剧透管到哪：('h', 标题级) 管到同级以上的标题；('any',) 管到下一个标题；('x',) 取文那一整块
    para, quote, table, lst = [], [], [], None

    def sp():
        return 1 if scope else 0

    def flush():
        nonlocal para, quote, table, lst
        if para:
            first, s = lead_spoil(para[0])
            rows = [first] + para[1:]
            blocks.append({'k': 'p', 'h': '<br>'.join(il(ctx, r) for r in rows), 's': 1 if (s or scope) else 0})
            para = []
        if quote:
            first, s = lead_spoil(quote[0])
            blocks.append({'k': 'q', 'h': '<br>'.join(il(ctx, r) for r in [first] + quote[1:]), 's': 1 if (s or scope) else 0})
            quote = []
        if table:
            rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in table]
            hd = len(table) > 1 and re.match(r'^\|?\s*:?-{2,}', table[1].strip()) is not None
            rows = [r for k, r in enumerate(rows) if not (hd and k == 1)]
            out, s_any = [], 0
            for r in rows:
                cells, rs = [], 0
                for c in r:
                    c2, s = lead_spoil(c)
                    rs = rs or s
                    cells.append(il(ctx, c2))
                out.append({'c': cells, 's': 1 if rs else 0})
            blocks.append({'k': 'tb', 'r': out, 'hd': 1 if hd else 0, 's': sp()})
            table = []
        if lst is not None:
            blocks.append(lst); lst = None

    for raw in lines:
        l = raw.rstrip()
        s = l.strip()
        if s == '\x01SB':
            flush(); scope.append(('x',)); continue
        if s == '\x01SE':
            flush()
            while scope and scope[-1] != ('x',):
                scope.pop()
            if scope:
                scope.pop()
            continue
        if not s:
            flush(); continue
        hm = re.match(r'^(#{3,6})\s+(.*)$', l)
        if hm:
            flush()
            lv = len(hm.group(1))
            while scope and scope[-1][0] in ('h', 'any') and (scope[-1][0] == 'any' or scope[-1][1] >= lv):
                scope.pop()
            t = hm.group(2)
            hs = '〔剧透〕' in t
            t = t.replace('〔剧透〕', '').strip()
            if hs:
                scope.append(('h', lv))
            blocks.append({'k': 'h3' if lv == 3 else 'h4', 'h': il(ctx, t), 's': sp()})
            continue
        if s == '〔剧透〕':
            flush(); scope.append(('any',)); continue
        if re.fullmatch(r'(?:〔注' + NUM + r'〕)+', s):          # 单独一行的注号：接在上一段末尾
            if para:
                para[-1] += s; continue
            if quote:
                quote[-1] += s; continue
            if lst is not None and lst['i']:
                lst['i'][-1]['h'] += il(ctx, s); continue
            if blocks and blocks[-1]['k'] in ('p', 'q', 'mk', 'fig'):
                blocks[-1]['h'] += il(ctx, s); continue
            if blocks and blocks[-1]['k'] in ('ul', 'ol') and blocks[-1]['i']:
                blocks[-1]['i'][-1]['h'] += il(ctx, s); continue
        if s.startswith('>'):
            if para or table or lst is not None:
                flush()
            quote.append(s.lstrip('>').strip()); continue
        if s.startswith('|'):
            if para or quote or lst is not None:
                flush()
            table.append(s); continue
        if re.fullmatch(r'-{3,}|\*{3,}|(?:\* ){2,}\*', s):
            flush(); blocks.append({'k': 'hr', 's': sp()}); continue
        mli = re.match(r'^([-*]|\d+[.、])\s+(.*)$', l)
        mind = re.match(r'^\s{2,}([-*]|\d+\.)\s+(.*)$', l)
        if mind and lst is not None and lst['i']:
            h, s2 = li_html(ctx, mind.group(2))
            lst['i'][-1].setdefault('sub', []).append({'h': h, 's': 1 if s2 else 0}); continue
        if mli:
            if para or quote or table:
                flush()
            kind = 'ol' if mli.group(1)[0].isdigit() else 'ul'
            if lst is not None and lst['k'] != kind:
                flush()
            if lst is None:
                lst = {'k': kind, 'i': [], 's': sp()}
                if kind == 'ol':
                    lst['st'] = int(re.match(r'\d+', mli.group(1)).group())
            h, s2 = li_html(ctx, mli.group(2))
            lst['i'].append({'h': h, 's': 1 if s2 else 0}); continue
        if lst is not None and raw.startswith((' ', '\t')) and lst['i']:
            lst['i'][-1]['h'] += '<br>' + il(ctx, s); continue
        if re.fullmatch(r'〔[^〔〕]*〕', s):
            inner = s[1:-1]
            pm = PLATE_LABEL.match(inner)
            if pm or inner.startswith('图：'):
                flush()
                lab, txt = (pm.group(1), pm.group(2)) if pm else ('图', inner[2:])
                v = 'score' if lab.startswith('谱') else 'coin' if lab.startswith('钱') else 'ring' if lab.startswith('纸环') else 'cut'
                blocks.append({'k': 'fig', 'l': esc(lab), 'h': il(ctx, txt), 'v': v, 's': sp()}); continue
            if inner not in ('剧透',) and not re.fullmatch('注' + NUM, inner):
                flush(); blocks.append({'k': 'mk', 'h': il(ctx, s), 's': sp()}); continue
        if quote or table or lst is not None:
            flush()
        para.append(s)
    flush()
    return blocks


def count_chars(blocks):
    n = 0
    for b in blocks:
        for k in ('h',):
            if k in b:
                n += len(re.sub('<[^>]+>', '', b[k]))
        for it in b.get('i', []):
            n += len(re.sub('<[^>]+>', '', it['h']))
        for r in b.get('r', []):
            n += sum(len(re.sub('<[^>]+>', '', c)) for c in r['c'])
    return n


# ---------- 一个书稿文件 ----------
def read_doc(path):
    text = open(path, encoding='utf-8').read().replace('\r\n', '\n')
    lines = text.split('\n')
    title, meta = '', {}
    secs, cur = [], None
    for l in lines:
        if l.startswith('# ') and not title:
            title = l[2:].strip(); continue
        if l.startswith('## '):
            cur = {'t': l[3:].strip(), 'lines': []}; secs.append(cur); continue
        if cur is None:
            m = re.match(r'^>\s*([^｜]{1,4})｜(.*)$', l)
            if m:
                meta[m.group(1)] = m.group(2).strip()
            continue
        cur['lines'].append(l)
    title = re.sub(r'^《(.*)》', r'\1', title)
    return title, meta, secs


def parse_notes(ctx, lines):
    items, cur = [], None
    for l in lines:
        m = re.match(r'^(?:[-*]\s*)?(?:〔注(' + NUM + r')〕|注(' + NUM + r')\s*[：:])\s*(.*)$', l)
        if m:
            cur = [m.group(1) or m.group(2), m.group(3)]; items.append(cur)
        elif cur is not None and l.strip():
            cur[1] += '\n' + l.strip()
    for mark, t in items:
        nid = note_id(ctx, mark)
        by = ''
        mh = re.match(r'^([^。]{2,40}添的[^。]{0,20})。', t)
        if mh:
            by = mh.group(1); t = t[mh.end():].lstrip()
        mm = None if by else re.search(r'（([^（）]*)）\s*$', t)
        if mm and re.search(r'添|青墨|署名|书记|史官|抄|批|记的|写的|管着', mm.group(1)):
            by = mm.group(1); t = t[:mm.start()].rstrip()
        sp = 0
        if '剧透' in by:
            sp = 1; by = re.sub(r'[，、]?剧透开关管着|[，、]?剧透', '', by).strip('，、 ')
        t2, s2 = lead_spoil(t)
        if s2:
            sp = 1; t = t2
        qing = '清点的人' in by or '青墨' in by
        ctx.notes[nid] = {'m': '注' + mark, 'h': '<br>'.join(il(ctx, x) for x in t.split('\n')), 'by': '' if qing else esc(strip_star(by)),
                          'ink': 'qing' if qing else 'late', 's': sp}


def expand_lines(book, lines):
    out = []
    for l in lines:
        if '〔正文取自' in l:
            if re.search(r'〔正文取自\s*\S+?\.md', l):
                pre = l[:l.index('〔正文取自')]
                ex = expand_pointer(book, l)
                if ex is None:
                    issue(book, '错', '取文：指针认不出 %s' % l[:60]); continue
                wrap = '〔剧透〕' in pre
                out.append('')
                if wrap:
                    out.append('\x01SB')
                out += ex
                if wrap:
                    out.append('\x01SE')
                out.append('')
            # 不带路径的（正文取自卡里……）：后头已经抄好了，指针这一行拿掉
            continue
        out.append(l)
    return out


FRONT = {'扉页', '目录', '注脚', '设计备注'}


def build_book(hall, files, key):
    """files: [(路径, 册名或 '')]，一本书一个文件，971 三个。"""
    ctx = Ctx(key)
    book = {'k': key, 'hall': hall, 'fly': [], 'secs': [], 'toc': [], 'notes': {}}
    tocsrc = []
    for pi, (path, part) in enumerate(files):
        title, meta, secs = read_doc(path)
        ctx.part = 'abc'[pi] if len(files) > 1 else ''
        if pi == 0:
            book['t'] = re.sub(r'（[上中下]）$', '', title)
            book['a'] = strip_star(meta.get('作者', ''))
            book['y'] = strip_star(meta.get('成书', ''))
            book['z'] = strip_star(meta.get('装帧', ''))
            book['p'] = strip_star(meta.get('篇幅', ''))
        if part:
            book.setdefault('parts', []).append(part)
        for s in secs:
            name = s['t']
            if name == '扉页':
                for l in s['lines']:
                    t = l.strip()
                    if not t or t.startswith('藏书票'):
                        continue
                    kind = 'h' if re.sub(r'[《》\s]', '', t) == re.sub(r'\s', '', book['t']) else 'l'
                    book['fly'].append([kind, il(ctx, t)])
            elif name == '目录':
                tocsrc.append((pi, s['lines']))
                if 'tocAt' not in book:
                    book['tocAt'] = len(book['secs'])
            elif name == '注脚':
                parse_notes(ctx, s['lines'])
            elif name == '设计备注':
                continue
            else:
                hs = '〔剧透〕' in name
                t = name.replace('〔剧透〕', '').strip()
                lines = expand_lines(key, s['lines'])
                blocks = to_blocks(ctx, lines)
                if hs:
                    for b in blocks:
                        b['s'] = 1
                sec = {'t': il(ctx, t), 'b': blocks}
                if part:
                    sec['pt'] = pi
                if hs:
                    sec['s'] = 1
                book['secs'].append(sec)
    book['notes'] = ctx.notes
    # 目录：书上写的那一份，一行一行对到正文的节（## 一节，或节里的 ### 小标题）
    norm = lambda x: re.sub(r'[\s　｜|：:·，。、（）()《》“”]', '', re.sub(r'<[^>]+>', '', x))
    seg = lambda x: re.split(r'[\s　｜|：:]', re.sub(r'<[^>]+>', '', x).strip())[0]
    tg = []          # (节, 块 或 -1, 规整后的字, 头一截)
    for i, s in enumerate(book['secs']):
        tg.append((i, -1, norm(s['t']), seg(s['t'])))
        for j, bl in enumerate(s['b']):
            if bl['k'] in ('h3', 'h4'):
                tg.append((i, j, norm(bl['h']), seg(bl['h'])))
    used, last = set(), 0

    def ok(n, sn):
        if not sn or not n:
            return False
        if n == sn:
            return True
        return min(len(n), len(sn)) >= 2 and (n.startswith(sn) or sn.startswith(n))
    for pi, lines in tocsrc:
        for l in lines:
            t = l.strip()
            if not t:
                continue
            m = re.match(r'^(?:[-*]|\d+[.、])\s+(.*)$', t)
            if not m:
                book['toc'].append({'c': il(ctx, t)}); continue
            item = m.group(1)
            n, g = norm(item), seg(item)
            order = list(range(last, len(tg))) + list(range(0, last))
            hit = next((k for k in order if k not in used and ok(n, tg[k][2])), -1)
            if hit < 0 and len(g) >= 2:
                cands = [k for k in order if k not in used and tg[k][3] == g]
                if len(cands) >= 1:
                    hit = cands[0]
            e = {'h': li_html(ctx, item)[0], 'i': -1}
            if l.startswith((' ', '	')):
                e['lv'] = 1
            if hit >= 0:
                used.add(hit); last = hit + 1
                e['i'] = tg[hit][0]
                if tg[hit][1] >= 0:
                    e['b'] = tg[hit][1]
            book['toc'].append(e)
    ents = [e for e in book['toc'] if 'i' in e]
    nhit = sum(1 for e in ents if e['i'] >= 0)
    if ents and nhit < len(ents) / 2:
        issue(key, '提醒', '目录对上正文的不到一半（%d/%d），页面上另附章次' % (nhit, len(ents)))
        book['tocx'] = 1
    if not tocsrc:
        book['tocx'] = 1
    return book, ctx


def paper_of(hall, z):
    if hall in ('child', 'stage'):
        return HALL_DEFAULT_PAPER[hall]
    for p, ws in PAPER_KEYS:
        if any(w in z for w in ws):
            return p
    return HALL_DEFAULT_PAPER.get(hall, 'bone')


def check(book, ctx):
    defined = set(book['notes'])
    refs = ctx.refs
    rs = set(refs)
    miss = sorted(rs - defined)
    orphan = sorted(defined - rs)
    if miss:
        issue(book['k'], '错', '正文引了注脚里没有的：%s' % '、'.join(miss))
    if orphan:
        issue(book['k'], '提醒', '注脚里有、正文没引的：%s' % '、'.join(orphan))
    nb = sum(len(s['b']) for s in book['secs'])
    sp = sum(1 for s in book['secs'] for b in s['b'] if b.get('s')) + sum(1 for s in book['secs'] for b in s['b'] for it in b.get('i', []) if it.get('s'))
    isp = sum(json.dumps(s['b'], ensure_ascii=False).count('class=\\"lx-isp\\"') for s in book['secs'])
    nsp = sum(1 for n in book['notes'].values() if n['s'])
    figs = sum(1 for s in book['secs'] for b in s['b'] if b['k'] == 'fig')
    return {'blocks': nb, 'notes': len(defined), 'refs': len(refs), 'spoil': sp, 'isp': isp, 'nsp': nsp, 'figs': figs,
            'qing': sum(1 for n in book['notes'].values() if n['ink'] == 'qing')}


# ---------- 往前、往后的廊 ----------
def build_corridors(path):
    title, meta, secs = read_doc(path)
    ctx = Ctx('lang'); ctx.part = 'n'
    notes_sec = next((s for s in secs if s['t'] == '注脚'), None)
    if notes_sec:
        parse_notes(ctx, notes_sec['lines'])
    past = {'intro': [], 'eras': [], 'deeper': ''}
    future = {'intro': [], 'slots': [], 'tail': ''}
    for s in secs:
        if s['t'] == '往前的廊':
            era, bk, stage = None, None, 'intro'
            for l in s['lines']:
                t = l.strip()
                m3 = re.match(r'^###\s+(.*)$', l)
                m4 = re.match(r'^####\s+(.*)$', l)
                if m3:
                    nm = m3.group(1).strip()
                    if nm == '再往里':
                        stage = 'deeper'; era = None; continue
                    era = {'n': nm, 'shelf': '', 'books': []}; past['eras'].append(era); bk = None; stage = 'era'; continue
                if m4:
                    bk = {'t': re.sub(r'^《(.*)》$', r'\1', m4.group(1).strip())}; era['books'].append(bk); continue
                if not t:
                    continue
                if stage == 'intro':
                    past['intro'].append(il(ctx, t))
                elif stage == 'deeper':
                    past['deeper'] += il(ctx, t)
                elif bk is None:
                    era['shelf'] += il(ctx, t)
                else:
                    mf = re.match(r'^-\s*([^｜]{1,4})｜(.*)$', t)
                    if mf:
                        f = {'书脊': 'spine', '烫手': 'hot', '摸到': 'touch', '扉页': 'fly'}.get(mf.group(1), mf.group(1))
                        bk[f] = il(ctx, mf.group(2))
        elif s['t'] == '往后的廊':
            for l in s['lines']:
                t = l.strip()
                if not t:
                    continue
                mf = re.match(r'^-\s*([^｜]{1,6})｜(.*)$', t)
                if mf:
                    future['slots'].append({'n': mf.group(1), 'h': il(ctx, mf.group(2)), 'last': 1 if mf.group(1) == '最末一格' else 0})
                elif not future['slots']:
                    future['intro'].append(il(ctx, t))
                else:
                    future['tail'] += il(ctx, t)
    # 注脚挂到书上（青墨的那一句写在指上去的那一张小签上）
    notes = ctx.notes
    for era in past['eras']:
        for bk in era['books']:
            for k in ('touch', 'hot', 'spine', 'fly'):
                for nid in re.findall(r'data-n="([^"]+)"', bk.get(k, '')):
                    bk.setdefault('qn', []).append(notes.get(nid, {}).get('h', ''))
                    bk[k] = re.sub(r'<sup class="lx-fn" data-n="%s">[^<]*</sup>' % nid, '', bk[k])
    for sl in future['slots']:
        for nid in re.findall(r'data-n="([^"]+)"', sl['h']):
            sl['qn'] = notes.get(nid, {}).get('h', '')
            sl['h'] = re.sub(r'<sup class="lx-fn" data-n="%s">[^<]*</sup>' % nid, '', sl['h'])
    return past, future


def cat_order():
    t = ''
    for p in CAT:
        if os.path.exists(p):
            t += open(p, encoding='utf-8').read()
    return t


def main():
    only_check = '--check' in sys.argv
    files = sorted(f for f in os.listdir(SRC) if f.endswith('.md'))
    pre = {p: k for k, p, n, l in HALLS if p}
    groups = {}          # 书 → [(路径, 册)]
    order = []
    for f in files:
        if f == '廊_往前往后.md':
            continue
        p = f.split('_', 1)[0]
        hall = pre.get(p)
        if not hall:
            issue(f, '错', '文件名前缀认不出厅'); continue
        m = re.match(r'^(.*)_([上中下])\.md$', f)
        if m and '971' in f:
            gk = (hall, m.group(1))
            groups.setdefault(gk, []).append((os.path.join(SRC, f), {'上': '上册', '中': '中册', '下': '下册'}[m.group(2)]))
            if gk not in order:
                order.append(gk)
        else:
            gk = (hall, f)
            groups[gk] = [(os.path.join(SRC, f), '')]
            order.append(gk)
    cat = cat_order()
    used, books, stats = set(), [], {}
    for gk in order:
        hall = gk[0]
        fl = sorted(groups[gk], key=lambda x: '上中下'.index(x[1][0]) if x[1] else 0)
        t0 = read_doc(fl[0][0])[0]
        key = book_key(hall, re.sub(r'（[上中下]）$', '', t0), used)
        book, ctx = build_book(hall, fl, key)
        book['paper'] = paper_of(hall, book.get('z', ''))
        book['src'] = [os.path.basename(x[0]) for x in fl]
        stats[key] = check(book, ctx)
        book['n'] = sum(count_chars(s['b']) for s in book['secs'])
        books.append(book)
    # 成套
    for b in books:
        if b['t'].startswith('大兽志'):
            b['set'] = 'dashou'
        elif b['t'].startswith('神谱'):
            b['set'] = 'shenpu'
    # 厅里的先后：照书目第二、三版里书名头一回出现的地方，书目里没有的排后头
    def pos(b):
        for t in (b['t'], b['t'].split('：')[0], b['t'].split('·')[0]):
            i = cat.find('《' + t + '》')
            if i >= 0:
                return i
            i = cat.find('《' + t)
            if i >= 0:
                return i
        return 10 ** 7
    halls = []
    past, future = build_corridors(os.path.join(SRC, '廊_往前往后.md'))
    for k, p, n, line in HALLS:
        hb = [b for b in books if b['hall'] == k]
        hb.sort(key=lambda b: (pos(b), b['src'][0]))
        # 成套的挨着放：套里头一本在哪，整套就在哪
        for sk in SETS:
            ms = [b for b in hb if b.get('set') == sk]
            if len(ms) > 1:
                first = hb.index(ms[0])
                rest = [b for b in hb if b.get('set') != sk]
                hb = rest[:first] + ms + rest[first:]
                for i, b in enumerate(ms):
                    b['seq'] = i + 1
        h = {'k': k, 'n': n, 'line': line, 'books': [{x: b[x] for x in ('k', 't', 'a', 'y', 'z', 'p', 'paper', 'n', 'set', 'seq', 'parts') if x in b} for b in hb]}
        for e, b in zip(h['books'], hb):
            e['sp'] = 1 if (stats[b['k']]['spoil'] or stats[b['k']]['isp'] or stats[b['k']]['nsp']) else 0
        if k == 'past':
            h['past'] = past; h['count'] = sum(len(e['books']) for e in past['eras'])
        elif k == 'future':
            h['future'] = future; h['count'] = len(future['slots'])
        else:
            h['count'] = len(hb)
        halls.append(h)
    index = {'v': 1, 'halls': halls, 'sets': SETS}
    # 图（另一份子任务出，放 共用/assets/lib/）：照目录列一份有哪几张，页面只取列着的，图到了重跑这一支就换上
    AD = os.path.join(HERE, 'assets', 'lib')
    index['assets'] = sorted(f[:-5] for f in os.listdir(AD) if f.endswith('.webp') and os.path.getsize(os.path.join(AD, f)) > 0) if os.path.isdir(AD) else []
    if not only_check:
        os.makedirs(OUT, exist_ok=True)
        for f in os.listdir(OUT):
            if f.endswith('.json'):
                os.remove(os.path.join(OUT, f))
        json.dump(index, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, separators=(',', ':'))
        for b in books:
            json.dump(b, open(os.path.join(OUT, b['k'] + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, separators=(',', ':'))
    # 报
    print('书 %d 本（书稿 %d 个文件），厅 %d 处，往前的廊 %d 本、往后的廊 %d 格' % (len(books), len(files), len(halls), halls[-2]['count'], halls[-1]['count']))
    for h in halls:
        if h['k'] in ('past', 'future'):
            continue
        print('  %-7s %-6s %3d 本' % (h['k'], h['n'], len(h['books'])))
    tot = {k: sum(s[k] for s in stats.values()) for k in ('blocks', 'notes', 'refs', 'spoil', 'isp', 'nsp', 'figs', 'qing')}
    print('合计：段落块 %(blocks)d，注 %(notes)d（青墨 %(qing)d），引注 %(refs)d，剧透块 %(spoil)d、行中剧透 %(isp)d、剧透注 %(nsp)d，图版 %(figs)d' % tot)
    print('图：assets/lib/ 里 %d 张' % len(index['assets']))
    print('取文：%d 处指针，源稿 %d 份' % (sum(open(os.path.join(SRC, f), encoding='utf-8').read().count('〔正文取自') for f in files), len(SRC_CACHE)))
    errs = [x for x in ISSUES if x[1] == '错']
    print('问题：错 %d，提醒 %d' % (len(errs), len(ISSUES) - len(errs)))
    for b, lvl, msg in ISSUES:
        print('  [%s] %s  %s' % (lvl, b, msg))
    if not only_check:
        sz = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
        print('写了 %s（%d 个文件，%.1f MB）' % (OUT, len(books) + 1, sz / 1e6))
    if '--stats' in sys.argv:
        for k, s in stats.items():
            print(k, s)


if __name__ == '__main__':
    main()
