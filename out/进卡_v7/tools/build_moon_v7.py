# -*- coding: utf-8 -*-
"""月银纪 v7（2026-10-18）：底卡 rili_v7 + 第一到三批（退掉被替下的、照改名表换名）+ 十五页万兽史诗 + 六页诸国时段 + 六页萨尔维斯时段，
套成一张日里卡，校验，再一条一条消息地模拟触发。
用法：python -I -X utf8 build_moon_v7.py <aldran 根目录> <工作目录> <输出目录>
沿用 build_moon_b1.py（v5）的口径：一条消息一条消息分开算，AND 和黑名单都跨不了消息，纯词分大小写，正则不许量词套量词、
整条不超过 25 个量词。页上的条目设置照抄成触发词，钥匙别名在这里展开。"""
import json, re, sys, os, glob, copy, runpy, collections

ROOT, WDIR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src', 'rili_v7.json')
PATCH = os.path.join(WDIR, '诸国期', '进卡补丁_rili_v7.py')
ED = runpy.run_path(os.path.join(HERE, 'batch_edits.py'))
OUT_NAME = '奥尔德兰_日里版_月银纪全卷_测试v7.json'

SONGS = ['第一歌_灰桥初火', '第二歌_镜中石瞳', '第三歌_鸦栖之石', '第四歌_雷纹豹裘', '第五歌_冰矛抵眉', '第六歌_九步冷泉',
         '第七歌_焚原断刃', '第八歌_未磨白骨', '第九歌_落日之弓', '第十歌_千鼓空角', '第十一歌_天马落羽', '第十二歌_珠湾沉冠',
         '第十三歌_不空的水囊', '第十四歌_藏命之匣', '第十五歌_日冕之晨']
ZHUGUO = ['诸国期时段_一_晨祷', '诸国期时段_二_午祷上', '诸国期时段_三_午祷下', '诸国期时段_四_晚祷上',
          '诸国期时段_五_晚祷下', '诸国期时段_六_夜祷']
SALVIS = ['萨尔维斯时段_一_崛起上', '萨尔维斯时段_二_崛起下', '萨尔维斯时段_三_帝国', '萨尔维斯时段_四_魔族之世',
          '萨尔维斯时段_五_末年上', '萨尔维斯时段_六_末年下']
PAGES = [(s, os.path.join(WDIR, '月银纪史诗', s + '.md')) for s in SONGS] + \
        [(z, os.path.join(WDIR, '诸国期', z + '.md')) for z in ZHUGUO] + \
        [(v, os.path.join(WDIR, '萨尔维斯', v + '.md')) for v in SALVIS]
# 灯里那一句照原话，两个感叹号留着，只许在这一句里
LAST_WORDS = '看啊，我的功业已成！欢呼吧，世界将因我而不再燃烧！'
problems, notes = [], []

# ---------- 钥匙别名 ----------
ERA_ANCHOR = lambda era: ['日期</b><br>' + era, 'hud-meta">' + era, '纪元：' + era]
YEAR = '(?:<br>|hud-meta">|纪元：)月银纪'
ALIASES = {
    '〔月银纪〕': ERA_ANCHOR('月银纪'),
    '〔别纪〕': ERA_ANCHOR('迷宫纪') + ERA_ANCHOR('纷争纪') + ERA_ANCHOR('山铜纪'),
    '〔月银纪·正则〕': ['/日期<\\/b><br>月银纪|hud-meta">月银纪|纪元：月银纪/'],
    '〔迷宫纪凭证〕': ['/^(?![\\s\\S]*纪元：月银纪)[\\s\\S]*命途已确认/'],
    # 祭火期 1 到 1000 年，万兽期 1001 到 3000 年；潮汐格、摘要行、凭证里的时段也认
    '〔时段·祭火·正则〕': ['/潮汐<\\/b><br>祭火| · 祭火·|开局时段：祭火|%s(?:\\d{1,3}|1000)年/' % YEAR],
    '〔时段·万兽·正则〕': ['/潮汐<\\/b><br>万兽| · 万兽·|开局时段：万兽|%s(?:100[1-9]|10[1-9]\\d|1[1-9]\\d\\d|2\\d\\d\\d|3000)年/' % YEAR],
}
for p in ['祭火', '万兽', '诸国', '崛起', '帝国', '魔族之世', '末年']:
    ALIASES['〔时段·%s〕' % p] = ['潮汐</b><br>' + p, ' · %s·' % p, '开局时段：' + p]
