#!/usr/bin/env python3
# 月银纪二十七个时代的页，从各页源稿里抽成一份数据（data/moon.json），时代页照它排。
# 只搬运，不改字：题、篇描述、钩子、史诗开头那一节、开局头几句、各幕的标题、默认收束、旅伴身份的头一句、灾祸之兽的所在和体型、地点谱里这一页提到的地方。
# 给作者和模型看的话（带 玩家、AI、★、裁定、底座、潮汐格、凭证 的句子）不抽。
#   python -I -X utf8 build_data.py            写 data/moon.json，报每个时代抽到了什么
#   python -I -X utf8 build_data.py --show m07 把这一个时代抽到的全文打出来看
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
CAST = os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'cast')
NUM = '一二三四五六七八九十'


def cn(i):
    return NUM[i - 1] if i <= 10 else '十' + NUM[i - 11]


# 三部：四首长诗里月银纪的三首，各带那一句节描述（合篇第三稿定的）
PARTS = [
    {'name': '天亮以前', 'line': '天亮以前，人只有火。', 'sub': '祭火与万兽 · 月银纪 1 年至 3000 年'},
    {'name': '天亮以后', 'line': '天亮以后，诸神于坛前落座。', 'sub': '诸国期 · 月银纪 3001 年至 6006 年'},
    {'name': '天黑以前', 'line': '天黑以前，人将灯火擎上高天。', 'sub': '萨尔维斯 · 月银纪 6007 年至 10081 年'},
]
SONG_YEARS = ['1', '约 1020', '约 1100', '约 1205', '1350', '1449', '1690', '1721', '2393', '2499', '2620', '2800', '2899', '2950', '3000']
ZG = [('晨祷', '3001 — 3720'), ('午祷上', '3800 — 4350'), ('午祷下', '4420 — 4830'), ('晚祷上', '5000 — 5300'), ('晚祷下', '5379 — 5600'), ('夜祷', '5600 — 6006')]
SA = [('崛起上', '6006 — 6599'), ('崛起下', '6600 — 8080'), ('帝国', '8081 — 9099'), ('魔族之世', '9100 — 9899'), ('末年上', '9900 — 10078'), ('末年下', '10075 — 10081')]

PAGES = []
for i in range(1, 16):
    d = os.path.join(ROOT, '月银纪史诗')
    f = [x for x in os.listdir(d) if x.startswith('第' + cn(i) + '歌_')][0]
    PAGES.append({'id': 'm%02d' % i, 'part': 0, 'label': '第' + cn(i) + '歌', 'title': f[:-3].split('_', 1)[1], 'years': SONG_YEARS[i - 1],
                  'path': os.path.join(d, f), 'cast': os.path.join(CAST, '月银纪史诗', 'ge%d.json' % i), 'set': '月银纪史诗'})
for i, (n, y) in enumerate(ZG, 1):
    PAGES.append({'id': 'm%02d' % (15 + i), 'part': 1, 'label': n, 'title': '', 'years': y,
                  'path': os.path.join(ROOT, '诸国期', '诸国期时段_%s_%s.md' % (cn(i), n)), 'cast': os.path.join(CAST, '诸国期', 'zg%d.json' % i), 'set': '诸国期'})
for i, (n, y) in enumerate(SA, 1):
    PAGES.append({'id': 'm%02d' % (21 + i), 'part': 2, 'label': n, 'title': '', 'years': y,
                  'path': os.path.join(ROOT, '萨尔维斯', '萨尔维斯时段_%s_%s.md' % (cn(i), n)), 'cast': os.path.join(CAST, '萨尔维斯', 'sa%d.json' % i), 'set': '萨尔维斯'})

META = re.compile(r'玩家|AI|★|裁定|底座|潮汐格|凭证|条目|这一页|这一条|正史里|旅伴|主线|开局|默认收束|下落不给')
NOTE = re.compile(r'[①②③④⑤⑥⑦⑧⑨⑩]')


