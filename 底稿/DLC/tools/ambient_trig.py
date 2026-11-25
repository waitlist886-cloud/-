"""四纪条目的话题触发，拿实测回复试：哪些分支在一条寻常回复里就中了（白醒）。

11-24 头一版只扫新料 290 条、样本只有 moon/samples/。11-25 扩成扫四纪各页分段、补卷、新料源稿、通用条目和底卡新条目
的条目设置，样本添上本地干跑 tools/dryrun/runs/ 的回复和玩家的话，再加一份骨架的固定栏名（每轮照抄的字）。

用法：python -I -X utf8 底稿/DLC/tools/ambient_trig.py <仓库根> [选项]
  --scope 全卷|新料   扫哪些，默认全卷
  --out 目录          把表写到这个目录：分支.tsv（一条一个分支）、词.tsv（照中的字归拢）、醒.tsv（--wake 的）
  --wake              照源稿的条目设置模拟各局各轮醒哪些条（纪、时段、主线钥匙照页上写的正则；年份黑名单照写的算；
                      星条和打包脚本现算的门不算），拿来比改前改后
  --word 字,字        只列中的字里带这几个字的
  --all               连放过的一起列
  --skip 字,字        文件名里带这几个字的不扫（目录条本来就不扫）
  --tide              拿各纪每条主线的名字（潮汐格、在办里照抄的那几个字）去试同一纪别的条目的话题分支
  --check-lit         列收窄以后没有单说就醒的字的条目
  --apply             只给 --scope 新料：把中了、没放过的分支从触发里拿掉（年份正则、〔纪·正则〕不动；拿完一条分支不剩的不动、报出来）

放过的写在同目录 ambient_allow.tsv：一行「中的字<TAB>缘故」（这个字是专名或者正对题，哪一条用它都放过），
或者「条目标题<TAB>分支<TAB>缘故」（只放这一条的这一个分支）。# 起头的行是说明。

看法：
  栏  中在骨架的固定栏名上（§面板｜委托、§角色行｜羁绊、活事件：无 这一类每轮照抄的字），等于常驻，要收
  录  中在回复的记录行里（§角色、§见闻、§记忆、§预载……），状态栏照抄以后会一直醒着
  文  只中在正文段落和台词里
只报、不改（--apply 那一路除外）。收窄以后每一条仍然要有一个单说就醒的专名，跑 --check-lit 看。
"""
import bisect, collections, glob, io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ROOT = ARGS[0] if ARGS else os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
HERE = os.path.dirname(os.path.abspath(__file__))


def opt(k, d=None):
    if k in sys.argv:
        i = sys.argv.index(k)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--') else True
    return d


SCOPE = opt('--scope', '全卷')
OUT = opt('--out')
APPLY = '--apply' in sys.argv
SHOW_ALL = '--all' in sys.argv
WORDS = [w for w in str(opt('--word', '') or '').split(',') if w and w != 'True']
BS = chr(92)
J = lambda *a: os.path.join(ROOT, *a)


# ---------------- 扫哪些文件 ----------------
def files_xinliao():
    d = J('底稿', 'DLC', '新料')
    fs = [os.path.join(d, '样稿三条.md'), os.path.join(d, '第一拨.md')]
    for sub, pat in (('律法志', 'L*.md'), ('风物志', 'F*.md'), ('谱系志', 'G*.md'), ('谱系志', 'C*.md')):
        fs += sorted(glob.glob(os.path.join(d, sub, pat)))
    return [(f, 'page') for f in fs if os.path.isfile(f)]


def files_all():
    out = []
    g = lambda *a: sorted(glob.glob(J(*a)))
    # 月银纪三卷：第一到三批是另一种写法（触发：一行），史诗、诸国期、萨尔维斯的页没有分段，页就是源
    for f in g('moon', 'batch[123]', '*.md'):
        out.append((f, 'batch'))
    for f in g('月银纪史诗', '第*歌_*.md') + g('诸国期', '诸国期时段_*.md') + g('萨尔维斯', '萨尔维斯时段_*.md'):
        out.append((f, 'page'))
    # 三纪的页改分段
    for f in g('纷争纪', 'parts*', '*.md') + g('山铜纪', 'parts[1-6]', '*.md') + g('迷宫纪前传', 'parts[1-6]', '*.md'):
        out.append((f, 'page'))
    # 补卷：新料那十二份是 place_xinliao.py 生成的，扫源稿，不扫生成的
    for f in g('萨尔维斯', '补卷', '*.md') + g('月银纪补卷', '*.md') + g('纷争纪', '补卷', '*.md') + g('山铜纪', '补卷', '*.md') + g('迷宫纪前传', '补卷', '*.md'):
        b = os.path.basename(f)
        if '说明' in b or '新料' in b:
            continue
        out.append((f, 'page'))
    out.append((J('山铜纪', '山铜纪_碑_第一版.md'), 'page'))
    out.append((J('迷宫纪前传', '迷宫纪前传_委托_第一版.md'), 'page'))
    out += files_xinliao()
    for f in g('通用条目', '*.md') + g('底卡新条目', '*.md') + g('底卡新条目_四纪大框', '*.md'):
        out.append((f, 'general'))
    # 目录条（make_index.py 生成，各纪 目录条.md、补卷_目录条.md、通用条目/大图书馆_目录条.md）本来就跟着底座常驻，不看
    skip = ['目录条'] + [w for w in str(opt('--skip', '') or '').split(',') if w and w != 'True']   # --skip 字,字：文件名里带这几个字的不看（比改前改后时对齐文件）
    return [(f, k) for f, k in out if os.path.isfile(f) and not any(w in os.path.basename(f) for w in skip)]


