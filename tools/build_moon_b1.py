# -*- coding: utf-8 -*-
"""月银纪第一批：把 moon/batch1/g*.md 里手写的条目套进 rili_v7 的副本（只加不改），并校验。
用法：python3 -I tools/build_moon_b1.py <repo根目录>
产物：out/moon_b1_entries.json、out/奥尔德兰_日里版_月银纪第一批_测试v2.json、out/moon_b1_report.txt
（文档分页用的 markdown 由 tools/moon_b1_docmd.py 另外生成）
v2（2026-10-13 开局测试后）：旧卡十三条会被开局口令叫醒的条目加〔月银纪〕黑名单，并模拟八条开局口令的第一轮。
v3（2026-10-13 晚，月银纪卷第十一、十二节定稿后）：条目改写、新写钱与兑和神性与圣土，模拟多一条黄金裔开局。
v3.1（2026-10-13 夜，探针三之后）：日里一条消息一条消息分开算（AND、黑名单都跨不了消息）。泛词条目改成
「〔月银纪·正则〕＋话题正则」同时满足；只在月银纪才有的专名条目直醒，黑名单挡别纪底座和迷宫纪建档凭证。
模拟改成按条算，深度 0 当三条；纯词分大小写；加正则体检；加月银纪第二轮和迷宫纪两头的漏检。
v3.2（2026-10-13 夜，用户实测两局之后）：面板上的「未认兵」会叫醒兵器那一条，认兵前面加「未」的守卫；常驻里黄金裔那段
点明身份格、输入格、记忆不写降临者，天生的 Passive 和 Special 命星二选一。模拟加两条实测回复（月银纪黄金裔、迷宫纪人类）。
v3.3（2026-10-13 深夜，用户说还串着中式古风和玄幻味）：钱格改记金币、银币、铜币（不用锭、两、文），张榜揭榜改悬赏，学宫改学院，
客栈改旅店，兵器条去掉炼体、破境、排辈分一类说法（炼体改饮血），常驻加一段西方上古和中世纪的日子，示范加一段兽市。
v4（2026-10-14，第二批「城与地点」）：加读 moon/batch2/*.md，城邦十三条、地点若干；焚原的触发去掉三座城名（归青麦三城）；
模拟加城邦与地点的叫醒检查和迷宫纪的泛词漏检。
v5（2026-10-14，第三批「人」）：加读 moon/batch3/*.md，人物四十四条、旅伴九条、势力十五条；直醒条目的名字查旧卡；
模拟加人物与势力的叫醒检查、迷宫纪里找帮手问行会的漏检。
"""
import json, re, sys, os, glob, copy

ROOT = sys.argv[1]
SRC = os.path.join(ROOT, 'src', 'rili_v7.json')
OUT = os.path.join(ROOT, 'out')

# ---------- 门控钥匙（纯词，挂在推演底座的格子上） ----------
ERA_ANCHOR = lambda era: ['日期</b><br>' + era, 'hud-meta">' + era, '纪元：' + era]
ALIASES = {
    '〔月银纪〕': ERA_ANCHOR('月银纪'),
    '〔别纪〕': ERA_ANCHOR('迷宫纪') + ERA_ANCHOR('纷争纪') + ERA_ANCHOR('山铜纪'),
    # 同时满足用：三把钥匙并成一个正则（和话题词在同一条消息里才算，首轮凭证或每轮回复）
    '〔月银纪·正则〕': ['/日期<\\/b><br>月银纪|hud-meta">月银纪|纪元：月银纪/'],
    # 黑名单用：迷宫纪的建档凭证（开头是「命途已确认」，里面没写「纪元：月银纪」）
    '〔迷宫纪凭证〕': ['/^(?![\\s\\S]*纪元：月银纪)[\\s\\S]*命途已确认/'],
}
PERIODS = ['祭火', '万兽', '诸国', '崛起', '帝国', '魔族之世', '末年']
for p in PERIODS:
    ALIASES['〔时段·%s〕' % p] = ['潮汐</b><br>' + p, ' · %s·' % p, '开局时段：' + p]
MAINLINES = ['祭火·第一堆火', '万兽·焚原', '诸国·三川会盟', '崛起·环山北口', '崛起·金冕城之门',
             '帝国·天上的宴席', '魔族之世·薇丝拉之路', '末年·登神术前夜']
for m in MAINLINES:
    ALIASES['〔主线·%s〕' % m] = [m + '·', '开局时段：' + m]

def expand(spec):
    spec = spec.strip()
    if spec in ('', '无'):
        return []
    out = []
    for tok in re.findall(r'〔[^〕]+〕|[^、〔〕]+', spec):
        tok = tok.strip().strip('、')
        if not tok:
            continue
        if tok.startswith('〔'):
            if tok not in ALIASES:
                raise SystemExit('未知钥匙别名 ' + tok)
            out += ALIASES[tok]
        else:
            out.append(tok)
    seen, res = set(), []
    for w in out:
        if w not in seen:
            seen.add(w); res.append(w)
    return res