def clean(t):
    t = re.sub(r'（[^（）]*★[^（）]*）', '', t)
    t = t.replace('★', '')
    t = re.sub(r'，?(往后的事)?照「[^」]*」(那一条)?', '', t)      # 指到别的条目的话，时代页上没有那些条目
    t = t.replace('，他没有活到下一段', '')
    return NOTE.sub('', t).strip()


def sentences(t):
    """按句号切，引号里的句号不切。"""
    out, cur, depth = [], '', 0
    for ch in t:
        cur += ch
        if ch == '“':
            depth += 1
        elif ch == '”':
            depth = max(0, depth - 1)
            if cur[-2:-1] in '。？':     # 引语收在句号上，引号后头就算一句完
                pass
        if ch in '。？' and depth == 0:
            out.append(cur)
            cur = ''
    if cur.strip():
        out.append(cur)
    return out


def head(t, cap):
    """取开头几句，不超过 cap 个字，至少一句。"""
    got = ''
    for s in sentences(t):
        if got and len(got) + len(s) > cap:
            break
        got += s
    return got.strip()


def drop_meta(t):
    return ''.join(s for s in sentences(t) if not META.search(s)).strip()


def blocks(lines):
    """按 ## 切成条目：[(标题, [行])]"""
    out, cur = [], None
    for l in lines:
        if l.startswith('## '):
            cur = (l[3:].strip(), [])
            out.append(cur)
        elif cur is not None:
            cur[1].append(l)
    return out


def epic_opening(body):
    """史诗条目的开头那一节：小标题和它底下的几段。"""
    title, paras, seen = '', [], False
    for l in body:
        if l.startswith('【调用】'):
            continue
        if l.startswith('### '):
            if seen:
                break
            title, seen = l[4:].strip(), True
            continue
        if not seen:
            if l.strip() and not title:
                seen = True      # 没有小标题的，从头一段起
            else:
                continue
        s = l.strip()
        if not s or s.startswith('〔') or s.startswith('**注') or s.startswith('- ') or s.startswith('|'):
            continue
        paras.append(clean(s))
    out, n = [], 0
    for p in paras:
        if out and n + len(p) > 400:
            break
        out.append(p)
        n += len(p)
    return {'title': title, 'text': out}


def mainline(title, body):
    name = re.sub(r'（[^）]*稿）', '', title.split('主线｜', 1)[1]).strip()
    r = {'name': name, 'pian': '', 'ti': '', 'pianDesc': '', 'hooks': [], 'open': '', 'acts': [], 'ending': ''}
    opened = False
    for l in body:
        s = l.strip()
        if s.startswith('题：'):
            a = s[2:].split('｜', 1)
            r['pian'], r['ti'] = a[0], a[1] if len(a) > 1 else ''
        elif s.startswith('篇：'):
            r['pianDesc'] = s[2:]
        elif s.startswith('“') and not opened and len(r['hooks']) < 3:
            r['hooks'].append(s)
        elif s.startswith('开局：'):
            opened = True
            r['open'] = head(drop_meta(clean(s[3:])), 190)
        elif re.match(r'^[一二三四五]幕｜', s) or s.startswith('收束｜'):
            r['acts'].append(clean(s))
        elif s.startswith('幕间｜'):
            r['acts'].append(clean(s))
        elif s.startswith('默认收束：'):
            r['ending'] = drop_meta(clean(s[5:]))
    m = re.search(r'月银纪(约)?(\d+)年', r['open'])
    r['year'] = (('约 ' if m.group(1) else '') + m.group(2)) if m else ''
    return r


