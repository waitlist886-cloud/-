#!/usr/bin/env python3
# 山铜纪的书（门面）的数据：六个时代（山铜纪六页），一页一章。只搬运，不改字。
#   python -I -X utf8 build_data.py            写 data/bronze.json 和 data/prof/p1..p6.json
#   python -I -X utf8 build_data.py --show p3  看一页抽出来的东西
# 借月银纪那一本（小样_月银纪书/build_data.py）的切条、主线、旅伴档案、地点，和纷争纪那一本（小样_纷争纪书/build_data.py）的神名、显像、深层挡法。
# 只给 AI 的、NPC 不知道的、★、出处括号、照某某那一条一律不搬；体态只取身高，三维和罩杯不搬。
import glob
import importlib.util
import io
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

# 六页：页名、起止年份（山铜纪）
PAGES = [('犁的年月', 2, 300), ('长夜的年月', 301, 579), ('白鸦的年月', 580, 660), ('黎明的年月', 661, 741), ('七城的年月', 742, 861), ('麦的年月', 862, 947)]
BASE = 21113          # 山铜纪 Y 年是总的第 21113+Y 年（纷争纪 N 年是 10080+N，月银纪 Y 是 Y，月银纪前 N 年是 1-N）

# ---- 碑 ----
# 碑立在墙哪一边（照“碑：”那一行的地点认，规矩照门面重做_方向稿第二十七节）：事出在墙西的立墙北（west），事出在墙东的立墙南（east），出在墙上、两边都有份的立墙脚（wall）
SIDE = {
    '雨城清查': 'wall', '机兵化犁': 'east', '盐路赎身': 'west', '归林': 'wall',
    '九年之路': 'east', '扶剑礼': 'east', '炭巷': 'east', '灰旗': 'west', '河心三日': 'west', '南沼停火': 'wall',
    '换俘碑': 'wall', '废弃水闸': 'wall', '红水': 'east', '喂山': 'east', '白母': 'east', '赤盐边镇': 'west',
    '灰雨城之乱': 'wall', '灰雨之夜': 'wall', '黎明篡位': 'east', '十四家之乱': 'east', '白杉堡': 'west', '碎碑矿坑': 'west',
    '苍焰角城': 'west', '血棘红园': 'west', '骸钟墓城': 'west', '无名碑林': 'west', '魇镜幻都': 'west', '黑翼天塔': 'west', '雷暴荒地': 'west', '最后一尊': 'west', '深潮蓝堡': 'west',
    '第一条': 'west', '界碑': 'wall', '烧麦': 'wall', '献祭台': 'west', '不灭王炉': 'east',
    '旁听': 'east', '三条长凳': 'east', '门楣': 'east', '分潮': 'east', '开岭': 'east', '曜石': 'east', '门与粮': 'east',      # 11-14 墙东补的七块
    '无字碑': 'wall',
}
SIDE_WHY = {      # 认不准的那几块怎么定的（写进 data，check_data 和交回来的话用）
    '雨城清查': '灰雨城在墙脚下，两边的人都住',
    '南沼停火': '南沼在长垒南段尽头往南，墙修到那里就没有了，两族在那里',
    '废弃水闸': '水闸在堰口段城西墙脚下，墙上的事',
    '赤盐边镇': '纷争纪联军的营垒，在长垒南段的墙外',
    '白杉堡': '在长垒南段墙外的西麓',
    '烧麦': '在射界里，界碑往南两步，两边的麦',
}
MAT = [('朝东那一面是', 'boundary'), ('黑曜石', 'obsidian'), ('一块白石', 'white'), ('白石', 'white'), ('一块河石', 'stone'), ('一块旧门石', 'stone'), ('一块劈下来的石头', 'stone'), ('山铜', 'bronze')]
AROUND = re.compile(r'插着|挂着|挂满|压着|码着|堆着|盘着|钉着|点着|碑脚|碑旁|碑顶|磨得像镜子|碑朝|四周|木架|石碗|台基|七百级|门洞顶上')
WHO_STRONG = re.compile(r'刻碑的是|立的|合立|凿的|铸的|铸在|嵌进|请碑匠|碑匠没有刻|刻上去|刻了这几句|刻出来|刻的头一块')
WHO = re.compile(r'立|刻|凿|铸|嵌|碑匠')
# 灰雨城之乱是灰雨之夜那一块碑 661 年冬到 668 年的样子（661 年冬南线铸了那一面，669 年开春新朝磨平重刻），
# 主会话 11-14 定的：长卷和时代页只立灰雨之夜一块，旧的那一面写进它的说明
MERGE = {'灰雨城之乱': '灰雨之夜'}
ART_KEY = {}      # 碑的图键：照 stele_forms.json 的固定表（comfy/gpt_cg3.py 的 MONS，m01..m43），灰雨城之乱是页上才有的，没有图
# 11-14 碑照事件做成不同的样子（墙东补叙与碑形），一块碑一行：图键、形制、大小档、横竖。原来照碑第一版的次序排 b01..b36，添了碑次序就错位，改成固定的表
FORMS = {k: v for k, v in json.load(open(os.path.join(HERE, 'stele_forms.json'), encoding='utf-8')).items() if not k.startswith('_')}