# ---------- 读手写条目 ----------
def parse_file(path):
    text = open(path, encoding='utf-8').read()
    blocks = re.split(r'^=== ', text, flags=re.M)[1:]
    items = []
    for b in blocks:
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
    """给卡内模型的正文：去掉作者批注（★、#条目号），段落之间单换行。"""
    t = AUTHOR_MARK.sub('', body)
    t = t.replace('★', '')
    paras = [p.strip() for p in re.split(r'\n\s*\n', t) if p.strip()]
    return '\n'.join(paras)

def build_entry(it):
    m = it['meta']
    content = '# ' + it['title'] + '\n' + model_text(it['body'])
    return {
        'enabled': True,
        'triggerWords': expand(m['触发']),
        'triggerWordsType': 'AND' if m.get('触发方式') == '同时满足' else 'OR',
        'blackListWords': expand(m.get('黑名单', '无')),
        'blackListWordsType': 'OR',
        'folder': m['文件夹'],
        'priority': int(m['优先级']),
        'probability': 100,
        'scanDepth': 2,
        'triggerRange': ['user', 'assistant'],
        'impactRange': ['system'],
        'contentMethod': 'single',
        'content': content,
    }

BATCH_DIRS = [('batch1', 'g*.md'), ('batch2', '*.md'), ('batch3', '*.md')]
items = []
for n, (d, pat) in enumerate(BATCH_DIRS, 1):
    for f in sorted(glob.glob(os.path.join(ROOT, 'moon', d, pat))):
        for it in parse_file(f):
            it['batch'] = n
            items.append(it)
entries = [build_entry(it) for it in items]

# ---------- 正则体检（平台口径：不许量词套量词，整条不超过 25 个量词；2026-10-13 实测） ----------
def is_rx(w):
    return w.startswith('/') and w.rfind('/') > 0

def quant_count(k):
    s_ = re.sub(r'\\.', 'x', k); s_ = re.sub(r'\[[^\]]*\]', 'C', s_)
    s_ = s_.replace('(?:', '(').replace('(?!', '(').replace('(?=', '(')
    return len(re.findall(r'\{\d*,?\d*\}|[*+?]', s_))

def star_height(k):
    i, best, contains, prev_close, prev_inner = 0, 0, [0], False, 0
    while i < len(k):
        c = k[i]
        if c == '\\': i += 2; prev_close = False; continue
        if c == '[':
            j = k.find(']', i + 2 if k[i + 1:i + 2] in ('^', ']') else i + 1); i = j + 1; prev_close = False; continue
        if c == '(':
            i += 3 if k[i:i + 3] in ('(?:', '(?!', '(?=') else 1; contains.append(0); prev_close = False; continue
        if c == ')':
            prev_inner = contains.pop(); prev_close = True; i += 1; continue
        m_ = re.match(r'\{\d*,?\d*\}', k[i:]) if c == '{' else None
        if c in '*+?' or m_:
            d_ = 1 + (prev_inner if prev_close else 0); best = max(best, d_); contains[-1] = max(contains[-1], d_)
            i += m_.end() if m_ else 1; prev_close = False; continue
        prev_close = False; i += 1
    return best

def regex_problems(w):
    body = w[1:w.rfind('/')]
    flags = w[w.rfind('/') + 1:]
    p_ = []
    if set(flags) - set('imsg'): p_.append('flags')
    try: re.compile(body)
    except re.error as ex: p_.append('编译失败 %s' % ex)
    if quant_count(body) > 25: p_.append('量词 %d>25' % quant_count(body))
    if star_height(body) > 1: p_.append('量词套量词')
    if re.search(r'\(\?P?<[A-Za-z]', body): p_.append('命名组没测过')
    return p_

# ---------- 校验 ----------
problems = []
card = json.load(open(SRC, encoding='utf-8'))
old = card['prompt']['lorebook']
old_titles = set()
for e in old:
    first = e['content'].strip().split('\n')[0]
    old_titles.add(first.lstrip('# ').strip())
titles = [it['title'] for it in items]
if len(set(titles)) != len(titles):
    problems.append('标题重复')
for it, e in zip(items, entries):
    t = it['title']
    if t in old_titles:
        problems.append('与旧条目同名：' + t)
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
    if e['triggerWordsType'] == 'AND' and ALIASES['〔月银纪·正则〕'][0] not in e['triggerWords']:
        problems.append(t + ' 同时满足里没有〔月银纪·正则〕')
    if not (0 <= e['priority'] <= 8192):
        problems.append(t + ' 优先级越界')
    c = e['content']
    for bad in ['——', '—', '；', '…', '！', '★', '（#']:
        if bad in c:
            problems.append('%s 正文里有「%s」' % (t, bad))
    if '：' in c:
        # 标签行、引号和反引号里的格式示例之外不该有冒号
        for line in c.split('\n'):
            bare = re.sub(r'「[^」]*」|`[^`]*`', '', line)
            if '：' in bare and not re.match(r'^(- )?[^，。：]{1,8}：', bare):
                problems.append('%s 冒号：%s' % (t, line[:40]))
    # 正文里引用的条目名要存在（允许只写标题的前一截；招式后缀•「冠」不算引用）
    for m_ in re.finditer(r'(?<!•)「([^」]+)」', c):
        ref = m_.group(1)
        if ref.startswith('纪元：'):
            continue
        if any(x == ref or x.startswith(ref) for x in list(titles) + list(old_titles)):
            continue
        problems.append('%s 引用了不存在的条目「%s」' % (t, ref))
    if len(c) > 100000:
        problems.append(t + ' 太长')

