# -*- coding: utf-8 -*-
"""两纪 v8（2026-10-21）：底卡 rili_v7 + 进卡补丁 v8（v7 那二十条、底卡加黑名单两张表、介绍页年表和命星档案）
+ 另两路写的底卡补丁（patch_truth.py、patch_strife.py，落了盘就读）
+ 月银纪第一到三批（退掉被替下的、照改名表换名）+ 十五页万兽史诗 + 六页诸国 + 六页萨尔维斯
+ 纷争纪七页 + 两纪的补卷（萨尔维斯帝国史、月银纪补卷、纷争纪第一项和补卷），
套成一张日里卡，校验，再一条一条消息地模拟触发。
用法：python -I -X utf8 build_moon_v8.py <aldran 根目录> <工作目录> <输出目录> [--fast] [--no-ext]
  --fast   不跑串段和迷宫纪中局那几段最慢的模拟（改脚本时用）
  --no-ext 不读另两路的底卡补丁（那两份还在写的时候用，正式跑别加）
沿用 v7 的口径：一条消息一条消息分开算，AND 和黑名单都跨不了消息，纯词分大小写，正则不许量词套量词、
整条不超过 25 个量词。页上的条目设置照抄成触发词，钥匙别名在这里展开。
v8.1（10-21）：用户导过 v8 以后定的两件，纷争纪 46、47、51 的门控换成在世那几段的时段钥匙（49 跟持有人走），月银纪 46、51 能落的落，
月银纪第一到三批那四十条直醒的改成同时满足〔月银纪·正则〕或那几段的时段钥匙。产物名带 v8.1，同一个目录里 v8 的报告拿来比。
v8 新加的：纷争纪的钥匙（〔纷争纪·正则〕并进山铜纪元年，七把时段钥匙各补第二十二张那一支，二十一把主线钥匙读页上写好的正则），
凡是 (?:<br>|hud-meta">|纪元：) 打头的触发正则也算门控；文件夹 40 到 55 两纪共用一套优先级带；STAR_GATE 第八版（键可以写成 星名@页）；
撞底卡的标题照纪元加（月银纪）（纷争纪）；两纪的开局口令都去叫一遍底卡，叫醒的照纪元加锚。"""
import json, re, sys, os, glob, copy, runpy, collections

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
FLAGS = set(a for a in sys.argv[1:] if a.startswith('--'))
ROOT, WDIR, OUT = ARGS[0], ARGS[1], ARGS[2]
FAST = '--fast' in FLAGS
NO_EXT = '--no-ext' in FLAGS
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src', 'rili_v7.json')
PATCH = os.path.join(HERE, '进卡补丁_rili_v8.py')
EXT_PATCHES = ['patch_truth.py', 'patch_strife.py']
ED = runpy.run_path(os.path.join(HERE, 'batch_edits_v8.py'))
# v8.1（10-21）：用户导过 v8 以后定的两件，时代钥匙，见 v8.1 那一节。v8 的产物留在同一个目录里，报告末尾拿来比。
VERSION = 'v8.1'
OUT_NAME = '奥尔德兰_日里版_两纪全卷_测试%s.json' % VERSION
REPORT_NAME = '%s_report.txt' % VERSION
ENTRIES_NAME = '%s_entries.json' % VERSION
PREV_REPORT = 'v8_report.txt'

SONGS = ['第一歌_灰桥初火', '第二歌_镜中石瞳', '第三歌_鸦栖之石', '第四歌_雷纹豹裘', '第五歌_冰矛抵眉', '第六歌_九步冷泉',
         '第七歌_焚原断刃', '第八歌_未磨白骨', '第九歌_落日之弓', '第十歌_千鼓空角', '第十一歌_天马落羽', '第十二歌_珠湾沉冠',
         '第十三歌_不空的水囊', '第十四歌_藏命之匣', '第十五歌_日冕之晨']
ZHUGUO = ['诸国期时段_一_晨祷', '诸国期时段_二_午祷上', '诸国期时段_三_午祷下', '诸国期时段_四_晚祷上',
          '诸国期时段_五_晚祷下', '诸国期时段_六_夜祷']
SALVIS = ['萨尔维斯时段_一_崛起上', '萨尔维斯时段_二_崛起下', '萨尔维斯时段_三_帝国', '萨尔维斯时段_四_魔族之世',
          '萨尔维斯时段_五_末年上', '萨尔维斯时段_六_末年下']
STRIFE = ['纷争纪时段_一_灰的年月', '纷争纪时段_二_白石的年月', '纷争纪时段_三_灯的年月', '纷争纪时段_四_炮的年月',
          '纷争纪时段_五_浮塔的年月', '纷争纪时段_六_铁狼的年月', '纷争纪时段_七_号角的年月']
PERIOD_NAME = {t: t.split('_')[-1] for t in STRIFE}          # 纷争纪时段_一_灰的年月 → 灰的年月
PAGES = [(s, os.path.join(WDIR, '月银纪史诗', s + '.md')) for s in SONGS] + \
        [(z, os.path.join(WDIR, '诸国期', z + '.md')) for z in ZHUGUO] + \
        [(v, os.path.join(WDIR, '萨尔维斯', v + '.md')) for v in SALVIS] + \
        [(v, os.path.join(WDIR, '纷争纪', v + '.md')) for v in STRIFE]
MOON_PAGES = SONGS + ZHUGUO + SALVIS

# 补卷：照文件名收，名字里带「说明」的跳过；tag 去掉 .md
def _supp(globpat):
    out = []
    for f in sorted(glob.glob(globpat)):
        b = os.path.basename(f)
        if '说明' in b:
            continue
        out.append((b[:-3], f))
    return out
SUPPS = _supp(os.path.join(WDIR, '萨尔维斯', '补卷', '帝国史_*.md')) + \
        _supp(os.path.join(WDIR, '萨尔维斯', '补卷', '月银纪_姓与家名.md')) + \
        _supp(os.path.join(WDIR, '月银纪补卷', '*.md')) + \
        _supp(os.path.join(WDIR, '纷争纪', '补卷', '第一项_*.md')) + \
        _supp(os.path.join(WDIR, '纷争纪', '补卷', '补卷_*.md'))
SUPP_TAGS = [t for t, _ in SUPPS]
TOTAL_CARD_FILE = os.path.join(WDIR, '纷争纪', '补卷', '补卷_32_二十二张.md')
# 不挂纪元门控的条目（直醒、只扫用户）：二十二张的总条，牌落进每一纪，迷宫纪的翻刻本也是玩家摸得到的线头
NO_GATE = {'纷争纪·传唱｜二十二张'}

# 灯里那一句照原话，两个感叹号留着，只许在这一句里
LAST_WORDS = '看啊，我的功业已成！欢呼吧，世界将因我而不再燃烧！'
problems, notes = [], []

# ---------- 钥匙别名 ----------
ERA_ANCHOR = lambda era: ['日期</b><br>' + era, 'hud-meta">' + era, '纪元：' + era]
YEAR_PRE = '(?:<br>|hud-meta">|纪元：)'
YEAR = YEAR_PRE + '月银纪'
YEAR_OF = {'月银纪': YEAR_PRE + '月银纪', '纷争纪': YEAR_PRE + '纷争纪'}
ALIASES = {
    '〔月银纪〕': ERA_ANCHOR('月银纪'),
    '〔纷争纪〕': ERA_ANCHOR('纷争纪'),
    '〔别纪〕': ERA_ANCHOR('迷宫纪') + ERA_ANCHOR('纷争纪') + ERA_ANCHOR('山铜纪'),
    '〔月银纪·正则〕': ['/日期<\\/b><br>月银纪|hud-meta">月银纪|纪元：月银纪/'],
    # 纷争纪最后那一个月底座写山铜纪元年，并进来，页七雨城那十条自写的门控就跟它一字不差
    '〔纷争纪·正则〕': ['/(?:<br>|hud-meta">|纪元：)(?:纷争纪|山铜纪元年)/'],
    '〔迷宫纪凭证〕': ['/^(?![\\s\\S]*纪元：月银纪)[\\s\\S]*命途已确认/'],
    # 祭火期 1 到 1000 年，万兽期 1001 到 3000 年；潮汐格、摘要行、凭证里的时段也认
    '〔时段·祭火·正则〕': ['/潮汐<\\/b><br>祭火| · 祭火·|开局时段：祭火|%s(?:\\d{1,3}|1000)年/' % YEAR],
    '〔时段·万兽·正则〕': ['/潮汐<\\/b><br>万兽| · 万兽·|开局时段：万兽|%s(?:100[1-9]|10[1-9]\\d|1[1-9]\\d\\d|2\\d\\d\\d|3000)年/' % YEAR],
}
for p in ['祭火', '万兽', '诸国', '崛起', '帝国', '魔族之世', '末年']:
    ALIASES['〔时段·%s〕' % p] = ['潮汐</b><br>' + p, ' · %s·' % p, '开局时段：' + p]
# 诸国四把、萨尔维斯四把、纷争纪七把时段钥匙照页上「打包脚本里要加，写成一条正则」那一句取
PAGE_TEXT = {tag: open(path, encoding='utf-8').read() for tag, path in PAGES}
for tag, path in PAGES:
    for m in re.finditer(r'〔(时段·(?:诸国·[^〕]+|[^〕]+·正则))〕打包脚本里要加，写成一条正则 `(/[^`]+/)`', PAGE_TEXT[tag]):
        ALIASES['〔%s〕' % m.group(1)] = [m.group(2)]
STRIFE_PERIOD_KEYS = ['%s·正则' % PERIOD_NAME[t] for t in STRIFE]
for k in ['诸国·晨祷', '诸国·午祷', '诸国·晚祷', '诸国·夜祷', '崛起·正则', '帝国·正则', '魔族之世·正则', '末年·正则'] + STRIFE_PERIOD_KEYS:
    if '〔时段·%s〕' % k not in ALIASES:
        raise SystemExit('页上找不到〔时段·%s〕的正则' % k)

# 纷争纪二十一把主线钥匙：页上「〔主线·X〕写成 `/…/`」那一句
ML_RX_PAGE = {}
for tag in STRIFE:
    for m in re.finditer(r'〔(主线·[^〕]+)〕写成 `(/[^`]+/)`', PAGE_TEXT[tag]):
        k = '〔%s〕' % m.group(1)
        if k in ML_RX_PAGE and ML_RX_PAGE[k] != m.group(2):
            problems.append('主线钥匙 %s 页上写了两种正则' % k)
        ML_RX_PAGE[k] = m.group(2)
for k, v in ML_RX_PAGE.items():
    ALIASES[k] = [v]

# ---------- 正则体检（同 v5） ----------
def is_rx(w):
    return w.startswith('/') and w.rfind('/') > 0

def quant_count(k):
    s_ = re.sub(r'\\.', 'x', k); s_ = re.sub(r'\[[^\]]*\]', 'C', s_)
    s_ = s_.replace('(?:', '(').replace('(?!', '(').replace('(?=', '(').replace('(?<=', '(').replace('(?<!', '(')
    return len(re.findall(r'\{\d*,?\d*\}|[*+?]', s_))

def star_height(k):
    i, best, contains, prev_close, prev_inner = 0, 0, [0], False, 0
    while i < len(k):
        c = k[i]
        if c == '\\': i += 2; prev_close = False; continue
        if c == '[':
            j = k.find(']', i + 2 if k[i + 1:i + 2] in ('^', ']') else i + 1); i = j + 1; prev_close = False; continue
        if c == '(':
            if k[i:i + 4] in ('(?<=', '(?<!'): i += 4
            elif k[i:i + 3] in ('(?:', '(?!', '(?='): i += 3
            else: i += 1
            contains.append(0); prev_close = False; continue
        if c == ')':
            prev_inner = contains.pop(); prev_close = True; i += 1; continue
        m_ = re.match(r'\{\d*,?\d*\}', k[i:]) if c == '{' else None
        if c in '*+?' or m_:
            d_ = 1 + (prev_inner if prev_close else 0); best = max(best, d_); contains[-1] = max(contains[-1], d_)
            i += m_.end() if m_ else 1; prev_close = False; continue
        prev_close = False; i += 1
    return best

_RP_CACHE = {}
def regex_problems(w):
    if w in _RP_CACHE:
        return _RP_CACHE[w]
    body, flags = w[1:w.rfind('/')], w[w.rfind('/') + 1:]
    p_ = []
    if set(flags) - set('imsg'): p_.append('flags')
    try: re.compile(body)
    except re.error as ex: p_.append('编译失败 %s' % ex)
    if quant_count(body) > 25: p_.append('量词 %d>25' % quant_count(body))
    if star_height(body) > 1: p_.append('量词套量词')
    if re.search(r'\(\?P?<[A-Za-z]', body): p_.append('命名组没测过')
    _RP_CACHE[w] = p_
    return p_

def split_top(s):
    parts, depth, cur, i = [], 0, '', 0
    while i < len(s):
        c = s[i]
        if c == '\\' and i + 1 < len(s):
            cur += s[i:i + 2]; i += 2; continue
        if c == '[':
            j = s.find(']', i + 2 if s[i + 1:i + 2] in ('^', ']') else i + 1)
            cur += s[i:j + 1]; i = j + 1; continue
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        if c == '|' and depth == 0:
            parts.append(cur); cur = ''
        else:
            cur += c
        i += 1
    parts.append(cur)
    return parts

# ---------- 年份段（万兽年份窗、第二十二张那一支、纷争纪的模拟都用） ----------
def _same_len(a, b):
    if a == b:
        return [a]
    i = 0
    while a[i] == b[i]:
        i += 1
    pre, a, b = a[:i], a[i:], b[i:]
    if len(a) == 1:
        return [pre + '[%s-%s]' % (a, b)]
    out, n = [], len(a) - 1
    lo_first = int(a[0]) if a[1:] == '0' * n else int(a[0]) + 1
    if a[1:] != '0' * n:
        out += [pre + x for x in _same_len(a, a[0] + '9' * n)]
    hi_first = int(b[0]) if b[1:] == '9' * n else int(b[0]) - 1
    if lo_first <= hi_first:
        out.append(pre + ('%d' % lo_first if lo_first == hi_first else '[%d-%d]' % (lo_first, hi_first)) + '\\d' * n)
    if b[1:] != '9' * n:
        out += [pre + x for x in _same_len(b[0] + '0' * n, b)]
    return out

def range_alts(lo, hi):
    out = []
    for n in range(len(str(lo)), len(str(hi)) + 1):
        a, b = max(lo, 10 ** (n - 1)), min(hi, 10 ** n - 1)
        if a <= b:
            out += _same_len(str(a), str(b))
    return out

# 纷争纪七段的年份（第二十二张那一支、模拟用）
STRIFE_SPAN = {'灰的年月': (1, 120), '白石的年月': (121, 300), '灯的年月': (301, 1050), '炮的年月': (1051, 4500),
               '浮塔的年月': (4501, 8800), '铁狼的年月': (8801, 10800), '号角的年月': (10801, 11034)}
for k in STRIFE_PERIOD_KEYS:
    pname = k.split('·')[0]
    lo, hi = STRIFE_SPAN[pname]
    alts = (['元'] if lo == 1 else []) + range_alts(lo, hi)
    w = ALIASES['〔时段·%s〕' % k][0]
    branch = '开局时段：第二十二张｜年份：(?:%s)(?!\\d)' % '|'.join(alts)
    if branch not in w:
        w = w[:w.rfind('/')] + '|' + branch + w[w.rfind('/'):]
    for p_ in regex_problems(w):
        problems.append('〔时段·%s〕补了第二十二张以后 %s' % (k, p_))
    ALIASES['〔时段·%s〕' % k] = [w]
    body_ = w[1:w.rfind('/')]
    for y in range(lo, hi + 1):
        if not re.search(body_, '纪元：纷争纪｜开局时段：第二十二张｜年份：%d' % y):
            raise SystemExit('第二十二张那一支漏了 %s %d 年' % (pname, y))
    for y in (lo - 1, hi + 1):
        if y >= 1 and re.search(body_, '纪元：纷争纪｜开局时段：第二十二张｜年份：%d' % y):
            raise SystemExit('第二十二张那一支多认了 %s %d 年' % (pname, y))