# 诸国四把时段钥匙照页上「打包脚本里要加，写成一条正则」那一句取
for tag, path in PAGES:
    for m in re.finditer(r'〔(时段·(?:诸国·[^〕]+|[^〕]+·正则))〕打包脚本里要加，写成一条正则 `(/[^`]+/)`', open(path, encoding='utf-8').read()):
        ALIASES['〔%s〕' % m.group(1)] = [m.group(2)]
for k in ['诸国·晨祷', '诸国·午祷', '诸国·晚祷', '诸国·夜祷', '崛起·正则', '帝国·正则', '魔族之世·正则', '末年·正则']:
    if '〔时段·%s〕' % k not in ALIASES:
        raise SystemExit('页上找不到〔时段·%s〕的正则' % k)
GATE_RX = set(v[0] for k, v in ALIASES.items() if k.endswith('·正则〕') or k.startswith('〔时段·诸国·'))

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

def regex_problems(w):
    body, flags = w[1:w.rfind('/')], w[w.rfind('/') + 1:]
    p_ = []
    if set(flags) - set('imsg'): p_.append('flags')
    try: re.compile(body)
    except re.error as ex: p_.append('编译失败 %s' % ex)
    if quant_count(body) > 25: p_.append('量词 %d>25' % quant_count(body))
    if star_height(body) > 1: p_.append('量词套量词')
    if re.search(r'\(\?P?<[A-Za-z]', body): p_.append('命名组没测过')
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

# ---------- 底卡 + 进卡补丁 ----------
raw = open(SRC, encoding='utf-8').read()
REPS = runpy.run_path(PATCH)['REPS']
for o, n in REPS:
    if raw.count(o) != 1:
        raise SystemExit('进卡补丁对不上底卡：%r 出现 %d 次' % (o, raw.count(o)))
for o, n in REPS:
    raw = raw.replace(o, n)
card = json.loads(raw)
base_card = json.load(open(SRC, encoding='utf-8'))
old = card['prompt']['lorebook']
title_of = lambda e: e['content'].strip().split('\n')[0].lstrip('# ').strip()
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
    batch_entries.append(e)

# ---------- 页 ----------
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
    m = re.search(r'文件夹 ?(\d\d·月银纪｜[^，（]+)', s)
    m2 = SET_RX.search(s)
    if not m or not m2:
        problems.append('%s 条目设置读不出：%s' % (where, s[:60]))
        return None
    need = {}
    return {'folder': m.group(1), 'and': bool(m2.group(1)), 'trig': page_tokens(m2.group(2), where, need),
            'bl': page_tokens(m2.group(3), where), 'range': RANGES[m2.group(4).strip()], 'depth': int(m2.group(5)),
            'need': need}

def parse_page(tag, path):
    lines = open(path, encoding='utf-8').read().split('\n')
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
for tag, path in PAGES:
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
    ABIL_STARS[tag] = set(holder_map)
    page_items += its

# 和底卡撞了标题的（守望长律这一类，底卡里是后世的那一门），名字后面加（月银纪）
for it in page_items:
    if it['title'] in old_titles:
        if it['kind'] == 'star':
            it['title'] = it['title'].replace(it['star'], it['star'] + '（月银纪）', 1)
        else:
            it['title'] += '（月银纪）'
        notes.append('和底卡同名，标题加了（月银纪）：' + it['title'])