# 钥匙不能误中迷宫纪：拿旧卡的主提示词与全部旧条目扫一遍
haystack = card['prompt']['systemPrompt'] + '\n'.join(e['content'] for e in old)
gate_words = set()
for e in entries:
    for w in e['triggerWords']:
        if any(w in v for v in ALIASES.values()):
            gate_words.add(w)
gate_words |= set(ALIASES['〔月银纪〕'])
for w in sorted(gate_words):
    if is_rx(w):
        continue
    if w in haystack:
        problems.append('门控钥匙在旧卡里出现过：%r' % w)
era_rx = ALIASES['〔月银纪·正则〕'][0]
if re.search(era_rx[1:era_rx.rfind('/')], haystack):
    problems.append('〔月银纪·正则〕在旧卡里能中')
cred_rx = ALIASES['〔迷宫纪凭证〕'][0][1:ALIASES['〔迷宫纪凭证〕'][0].rfind('/')]
if not re.search(cred_rx, '命途已确认，请记录我的《奥尔德兰》角色建档：\n【一·灵魂形态】'):
    problems.append('〔迷宫纪凭证〕挡不住迷宫纪的建档凭证')
if re.search(cred_rx, '纪元：月银纪｜开局时段：万兽·焚原\n命途已确认，请记录我的《奥尔德兰》角色建档：'):
    problems.append('〔迷宫纪凭证〕把月银纪的开局也挡了')
# 别纪钥匙在旧卡主提示词里该出现（迷宫纪的日期格）
if '日期</b><br>迷宫纪' not in card['prompt']['systemPrompt']:
    problems.append('旧卡主提示词里找不到「日期</b><br>迷宫纪」，别纪钥匙对不上底座')
if 'hud-meta">日期' not in card['prompt']['systemPrompt']:
    problems.append('旧卡主提示词里 hud-meta 的格式变了')

# ---------- 旧条目：只给开局口令会叫醒的那几条加黑名单 ----------
# 旧卡的月银纪详史拿「月银纪」当触发词，开局口令「纪元：月银纪｜…」正好带着这三个字；
# 末年、魔族之世两条口令还会叫醒「登神」「魔族」两条。给它们加上〔月银纪〕三把钥匙当黑名单，
# 只挡月银纪开局那一轮。这几条只扫玩家的话，迷宫纪的局里玩家打不出这几个字，不受影响。
# 2026-10-13 用户同意（开局测试后「加黑名单」）。
OLD_PATCH = {
    14: '月银纪：详细正史', 29: '月银纪·各族发展史', 33: '精灵详史·月银纪', 34: '矮人详史·月银纪',
    35: '半身人详史·月银纪', 36: '兽耳族详史·月银纪', 37: '龙裔详史·月银纪', 38: '魔族详史·月银纪',
    39: '圣堂详史·月银纪', 43: '真龙详史·月银纪', 44: '月银纪·各族传奇与英雄名录',
    157: '神域之路·其一', 485: '魔族七大类',
}
patched_old = copy.deepcopy(old)
patch_lines = []
for i, prefix in sorted(OLD_PATCH.items()):
    e = patched_old[i]
    t = e['content'].strip().split('\n')[0].lstrip('# ').strip()
    if not t.startswith(prefix):
        raise SystemExit('旧条目 #%d 对不上：%s' % (i, t))
    if e.get('triggerRange') != ['user']:
        problems.append('旧条目 #%d 不是只扫用户，黑名单的效果要另算' % i)
    if e.get('blackListWords') and e.get('blackListWordsType') != 'OR':
        raise SystemExit('旧条目 #%d 原有黑名单是 AND，不能直接追加' % i)
    bl = list(e.get('blackListWords') or [])
    added = [w for w in ALIASES['〔月银纪〕'] if w not in bl]
    bl += added
    if len(bl) > 20:
        problems.append('旧条目 #%d 黑名单超过 20 个' % i)
    e['blackListWords'] = bl
    e['blackListWordsType'] = 'OR'
    patch_lines.append('旧 #%d %s  黑名单 +%d' % (i, t[:30], len(added)))

# ---------- 模拟第一轮：八条开局口令各叫醒哪些条目 ----------
def _match(w, t):
    if is_rx(w):
        body, flags = w[1:w.rfind('/')], w[w.rfind('/') + 1:]
        if regex_problems(w):
            return False                      # 平台会把它换成永不命中
        f = (re.I if 'i' in flags else 0) | (re.M if 'm' in flags else 0) | (re.S if 's' in flags else 0)
        return re.search(body, t, f) is not None
    return w in t                             # 纯词分大小写（探针三 R3）

def fires(e, msgs, sysp):
    """照探针三的结果：扫描深度圈出最近 N 条消息，按触发范围挑出来，一条一条单独判。
    OR 是这一条里有任一触发词，AND 是所有触发词都在这一条里，黑名单只看这一条。深度 0 当三条。"""
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