# ---------------- 条目设置怎么读 ----------------
SET_RX = re.compile(r'触发(（同时满足）)?(.*?)，(?:黑名单 ?(.*?)，)?(?:优先级 ?\d+，)?范围 ?([^，。]+)，深度 ?(\d+)')


def split_top(rx):
    out, depth, cur, esc, cls = [], 0, '', False, False
    for ch in rx:
        if esc:
            cur += ch; esc = False; continue
        if ch == BS:
            cur += ch; esc = True; continue
        if cls:
            cur += ch
            if ch == ']':
                cls = False
            continue
        if ch == '[':
            cls = True; cur += ch; continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == '|' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    return out


GATE_HINT = re.compile(r'纪元：|hud-meta|<br>|开局时段：|的年月·')


def is_gate(rx):
    return bool(GATE_HINT.search(rx))


def toks_of(seg):
    """一段触发或黑名单 → [('rx', 正则体) | ('alias', 〔…〕) | ('star', None) | ('word', 字)]"""
    seg = (seg or '').strip()
    if seg in ('', '无'):
        return []
    rxs = re.findall(r'`/(.+?)/[a-z]*`', seg)
    rest = re.sub(r'`[^`]+`', '\x00', seg)
    rest = re.sub(r'（[^（）]*）', '', rest)
    out, k = [], 0
    for part in re.split(r'[、\s]+', rest):
        if not part:
            continue
        for m in re.finditer(r'〔[^〕]+〕|\x00|星名加持有人的名字|[^〔\x00]+', part):
            g = m.group(0)
            if g == '\x00':
                if k < len(rxs):
                    out.append(('rx', rxs[k]))
                k += 1
            elif g.startswith('〔'):
                out.append(('alias', g))
            elif g == '星名加持有人的名字':
                out.append(('star', None))
            else:
                out.append(('word', g))
    return out


# 第一拨里 1001 年三条“书写与衣食”合条，place_xinliao.py 不收（风物志下半拆完以后撤的），不进卡，不看
SKIP_TITLES = {'迷宫纪·风物｜书写与衣食·西陆', '迷宫纪·风物｜书写与衣食·东陆', '迷宫纪·风物｜书写与衣食·阿卡迪亚'}
ERA_1001 = r'(?:<br>|hud-meta">|纪元：)迷宫纪(?:100[1-9]|10[1-9]\d|1[1-9]\d\d)年'


class Entry:
    __slots__ = ('file', 'line', 'title', 'kind', 'folder', 'era', 'and_', 'trig', 'bl', 'rng', 'depth', 'raw', 'star')


def era_of(folder, line, kind, fname):
    m = re.search(r'\d\d·(月银纪|纷争纪|山铜纪|迷宫纪)｜', folder or '')
    if not m:
        return '迷宫纪1001' if (kind == 'general' and '底卡新条目' in fname) else '通用'
    e = m.group(1)
    if e != '迷宫纪':
        return e
    if '迷宫纪前传' in line or '的年月' in line:
        return '迷宫纪前传'
    if re.search(r'100\[1-9\]|1001', line):
        return '迷宫纪1001'
    return '迷宫纪前传'