# 同名标题加页名区分（这一段旅伴之间这一类）
cnt = collections.Counter(it['title'] for it in page_items)
for it in page_items:
    if cnt[it['title']] > 1:
        short = it['page'].split('_')[-1]
        it['title'] = '%s｜%s' % (it['title'], short)

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
    if s['folder'].startswith('51'):
        # 传奇条不叫开局口令叫醒（镜中石瞳开局那一句会把狄昂的传奇条叫进来，他这时候还没成名）
        bl.append('/开局时段：/')
    e = mk(it['title'], body_text(it['body']), s['folder'], dedupe(trig), 'AND' if s['and'] else 'OR', dedupe(bl),
           s['range'], s['depth'])
    e['_src'] = it['page']
    e['_page'], e['_star'], e['_holders'] = it['page'], it.get('star'), it.get('holders', [])
    return e

page_entries = [page_entry(it) for it in page_items if it.get('setting')]

# 跨时段的命星（各页命星一节条目设置后头写的）：换门控、或者再挂一把时段钥匙、或者星名后头添几个词
def _body(w):
    return w[1:w.rfind('/')]
STAR_GATE = ED.get('STAR_GATE', {})
gate_log = []
for e in page_entries:
    st = e.get('_star')
    if not st or st not in STAR_GATE:
        continue
    rule = STAR_GATE[st]
    gi = [i for i, w in enumerate(e['triggerWords']) if w in GATE_RX]
    if len(gi) != 1:
        problems.append('命星「%s」找不到唯一的门控钥匙' % st); continue
    g = e['triggerWords'][gi[0]]
    if rule.get('gate'):
        g = alias(rule['gate'])[0]
    for extra in rule.get('also', []):
        g = '/' + _body(g) + '|' + _body(alias(extra)[0]) + '/'
        GATE_RX.add(g)
    e['triggerWords'][gi[0]] = g
    if rule.get('names'):
        ni = [i for i, w in enumerate(e['triggerWords']) if i != gi[0] and is_rx(w)]
        w = e['triggerWords'][ni[0]]
        e['triggerWords'][ni[0]] = w[:w.rfind('/')] + '|' + '|'.join(re.escape(x) for x in rule['names']) + w[w.rfind('/'):]
    if rule.get('copy_bl_from'):
        src_ = [x for x in page_entries if title_of(x).startswith('旅途同行：%s（' % rule['copy_bl_from'])]
        if src_:
            e['blackListWords'] += [w for w in src_[0]['blackListWords'] if '月银纪' in w and '年' in w and w not in e['blackListWords']]
        else:
            problems.append('命星「%s」要照的旅伴条找不到：%s' % (st, rule['copy_bl_from']))
    e['_gate_fixed'] = True
    gate_log.append('%s：%s' % (st, '、'.join(x for x in [('换成' + rule['gate']) if rule.get('gate') else '',
                                                         ('再挂' + '、'.join(rule.get('also', []))) if rule.get('also') else '',
                                                         ('添' + '、'.join(rule['names'])) if rule.get('names') else '',
                                                         ('照%s的年份黑名单' % rule['copy_bl_from']) if rule.get('copy_bl_from') else ''] if x)))
for st in STAR_GATE:
    if not any(e.get('_star') == st for e in page_entries):
        problems.append('跨时段的命星找不到：' + st)

# ---------- 年份窗：万兽各段的人物、旅伴、命星只在自己那一段的年份里醒 ----------
# 〔时段·万兽·正则〕横跨 1001 到 3000 年，后面的段讲起前面段里的人，前面那一段的旅伴条和命星会整套醒过来。
# 页上没写年份黑名单的，照这一段主线的开局年到下一段开局年的前一年给一个；命星被后面哪一段的旅伴能力里点了名，
# 那一段的年份也放开。诸国各段已经按时段钥匙分开，旅伴条都写了年份黑名单，命星照持有人那一条的黑名单。
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
    y = re.search(r'月银纪(\d+)年', c) or re.search(r'(?<!\d)(\d{3,5})年', op)
    return int(y.group(1)) if y else None