full = patched_old + entries
title_of = lambda e: e['content'].strip().split('\n')[0].lstrip('# ').strip()
sim_lines = []
OPENINGS = [(m, '纪元：月银纪｜开局时段：' + m) for m in MAINLINES]
OPENINGS.append(('万兽·焚原', '纪元：月银纪｜开局时段：万兽·焚原｜出身：黄金裔'))
for m, u in OPENINGS:
    got = [i for i, e in enumerate(full) if fires(e, [('user', u)], card['prompt']['systemPrompt'])]
    olds = [i for i in got if i < len(old) and not title_of(full[i]).startswith('世界自转')]
    news = [title_of(full[i]) for i in got if i >= len(old)]
    tag = m + ('＋黄金裔' if '黄金裔' in u else '')
    sim_lines.append('%-14s 新条目 %d 条 %d 字，旧条目 %d 条｜%s' % (
        tag, len(news), sum(len(full[i]['content']) for i in got if i >= len(old)), len(olds),
        '、'.join(n.replace('月银纪·', '') for n in news)))
    if olds:
        problems.append('开局口令「%s」还会叫醒旧条目 %s' % (u, olds))
    for need in ['月银纪·常驻｜这一局在月银纪', '月银纪·示范', '月银纪·主线｜' + m]:
        if need not in news:
            problems.append('开局口令「%s」没叫醒「%s」' % (m, need))

# ---------- 月银纪第二轮：拿焚原第一轮的真实回复，玩家再说一句 ----------
SAMPLES = os.path.join(ROOT, 'moon', 'samples')
read_sample = lambda n: open(os.path.join(SAMPLES, n), encoding='utf-8').read()
MOON_RUNS = [
    ('焚原首轮（10月13日，旧凭证）', read_sample('reply1_焚原首轮.html'), '纪元：月银纪｜开局时段：万兽·焚原',
     ['继续', '我去城里的神殿看看，问问祭司焚原的事', '找个铁匠，用狼骨打一把大剑', '去兽市卖掉狼皮，换点钱']),
    ('焚原首轮·黄金裔（v3.1 实测）', read_sample('reply_焚原首轮_黄金裔.html'), '纪元：月银纪｜开局时段：万兽·焚原｜出身：黄金裔',
     ['继续', '径直走向照壁，在达克牙将面前画押入伍，领取十两白银，加入明日开拔的第一支围剿联军。',
      '走向那个刻木棍的麦仓城幸存者（麦伦），向他打听古龙焚原那一夜的实情与麦仓城的废墟细节。',
      '暂不理会招募榜，顺着人流进入双桥城内，寻找铁匠铺、兽市或换钱处，打探兵刃行情与当地局势。']),
    ('焚原首轮·黄金裔（v3.2 实测）', read_sample('reply_焚原首轮_黄金裔_v32.html'), '纪元：月银纪｜开局时段：万兽·焚原｜出身：黄金裔',
     ['继续', '走上前去揭榜：向招募官询问围剿的队伍安排，以及金子的预付规矩。',
      '接近那个刻木棍的男人：他身上的血和灰证明他昨晚就在麦仓城，向他打听那头红鳞古龙的底细。']),
    ('焚原首轮·黄金裔（v4 实测）', read_sample('reply_焚原首轮_黄金裔_v4.html'), '纪元：月银纪｜开局时段：万兽·焚原｜出身：黄金裔',
     ['继续', '走向那个拿着木棍的青年（麦伦），问他麦仓城到底是怎么烧没的。',
      '拨开人群走到悬赏板前，不管别人怎么嘲笑，伸手把那张羊皮纸揭下来。',
      '向猎兽人们打听双桥城里哪里还能买到干粮，为接下来的长途跋涉做准备。']),
]
# 第三轮：拿去神殿那一轮的真实回复再往下推
MOON_RUNS3 = [
    ('焚原第二轮·去神殿（v4 实测）', read_sample('reply_焚原首轮_黄金裔_v4.html'), '去神殿', read_sample('reply_焚原第二轮_去神殿_v4.html'),
     '纪元：月银纪｜开局时段：万兽·焚原｜出身：黄金裔',
     ['继续', '询问老祭司，既然寻常刀剑无用，这附近有没有哪里能找到对付渊染古龙的兵器',
      '在祭火前站定，向这里的神明供奉两枚铜币', '去旅店要一碗热汤，顺便问问去熔铁炉心的路怎么走']),
]
moon_lines = []
for tag, r1, u2, r2, cmd, users in MOON_RUNS3:
    moon_lines.append('〔%s〕' % tag)
    for u in users:
        msgs = [('user', cmd), ('assistant', r1), ('user', u2), ('assistant', r2), ('user', u)]
        got = [i for i, e in enumerate(full) if fires(e, msgs, card['prompt']['systemPrompt'])]
        news = [i for i in got if i >= len(old)]
        olds = [i for i in got if i < len(old) and not title_of(full[i]).startswith('世界自转')]
        moon_lines.append('玩家「%s」：新条目 %d 条 %d 字｜%s' % (u[:20], len(news), sum(len(full[i]['content']) for i in news),
                          '、'.join(title_of(full[i]).replace('月银纪·', '') for i in news)))
        if olds:
            moon_lines.append('    旧条目 %d 条：%s' % (len(olds), '、'.join('#%d %s' % (i, title_of(full[i])[:16]) for i in olds)))