GATE_RX = set(v[0] for k, v in ALIASES.items() if k.endswith('·正则〕') or k.startswith('〔时段·诸国·') or k.startswith('〔主线·'))
GATE_PREFIX = '/' + YEAR_PRE

def is_gate(w):
    return w in GATE_RX or (is_rx(w) and w.startswith(GATE_PREFIX))

def mainline_rx(name):
    return '/%s·|开局时段：%s/' % (name, name)

def alias(tok):
    if tok in ALIASES:
        return ALIASES[tok]
    m = re.match(r'^〔主线·(.+)〕$', tok)
    if m:
        ALIASES[tok] = [mainline_rx(m.group(1))]
        GATE_RX.add(ALIASES[tok][0])
        return ALIASES[tok]
    raise SystemExit('未知钥匙别名 ' + tok)

def dedupe(ws):
    seen, res = set(), []
    for w in ws:
        if w not in seen:
            seen.add(w); res.append(w)
    return res

def expand_batch(spec):
    spec = spec.strip()
    if spec in ('', '无'):
        return []
    out = []
    for tok in re.findall(r'〔[^〕]+〕|[^、〔〕]+', spec):
        tok = tok.strip().strip('、')
        if tok:
            out += alias(tok) if tok.startswith('〔') else [tok]
    return dedupe(out)

# ---------- 底卡 + 进卡补丁 ----------
raw = open(SRC, encoding='utf-8').read()
PM = runpy.run_path(PATCH)
REPS = PM['REPS']
for o, n in REPS:
    if raw.count(o) != 1:
        raise SystemExit('进卡补丁对不上底卡：%r 出现 %d 次' % (o, raw.count(o)))
for o, n in REPS:
    raw = raw.replace(o, n)
card = json.loads(raw)
base_card = json.load(open(SRC, encoding='utf-8'))
title_of = lambda e: e['content'].strip().split('\n')[0].lstrip('# ').strip()
BASE_TITLES = [title_of(e) for e in base_card['prompt']['lorebook']]

# 另两路的底卡补丁：先套 REPS（上面），再按 PATCHES 改解析后的 content
ext_log, ext_new_texts, EXT_INTRO_REPS, REF_RENAME, ext_missing = [], [], [], {}, []
for name in EXT_PATCHES:
    p = os.path.join(HERE, name)
    if NO_EXT:
        ext_missing.append(name + '（这一回加了 --no-ext，没读）'); continue
    if not os.path.exists(p):
        ext_missing.append(name + '（还没有落盘，这一回跳过）'); continue
    mod = runpy.run_path(p)
    lb = card['prompt']['lorebook']
    for pt in mod.get('PATCHES', []):
        i, head, ops = pt['idx'], pt['head'], pt.get('ops', [])
        if not (0 <= i < len(lb)):
            raise SystemExit('%s：#%d 越界' % (name, i))
        first = lb[i]['content'].strip().split('\n')[0]
        if head not in first:
            raise SystemExit('%s：#%d 第一行里没有「%s」，现在是「%s」' % (name, i, head, first[:40]))
        kinds = [op[0] for op in ops]
        if 'rewrite' in kinds and len(ops) != 1:
            raise SystemExit('%s：#%d rewrite 不能跟别的操作混用' % (name, i))
        c = lb[i]['content']
        for op in ops:
            if op[0] == 'replace':
                if c.count(op[1]) != 1:
                    raise SystemExit('%s：#%d 旧串出现 %d 次：%s' % (name, i, c.count(op[1]), op[1][:40]))
                c = c.replace(op[1], op[2])
                ext_new_texts.append((name, i, op[2], op[1]))
            elif op[0] == 'rewrite':
                ext_new_texts.append((name, i, op[1], c))
                c = op[1]
            else:
                raise SystemExit('%s：#%d 不认得的操作 %s' % (name, i, op[0]))
        lb[i]['content'] = c
        if pt.get('trig') is not None:
            lb[i]['triggerWords'] = list(pt['trig'])
        ext_log.append('%s #%d %s｜%s｜%s%s' % (name, i, title_of(lb[i])[:30], pt.get('why', ''),
                                                '、'.join('%s×%d' % (k, kinds.count(k)) for k in dict.fromkeys(kinds)),
                                                '｜触发词换了' if pt.get('trig') is not None else ''))
    EXT_INTRO_REPS += [(name, o, n) for o, n in mod.get('INTRO_REPS', [])]
    REF_RENAME.update(mod.get('REF_RENAME', {}))

# ---------- 介绍页：纷争纪年表（只改年份和顺序）、命星档案那一句、另两路的 INTRO_REPS ----------
ROW_RX = re.compile(r'<div class="chronicle-row"><b>纷争纪(\d+)年</b><span>(.*?)</span></div>')
def fix_chronicle(html, ymap, log):
    rows = list(ROW_RX.finditer(html))
    if not rows:
        raise SystemExit('介绍页里找不到纷争纪年表')
    a, b = rows[0].start(), rows[-1].end()
    seps = [html[rows[k].end():rows[k + 1].start()] for k in range(len(rows) - 1)]
    for s_ in seps:
        if s_.strip():
            raise SystemExit('纷争纪年表的行与行之间夹着别的东西：%r' % s_[:40])
    olds = [int(r.group(1)) for r in rows]
    if sorted(olds) != sorted(ymap):
        raise SystemExit('介绍页纷争纪年表的年份跟补丁表对不上：页上 %s，表里 %s' % (olds, sorted(ymap)))
    items = [(ymap[int(r.group(1))], int(r.group(1)), r.group(2)) for r in rows]
    items.sort(key=lambda x: (x[0], x[1]))
    new_rows = ['<div class="chronicle-row"><b>纷争纪%d年</b><span>%s</span></div>' % (ny, sp) for ny, oy, sp in items]
    out = new_rows[0] + ''.join(s_ + r for s_, r in zip(seps, new_rows[1:]))
    for ny, oy, sp in items:
        if ny != oy:
            log.append('纷争纪%d年 → %d年｜%s' % (oy, ny, re.sub('<[^>]+>', '', sp)[:24]))
    return html[:a] + out + html[b:], [sp for _, _, sp in items]

def intro_transform(html, log):
    html, spans = fix_chronicle(html, PM['STRIFE_YEAR_MAP'], log)
    for o, n in PM.get('INTRO_FIX', []):
        if html.count(o) != 1:
            raise SystemExit('介绍页补丁对不上：%r 出现 %d 次' % (o[:30], html.count(o)))
        html = html.replace(o, n)
        log.append('改句：%s' % o[:24])
    for nm, o, n in EXT_INTRO_REPS:
        if html.count(o) != 1:
            raise SystemExit('%s 的 INTRO_REPS 对不上介绍页：%r 出现 %d 次' % (nm, o[:30], html.count(o)))
        html = html.replace(o, n)
        log.append('%s 改句：%s' % (nm, o[:24]))
    return html, spans

intro_log = []
card['introPage'], _spans_new = intro_transform(card['introPage'], intro_log)
_spans_old = [m.group(2) for m in ROW_RX.finditer(base_card['introPage'])]
if sorted(_spans_old) != sorted(_spans_new):
    raise SystemExit('纷争纪年表改完以后 span 的字变了')

old = card['prompt']['lorebook']
old_titles = set(title_of(e) for e in old)
SYSP = card['prompt']['systemPrompt']

# ---------- 第一到三批 ----------
def parse_batch(path):
    text = open(path, encoding='utf-8').read()
    items = []
    for b in re.split(r'^=== ', text, flags=re.M)[1:]:
        title, rest = b.split('\n', 1)
        head, body = rest.split('\n---\n', 1)
        meta = {}
        for line in head.strip().split('\n'):
            k, v = line.split('：', 1)
            meta[k.strip()] = v.strip()
        items.append({'title': title.strip(), 'meta': meta, 'body': body.strip('\n'), 'file': os.path.basename(path)})
    return items

AUTHOR_MARK = re.compile(r'（[★#][^）]*）')
def model_text(body):
    t = AUTHOR_MARK.sub('', body).replace('★', '')
    return '\n'.join(p.strip() for p in re.split(r'\n\s*\n', t) if p.strip())

def merge_rx_names(w, pairs):
    """触发正则里有旧名的备选项，添上新名的那一个，旧的留着。"""
    if not is_rx(w):
        return w
    body, flags = w[1:w.rfind('/')], w[w.rfind('/') + 1:]
    out = []
    for a in split_top(body):
        b = a
        for o, n in pairs:
            b = b.replace(o, n)
        if b != a and b not in out:
            out.append(b)
        if a not in out:
            out.append(a)
    return '/' + '|'.join(out) + '/' + flags

batch_items, retired, seen_retire = [], [], set()
for n_, d in enumerate(['batch1', 'batch2', 'batch3'], 1):
    for f in sorted(glob.glob(os.path.join(ROOT, 'moon', d, '*.md'))):
        for it in parse_batch(f):
            it['batch'] = n_
            if it['title'] in ED['RETIRE']:
                retired.append((it['title'], ED['RETIRE'][it['title']]))
                seen_retire.add(it['title'])
                continue
            batch_items.append(it)
for t in set(ED['RETIRE']) - seen_retire:
    problems.append('要退的旧条目找不到：' + t)

rename_log = collections.Counter()
for it in batch_items:
    t0 = it['title']
    for o, n in ED['PROPER']:
        c = it['body'].count(o) + it['title'].count(o)
        if c:
            rename_log[(o, n)] += c
            it['body'] = it['body'].replace(o, n); it['title'] = it['title'].replace(o, n)
    for o, n, skip in ED['GENERIC']:
        if t0 in skip or it['title'] in skip:
            continue
        c = it['body'].count(o)
        if c:
            rename_log[(o, n)] += c
            it['body'] = it['body'].replace(o, n)
    it['old_title'] = t0
    trig = it['meta']['触发']
    # 纪元钟的时段钥匙换成正则，诸国添四把
    trig = trig.replace('〔时段·祭火〕', '〔时段·祭火·正则〕').replace('〔时段·万兽〕', '〔时段·万兽·正则〕')
    trig = trig.replace('〔时段·诸国〕', '〔时段·诸国〕〔时段·诸国·晨祷〕〔时段·诸国·午祷〕〔时段·诸国·晚祷〕〔时段·诸国·夜祷〕')
    for p_ in ['崛起', '帝国', '魔族之世', '末年']:
        trig = trig.replace('〔时段·%s〕' % p_, '〔时段·%s·正则〕' % p_)
    it['trig'] = [w if w in GATE_RX else merge_rx_names(w, ED['PROPER']) for w in expand_batch(trig)]
    for e_old, e_new in ED['EDITS'].get(it['title'], []):
        if it['body'].count(e_old) != 1:
            problems.append('逐条改对不上：%s｜%s 出现 %d 次' % (it['title'], e_old[:30], it['body'].count(e_old)))
        else:
            it['body'] = it['body'].replace(e_old, e_new)
    if it['title'] in ED['REWRITE']:
        it['body'] = ED['REWRITE'][it['title']]
        it['trig'] = [ED['REWRITE_TRIG'][it['title']]]
    for add in ED['TRIG_ADD'].get(it['title'], []):
        rx = [i for i, w in enumerate(it['trig']) if is_rx(w) and w not in GATE_RX]
        w = it['trig'][rx[-1]]
        it['trig'][rx[-1]] = w[:w.rfind('/')] + '|' + add + w[w.rfind('/'):]
for t in ED['EDITS']:
    if t not in [it['title'] for it in batch_items]:
        problems.append('逐条改的条目找不到：' + t)

def mk(title, body_text, folder, trig, ttype, bl, rng, depth):
    return {'enabled': True, 'triggerWords': trig, 'triggerWordsType': ttype, 'blackListWords': bl,
            'blackListWordsType': 'OR', 'folder': folder, 'priority': 0, 'probability': 100, 'scanDepth': depth,
            'triggerRange': rng, 'impactRange': ['system'], 'contentMethod': 'single',
            'content': '# ' + title + '\n' + body_text}

batch_entries = []
for it in batch_items:
    m = it['meta']
    e = mk(it['title'], model_text(it['body']), m['文件夹'], it['trig'],
           'AND' if m.get('触发方式') == '同时满足' else 'OR', expand_batch(m.get('黑名单', '无')), ['user', 'assistant'], 2)
    e['_src'] = '第%d批 %s' % (it['batch'], it['file'])
    e['_oldpri'] = int(m['优先级'])
    e['_era'] = '月银纪'
    batch_entries.append(e)

# ---------- 页和补卷 ----------
SET_RX = re.compile(r'触发(（同时满足）)?(.*?)，(?:黑名单 ?(.*?)，)?(?:优先级 ?\d+，)?范围 ?([^，。]+)，深度 ?(\d+)')
NEED_RX = re.compile(r'，?([^，、（）\x00]+?)那一条要同时出现([^，、（）\x00]+)')
RANGES = {'用户与助手': ['user', 'assistant'], '用户': ['user'], '助手': ['assistant']}
STAR_HEAD = re.compile(r'^### (.+?) \((Special|Passive|Art|Ability) \| (Common|Rare|Epic|Legend|Unique)\)\s*$')
NON_ENTRY = {'这一代的命星': 'stars', '这一代的人物': 'skip', '这一段的传奇表': 'skip'}

def page_tokens(seg, where, need=None):
    seg = (seg or '').strip()
    if seg in ('', '无'):
        return []
    rx = re.findall(r'`([^`]+)`', seg)
    rest = re.sub(r'`[^`]+`', '\x00', seg)
    rest = re.sub(r'（[^（）]*）', '', rest)
    if need is not None:
        for m in NEED_RX.finditer(rest):
            need[m.group(1).strip()] = m.group(2).strip()
        rest = NEED_RX.sub('', rest)
    toks, k = [], 0
    for m in re.finditer(r'〔[^〕]+〕|\x00|星名加持有人的名字', rest):
        g = m.group(0)
        if g == '\x00':
            toks.append(('rx', rx[k])); k += 1
        elif g.startswith('〔'):
            toks.append(('alias', g))
        else:
            toks.append(('star', None))
    left = re.sub(r'〔[^〕]+〕|\x00|星名加持有人的名字|[、\s]', '', rest)
    if left:
        problems.append('%s 条目设置里有认不出的字：%s' % (where, left))
    return toks

def parse_setting(s, where):
    m = re.search(r'文件夹 ?(\d\d·(?:月银纪|纷争纪)｜[^，（]+)', s)
    m2 = SET_RX.search(s)
    if not m or not m2:
        problems.append('%s 条目设置读不出：%s' % (where, s[:60]))
        return None
    need = {}
    return {'folder': m.group(1), 'and': bool(m2.group(1)), 'trig': page_tokens(m2.group(2), where, need),
            'bl': page_tokens(m2.group(3), where), 'range': RANGES[m2.group(4).strip()], 'depth': int(m2.group(5)),
            'need': need}