# ---- 传奇 ----
# 照各页 p8_legends 那一张表排的（手排，★ 那几位照表上的“地方上凝名的”算）：简名、全名、传奇之名、在哪几页（a 到 b，山铜纪以前就是传奇的 a 写 0）、哪一年踏进传奇、殁年（不在这六页里死的写 None）
LEG = [
    ('希尔妲', '希尔妲', '向长夜索春者', 0, 6, None, None),
    ('霍布', '霍布', '饥馑之敌', 0, 6, None, None),
    ('凯恩', '凯恩', '含雷者', 0, 6, None, None),
    ('珀拉', '珀拉', '沉城之喉', 0, 6, None, None),
    ('卡兰缇娅', '卡兰缇娅', '林冠的守夜人', 0, 6, None, None),
    ('艾瑟莉娅', '艾瑟莉娅·维洛恩', '月桂贤王', 0, 6, None, None),
    ('岑瓦', '岑瓦', '无献之晨', 0, 6, None, None),
    ('芙莉莲', '芙莉莲·银露', '千年葬星', 0, 6, None, None),
    ('辛美尔', '辛美尔', '勇者', 0, 1, None, 12),
    ('海塔', '海塔', '醉烛', 0, 1, None, 7),
    ('艾冯', '艾冯', '三响', 0, 1, None, 31),
    ('埃斐林', '埃斐林·晨栎', '唤班者', 1, 6, 238, None),
    ('妲蕾格', '妲蕾格·铁灰鳞', '系冰', 1, 6, 270, None),
    ('索伦德', '索伦德', '领路的', 2, 2, 320, 330),
    ('盖尔蒙', '盖尔蒙', '压山之枪', 2, 2, 365, 371),
    ('英薇', '英薇·桦火', '雪里的春线', 2, 2, 395, 405),
    ('瑟涅', '瑟涅·盐汲', '咸水之门', 2, 4, 420, 661),
    ('约尔贡', '约尔贡', '凛塔家的弟弟', 2, 2, 425, 425),
    ('石楠', '石楠', '炭巷的大姐', 2, 2, 450, 450),
    ('绮洛', '绮洛', '托天之翼', 2, 2, 465, 470),
    ('达乌德', '达乌德', '灰旗', 2, 2, 470, 470),
    ('伊洛温', '伊洛温', '口子里的林', 3, 6, 600, None),
    ('柯斯瑟', '柯斯瑟', '两圈之间', 3, 4, 610, 671),
    ('薇丝塔', '薇丝塔', '', 3, 4, 637, 661),
    ('朵娜', '朵娜·芦沟', '拾枪', 4, 4, 665, 670),
    ('索恩薇娅', '索恩薇娅·里德', '黎明之剑', 4, 6, 668, None),
    ('瓦尔德拉克', '瓦尔德拉克·烬角', '军锋', 5, 6, 742, None),
    ('莉西娅', '莉西娅·血棘', '血棘', 5, 6, 758, None),
    ('芭鲁娜', '芭鲁娜', '桥下的手', 5, 6, 770, None),
    ('赛勒斐恩', '赛勒斐恩·夜翼', '夜翼', 5, 6, 824, None),
    ('莫尔图斯', '莫尔图斯·骨钟', '骨钟', 5, 6, 845, None),
    ('格罗姆', '格罗姆·伏雷', '伏雷', 5, 6, 847, None),
    ('涅芙拉', '涅芙拉·梦镜', '梦镜', 5, 6, 850, None),
    ('妲薇', '妲薇', '带书的人', 5, 5, 853, 861),
    ('赛壬缇娅', '赛壬缇娅·潮誓', '潮誓', 5, 6, 861, None),
    ('妮洛丝', '妮洛丝', '人堤', 5, 5, 861, 861),
    ('葵丝', '葵丝·刻雪', '胸甲碑', 6, 6, 887, None),
    ('格拉德', '格拉德·灰拳', '血誓余烬', 6, 6, 926, None),
    ('冈娜', '冈娜·炉脉', '合缝之锤', 6, 6, 934, None),
    ('布洛姆加', '布洛姆加·炉脉', '不灭锻王', 6, 6, 934, None),
    ('扎希尔', '扎希尔', '角尽', 6, 6, 935, None),
    ('哈格勒', '哈格勒·枷匠', '钩锁', 6, 6, 940, None),
]
LEG_SRC = {'那一本书的最后一任抄手': '妲薇'}       # 人物条标题里没写名字、写的是传奇本人的
LEG_KEY = {}                                        # 传奇的立绘键另指的（暂无）