def read_entries(path, kind):
    L = open(path, encoding='utf-8').read().replace('\r', '').split('\n')
    out = []
    if kind == 'batch':
        cur = None
        for i, ln in enumerate(L):
            if ln.startswith('=== '):
                cur = Entry(); cur.file, cur.line, cur.title, cur.kind = path, None, ln[4:].strip(), kind
                cur.folder, cur.and_, cur.trig, cur.bl, cur.rng, cur.depth, cur.raw, cur.star = '', False, [], [], ['user', 'assistant'], 2, '', False
                out.append(cur)
            elif cur is not None and ln.startswith('文件夹：'):
                cur.folder = ln[4:].strip()
            elif cur is not None and ln.startswith('触发：'):
                cur.line, cur.raw = i, ln
                seg = ln[3:]
                rxs = re.findall(r'(?:^|、)/(.+?)/(?=、|$)', seg)
                rest = re.sub(r'(^|、)/.+?/(?=、|$)', lambda m: m.group(1) + '\x00', seg)
                k = 0
                for part in rest.split('、'):
                    part = part.strip()
                    if part == '\x00':
                        cur.trig.append(('rx', rxs[k])); k += 1
                    elif part.startswith('〔'):
                        cur.trig += [('alias', x) for x in re.findall('〔[^〕]+〕', part)]
                    elif part:
                        cur.trig.append(('word', part))
            elif cur is not None and ln.startswith('触发方式：'):
                cur.and_ = '同时满足' in ln
            elif cur is not None and ln.startswith('黑名单：'):
                seg = ln[4:].strip()
                if seg != '无':
                    for part in seg.split('、'):
                        part = part.strip()
                        if part.startswith('/') and part.endswith('/'):
                            cur.bl.append(('rx', part[1:-1]))
                        elif part.startswith('〔'):
                            cur.bl += [('alias', x) for x in re.findall('〔[^〕]+〕', part)]
                        elif part:
                            cur.bl.append(('word', part))
            elif ln.strip() == '---':
                cur = None if cur is None else cur
        for e in out:
            e.era = era_of(e.folder, e.raw, kind, path)
        return [e for e in out if e.line is not None]
    title, in_notes = '', False
    for i, ln in enumerate(L):
        if ln.startswith('## 设计备注') or ln.startswith('## 这一份的设计备注'):
            in_notes = True
        if ln.startswith('## ') and not in_notes:
            h = ln[3:].strip()
            if h != '裁定锁':
                title = h
        elif ln.startswith('### ') and not in_notes and re.search(r'\((?:Special|Passive|Art|Ability) \| ', ln):
            title = ln[4:].strip()
        if not ln.startswith('> 条目设置：') or in_notes:
            continue
        m2 = SET_RX.search(ln)
        if not m2:
            continue
        e = Entry()
        e.file, e.line, e.title, e.kind, e.raw = path, i, title, kind, ln
        mf = re.search(r'文件夹 ?([^，（]+)', ln)
        e.folder = mf.group(1).strip() if mf else ''
        e.and_ = bool(m2.group(1))
        e.trig = toks_of(m2.group(2))
        e.bl = toks_of(m2.group(3))
        r = m2.group(4).strip()
        e.rng = ['user'] if r == '用户' else ['assistant'] if r in ('助手', 'AI') else ['user', 'assistant']
        e.depth = int(m2.group(5))
        e.star = any(t[0] == 'star' for t in e.trig)
        e.era = era_of(e.folder, ln, kind, path)
        if title in SKIP_TITLES:
            continue
        if kind == 'general' and '底卡新条目' in path:
            # 底卡新条目进四纪大框的时候改成同时满足 1001 年以后的底座和原来的字眼（general_entries.apply_1001_new）
            e.trig = [('rx', ERA_1001), ('rx', '|'.join(v if k == 'rx' else re.escape(v) for k, v in e.trig if k in ('rx', 'word')))]
            e.and_ = True
            e.depth = max(2, e.depth)
        out.append(e)
    return out