def parse_page(tag, path):
    lines = open(path, encoding='utf-8').read().replace('\r', '').split('\n')
    items, cur, mode, stars = [], None, None, []
    for no, ln in enumerate(lines, 1):
        where = '%s:%d' % (tag, no)
        if ln.startswith('## 设计备注'):
            break
        if ln.startswith('> 条目设置：'):
            spec = parse_setting(ln[len('> 条目设置：'):], where)
            if mode == 'stars':
                if not stars:
                    problems.append(where + ' 命星一节没有星')
                for s_ in stars:
                    s_['setting'] = spec; items.append(s_)
                stars = []
            elif cur:
                cur['setting'] = spec; items.append(cur)
            else:
                problems.append(where + ' 条目设置前面没有条目')
            cur, mode = None, None
            continue
        if ln.startswith('## '):
            h = ln[3:].strip()
            if cur and h == '裁定锁':
                cur['body'].append('## 裁定锁'); continue
            if cur:
                problems.append('%s「%s」没有条目设置就到了「%s」' % (where, cur['title'], h))
            if mode == 'stars' and stars:
                problems.append(where + ' 命星一节没有条目设置')
            cur, stars = None, []
            if h in NON_ENTRY:
                mode = NON_ENTRY[h]; continue
            cur = {'title': h, 'body': [], 'page': tag, 'kind': 'entry'}
            mode = 'entry'
            continue
        if mode == 'stars':
            m = STAR_HEAD.match(ln)
            if m:
                stars.append({'title': ln[4:].strip(), 'star': m.group(1), 'tier': m.group(3), 'body': [], 'page': tag, 'kind': 'star'})
            elif stars:
                if ln.startswith('### '):
                    problems.append(where + ' 命星一节里有不是星的小标题：' + ln)
                stars[-1]['body'].append(ln)
            continue
        if mode == 'entry':
            hm = re.match(r'^(#{3,6}) (.*)$', ln)
            if hm:
                cur['body'].append('#' * (len(hm.group(1)) - 1) + ' ' + hm.group(2).strip())
            elif ln.startswith('>'):
                problems.append(where + ' 条目里有引用块：' + ln[:40])
                cur['body'].append(ln.lstrip('> '))
            else:
                cur['body'].append(ln)
    if cur:
        problems.append('%s 页尾「%s」没有条目设置' % (tag, cur['title']))
    return items

def body_text(lines):
    t = '\n'.join(l.rstrip() for l in lines if l.strip())
    return AUTHOR_MARK.sub('', t).replace('★', '')

page_items = []
ABIL_STARS = {}
HOLDERS_BY_PAGE = {}
for tag, path in PAGES + SUPPS:
    its = parse_page(tag, path)
    comps, holder_map = [], collections.defaultdict(list)
    for it in its:
        m = re.match(r'^旅途同行：(.+?)（', it['title']) or re.match(r'^凡世至强：.+? · (.+?)（', it['title'])
        if m:
            nm = m.group(1).strip()
            vs = [v for v in dict.fromkeys([nm, nm.split('·')[0]]) if v]
            comps += [v for v in vs if v not in comps]
            # 旅伴条的能力那一行列着他身上的星
            for l in it['body']:
                if l.startswith('能力：'):
                    for s_ in re.findall(r'【([^】]+)】', l):
                        holder_map[s_] += [v for v in vs if v not in holder_map[s_]]
    for it in its:
        it['title'] = re.sub(r'（第二稿）$', '', it['title'])
        if it['kind'] == 'star':
            call = next((l for l in it['body'] if l.startswith('【调用】')), '')
            it['holders'] = list(dict.fromkeys(holder_map.get(it['star'], []) + [c for c in comps if c in call]))
            if not it['holders']:
                problems.append('%s 命星「%s」找不到持有人' % (tag, it['star']))
        it['era'] = it['setting']['folder'].split('·')[1].split('｜')[0] if it.get('setting') else None
    ABIL_STARS[tag] = set(holder_map)
    HOLDERS_BY_PAGE[tag] = holder_map
    page_items += its

# 补卷里只该有「纪·门类｜名」的条目，条目名的纪跟文件夹的纪要对上
supp_set = set(SUPP_TAGS)
for it in page_items:
    if it['page'] not in supp_set:
        continue
    t_ = it['title']
    if it['kind'] != 'entry':
        problems.append('%s 补卷里有不是条目的东西：%s' % (it['page'], t_))
    m_ = re.match(r'^(月银纪|纷争纪)·', t_)
    if not m_:
        problems.append('%s 补卷的条目名不是「纪·门类｜名」：%s' % (it['page'], t_))
    elif it.get('era') and m_.group(1) != it['era']:
        problems.append('%s 条目名的纪跟文件夹对不上：%s｜%s' % (it['page'], t_, it['setting']['folder']))

# 和底卡撞了标题的（守望长律这一类，底卡里是后世的那一门），名字后面照纪元加（月银纪）或（纷争纪）
for it in page_items:
    if it['title'] in old_titles:
        era = it.get('era') or '月银纪'
        if it['kind'] == 'star':
            it['title'] = it['title'].replace(it['star'], it['star'] + '（%s）' % era, 1)
        else:
            it['title'] += '（%s）' % era
        notes.append('和底卡同名，标题加了（%s）：%s' % (era, it['title']))

# 同名标题加页名区分（这一段旅伴之间这一类）
cnt = collections.Counter(it['title'] for it in page_items)
for it in page_items:
    if cnt[it['title']] > 1:
        short = it['page'].split('_')[-1]
        it['title'] = '%s｜%s' % (it['title'], short)
cnt2 = collections.Counter(it['title'] for it in page_items if it.get('setting'))
for t_, c_ in cnt2.items():
    if c_ > 1:
        problems.append('加了页名还是同名：%s ×%d' % (t_, c_))

def page_entry(it):
    s = it['setting']
    trig = []
    for kind, v in s['trig']:
        if kind == 'alias':
            trig += alias(v)
        elif kind == 'rx':
            trig.append(v)
        else:
            need = s['need'].get(it['star'])
            # 星名加持有人的名字；页上写了「X那一条要同时出现Y」的，星名太泛，只认人，再要Y同在一条消息里
            alts = ([] if need else [re.escape(it['star'])]) + [re.escape(h) for h in it.get('holders', [])]
            trig.append('/' + '|'.join(alts or [re.escape(it['star'])]) + '/')
            if need and need not in it.get('holders', []):
                trig.append('/' + re.escape(need) + '/')
    bl = []
    for kind, v in s['bl']:
        bl += alias(v) if kind == 'alias' else [v]
    if it['title'] == '月银纪·主线｜诸国·神渡之盟':
        # 旧钥匙〔主线·诸国·三川会盟〕留着，测试卡里开过三川会盟的老存档还认得
        trig += alias('〔主线·诸国·三川会盟〕')
    if it['title'] == '月银纪·主线｜崛起·辉塔初升':
        # 10-21 灯台改名辉塔，旧钥匙〔主线·崛起·灯台初升〕留着，开过灯台初升的老存档还认得
        trig += alias('〔主线·崛起·灯台初升〕')
    if s['folder'].startswith('51'):
        # 传奇条不叫开局口令叫醒（镜中石瞳开局那一句会把狄昂的传奇条叫进来，他这时候还没成名）
        bl.append('/开局时段：/')
    e = mk(it['title'], body_text(it['body']), s['folder'], dedupe(trig), 'AND' if s['and'] else 'OR', dedupe(bl),
           s['range'], s['depth'])
    e['_src'] = it['page']
    e['_page'], e['_star'], e['_holders'] = it['page'], it.get('star'), it.get('holders', [])
    e['_era'] = it['era']
    return e

page_entries = [page_entry(it) for it in page_items if it.get('setting')]
for e in page_entries:
    if e['_era'] not in ('月银纪', '纷争纪'):
        problems.append('%s 文件夹认不出纪元：%s' % (title_of(e), e['folder']))

# ---------- 跨时段的命星（STAR_GATE 第八版，键写 星名 或 星名@页） ----------
def _body(w):
    return w[1:w.rfind('/')]
STAR_GATE = ED.get('STAR_GATE', {})
STAR_DEF = collections.defaultdict(list)          # 星名 → 定义它的页
for e in page_entries:
    if e.get('_star'):
        STAR_DEF[e['_star']].append(e['_page'])
used_rules = set()
gate_log = []
for e in page_entries:
    st = e.get('_star')
    if not st:
        continue
    key = '%s@%s' % (st, e['_page'])
    if key in STAR_GATE:
        rule = STAR_GATE[key]; used_rules.add(key)
    elif st in STAR_GATE:
        rule = STAR_GATE[st]; used_rules.add(st)
        if len(STAR_DEF[st]) > 1:
            problems.append('STAR_GATE「%s」没写页，可星名有 %d 版：%s' % (st, len(STAR_DEF[st]), '、'.join(STAR_DEF[st])))
    else:
        continue
    gi = [i for i, w in enumerate(e['triggerWords']) if w in GATE_RX]
    if len(gi) != 1:
        problems.append('命星「%s」找不到唯一的门控钥匙' % key); continue
    g = e['triggerWords'][gi[0]]
    if rule.get('gate'):
        g = alias(rule['gate'])[0]
    for extra in rule.get('also', []):
        add_ = _body(alias(extra)[0])
        if add_ not in split_top(_body(g)):
            g = '/' + _body(g) + '|' + add_ + '/'
        GATE_RX.add(g)
    e['triggerWords'][gi[0]] = g
    if rule.get('names'):
        ni = [i for i, w in enumerate(e['triggerWords']) if i != gi[0] and is_rx(w)]
        w = e['triggerWords'][ni[0]]
        have = set(split_top(_body(w)))
        add_ = [re.escape(x) for x in rule['names'] if re.escape(x) not in have]
        if add_:
            e['triggerWords'][ni[0]] = w[:w.rfind('/')] + '|' + '|'.join(add_) + w[w.rfind('/'):]
    if rule.get('copy_bl_from'):
        src_ = [x for x in page_entries if title_of(x).startswith('旅途同行：%s（' % rule['copy_bl_from'])]
        if src_:
            era_ = src_[0]['_era']
            e['blackListWords'] += [w for w in src_[0]['blackListWords'] if era_ in w and '年' in w and w not in e['blackListWords']]
        else:
            problems.append('命星「%s」要照的旅伴条找不到：%s' % (key, rule['copy_bl_from']))
    if rule.get('gate') or rule.get('also'):
        e['_gate_fixed'] = True
    gate_log.append('%s：%s' % (key, '、'.join(x for x in [('换成' + rule['gate']) if rule.get('gate') else '',
                                                          ('再挂' + '、'.join(rule.get('also', []))) if rule.get('also') else '',
                                                          ('添' + '、'.join(rule['names'])) if rule.get('names') else '',
                                                          ('照%s的年份黑名单' % rule['copy_bl_from']) if rule.get('copy_bl_from') else ''] if x)))
for k in STAR_GATE:
    if k not in used_rules:
        problems.append('跨时段的命星找不到：' + k)

# 脚本自己对一遍：纷争纪七页旅伴条能力那一行里的星，本页没有的，算借来的；跟手写的 STAR_GATE 比
BORROW_PICK = ED.get('BORROW_PICK', {})
BASE_POOL_STARS = set(ED.get('BASE_POOL_STARS', []))
auto_borrow = collections.OrderedDict()          # (星名, 出处页) → [纷争纪的持有人]
borrow_diff = []
for tag in STRIFE:
    for st in sorted(ABIL_STARS.get(tag, set())):
        homes = [p for p in STAR_DEF.get(st, []) if p in [t for t, _ in PAGES]]
        if tag in homes:
            continue
        if not homes:
            if st not in BASE_POOL_STARS:
                borrow_diff.append('%s 能力行里的【%s】哪一页都没有这一颗（也不在底卡池的名单里）' % (tag, st))
            continue
        order = [t for t, _ in PAGES]
        if (tag, st) in BORROW_PICK:
            home = BORROW_PICK[(tag, st)]
        elif len(homes) == 1:
            home = homes[0]
        else:
            before = [p for p in homes if order.index(p) < order.index(tag)]
            home = before[-1] if before else homes[0]
            borrow_diff.append('%s 借的【%s】有 %d 版（%s），脚本挑了离得最近的 %s' % (tag, st, len(homes), '、'.join(homes), home))
        hs = auto_borrow.setdefault((st, home), [])
        hs += [h for h in HOLDERS_BY_PAGE[tag][st] if h not in hs]
def _rule_for(st, home):
    return STAR_GATE.get('%s@%s' % (st, home)) or STAR_GATE.get(st)
for (st, home), hs in auto_borrow.items():
    rule = _rule_for(st, home)
    home_e = [e for e in page_entries if e.get('_star') == st and e['_page'] == home][0]
    g = [w for w in home_e['triggerWords'] if w in GATE_RX]
    has_strife = any('纷争纪' in w for w in g)
    if not rule:
        borrow_diff.append('【%s】（出处 %s）纷争纪的 %s 借了，STAR_GATE 里没有这一条' % (st, home, '、'.join(hs)))
        continue
    if not has_strife:
        borrow_diff.append('【%s】（出处 %s）纷争纪借了，门控没挂上纷争纪' % (st, home))
    names_have = set(rule.get('names', [])) | set(home_e.get('_holders', []))
    miss = [h for h in hs if h not in names_have]
    if miss:
        borrow_diff.append('【%s】（出处 %s）纷争纪的持有人没进星名那一支：%s' % (st, home, '、'.join(miss)))
for k, rule in STAR_GATE.items():
    st, _, home = k.partition('@')
    if rule.get('also') and '〔纷争纪·正则〕' in rule.get('also', []) and not home:
        homes = STAR_DEF.get(st, [])
        if homes and not any((st, h) in auto_borrow for h in homes):
            borrow_diff.append('STAR_GATE「%s」挂了纷争纪，可七页能力行里没人借它' % k)

# ---------- 年份窗：万兽各段的人物、旅伴、命星只在自己那一段的年份里醒 ----------
# 〔时段·万兽·正则〕横跨 1001 到 3000 年，后面的段讲起前面段里的人，前面那一段的旅伴条和命星会整套醒过来。
# 页上没写年份黑名单的，照这一段主线的开局年到下一段开局年的前一年给一个；命星被后面哪一段的旅伴能力里点了名，
# 那一段的年份也放开。诸国、萨尔维斯、纷争纪各段已经按时段钥匙分开，旅伴条都写了年份黑名单，命星照持有人那一条的黑名单。
def outside_rx(allowed):
    """allowed：[(起, 止)] 年份段（含两头，止为 None 是一直到底）。返回挡住这些年份以外的正则。"""
    iv = sorted((a, b if b is not None else 99999) for a, b in allowed)
    merged = []
    for a, b in iv:
        if merged and a <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    blocked, cur = [], 1
    for a, b in merged:
        if a > cur:
            blocked.append((cur, a - 1))
        cur = b + 1
    if cur <= 99999:
        blocked.append((cur, 99999))
    alts = [x for a, b in blocked for x in range_alts(a, b)]
    return '/%s(?:%s)年/' % (YEAR, '|'.join(alts)) if alts else None

def ml_year(e):
    c = e['content']
    op = re.search(r'(?m)^开局：(.*)$', c)
    op = op.group(1) if op else c.split('\n')[2][:300]
    y = re.search(r'纷争纪(\d+|元)年', c) if e.get('_era') == '纷争纪' or title_of(e).startswith('纷争纪·') else None
    if y:
        return 1 if y.group(1) == '元' else int(y.group(1))
    y = re.search(r'月银纪(\d+)年', c) or re.search(r'(?<!\d)(\d{3,5})年', op)
    return int(y.group(1)) if y else None

for allowed in ([(1020, 1099)], [(2950, 2999), (3000, None)], [(1690, 1720), (2393, 2498)], [(7, 7)]):
    rx_ = outside_rx(allowed)
    body_ = rx_[1:rx_.rfind('/')]
    for y_ in list(range(1, 3200)) + [5000, 9999, 10081, 12345]:
        inside = any(a <= y_ <= (b if b is not None else 99999) for a, b in allowed)
        if bool(re.search(body_, '<br>月银纪%d年·秋' % y_)) == inside:
            raise SystemExit('年份窗正则算错了：%s %d' % (allowed, y_))
def has_year_bl(e, era='月银纪'):
    return any(era in w and '年' in w and is_rx(w) for w in e['blackListWords'])
WS = SONGS[1:]
ws_start = {}
for e in page_entries:
    if e['_page'] in WS and title_of(e).startswith('月银纪·主线｜万兽·'):
        ws_start[e['_page']] = ml_year(e)