# ---- 人物条 ----
# 标题拆不准的那几条：标题开头 → (名字, 称谓, 说明)
NAME_FIX = {
    '墙那边那座营的营主': ('铎尔坎', '墙那边那座营的营主', '轰狱'),
    '吹号角的那个人': ('洛伦茨·布莱泽', '吹号角的那个人', '堰口段城的老号手'),
    '赎罪军里头一批的那一个': ('纳迪尔', '赎罪军里头一批的那一个', '当过收血人的熔环氏'),
    '角城试火的努尔': ('努尔', '角城试火的', ''),
    '红炉段城的约伦': ('约伦·无炉', '红炉段城的约伦', ''),
    '炉脉的老家长兰维格': ('兰维格', '炉脉的老家长', '和王城里没有上来的那一百一十七个'),
    '压山之枪，盖尔蒙': ('盖尔蒙', '压山之枪', '往北扔了兵器的王的长枪手'),
    '灰旗，达乌德': ('达乌德', '灰旗', '连下三城、一个人在山口迎的那一个'),
}
GROUP_GODS = {'灰雨以后的七神': '正', '七城的年月里的七神': '正', '麦的年月里的七神': '正', '高座之主': '魔'}
GROUP_KEEP = {'灰雨魔女看着长大的那几个孩子'}        # 竖线写着一个一个人、可是整条讲的是一群孩子的，照一条留着
SKIP_PEOPLE = {'白母'}                               # 是兽，灾祸那一栏里有它
DROP_FIELD = {'声口', '只给 AI', '写法', '玩家在场', '碰得上', '命星', '本事', '交出去的东西', '交出去的七份', '身上的两份', '表层', '维拉瑟', '这一页'}
GROUP_RX = re.compile(r'那几位|那几家|几位|[一二三四五六七八九十]位|十四家|十二家|那一路人|那一家|那一伙|那几个|那两位|三千个人|十一个人|的七神|七个人')

# ---- 挡法 ----
PAREN_REF = re.compile(r'（[^（）]*(?:照|见)[^（）]*那[一两三]?[条段块页][^（）]*）|（(?:照|见)[^（）]*）|（#[^（）]*）')
REF_BG = re.compile(r'，?照[^，。“”]{1,12}那[一两]条的(?:背景|来路|样子)')
REF4 = re.compile(r'，?(?:往后的事)?(?:见|照)(?:人物|旅伴|主线|遗迹|案子|号墙|规则|山铜纪·)[^，。“”]{0,40}?那[一两三]?[条段块]')
EXTRA = re.compile(r'NPC|只给|不提前说|不写死|不写细|不解释|不裁定|叙述不|叙述只|这一层|裁定|玩家|AI|锁里')
BODY = re.compile(r'三维|三围|罩杯|[A-HＡ-Ｈ]杯|cup|\d+[／/]\d+')


def clause_drop(t, rx):
    """按逗号和句号切成小句，带 rx 的小句拿掉（引号里的不切）。"""
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


def scrub(v):
    if isinstance(v, str):
        return scrub_str(v)
    if isinstance(v, list):
        return [x for x in (scrub(x) for x in v) if x not in ('', None, [], {})]
    if isinstance(v, dict):
        return {k: scrub(x) if k not in ('id', 'key', 'pset', 'side', 'kind', 'img', 'imgs') else x for k, x in v.items()}
    return v


# ---- 小工具 ----
def page_file(i):
    return os.path.join(ROOT, '山铜纪', '山铜纪时段_%s_%s.md' % (NUM[i], PAGES[i][0]))


def read_lines(p):
    return open(p, encoding='utf-8').read().replace('\r\n', '\n').split('\n')


def born_abs(body):
    for l in body:
        if l.strip().startswith('固定锚定：'):
            m = re.search(r'生于(月银纪|纷争纪|山铜纪)(前)?(元|\d+)年', l)
            if m:
                n = 1 if m.group(3) == '元' else int(m.group(3))
                if m.group(1) == '山铜纪':
                    return BASE + n
                if m.group(1) == '纷争纪':
                    return FB.BASE + n
                return (1 - n) if m.group(2) else n
    return None


def year_of(t):
    m = re.search(r'山铜纪(约)?(元|\d+)年', t)
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
    """山铜纪的立绘资料（s*.json），带源稿文件和行号，同名的几条照行号挑。"""
    global ALLC
    if ALLC is None:
        ALLC = []
        for f in sorted(glob.glob(os.path.join(COMFY, 'cast', '山铜纪', 's*.json'))):
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
    """同名的几条（年轻时和后来）：同一页照行号挑最近的；别的页先挑这一页以前、离这一页最近的那一页（长到这个年纪的样子）。"""
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
    """先在山铜纪的资料里照行号找，找不到再到别的纪找（活过几纪的人画在别的纪的文件夹里）。"""
    k = key_at(name, fname, line)
    if k:
        return k, '山铜纪'
    return MB.find_cast(name, ([], '山铜纪'))