# ---------------- 样本 ----------------
# 骨架（底稿/状态栏/大框/主提示词/03_输出驱动_骨架.md）每轮照抄的名目、栏名和固定的值，一行一条记录的样子。
# 只放固定的字，例子里现编的内容不放。骨架改了栏名，这里跟着改。
SKELETON = '''§底座｜纪元： · 防抢话 开 · 难度 普通 · 节奏 均衡 · 调子 史诗 · 档位 很长
§环境｜
§推演｜0｜输入｜玩家要做：｜本轮停在：｜挡位：1日常｜正文：很长·6段｜修正：无｜裁定：
§推演｜1｜时空｜时间：
§推演｜2｜场面｜活事件：无｜事件核心：｜关系核心：｜其他在场：｜战斗：不出
§推演｜2｜场面｜活事件：无｜事件核心：无｜关系核心：无｜其他在场：无｜战斗：战斗栏
§推演｜3｜人物｜（锚定源：旅途同行）｜底线：｜要：｜知：｜做：｜好感 Lv.1 0/10 不变
§推演｜3｜人物｜（锚定源：凡世至强）（锚定源：任务人物）（锚定源：本地角色）（锚定源：新）
§推演｜4｜视角｜主角本轮知道的：（来源：看到、听到）｜队友对主角展示过的：无｜NPC各自知道：无新增｜不在场：无｜新登场有名路人：无
§推演｜4｜视角｜新登场有名路人：（已核不与旅伴、传奇、任务人物同名）·对主角知道多少（不认识）
§推演｜5｜记忆｜上轮短期1条→本轮：追加[2]
§推演｜6｜结算｜EXP：0｜属性经验：无｜潜力：不变｜升级裁定：无｜属性：无｜队友：无｜检定：无
§推演｜7｜面板｜主角魅力：耐看｜日报渠道：无｜角色卡：2张
§推演｜8｜收尾｜迷雾：无｜反媚主：无｜行动分支：3条，末条自定义
§推演｜9｜世界｜事件线：无
§正文｜
§话｜｜平常｜
§分支｜自定义行动：由玩家输入
§战斗｜｜交战中
§面板｜身份｜
§面板｜立绘｜无
§面板｜立绘｜预设·｜衣着:常服
§面板｜容貌｜评＝｜魅力＝耐看·
§面板｜着装｜
§面板｜姿态｜
§面板｜位阶｜LVL 4 启源·初识｜EXP 0/4000｜蓄势 无
§面板｜资源｜HP 132/132 MP 85/85 SP 78/84 架势 55/55｜饱食 54%｜负重 6/100 kg｜伤 无｜污染 无
§状态｜无
§面板｜六维｜STR 15(0/1500·潜100%)｜DEX 15(0/1500·潜100%)｜MANA 15(0/1500·潜100%)｜MIND 15(0/1500·潜100%)｜VGR 15(0/1500·潜100%)｜FTH 15(0/1500·潜100%)
§面板｜攻防｜ATK 15 · PV 18 · DV 16｜物0 火0 冰0 雷0 土0 风0 圣0 暗0 狱0
§面板｜命路｜｜职业 未就职｜命星
§面板｜旅印｜无印｜｜信用 ｜权限
§面板｜委托｜无｜无｜无｜无｜无
§面板｜层级｜
§装备｜主手｜空置
§装备｜副手｜空置
§装备｜头｜空置
§装备｜上衣｜空置
§装备｜下装｜空置
§装备｜鞋｜空置
§装备｜饰品｜空置
§装备｜配饰｜空置
§装备｜内衣｜
§装备｜内裤｜
§装备｜袜｜空置
§能力｜命星｜｜Rare｜被动·
§能力｜Art｜｜Rare｜一阶·×1.2｜｜招
§能力｜Passive｜无
§能力｜Active｜无
§能力｜Skill｜｜生手｜｜｜下一档
§能力｜职业能力｜无
§伟业｜职业｜未就职｜已评：无｜下一层 LVL 21
§伟业｜伟业｜启源→共鸣｜LVL 4/20 · ｜命路五阶 未开｜蓄势 无｜伟业簿 无｜破格铸史冠名 无｜候选称号 无
§伟业｜斩过｜无
§物品｜未装备｜
§物品｜消耗｜
§物品｜贵重｜
§物品｜材料｜
§物品｜不可丢弃｜
§背包｜队伍共用｜无
§角色｜｜人类 / 51岁 / 女｜立绘:｜衣着:常服
§角色｜｜人类 / 27岁 / 女｜名牌
§角色签｜｜｜LVL 66｜灵格·临界｜｜已识
§角色签｜｜｜LVL 66｜灵格·临界｜｜同行
§角色话｜
§角色行｜容貌｜ ｜ 魅力 出众·
§角色行｜着装与姿态｜
§角色行｜状态｜HP 1/1 MP 1/1 SP 1/1 架势 1/1 ｜ 伤 无 ｜ 污染 无 ｜ 异常 无
§角色行｜属性｜EXP 0/1｜ATK 1 · PV 1 · DV 1 ｜ 未知
§角色行｜私产｜
§角色行｜羁绊｜好感 Lv.1 初次见面的关系 3/10 ｜ 羁绊任务 无 ｜ 协战技 无
§角色行｜关系因果｜最近变化：不变 ｜ 未兑现承诺/债务：暂无 ｜ 当前矛盾与边界：暂无
§角色细｜装备｜主手 ｜ 副手 无 ｜ 甲 ｜ 随身
§角色细｜命星·能力｜
§角色细｜职业｜未就职 ｜ 已评：
§角色细｜职业能力｜无
§见闻｜日报｜无
§见闻｜已知情报｜（来源：，可信度：高）
§见闻｜流言风闻｜无
§见闻｜在办｜当前委托 无 ｜ 当前任务 无
§见闻｜可接｜无
§见闻｜线索｜无
§见闻｜预告｜无
§记忆｜修正｜无
§记忆｜短期｜[1] | 核心事件：
§记忆｜未结因果｜无
§记忆｜长期｜无
§记忆｜核心｜无
§记忆｜已完成｜无
§预载｜
'''


class Sample:
    __slots__ = ('name', 'run', 'era', 'role', 'rnd', 'text', 'year')


RUN_ERA = {'月银纪': '月银纪', '纷争纪': '纷争纪', '山铜纪': '山铜纪', '前传': '迷宫纪前传', '迷宫纪1001': '迷宫纪1001'}


def load_samples():
    out = []
    for p in sorted(glob.glob(J('tools', 'dryrun', 'runs', '*', '轮*_*.txt'))):
        b = os.path.basename(p)
        m = re.match(r'轮(\d+)_(回复|玩家)\.txt$', b)
        if not m:
            continue
        s = Sample()
        s.run = os.path.basename(os.path.dirname(p))
        s.era = next((v for k, v in RUN_ERA.items() if s.run.startswith(k)), '通用')
        s.rnd = int(m.group(1))
        s.role = 'assistant' if m.group(2) == '回复' else 'user'
        s.text = open(p, encoding='utf-8').read().replace('\r', '').lstrip('﻿')
        s.name = '%s·轮%d%s' % (s.run, s.rnd, '回复' if s.role == 'assistant' else ('凭证' if s.rnd == 1 else '玩家'))
        out.append(s)
    for p in sorted(glob.glob(J('moon', 'samples', 'reply*.html'))):
        s = Sample()
        s.run, s.rnd, s.role = 'moon/samples', 0, 'assistant'
        s.era = '迷宫纪1001' if '迷宫纪' in os.path.basename(p) else '月银纪'
        s.text = open(p, encoding='utf-8').read().replace('\r', '')
        s.name = '旧样本·' + os.path.basename(p)[:-5]
        out.append(s)
    s = Sample()
    s.name, s.run, s.era, s.role, s.rnd, s.text = '骨架固定栏名', '骨架', '通用', 'assistant', 0, SKELETON
    out.append(s)
    return out


