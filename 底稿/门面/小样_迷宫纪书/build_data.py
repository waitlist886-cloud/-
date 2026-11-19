#!/usr/bin/env python3
# 迷宫纪的书（门面）的数据：迷宫纪前传六页，一页一圈；最外一圈是地开那一夜，最里一小圈是1001年今天。只搬运，不改字。
#   python -I -X utf8 build_data.py            写 data/maze.json 和 data/prof/q1..q6.json
#   python -I -X utf8 build_data.py --show q3  看一页抽出来的东西
# 借月银纪那一本（小样_月银纪书/build_data.py）的切条、主线、旅伴档案、地点，纷争纪那一本（小样_纷争纪书/build_data.py）的神名、显像、深层挡法，
# 山铜纪那一本（小样_山铜纪书/build_data.py）的人物条、传奇表的抽法。碑那一块换成委托，另添这一页的迷宫和冒险团。
# 只给 AI 的、NPC 不知道的、★、出处括号、照某某那一条一律不搬；体态只取身高，三维和罩杯不搬。
import glob
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
_OUTS = []         # 那两本的脚本一载入就各自把 stdout 换成 utf-8，换下来的那一个留着引用，免得回收时把底下的缓冲关掉


def _load(name, rel):
    _OUTS.append(sys.stdout)
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    _OUTS.append(sys.stdout)
    return m