# ---- 档案页（11-12 用户要的：旅伴和相遇点开看档案、立绘、表情，会死在这一段里的写死期和死因）----
# 档案的字照旧只搬运。比时代页多挡几样：只给模型留底的话、说“不点破”的那几句、指到别的条目和别的时段的话。
META_P = re.compile(r'玩家|AI|★|裁定|底座|底卡|照原条|潮汐格|凭证|条目|这一页|这一条|这一卷|这一稿|叙述里|不点破|不说破|不定死|演的时候|马脚|模型|留底|局里|默认收束|下落不给|不下结论')
REF_TAIL = re.compile(r'，?(?:往后的事|往后)照[^，。]{0,18}(?:那一段|传奇条|那一条)')
VEIL = re.compile(r'不点破|不说破|不露马脚|不定死')      # 这个人是谁不点破的（多半是走在凡人中间的神）：底那一栏不搬，祂换成寻常的他、她
STAR = re.compile(r'(Special|Passive|Art|Active|Ability)【([^】]+)】\((Common|Rare|Epic|Legend|Unique)')


def keep(t):
    t = REF_TAIL.sub('', clean(t))
    return ''.join(s for s in sentences(t) if not META_P.search(s)).strip()


def stars_of(line):
    """能力那一行：Special【名】(阶，说明)｜Passive【名】(…)。说明里可能有逗号，照括号配对切。"""
    out = []
    for m in STAR.finditer(line):
        i, depth, j = m.end(), 1, m.end()
        while j < len(line) and depth:
            depth += {'(': 1, ')': -1}.get(line[j], 0)
            j += 1
        text = line[i:j - 1].lstrip('，, ')
        out.append({'kind': m.group(1), 'name': m.group(2), 'tier': m.group(3), 'text': keep(text + '。').rstrip('。')})
    return out


def para_after(body, i):
    """小标题底下那一段（到下一个小标题、方括号栏、专属羁绊、条目设置为止）。"""
    out = []
    for l in body[i + 1:]:
        s = l.strip()
        if s.startswith('###') or s.startswith('【') or s.startswith('专属羁绊') or s.startswith('>') or s.startswith('## '):
            break
        if s:
            out.append(s)
    return out


def prof_cast(body):
    """旅伴条里给人看的那几栏。体态只取身高；声口只取台词样例；好感、裁定锁、条目设置不搬。"""
    p = {'sec': [], 'stars': [], 'lines': [], 'life': [], 'lifeT': '', 'fate': '', 'bond': '', 'height': '', 'rank': '', 'job': '', 'trait': ''}
    for i, l in enumerate(body):
        s = l.strip()
        for tag, h in (('身份：', '身份'), ('外貌：', '外貌'), ('装束：', '装束'), ('初见：', '初见'), ('关系：', '相处')):
            if s.startswith(tag):
                t = keep(s[len(tag):])
                if t:
                    p['sec'].append({'h': h, 't': t})
        if s.startswith('**性格底色：'):
            p['trait'] = keep(s.strip('*')[5:])
        elif s.startswith('体态数据'):
            m = re.search(r'身高\s*([0-9.]+\s*cm)', s)
            p['height'] = m.group(1).replace(' ', '') if m else ''
        elif s.startswith('底座：'):
            segs = s[3:].split('｜')
            if len(segs) > 1:
                p['rank'] = re.split(r'[，,]', segs[1])[0].strip()
            for g in segs:
                if g.startswith('职业 '):
                    p['job'] = keep(g[3:] + '。').rstrip('。')
        elif s.startswith('能力：'):
            p['stars'] = stars_of(s[3:])
        elif s.startswith('- 台词样例：'):
            p['lines'] = [x.strip() for x in s[len('- 台词样例：'):].split('／') if x.strip()][:6]
        elif s.startswith('### 手写活人层'):
            p['lifeT'] = s.split('｜', 1)[1].strip() if '｜' in s else ''
            p['life'] = [keep(x.lstrip('- ')) for x in para_after(body, i)]
            p['life'] = [x for x in p['life'] if x]
        elif s.startswith('### 正史里的下场'):
            p['fate'] = keep(''.join(para_after(body, i)))
        elif s.startswith('专属羁绊：'):
            p['bond'] = s[5:].strip()
    return p