win = {}
for i, p in enumerate(WS):
    if ws_start.get(p) is None:
        problems.append('%s 主线里找不到开局年份，年份窗没法定' % p); continue
    nxt = ws_start.get(WS[i + 1]) if i + 1 < len(WS) else None
    win[p] = (ws_start[p], nxt - 1 if nxt else None)
window_log = collections.Counter()
# 页上写的「这一段以后」黑名单多半写到 2\d\d\d 为止，万兽钥匙还认 3000 年（日冕之晨那一年），3000 年会漏，补上 3000 年以后
AFTER_3000 = '/%s(?:[3-9]\\d\\d\\d|[1-9]\\d\\d\\d\\d)年/' % YEAR
def _blocks(e, y):
    return any(is_rx(w) and re.search(w[1:w.rfind('/')], '<br>月银纪%d年' % y) for w in e['blackListWords'])
for e in page_entries:
    if e['_page'] in WS[:-1] and e['folder'][:2] in ('46', '47', '49') and _blocks(e, 2999) and not _blocks(e, 3000):
        e['blackListWords'].append(AFTER_3000)
        window_log['补3000'] += 1
for e in page_entries:
    p, fd = e['_page'], e['folder'][:2]
    if p in win and fd in ('46', '47', '49') and not has_year_bl(e) and win[p][1] is not None:
        allowed = [win[p]]
        if fd == '49':
            allowed += [win[q] for q in WS if q != p and q in win and e['_star'] in ABIL_STARS.get(q, set())]
        rx = outside_rx(allowed)
        if rx:
            e['blackListWords'].append(rx)
            window_log[fd] += 1
# 命星照持有人那一条的年份黑名单：诸国、萨尔维斯（v7），纷争纪七页（v8）各照各的纪元，换了门控的不照
for group, era in ((ZHUGUO + SALVIS, '月银纪'), (STRIFE, '纷争纪')):
    for e in page_entries:
        if e['folder'][:2] != '49' or e['_page'] not in group or has_year_bl(e, era) or e.get('_gate_fixed'):
            continue
        if any(e['_star'] in ABIL_STARS.get(q, set()) for q in group if q != e['_page']):
            continue
        owners = [x for x in page_entries if x['_page'] == e['_page'] and
                  any(title_of(x).startswith('旅途同行：%s（' % h) for h in e['_holders'])]
        bls = set(tuple(w for w in x['blackListWords'] if era in w and '年' in w) for x in owners)
        if len(owners) >= 1 and len(bls) == 1 and list(bls)[0]:
            e['blackListWords'] += list(list(bls)[0])
            window_log['49' + ('诸国' if era == '月银纪' else '纷争纪')] += 1
# ---------- v8.1：时代钥匙（用户 10-21 导过 v8 以后定的两件，细则见 batch_edits_v8.py 末尾 v8.1 那一节） ----------
# 一、纷争纪 46、47、51 同时满足认〔纷争纪·正则〕的换成在世那几段的时段钥匙；49 没挂 STAR_GATE 的照持有人旅伴条的窗走。
# 二、月银纪 46 人物照【调用】的在世年份、51 传奇照年份黑名单，能落到时段的落；49 挂了 STAR_GATE 的、47 总条照旧，报告里列出来。
# 三、月银纪第一到三批四十条直醒的改成同时满足，门控是〔月银纪·正则〕或那几段的时段钥匙。
ERA_MAX = {'月银纪': 10081, '纷争纪': 11034}
MOON_PERIOD_KEYS = ['〔时段·祭火·正则〕', '〔时段·万兽·正则〕', '〔时段·诸国·晨祷〕', '〔时段·诸国·午祷〕', '〔时段·诸国·晚祷〕',
                    '〔时段·诸国·夜祷〕', '〔时段·崛起·正则〕', '〔时段·帝国·正则〕', '〔时段·魔族之世·正则〕', '〔时段·末年·正则〕']
STRIFE_KEYS = ['〔时段·%s〕' % k for k in STRIFE_PERIOD_KEYS]
ERA_KEYS = {'月银纪': MOON_PERIOD_KEYS, '纷争纪': STRIFE_KEYS}
ERA_GATE = {'月银纪': ALIASES['〔月银纪·正则〕'][0], '纷争纪': ALIASES['〔纷争纪·正则〕'][0]}
KEY_SPAN = {}
for era_, keys_ in ERA_KEYS.items():
    for k in keys_:
        c_ = re.compile(_body(ALIASES[k][0]))
        ys = [y for y in range(1, ERA_MAX[era_] + 1) if c_.search('<br>%s%d年' % (era_, y))]
        if not ys or ys != list(range(ys[0], ys[-1] + 1)):
            raise SystemExit('时段钥匙 %s 认的年份不是连着的一段' % k)
        KEY_SPAN[k] = (ys[0], ys[-1])
    for y in range(1, ERA_MAX[era_] + 1):
        if sum(1 for k in keys_ if KEY_SPAN[k][0] <= y <= KEY_SPAN[k][1]) != 1:
            raise SystemExit('%s%d年不是恰好落在一把时段钥匙里' % (era_, y))
STRIFE_KEY_OF_PAGE = {t: '〔时段·%s·正则〕' % PERIOD_NAME[t] for t in STRIFE}

def _ranges(ys):
    out = []
    for y in ys:
        if out and y == out[-1][1] + 1:
            out[-1][1] = y
        else:
            out.append([y, y])
    return [tuple(x) for x in out]

def bl_window(e, era):
    """照年份黑名单推出来的窗：[(起, 止)]，外加山铜纪元年那一个月放不放开；没有年份黑名单回 None"""
    rx = [re.compile(_body(w)) for w in e['blackListWords'] if is_rx(w) and era in w and '年' in w]
    if not rx:
        return None, True
    ys = [y for y in range(1, ERA_MAX[era] + 1) if not any(c.search('<br>%s%d年' % (era, y)) for c in rx)]
    shan = era == '纷争纪' and not any(c.search('<br>山铜纪元年') for c in rx)
    return _ranges(ys), shan

def clip_low(ranges, lo):
    out = []
    for a, b in ranges:
        a = max(a, lo)
        if a <= b:
            out.append((a, b))
    return out

def gate_for(era, ranges, shan=True):
    """回 (门控正则或 None, 做法, 覆盖的钥匙)。None：窗是空的，或者覆盖整一纪，门控照旧。"""
    keys = ERA_KEYS[era]
    cov = [k for k in keys if any(not (b < KEY_SPAN[k][0] or a > KEY_SPAN[k][1]) for a, b in ranges)]
    if not cov:
        return None, '窗是空的', cov
    if len(cov) == len(keys):
        return None, '整一纪', cov
    if len(cov) == 1:
        return ALIASES[cov[0]][0], '一段', cov
    union = '/' + '|'.join(_body(ALIASES[k][0]) for k in cov) + '/'
    if len(union) <= 1024 and not regex_problems(union):
        return union, '几段并起来', cov
    # 退成年份窗正则加那几段的潮汐格和开局时段写法
    alts = [x for a, b in ranges for x in range_alts(a, b)]
    if era == '纷争纪':
        y_alts = (['元'] if any(a <= 1 for a, b in ranges) else []) + alts
        reach_end = any(b >= ERA_MAX[era] for a, b in ranges)
        date = YEAR_PRE + (('(?:纷争纪(?:%s)年|山铜纪元年)' if shan and reach_end else '纷争纪(?:%s)年') % '|'.join(y_alts))
        tail = ['开局时段：第二十二张｜年份：(?:%s)(?!\\d)' % '|'.join(y_alts)]
    else:
        date = YEAR_PRE + '月银纪(?:%s)年' % '|'.join(alts)
        tail = []
    tides, opens = [], []
    for k in cov:
        for a in split_top(_body(ALIASES[k][0])):
            if a.startswith(YEAR_PRE) or a.startswith('开局时段：第二十二张'):
                continue
            if a.startswith('开局时段：'):
                o_ = a[len('开局时段：'):]
                if o_ not in opens:
                    opens.append(o_)
            elif a not in tides:
                tides.append(a)
    parts = [date] + tides + (['开局时段：(?:%s)' % '|'.join(opens)] if opens else []) + tail
    fb = '/' + '|'.join(parts) + '/'
    if len(fb) > 1024 or regex_problems(fb):
        problems.append('时代钥匙退成年份窗以后还是过不了体检（%d 字，%s）：%s' % (len(fb), '、'.join(regex_problems(fb)) or '太长', fb[:80]))
    return fb, '年份窗加几段的潮汐格和开局时段', cov

def _cov_name(cov):
    return '、'.join(k.strip('〔〕').replace('时段·', '').replace('·正则', '') for k in cov)

def swap_gate(e, old_gate, new_gate):
    gi = [i for i, w in enumerate(e['triggerWords']) if w == old_gate]
    if len(gi) != 1:
        problems.append('%s 换时代钥匙时找不到唯一的旧门控' % title_of(e))
        return False
    e['triggerWords'][gi[0]] = new_gate
    GATE_RX.add(new_gate)
    return True

V81 = collections.defaultdict(list)       # 类别 → 报告里的行
V81_COUNT = collections.Counter()
V81_WIN = {}                              # id(e) → (era, ranges, shan)，模拟里拿来正反测
STRIFE_PERSON_WINDOW = ED.get('STRIFE_PERSON_WINDOW', {})
MOON_PERSON_WINDOW = ED.get('MOON_PERSON_WINDOW', {})
MOON_DIRECT_WINDOW = ED.get('MOON_DIRECT_WINDOW', {})
SG_ = ERA_GATE['纷争纪']
MG_ = ERA_GATE['月银纪']

def comp_name(t):
    m = re.match(r'^旅途同行：(.+?)（', t) or re.match(r'^旅途同行·背景：(.+?)(?:｜.*)?$', t)
    return m.group(1) if m else None

# 纷争纪 47 旅伴条先算窗（背景条要照它）
comp_win = {}
for e in page_entries:
    if e['_era'] != '纷争纪' or e['folder'][:2] != '47' or e['triggerWordsType'] != 'AND' or SG_ not in e['triggerWords']:
        continue
    t = title_of(e)
    if not t.startswith('旅途同行：'):
        continue
    lo_ = STRIFE_SPAN[PERIOD_NAME[e['_page']]][0]
    r_, shan_ = bl_window(e, '纷争纪')
    if r_ is None:
        r_, why_ = [(lo_, ERA_MAX['纷争纪'])], '没有年份黑名单，从这一段的头一年到纪末'
    elif r_ and r_[0][0] == 1 and lo_ > 1:
        r_, why_ = clip_low(r_, lo_), '黑名单推的窗，下限抬到这一段的头一年'
    else:
        why_ = '黑名单推的窗'
    comp_win.setdefault((e['_page'], comp_name(t)), []).append((r_, shan_))
    e['_v81'] = (r_, shan_, why_)
for e in page_entries:
    if e['_era'] != '纷争纪' or e['folder'][:2] not in ('46', '47', '51') or e['triggerWordsType'] != 'AND' or SG_ not in e['triggerWords']:
        continue
    t, fd = title_of(e), e['folder'][:2]
    lo_ = STRIFE_SPAN[PERIOD_NAME[e['_page']]][0]
    if '_v81' in e:
        r_, shan_, why_ = e.pop('_v81')
    elif fd == '46':
        if t in STRIFE_PERSON_WINDOW:
            w_ = STRIFE_PERSON_WINDOW[t]
            if w_ is None:
                V81['纷争纪46'].append('%s｜整一纪都在，照旧' % t); V81_COUNT['纷争纪46照旧'] += 1
                continue
            r_, shan_, why_ = [w_], True, '照【调用】里的在世年份'
        else:
            r_, shan_ = bl_window(e, '纷争纪')
            r_ = clip_low(r_, lo_) if r_ else [(lo_, ERA_MAX['纷争纪'])]
            why_ = '不在表里，照黑名单和这一页那一段推'
            notes.append('纷争纪 46「%s」不在 STRIFE_PERSON_WINDOW 里，照黑名单推的窗' % t)
    else:
        r_, shan_ = bl_window(e, '纷争纪')
        if r_ is None and fd == '47':
            src_ = comp_win.get((e['_page'], comp_name(t)))
            if src_:
                r_ = _ranges(sorted(set(y for rr, _ in src_ for a, b in rr for y in range(a, b + 1))))
                shan_ = any(s for _, s in src_)
                why_ = '背景条没有年份黑名单，照同一页旅伴条的窗'
            else:
                r_, shan_, why_ = [(lo_, ERA_MAX['纷争纪'])], True, '没有年份黑名单，从这一段的头一年到纪末'
        elif r_ is None:
            r_, shan_, why_ = [(lo_, ERA_MAX['纷争纪'])], True, '没有年份黑名单，从这一段的头一年到纪末'
        elif r_ and r_[0][0] == 1 and lo_ > 1:
            r_, why_ = clip_low(r_, lo_), '黑名单推的窗，下限抬到这一段的头一年'
        else:
            why_ = '黑名单推的窗'
    g_, how_, cov_ = gate_for('纷争纪', r_, shan_)
    win_s = '、'.join('%d到%d' % ab if ab[0] != ab[1] else '%d' % ab[0] for ab in r_)
    if g_ is None:
        V81['纷争纪' + fd].append('%s｜窗 %s 覆盖%s，照旧（%s）' % (t, win_s, how_, why_)); V81_COUNT['纷争纪%s照旧' % fd] += 1
        continue
    if swap_gate(e, SG_, g_):
        V81['纷争纪' + fd].append('%s｜窗 %s → %s（%s；%s）' % (t, win_s, _cov_name(cov_), how_, why_))
        V81_COUNT['纷争纪%s改了' % fd] += 1
        V81_WIN[id(e)] = ('纷争纪', r_, shan_)

# 纷争纪 49：没挂 STAR_GATE 的，照持有人旅伴条的窗走
for e in page_entries:
    if e['_era'] != '纷争纪' or e['folder'][:2] != '49' or e.get('_gate_fixed'):
        continue
    page_key = ALIASES[STRIFE_KEY_OF_PAGE[e['_page']]][0]
    if page_key not in e['triggerWords']:
        continue
    wins = [w for h in e['_holders'] for w in comp_win.get((e['_page'], h), [])]
    if not wins:
        V81_COUNT['纷争纪49没有旅伴条照旧'] += 1
        continue
    r_ = _ranges(sorted(set(y for rr, _ in wins for a, b in rr for y in range(a, b + 1))))
    shan_ = any(s for _, s in wins)
    g_, how_, cov_ = gate_for('纷争纪', r_, shan_)
    if g_ is None or cov_ == [STRIFE_KEY_OF_PAGE[e['_page']]]:
        V81_COUNT['纷争纪49照旧'] += 1
        continue
    if swap_gate(e, page_key, g_):
        V81['纷争纪49'].append('%s｜持有人 %s → %s（%s）' % (title_of(e), '、'.join(e['_holders']), _cov_name(cov_), how_))
        V81_COUNT['纷争纪49改了'] += 1
        V81_WIN[id(e)] = ('纷争纪', r_, shan_)
for e in page_entries:
    if e['_era'] == '纷争纪' and e['folder'][:2] == '49' and e.get('_gate_fixed'):
        V81_COUNT['纷争纪49挂了STAR_GATE不动'] += 1