def has_art(key, pset):
    if not key:
        return False
    if pset == '神明显像':
        return os.path.exists(os.path.join(COMFY, 'out', '神明显像', key + '.png'))
    d = {'1001': '立绘_v3'}.get(pset, '立绘_' + pset)
    return os.path.exists(os.path.join(COMFY, 'out', d, 'art', 'art_' + key + '.webp'))


# ---- 碑 ----
def stele_blocks(lines):
    out = []
    for title, body in MB.blocks(lines):
        if '·碑｜' in title:
            out.append((title.split('｜', 1)[1].strip(), body))
    return out


def split_bei(line):
    """“碑：”那一行拆成在哪、什么做的、谁立的谁刻的、四周有什么。"""
    t = re.sub(r'（[^（）]*★[^（）]*）', '', line).replace('★', '').strip()
    kind, mat, where, rest = 'bronze', '', t, ''
    if '朝东那一面是' in t:
        i = t.index('朝东那一面是')
        where = t[:i].rstrip('，。')
        j = t.find('。', i)
        mat, rest, kind = t[i:j], t[j + 1:], 'boundary'
    else:
        best = None
        for word, k in MAT:
            m = re.search('[，。]' + word + '[，。]', t)
            if m and (best is None or m.start() < best[0].start()):
                best = (m, word, k)
        if best:
            m, word, kind = best
            where, mat, rest = t[:m.start()], word, t[m.end():]
    who, around, more = [], [], []
    for s in MB.sentences(rest):
        s = s.strip().lstrip('，')
        if not s:
            continue
        if WHO_STRONG.search(s):
            who.append(s)
        elif AROUND.search(s):
            around.append(s)
        elif WHO.search(s):
            who.append(s)
        else:
            more.append(s)
    where = where.strip('，。') + ('。' if where else '')
    if more:
        where += ''.join(more)
    return kind, mat, where, ''.join(who), ''.join(around)


def stele(name, body, page_i):
    d = {'name': name, 'side': SIDE.get(name, 'wall')}
    call = ''
    for l in body:
        s = l.strip()
        if s.startswith('【调用】'):
            call = s
        elif s.startswith('- 碑：'):
            d['kind'], d['material'], d['where'], d['who'], d['around'] = split_bei(s[4:])
        elif s.startswith('- 正面：'):
            d['front'] = s[5:]
        elif s.startswith('- 背面：'):
            d['back'] = s[5:]
        elif s.startswith('- 朝东那一面：'):
            d['front'] = s[len('- 朝东那一面：'):]
            d['frontLabel'] = '朝东那一面'
        elif s.startswith('- 朝西那一面：'):
            d['back'] = s[len('- 朝西那一面：'):]
            d['backLabel'] = '朝西那一面'
        elif s.startswith('- 两侧：'):
            d['sides'] = s[5:]
    m = re.search(r'山铜纪(\d+)年', call)
    d['year'] = int(m.group(1)) if m else PAGES[page_i][1]
    erased = re.search(r'(\d+年开春这一面磨掉了)', call)
    if erased:
        d['erased'] = erased.group(1)
    d['page'] = page_i
    f = FORMS.get(name)
    if f:
        d['form'], d['size'], d['o'] = f['form'], f['size'], f['o']
    if name in SIDE_WHY:
        d['why'] = SIDE_WHY[name]
    return d


def face_lines(text, name):
    """碑面那一段：头一句是正名的照留成标题，往下一句一行。回 (有没有正名, [行])。"""
    ss = [x.strip() for x in MB.sentences(text) if x.strip()]
    if ss and ss[0].rstrip('。') == name:
        return True, ss[1:]
    return False, ss


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


# ---- 人物条 ----
def fields(body):
    """“- 标签：内容”一行一栏，下一层的小条接在上一栏后头。"""
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


def bar_people(body):
    """一群人那几条：“- 名｜内容”。回 {名: [(标签, 内容)]}，名字照第一回出现的次序。"""
    got = {}
    for l in body:
        s = l.strip()
        if s.startswith('### 裁定锁') or s.startswith('>'):
            break
        m = re.match(r'^- ([^：｜]{1,16})｜(.*)$', s)
        if not m or m.group(1) == '来由':
            continue
        name, t = m.group(1), m.group(2)
        lm = re.match(r'^([^，。“”：、]{2,8})。(.+)$', t)
        lab, txt = (lm.group(1), lm.group(2)) if lm else ('是谁', t)
        got.setdefault(name, []).append((lab, txt))
    return got


def quotes_of(t):
    return [q for q in re.findall(r'“[^“”]{2,80}”', t)][:6]