SAMPLES = load_samples()
SEP = '\n\x00\n'
BIG = SEP.join(s.text for s in SAMPLES)
STARTS, _p = [], 0
for s in SAMPLES:
    STARTS.append(_p)
    _p += len(s.text) + len(SEP)


def where(pos):
    """大串里的位置 → (样本, 这一行的行首名目, 上下文)"""
    k = bisect.bisect_right(STARTS, pos) - 1
    s = SAMPLES[k]
    off = pos - STARTS[k]
    a = s.text.rfind('\n', 0, off) + 1
    b = s.text.find('\n', off)
    b = len(s.text) if b < 0 else b
    line = s.text[a:b]
    m = re.match(r'§[^｜\n]{1,6}(?:｜[^｜\n]{1,8})?', line)
    lab = m.group(0) if m else '正文'
    return s, lab, off, a


def kind_of(s, lab):
    if s.run == '骨架':
        return '栏'
    if s.role == 'user':
        return '凭' if s.rnd == 1 else '问'
    if s.run == 'moon/samples':
        return '旧'
    return '文' if lab in ('正文',) or lab.startswith('§话') or lab.startswith('§正文') or lab.startswith('§分支') else '录'


_C = {}


def comp(rx):
    c = _C.get(rx, 0)
    if c == 0:
        try:
            c = re.compile(rx)
        except re.error:
            c = None
        _C[rx] = c
    return c


def hits(branch, literal=False):
    """一个分支在样本里的命中：[(样本, 名目, 中的字, 上下文)]，一份样本只记头一处"""
    out, seen = [], set()
    if literal:
        it, pos = [], BIG.find(branch)
        while pos >= 0:
            it.append((pos, branch)); pos = BIG.find(branch, pos + 1)
    else:
        c = comp(branch)
        if c is None:
            return out
        it = ((m.start(), m.group(0)) for m in c.finditer(BIG))
    for pos, g in it:
        if '\x00' in g:
            continue
        s, lab, off, a = where(pos)
        key = (s.name,)
        if key in seen:
            continue
        seen.add(key)
        ctx = s.text[max(0, off - 12):off + len(g) + 12].replace('\n', ' ')
        out.append((s, lab, g, ctx))
    return out


# ---------------- 放过的 ----------------
ALLOW_W, ALLOW_E = {}, {}
_af = os.path.join(HERE, 'ambient_allow.tsv')
if os.path.isfile(_af):
    for ln in open(_af, encoding='utf-8').read().replace('\r', '').split('\n'):
        if not ln.strip() or ln.startswith('#'):
            continue
        c = ln.split('\t')
        if len(c) >= 3:
            ALLOW_E[(c[0].strip(), c[1].strip())] = c[2].strip()
        elif len(c) == 2:
            ALLOW_W[c[0].strip()] = c[1].strip()


# ---------------- 钥匙别名（给 --wake 用，照 build_v12.py 开头那一段的读法，不现算合篇和星的门） ----------------
def load_aliases():
    A = {
        '〔月银纪·正则〕': r'日期<\/b><br>月银纪|hud-meta">月银纪|纪元：月银纪',
        '〔纷争纪·正则〕': r'(?:<br>|hud-meta">|纪元：)(?:纷争纪|山铜纪元年)',
        '〔迷宫纪凭证〕': r'^(?![\s\S]*纪元：月银纪)[\s\S]*命途已确认',
    }
    Y = r'(?:<br>|hud-meta">|纪元：)月银纪'
    A['〔时段·祭火·正则〕'] = r'潮汐<\/b><br>祭火| · 祭火·|开局时段：祭火|%s(?:\d{1,3}|1000)年' % Y
    A['〔时段·万兽·正则〕'] = r'潮汐<\/b><br>万兽| · 万兽·|开局时段：万兽|%s(?:100[1-9]|10[1-9]\d|1[1-9]\d\d|2\d\d\d|3000)年' % Y
    for p in ['祭火', '万兽', '诸国', '崛起', '帝国', '魔族之世', '末年']:
        A['〔时段·%s〕' % p] = '|'.join(re.escape(x) for x in ['潮汐</b><br>' + p, ' · %s·' % p, '开局时段：' + p])
    for era in ('月银纪', '纷争纪', '山铜纪'):
        A['〔%s〕' % era] = '|'.join(re.escape(x) for x in ['日期</b><br>' + era, 'hud-meta">' + era, '纪元：' + era])
    pats = ['月银纪史诗/第*歌_*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md', '纷争纪/纷争纪时段_*.md', '山铜纪/山铜纪时段_*.md',
            '迷宫纪前传/迷宫纪前传时段_*.md', '山铜纪/补卷/*.md', '迷宫纪前传/补卷/*.md', '纷争纪/补卷/*.md', '月银纪补卷/*.md', '萨尔维斯/补卷/*.md',
            'moon/batch[123]/*.md']
    for p in pats:
        for f in glob.glob(J(*p.split('/'))):
            t = open(f, encoding='utf-8').read()
            for m in re.finditer(r'(〔[^〕]+〕)(?:打包脚本里要加，)?写成(?:一条正则)? ?`/([^`]+)/`', t):
                A.setdefault(m.group(1), m.group(2))
    A['〔迷宫纪前传〕'] = A.get('〔迷宫纪前传·正则〕', '(?!)')
    A['〔别纪〕'] = '|'.join(re.escape(x) for era in ('迷宫纪', '纷争纪', '山铜纪') for x in ['日期</b><br>' + era, 'hud-meta">' + era, '纪元：' + era])
    return A