# 月银纪 46、47、49、51 里只认〔月银纪·正则〕的
moon_person_seen = set()
for e in batch_entries + page_entries:
    if e['_era'] != '月银纪' or e['folder'][:2] not in ('46', '47', '49', '51') or e['triggerWordsType'] != 'AND' or MG_ not in e['triggerWords']:
        continue
    t, fd = title_of(e), e['folder'][:2]
    if fd == '46':
        moon_person_seen.add(t)
        if t not in MOON_PERSON_WINDOW:
            V81['月银纪46'].append('%s｜不在 MOON_PERSON_WINDOW 里，照旧' % t); V81_COUNT['月银纪46照旧'] += 1
            continue
        w_ = MOON_PERSON_WINDOW[t]
        if w_ is None:
            V81['月银纪46'].append('%s｜整一纪都在，照旧' % t); V81_COUNT['月银纪46照旧'] += 1
            continue
        g_, how_, cov_ = gate_for('月银纪', [w_])
        if g_ is None:
            V81['月银纪46'].append('%s｜%d到%d 覆盖%s，照旧' % (t, w_[0], w_[1], how_)); V81_COUNT['月银纪46照旧'] += 1
            continue
        if swap_gate(e, MG_, g_):
            V81['月银纪46'].append('%s｜%d到%d → %s（%s）' % (t, w_[0], w_[1], _cov_name(cov_), how_)); V81_COUNT['月银纪46改了'] += 1
            V81_WIN[id(e)] = ('月银纪', [w_], True)
    elif fd == '51':
        # 传奇照年份黑名单推窗，跟纷争纪 51 一个做法：从成名那一年到纪末，窗覆盖整一纪的照旧
        r_, _ = bl_window(e, '月银纪')
        if not r_:
            V81['月银纪51'].append('%s｜没有年份黑名单，照旧' % t); V81_COUNT['月银纪51照旧'] += 1
            continue
        g_, how_, cov_ = gate_for('月银纪', r_)
        win_s = '、'.join('%d到%d' % ab if ab[0] != ab[1] else '%d' % ab[0] for ab in r_)
        if g_ is None:
            V81['月银纪51'].append('%s｜窗 %s 覆盖%s，照旧' % (t, win_s, how_)); V81_COUNT['月银纪51照旧'] += 1
            continue
        if swap_gate(e, MG_, g_):
            V81['月银纪51'].append('%s｜窗 %s → %s（%s；黑名单推的窗）' % (t, win_s, _cov_name(cov_), how_)); V81_COUNT['月银纪51改了'] += 1
            V81_WIN[id(e)] = ('月银纪', r_, True)
    else:
        why_ = {'49': 'STAR_GATE 有意挂〔月银纪·正则〕的，照旧', '47': '月银纪·旅伴总条，照旧'}[fd]
        V81['月银纪' + fd].append('%s｜%s' % (t, why_)); V81_COUNT['月银纪%s照旧' % fd] += 1
for t in set(MOON_PERSON_WINDOW) - moon_person_seen:
    problems.append('MOON_PERSON_WINDOW 里的条目找不到：' + t)
for t in set(STRIFE_PERSON_WINDOW) - set(title_of(e) for e in page_entries if e['_era'] == '纷争纪'):
    problems.append('STRIFE_PERSON_WINDOW 里的条目找不到：' + t)

# 三、月银纪第一到三批直醒的四十条改成同时满足
def merge_trig(ws):
    alts = []
    for w in ws:
        for a in (split_top(_body(w)) if is_rx(w) else [re.escape(w)]):
            if a not in alts:
                alts.append(a)
    return '/' + '|'.join(alts) + '/'
direct_before = {}                        # 标题 → 原来的触发（模拟里认纷争纪源稿里出现过的那些词）
seen_direct = set()
for e in batch_entries:
    t = title_of(e)
    if e['triggerWordsType'] != 'OR' or not any(w in e['blackListWords'] for w in ALIASES['〔别纪〕']):
        continue
    if t not in MOON_DIRECT_WINDOW:
        V81['月银纪直醒'].append('%s｜不在 MOON_DIRECT_WINDOW 里，照旧直醒' % t); V81_COUNT['直醒照旧'] += 1
        continue
    seen_direct.add(t)
    direct_before[t] = list(e['triggerWords'])
    w_ = MOON_DIRECT_WINDOW[t]
    if w_ is None:
        g_, how_, cov_ = MG_, '整一纪，认〔月银纪·正则〕', []
    else:
        g_, how_, cov_ = gate_for('月银纪', [w_])
        if g_ is None:
            g_, how_ = MG_, how_ + '，认〔月银纪·正则〕'
    trig_ = merge_trig(e['triggerWords'])
    for p_ in regex_problems(trig_):
        problems.append('%s 并成一条的触发 %s' % (t, p_))
    e['triggerWords'] = [g_, trig_]
    e['triggerWordsType'] = 'AND'
    e['triggerRange'] = ['user', 'assistant']
    GATE_RX.add(g_)
    V81['月银纪直醒'].append('%s｜%s → %s（%s）' % (t, ('%d到%d' % w_) if w_ else '整一纪', _cov_name(cov_) or '〔月银纪·正则〕', how_))
    V81_COUNT['直醒改成同时满足'] += 1
    V81_WIN[id(e)] = ('月银纪', [w_] if w_ else [(1, ERA_MAX['月银纪'])], True)
for t in set(MOON_DIRECT_WINDOW) - seen_direct:
    problems.append('MOON_DIRECT_WINDOW 里的条目找不到或者不是直醒：' + t)

for e in page_entries:
    for k in ('_page', '_star', '_holders', '_gate_fixed'):
        e.pop(k, None)

# 引用跟着改了的标题走
cite_map = dict(ED['CITE'])
for it in batch_items:
    if it['old_title'] != it['title']:
        cite_map['「%s」' % it['old_title']] = '「%s」' % it['title']
for o, n in REF_RENAME.items():
    cite_map['「%s」' % o] = '「%s」' % n
cite_log = collections.Counter()
for e in batch_entries + page_entries:
    for o, n in cite_map.items():
        if o in e['content']:
            cite_log[(o, n)] += e['content'].count(o)
            e['content'] = e['content'].replace(o, n)
meta_log = collections.Counter()
for e in page_entries:
    for rx_, rep_ in ED['META_RX']:
        e['content'], k_ = re.subn(rx_, rep_, e['content'])
        meta_log[rx_[:24]] += k_
    e['content'] = re.sub(r'\n{2,}', '\n', e['content'])
for rx_, _ in ED['META_RX']:
    if not meta_log[rx_[:24]]:
        problems.append('版本说明的清理没有命中：' + rx_[:30])
META_LEFT = re.compile(r'第[一二三]批里|旧稿|第三版|改名表|\br[1-4]\b|第十稿|新起的一个时段|这一稿')
for e in page_entries:
    for m_ in META_LEFT.finditer(e['content']):
        problems.append('%s 还剩版本说明：%s' % (title_of(e), e['content'][max(0, m_.start() - 20):m_.end() + 20]))

# ---------- 优先级：两纪排在底卡后面，文件夹 40 到 55 一段一段排，带宽照条数摊，同一带里月银纪在前、纷争纪在后，挤不下的并列 ----------
DEMOS = ['月银纪·示范', '纷争纪·示范']
all_new = batch_entries + page_entries
by_folder = collections.defaultdict(list)
moon_order = sorted(batch_entries, key=lambda x: x['_oldpri']) + [e for e in page_entries if e['_era'] == '月银纪']
strife_order = [e for e in page_entries if e['_era'] == '纷争纪']
for e in moon_order + strife_order:
    if title_of(e) in DEMOS:
        continue
    by_folder[e['folder'][:2]].append(e)
LO, HI = 7550, 8191
fds = sorted(by_folder)
for fd in fds:
    if not ('40' <= fd <= '55'):
        problems.append('文件夹 %s 不在 40 到 55 之间' % fd)