MB = _load('moon_build', ('底稿', '门面', '小样_月银纪书', 'build_data.py'))
FB = _load('strife_build', ('底稿', '门面', '小样_纷争纪书', 'build_data.py'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
NUM = '一二三四五六'

# 六页：页名、起止年份（迷宫纪）
PAGES = [('探井的年月', 2, 100), ('共约的年月', 101, 317), ('繁荣的年月', 318, 599), ('深井的年月', 600, 849), ('黑潮的年月', 850, 970), ('垂暮的年月', 971, 1000)]
BASE = 22059          # 迷宫纪 Y 年是总的第 22059+Y 年（山铜纪 N 年是 21113+N，纷争纪 N 年是 10080+N，月银纪 Y 是 Y，月银纪前 N 年是 1-N）
SUPP = os.path.join(ROOT, '迷宫纪前传', '补卷')

# ---- 人物条 ----
NAME_FIX = {}         # 标题拆不准的那几条：标题开头 → (名字, 称谓, 说明)，照打出来的单子添
GROUP_GODS = {}
GROUP_KEEP = set()
SKIP_PEOPLE = set()
DROP_FIELD = {'声口', '只给 AI', '写法', '玩家在场', '碰得上', '命星', '本事', '这一页', '台词样例'}
GROUP_RX = re.compile(r'那几位|那几家|几位|[一二三四五六七八九十]位|那一路人|那一家|那一伙|那几个|那两位|七个人|的七神|一千零六|四十七')

# ---- 挡法（照山铜纪那一本）----
PAREN_REF = re.compile(r'（[^（）]*(?:照|见)[^（）]*那[一两三]?[条段块页张][^（）]*）|（(?:照|见)[^（）]*）|（#[^（）]*）')
REF_BG = re.compile(r'，?照[^，。“”]{1,12}那[一两]条的(?:背景|来路|样子)')
REF4 = re.compile(r'，?(?:往后的事)?(?:见|照)(?:人物|旅伴|主线|迷宫|案子|地点|公告板|规则|委托|冒险团|凡世至强|迷宫纪·|山铜纪·)[^，。“”]{0,40}?那[一两三]?[条段块张]')
EXTRA = re.compile(r'NPC|只给|不提前说|不写死|不写细|不解释|不裁定|叙述不|叙述只|这一层|裁定|玩家|AI|锁里')
BODY = re.compile(r'三维|三围|罩杯|[A-HＡ-Ｈ]杯|cup|\d+[／/]\d+')


def clause_drop(t, rx):
    out, cur, depth = [], '', 0
    for ch in t:
        cur += ch
        if ch == '“':
            depth += 1
        elif ch == '”':
            depth = max(0, depth - 1)
        if ch in '，。？' and depth == 0:
            out.append(cur)
            cur = ''
    if cur:
        out.append(cur)
    keep = [c for c in out if not rx.search(c)]
    s = ''.join(keep)
    s = re.sub(r'，(?=[。？]|$)', '。', s)
    if s and s[-1] == '，':
        s = s[:-1] + '。'
    return s.strip()


def scrub_str(v):
    v = PAREN_REF.sub('', v)
    v = REF_BG.sub('', v)
    v = REF4.sub('', v)
    v = FB.REF3.sub('', FB.HASH.sub('', FB.REF2.sub('', v)))
    v = re.sub(r'（[^（）]*★[^（）]*）', '', v).replace('★', '')
    if BODY.search(v):
        v = clause_drop(v, BODY)
    if EXTRA.search(v) or FB.DEEP.search(v):
        v = ''.join(s for s in MB.sentences(v) if not EXTRA.search(s) and not FB.DEEP.search(s)).strip()
    return v.replace('（）', '').strip()


RAW_KEYS = ('id', 'key', 'pset', 'kind', 'img', 'imgs', 'mural', 'edge', 'grade', 'name', 'title')     # 名字不过挡深层的那一道（第四十几层叫深层）


def scrub(v):
    if isinstance(v, str):
        return scrub_str(v)
    if isinstance(v, list):
        return [x for x in (scrub(x) for x in v) if x not in ('', None, [], {})]
    if isinstance(v, dict):
        return {k: scrub(x) if k not in RAW_KEYS else x for k, x in v.items()}
    return v


# ---- 小工具 ----
CN = {'零': 0, '〇': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
CNU = {'十': 10, '百': 100, '千': 1000, '万': 10000}


def cn2int(s):
    """汉字写的数（一万以内，三百一十八、二百零一、十九、一万一千八百七十二）。阿拉伯数字照转。"""
    if not s:
        return None
    if s.isdigit():
        return int(s)
    if s == '元':
        return 1
    total, sec, num = 0, 0, 0
    for ch in s:
        if ch in CN:
            num = CN[ch]
        elif ch in CNU:
            u = CNU[ch]
            if u == 10000:
                total += (sec + num) * u
                sec = num = 0
            else:
                sec += (num or 1) * u
                num = 0
        else:
            return None
    return total + sec + num


def page_file(i):
    return os.path.join(ROOT, '迷宫纪前传', '迷宫纪前传时段_%s_%s.md' % (NUM[i], PAGES[i][0]))


def read_lines(p):
    return open(p, encoding='utf-8').read().replace('\r\n', '\n').split('\n')


def born_abs(body):
    for l in body:
        if l.strip().startswith('固定锚定：'):
            m = re.search(r'生于(月银纪|纷争纪|山铜纪|迷宫纪)(前)?(元|\d+)年', l)
            if m:
                n = 1 if m.group(3) == '元' else int(m.group(3))
                if m.group(1) == '迷宫纪':
                    return BASE + n
                if m.group(1) == '山铜纪':
                    return 21113 + n
                if m.group(1) == '纷争纪':
                    return FB.BASE + n
                return (1 - n) if m.group(2) else n
    return None


def year_of(t):
    m = re.search(r'迷宫纪(约)?(元|\d+)年', t)
    if not m:
        return '', None
    n = 1 if m.group(2) == '元' else int(m.group(2))
    return ('约 ' if m.group(1) else '') + str(n), n


def page_of_year(y):
    for i, (_, a, b) in enumerate(PAGES):
        if a <= y <= b:
            return i
    return 0 if y < PAGES[0][1] else len(PAGES) - 1


ALLC = None


def all_cast():
    """前传的立绘资料（q*.json），带源稿文件和行号，同名的几条照行号挑。"""
    global ALLC
    if ALLC is None:
        ALLC = []
        for f in sorted(glob.glob(os.path.join(COMFY, 'cast', '前传', 'q*.json'))):
            for c in json.load(open(f, encoding='utf-8')):
                m = re.match(r'^(.*\.md):(\d+)$', c.get('src', ''))
                ALLC.append({'name': c.get('name', ''), 'en': c.get('en', ''), 'file': os.path.basename(m.group(1)) if m else '', 'line': int(m.group(2)) if m else 0})
    return ALLC


def page_no(fname):
    for i in range(len(PAGES)):
        if fname == os.path.basename(page_file(i)):
            return i
    return -1


def key_at(name, fname, line):
    short = name.split('·')[0]
    c = [x for x in all_cast() if x['name'] == name or x['name'].split('·')[0] == short or x['name'].split('（')[0] == name]
    c = [x for x in c if not x['en'].endswith('_child') or x['file'] == fname]
    if not c:
        return ''
    here = page_no(fname)

    def rank(x):
        if x['file'] == fname:
            return (0, abs(x['line'] - line))
        d = here - page_no(x['file'])
        return (1, d if d > 0 else 100 - d, 0)
    c.sort(key=rank)
    return c[0]['en']


def find_key(name, fname, line):
    k = key_at(name, fname, line)
    if k:
        return k, '前传'
    return MB.find_cast(name, ([], '前传'))


# ---- 委托 ----
EDGE = [('红边', 'red'), ('蓝边', 'blue'), ('白边', 'white')]


def commission(name, body, page_i):
    """委托单：单头拆成编号、日期、贴在哪、边色、等级、委托人、押；题、正面、背面、结案照搬。经过、知情、玩家碰得上、这一张以后是给模型看的，不搬。"""
    d = {'name': name, 'page': page_i}
    cur = None
    for l in body:
        s = l.rstrip()
        st = s.strip()
        if st.startswith('>') or st.startswith('### '):
            break
        m = re.match(r'^- (单头|题|正面|背面|结案|经过|知情|玩家碰得上|这一张以后)：(.*)$', st)
        if m and not s.startswith('  '):
            cur = m.group(1)
            d.setdefault(cur, [])
            if m.group(2):
                d[cur].append(m.group(2))
            continue
        if cur and s.startswith('  ') and st:
            d[cur].append(st)
    out = {'name': name, 'page': page_i}
    head = ''.join(d.get('单头', []))
    sents = [x.strip() for x in MB.sentences(head) if x.strip()]
    if sents:
        out['no'] = sents[0].split('，')[0].rstrip('。')
    ym = re.search(r'迷宫纪([〇零一二三四五六七八九十百千两]+|\d+)年', head)
    out['year'] = cn2int(ym.group(1)) if ym else None
    for s_ in sents[1:]:
        if s_.startswith('迷宫纪') and 'date' not in out:
            out['date'] = s_.rstrip('。')
        elif ('边' in s_[:4] or s_.startswith('没有边色')) and 'edgeText' not in out:
            out['edgeText'] = s_.rstrip('。')
        elif '委托人一栏' in s_ and 'client' not in out:
            out['client'] = s_.rstrip('。')
        elif ('委托等级' in s_ or '推荐旅印' in s_) and 'gradeText' not in out:
            out['gradeText'] = s_.rstrip('。')
        elif s_.startswith('押') and 'seal' not in out:
            out['seal'] = s_.rstrip('。')
        elif 'where' not in out and not s_.startswith('迷宫纪'):
            out['where'] = s_.rstrip('。')
    out['edge'] = next((v for k, v in EDGE if k in out.get('edgeText', '')), 'none')
    gm = re.search(r'委托等级\s*([SABCDE])', head)
    out['grade'] = gm.group(1) if gm else ''
    if d.get('题'):
        out['title'] = d['题'][0]
    out['front'] = d.get('正面', [])
    out['back'] = ''.join(d.get('背面', []))
    out['close'] = ''.join(d.get('结案', []))
    return out


# ---- 主线 ----
def mainline(title, body):
    l = MB.mainline(title, body)
    l['task'], l['chap'], l['chapName'], l['chapDesc'] = '', '', '', ''
    for x in body:
        s = x.strip()
        if s.startswith('题：'):
            parts = s[2:].split('｜')
            l['series'] = parts[0]
            l['chap'] = parts[1] if len(parts) > 2 else ''
            m = re.search(r'【([^】]+)】', parts[-1])
            l['task'] = m.group(1) if m else parts[-1]
            l['ti'] = s[2:]
        elif s.startswith('章：'):
            m = re.match(r'^《([^》]+)》｜(.*)$', s[2:])
            if m:
                l['chapName'], l['chapDesc'] = m.group(1), m.group(2)
    l['year'], l['_y'] = year_of(l['open'] or '')
    for k in ('pian', 'pianDesc'):
        l.pop(k, None)
    return l


# ---- 人物条（照山铜纪那一本）----
def fields(body):
    out = []
    for l in body:
        s = l.strip()
        if s.startswith('###') or s.startswith('>'):
            if s.startswith('### 裁定锁') or s.startswith('>'):
                break
            continue
        m = re.match(r'^- ([^：｜]{1,12})：(.*)$', s)
        if m and not l.startswith('  '):
            out.append([m.group(1), m.group(2)])
        elif s.startswith('- ') and l.startswith('  ') and out:
            out[-1][1] += s[2:]
    return out


PERSONISH = re.compile(r'\d+岁|岁|年生|生于|生在|人族|人类|矮人|精灵|半身人|提夫林|魔族|龙裔|半兽人|地精|巨魔|牛魔|轰狱|夜翼|炎角|白骸|深潮|梦魇|骨族|兽耳|[狐猫犬狼兔鹿熊]耳')
ROLE_WORDS = {'队长', '副手', '家长', '所长', '书记', '老人', '孩子', '是谁', '是什么', '往后', '来由'}
# 11-18：十三位升传奇里活到 1001 年的六位，各页人物条的小条标签是“传奇之名·名字”。门面上用本名（名号不抢在前头），带“的”的两个名号照样收。
BAR_ALIAS = {'负岭·蕾娃·升井': '蕾娃·升井', '下山的门·苏海拉': '苏海拉', '撑焰者·托芙·深井': '托芙·深井',
             '营心之钟·朵薇·六钟': '朵薇·六钟', '唤名之盾·肯特·墨鳞': '肯特·墨鳞', '队长的门·坎黛丝·焰沙': '坎黛丝·焰沙'}
BAR_SKIP = {'暮毒那家'}       # 一家人，不单拆出来，“净化圣所那一夜的几个人”照旧整条出
BAR_FORCE = {'营里'}          # 写的是第五十层前沿的营，字里没有族名，照旧收（fix_lists 给它改名）


def bar_people(body):
    """一群人那几条：“- 名｜内容”。前传的人物条里这种写法也拿来写别的（是什么、往后、两本账），只收看得出是人的那几行。"""
    got = {}
    for l in body:
        s = l.strip()
        if s.startswith('### 裁定锁') or s.startswith('>'):
            break
        m = re.match(r'^- ([^：｜]{1,16})｜(.*)$', s)
        if not m or m.group(1) in ROLE_WORDS:
            continue
        name, t = m.group(1), m.group(2)
        if name in BAR_SKIP:
            continue
        name = BAR_ALIAS.get(name, name)
        if name not in got and name not in BAR_FORCE and ('的' in name or not ('·' in name or len(name) <= 4) or not PERSONISH.search(t)):
            continue
        lm = re.match(r'^([^，。“”：、]{2,8})。(.+)$', t)
        lab, txt = (lm.group(1), lm.group(2)) if lm else ('是谁', t)
        got.setdefault(name, []).append((lab, txt))
    return got


def prof_from(items, veil=False, she=False):
    p = {'sec': [], 'lines': [], 'fate': ''}
    for h, t in items:
        if h in DROP_FIELD or t.strip().startswith('只给 AI') or t.strip().startswith('只给AI'):
            if h in ('台词', '台词样例'):
                p['lines'] += [q for q in (x.strip() for x in t.split('／')) if q]
            continue
        if h in ('台词',):
            p['lines'] += [q for q in (x.strip() for x in t.split('／')) if q]
            continue
        if veil:
            t = t.replace('祂', '她' if she else '他')
        if h == '底':
            if not veil:
                p['fate'] = MB.keep(re.sub(r'^正史里', '', t))
            continue
        t = MB.keep(t)
        if t:
            p['sec'].append({'h': {'位阶／兵器／出身': '位阶与出身'}.get(h, h), 't': t})
    p['lines'] = p['lines'][:6]
    return p


def parse_title(t):
    for k, v in NAME_FIX.items():
        if t.startswith(k):
            return v[0], v[1], v[2], False
    seg = t.split('，')
    grp = lambda n: bool(GROUP_RX.search(n))
    if len(seg) >= 3:
        name, tag, who = seg[-1], seg[0], '，'.join(seg[1:-1])
        if ('的' in name or len(name) > 8) and len(seg[1]) <= 6 and '的' not in seg[1]:
            name, who = seg[1], '，'.join([seg[-1]] + seg[2:-1])
        return name, tag, who, grp(name)
    if len(seg) == 2:
        a, b = seg
        if '的' not in b and len(b) <= 8 and not re.search(r'[、和那里]|以前|以后', b):
            return b, a, '', grp(b)
        head_, _, tail = b.rpartition('的')
        if tail and 2 <= len(tail) <= 12 and '那' not in tail and ('·' in tail or re.search(r'(?:氏|家|狱)$', head_)):
            return tail, a, head_, grp(tail)
        return a, '', b, grp(a)
    return t, '', '', grp(t)


def person(title, body, fname, line):
    t = title[:-len('（人物）')].strip()
    name, tag, who, group = parse_title(t)
    text = '\n'.join(body)
    veil = bool(MB.VEIL.search(text))
    she = bool(re.search(r'姑娘|妇人|女|婆|她', t))
    gs = FB.gods_in(t)
    key, pset = ('', '')
    if not group and not gs:
        key, pset = find_key(name, fname, line)
    for n, _ in gs:
        if n and FB.show_of(n):
            key, pset = FB.show_of(n), '神明显像'
            break
    bars = bar_people(body)
    items = fields(body)
    return {'name': name, 'tag': tag, 'who': who, 'key': key, 'pset': pset, 'group': group, 'gods': gs,
            'prof': prof_from(items, veil, she), 'bars': bars, 'title': t, 'line': line}


# ---- 传奇表里的近况（照山铜纪那一本）----
def legend_now(p8_body, shorts):
    on, out = False, {}
    ref = re.compile(r'，?(?:见|照)(?:人物|旅伴|各自|凡世至强)[^。]*?那[一两三]?条(?:人物)?(?:（★）)?')
    for l in p8_body:
        s = l.strip()
        if s.startswith('在世的'):
            on = True
            continue
        if not on or not s.startswith('- '):
            continue
        cur = []
        for sent in MB.sentences(ref.sub('', s[2:])):
            got = set()
            for cl in re.split(r'(?<=，)', sent):
                c = cl.strip()
                if not c:
                    continue
                hits = []
                for sh in shorts:
                    i = c.find(sh)
                    if i >= 0 and not any(sh in h for h, _ in hits):
                        hits.append((sh, i))
                hits.sort(key=lambda x: x[1])
                bare = c.rstrip('，。')
                if hits and re.fullmatch(r'[^，。、]{1,10}·' + re.escape(hits[0][0]) + r'(?:·[^，。、]{1,4})?', bare):
                    cur = []
                    continue
                if hits and hits[0][1] <= 12:
                    cur = [h for h, _ in hits] if '、' in c else [hits[0][0]]
                if not cur or EXTRA.search(c) or REF4.search(c) or '这一页' in c or re.search(r'照[^，。]*那[一两三]?条', c):
                    continue
                for k in cur:
                    out.setdefault(k, []).append(c)
                    got.add(k)
            for k in got:
                if not out[k][-1].endswith('。'):
                    out[k][-1] = out[k][-1].rstrip('，') + '。'
    res = {}
    for k, v in out.items():
        s = ''.join(v)
        s = re.sub(r'，$', '。', s)
        if not s.endswith('。'):
            s += '。'
        res[k] = s
    return res


def legend_died(p8_body, short, full, others):
    names = [full, short]
    dead = re.compile(r'死|没有下来|没有上来|没有出来|没回来|没有回来')
    nodeath = re.compile(r'没有死|没有殁|一位也没有|不死')
    bullets = [l.strip()[2:] for l in p8_body if l.strip().startswith('- ')]
    pool = bullets + [l.strip() for l in p8_body if l.strip() and not l.strip().startswith('- ')]

    def tidy(c):
        c = re.sub(r'^(殁于这一段的[一两三四五]位|殁[一两三四五]位|这一段)', '', c).strip('，')
        return c + '。'
    for s in pool:
        for sent in s.split('。'):
            for cl in sent.split('，'):
                if any(n in cl for n in names) and dead.search(cl) and not nodeath.search(cl):
                    return tidy(cl)
    for s in bullets:
        for sent in s.split('。'):
            cls = sent.split('，')
            for i, cl in enumerate(cls):
                if not any(n in cl for n in names):
                    continue
                for j in range(i + 1, min(i + 4, len(cls))):
                    if any(o in cls[j] for o in others) or nodeath.search(cls[j]):
                        break
                    if dead.search(cls[j]):
                        c = '，'.join(cls[i:j + 1])
                        if len(c) <= 90:
                            return tidy(c)
    return ''


# ---- 灾祸：史诗战的对手（底稿/立绘/史诗战名号/迷宫纪前传.md 对上 comfy/epic/prompts/maze.json）----
def bosses():
    md = read_lines(os.path.join(ROOT, '底稿', '立绘', '史诗战名号', '迷宫纪前传.md'))
    year_of_block, cur = {}, None
    for l in md:
        m = re.match(r'^### (P\d+)\s+(.+)$', l)
        if m:
            cur = m.group(1)
            continue
        if cur and l.startswith('- 对手：') and cur not in year_of_block:
            ys = [int(x) for x in re.findall(r'(\d+)年', l)]
            year_of_block[cur] = ys[0] if ys else None
    blocks = json.load(open(os.path.join(COMFY, 'epic', 'prompts', 'maze.json'), encoding='utf-8'))
    out, last_y = [], 2
    for b in blocks:
        code, _, short = b['block'].partition(' ')
        y = year_of_block.get(code) or last_y
        last_y = y
        keys = [p['key'] for p in b['phases'] if os.path.exists(os.path.join(COMFY, 'out', '史诗战', 'maze', p['key'] + '.png'))]
        out.append({'code': code, 'name': short.strip(), 'year': y, 'page': page_of_year(y), 'phases': [p.get('name', '') for p in b['phases']], 'imgs': keys,
                    'what': (b.get('design') or '')[:0]})
    return out


# ---- 这一页的迷宫和冒险团 ----
def supp_blocks():
    """补卷_71 到 _81：大型迷宫、各地的井、冒险团。回 [(标题, 行, 文件)]。"""
    out = []
    for f in sorted(glob.glob(os.path.join(SUPP, '补卷_*.md'))):
        n = int(re.match(r'补卷_(\d+)', os.path.basename(f)).group(1))
        if not (71 <= n <= 81):
            continue
        for title, body in MB.blocks(read_lines(f)):
            if title.startswith('迷宫纪·迷宫｜') or title.startswith('迷宫纪·冒险团｜'):
                out.append((title, body, os.path.basename(f)))
    return out


def what_of(body):
    """头一条“- **是什么。**”那一段，没有就取【调用】以后头一段话。"""
    for l in body:
        s = l.strip()
        m = re.match(r'^- \*\*是什么(?:（★）)?。\*\*\s*(.*)$', s)
        if m:
            return m.group(1)
    for l in body:
        s = l.strip()
        if s and not s.startswith('【调用】') and not s.startswith('>') and not s.startswith('#'):
            return re.sub(r'^- \*\*[^*]+\*\*\s*', '', s)
    return ''


def span_of(body):
    for l in body:
        if l.startswith('【调用】'):
            m = re.search(r'管约?(\d+)年到约?(\d+)年', l)
            if m:
                return int(m.group(1)), int(m.group(2))
    return None, None


def members_of(body):
    names, on = [], False
    for l in body:
        s = l.strip()
        if re.match(r'^- \*\*人', s):
            on = True
            continue
        if on and re.match(r'^- \*\*', s):
            on = False
        if on and l.startswith('  - '):
            m = re.match(r'^- ([^｜：]{1,14})｜', s)
            if m and not m.group(1).startswith('台词'):
                names.append(m.group(1))
    return names


def build():
    lp = os.path.join(HERE, 'legends.json')
    LEG = []
    if os.path.exists(lp):
        for x in json.load(open(lp, encoding='utf-8'))['legends']:
            LEG.append((x['short'], x['full'], x.get('title') or '', int(x['a']), int(x['b']), x.get('rose'), x.get('died')))
    leg_by_short = {x[0]: x for x in LEG}
    rows = read_lines(os.path.join(ROOT, '底稿', '地图', '地点谱', '迷宫纪前传.tsv'))
    keys = rows[0].split('\t')
    table = [dict(zip(keys, r.split('\t'))) for r in rows[1:] if r.strip()]
    fp = os.path.join(HERE, 'fate_table.json')
    fate_all = json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {}
    boss = bosses()
    supp = supp_blocks()
    report, eras, comms_all = [], [], []
    for pi, (pname, y0, y1) in enumerate(PAGES):
        fname = os.path.basename(page_file(pi))
        lines = read_lines(page_file(pi))
        heads = [n for n, l in enumerate(lines, 1) if l.startswith('## ')]
        bl = MB.blocks(lines)
        assert len(heads) == len(bl)
        e = {'id': 'q%d' % (pi + 1), 'no': pi + 1, 'title': pname, 'years': '%d — %d' % (y0, y1), 'y0': y0, 'y1': y1, 'set': '前传',
             'chap': '', 'chapName': '', 'chapDesc': '', 'comms': [], 'lines': [], 'cast': [], 'meet': [], 'legends': [], 'gods': [],
             'bosses': [], 'places': [], 'mazes': [], 'teams': []}
        text, bgs, people, p8, legend_blocks = '', {}, [], [], {}
        for (title, body), ln in zip(bl, heads):
            if title.startswith('迷宫纪·委托｜'):
                c = commission(title.split('｜', 1)[1].strip(), body, pi)
                e['comms'].append(c)
            elif '主线｜' in title:
                l = mainline(title, body)
                l['_text'] = '\n'.join(body)
                e['lines'].append(l)
                text += '\n'.join(x for x in body if not x.startswith('【调用】'))
            elif title.startswith('旅途同行·背景：'):
                nm = re.sub(r'（.*', '', title.split('：', 1)[1]).strip()
                bgs.setdefault(nm, MB.background(body))
            elif title == '这一段的传奇表':
                p8 = body
            elif title.startswith('凡世至强：'):
                legend_blocks[title.split('·')[-1].strip()] = body
            elif title.startswith('迷宫纪·迷宫｜'):
                nm = re.sub(r'（[^）]*）$', '', title.split('｜', 1)[1]).strip()
                e['mazes'].append({'name': nm, 'kind': '井里', 'what': what_of(body)})
        # 主线照这一页在任务单里的次序记壁画的键（a、b、c……），再照年份排
        for k, l in enumerate(e['lines']):
            l['mural'] = '%s_%s' % (e['id'], 'abcdefghijklmnopqrstuvwxyz'[k])
        e['lines'].sort(key=lambda l: (l['_y'] or 9999))
        by_seg = {l['name'].split('·', 1)[-1]: l for l in e['lines']}
        first_y = min((l['_y'] for l in e['lines'] if l['_y']), default=y0)
        shorts_here = [x[0] for x in LEG if x[3] <= pi + 1 <= x[4]]
        for (title, body), ln in zip(bl, heads):
            if title.startswith('旅途同行：'):
                c = MB.companion(title, body, ([], '前传'))
                seg = re.search(r'（迷宫纪·([^）]+)）', title)
                segs = [s.strip() for s in seg.group(1).split('、')] if seg else []
                c['key'], c['pset'] = find_key(c['name'], fname, ln)
                c['born'] = born_abs(body)
                hit = [by_seg[s] for s in segs if s in by_seg]
                if not hit and not any(s == pname for s in segs):
                    report.append('旅伴没有对上主线：%s %s' % (c['name'], segs))
                if not hit:
                    alias = [c['name'].split('·')[0]] + ([c['name'].split('·')[-1]] if '·' in c['name'] else [])
                    hit = [l for l in e['lines'] if any(a in l['_text'] for a in alias)][:1]
                y = min((l['_y'] for l in hit if l['_y']), default=first_y)
                c['seg'] = [s for s in segs if s in by_seg] or ([pname] if pname in segs else [])
                c['age'] = (BASE + y - c['born']) if c['born'] is not None else None
                e['cast'].append(c)
            elif title.endswith('（人物）'):
                t = title[:-len('（人物）')].strip()
                if t.split('，')[0] in SKIP_PEOPLE:
                    continue
                people.append(person(title, body, fname, ln))
        chaps = [(l['chap'], l['chapName'], l['chapDesc']) for l in e['lines'] if l['chap'] and '间' not in l['chap']]
        if not chaps:          # 垂暮的年月三条都在间章里
            chaps = [(l['chap'], l['chapName'], l['chapDesc']) for l in e['lines'] if l['chap']]
        if chaps:
            best = max(set(chaps), key=chaps.count)
            e['chap'], e['chapName'], e['chapDesc'] = best
        # 三类人
        old = {x[0] for x in LEG if x[3] < pi + 1 <= x[4]}
        new = {x[0] for x in LEG if x[3] == pi + 1}
        keep, grown, moved, seen = [], [], [], set()
        for c in e['cast']:
            short = c['name'].split('·')[0]
            if short in seen:
                continue
            seen.add(short)
            mortal = bool(re.match(r'^(人类|人族|半身人|兽耳|半兽人|狼耳|犬耳|狐耳|猫耳|兔耳|鹿耳)', c['race']))
            if short in old or (c.get('role') == '传奇' and any(g['name'].split('·')[0] == short for g in alive)):
                moved.append((c['name'], '传奇', c['age']))
                continue
            if c.get('role') == '相遇':        # 11-18 起照旅伴条里“类别”那一行（旅伴表定的），不再照年纪估
                grown.append({'name': c['name'], 'tag': '', 'who': c['who'], 'key': c['key'], 'pset': c['pset'], 'race': c['race'], 'age': c['age'], 'prof': c.get('prof')})
                moved.append((c['name'], '相遇', c['age']))
                continue
            keep.append(c)
        cast_short = {c['name'].split('·')[0] for c in keep} | {g['name'].split('·')[0] for g in grown}
        leg_prof, meets, gods = {}, [], []
        for p in people:
            short = p['name'].split('·')[0]
            if p['gods']:
                d = {k: p[k] for k in ('name', 'tag', 'who', 'key', 'pset')}
                d['prof'] = p['prof']
                d['side'] = '魔' if all(s == '魔' for _, s in p['gods']) else '正'
                gods.append(d)
                continue
            if p['bars']:
                for bn, items in p['bars'].items():
                    # “向长夜索春者·希尔妲”这种传奇之名打头的，认后头那个名字（照山铜纪那一本）
                    if '·' in bn and bn.split('·')[0] not in leg_by_short and bn.split('·', 1)[-1].split('·')[0] in leg_by_short:
                        bn = bn.split('·', 1)[-1]
                    bshort = bn.split('·')[0]
                    pr = prof_from(items)
                    if bshort in shorts_here and bshort not in cast_short:
                        leg_prof.setdefault(bshort, {'sec': [], 'lines': []})
                        leg_prof[bshort]['sec'] += pr['sec']
                        leg_prof[bshort]['lines'] += pr['lines']
                        continue
                    if bshort in cast_short:
                        continue
                    k2, ps2 = find_key(bn, fname, p['line'])
                    meets.append({'name': bn, 'tag': p['name'] if p['group'] else p['tag'], 'who': '', 'key': k2, 'pset': ps2, 'prof': pr})
                continue
            if short in shorts_here:
                if short in cast_short:
                    continue
                lp_ = leg_prof.setdefault(short, {'sec': [], 'lines': []})
                lp_['sec'] = p['prof']['sec'] + lp_['sec']
                lp_['lines'] = p['prof']['lines'] + lp_['lines']
                if p['tag']:
                    lp_['tag'] = p['tag']
                continue
            if short in cast_short:
                continue
            meets.append({k: p[k] for k in ('name', 'tag', 'who', 'key', 'pset', 'prof')})
        # 凡世至强那一条（守井人、阶顶的燧石、无灯之凿）：照栏目收进传奇的档案
        for nm, body in legend_blocks.items():
            short = nm.split('·')[0]
            if short in leg_by_short and short not in cast_short:
                pr = prof_from(fields(body))
                lp_ = leg_prof.setdefault(short, {'sec': [], 'lines': []})
                lp_['sec'] = lp_['sec'] + pr['sec']
                lp_['lines'] = lp_['lines'] + pr['lines']
        # 传奇
        p8_shorts = [x[0] for x in LEG] + [x[1] for x in LEG]
        now = legend_now(p8, sorted(set(p8_shorts), key=len, reverse=True))
        lg = []
        for x in LEG:
            short, full, ttl, a, b, ny, dy = x
            if not (a <= pi + 1 <= b) or short in cast_short:
                continue
            key, pset = find_key(full, fname, len(lines))
            g = {'name': full, 'title': ttl, 'key': key, 'pset': pset}
            if dy and page_of_year(int(dy)) == pi:
                g['end'] = '殁于这一段'
            if a == pi + 1 and ny:
                g['new'] = 1
            lg.append((g, short, full, ny, dy))
        e['legends'] = [g for g, *_ in lg]
        e['cast'] = keep
        e['meet'] = grown + meets
        e['gods'] = gods
        e['moved'] = moved
        for c in e['cast']:
            c.pop('born', None)
            c.pop('role', None)
        MB.take_profiles(e, bgs, fate_all.get(e['id'], {}))
        for g in e['gods']:
            pr = g.pop('prof', None)
            if pr and (pr.get('sec') or pr.get('fate')):
                pr['kind'] = 'god'
                if g.get('tag'):
                    pr['tag'] = g['tag']
                MB.PROFS[e['id']][g['name']] = {k: v for k, v in pr.items() if v not in ('', [], None, False)}
                g['p'] = 1
        others = [x[0] for x in LEG]
        for g, short, full, ny, dy in lg:
            lp_ = leg_prof.get(short, {})
            nw = now.get(short) or now.get(full, '')
            if re.search(r'死了|没了|死在|就死', nw):
                nw = ''
            pr = {'kind': 'legend', 'tag': g['title'] or lp_.get('tag', ''), 'now': nw,
                  'sec': lp_.get('sec', []), 'lines': lp_.get('lines', [])[:6]}
            if ny and g.get('new'):
                pr['rose'] = '约 %d 年踏进传奇' % int(ny)
            if g.get('end'):
                pr['died'] = legend_died(p8, short, full, [o for o in others if o != short])
            if not (pr['now'] or pr['sec'] or pr.get('died')):
                report.append('传奇没有档案：%s %s' % (e['id'], full))
                continue
            MB.PROFS[e['id']][full] = {k: v for k, v in pr.items() if v not in ('', [], None, False)}
            g['p'] = 1
        # 灾祸
        e['bosses'] = [{k: v for k, v in b.items() if k not in ('page', 'what')} for b in boss if b['page'] == pi]
        # 补卷里的大型迷宫、各地的井、冒险团：照【调用】管的头一年落到页上
        for title, body, f in supp:
            a, b = span_of(body)
            if a is None:
                report.append('补卷条目没读到年份：%s %s' % (f, title))
                continue
            if page_of_year(a) != pi:
                continue
            nm = title.split('｜', 1)[1].strip()
            if title.startswith('迷宫纪·冒险团｜'):
                e['teams'].append({'name': nm, 'y0': a, 'what': what_of(body), 'who': members_of(body)})
            else:
                e['mazes'].append({'name': nm, 'kind': '各地' if nm.startswith('各地的井') else '大型', 'y0': a, 'what': what_of(body)})
        e['places'] = MB.places_of(text, table)
        for pl in e['places']:
            if '；' in pl['where']:
                pl['where'] = pl['where'].split('；')[0].rstrip('，') + '。'
        for l in e['lines']:
            l.pop('_y', None)
            l.pop('_text', None)
        eras.append(e)
        comms_all += e['comms']
    # 最外一圈：地开那一夜
    rim = {'title': '地开那一夜', 'years': '山铜纪947年归寂月最后一夜', 'mural': 'q0_a', 'desc': ''}
    for l in read_lines(os.path.join(SUPP, '第一项_常驻与纪元钟.md')):
        s = l.strip()
        if s.startswith('- 元年归寂月最后一夜'):
            rim['desc'] = s[2:]
            break
    data = {'era': '迷宫纪', 'total': '一千年', 'series': '奥尔德兰的旅印｜中部', 'eras': eras, 'rim': rim,
            'end': {'title': '迷宫纪 1001 年', 'line': '绳到了头，底下有她接着。'}}
    return scrub(data), report


if __name__ == '__main__':
    data, report = build()
    if len(sys.argv) > 2 and sys.argv[1] == '--show':
        e = [x for x in data['eras'] if x['id'] == sys.argv[2]][0]
        print(json.dumps(e, ensure_ascii=False, indent=1)[:20000])
        print(json.dumps(scrub(MB.PROFS.get(sys.argv[2], {})), ensure_ascii=False, indent=1)[:8000])
        sys.exit(0)
    os.makedirs(os.path.join(HERE, 'data', 'prof'), exist_ok=True)
    js = json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n'
    open(os.path.join(HERE, 'data', 'maze.json'), 'w', encoding='utf-8', newline='\n').write(js)
    print('写了 data/maze.json', len(js), '字')
    tot = 0
    for eid, ps in MB.PROFS.items():
        pj = json.dumps(scrub(ps), ensure_ascii=False, separators=(',', ':')) + '\n'
        open(os.path.join(HERE, 'data', 'prof', eid + '.json'), 'w', encoding='utf-8', newline='\n').write(pj)
        tot += len(pj)
    print('写了 data/prof/', len(MB.PROFS), '份，', sum(len(v) for v in MB.PROFS.values()), '人，', tot, '字')
    for e in data['eras']:
        print(e['id'], e['title'], e['years'], '｜', e['chap'], e['chapName'], '｜ 委托', len(e['comms']), '主线', len(e['lines']), '旅伴', len(e['cast']), '相遇', len(e['meet']),
              '传奇', len(e['legends']), '神', len(e['gods']), '灾祸', len(e['bosses']), '迷宫', len(e['mazes']), '冒险团', len(e['teams']), '地', len(e['places']))
        print('      委托', ' '.join('%s(%s,%s,%s)' % (c.get('no', ''), c.get('year'), c.get('edge'), c.get('grade') or '-') for c in e['comms']))
        print('      主线', ' ／ '.join('%s【%s】(%s,%s)' % (l['name'].split('·', 1)[-1], l.get('task', ''), l['year'], l.get('mural')) for l in e['lines']))
        print('      旅伴', ' '.join('%s(%s,%s)' % (c['name'], c.get('age'), c.get('key') or '无图') for c in e['cast']))
        print('      相遇', ' '.join('%s(%s)' % (c['name'], c.get('key') or '无图') for c in e['meet'])[:600])
        print('      传奇', ' '.join('%s(%s%s)' % (c['name'], c.get('key') or '无图', '' if c.get('p') else '，无档') for c in e['legends']))
        print('      灾祸', ' '.join('%s(%s)' % (b['name'], b['year']) for b in e['bosses']))
        print('      迷宫', ' '.join('%s[%s]' % (m['name'], m['kind']) for m in e['mazes']))
        print('      冒险团', ' '.join('%s(%s)' % (t['name'], t['y0']) for t in e['teams']))
        for l in e['lines']:
            if not (l.get('task') and l['open'] and l['acts']):
                print('    缺', l['name'], {k: bool(l.get(k)) for k in ('task', 'hooks', 'open', 'acts', 'ending')})
    for r in report:
        print('！', r)