for tag, reply, cmd, users in MOON_RUNS:
    moon_lines.append('〔%s〕' % tag)
    for u in users:
        msgs = [('user', cmd), ('assistant', reply), ('user', u)]
        got = [i for i, e in enumerate(full) if fires(e, msgs, card['prompt']['systemPrompt'])]
        news = [i for i in got if i >= len(old)]
        olds = [i for i in got if i < len(old) and not title_of(full[i]).startswith('世界自转')]
        moon_lines.append('玩家「%s」：新条目 %d 条 %d 字｜%s' % (u[:20], len(news), sum(len(full[i]['content']) for i in news),
                          '、'.join(title_of(full[i]).replace('月银纪·', '') for i in news)))
        if olds:
            moon_lines.append('    旧条目 %d 条：%s' % (len(olds), '、'.join('#%d %s' % (i, title_of(full[i])[:16]) for i in olds)))

# 面板上一直印着的字不该叫醒条目：未认兵、未就职
PANEL_ONLY = ('<div><b>日期</b><br>月银纪1690年·秋·坠叶月·上旬三日</div>'
              '<div class="f path"><b>命路</b>命路未定｜职业 未认兵(Common)｜命星 未觉醒</div>'
              '<div class="f job"><b>职业</b>未认兵·Ⅰ｜职业 未就职</div>')
for i in range(len(old), len(full)):
    if title_of(full[i]) == '月银纪·兵器、风格与法门' and fires(full[i], [('assistant', PANEL_ONLY)], ''):
        problems.append('面板上的「未认兵／未就职」叫醒了兵器那一条')

# ---------- 迷宫纪的局：月银纪的条目一条都不该醒 ----------
MAZE_CREDS = {
    '身穿凭证': '命途已确认，请记录我的《奥尔德兰》角色建档：\n\n【一·灵魂形态】\n降临之魂 · 身穿（连人带身跌入）\n\n【二·种族胎骨】\n人类\n\n'
            '【六·誓心与赐物】\n誓心阵营：中立善良\n神殿赐物：风语短剑（Rare）：一把会低鸣的短剑\n'
            '【面板状态】尚未觉醒——开局第一件事是找一处冒险者公会分会完成登记与面板觉醒\n\n'
            '【七·现在何处】\n现在所在：阿卡迪亚·公会城\n\n【八·冒险初心】\n想变强，攒钱，顺便看看这个世界的魔兽和迷宫\n\n开始游戏。',
    '本地凭证': '命途已确认，请记录我的《奥尔德兰》角色建档：\n\n【一·灵魂形态】\n本地之魂（生于此世）\n\n【六·你的前半生】\n'
            '出生地：金鸢城\n出身家世：神殿孤儿　在七神圣堂的神殿里长大，跟着祭司学过祷告和冥想\n\n'
            '【七·现在何处】\n现在所在：阿卡迪亚·公会城\n当前处境：刚到公会城，想去冒险者公会就职\n\n'
            '【八·冒险初心】\n斩一头领主级的魔兽，攒钱买一把名器，有朝一日自立一国\n\n开始游戏。',
}
MAZE_REPLY = ('<details class="arc-hud-details"><summary class="arc-hud-summary"><div class="hud-summary-inner">'
              '<span class="hud-title-icon">✦</span><b>推演底座</b><span class="hud-meta">迷宫纪1001年·春·萌芽月·上旬三日 · '
              '09:20 巳初 · 阿卡迪亚·公会城·旅印大厅 · 第一兆·魔兽离巢·潮位二 · 防抢话 开 · 档位 很长</span></div></summary>'
              '<div class="detail-body arc-hud-body"><div class="hud-grid"><div><b>日期</b><br>迷宫纪1001年·春·萌芽月·上旬三日</div>'
              '<div><b>时辰</b><br>09:20 · 巳初</div><div><b>天气</b><br>晴，北面雪原吹来冷风</div>'
              '<div><b>地点</b><br>阿卡迪亚·公会城·旅印大厅</div><div><b>潮汐</b><br>第一兆·魔兽离巢·潮位二</div>'
              '<div><b>防抢话</b><br>开</div></div><div class="ap"><div class="f d"><b>2｜场面</b>活事件：公会悬赏榜换新｜'
              '其他在场：七神圣堂的祭司、猎兽的冒险者</div><div class="f d"><b>职业</b>未就职</div></div></div></details>\n\n'
              '公会的悬赏榜前挤满了人，七神圣堂的祭司站在神殿门口分圣水。几个刚到的新人围着柜台问就职和转职，'
              '有人说城外的领主级魔兽又下山了，铁匠铺里传来锤声，换钱的柜台排着长队，报酬照巴尔和索恩结。')
MAZE_USERS = ['我想去神殿拜一拜七神', '去公会揭一张魔兽的悬赏，顺便问问报酬', '拜师学剑，再去问问就职和转职',
              '这附近有没有火山或者雪原', '我要自立为王，建一座城',
              '我想打听焚原断刃的下落，还有落日弓', '林子里的树根盘根错节，我绕着走']