def prof_meet(title, body):
    """人物条：一条一条的小栏照搬（声口是给模型看的写法，不搬）。是谁不点破的那几位，底那一栏不搬。"""
    text = '\n'.join(body)
    veil = bool(VEIL.search(text))
    she = bool(re.search(r'姑娘|妇人|女|婆|她', title))
    p = {'sec': [], 'fate': '', 'veil': veil}
    for l in body:
        m = re.match(r'^- ([^：]{1,12})：(.+)$', l.strip())
        if not m or m.group(1) in ('声口',):
            continue
        h, t = m.group(1), m.group(2)
        if veil:
            t = t.replace('祂', '她' if she else '他')
        if h == '底':
            if not veil:
                t = re.sub(r'^正史里', '', t)
                cut = re.search(r'玩家', t)        # 从说到玩家的那一句起都是给模型的话
                if cut:
                    t = t[:t.rfind('。', 0, cut.start()) + 1]
                p['fate'] = keep(t)
            continue
        t = keep(t)
        if t:
            p['sec'].append({'h': {'位阶／兵器／出身': '位阶与出身'}.get(h, h), 't': t})
    return p


def companion(title, body, cast):
    name = re.sub(r'（.*', '', title.split('：', 1)[1]).strip()
    who, race = '', ''
    for l in body:
        s = l.strip()
        if s.startswith('身份：') and not who:
            who = head(drop_meta(clean(s[3:])) or clean(s[3:]), 46)
        if s.startswith('固定锚定：') and not race:
            m = re.search(r'种族锚定=([^｜]+)', s)
            race = m.group(1).strip() if m else ''
    key, pset = find_cast(name, cast)
    seg = re.search(r'（月银纪·([^）]+)）', title)
    born = None
    for l in body:
        m = re.search(r'生于月银纪(前)?(\d+)年', l)
        if m and l.strip().startswith('固定锚定：'):
            born = (1 - int(m.group(2))) if m.group(1) else int(m.group(2))
            break
    return {'name': name, 'who': who, 'race': race, 'key': key, 'pset': pset, 'seg': seg.group(1) if seg else '', 'born': born, 'prof': prof_cast(body)}


def person(title, body, cast):
    """人物条：名字和称谓取标题里的，档案照 prof_meet 抽（有的条目底下写着这个人其实是谁，那几句挡在 prof_meet 里）。"""
    t = title[:-len('（人物）')].strip()
    name, _, tag = t.partition('，')
    key, pset = find_cast(name, cast) if tag else ('', '')
    return {'name': name, 'tag': tag, 'who': '', 'key': key, 'pset': pset, 'prof': prof_meet(title, body)}


def background(body):
    """旅途同行·背景：头一段是来路，最深恐惧那一行单取。"""
    past, fear = [], ''
    for l in body:
        s = l.strip()
        if not s or s.startswith('【调用】') or s.startswith('>') or s.startswith('#'):
            continue
        if s.startswith('- '):
            if s.startswith('- 最深恐惧：'):
                fear = keep(s[len('- 最深恐惧：'):])
            continue
        past.append(keep(s))
    return {'past': ' '.join(x for x in past if x), 'fear': fear}


def legends(body, cast):
    """这一段的传奇表：一行一位，名字、传奇之名、哪一档。前头几歌传下来的标 old。"""
    out = []
    for l in body:
        s = l.strip()
        # 三种写法：名，名号，传奇·档（…）｜名，名号，传奇（…）｜名，传奇，哪一年到的
        m = re.match(r'^- ([^，、]{1,10})，(?:([^，]{1,14})，)?(圣座位阶的)?传奇(?:·([^（，]+))?', s)
        if not m or '照' in m.group(1) or '位' in m.group(1):
            continue
        name = re.sub(r'^主祭', '', m.group(1))
        key, pset = find_cast(name, cast)
        out.append({'name': name, 'title': m.group(2) or '', 'tier': (m.group(4) or ('圣座' if m.group(3) else '')).strip(), 'key': key, 'pset': pset, 'old': '传下来的' in s})
    return out