ALIASES = None
UNKNOWN_ALIAS = collections.Counter()


def tok_match(tok, text):
    kind, v = tok
    if kind == 'rx':
        c = comp(v)
        return bool(c and c.search(text))
    if kind == 'word':
        return v in text
    if kind == 'alias':
        rx = ALIASES.get(v)
        if rx is None:
            m = re.match(r'〔主线·(.+)〕', v)
            if m:                                     # 主线钥匙没写正则的：认潮汐格和开局口令里的主线名
                nm = m.group(1)
                rx = re.escape(nm + '·') + '|' + re.escape('开局时段：' + nm.split('·')[-1])
                ALIASES[v] = rx
            else:
                UNKNOWN_ALIAS[v] += 1
                return False
        c = comp(rx)
        return bool(c and c.search(text))
    return False


def fires(e, text):
    if not e.trig:
        return False
    rs = [tok_match(t, text) for t in e.trig]
    ok = all(rs) if e.and_ else any(rs)
    if not ok:
        return False
    return not any(tok_match(t, text) for t in e.bl)


def wake_table(entries):
    """各局各轮照源稿的条目设置模拟醒哪些条。第 N 轮扫玩家第 N 句、回复第 N-1 条（深度 2），深度 3 再加玩家第 N-1 句。"""
    global ALIASES
    ALIASES = load_aliases()
    runs = collections.defaultdict(dict)
    for s in SAMPLES:
        if s.run in ('骨架', 'moon/samples'):
            continue
        runs[s.run][(s.rnd, s.role)] = s
    rows = []
    for run in sorted(runs):
        d = runs[run]
        nmax = max(r for r, _ in d)
        for n in range(1, nmax + 1):
            if (n, 'user') not in d:
                continue
            msgs = [d[(n, 'user')]]
            for back in range(1, 4):
                if (n - back, 'assistant') in d:
                    msgs.append(d[(n - back, 'assistant')])
                if (n - back, 'user') in d:
                    msgs.append(d[(n - back, 'user')])
            for e in entries:
                if e.star:
                    continue
                dep = e.depth or 3
                for s in msgs[:dep]:
                    if s.role not in e.rng:
                        continue
                    if fires(e, s.text):
                        rows.append((run, n, e, s))
                        break
    return rows


# ---------------- 主流程 ----------------
def topic_branches(e):
    """这一条的话题分支：[(分支, 是不是纯字)]。同时满足的条目里认纪元、时段、主线的那一支不算。"""
    out = []
    for kind, v in e.trig:
        if kind == 'rx':
            if e.and_ and is_gate(v):
                continue
            if not e.and_ and is_gate(v) and len(e.trig) == 1:
                continue
            for b in split_top(v):
                if b:
                    out.append((b, False))
        elif kind == 'word':
            out.append((v, True))
    return out


def literal_runs(rx):
    body = re.sub(r'\\.', '\x01', rx)
    return [r.strip() for r in re.split(r'[\\^$.|?*+()\[\]{}/\x01]', body) if len(r.strip()) >= 2 and re.search(r'[一-鿿]', r)]


def check_lit(entries):
    """收窄以后每一条仍然要有一个单说就醒的字（照 make_dlc.py 的模拟：触发里拆到元字符为止的字面词，单独接在凭证后头试）。"""
    bad = []
    for e in entries:
        if e.star:
            continue
        topics = [(k, v) for k, v in e.trig if (k == 'word') or (k == 'rx' and not is_gate(v))]
        if not topics:
            continue
        def lit_ok(k, v):
            if k == 'word':
                return True
            c = comp(v)
            return bool(c) and any(c.search(r) for r in literal_runs(v))
        # 同时满足的：话题那几支每一支都要单说得醒；只要满足一个的：有一支单说得醒就行
        ok = all(lit_ok(k, v) for k, v in topics) if e.and_ else any(lit_ok(k, v) for k, v in topics)
        if not ok:
            bad.append(e)
    return bad