maze_lines = []
def maze_check(tag, msgs):
    got = [i for i, e in enumerate(full) if i >= len(old) and fires(e, msgs, card['prompt']['systemPrompt'])]
    maze_lines.append('%s：月银纪条目 %d 条%s' % (tag, len(got), ('｜' + '、'.join(title_of(full[i]) for i in got)) if got else ''))
    for i in got:
        problems.append('迷宫纪的局漏进月银纪条目（%s）：%s' % (tag, title_of(full[i])))
for k, cred in MAZE_CREDS.items():
    maze_check('迷宫纪首轮·' + k, [('user', cred)])
for u in MAZE_USERS:
    maze_check('迷宫纪中局·玩家「%s」' % u, [('user', MAZE_CREDS['本地凭证']), ('assistant', MAZE_REPLY), ('user', u)])
# v3.1 实测的迷宫纪首轮：开局口令＋真实回复＋回复给的三个分支
MAZE_CMD = '纪元：迷宫纪｜开局时段：默认时段｜出身：人类'
maze_real = read_sample('reply_迷宫纪首轮_人类.html')
maze_check('迷宫纪实测首轮·口令', [('user', MAZE_CMD)])
for u in ['出示行囊中的身份文书，报上姓名并宣告自己的誓心，正式完成见习旅印的烙印流程。',
          '向贝拉打听近期第一层「浅绿石窟」的魔兽离巢动向，以及报酬最稳妥的浅层清理委托。',
          '暂不在誓心栏落笔，先询问转职引导机构与本地铁匠铺的方位，打算先检视装备与补给。',
          '我想去神殿拜一拜七神，再问问哪里能换钱']:
    maze_check('迷宫纪实测第二轮·玩家「%s」' % u[:20], [('user', MAZE_CMD), ('assistant', maze_real), ('user', u)])

# ---------- 第二批：泛词地点在迷宫纪里不能醒，月银纪里要醒；条目之间的连带 ----------
B2_WORDS = ['镜湖', '熔铁炉心', '蜜酒丘陵', '王道', '原初之森', '龙眠天脊', '浮空塔', '曜冠山脉', '贾曼尼', '风铃高原',
            '风铃天池', '长船', '化圣雪原', '雷暴荒地', '火山带', '白鹿书堡', '星冠圣城', '轰鸣断崖', '裂影之地', '黑石高地', '西海', '塔影']
b2_lines = []
for w in B2_WORDS:
    maze_check('迷宫纪泛词·玩家「我想去%s看看」' % w, [('user', MAZE_CMD), ('assistant', maze_real), ('user', '我想去%s看看' % w)])
maze_check('迷宫纪泛词·回复里全提一遍', [('user', MAZE_CMD), ('assistant', MAZE_REPLY.replace('公会的悬赏榜前', '、'.join(B2_WORDS) + '，公会的悬赏榜前'))])
MOON_HUD = lambda era_year, place: ('<div><b>日期</b><br>月银纪%s</div><div><b>地点</b><br>%s</div>' % (era_year, place))
B2_SCENES = [
    ('诸国·金冕城加冕日', MOON_HUD('5380年·春·花信月·上旬三日', '东陆·白石平原·金冕城·冠殿前广场') + '老王死了，冠殿开门，日轮的祭司站在门口看日出，王道上来的商人挤在广场边上。',
     ['金冕城（月银纪）', '白石平原', '王道（月银纪）']),
    ('帝国·白冠城登记所', MOON_HUD('9102年·秋·坠叶月·中旬五日', '东陆·东方行省·白冠城·登记所外') + '塔影里的灯刚亮，登记所门口排着队，塔主的学徒从浮舟上下来。',
     ['白冠城', '浮空塔与塔影']),
    ('万兽·潮门港', MOON_HUD('2850年·夏·麦浪月·下旬二日', '西陆·西海岸·潮门港·船主会会馆') + '老珠湾的人在坡上晒网，有人说珠湾旧城的塔尖退潮的时候露出来了。',
     ['潮门港（月银纪）', '珠湾', '西海（月银纪）']),
    ('崛起·环山北口', MOON_HUD('5992年·冬·初雪月·上旬一日', '西陆·黑石高地·环山北口·谷口的村子') + '公国的山口关着，谷里等门开的人在教孩子唱歌，高地上的诸侯又打起来了。',
     ['环山北口', '黑石高地（月银纪）']),
    ('帝国·熔铁炉心', MOON_HUD('8400年·春·花信月·中旬一日', '东陆·南部山脉·熔铁炉心·上层的市') + '炉城的锻师在多恩砧前看一个学徒的头一件作品，外坊的矮人从轰鸣断崖上来了。',
     ['熔铁炉心（月银纪）', '轰鸣断崖与断崖桥']),
]
for tag, reply, want in B2_SCENES:
    got = [title_of(e) for e in full[len(old):] if fires(e, [('assistant', reply)], '')]
    b2_lines.append('%s：醒了 %d 条｜%s' % (tag, len(got), '、'.join(t.replace('月银纪·', '') for t in got)))
    for w in want:
        if w not in got:
            problems.append('月银纪场景「%s」没叫醒「%s」' % (tag, w))