CAST_ALL = None


def find_cast(name, cast):
    """先在这一页自己的资料里找，找不到再到别的纪的资料里找（活过几纪的传奇画在别的纪的文件夹里）。回 (键, 哪一套)。"""
    global CAST_ALL
    for c in cast[0]:
        if c.get('name') == name:
            return c.get('en', ''), cast[1]
    if CAST_ALL is None:
        import glob
        CAST_ALL = []
        for f in sorted(glob.glob(os.path.join(CAST, '**', '*.json'), recursive=True)):
            if os.path.basename(f) == '覆盖.json' or os.sep + '主角' + os.sep in f or os.sep + '神明' + os.sep in f:
                continue
            try:
                d = json.load(open(f, encoding='utf-8'))
            except Exception:
                continue
            rel = os.path.relpath(f, CAST).split(os.sep)
            pset = rel[0] if len(rel) > 1 else '1001'
            if isinstance(d, list):
                CAST_ALL += [(c.get('name', ''), c.get('en', ''), pset) for c in d if isinstance(c, dict)]
    short = name.split('·')[0]
    for same in (True, False):
        for n, en, pset in CAST_ALL:
            if (pset == cast[1]) != same or not n or not en:
                continue
            if n == name or n.split('·')[0] == short:
                return en, pset
    return '', ''


def beast(title, body):
    name = title.split('｜', 1)[1]
    name = re.sub(r'（[^）]*稿）', '', name).strip()
    kind = title.split('｜', 1)[0]
    line = ''
    for l in body:
        s = l.strip()
        if s.startswith('所在：'):
            line = s
            break
    where = re.search(r'所在：(.*?)。', line)
    size = re.search(r'体型：(.*?)。', line)
    tier = re.search(r'位阶：(.*?)。', line)
    return {'kind': kind, 'name': name, 'where': clean(where.group(1)) if where else '', 'size': clean(size.group(1)) if size else '', 'tier': tier.group(1) if tier else ''}


def places_of(text, table):
    out = []
    for row in table:
        n = row['名字']
        if len(n) < 2:
            continue
        if text.count(n) >= 2:
            later = re.sub(r'（.*?）', '', row.get('1001年叫什么', '')).split('、')[0].split('，')[0].strip()
            if later in ('', '无', '—', '-') or later.startswith('没有') or later.startswith('无') or later == n:
                later = ''
            out.append({'name': n, 'kind': row.get('类', ''), 'main': row.get('主要还是次要', '') == '主要', 'where': head(clean(row.get('位置', '')), 44), 'later': later, 'n': text.count(n)})
    out.sort(key=lambda r: (-r['main'], -r['n']))
    for r in out:
        del r['n']
    return out[:8]


OLD_AT = 40        # 人、半身人、兽耳这些寿数跟人差不多的，到了这个岁数算大人