def prof_from(items, veil=False, she=False):
    """[(标签, 内容)] 照档案页的样子收：声口、只给 AI 那几栏不搬，台词那一栏拆成说过的话。"""
    p = {'sec': [], 'lines': [], 'fate': ''}
    for h, t in items:
        if h in DROP_FIELD or t.strip().startswith('只给 AI') or t.strip().startswith('只给AI'):
            continue
        if h in ('台词', '台词样例'):
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
    """人物条标题：回 (名字, 称谓, 说明, 是不是一群人)。"""
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


def person(title, body, fname, line, legend_short):
    t = title[:-len('（人物）')].strip()
    name, tag, who, group = parse_title(t)
    text = '\n'.join(body)
    veil = bool(MB.VEIL.search(text))
    she = bool(re.search(r'姑娘|妇人|女|婆|她', t))
    gs = FB.gods_in(t)
    if not gs and name in GROUP_GODS:
        gs = [('', GROUP_GODS[name])]
    key, pset = ('', '')
    if not group and not gs:
        key, pset = find_key(name, fname, line)
    for n, _ in gs:
        if n and FB.show_of(n):
            key, pset = FB.show_of(n), '神明显像'
            break
    bars = bar_people(body)
    if t in GROUP_KEEP:
        items = [(h, x) for h, x in fields(body)] + [(n, '，'.join(x for _, x in v)) for n, v in bars.items()]
        bars = {}
    else:
        items = fields(body)
    return {'name': name, 'tag': tag, 'who': who, 'key': key, 'pset': pset, 'group': group, 'gods': gs,
            'prof': prof_from(items, veil, she), 'bars': bars, 'title': t, 'line': line}


# ---- 传奇表里的近况 ----
def legend_now(p8_body, shorts):
    """“在世的传奇”那几行：按小句分给句头上的那一位（一个小句里用顿号排了几位的，往下的话归那几位）。回 {简名: 文字}。"""
    on, out = False, {}
    ref = re.compile(r'，?(?:见|照)(?:人物|旅伴|各自)[^。]*?那[一两三]?条(?:人物)?(?:（★）)?')
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
                    cur = []          # 名单里的一项（名号·名字），不算话
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


def legend_died(p8_body, short, full):
    """殁于这一段的那一位：传奇表里写他死的那一小句。先找分段那几行里名字和死在同一个小句的，再放宽到隔几个小句。"""
    names = [full, short]
    dead = re.compile(r'死|没有下来|没有上来|没有出来')
    nodeath = re.compile(r'没有死|没有殁|一位也没有|不死')
    others = [x[0] for x in LEG if x[0] != short]
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


# ---- 灾祸 ----
def bosses():
    """史诗战的对手：总表（底稿/立绘/史诗战名号/山铜纪.md）对上 comfy/epic/prompts/bronze.json 的图，照年份落到页上。"""
    rows = []
    md = read_lines(os.path.join(ROOT, '底稿', '立绘', '史诗战名号', '山铜纪.md'))
    sec = ''
    for l in md:
        if l.startswith('## '):
            sec = l
        if '总表' in sec and re.match(r'^\| B\d+隐? \|', l):
            cells = [x.strip() for x in l.strip().strip('|').split('|')]
            rows.append((cells + [''] * 6)[:6])
    body_of, cur = {}, None
    for l in md:
        mm = re.match(r'^### (B\d+)', l)
        if mm:
            cur = mm.group(1)
        elif cur and l.startswith('- 本体：') and cur not in body_of:
            body_of[cur] = l
    blocks = json.load(open(os.path.join(COMFY, 'epic', 'prompts', 'bronze.json'), encoding='utf-8'))
    assert len(blocks) == len(rows), (len(blocks), len(rows))
    out, last_y = [], 2
    for r, b in zip(rows, blocks):
        code, what, short = r[0], r[1], r[2]
        phases = [x.strip('【】') for x in r[3:] if x]
        m = re.search(r'（([^）]*)）', what)
        y = None
        if m:
            nm = re.search(r'(\d+)', m.group(1))
            y = int(nm.group(1)) if nm else None
        if y is None and code.endswith('隐'):
            y = last_y
        if y is None:
            pm = re.search(r'P(\d):', body_of.get(code, ''))
            pi = int(pm.group(1)) - 1 if pm else 0
            y = PAGES[pi][1]
        last_y = y
        keys = [p['key'] for p in b['phases'] if os.path.exists(os.path.join(COMFY, 'out', '史诗战', 'bronze', p['key'] + '.png'))]
        out.append({'code': code, 'name': short, 'what': re.sub(r'（[^）]*）', '', what).strip('，'), 'year': y, 'page': page_of_year(y),
                    'phases': phases, 'imgs': keys, 'hidden': code.endswith('隐'), 'common': '通用' in what})
    return out