def tide_scan(entries, rel):
    """主线名每轮写在底座的潮汐格和 §见闻｜在办 的当前任务里。拿各纪每条主线的名字去试同一纪别的条目的话题分支：
    中了的，这条主线开着的局里那一条就是常驻。主线自己那一条、标题里带这个主线名的（幕、委托、对手名号）不算。"""
    mains = []                                   # (纪, 时段, 主线名)
    for e in entries:
        m = re.match(r'(月银纪|纷争纪|山铜纪|迷宫纪)·主线｜([^·｜]+)·(.+?)(?:·[一二三四五六七八九]幕)?$', e.title)
        if m:
            era = e.era
            k = (era, m.group(2), m.group(3))
            if k not in mains:
                mains.append(k)
    n = 0
    seen = set()
    for era, per, name in mains:
        text = ' · %s·%s·一幕 · 防抢话 开\n当前任务 %s｜%s·一幕' % (per, name, per, name)
        for e in entries:
            if e.star or e.era != era or name in e.title:
                continue
            for b, lit in topic_branches(e):
                if lit:
                    mm = b in name
                    g = b
                else:
                    c = comp(b)
                    r = c.search(text) if c else None
                    mm = bool(r)
                    g = r.group(0) if r else ''
                if not mm or not g.strip(' ·｜') or (e.title, b) in ALLOW_E:
                    continue
                if g in per and g not in name:            # 中在时段名上的另说（时段名是这一段所有条目共有的）
                    continue
                if not gate_ok(e, text):
                    continue
                key = (e.file, e.line, b, name)
                if key in seen:
                    continue
                seen.add(key)
                n += 1
                print('%s｜主线 %s·%s｜%s｜%s｜分支 %s｜中 %s' % (era, per, name, rel(e.file), e.title, b, g))
    print('主线 %d 条；话题分支中在别的主线名上的 %d 处' % (len(mains), n))


def gate_ok(e, text):
    """这条主线开着的局里，这一条的门过不过得去：时段钥匙、主线钥匙拿潮汐格试，认整一纪的钥匙和写死年份的正则当过得去，
    黑名单里带主线名、时段名的照挡（年份黑名单没有年份可试，当不挡）。"""
    global ALIASES
    if ALIASES is None:
        ALIASES = load_aliases()
    for kind, v in e.trig:
        if kind == 'alias':
            if re.search(r'^〔(?:月银纪|纷争纪|山铜纪|迷宫纪前传)(?:·正则)?〕$', v):
                continue
            if not tok_match((kind, v), text):
                return False
    for kind, v in e.bl:
        if kind == 'alias' and re.search(r'^〔(?:月银纪|纷争纪|山铜纪|迷宫纪前传|别纪)(?:·正则)?〕$', v):
            continue
        if tok_match((kind, v), text):
            return False
    return True