total = sum(len(by_folder[f]) for f in fds)
slots = HI - LO + 1
width = {f: max(1, min(len(by_folder[f]), slots * len(by_folder[f]) // total)) for f in fds}
left_ = slots - sum(width.values())
while left_ > 0:
    cand = [f for f in fds if width[f] < len(by_folder[f])]
    if not cand:
        break
    f = max(cand, key=lambda x: len(by_folder[x]) / width[x])
    width[f] += 1; left_ -= 1
BANDS, a_ = {}, LO
for f in fds:
    BANDS[f] = (a_, a_ + width[f] - 1); a_ += width[f]
if a_ - 1 > HI:
    problems.append('优先级带排出界了：到 %d' % (a_ - 1))
entries = []
for fd in fds:
    a, b = BANDS[fd]
    es = by_folder[fd]
    span = b - a + 1
    for i, e in enumerate(es):
        e['priority'] = a + (i if len(es) <= span else i * span // len(es))
    entries += es
for dt in DEMOS:
    d_ = [e for e in all_new if title_of(e) == dt]
    if len(d_) != 1:
        problems.append('示范「%s」找到 %d 条' % (dt, len(d_))); continue
    d_[0]['priority'] = 8192
    entries.append(d_[0])
meta_of = {id(e): (e.pop('_src', ''), e.pop('_oldpri', None), e.pop('_era', None)) for e in entries}
era_of = {id(e): meta_of[id(e)][2] for e in entries}

# ---------- 校验 ----------
titles = [title_of(e) for e in entries]
for t, c in collections.Counter(titles).items():
    if c > 1:
        problems.append('标题重复：%s ×%d' % (t, c))
haystack = SYSP + '\n'.join(e['content'] for e in old)
all_titles = set(titles) | old_titles
BAD_CHARS = ['——', '—', '；', '…', '！', '★', '（#']
def text_bad(c):
    out = []
    for bad in BAD_CHARS:
        if bad == '！' and c.count('！') == c.count(LAST_WORDS) * 2:
            continue
        if bad in c:
            out.append(bad)
    return out
for e in entries:
    t = title_of(e)
    if t in old_titles:
        problems.append('与底卡条目同名：' + t)
    if not (1 <= len(e['triggerWords']) <= 20):
        problems.append('%s 触发词 %d 个' % (t, len(e['triggerWords'])))
    if len(e['blackListWords']) > 20:
        problems.append('%s 黑名单 %d 个' % (t, len(e['blackListWords'])))
    for w in e['triggerWords'] + e['blackListWords']:
        if len(w) > 1024 or not w.strip():
            problems.append('%s 触发词不合规：%r' % (t, w))
        if is_rx(w):
            for p_ in regex_problems(w):
                problems.append('%s 正则 %s：%s' % (t, p_, w[:60]))
    if e['triggerWordsType'] == 'AND' and not any(is_gate(w) for w in e['triggerWords']):
        problems.append(t + ' 同时满足里没有纪元或时段的门控')
    if era_of[id(e)] == '纷争纪' and e['triggerWordsType'] != 'AND' and t not in NO_GATE:
        # 直醒的只许是常驻、纪元钟、示范这种触发全是门控的（纪元钟另认第二十二张的开局口令）
        if not all(is_gate(w) or w.startswith('/开局时段：第二十二张') for w in e['triggerWords']):
            problems.append(t + ' 纷争纪的直醒条目（触发里有不是门控的词），又不在 NO_GATE 里')
    if t in NO_GATE and (e['triggerRange'] != ['user'] or e['triggerWordsType'] != 'OR'):
        problems.append(t + ' 不挂门控的条目只许直醒、只扫用户')
    if not (0 <= e['priority'] <= 8192):
        problems.append(t + ' 优先级越界')
    c = e['content']
    for bad in text_bad(c):
        problems.append('%s 正文里有「%s」' % (t, bad))
    for line in c.split('\n')[1:]:
        bare = re.sub(r'「[^」]*」|`[^`]*`|“[^”]*”', '', line)
        if '：' in bare and not re.match(r'^(- )?[^，。：]{1,8}：', bare) and not line.startswith('#'):
            problems.append('%s 冒号：%s' % (t, line[:40]))
    for m_ in re.finditer(r'(?<!•)「([^」]+)」', c):
        ref = m_.group(1)
        if ref.startswith('纪元：'):
            continue
        if not any(x == ref or x.startswith(ref) for x in all_titles):
            problems.append('%s 引用了不存在的条目「%s」' % (t, ref))
    if len(c) > 100000:
        problems.append(t + ' 太长')
for t in NO_GATE:
    if t not in titles:
        notes.append('不挂门控的条目「%s」这一回没有（%s）' % (t, '源稿还没落盘' if not os.path.exists(TOTAL_CARD_FILE) else '源稿里没读到'))

# 另两路底卡补丁新写的字：标点、禁名、月相、引用
MOON_WORDS = re.compile(r'新月|满月|残月|月牙|弦月|月亮|月光|月相')
for nm, i, new_, old_ in ext_new_texts:
    # 只算新添的：旧串（rewrite 是整条原文）里本来就有的不算，底卡原有的破折号不顺手改
    for bad in text_bad(new_):
        if new_.count(bad) > (old_ or '').count(bad):
            problems.append('%s #%d 新写的字里有「%s」' % (nm, i, bad))
    if '厄洛伽' in new_:
        problems.append('%s #%d 新写的字里点了不该点的名' % (nm, i))
    if MOON_WORDS.search(new_):
        problems.append('%s #%d 新写的字里有月相字眼：%s' % (nm, i, MOON_WORDS.search(new_).group(0)))
    for m_ in re.finditer(r'「([^」]+)」', new_):
        ref = m_.group(1)
        if ref.startswith('纪元：') or (old_ and '「%s」' % ref in old_):
            continue
        if not any(x == ref or x.startswith(ref) for x in all_titles):
            notes.append('%s #%d 新写的字里引了「%s」，标题里找不到（底卡里的「」不全是条目名，看一眼）' % (nm, i, ref))
for o in REF_RENAME:
    for i, e in enumerate(old):
        if '「%s」' % o in e['content']:
            notes.append('底卡 #%d %s 里还引着旧名「%s」' % (i, title_of(e)[:20], o))

# 门控钥匙不能在底卡里中
for w in sorted(GATE_RX):
    body = w[1:w.rfind('/')]
    if re.search(body, haystack):
        problems.append('门控正则在底卡里能中：' + w[:60])
for k in ('〔月银纪〕', '〔纷争纪〕'):
    for w in ALIASES[k]:
        if w in haystack:
            problems.append('门控钥匙在底卡里出现过：%r' % w)
cred_rx = ALIASES['〔迷宫纪凭证〕'][0][1:ALIASES['〔迷宫纪凭证〕'][0].rfind('/')]
if not re.search(cred_rx, '命途已确认，请记录我的《奥尔德兰》角色建档：\n【一·灵魂形态】'):
    problems.append('〔迷宫纪凭证〕挡不住迷宫纪的建档凭证')

# 直醒（OR、黑名单挡别纪）的名字不该在底卡里出现
for e in entries:
    if e['triggerWordsType'] != 'OR' or not any(w in e['blackListWords'] for w in ALIASES['〔别纪〕']):
        continue
    for w in e['triggerWords']:
        for a in (split_top(w[1:w.rfind('/')]) if is_rx(w) else [w]):
            if '(?' in a or any(ch in a for ch in '[]()^$\\.'):
                continue
            if a and a in haystack:
                problems.append('直醒条目的名字撞了底卡：%s「%s」' % (title_of(e), a))

# ---------- 触发 ----------
_RX_C = {}
def _compiled(w):
    c = _RX_C.get(w, 0)
    if c != 0:
        return c
    if regex_problems(w):
        c = None
    else:
        body, flags = w[1:w.rfind('/')], w[w.rfind('/') + 1:]
        f = (re.I if 'i' in flags else 0) | (re.M if 'm' in flags else 0) | (re.S if 's' in flags else 0)
        c = re.compile(body, f)
    _RX_C[w] = c
    return c

def _match(w, t):
    if is_rx(w):
        c = _compiled(w)
        return c is not None and c.search(t) is not None
    return w in t

def fires(e, msgs, sysp):
    if not e.get('enabled', True):
        return False
    d = e.get('scanDepth', 1)
    d = 3 if not d else d
    rng = e.get('triggerRange', ['user'])
    units = [x for r, x in msgs[-d:] if r in rng] + ([sysp] if 'system' in rng else [])
    tw, bl = e['triggerWords'], e.get('blackListWords') or []
    for t in units:
        hits = [w for w in tw if _match(w, t)]
        if not (len(hits) == len(tw) if e.get('triggerWordsType') == 'AND' else hits):
            continue
        bh = [w for w in bl if _match(w, t)]
        if bl and (len(bh) == len(bl) if e.get('blackListWordsType') == 'AND' else bh):
            continue
        return True
    return False

# ---------- 开局口令 ----------
MAINLINES = []                                   # 月银纪
S_MAINLINES = []                                 # 纷争纪：(主线名, 页名, [开局时段里认的名字])
for e in entries:
    t = title_of(e)
    m = re.match(r'^月银纪·主线｜(.+)$', t)
    if m:
        MAINLINES.append(m.group(1))
    m = re.match(r'^纷争纪·主线｜(.+)$', t)
    if m:
        k = '〔主线·%s〕' % m.group(1)
        w = ALIASES.get(k, [mainline_rx(m.group(1))])[0]
        names_ = []
        mm = re.search(r'开局时段：(\(\?:(.*?)\)|[^|/]+)(?:\||/$|$)', w[1:])
        if mm:
            inner = mm.group(2) if mm.group(2) is not None else mm.group(1)
            for a in split_top(inner):
                a = re.sub(r'\(\?[=!][^)]*\)', '', a)
                if a:
                    names_.append(a)
        if not names_:
            problems.append('纷争纪主线「%s」的钥匙里读不出开局时段的名字：%s' % (m.group(1), w[:60]))
        S_MAINLINES.append((m.group(1), m.group(1).split('·')[0], names_))
OPENINGS = [('月银纪', m, '纪元：月银纪｜开局时段：' + m) for m in MAINLINES]
OPENINGS.append(('月银纪', '万兽·焚原', '纪元：月银纪｜开局时段：万兽·焚原｜出身：黄金裔'))
S_OPENINGS = []
for ml, pname, names_ in S_MAINLINES:
    for nm in names_:
        S_OPENINGS.append(('纷争纪', ml, '纪元：纷争纪｜开局时段：' + nm))
S_OPENINGS.append(('纷争纪', '抽一张', '纪元：纷争纪｜开局时段：抽一张'))
S22_YEARS = ['元', 120, 121, 300, 301, 1050, 1051, 4500, 4501, 8800, 8801, 10800, 10801, 11034]
for y in S22_YEARS:
    S_OPENINGS.append(('纷争纪', '第二十二张·%s' % y, '纪元：纷争纪｜开局时段：第二十二张｜年份：%s' % y))
S_OPENINGS.append(('纷争纪', '白石的年月·赤土之冠', '纪元：纷争纪｜开局时段：赤原｜出身：黄金裔'))
ALL_OPENINGS = OPENINGS + S_OPENINGS

OLD_PATCH = {14: '月银纪：详细正史', 29: '月银纪·各族发展史', 33: '精灵详史·月银纪', 34: '矮人详史·月银纪',
             35: '半身人详史·月银纪', 36: '兽耳族详史·月银纪', 37: '龙裔详史·月银纪', 38: '魔族详史·月银纪',
             39: '圣堂详史·月银纪', 43: '真龙详史·月银纪', 44: '月银纪·各族传奇与英雄名录',
             157: '神域之路·其一', 485: '魔族七大类'}
for i, prefix in OLD_PATCH.items():
    if not title_of(old[i]).startswith(prefix):
        raise SystemExit('旧条目 #%d 对不上：%s' % (i, title_of(old[i])))
wake_era = collections.defaultdict(set)
for era, m, u in ALL_OPENINGS:
    for i, e in enumerate(old):
        if i in OLD_PATCH and era == '月银纪':
            continue
        if title_of(e).startswith('世界自转'):
            continue
        if fires(e, [('user', u)], SYSP):
            wake_era[i].add(era)
patched_old = copy.deepcopy(old)
patch_lines = []
for i in sorted(set(OLD_PATCH) | set(wake_era)):
    e = patched_old[i]
    eras = set(wake_era.get(i, set())) | ({'月银纪'} if i in OLD_PATCH else set())
    # 只扫用户，或者深度 1（只看玩家这一条）的，加了黑名单只挡带「纪元：月银纪」这类字的那一句，迷宫纪的局不受影响
    if e.get('triggerRange') != ['user'] and e.get('scanDepth') != 1:
        problems.append('旧条目 #%d %s 不是只扫用户，开局口令叫醒了它，黑名单的效果要另算' % (i, title_of(e)[:20]))
        continue
    if e.get('blackListWords') and e.get('blackListWordsType') != 'OR':
        raise SystemExit('旧条目 #%d 原有黑名单是 AND，不能直接追加' % i)
    bl = list(e.get('blackListWords') or [])
    added = []
    for era in sorted(eras):
        added += [w for w in ALIASES['〔%s〕' % era] if w not in bl + added]
    e['blackListWords'] = bl + added
    e['blackListWordsType'] = 'OR'
    if len(e['blackListWords']) > 20:
        problems.append('旧条目 #%d 黑名单超过 20 个' % i)
    patch_lines.append('旧 #%d %s  黑名单 +%d（%s的开局口令%s）' % (i, title_of(e)[:30], len(added), '、'.join(sorted(eras)),
                                                       '，v5 的十三条' if i in OLD_PATCH else ''))
S_OPEN_EXPECT = set(PM.get('OPEN_WAKE_STRIFE', []))
s_got = set(i for i, er in wake_era.items() if '纷争纪' in er)
if S_OPEN_EXPECT and s_got != S_OPEN_EXPECT:
    notes.append('纷争纪开局口令叫醒的底卡跟清单不一样：多了 %s，少了 %s' % (sorted(s_got - S_OPEN_EXPECT), sorted(S_OPEN_EXPECT - s_got)))
# 回复里会醒的（范围含助手），照表加锚，不走只扫用户那一道检查
for i, (prefix, eras) in sorted(PM.get('REPLY_BL', {}).items()):
    e = patched_old[i]
    if not title_of(e).startswith(prefix):
        raise SystemExit('回复黑名单那张表对不上 #%d：%s' % (i, title_of(e)))
    if e.get('blackListWords') and e.get('blackListWordsType') != 'OR':
        raise SystemExit('旧条目 #%d 原有黑名单是 AND，不能直接追加' % i)
    bl = list(e.get('blackListWords') or [])
    added = []
    for era in eras:
        added += [w for w in ALIASES['〔%s〕' % era] if w not in bl + added]
    e['blackListWords'] = bl + added
    e['blackListWordsType'] = 'OR'
    if len(e['blackListWords']) > 20:
        problems.append('旧条目 #%d 黑名单超过 20 个' % i)
    patch_lines.append('旧 #%d %s  黑名单 +%d（回复里会醒，挡%s的底座）' % (i, title_of(e)[:30], len(added), '、'.join(eras)))

full = patched_old + entries
N_OLD = len(old)
short = lambda t: t.replace('月银纪·', '').replace('纷争纪·', '')

def run(msgs, sysp=SYSP):
    got = [i for i, e in enumerate(full) if fires(e, msgs, sysp)]
    news = [i for i in got if i >= N_OLD]
    olds = [i for i in got if i < N_OLD and not title_of(full[i]).startswith('世界自转')]
    return news, olds

def fmt(news):
    return '%d 条 %d 字｜%s' % (len(news), sum(len(full[i]['content']) for i in news), '、'.join(short(title_of(full[i])) for i in news))

def era_i(i):
    return era_of.get(id(full[i]))

def gated_for(i, era):
    """别纪的条目在这一纪的局里醒，只许是 STAR_GATE 挂过这一纪门控的星"""
    return any(is_rx(w) and w in GATE_RX and era in w for w in full[i]['triggerWords'])

# ---------- 模拟一：开局口令 ----------
PERIOD_TITLE = {}
for e in entries:
    m = re.match(r'^月银纪·时段｜(诸国·.+|崛起|帝国|魔族之世|末年)$', title_of(e))
    if m:
        PERIOD_TITLE[m.group(1)] = title_of(e)
def period_of(ml):
    for k in ['晨祷', '午祷', '晚祷', '夜祷']:
        body = ALIASES['〔时段·诸国·%s〕' % k][0]
        if re.search(body[1:body.rfind('/')], '开局时段：' + ml):
            return '诸国·' + k
    for k in ['崛起', '帝国', '魔族之世', '末年']:
        body = ALIASES['〔时段·%s·正则〕' % k][0]
        if re.search(body[1:body.rfind('/')], '开局时段：' + ml):
            return k
    return None
CLOCK_OF = [((1, 1050), '纷争纪·纪元钟｜前一千年'), ((1051, 8800), '纷争纪·纪元钟｜神战的年月'), ((8801, 11034), '纷争纪·纪元钟｜死域的年月')]
def strife_period_of_year(y):
    for pn, (lo, hi) in STRIFE_SPAN.items():
        if lo <= y <= hi:
            return pn
sim_lines = []
for era, m, u in ALL_OPENINGS:
    news, olds = run([('user', u)])
    names = [title_of(full[i]) for i in news]
    label = u.split('开局时段：')[1]
    sim_lines.append('%-22s %s' % (('〔月〕' if era == '月银纪' else '〔纷〕') + label, fmt(news)))
    if olds:
        problems.append('开局口令「%s」还会叫醒旧条目 %s' % (u, olds))
    other = [title_of(full[i]) for i in news if era_i(i) != era and not gated_for(i, era)]
    if other:
        problems.append('开局口令「%s」叫醒了别纪的条目：%s' % (u, '、'.join(other)))
    if era == '月银纪':
        need = ['月银纪·常驻｜这一局在月银纪', '月银纪·示范', '月银纪·主线｜' + m]
        pk = period_of(m) if m.startswith(('诸国·', '崛起·', '帝国·', '魔族之世·', '末年·')) else None
        if pk:
            need.append(PERIOD_TITLE.get(pk, '月银纪·时段｜' + pk))
        forbid = []
    else:
        need = ['纷争纪·常驻｜这一局在纷争纪', '纷争纪·示范']
        forbid = []
        if m == '抽一张':
            extra = [t for t in names if t not in need]
            if extra:
                problems.append('开局口令「抽一张」除了常驻和示范还叫醒了：%s' % '、'.join(extra))
        elif m.startswith('第二十二张'):
            y = 1 if m.endswith('元') else int(m.split('·')[1])
            need += ['纷争纪·时段｜' + strife_period_of_year(y)] + [t for (lo, hi), t in CLOCK_OF if lo <= y <= hi]
            forbid = [t for t in names if t.startswith('纷争纪·主线｜')]
        else:
            need += ['纷争纪·主线｜' + m, '纷争纪·时段｜' + m.split('·')[0]]
    for n_ in need:
        if n_ not in names:
            problems.append('开局口令「%s」没叫醒「%s」' % (u, n_))
    if forbid:
        problems.append('开局口令「%s」叫醒了主线：%s' % (u, '、'.join(forbid)))
    ng = [t for t in names if t in NO_GATE]
    if ng:
        problems.append('开局口令「%s」叫醒了不挂门控的条目：%s' % (u, '、'.join(ng)))

# ---------- 模拟二：每一页一条假回复（底座日期＋潮汐＋主线开局那一段），看醒多少 ----------
def hud(date, tide, place='某地'):
    return ('<details class="arc-hud-details"><summary class="arc-hud-summary"><div class="hud-summary-inner">'
            '<span class="hud-title-icon">✦</span><b>推演底座</b><span class="hud-meta">%s · 09:20 · %s · %s · 防抢话 开</span>'
            '</div></summary><div class="detail-body arc-hud-body"><div class="hud-grid"><div><b>日期</b><br>%s</div>'
            '<div><b>地点</b><br>%s</div><div><b>潮汐</b><br>%s</div></div>'
            '<div class="f path"><b>命路</b>命路未定｜职业 未认兵(Common)｜命星 未觉醒</div>'
            '<div class="f job"><b>职业</b>未认兵·Ⅰ｜职业 未就职</div></div></details>\n\n' % (date, place, tide, date, place, tide))
def era_date(era, yr, rest='·秋·坠叶月·上旬三日'):
    if era == '纷争纪' and yr == 'C':
        return '山铜纪元年·冬·归寂月·上旬三日'
    return '%s%s年%s' % (era, yr, rest)

ML_INFO = {}
for e in entries:
    m = re.match(r'^(月银纪|纷争纪)·主线｜(.+)$', title_of(e))
    if not m:
        continue
    c = e['content']
    op = re.search(r'(?m)^开局：(.*)$', c)
    op = op.group(1) if op else c.split('\n')[2][:300]
    e_ = dict(e); e_['_era'] = m.group(1)
    ML_INFO[(m.group(1), m.group(2))] = (ml_year(e_), op)
OPEN_NAME = {ml: names_[0] for ml, _, names_ in S_MAINLINES if names_}
load_lines = []
load_runs = list(ML_INFO.items()) + [(('纷争纪', '号角的年月·雨城的星'), ('C', ML_INFO.get(('纷争纪', '号角的年月·雨城的星'), (None, ''))[1]))]
mid_old = collections.Counter()
for (era, ml), (yr, op) in load_runs:
    if yr is None:
        load_lines.append('%s：主线里找不到年份' % ml); continue
    msg = hud(era_date(era, yr), ml + '·一幕') + op
    cmd = '纪元：%s｜开局时段：%s' % (era, ml if era == '月银纪' else OPEN_NAME.get(ml, ml))
    news, olds = run([('user', cmd), ('assistant', msg), ('user', '继续')])
    load_lines.append('〔%s〕%-18s %s年 %s' % (era[:1], ml, '山铜纪元' if yr == 'C' else yr, fmt(news)))
    other = [title_of(full[i]) for i in news if era_i(i) != era and not gated_for(i, era)]
    borrowed_ = [title_of(full[i]) for i in news if era_i(i) != era and gated_for(i, era)]
    if borrowed_:
        load_lines.append('    其中借来的别纪的星 %d 颗：%s' % (len(borrowed_), '、'.join(borrowed_)))
    if other:
        problems.append('%s 一幕的假回复叫醒了别纪的条目：%s' % (ml, '、'.join(other)))
    if olds:
        load_lines.append('    底卡 %d 条：%s' % (len(olds), '、'.join('#%d %s' % (i, title_of(full[i])[:14]) for i in olds)))
        if era == '纷争纪':
            for i in olds:
                mid_old[i] += 1

# ---------- 模拟三：串段。一页的旅伴、人物、命星，在别的时段的回复里被点名，醒不醒 ----------
page_of = {}
for e, it in zip(page_entries, [x for x in page_items if x.get('setting')]):
    page_of[id(e)] = it['page']
page_ml = collections.defaultdict(list)
for e in page_entries:
    m = re.match(r'^(?:月银纪|纷争纪)·主线｜(.+)$', title_of(e))
    if m:
        page_ml[page_of[id(e)]].append(m.group(1))
names_by_page = collections.defaultdict(list)
for e in page_entries:
    t = title_of(e)
    m = re.match(r'^旅途同行：(.+?)（', t)
    if m:
        names_by_page[page_of[id(e)]].append(m.group(1).split('·')[0])
cross_lines = []
for group, era in ((MOON_PAGES, '月银纪'), (STRIFE, '纷争纪')):
    if FAST:
        cross_lines.append('（--fast，%s的串段没跑）' % era); continue
    for tag in group:
        mls = page_ml.get(tag, [])
        if not mls or ML_INFO.get((era, mls[0]), (None,))[0] is None:
            continue
        yr = ML_INFO[(era, mls[0])][0]
        # 后面的段讲起前面段里的人（一次讲一个人，一条回复）
        earlier = [(p, n) for p in group[:group.index(tag)] for n in dict.fromkeys(names_by_page.get(p, []))]
        per_fd, chars, worst = collections.Counter(), 0, []
        for p, n in earlier:
            msg = hud(era_date(era, yr), mls[0] + '·二幕') + '火边有人说起%s当年的事。' % n
            news, _ = run([('assistant', msg)])
            got = [i for i in news if page_of.get(id(full[i])) == p and full[i]['folder'][:2] in ('46', '47', '49')]
            for i in got:
                per_fd[full[i]['folder'][:2]] += 1
            c_ = sum(len(full[i]['content']) for i in got)
            chars += c_
            if got:
                worst.append((c_, n, len(got)))
        if earlier:
            worst.sort(reverse=True)
            cross_lines.append('%s（%s年）：讲起前面 %d 个人，醒了旧段的人物 %d、旅伴 %d、命星 %d，共 %d 字｜最多的：%s' % (
                tag, yr, len(earlier), per_fd['46'], per_fd['47'], per_fd['49'], chars,
                '、'.join('%s %d条%d字' % (n, k, c_) for c_, n, k in worst[:4])))

# ---------- 模拟四：跨纪漏检 ----------
NEW_NAMES = {'月银纪': [], '纷争纪': []}
for e in page_entries:
    t = title_of(e)
    m = re.match(r'^旅途同行：(.+?)（', t) or re.match(r'^(.+?)（人物）', t) or re.match(r'^灾祸之兽｜(.+)$', t) \
        or re.match(r'^凡世至强：(.+?)（', t) or re.match(r'^(.+?) \((?:Special|Passive|Art|Ability) \|', t)
    if m and era_of.get(id(e)) in NEW_NAMES:
        NEW_NAMES[era_of[id(e)]].append(m.group(1))
cross_era_lines = []
moon_ml = [k for k in ML_INFO if k[0] == '月银纪']
strife_ml = [k for k in ML_INFO if k[0] == '纷争纪']
# 月银纪的回复里点纷争纪的名字，纷争纪条目一条不醒
for (era, ml) in moon_ml[::6]:
    yr, op = ML_INFO[(era, ml)]
    msg = hud(era_date(era, yr), ml + '·二幕') + '、'.join(NEW_NAMES['纷争纪'])
    news, _ = run([('assistant', msg)])
    bad = [title_of(full[i]) for i in news if era_i(i) == '纷争纪']
    cross_era_lines.append('月银纪 %s 的回复点纷争纪的名字 %d 个：纷争纪条目醒 %d 条%s' % (ml, len(NEW_NAMES['纷争纪']), len(bad),
                                                                     ('｜' + '、'.join(bad[:8])) if bad else ''))
    for t in bad:
        problems.append('月银纪的回复叫醒了纷争纪条目（%s）：%s' % (ml, t))
# 纷争纪的回复里点月银纪的名字，月银纪条目只许挂了纷争纪门控的星醒
def strife_gated(i):
    return gated_for(i, '纷争纪')
for (era, ml) in strife_ml[::3]:
    yr, op = ML_INFO[(era, ml)]
    msg = hud(era_date(era, yr), ml + '·二幕') + '、'.join(NEW_NAMES['月银纪'])
    news, _ = run([('assistant', msg)])
    moon_hit = [i for i in news if era_i(i) == '月银纪']
    bad = [title_of(full[i]) for i in moon_hit if not strife_gated(i)]
    cross_era_lines.append('纷争纪 %s 的回复点月银纪的名字 %d 个：月银纪条目醒 %d 条（挂了纷争纪门控的星 %d，别的 %d）%s' % (
        ml, len(NEW_NAMES['月银纪']), len(moon_hit), len(moon_hit) - len(bad), len(bad), ('｜' + '、'.join(bad[:8])) if bad else ''))
    for t in bad:
        problems.append('纷争纪的回复叫醒了月银纪条目（%s）：%s' % (ml, t))
# 月银纪第一到三批那四十条（v8 是直醒，v8.1 改成同时满足）：触发词在纷争纪源稿里出现过的那些，纷争纪的局里玩家打出来，应当一条都不醒
strife_src = '\n'.join(PAGE_TEXT[t] for t in STRIFE) + '\n'.join(open(f, encoding='utf-8').read() for t, f in SUPPS if t.startswith(('第一项', '补卷_')))
direct_hits = []
for e in entries:
    t_ = title_of(e)
    if era_of.get(id(e)) != '月银纪':
        continue
    if t_ in direct_before:
        ws0 = direct_before[t_]
    elif e['triggerWordsType'] == 'OR' and any(w in e['blackListWords'] for w in ALIASES['〔别纪〕']):
        ws0 = e['triggerWords']
    else:
        continue
    ws_ = []
    for w in ws0:
        for a in (split_top(w[1:w.rfind('/')]) if is_rx(w) else [w]):
            if '(?' in a or any(ch in a for ch in '[]()^$\\.') or len(a) < 2:
                continue
            if a in strife_src and a not in ws_:
                ws_.append(a)
    if ws_:
        direct_hits.append((t_, ws_))
cross_era_lines.append('月银纪那四十条里触发词在纷争纪源稿里出现过的 %d 条：' % len(direct_hits))
cross_era_lines += ['  %s｜%s' % (t_, '、'.join(ws_[:6])) for t_, ws_ in direct_hits]
place_lines = []
if direct_hits:
    words = [ws_[0] for t_, ws_ in direct_hits]
    worst_ = 0
    for (era, ml) in strife_ml:
        yr0, op0 = ML_INFO[(era, ml)]
        cmd0 = '纪元：纷争纪｜开局时段：' + OPEN_NAME.get(ml, ml)
        hist_ = [('user', cmd0), ('assistant', hud(era_date('纷争纪', yr0), ml + '·二幕') + op0)]
        base_, _ = run(hist_ + [('user', '继续')])
        base_ = set(base_)
        news, _ = run(hist_ + [('user', '、'.join(words))])
        moon_hit = [i for i in news if era_i(i) == '月银纪' and i not in base_]
        bad = [title_of(full[i]) for i in moon_hit if not gated_for(i, '纷争纪')]
        worst_ = max(worst_, len(moon_hit))
        for t in bad:
            problems.append('纷争纪的局（%s）玩家打月银纪地名，叫醒了月银纪条目：%s' % (ml, t))
        # 一个词一句也打一遍（只算这一句多叫醒的；上一条回复里点了名、借来的月银纪的星本来就醒，不算）
        per_ = 0
        for w in words:
            n_, _ = run(hist_ + [('user', '我想去%s看看' % w)])
            per_ += sum(1 for i in n_ if era_i(i) == '月银纪' and i not in base_)
        place_lines.append('纷争纪 %s 的局：玩家一句打全 %d 个词，月银纪条目多醒 %d 条；一词一句打 %d 句，合计多醒 %d 条' % (ml, len(words), len(moon_hit), len(words), per_))
        if per_:
            problems.append('纷争纪的局（%s）玩家一词一句打月银纪地名，月银纪条目多醒了 %d 条' % (ml, per_))
    cross_era_lines.append('纷争纪的局玩家打这 %d 个词：二十一段里月银纪条目醒得最多的一段 %d 条（应当 0）' % (len(words), worst_))

# v8.1 改了门控的条目正反各测一回：窗里那一年的回复点名要醒，窗外一段（不在覆盖的时段里）的回复点名不醒；月银纪那四十条另测玩家自己打不醒
def _probe_word(e):
    for w in e['triggerWords']:
        if is_gate(w) or w in GATE_RX:
            continue
        for a in (split_top(_body(w)) if is_rx(w) else [w]):
            if a and not any(ch in a for ch in '[]()^$\\.|?*+{}'):
                return a
    return None
probe_ok, probe_bad, probe_skip = 0, [], []
for e in entries:
    if id(e) not in V81_WIN:
        continue
    era_, r_, shan_ = V81_WIN[id(e)]
    w_ = _probe_word(e)
    if not w_:
        probe_skip.append(title_of(e)); continue
    y_in = r_[0][0]
    cov_ = [k for k in ERA_KEYS[era_] if any(not (b < KEY_SPAN[k][0] or a > KEY_SPAN[k][1]) for a, b in r_)]
    outside = [k for k in ERA_KEYS[era_] if k not in cov_]
    msg_in = hud(era_date(era_, y_in), '某处·二幕') + '有人说起%s。' % w_
    ok_in = fires(e, [('assistant', msg_in)], SYSP)
    ok_out = True
    if outside:
        y_out = KEY_SPAN[outside[0]][0]
        msg_out = hud(era_date(era_, y_out), '某处·二幕') + '有人说起%s。' % w_
        ok_out = not fires(e, [('assistant', msg_out)], SYSP)
    ok_user = not fires(e, [('user', '我想去%s看看' % w_)], SYSP) if title_of(e) in direct_before else True
    if ok_in and ok_out and ok_user:
        probe_ok += 1
    else:
        probe_bad.append('%s｜窗里%s醒，窗外%s，玩家自己打%s' % (title_of(e), '' if ok_in else '没', '不醒' if ok_out else '也醒了', '不醒' if ok_user else '醒了'))
for x in probe_bad:
    problems.append('v8.1 正反测没过：' + x)
cross_era_lines.append('v8.1 改了门控的条目正反测：过了 %d 条，没过 %d 条，找不到纯词可测的跳过 %d 条%s' % (
    probe_ok, len(probe_bad), len(probe_skip), ('（%s）' % '、'.join(probe_skip)) if probe_skip else ''))

# ---------- 模拟五：迷宫纪的局，两纪条目一条都不该醒 ----------
SAMPLES = os.path.join(ROOT, 'moon', 'samples')
read_sample = lambda n: open(os.path.join(SAMPLES, n), encoding='utf-8').read()
MAZE_CREDS = {
    '身穿凭证': '命途已确认，请记录我的《奥尔德兰》角色建档：\n\n【一·灵魂形态】\n降临之魂 · 身穿（连人带身跌入）\n\n【二·种族胎骨】\n人类\n\n'
            '【六·誓心与赐物】\n誓心阵营：中立善良\n神殿赐物：风语短剑（Rare）：一把会低鸣的短剑\n\n【七·现在何处】\n现在所在：阿卡迪亚·公会城\n\n开始游戏。',
    '本地凭证': '命途已确认，请记录我的《奥尔德兰》角色建档：\n\n【一·灵魂形态】\n本地之魂（生于此世）\n\n【六·你的前半生】\n'
            '出生地：金鸢城\n出身家世：神殿孤儿\n\n【七·现在何处】\n现在所在：阿卡迪亚·公会城\n\n开始游戏。',
}
MAZE_REPLY = ('<details class="arc-hud-details"><summary class="arc-hud-summary"><div class="hud-summary-inner">'
              '<span class="hud-title-icon">✦</span><b>推演底座</b><span class="hud-meta">迷宫纪1001年·春·萌芽月·上旬三日 · '
              '09:20 巳初 · 阿卡迪亚·公会城·旅印大厅 · 第一兆·魔兽离巢·潮位二 · 防抢话 开 · 档位 很长</span></div></summary>'
              '<div class="detail-body arc-hud-body"><div class="hud-grid"><div><b>日期</b><br>迷宫纪1001年·春·萌芽月·上旬三日</div>'
              '<div><b>地点</b><br>阿卡迪亚·公会城·旅印大厅</div><div><b>潮汐</b><br>第一兆·魔兽离巢·潮位二</div></div></div></details>\n\n'
              '公会的悬赏榜前挤满了人，七神圣堂的祭司站在神殿门口分圣水。')
maze_lines = []
def maze_check(tag, msgs, strict=True):
    news, _ = run(msgs)
    news_c = [i for i in news if title_of(full[i]) not in NO_GATE]
    maze_lines.append('%s：两纪条目 %d 条%s%s' % (tag, len(news), ('｜' + '、'.join(title_of(full[i]) for i in news[:30])) if news else '',
                                              '' if strict else '（玩家在迷宫纪里打两纪才有的专名，直醒条目会醒，v5 起就是这样定的，只记不算）'))
    if strict:
        for i in news_c:
            problems.append('迷宫纪的局漏进两纪条目（%s）：%s' % (tag, title_of(full[i])))
    return news
MAZE_CMD = '纪元：迷宫纪｜开局时段：默认时段｜出身：人类'
maze_real = read_sample('reply_迷宫纪首轮_人类.html')
for k, cred in MAZE_CREDS.items():
    maze_check('迷宫纪首轮·' + k, [('user', cred)])
maze_check('迷宫纪实测首轮·口令', [('user', MAZE_CMD)])
ALL_NEW_NAMES = NEW_NAMES['月银纪'] + NEW_NAMES['纷争纪']
if not FAST:
    for u in ['我想去神殿拜一拜七神', '去公会揭一张魔兽的悬赏，顺便问问报酬', '找个同伴一起走，最好是会治伤的', '我要自立为王，建一座城',
              '这附近有没有火山或者雪原', '拜师学剑，再去问问就职和转职', '找个诗人打听打听名号', '去协会问问大魔导收不收学徒',
              '我想去神坛前许个愿', '找钱商行换点钱', '去王道上走走', '河谷里的采石场还招人吗',
              '去长垒上看看那些刻名字的石头', '听说金鸢城以前打过很久的仗', '问问老兵当年墙上的事', '找人修一修这台机兵']:
        maze_check('迷宫纪中局·玩家「%s」' % u[:16], [('user', MAZE_CMD), ('assistant', maze_real), ('user', u)])
    for n in ALL_NEW_NAMES[::9]:
        maze_check('迷宫纪中局·玩家「我想打听%s的事」' % n[:12], [('user', MAZE_CMD), ('assistant', maze_real), ('user', '我想打听%s的事' % n)], strict=False)
maze_check('迷宫纪·回复里把新名字全提一遍', [('user', MAZE_CMD), ('assistant', MAZE_REPLY + '、'.join(ALL_NEW_NAMES))])
maze_check('迷宫纪·玩家把新名字全打一遍', [('user', MAZE_CMD), ('assistant', maze_real), ('user', '、'.join(ALL_NEW_NAMES))], strict=False)
# 二十二张的总条迷宫纪的局也叫得醒（翻刻本是玩家摸得到的线头）
total_lines = []
for t in NO_GATE:
    idx = [i for i in range(N_OLD, len(full)) if title_of(full[i]) == t]
    if not idx:
        total_lines.append('%s：这一回没有这一条' % t); continue
    for tag, msgs in [('迷宫纪中局·玩家问那副叫二十一张的旧牌', [('user', MAZE_CMD), ('assistant', maze_real), ('user', '集市上有人在卖一副叫二十一张的旧牌，翻刻本，我想问问来路')]),
                      ('纷争纪的局·玩家问二十二张', [('user', '纪元：纷争纪｜开局时段：执式者'), ('user', '那一副二十二张的旧牌是谁画的')]),
                      ('迷宫纪·回复里写到二十二张（只扫用户，不该醒）', [('user', MAZE_CMD), ('assistant', MAZE_REPLY + '桌上摊着一副二十二张的旧牌。')])]:
        news, _ = run(msgs)
        hit = idx[0] in news
        total_lines.append('%s：%s' % (tag, '醒' if hit else '没醒'))
        if ('不该醒' in tag) == hit:
            problems.append('总条「%s」%s：%s' % (t, tag, '醒了' if hit else '没醒'))

# ---------- 模拟六：v5 的焚原实测回复，再往下推一轮 ----------
moon_lines = []
MOON_RUNS = [
    ('焚原首轮·黄金裔（v4 实测）', read_sample('reply_焚原首轮_黄金裔_v4.html'), '纪元：月银纪｜开局时段：万兽·焚原｜出身：黄金裔',
     ['继续', '走向那个拿着木棍的青年（麦伦），问他麦仓城到底是怎么烧没的。', '拨开人群走到悬赏板前，把那张羊皮纸揭下来。']),
]
for tag, reply, cmd, users in MOON_RUNS:
    moon_lines.append('〔%s〕' % tag)
    for u in users:
        news, olds = run([('user', cmd), ('assistant', reply), ('user', u)])
        moon_lines.append('玩家「%s」：%s' % (u[:16], fmt(news)))
        if olds:
            moon_lines.append('    旧条目 %d 条：%s' % (len(olds), '、'.join('#%d %s' % (i, title_of(full[i])[:16]) for i in olds)))

# 面板上一直印着的字不该叫醒条目
panel_lines = []
for era, date, tide in (('月银纪', '月银纪1690年·秋·坠叶月·上旬三日', '万兽·焚原·一幕'),
                        ('纷争纪', '纷争纪233年·春·萌芽月·上旬三日', '白石的年月·合龙之车·一幕'),
                        ('纷争纪', '山铜纪元年·冬·归寂月·上旬三日', '号角的年月·雨城的星·一幕')):
    news, _ = run([('assistant', hud(date, tide))])
    panel_lines.append('只有面板的一条回复（%s %s）：%s' % (date, tide, fmt(news)))

# 纷争纪中局会醒的底卡（模拟二里纷争纪二十一段，再加几句寻常的玩家话）
if not FAST:
    for (era, ml) in strife_ml:
        yr, op = ML_INFO[(era, ml)]
        cmd = '纪元：纷争纪｜开局时段：' + OPEN_NAME.get(ml, ml)
        for u in ['去墙上看看', '找个酒馆坐坐，打听打听最近的仗', '去圣堂求个祝福', '问问这附近有什么魔兽']:
            news, olds = run([('user', cmd), ('assistant', hud(era_date(era, yr), ml + '·二幕') + op), ('user', u)])
            for i in olds:
                mid_old[i] += 1

# ---------- 模拟七：纷争纪的回复里写到纷争纪自己的词（各条的触发词），底卡哪些条会醒（范围含助手的那些） ----------
reply_base = collections.Counter()
reply_example = {}
n_words = 0
if not FAST:
    s_words = []
    for e in entries:
        if era_of.get(id(e)) != '纷争纪':
            continue
        for w in e['triggerWords']:
            if is_gate(w) or w.startswith('/开局时段：'):
                continue
            for a in (split_top(w[1:w.rfind('/')]) if is_rx(w) else [w]):
                if '(?' in a or any(ch in a for ch in '[]()^$\\.|{}*+?') or len(a) < 2:
                    continue
                s_words.append(a)
    s_words = dedupe(s_words)
    n_words = len(s_words)
    asst_old = [(i, e) for i, e in enumerate(patched_old) if 'assistant' in (e.get('triggerRange') or ['user'])
                and not title_of(e).startswith('世界自转')]
    base_msg = hud(era_date('纷争纪', 1192), '炮的年月·箭与冠的秤·二幕')
    for w in s_words:
        msg = base_msg + '营火边有人说起%s。' % w
        for i, e in asst_old:
            if fires(e, [('assistant', msg)], SYSP):
                reply_base[i] += 1
                reply_example.setdefault(i, w)

# ---------- 产物 ----------
os.makedirs(OUT, exist_ok=True)
new_card = copy.deepcopy(card)
new_card['prompt']['lorebook'] = patched_old + entries
out_card = os.path.join(OUT, OUT_NAME)
json.dump(new_card, open(out_card, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(entries, open(os.path.join(OUT, ENTRIES_NAME), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
back = json.load(open(out_card, encoding='utf-8'))
assert len(back['prompt']['lorebook']) == len(old) + len(entries)
assert back['prompt']['lorebook'][len(old):] == entries
for k in card:
    if k == 'introPage':
        # 介绍页：底卡原文照进卡补丁（REPS）换过，再照年表、命星档案、另两路的 INTRO_REPS 改，跟产物比
        exp_ = base_card[k]
        for o_, n_ in REPS:
            exp_ = exp_.replace(o_, n_)
        exp_, _ = intro_transform(exp_, [])
        assert back[k] == exp_, k
    elif k != 'prompt':
        assert back[k] == base_card[k], k
for k in card['prompt']:
    if k != 'lorebook':
        assert back['prompt'][k] == base_card['prompt'][k], k
# 底卡条目：改了哪几条
diff_old = [i for i, (a, b) in enumerate(zip(back['prompt']['lorebook'][:len(old)], base_card['prompt']['lorebook'])) if a != b]
real_prompt_bytes = len(json.dumps(back['prompt'], ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
real_lb_len = sum(len(e['content']) for e in back['prompt']['lorebook'])
card_mb = os.path.getsize(out_card) / 1e6

n_moon = sum(1 for e in entries if era_of[id(e)] == '月银纪')
n_strife = sum(1 for e in entries if era_of[id(e)] == '纷争纪')
lines = ['两纪条目 %d 条（月银纪 %d：第一到三批留下 %d，页上和补卷 %d；纷争纪 %d），底卡 %d 条，合计 %d 条，卡 %.1fMB' % (
    len(entries), n_moon, len(batch_entries), n_moon - len(batch_entries), n_strife, len(old), len(old) + len(entries), card_mb), '']
lines.append('卡上的账目栏照底卡没动：promptSizeBytes %d、lorebookLength %d；照实算是 promptSizeBytes %d、正文合计 %d 字' % (
    back['promptSizeBytes'], back['lorebookLength'], real_prompt_bytes, real_lb_len))
lines.append('')
fc = collections.Counter(e['folder'] for e in entries)
for k in sorted(fc):
    lines.append('%s %d 条 %d 字' % (k, fc[k], sum(len(e['content']) for e in entries if e['folder'] == k)))
lines.append('正文合计 %d 字' % sum(len(e['content']) for e in entries))
lines += ['', '优先级带（两纪共用，7550 到 8191，两条示范 8192）：'] + ['%s %d 到 %d（%d 条）' % (f, a, b, len(by_folder[f])) for f, (a, b) in BANDS.items()]
lines += ['', '源稿：页 %d 张，补卷 %d 份' % (len(PAGES), len(SUPPS))] + ['  ' + t for t in SUPP_TAGS]
lines += ['', '退掉的旧条目 %d 条：' % len(retired)] + ['%s｜%s' % r for r in retired]
lines += ['', '改名（次数）：'] + ['%s→%s ×%d' % (o, n, c) for (o, n), c in rename_log.most_common()]
lines += ['', '底卡改动：进卡补丁 %d 处，另两路的补丁 %d 条，旧条目加黑名单 %d 条，有改动的底卡条目 %d 条' % (
    len(REPS), len(ext_log), len(patch_lines), len(diff_old))] + ext_log + patch_lines + ['没读的补丁：' + x for x in ext_missing]
lines += ['', 'v8.1 时代钥匙（用户 10-21 定的两件，细则见 batch_edits_v8.py 末尾 v8.1 那一节）：'] + \
         ['  %s %d 条' % (k, c) for k, c in sorted(V81_COUNT.items())]
for cat in ['纷争纪46', '纷争纪47', '纷争纪51', '纷争纪49', '月银纪46', '月银纪51', '月银纪49', '月银纪47', '月银纪直醒']:
    if V81.get(cat):
        lines += ['', 'v8.1 · %s（%d 条）：' % (cat, len(V81[cat]))] + ['  ' + x for x in V81[cat]]
lines += ['', '改了的底卡条目：'] + ['#%d %s' % (i, title_of(back['prompt']['lorebook'][i])[:40]) for i in diff_old]
lines += ['', '介绍页改动：'] + intro_log
lines += ['', '年份窗（页上没写年份黑名单的，照这一段主线开局年到下一段开局年的前一年加一个）：%s' % dict(window_log)] + \
         ['%s %d 到 %s' % (p, win[p][0], win[p][1] if win[p][1] else '万兽期末') for p in WS if p in win]
lines += ['', '引用改了的：'] + ['%s → %s ×%d' % (o, n, c) for (o, n), c in cite_log.items()] + notes
lines += ['', '新钥匙：'] + ['%s = %s' % (k, v[0] if len(v) == 1 else v) for k, v in ALIASES.items()
                          if (k.startswith(('〔时段·', '〔主线·')) and k.endswith('·正则〕')) or k.startswith(('〔时段·诸国·', '〔主线·', '〔纷争纪'))]
lines += ['', '跨时段的命星：'] + gate_log
lines += ['', '纷争纪借来的星（脚本对出来的）：'] + ['%s（出处 %s）：%s' % (st, h, '、'.join(hs)) for (st, h), hs in auto_borrow.items()]
lines += ['', 'STAR_GATE 跟脚本对出来的差：'] + (borrow_diff or ['无'])
lines += ['', '模拟一·开局口令（世界自转那条不计）：'] + sim_lines
lines += ['', '模拟二·每段主线一条假回复（底座＋开局那一段），玩家说继续：'] + load_lines
lines += ['', '模拟三·串段（别页的名字在这一段的回复里出现）：'] + (cross_lines or ['无'])
lines += ['', '模拟四·跨纪漏检：'] + cross_era_lines
lines += ['', '模拟四之二·纷争纪的局里玩家打月银纪那四十条的地名（应当一条不醒）：'] + (place_lines or ['（--fast 没跑）' if FAST else '无'])
lines += ['', '模拟五·迷宫纪漏检：'] + maze_lines + total_lines
lines += ['', '模拟六·焚原实测回复：'] + moon_lines + panel_lines
lines += ['', '纷争纪中局会醒的底卡（二十一段一幕假回复加四句寻常话，次数）：'] + \
         ['#%d %s ×%d' % (i, title_of(full[i])[:30], c) for i, c in mid_old.most_common()]
lines += ['', '模拟七·纷争纪的回复里写到纷争纪条目的触发词（%d 个词，一词一条回复，底座纷争纪1192年），范围含助手的底卡醒了 %d 条：' % (n_words, len(reply_base))] + \
         ['#%d %s ×%d（比如「%s」）' % (i, title_of(full[i])[:30], c, reply_example[i]) for i, c in reply_base.most_common()] + \
         ['（加了纷争纪锚的那几条，带底座的回复先叫黑名单挡下，不在这张单子上）']
# 年份窗断成几截的：门控认的年份减去年份黑名单挡的，剩下的不连着（--fast 不跑）。多半是源稿黑名单漏写了一截；
# 49 命星别页借用的，窗本来就是几截，照设计
hole_lines = []
if not FAST:
    for e in entries:
        if e['triggerWordsType'] != 'AND':
            continue
        for era_ in ERA_MAX:
            gs_ = [re.compile(_body(w)) for w in e['triggerWords'] if is_rx(w) and (is_gate(w) or w in GATE_RX) and era_ in w]
            bs_ = [re.compile(_body(w)) for w in e['blackListWords'] if is_rx(w) and era_ in w and '年' in w]
            if not gs_ or not bs_:
                continue
            r_ = _ranges([y for y in range(1, ERA_MAX[era_] + 1) if any(g.search('<br>%s%d年' % (era_, y)) for g in gs_)
                          and not any(b.search('<br>%s%d年' % (era_, y)) for b in bs_)])
            if len(r_) > 1:
                hole_lines.append('%s｜%s｜%s%s' % (e['folder'], title_of(e)[:40], '、'.join('%d到%d' % ab if ab[0] != ab[1] else '%d' % ab[0] for ab in r_),
                                                   '（命星，别页借用，照设计）' if e['folder'][:2] == '49' else '（多半是黑名单漏了一截，源稿改）'))
lines += ['', '年份窗断成几截的（门控认的年份减去年份黑名单挡的）：'] + (hole_lines or ['（--fast 没跑）' if FAST else '无'])
# 跟 v8 比（同一个目录里 v8 的报告还在就比）
def _sim_rows(text, a, b):
    i = text.find(a); j = text.find(b, i + 1)
    rows = collections.OrderedDict()
    if i < 0:
        return rows
    for ln in text[i:j].split('\n'):
        m_ = re.match(r'^(〔.〕\S+)\s+(?:(\S+)年 )?(\d+) 条 (\d+) 字', ln)
        if m_:
            rows[m_.group(1) + (('@' + m_.group(2)) if m_.group(2) else '')] = (int(m_.group(3)), int(m_.group(4)))
    return rows
prev_path = os.path.join(OUT, PREV_REPORT)
cmp_lines = []
if os.path.exists(prev_path):
    prev_txt = open(prev_path, encoding='utf-8').read()
    cur_txt = '\n'.join(lines)
    for label, a_, b_ in (('开局口令', '模拟一', '模拟二'), ('口令加一幕回复', '模拟二', '模拟三')):
        pv, cu = _sim_rows(prev_txt, a_, b_), _sim_rows(cur_txt, a_, b_)
        for era_t in ('〔月〕', '〔纷〕'):
            ks = [k for k in cu if k.startswith(era_t) and k in pv]
            if not ks:
                continue
            d_ = [(cu[k][1] - pv[k][1], k) for k in ks]
            cmp_lines.append('%s%s %d 项：v8 醒 %d 到 %d 字（合计 %d），v8.1 醒 %d 到 %d 字（合计 %d），变了的 %d 项' % (
                label, era_t, len(ks), min(pv[k][1] for k in ks), max(pv[k][1] for k in ks), sum(pv[k][1] for k in ks),
                min(cu[k][1] for k in ks), max(cu[k][1] for k in ks), sum(cu[k][1] for k in ks), sum(1 for x, _ in d_ if x)))
            for x, k in sorted(d_)[:4] + sorted(d_)[-2:]:
                if x:
                    cmp_lines.append('    %s %+d 字（v8 %d 条 %d 字 → v8.1 %d 条 %d 字）' % (k, x, pv[k][0], pv[k][1], cu[k][0], cu[k][1]))
    # 串段：每段旅伴、命星条数和字数
    def _chuan(text):
        out_ = collections.OrderedDict()
        i_ = text.find('模拟三'); j_ = text.find('模拟四', i_ + 1)
        for ln in text[i_:j_].split('\n'):
            m_ = re.match(r'^(\S+?)（(\d+)年）：讲起前面 (\d+) 个人，醒了旧段的人物 (\d+)、旅伴 (\d+)、命星 (\d+)，共 (\d+) 字', ln)
            if m_:
                out_[m_.group(1)] = tuple(int(x) for x in m_.groups()[3:])
        return out_
    pc, cc = _chuan(prev_txt), _chuan(cur_txt)
    ch_ = [k for k in cc if k in pc and pc[k] != cc[k]]
    cmp_lines.append('串段 %d 段，变了的 %d 段%s' % (len([k for k in cc if k in pc]), len(ch_), '：' if ch_ else ''))
    for k in ch_:
        cmp_lines.append('    %s 人物%d 旅伴%d 命星%d %d字 → 人物%d 旅伴%d 命星%d %d字' % ((k,) + pc[k] + cc[k]))
    # 迷宫纪：玩家打两纪专名醒了直醒条目的行数
    def _maze(text):
        i_ = text.find('模拟五'); j_ = text.find('模拟六', i_ + 1)
        return [ln for ln in text[i_:j_].split('\n') if re.search(r'两纪条目 [1-9]', ln)]
    pm, cm = _maze(prev_txt), _maze(cur_txt)
    cmp_lines.append('迷宫纪漏检有醒的行：v8 %d 行，v8.1 %d 行' % (len(pm), len(cm)))
    for ln in pm:
        cmp_lines.append('    v8：' + ln[:120])
    # 纷争纪的局玩家打月银纪那二十二个词
    for ln in prev_txt.split('\n'):
        if ln.startswith('纷争纪的局玩家把这些词各打一个'):
            cmp_lines.append('纷争纪的局玩家打月银纪那二十二个词：v8 ' + ln.split('：', 1)[1])
    for ln in cross_era_lines:
        if ln.startswith('纷争纪的局玩家打这'):
            cmp_lines.append('    v8.1 ' + ln.split('：', 1)[1])
else:
    cmp_lines.append('同一个目录里找不到 %s，没比' % PREV_REPORT)
lines += ['', '跟 v8 比：'] + cmp_lines
lines += ['', '条目一览：']
for e in entries:
    src, op, era = meta_of[id(e)]
    lines.append('%-34s %s 优先级%d %s触发%d 黑名单%d %d字  %s' % (
        title_of(e)[:34], e['folder'][:2], e['priority'], '同时 ' if e['triggerWordsType'] == 'AND' else '直醒 ',
        len(e['triggerWords']), len(e['blackListWords']), len(e['content']), src))
lines += ['', '产物：' + OUT_NAME, '', '问题 %d 条：' % len(problems)] + problems
open(os.path.join(OUT, REPORT_NAME), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines[:40]))
print('...')
print('问题 %d 条' % len(problems))
for p in problems[:120]:
    print(' ', p)