# ---------- 第三批：人物、旅伴、势力 ----------
# 迷宫纪里玩家找帮手、问行会、问登记所、问诗人，泛词条目一条都不该醒（都是同时满足的 G 形）
B3_MAZE_USERS = ['找个同伴一起走，最好是会治伤的', '我想雇个人搭伙下迷宫', '去登记所登记一下', '问问骑士誓约是怎么回事',
                 '找个诗人打听打听名号', '猎团怎么分成的', '去林市买一把弓', '我想加入军团', '去协会问问大魔导收不收学徒',
                 '找车队搭车去下一座城', '问问王室和宫廷的规矩', '找祭司们问问丧仪的事']
for u in B3_MAZE_USERS:
    maze_check('迷宫纪第三批泛词·玩家「%s」' % u, [('user', MAZE_CMD), ('assistant', maze_real), ('user', u)])
B3_REPLY_WORDS = ['军团', '协会', '王室', '诗人', '名号', '精灵王庭', '登记所', '医棚', '猎团', '车队', '掌柜', '会盟', '盟主',
                  '骑士誓约', '散裔', '信使家族', '四支', '同伴', '旅伴', '大魔导', '祭司们', '守火人', '判词', '木牌']
maze_check('迷宫纪第三批泛词·回复里全提一遍', [('user', MAZE_CMD), ('assistant', MAZE_REPLY.replace('公会的悬赏榜前', '、'.join(B3_REPLY_WORDS) + '，公会的悬赏榜前'))])
# 只在月银纪才有的名字（直醒的 U 形条目）不该在旧卡里出现过，不然迷宫纪的玩家也可能打出来
u_name_lines = []
for it, e in zip(items, entries):
    if e['triggerWordsType'] != 'OR' or not any(w in e['blackListWords'] for w in ALIASES['〔别纪〕']):
        continue
    for w in e['triggerWords']:
        alts = w[1:w.rfind('/')].split('|') if is_rx(w) else [w]
        for a in alts:
            if '(?' in a or any(ch in a for ch in '[]()^$\\.'):
                continue                      # 带守卫或别的正则记号的备选项另算
            if a and a in haystack:
                u_name_lines.append('%s：「%s」旧卡里有' % (it['title'], a))
for l in u_name_lines:
    problems.append('直醒条目的名字撞了旧卡：' + l)
# 月银纪的回复里提到人、提到找帮手、提到势力，该醒的要醒
B3_SCENES = [
    ('万兽·双桥城河滩', MOON_HUD('1690年·秋·坠叶月·上旬三日', '东陆·青麦原·双桥城·南桥河滩') +
     '麦伦蹲在河滩上刻木棍，猎兽人围着悬赏板掂量那张羊皮纸，有人说缇里安的落日弓只射一次，有人说要去找个同伴再走。',
     ['人物｜麦伦，青麦原人', '人物｜缇里安，只射一次', '月银纪·旅伴']),
    ('诸国·三川会盟', MOON_HUD('5380年·春·花信月·上旬三日', '东陆·三川城·万神坛前') +
     '七王的旗立在万神坛前，盟坛上只站得下一个人，埃德加走了上去。城外嘉兰的白烛医棚里还躺着昨天的伤兵，酒馆里一个诗人抱着琴唱哈尔加的独桥。',
     ['势力｜七王与三川会盟', '人物｜埃德加，星湖王，头一位盟主', '势力｜朱亚教会与白烛医棚', '人物｜嘉兰，白烛之始',
      '势力｜诗人与传唱', '人物｜哈尔加·石踵，独桥']),
    ('帝国·白冠城登记所', MOON_HUD('9102年·秋·坠叶月·中旬五日', '东陆·东方行省·白冠城·登记所外') +
     '登记官翻着册子，驱逐队押着一队人往西走，有个兵说起渡火者薇丝拉。塔上的大魔导没下来，总督府的人在门口数木牌。',
     ['势力｜血脉审判与登记所', '势力｜术式军团', '人物｜渡火者薇丝拉', '势力｜月银学院与魔导协会']),
    ('旅伴·旅店里找帮手', MOON_HUD('1702年·冬·初雪月·上旬一日', '东陆·青麦原·双桥城·南桥旅店') +
     '玩家说要找个帮手。旅店里坐着一个叫席格的猎户，腰上挂着一把旧刀，灶边一个半身人孩子提姆在刮锅，门口的猎兽人戈兰一个人喝酒。',
     ['月银纪·旅伴', '旅伴｜席格，练了一半呼吸法的猎户', '旅伴｜提姆，半身人厨子的学徒', '旅伴｜戈兰，一个人猎的猎兽人']),
    ('崛起·环山北口结阵', MOON_HUD('6007年·冬·初雪月·下旬三日', '西陆·黑石高地·环山北口') +
     '梅瑞丝站在阵心，一百枚月银指环一起亮了。塞维林在山口的塔上看着，瓦伦廷还是个孩子。',
     ['人物｜梅瑞丝，百人阵的阵心', '人物｜塞维林，出山的公爵', '人物｜瓦伦廷，萨尔维斯的头一位王']),
]
b3_lines = []
for tag, reply, want in B3_SCENES:
    got = [title_of(e) for e in full[len(old):] if fires(e, [('assistant', reply)], '')]
    b3_lines.append('%s：醒了 %d 条 %d 字｜%s' % (tag, len(got), sum(len(e['content']) for e in full[len(old):] if title_of(e) in got),
                    '、'.join(t.replace('月银纪·', '') for t in got)))
    for w in want:
        if w not in got:
            problems.append('月银纪场景「%s」没叫醒「%s」' % (tag, w))