for allowed in ([(1020, 1099)], [(2950, 2999), (3000, None)], [(1690, 1720), (2393, 2498)], [(7, 7)]):
    rx_ = outside_rx(allowed)
    body_ = rx_[1:rx_.rfind('/')]
    for y_ in list(range(1, 3200)) + [5000, 9999, 10081, 12345]:
        inside = any(a <= y_ <= (b if b is not None else 99999) for a, b in allowed)
        if bool(re.search(body_, '<br>月银纪%d年·秋' % y_)) == inside:
            raise SystemExit('年份窗正则算错了：%s %d' % (allowed, y_))
has_year_bl = lambda e: any('月银纪' in w and '年' in w and is_rx(w) for w in e['blackListWords'])
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
for e in page_entries:
    if e['folder'][:2] != '49' or e['_page'] not in ZHUGUO + SALVIS or has_year_bl(e) or e.get('_gate_fixed'):
        continue
    if any(e['_star'] in ABIL_STARS.get(q, set()) for q in ZHUGUO + SALVIS if q != e['_page']):
        continue
    owners = [x for x in page_entries if x['_page'] == e['_page'] and
              any(title_of(x).startswith('旅途同行：%s（' % h) for h in e['_holders'])]
    bls = set(tuple(w for w in x['blackListWords'] if '月银纪' in w and '年' in w) for x in owners)
    if len(owners) >= 1 and len(bls) == 1 and list(bls)[0]:
        e['blackListWords'] += list(list(bls)[0])
        window_log['49诸国'] += 1
for e in page_entries:
    for k in ('_page', '_star', '_holders', '_gate_fixed'):
        e.pop(k, None)

# 引用跟着改了的标题走
cite_map = dict(ED['CITE'])
for it in batch_items:
    if it['old_title'] != it['title']:
        cite_map['「%s」' % it['old_title']] = '「%s」' % it['title']
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

# ---------- 优先级：月银纪一块排在底卡后面，文件夹一段一段排，同文件夹里先旧后新，挤不下的并列 ----------
BANDS = {'40': (7550, 7569), '41': (7570, 7609), '42': (7610, 7619), '43': (7620, 7669), '44': (7670, 7689),
         '45': (7690, 7729), '46': (7730, 7849), '47': (7850, 8029), '48': (8030, 8049), '49': (8050, 8129),
         '50': (8130, 8159), '51': (8160, 8191)}
entries = []
by_folder = collections.defaultdict(list)
for e in sorted(batch_entries, key=lambda x: x['_oldpri']) + page_entries:
    if title_of(e) == '月银纪·示范':
        continue
    by_folder[e['folder'][:2]].append(e)