def build():
    first = {n: b for n, b in stele_blocks(read_lines(os.path.join(ROOT, '山铜纪', '山铜纪_碑_第一版.md')))}
    for n, f in FORMS.items():                   # 图键照 stele_forms.json
        ART_KEY[n] = f['key']
    miss = [n for n in first if n not in FORMS and n != '灰雨城之乱']
    assert not miss, ('stele_forms.json 里缺', miss)
    rows = read_lines(os.path.join(ROOT, '底稿', '地图', '地点谱', '山铜纪.tsv'))
    keys = rows[0].split('\t')
    table = [dict(zip(keys, r.split('\t'))) for r in rows[1:] if r.strip()]
    fp = os.path.join(HERE, 'fate_table.json')
    fate_all = json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {}
    boss = bosses()
    report, eras, steles_all = [], [], []
    leg_by_short = {x[0]: x for x in LEG}
    for pi, (pname, y0, y1) in enumerate(PAGES):
        fname = os.path.basename(page_file(pi))
        lines = read_lines(page_file(pi))
        heads = [n for n, l in enumerate(lines, 1) if l.startswith('## ')]
        bl = MB.blocks(lines)
        assert len(heads) == len(bl)
        e = {'id': 'p%d' % (pi + 1), 'no': pi + 1, 'title': pname, 'years': '%d — %d' % (y0, y1), 'y0': y0, 'y1': y1, 'set': '山铜纪',
             'chap': '', 'chapName': '', 'chapDesc': '', 'steles': [], 'lines': [], 'cast': [], 'meet': [], 'legends': [], 'gods': [], 'bosses': [], 'places': []}
        text, bgs, people, p8 = '', {}, [], []
        # 碑（以页头那几块为准）
        for name, body in stele_blocks(lines):
            if name not in first and name != '灰雨城之乱':
                report.append('页上的碑碑第一版里没有：%s' % name)
            d = stele(name, body, pi)
            d['art'] = ART_KEY.get(name, '')
            front = d.get('front', '')
            m = re.match(r'^(.*?)刻的是，(.+)$', front)       # 灰旗那一块：正面先空着，往后才刻
            if m:
                d['frontNote'], front = m.group(1).rstrip('，') + '刻的', m.group(2)
            d['ft'], d['fl'] = face_lines(front, name)
            if '没有正名' in d.get('who', ''):
                d['ft'] = False
            d['bt'], d['bl'] = face_lines(d.get('back', ''), name)
            if '字是凸的' in d.get('who', ''):
                d['raised'] = 1
            e['steles'].append(d)
        for d in [x for x in e['steles'] if x['name'] in MERGE]:
            into = [x for x in e['steles'] if x['name'] == MERGE[d['name']]]
            if not into:
                continue
            into[0]['was'] = '这一面原来铸的是%s。' % d['name']
            into[0]['old'] = {'name': d['name'], 'year': d['year'], 'front': d.get('front', ''), 'erased': d.get('erased', '')}
            e['steles'].remove(d)
        for (title, body), ln in zip(bl, heads):
            if '主线｜' in title:
                l = mainline(title, body)
                l['_text'] = '\n'.join(body)
                e['lines'].append(l)
                text += '\n'.join(x for x in body if not x.startswith('【调用】'))
            elif title.startswith('旅途同行·背景：'):
                nm = re.sub(r'（.*', '', title.split('：', 1)[1]).strip()
                bgs.setdefault(nm, MB.background(body))
            elif title == '这一段的传奇表':
                p8 = body
        e['lines'].sort(key=lambda l: (l['_y'] or 9999))
        by_seg = {l['name'].split('·', 1)[-1]: l for l in e['lines']}
        first_y = min((l['_y'] for l in e['lines'] if l['_y']), default=y0)
        shorts_here = [x[0] for x in LEG if x[3] <= pi + 1 <= x[4]]
        for (title, body), ln in zip(bl, heads):
            if title.startswith('旅途同行：'):
                c = MB.companion(title, body, ([], '山铜纪'))
                seg = re.search(r'（山铜纪·([^）]+)）', title)
                segs = [s.strip() for s in seg.group(1).split('、')] if seg else []
                c['key'], c['pset'] = find_key(c['name'], fname, ln)
                c['born'] = born_abs(body)
                hit = [by_seg[s] for s in segs if s in by_seg]
                if not hit and not any(s == pname for s in segs):
                    report.append('旅伴没有对上主线：%s %s' % (c['name'], segs))
                if not hit:           # 管整一页的（巴尔缇娜、索恩薇娅那几条）：照头一条写到她的主线算岁数
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
                people.append(person(title, body, fname, ln, shorts_here))
        chaps = [(l['chap'], l['chapName'], l['chapDesc']) for l in e['lines'] if l['chap'] and '间' not in l['chap']]
        if chaps:
            best = max(set(chaps), key=chaps.count)
            e['chap'], e['chapName'], e['chapDesc'] = best
        # 三类人
        old = {x[0] for x in LEG if x[3] < pi + 1 <= x[4]}            # 前几页就是传奇的
        new = {x[0] for x in LEG if x[3] == pi + 1}                     # 这一页踏进传奇的：他是这一段的主角，留在旅伴里
        keep, grown, moved, seen = [], [], [], set()
        for c in e['cast']:
            short = c['name'].split('·')[0]
            if short in seen:
                continue
            seen.add(short)
            mortal = bool(re.match(r'^(人类|人族|半身人|兽耳|半兽人|狼耳|犬耳|狐耳|猫耳)', c['race']))
            if short in old:
                moved.append((c['name'], '传奇', c['age']))
                continue
            if mortal and c['age'] is not None and c['age'] >= MB.OLD_AT and short not in new:
                grown.append({'name': c['name'], 'tag': '', 'who': c['who'], 'key': c['key'], 'pset': c['pset'], 'race': c['race'], 'age': c['age'], 'prof': c.get('prof')})
                moved.append((c['name'], '相遇', c['age']))
                continue
            keep.append(c)
        cast_short = {c['name'].split('·')[0] for c in keep} | {g['name'].split('·')[0] for g in grown}
        # 人物条：神、传奇的档案、相遇
        leg_prof, meets, gods = {}, [], []
        for p in people:
            short = LEG_SRC.get(p['title'], p['name']).split('·')[0]
            if p['gods']:
                d = {k: p[k] for k in ('name', 'tag', 'who', 'key', 'pset')}
                d['prof'] = p['prof']
                d['side'] = '魔' if all(s == '魔' for _, s in p['gods']) else '正'
                gods.append(d)
                continue
            if p['bars']:
                for bn, items in p['bars'].items():
                    nm = bn.split('·', 1)[-1] if bn.split('·')[0] not in leg_by_short and '·' in bn and bn.split('·', 1)[-1].split('·')[0] in leg_by_short else bn
                    bshort = nm.split('·')[0]
                    pr = prof_from(items)
                    if bshort in shorts_here and bshort not in cast_short:
                        leg_prof.setdefault(bshort, {'sec': [], 'lines': []})
                        leg_prof[bshort]['sec'] += pr['sec']
                        leg_prof[bshort]['lines'] += pr['lines']
                        continue
                    if bshort in cast_short:
                        continue
                    k2, ps2 = find_key(nm, fname, p['line'])
                    meets.append({'name': nm, 'tag': p['name'] if p['group'] else p['tag'], 'who': '', 'key': k2, 'pset': ps2, 'prof': pr})
                continue          # 一群人那一条拆成一个一个人以后，总的那几栏（来由、是谁）不另留一张
            if short in shorts_here:
                if short in cast_short:
                    continue                    # 这一页才到传奇的那一位，档案照旅伴条
                lp = leg_prof.setdefault(short, {'sec': [], 'lines': []})
                lp['sec'] = p['prof']['sec'] + lp['sec']
                lp['lines'] = p['prof']['lines'] + lp['lines']
                if p['tag']:
                    lp['tag'] = p['tag']
                continue
            if short in cast_short:
                continue
            meets.append({k: p[k] for k in ('name', 'tag', 'who', 'key', 'pset', 'prof')})
        # 传奇
        p8_shorts = [x[0] for x in LEG] + [x[1] for x in LEG]
        now = legend_now(p8, sorted(set(p8_shorts), key=len, reverse=True))
        lg = []
        for x in LEG:
            short, full, ttl, a, b, ny, dy = x
            if not (a <= pi + 1 <= b) or short in cast_short:
                continue
            key, pset = find_key(full, fname, len(lines))
            key, pset = (LEG_KEY[short], '山铜纪') if short in LEG_KEY else (key, pset)
            g = {'name': full, 'title': ttl, 'key': key, 'pset': pset}
            if b == pi + 1 and dy:
                g['end'] = '殁于这一段'
            if a == pi + 1:
                g['new'] = 1
            lg.append((g, short, full, ny, dy))
        e['legends'] = [g for g, *_ in lg]
        e['cast'] = keep
        e['meet'] = grown + meets
        e['gods'] = gods
        e['moved'] = moved
        for c in e['cast']:
            c.pop('born', None)
        MB.take_profiles(e, bgs, fate_all.get(e['id'], {}))
        for g in e['gods']:
            pr = g.pop('prof', None)
            if pr and (pr.get('sec') or pr.get('fate')):
                pr['kind'] = 'god'
                if g.get('tag'):
                    pr['tag'] = g['tag']
                MB.PROFS[e['id']][g['name']] = {k: v for k, v in pr.items() if v not in ('', [], None, False)}
                g['p'] = 1
        for g, short, full, ny, dy in lg:
            lp = leg_prof.get(short, {})
            nw = now.get(short) or now.get(full, '')
            if re.search(r'死了|没了|死在|就死', nw):
                nw = ''           # 说的是怎么死的，死的那一句另有一栏
            pr = {'kind': 'legend', 'tag': g['title'] or lp.get('tag', ''), 'now': nw,
                  'sec': lp.get('sec', []), 'lines': lp.get('lines', [])[:6]}
            if ny and g.get('new'):
                pr['rose'] = '约 %d 年踏进传奇' % ny
            if g.get('end'):
                pr['died'] = legend_died(p8, short, full)
            if not (pr['now'] or pr['sec'] or pr.get('died')):
                report.append('传奇没有档案：%s %s' % (e['id'], full))
                continue
            MB.PROFS[e['id']][full] = {k: v for k, v in pr.items() if v not in ('', [], None, False)}
            g['p'] = 1
        # 灾祸
        e['bosses'] = [{k: v for k, v in b.items() if k != 'page'} for b in boss if b['page'] == pi]
        e['places'] = MB.places_of(text, table)
        for pl in e['places']:          # 地点谱的“位置”一栏是几段拿分号接的，页上只要头一段
            if '；' in pl['where']:
                pl['where'] = pl['where'].split('；')[0].rstrip('，') + '。'
        for l in e['lines']:
            l.pop('_y', None)
            l.pop('_text', None)
        eras.append(e)
        steles_all += e['steles']
    # 尽头：无字碑（碑基那四处半行）
    wz = first['无字碑']
    end = {'name': '无字碑', 'side': 'wall', 'art': ART_KEY.get('无字碑', ''), 'base': []}
    end.update(form=FORMS['无字碑']['form'], size=FORMS['无字碑']['size'], o=FORMS['无字碑']['o'])
    for l in wz:
        s = l.rstrip()
        if s.strip().startswith('- 碑：'):
            end['kind'], end['material'], end['where'], end['who'], end['around'] = split_bei(s.strip()[4:])
            end['kind'], end['where'], end['who'] = 'white', end['where'] + end['who'], ''
        elif s.strip().startswith('- 正面：'):
            end['front'] = s.strip()[5:]
        elif s.strip().startswith('- 背面：'):
            end['back'] = s.strip()[5:]
        elif s.strip().startswith('- 碑基：'):
            end['baseIntro'] = s.strip()[5:]
        elif s.startswith('  - ') and 'baseIntro' in end and len(end['base']) < 4:
            end['base'].append(s.strip()[2:])
    data = {'era': '山铜纪', 'total': '九百四十七年', 'series': '奥尔德兰的旅印｜上部', 'eras': eras, 'end': end}
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
    open(os.path.join(HERE, 'data', 'bronze.json'), 'w', encoding='utf-8', newline='\n').write(js)
    print('写了 data/bronze.json', len(js), '字')
    tot = 0
    for eid, ps in MB.PROFS.items():
        pj = json.dumps(scrub(ps), ensure_ascii=False, separators=(',', ':')) + '\n'
        open(os.path.join(HERE, 'data', 'prof', eid + '.json'), 'w', encoding='utf-8', newline='\n').write(pj)
        tot += len(pj)
    print('写了 data/prof/', len(MB.PROFS), '份，', sum(len(v) for v in MB.PROFS.values()), '人，', tot, '字')
    for e in data['eras']:
        print(e['id'], e['title'], e['years'], '｜', e['chap'], e['chapName'], '｜ 碑', len(e['steles']), '主线', len(e['lines']), '旅伴', len(e['cast']), '相遇', len(e['meet']),
              '传奇', len(e['legends']), '神', len(e['gods']), '灾祸', len(e['bosses']), '地', len(e['places']),
              ('｜ 挪了：' + '、'.join('%s→%s(%s岁)' % m for m in e['moved'])) if e['moved'] else '')
        print('      碑', ' '.join('%s(%s,%s,%s)' % (s['name'], s['year'], {'west': '北', 'east': '南', 'wall': '脚'}[s['side']], s.get('kind')) for s in e['steles']))
        print('      主线', ' ／ '.join('%s【%s】(%s)' % (l['name'].split('·', 1)[-1], l.get('task', ''), l['year']) for l in e['lines']))
        print('      旅伴', ' '.join('%s(%s,%s)' % (c['name'], c.get('age'), c.get('key') or '无图') for c in e['cast']))
        print('      相遇', ' '.join('%s(%s)' % (c['name'], c.get('key') or '无图') for c in e['meet']))
        if e['gods']:
            print('      神与魔神', ' '.join('%s%s(%s,%s)' % (c['tag'] + '·' if c['tag'] else '', c['name'], c['side'], c.get('key') or '无图') for c in e['gods']))
        print('      传奇', ' '.join('%s(%s%s)' % (c['name'], c.get('key') or '无图', '' if c.get('p') else '，无档') for c in e['legends']))
        print('      灾祸', ' '.join('%s(%s)' % (b['name'], b['year']) for b in e['bosses']))
        for l in e['lines']:
            if not (l.get('task') and l['open'] and l['acts'] and l['ending']):
                print('    缺', l['name'], {k: bool(l.get(k)) for k in ('task', 'hooks', 'open', 'acts', 'ending')})
    for r in report:
        print('！', r)