# 连带：一条新条目的触发词，顺带叫醒了哪些别的新条目（看第二、三批）
b2_items = [it for it in items if it['batch'] >= 2]
b2_entries = entries[len(items) - len(b2_items):]
era_msg = '日期</b><br>月银纪'
link_lines = []
for it, e in zip(b2_items, b2_entries):
    rx = [w for w in e['triggerWords'] if is_rx(w) and w != ALIASES['〔月银纪·正则〕'][0]]
    alts = rx[0][1:rx[0].rfind('/')].split('|') if rx else []
    hit_others = set()
    for a in alts:
        a_plain = re.sub(r'\(\?[!:].*?\)', '', a)
        if any(ch in a_plain for ch in '[]()^$\\'):
            continue
        msg = era_msg + ' ' + a_plain
        for j, (it2, e2) in enumerate(zip(items, entries)):
            if it2['title'] == it['title'] or it2['title'].startswith(('月银纪·常驻', '月银纪·示范', '月银纪·纪元钟')):
                continue
            if fires(e2, [('assistant', msg)], ''):
                hit_others.add('%s←%s' % (it2['title'].replace('月银纪·', '')[:12], a_plain))
    if hit_others:
        link_lines.append('%s：%s' % (it['title'], '、'.join(sorted(hit_others))))

# ---------- 产物 ----------
OUT_NAME = '奥尔德兰_日里版_月银纪前三批_测试v5.json'
os.makedirs(OUT, exist_ok=True)
new_card = copy.deepcopy(card)
new_card['prompt']['lorebook'] = patched_old + entries
json.dump(entries, open(os.path.join(OUT, 'moon_b1_entries.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
out_card = os.path.join(OUT, OUT_NAME)
json.dump(new_card, open(out_card, 'w', encoding='utf-8'), ensure_ascii=False)
# 往返校验：重新读回。旧条目除了那十三条的黑名单逐字不变，新条目逐字一致
back = json.load(open(out_card, encoding='utf-8'))
strip_bl = lambda e: {k: v for k, v in e.items() if k not in ('blackListWords', 'blackListWordsType')}
for i, (a, b) in enumerate(zip(back['prompt']['lorebook'][:len(old)], old)):
    if i in OLD_PATCH:
        assert strip_bl(a) == strip_bl(b), i
        assert a['blackListWords'][:len(b['blackListWords'])] == b['blackListWords'], i
        assert a['blackListWords'][len(b['blackListWords']):] == [w for w in ALIASES['〔月银纪〕'] if w not in b['blackListWords']], i
    else:
        assert a == b, i
assert len(back['prompt']['lorebook']) == len(old) + len(entries)
assert back['prompt']['lorebook'][len(old):] == entries
for k in card:
    if k != 'prompt':
        assert back[k] == card[k], k
for k in card['prompt']:
    if k != 'lorebook':
        assert back['prompt'][k] == card['prompt'][k], k

# 报告
lines = ['条目 %d 条，旧条目 %d 条，合计 %d 条' % (len(entries), len(old), len(old) + len(entries)), '']
total = 0
for it, e in zip(items, entries):
    n = len(e['content']); total += n
    lines.append('%-28s %s  优先级%d  %s触发%d 黑名单%d  %d字' % (it['title'], e['folder'], e['priority'],
                 '同时满足 ' if e['triggerWordsType'] == 'AND' else '', len(e['triggerWords']), len(e['blackListWords']), n))
lines += ['', '正文合计 %d 字' % total]
for n in sorted(set(it['batch'] for it in items)):
    bi = [(it, e) for it, e in zip(items, entries) if it['batch'] == n]
    lines.append('第%d批 %d 条 %d 字（直醒 %d 条，同时满足 %d 条）' % (
        n, len(bi), sum(len(e['content']) for _, e in bi),
        sum(1 for _, e in bi if e['triggerWordsType'] == 'OR'), sum(1 for _, e in bi if e['triggerWordsType'] == 'AND')))
lines += ['', '旧条目改动（只加黑名单）：'] + patch_lines
lines += ['', '第一轮模拟（开局口令，世界自转那条不计）：'] + sim_lines
lines += ['', '月银纪第二轮模拟（首轮真实回复＋玩家一句）：'] + moon_lines
lines += ['', '迷宫纪漏检（月银纪条目一条都不该醒）：'] + maze_lines
lines += ['', '第二批场景（月银纪回复里提到地方）：'] + b2_lines
lines += ['', '第三批场景（月银纪回复里提到人、帮手、势力）：'] + b3_lines
lines += ['', '第二、三批连带（一个词叫醒的别的新条目，常驻、示范、纪元钟不计）：'] + [l for l in link_lines if l]
lines += ['', '产物：' + OUT_NAME, '', '问题：' + ('无' if not problems else '')] + problems
open(os.path.join(OUT, 'moon_b1_report.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