def sort_roles(era):
    """照用户 11-12 定的三类分：
    旅伴是这个时代最有天分的年轻人、故事原本的主人公；相遇是大人和老人、故事的配角；传奇是此刻在世、已经讲完自己故事的人。
    旅途同行里已经在传奇表上的（前头几歌传下来的）归传奇；寿数跟人差不多、到这一段已经四十岁往上的归相遇。"""
    years = {l['name'].split('·', 1)[-1]: l['year'] for l in era['lines']}
    first = era['lines'][0]['year'] if era['lines'] else ''
    old_names = {g['name'] for g in era['legends'] if g['old']}
    keep, moved, grown = [], [], []
    for c in era['cast']:
        y = years.get(c['seg'], first)
        y = int(re.sub(r'\D', '', y)) if re.search(r'\d', y or '') else None
        age = (y - c['born']) if (y is not None and c['born'] is not None) else None
        c['age'] = age
        mortal = bool(re.match(r'^(人类|半身人|兽耳|半兽人|狼耳|犬耳|狐耳|猫耳)', c['race']))
        if c['name'] in old_names:
            moved.append((c['name'], '传奇', age))
            continue
        if mortal and age is not None and age >= OLD_AT:
            grown.append({'name': c['name'], 'tag': '', 'who': c['who'], 'key': c['key'], 'pset': c['pset'], 'race': c['race'], 'age': age, 'prof': c.get('prof')})
            moved.append((c['name'], '相遇', age))
            continue
        keep.append(c)
    era['cast'] = keep
    short = lambda n: n.split('·')[0]
    mine = {short(c['name']) for c in keep} | {short(g['name']) for g in grown}
    era['legends'] = [g for g in era['legends'] if short(g['name']) not in mine]   # 这一段里才到传奇的那一位不在表上露底
    lg = [g['name'] for g in era['legends']]
    era['meet'] = grown + [m for m in era['meet'] if not any(short(n) in (m['name'] + m['tag']) for n in lg)]   # 人物条写的是传奇本人的，归传奇
    era['moved'] = moved
    for c in era['cast']:
        c.pop('born', None)