for fd in sorted(by_folder):
    if fd not in BANDS:
        problems.append('没有给文件夹 %s 排优先级' % fd); continue
    a, b = BANDS[fd]
    es = by_folder[fd]
    span = b - a + 1
    for i, e in enumerate(es):
        e['priority'] = a + (i if len(es) <= span else i * span // len(es))
    entries += es
demo = [e for e in batch_entries if title_of(e) == '月银纪·示范'][0]
demo['priority'] = 8192
entries.append(demo)
meta_of = {id(e): (e.pop('_src', ''), e.pop('_oldpri', None)) for e in entries}

# ---------- 校验 ----------
titles = [title_of(e) for e in entries]
for t, c in collections.Counter(titles).items():
    if c > 1:
        problems.append('标题重复：%s ×%d' % (t, c))
haystack = SYSP + '\n'.join(e['content'] for e in old)
all_titles = set(titles) | old_titles
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
    if e['triggerWordsType'] == 'AND' and not any(w in GATE_RX for w in e['triggerWords']):
        problems.append(t + ' 同时满足里没有纪元或时段的门控')
    if not (0 <= e['priority'] <= 8192):
        problems.append(t + ' 优先级越界')
    c = e['content']
    for bad in ['——', '—', '；', '…', '！', '★', '（#']:
        if bad == '！' and c.count('！') == c.count(LAST_WORDS) * 2:
            continue
        if bad in c:
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

# 门控钥匙不能在底卡里中
for w in sorted(GATE_RX):
    body = w[1:w.rfind('/')]
    if re.search(body, haystack):
        problems.append('门控正则在底卡里能中：' + w[:60])
for w in ALIASES['〔月银纪〕']:
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

# ---------- 旧条目：开局口令会叫醒的那几条加〔月银纪〕黑名单（v5 的十三条，再加这一轮新口令叫醒的） ----------
def _match(w, t):
    if is_rx(w):
        if regex_problems(w):
            return False
        body, flags = w[1:w.rfind('/')], w[w.rfind('/') + 1:]
        f = (re.I if 'i' in flags else 0) | (re.M if 'm' in flags else 0) | (re.S if 's' in flags else 0)
        return re.search(body, t, f) is not None
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

MAINLINES = []
for e in entries:
    m = re.match(r'^月银纪·主线｜(.+)$', title_of(e))
    if m:
        MAINLINES.append(m.group(1))
OPENINGS = [(m, '纪元：月银纪｜开局时段：' + m) for m in MAINLINES]
OPENINGS.append(('万兽·焚原', '纪元：月银纪｜开局时段：万兽·焚原｜出身：黄金裔'))
OLD_PATCH = {14: '月银纪：详细正史', 29: '月银纪·各族发展史', 33: '精灵详史·月银纪', 34: '矮人详史·月银纪',
             35: '半身人详史·月银纪', 36: '兽耳族详史·月银纪', 37: '龙裔详史·月银纪', 38: '魔族详史·月银纪',
             39: '圣堂详史·月银纪', 43: '真龙详史·月银纪', 44: '月银纪·各族传奇与英雄名录',
             157: '神域之路·其一', 485: '魔族七大类'}
for i, prefix in OLD_PATCH.items():
    if not title_of(old[i]).startswith(prefix):
        raise SystemExit('旧条目 #%d 对不上：%s' % (i, title_of(old[i])))
extra_patch = {}
for m, u in OPENINGS:
    for i, e in enumerate(old):
        if i in OLD_PATCH or title_of(e).startswith('世界自转'):
            continue
        if fires(e, [('user', u)], SYSP):
            extra_patch[i] = title_of(e)
patched_old = copy.deepcopy(old)
patch_lines = []
for i in sorted(set(OLD_PATCH) | set(extra_patch)):
    e = patched_old[i]
    # 只扫用户，或者深度 1（只看玩家这一条）的，加了黑名单只挡带「纪元：月银纪」这类字的那一句，迷宫纪的局不受影响
    if e.get('triggerRange') != ['user'] and e.get('scanDepth') != 1:
        problems.append('旧条目 #%d %s 不是只扫用户，黑名单的效果要另算' % (i, title_of(e)[:20]))
        continue
    if e.get('blackListWords') and e.get('blackListWordsType') != 'OR':
        raise SystemExit('旧条目 #%d 原有黑名单是 AND，不能直接追加' % i)
    bl = list(e.get('blackListWords') or [])
    added = [w for w in ALIASES['〔月银纪〕'] if w not in bl]
    e['blackListWords'] = bl + added
    e['blackListWordsType'] = 'OR'
    if len(e['blackListWords']) > 20:
        problems.append('旧条目 #%d 黑名单超过 20 个' % i)
    patch_lines.append('旧 #%d %s  黑名单 +%d%s' % (i, title_of(e)[:30], len(added), '（这一轮新加）' if i in extra_patch else ''))

full = patched_old + entries
N_OLD = len(old)
short = lambda t: t.replace('月银纪·', '')

def run(msgs, sysp=SYSP):
    got = [i for i, e in enumerate(full) if fires(e, msgs, sysp)]
    news = [i for i in got if i >= N_OLD]
    olds = [i for i in got if i < N_OLD and not title_of(full[i]).startswith('世界自转')]
    return news, olds

def fmt(news):
    return '%d 条 %d 字｜%s' % (len(news), sum(len(full[i]['content']) for i in news), '、'.join(short(title_of(full[i])) for i in news))

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
sim_lines = []
for m, u in OPENINGS:
    news, olds = run([('user', u)])
    names = [title_of(full[i]) for i in news]
    sim_lines.append('%-16s %s' % (m + ('＋黄金裔' if '黄金裔' in u else ''), fmt(news)))
    if olds:
        problems.append('开局口令「%s」还会叫醒旧条目 %s' % (u, olds))
    need = ['月银纪·常驻｜这一局在月银纪', '月银纪·示范', '月银纪·主线｜' + m]
    pk = period_of(m) if m.startswith(('诸国·', '崛起·', '帝国·', '魔族之世·', '末年·')) else None
    if pk:
        need.append(PERIOD_TITLE.get(pk, '月银纪·时段｜' + pk))
    for n_ in need:
        if n_ not in names:
            problems.append('开局口令「%s」没叫醒「%s」' % (m, n_))

# ---------- 模拟二：每一页一条假回复（底座日期＋潮汐＋主线开局那一段），看醒多少 ----------
def hud(year_rest, tide, place='某地'):
    return ('<details class="arc-hud-details"><summary class="arc-hud-summary"><div class="hud-summary-inner">'
            '<span class="hud-title-icon">✦</span><b>推演底座</b><span class="hud-meta">月银纪%s · 09:20 · %s · %s · 防抢话 开</span>'
            '</div></summary><div class="detail-body arc-hud-body"><div class="hud-grid"><div><b>日期</b><br>月银纪%s</div>'
            '<div><b>地点</b><br>%s</div><div><b>潮汐</b><br>%s</div></div>'
            '<div class="f path"><b>命路</b>命路未定｜职业 未认兵(Common)｜命星 未觉醒</div>'
            '<div class="f job"><b>职业</b>未认兵·Ⅰ｜职业 未就职</div></div></details>\n\n' % (year_rest, place, tide, year_rest, place, tide))

ML_INFO = {}
for e in entries:
    m = re.match(r'^月银纪·主线｜(.+)$', title_of(e))
    if not m:
        continue
    c = e['content']
    op = re.search(r'(?m)^开局：(.*)$', c)
    op = op.group(1) if op else c.split('\n')[2][:300]
    y = re.search(r'月银纪(\d+)年', c) or re.search(r'(?<!\d)(\d{3,5})年', op)
    ML_INFO[m.group(1)] = (int(y.group(1)) if y else None, op)
load_lines = []
for ml, (yr, op) in ML_INFO.items():
    if yr is None:
        load_lines.append('%s：主线里找不到年份' % ml); continue
    msg = hud('%d年·秋·坠叶月·上旬三日' % yr, ml + '·一幕') + op
    news, olds = run([('user', '纪元：月银纪｜开局时段：' + ml), ('assistant', msg), ('user', '继续')])
    load_lines.append('%-16s %d年 %s' % (ml, yr, fmt(news)))
    if olds:
        load_lines.append('    旧条目 %d 条：%s' % (len(olds), '、'.join('#%d %s' % (i, title_of(full[i])[:14]) for i in olds)))

# ---------- 模拟三：串段。一页的旅伴、人物、命星，在别的时段的回复里被点名，醒不醒 ----------
PAGE_YEAR = {}
for tag, _ in PAGES:
    for e, it in zip(page_entries, [x for x in page_items if x.get('setting')]):
        pass
page_of = {}
for e, it in zip(page_entries, [x for x in page_items if x.get('setting')]):
    page_of[id(e)] = it['page']
page_ml = collections.defaultdict(list)
for e in page_entries:
    m = re.match(r'^月银纪·主线｜(.+)$', title_of(e))
    if m:
        page_ml[page_of[id(e)]].append(m.group(1))
cross_lines = []
names_by_page = collections.defaultdict(list)
for e in page_entries:
    t = title_of(e)
    m = re.match(r'^旅途同行：(.+?)（', t)
    if m:
        names_by_page[page_of[id(e)]].append(m.group(1).split('·')[0])
page_order = [t for t, _ in PAGES]
for tag, _ in PAGES:
    mls = page_ml.get(tag, [])
    if not mls or ML_INFO.get(mls[0], (None,))[0] is None:
        continue
    yr = ML_INFO[mls[0]][0]
    # 后面的段讲起前面段里的人（一次讲一个人，一条回复）
    earlier = [(p, n) for p in page_order[:page_order.index(tag)] for n in names_by_page.get(p, [])]
    per_fd, chars, worst = collections.Counter(), 0, []
    for p, n in earlier:
        msg = hud('%d年·秋·坠叶月·上旬三日' % yr, mls[0] + '·二幕') + '火边有人说起%s当年的事。' % n
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
        cross_lines.append('%s（%d年）：讲起前面 %d 个人，醒了旧段的人物 %d、旅伴 %d、命星 %d，共 %d 字｜最多的：%s' % (
            tag, yr, len(earlier), per_fd['46'], per_fd['47'], per_fd['49'], chars,
            '、'.join('%s %d条%d字' % (n, k, c_) for c_, n, k in worst[:4])))

# ---------- 模拟四：迷宫纪的局，月银纪条目一条都不该醒 ----------
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
    maze_lines.append('%s：月银纪条目 %d 条%s%s' % (tag, len(news), ('｜' + '、'.join(title_of(full[i]) for i in news)) if news else '',
                                              '' if strict else '（玩家在迷宫纪里打月银纪才有的专名，直醒条目会醒，v5 起就是这样定的，只记不算）'))
    if strict:
        for i in news:
            problems.append('迷宫纪的局漏进月银纪条目（%s）：%s' % (tag, title_of(full[i])))
MAZE_CMD = '纪元：迷宫纪｜开局时段：默认时段｜出身：人类'
maze_real = read_sample('reply_迷宫纪首轮_人类.html')
for k, cred in MAZE_CREDS.items():
    maze_check('迷宫纪首轮·' + k, [('user', cred)])
maze_check('迷宫纪实测首轮·口令', [('user', MAZE_CMD)])
NEW_NAMES = []
for e in page_entries:
    t = title_of(e)
    m = re.match(r'^旅途同行：(.+?)（', t) or re.match(r'^(.+?)（人物）', t) or re.match(r'^灾祸之兽｜(.+)$', t) \
        or re.match(r'^凡世至强：(.+?)（', t) or re.match(r'^(.+?) \((?:Special|Passive|Art|Ability) \|', t)
    if m:
        NEW_NAMES.append(m.group(1))
for u in ['我想去神殿拜一拜七神', '去公会揭一张魔兽的悬赏，顺便问问报酬', '找个同伴一起走，最好是会治伤的', '我要自立为王，建一座城',
          '这附近有没有火山或者雪原', '拜师学剑，再去问问就职和转职', '找个诗人打听打听名号', '去协会问问大魔导收不收学徒',
          '我想去神坛前许个愿', '找钱商行换点钱', '去王道上走走', '河谷里的采石场还招人吗']:
    maze_check('迷宫纪中局·玩家「%s」' % u[:16], [('user', MAZE_CMD), ('assistant', maze_real), ('user', u)])
for n in NEW_NAMES[::9]:
    maze_check('迷宫纪中局·玩家「我想打听%s的事」' % n[:12], [('user', MAZE_CMD), ('assistant', maze_real), ('user', '我想打听%s的事' % n)], strict=False)
maze_check('迷宫纪·回复里把新名字全提一遍', [('user', MAZE_CMD), ('assistant', MAZE_REPLY + '、'.join(NEW_NAMES))])
maze_check('迷宫纪·玩家把新名字全打一遍', [('user', MAZE_CMD), ('assistant', maze_real), ('user', '、'.join(NEW_NAMES))], strict=False)

# ---------- 模拟五：v5 的焚原实测回复，再往下推一轮 ----------
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
PANEL_ONLY = hud('1690年·秋·坠叶月·上旬三日', '万兽·焚原·一幕')
news, _ = run([('assistant', PANEL_ONLY)])
panel_line = '只有面板的一条回复（焚原一幕）：' + fmt(news)

# ---------- 产物 ----------
os.makedirs(OUT, exist_ok=True)
new_card = copy.deepcopy(card)
new_card['prompt']['lorebook'] = patched_old + entries
out_card = os.path.join(OUT, OUT_NAME)
json.dump(new_card, open(out_card, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(entries, open(os.path.join(OUT, 'moon_v7_entries.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
back = json.load(open(out_card, encoding='utf-8'))
assert len(back['prompt']['lorebook']) == len(old) + len(entries)
assert back['prompt']['lorebook'][len(old):] == entries
for k in card:
    if k == 'introPage':
        # 介绍页的开局赐物表里有当铺重剑的一行描述，补丁里那一处当铺伙计就在这里
        assert back[k] == base_card[k].replace('当铺伙计当年亲手加钉', '当铺帮工当年亲手加钉'), k
    elif k != 'prompt':
        assert back[k] == base_card[k], k
for k in card['prompt']:
    if k != 'lorebook':
        assert back['prompt'][k] == base_card['prompt'][k], k
# 底卡条目：除了补丁那几处和加的黑名单，逐字不变
diff_old = [i for i, (a, b) in enumerate(zip(back['prompt']['lorebook'][:len(old)], base_card['prompt']['lorebook'])) if a != b]

lines = ['月银纪条目 %d 条（第一到三批留下 %d 条，页上新起 %d 条），底卡 %d 条，合计 %d 条' % (
    len(entries), len(batch_entries), len(page_entries), len(old), len(old) + len(entries)), '']
fc = collections.Counter(e['folder'] for e in entries)
for k in sorted(fc):
    lines.append('%s %d 条 %d 字' % (k, fc[k], sum(len(e['content']) for e in entries if e['folder'] == k)))
lines.append('正文合计 %d 字' % sum(len(e['content']) for e in entries))
lines += ['', '退掉的旧条目 %d 条：' % len(retired)] + ['%s｜%s' % r for r in retired]
lines += ['', '改名（次数）：'] + ['%s→%s ×%d' % (o, n, c) for (o, n), c in rename_log.most_common()]
lines += ['', '底卡改动：进卡补丁 %d 处，旧条目加黑名单 %d 条，有改动的底卡条目 %d 条' % (len(REPS), len(patch_lines), len(diff_old))] + patch_lines
lines += ['', '年份窗（页上没写年份黑名单的，照这一段主线开局年到下一段开局年的前一年加一个）：%s' % dict(window_log)] + \
         ['%s %d 到 %s' % (p, win[p][0], win[p][1] if win[p][1] else '万兽期末') for p in WS if p in win]
lines += ['', '引用改了的：'] + ['%s → %s ×%d' % (o, n, c) for (o, n), c in cite_log.items()] + notes
lines += ['', '新钥匙：'] +['%s = %s' % (k, v[0] if len(v) == 1 else v) for k, v in ALIASES.items()
                          if k.startswith(('〔时段·', '〔主线·')) and k.endswith(('·正则〕',)) or k.startswith(('〔时段·诸国·', '〔主线·'))]
lines += ['', '跨时段的命星：'] + gate_log
lines += ['', '模拟一·开局口令（世界自转那条不计）：'] + sim_lines
lines += ['', '模拟二·每段主线一条假回复（底座＋开局那一段），玩家说继续：'] + load_lines
lines += ['', '模拟三·串段（别页的名字在这一段的回复里出现）：'] + (cross_lines or ['无'])
lines += ['', '模拟四·迷宫纪漏检：'] + maze_lines
lines += ['', '模拟五·焚原实测回复：'] + moon_lines + [panel_line]
lines += ['', '条目一览：']
for e in entries:
    src, op = meta_of[id(e)]
    lines.append('%-34s %s 优先级%d %s触发%d 黑名单%d %d字  %s' % (
        title_of(e)[:34], e['folder'][:2], e['priority'], '同时 ' if e['triggerWordsType'] == 'AND' else '直醒 ',
        len(e['triggerWords']), len(e['blackListWords']), len(e['content']), src))
lines += ['', '产物：' + OUT_NAME, '', '问题 %d 条：' % len(problems)] + problems
open(os.path.join(OUT, 'moon_v7_report.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines[:60]))
print('...')
print('问题 %d 条' % len(problems))
for p in problems[:80]:
    print(' ', p)