def main():
    files = files_xinliao() if SCOPE == '新料' else files_all()
    entries = []
    for f, k in files:
        entries += read_entries(f, k)
    rel = lambda p: os.path.relpath(p, ROOT).replace(BS, '/')
    print('扫 %d 个文件，条目设置 %d 行（星条 %d 行不看话题），样本 %d 份（干跑回复 %d、玩家的话 %d、旧样本 %d、骨架 1）' % (
        len(files), len(entries), sum(1 for e in entries if e.star), len(SAMPLES),
        sum(1 for s in SAMPLES if s.role == 'assistant' and s.rnd), sum(1 for s in SAMPLES if s.role == 'user'),
        sum(1 for s in SAMPLES if s.run == 'moon/samples')))

    if '--tide' in sys.argv:
        tide_scan(entries, rel)
        return

    if '--check-lit' in sys.argv:
        bad = check_lit(entries)
        for e in bad:
            print('没有单说就醒的字：%s｜%s' % (rel(e.file), e.title))
        print('没有单说就醒的字的 %d 条' % len(bad))
        return

    cache = {}
    rows = []                                   # (条目, 分支, 命中列表)
    for e in entries:
        if e.star:
            continue
        for b, lit in topic_branches(e):
            key = (b, lit)
            if key not in cache:
                cache[key] = hits(b, lit)
            h = cache[key]
            if h:
                rows.append((e, b, h))

    def allowed(e, b, h):
        if (e.title, b) in ALLOW_E:
            return True
        gs = set(g for _, _, g, _ in h)
        return all(g in ALLOW_W for g in gs)

    def klass(h):
        ks = set(kind_of(s, lab) for s, lab, _, _ in h)
        for k in ('栏', '录', '文', '旧', '问', '凭'):
            if k in ks:
                return k
        return '?'

    todo = [(e, b, h) for e, b, h in rows if SHOW_ALL or not allowed(e, b, h)]
    if WORDS:
        todo = [(e, b, h) for e, b, h in todo if any(w in g for _, _, g, _ in h for w in WORDS)]
    cnt = collections.Counter(klass(h) for _, _, h in todo)
    ent_hit = set((e.file, e.line) for e, _, _ in todo)
    # 在这一纪的回复里中的（这一局里真会醒的那一种口径：样本的纪跟条目的纪一样，或者条目不挡纪元）
    same = [(e, b, h) for e, b, h in todo if any(s.run not in ('骨架', 'moon/samples') and s.role == 'assistant' and (e.era == s.era or e.era == '通用') for s, _, _, _ in h)]
    same_ent = set((e.file, e.line) for e, _, _ in same)
    print('中了的分支 %d 个（放过的 %d 个不算），涉及 %d 条；其中 栏 %d、录 %d、文 %d、只在旧样本 %d、只在玩家的话 %d、只在凭证 %d' % (
        len(todo), len(rows) - len([1 for e, b, h in rows if not allowed(e, b, h)]), len(ent_hit),
        cnt['栏'], cnt['录'], cnt['文'], cnt['旧'], cnt['问'], cnt['凭']))
    print('在同一纪的干跑回复里中的分支 %d 个，涉及 %d 条' % (len(same), len(same_ent)))

    if OUT and OUT is not True:
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, '分支.tsv'), 'w', encoding='utf-8', newline='\n') as w:
            w.write('类\t纪\t文件\t条目\t分支\t中的字\t样本数\t同纪回复\t头一处\n')
            for e, b, h in sorted(todo, key=lambda r: ('栏录文旧问凭?'.index(klass(r[2])), r[0].era, rel(r[0].file), r[0].line)):
                gs = '、'.join(sorted(set(g for _, _, g, _ in h)))[:60]
                sm = sum(1 for s, _, _, _ in h if s.role == 'assistant' and s.rnd and (e.era == s.era or e.era == '通用'))
                s0, lab0, g0, ctx0 = h[0]
                w.write('%s\t%s\t%s\t%s\t%s\t%s\t%d\t%d\t%s｜%s｜%s\n' % (klass(h), e.era, rel(e.file), e.title, b, gs, len(h), sm, s0.name, lab0, ctx0))
        byw = collections.defaultdict(lambda: {'ent': set(), 'smp': set(), 'ctx': None, 'k': set()})
        for e, b, h in todo:
            for s, lab, g, ctx in h:
                d = byw[g]
                d['ent'].add(e.title); d['smp'].add(s.name); d['k'].add(kind_of(s, lab))
                if d['ctx'] is None or kind_of(s, lab) == '栏':
                    d['ctx'] = '%s｜%s｜%s' % (s.name, lab, ctx)
        with open(os.path.join(OUT, '词.tsv'), 'w', encoding='utf-8', newline='\n') as w:
            w.write('中的字\t类\t几份样本\t几条在用\t头一处\t用它的条目\n')
            for g, d in sorted(byw.items(), key=lambda kv: (-len(kv[1]['smp']), kv[0])):
                w.write('%s\t%s\t%d\t%d\t%s\t%s\n' % (g, ''.join(k for k in '栏录文旧问凭' if k in d['k']), len(d['smp']), len(d['ent']), d['ctx'], '；'.join(sorted(d['ent']))[:400]))
        print('写了', os.path.join(OUT, '分支.tsv'), '和 词.tsv')
    else:
        for e, b, h in sorted(todo, key=lambda r: ('栏录文旧问凭?'.index(klass(r[2])), rel(r[0].file), r[0].line))[:400]:
            s0, lab0, g0, ctx0 = h[0]
            print('%s｜%s｜%s｜分支 %s｜%d 份｜%s｜%s｜%s' % (klass(h), rel(e.file), e.title, b, len(h), s0.name, lab0, ctx0))
        if len(todo) > 400:
            print('……还有 %d 个，加 --out 目录 写成表看' % (len(todo) - 400))

    if '--wake' in sys.argv:
        wr = wake_table(entries)
        per = collections.Counter((run, n) for run, n, e, s in wr)
        for (run, n), c in sorted(per.items()):
            print('  醒 %s 轮%d：%d 条' % (run, n, c))
        print('  合计 %d 条次，%d 条不同的条目' % (len(wr), len(set((e.file, e.line) for _, _, e, _ in wr))))
        if UNKNOWN_ALIAS:
            print('  认不出的钥匙（当不中算）：' + '、'.join('%s×%d' % kv for kv in UNKNOWN_ALIAS.most_common(12)))
        if OUT and OUT is not True:
            with open(os.path.join(OUT, '醒.tsv'), 'w', encoding='utf-8', newline='\n') as w:
                w.write('局\t轮\t纪\t文件\t条目\t叫醒它的\n')
                for run, n, e, s in wr:
                    w.write('%s\t%d\t%s\t%s\t%s\t%s\n' % (run, n, e.era, rel(e.file), e.title, s.name))
            print('  写了', os.path.join(OUT, '醒.tsv'))

    if APPLY:
        if SCOPE != '新料':
            print('--apply 只给 --scope 新料 用；全卷的照表一条一条看过再改源稿')
            return
        drop = collections.defaultdict(set)
        for e, b, h in todo:
            if any(kind_of(s, lab) in ('栏', '录', '文', '旧') for s, lab, _, _ in h):
                drop[(e.file, e.line)].add(b)
        n_drop = 0
        for f in sorted(set(k[0] for k in drop)):
            L = open(f, encoding='utf-8', newline='').read().split('\n')      # 行尾照原样留着（仓库里 LF、CRLF 都有）
            for (ff, i), bs in drop.items():
                if ff != f:
                    continue
                head, sep, tail = L[i].partition('黑名单')

                def fix(m):
                    nonlocal n_drop
                    rx = m.group(1)
                    if is_gate(rx):
                        return m.group(0)
                    toks = split_top(rx)
                    keep = [t for t in toks if t not in bs]
                    if len(keep) == len(toks):
                        return m.group(0)
                    if not keep:
                        print('   !! 拿完就空了，没动：', rel(f), i + 1)
                        return m.group(0)
                    n_drop += len(toks) - len(keep)
                    re.compile('|'.join(keep))
                    return '`/' + '|'.join(keep) + '/`'

                L[i] = re.sub(r'`/(.+?)/`', fix, head) + sep + tail
            open(f, 'w', encoding='utf-8', newline='').write('\n'.join(L))
        print('拿掉', n_drop, '个分支')


if __name__ == '__main__':
    main()