def load_places():
    p = os.path.join(ROOT, '底稿', '地图', '地点谱', '月银纪.tsv')
    rows = open(p, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
    keys = rows[0].split('\t')
    return [dict(zip(keys, r.split('\t'))) for r in rows[1:] if r.strip()]


PROFS = {}        # 时代 → 名字 → 档案，另写成 data/prof/时代.json，点开人的时候才载


def take_profiles(era, bgs, fates):
    """把旅伴和相遇身上的档案摘出来放进 PROFS，时代页的数据里只留一个记号 p。死期和死因照手写的 fate_table.json。"""
    out = {}
    for kind in ('cast', 'meet'):
        for c in era[kind]:
            p = c.pop('prof', None)
            if not p or not (p.get('sec') or p.get('fate')):
                continue
            p['kind'] = kind
            for k in ('race', 'age'):
                if c.get(k) not in (None, ''):
                    p[k] = c[k]
            if c.get('tag'):
                p['tag'] = c['tag']
            bg = bgs.get(c['name'])
            if bg and (bg['past'] or bg['fear']):
                p.update(bg)
            d = fates.get(c['name'])
            if d:
                p['death'] = d
            out[c['name']] = {k: v for k, v in p.items() if v not in ('', [], None, False)}
            c['p'] = 1
            if d:
                c['d'] = 1          # 名单上给会死在这一段里的人留一个记号
    PROFS[era['id']] = out


def build():
    table = load_places()
    eras = []
    running = []       # 上一页的传奇表
    fp = os.path.join(HERE, 'fate_table.json')
    fate_all = json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {}
    for pg in PAGES:
        text = open(pg['path'], encoding='utf-8').read().replace('\r\n', '\n')
        bl = blocks(text.split('\n'))
        cast = (json.load(open(pg['cast'], encoding='utf-8')) if os.path.exists(pg['cast']) else [], pg['set'])
        era = {'id': pg['id'], 'part': pg['part'], 'label': pg['label'], 'title': pg['title'], 'years': pg['years'], 'set': pg['set'],
               'epic': None, 'songs': [], 'lines': [], 'cast': [], 'meet': [], 'legends': [], 'beasts': [], 'places': []}
        main_text = ''      # 地点只照主线正文里提到的算：别的条目的【调用】里常提往后才有的地方
        bgs = {}
        for title, body in bl:
            if title.startswith('旅途同行·背景：'):
                bgs.setdefault(re.sub(r'（.*', '', title.split('：', 1)[1]).strip(), background(body))
            if '主线｜' in title:
                main_text += '\n'.join(l for l in body if not l.startswith('【调用】'))
            if '（史诗' in title or '（传唱' in title:
                nm = re.sub(r'（.*', '', title).strip()
                if era['epic'] is None:
                    era['epic'] = epic_opening(body)
                    era['epic']['name'] = nm
                era['songs'].append(nm)
            elif '主线｜' in title:
                era['lines'].append(mainline(title, body))
            elif title.startswith('旅途同行：'):
                era['cast'].append(companion(title, body, cast))
            elif title.startswith('灾祸之兽｜') or title.startswith('魔兽｜') or title.startswith('领主｜'):
                era['beasts'].append(beast(title, body))
            elif title.endswith('（人物）'):
                era['meet'].append(person(title, body, cast))
            elif title.startswith('这一段的传奇表'):
                got = legends(body, cast)
                if '那一张表' in ''.join(body) and len(got) < len(running):     # 照前一页的表往下带，再添这一页新到的
                    have = {g['name'] for g in running}
                    got = [dict(g, old=True) for g in running] + [g for g in got if g['name'] not in have]
                era['legends'] = got
        seen, uniq = set(), []
        for c in era['cast']:          # 同一个人两条旅伴条（年轻时和后来）只留头一条
            if c['name'] not in seen:
                seen.add(c['name'])
                uniq.append(c)
        era['cast'] = uniq
        if not era['legends'] and pg['part'] == 2:
            era['legends'] = [dict(g, old=True) for g in running]
        running = [dict(g) for g in era['legends']]
        sort_roles(era)
        take_profiles(era, bgs, fate_all.get(era['id'], {}))
        era['places'] = places_of(main_text, table)
        if era['lines']:
            era['pian'] = era['lines'][0]['pian']
            era['pianDesc'] = era['lines'][0]['pianDesc']
        if not era['title']:
            era['title'] = era.get('pian', '')
        eras.append(era)
    return {'era': '月银纪', 'total': '一万零八十一年', 'parts': PARTS, 'eras': eras}


if __name__ == '__main__':
    data = build()
    if len(sys.argv) > 2 and sys.argv[1] == '--show':
        e = [x for x in data['eras'] if x['id'] == sys.argv[2]][0]
        print(json.dumps(e, ensure_ascii=False, indent=1))
        sys.exit(0)
    os.makedirs(os.path.join(HERE, 'data', 'prof'), exist_ok=True)
    js = json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n'
    open(os.path.join(HERE, 'data', 'moon.json'), 'w', encoding='utf-8', newline='\n').write(js)
    print('写了 data/moon.json', len(js), '字')
    tot = 0
    for eid, ps in PROFS.items():
        pj = json.dumps(ps, ensure_ascii=False, separators=(',', ':')) + '\n'
        open(os.path.join(HERE, 'data', 'prof', eid + '.json'), 'w', encoding='utf-8', newline='\n').write(pj)
        tot += len(pj)
    print('写了 data/prof/ 二十七份，', sum(len(v) for v in PROFS.values()), '人，', tot, '字')
    for e in data['eras']:
        nokey = [c['name'] for c in e['cast'] if not c['key']]
        print(e['id'], e['label'], e['title'], '｜ 主线', len(e['lines']), '旅伴', len(e['cast']), '相遇', len(e['meet']), '传奇', len(e['legends']), '兽', len(e['beasts']), '地', len(e['places']),
              ('｜ 没对上立绘：' + '、'.join(nokey)) if nokey else '', ('｜ 挪了：' + '、'.join('%s→%s(%s岁)' % m for m in e['moved'])) if e['moved'] else '')
        print('      旅伴', ' '.join('%s(%s)' % (c['name'], c.get('age')) for c in e['cast']))
        for l in e['lines']:
            if not (l['ti'] and l['open'] and l['acts'] and l['ending']):
                print('    缺', l['name'], {k: bool(l[k]) for k in ('ti', 'hooks', 'open', 'acts', 'ending')})
