# 11-25 本地干跑修，底卡侧的那一半（tools/dryrun/报告_11-25.md 第 2、3、7、18 条；备注 底稿/收尾_11-25/干跑修/目录条与底卡侧.md）。
# make_four_era_card.py 在机械瘦身以后套 apply()。只动触发词和黑名单，正文一个字不动。
#   一、预载钥匙（preload_extra）
#       · 【战斗栏】（标题「战斗栏｜普通战斗的敌情卡」）认 §预载 的那一支里添「战斗栏」：主提示词里叫它【战斗栏】，原来只认标题后半截。
#       · 【数值机制·06｜伤害公式】添一支认 §预载 的，写「战斗栏」或「伤害公式」都醒。
#       · 这两条另添一支只认玩家的话：玩家写了动兵器的话（举盾、拔剑、一剑横扫、放箭、拿枪把巷口堵住……）当轮就醒，不用等回复写出「战斗：战斗栏」。
#       · 21·委托、奖励与结算 那七条原来只扫玩家的话，照 preload.py「丙」的改法添上认 §预载 的那一支（写「结算台」「委托·结算台」都醒），玩家那一侧照旧认原来的词。
#   二、别纪的门（era_gate）
#       底卡条目挡别纪，是 build_v12.py 拿「纪元：X纪｜开局时段：Y」这一行开局口令去试、叫醒了哪一条就给哪一条挂那一纪的锚；
#       11-17 起建档页出的是整份凭证，里头每一份都有的几句（「旅印：无（这一纪没有旅印…）」、命星那一行的「迷宫纪1001年叫某某」）那时候没试过，所以漏了。
#       这里照表补：GATE 一条一条点名，FOLDER_GATE 整个文件夹。锚的写法跟卡里现成的一样（瘦身以后的样子）。
#       · 种族那一组（08）另挂一条黑名单：建档凭证里只认【二·种族胎骨】那一节写的族，命星说明、出身里顺口带到的族名不叫醒那一族的条目。
#       · 1001 年老建档页的凭证头一行没有「纪元：」、也没有「旅印」两个字，旅印权限表头一轮醒不了，给它添一支认这种凭证的。
#   三、1001 年的目录条（index_1001）：底稿/DLC/tools/make_index.py 出的那几条，触发改成跟 1001 年常驻一样（1001 年以后的底座，或者不带别纪纪元的凭证）。
#   四、核对：拿 slim_card.cases 的凭证补上建档页写死的套话（身穿、本地各一份）和回复底座，列别纪头一轮里还醒着的底卡侧条目，写进输出目录的 别纪头一轮_底卡.txt；
#       拿 make_index 的算法对一遍卡里的目录条，跟现在该出的不一样就提醒重跑。
import collections
import os
import re
import sys

import preload as PL
import prompt_stage1 as PS1
import slim_card as SC

NB = 1397
ERAS = ['月银纪', '纷争纪', '山铜纪', '迷宫纪']
ANCHOR = {'月银纪': '纪元：月银纪', '纷争纪': '纪元：纷争纪', '山铜纪': '纪元：山铜纪',
          '迷宫纪': '/纪元：迷宫纪(?:[2-9]|[1-9]\\d|[1-9]\\d\\d|1000)年|纪元：迷宫纪｜开局时段：/'}

# ---------------- 一、预载钥匙 ----------------
EXTRA_KEYS = [('战斗栏｜普通战斗的敌情卡', ['战斗栏']), ('数值机制·06｜伤害公式', ['战斗栏', '伤害公式'])]
FOLDER_COMM = '21·委托、奖励与结算'
# 玩家这一句里动兵器的话。建档凭证（命星说明里有招架、反击这些字）和回复不算。
NOT_REPLY = r'(?![\s\S]{0,4000}(?:§底座|§推演|hud-meta|<details|命途已确认))'
WEAPON = '盾|剑|刀|枪|矛|戟|斧|锤|弓|弩|杖|匕首'
FIGHT = ('举盾|架盾|顶盾|拔剑|拔刀|抽剑|抽刀|出鞘|一剑|一刀|一枪|一矛|一斧|一锤|一箭|一拳|横扫|横斩|劈过去|劈下去|砍过去|砍下去|砍向|刺过去|刺向|捅过去|斩向|斩下去|'
         '放箭|专射|射向|射过去|砸过去|轰过去|开打|打起来|迎战|开战|应战|接战|反击|还击|杀过去|冲锋|'
         '(?:%s)[^，。？\\n]{0,8}(?:堵住|拦住|挡住|顶住|架住|逼住|指着|对准|抵住)' % WEAPON)
COMBAT_RX = '/^%s[\\s\\S]{0,1500}(?:%s)/' % (NOT_REPLY, FIGHT)
COMBAT_FOR = ['战斗栏｜普通战斗的敌情卡', '数值机制·06｜伤害公式']       # 伤害公式那一条五千字，嫌白醒的话从这里拿掉它，预载钥匙照留

# ---------------- 二、别纪的门 ----------------
ALL4 = ERAS
# (标题开头, 补挡哪几纪, 缘故)。已经挂着的不重复挂。
GATE = [
    ('双王与迷宫纪年表', ALL4, '凭证命星那一行的「迷宫纪1001年叫某某」中了纯词 迷宫纪'),
    ('垂暮和平｜迷宫纪1001年', ALL4, '同上'),
    ('迷宫纪｜最好的时代', ALL4, '同上'),
    ('黑潮战史｜迷宫纪850', ALL4, '同上'),
    ('冒险者旅印总则｜', ALL4, '凭证【七】每一份都有「旅印：」那一行；前传有自己的 规则｜旅印'),
    ('旅印等级权限表｜', ALL4, '同上'),
    ('旅印晋升与处分', ALL4, '同上'),
    ('冒险者公会旅印纹章外观', ALL4, '同上'),
    ('委托·完成不等于合法｜', ALL4, '同上，触发里有纯词 旅印'),
    ('本版可建档种族（前端十族）', ALL4, '凭证每一份都有【二·种族胎骨】；写的是 1001 年前端的十族和黑潮以后这一代人，四纪各有自己的 规则｜建档的种族'),
]
# 整个文件夹，只挡月银纪、纷争纪、山铜纪（前传跟 1001 年是同一纪，不整组挡，只点名挡上面那几条）：
#   委托那一组：这三纪没有公会和委托板；
#   势力、城和据点、自然地理三组：写的是 1001 年今天的样子（人口、列车、飞艇坪、今天谁当家），这三纪各有自己的势力、城邦、地点条目。
#   干跑月银纪那一局，凭证里学派写了「熔铁炉心的炉城」，叫进来的是 1001 年的矮人王国、熔铁炉心和金鸢工坊区。
#   只挡得住带着纪元的那一条消息（凭证、带底座的回复里的 §预载）；玩家后来的话里没有纪元，照旧会叫醒，这是平台一条消息一条消息分开算定的。
PRE3 = ['月银纪', '纷争纪', '山铜纪']
FOLDER_GATE = collections.OrderedDict([
    (FOLDER_COMM, (PRE3, '这三纪没有公会和委托板')),
    ('11·势力、政体与法度', (PRE3, '写的是 1001 年今天的势力，这三纪各有自己的势力条目')),
    ('13·城市、据点与设施', (PRE3, '写的是 1001 年今天的城，这三纪各有自己的城邦和地点条目')),
    ('14·自然地理与遗址', (PRE3, '写的是 1001 年今天的地方，这三纪各有自己的地点条目')),
])
FOLDER_RACE = '08·种族、血脉与寿命'
RACE_SKIP = ('胎骨',)          # 认「胎骨」两个字的那一条（本版可建档种族）在 1001 年的凭证里照旧醒
CRED_1001_OLD = '/^(?![\\s\\S]{0,300}纪元：)[\\s\\S]{0,60}命途已确认/'
CRED_1001_FOR = ['旅印等级权限表｜']
# 别纪凭证的套话叫醒了也算对的（四纪通用的规矩、建档那一步要用的）。标题开头；92 号文件夹（命运骰）整组算。
KEEP = ['首轮入局驱动', '输出模板·完整版', '冒险初心｜', '誓心｜', '六维属性', '位阶：', '数值机制·', '装备换算｜', '通用Skill底层运转逻辑', '穿越者的地球知识｜',
        '真相层·降临者', '世界自转', '冒险者面板与公会秘仪']
KEEP_WHY = {
    '真相层·降临者': '降临能落在月银纪到迷宫纪之间的任何一刻，四纪的降临者都用这一条；只给 AI',
    '冒险者面板与公会秘仪': '前传 420 年以后才有面板觉醒，凭证写着去公会觉醒面板的那几年醒，对',
    '穿越者的地球知识｜': '身穿的凭证才醒，四纪通用',
    '世界自转': '低概率的加权条目，认一个「的」字，哪一纪都在',
}
INDEX_1001 = re.compile(r'目录｜这一年问了才醒|目录｜[^\n]*（迷宫纪1001年）|大图书馆｜目录·迷宫纪1001年')


def title_of(e):
    first = (e.get('content') or '').lstrip().split('\n', 1)[0]
    return re.sub(r'^#+\s*', '', first).strip()


def is_index(t):
    """make_index.py 出的目录条。"""
    return '目录｜' in t or t.startswith('大图书馆｜目录·')


def folder_no(e):
    m = re.match(r'(\d+)·', e.get('folder') or '')
    return int(m.group(1)) if m else -1


def base_side(lb):
    return [i for i, e in enumerate(lb) if 0 <= folder_no(e) < 40 or folder_no(e) >= 90]


def find(lb, prefix, nb=NB):
    hit = [i for i in range(min(nb, len(lb))) if title_of(lb[i]).startswith(prefix)]
    assert len(hit) == 1, ('底卡里照标题找不到，或者不止一条', prefix, hit)
    return hit[0]


def _add_preload(e, names):
    """认 §预载 的那一支里添名字；没有那一支就添一支。回添了几个。"""
    tw = list(e.get('triggerWords') or [])
    for k, w in enumerate(tw):
        m = re.match(r'^(/§预载｜\[\^\\n\]\{0,400\}\(\?:)(.*)(\)/)$', w, re.S)
        if m:
            have = m.group(2).split('|')
            add = [PL.esc(n) for n in names if PL.esc(n) not in have]
            if add:
                tw[k] = m.group(1) + '|'.join(add + have) + m.group(3)
                e['triggerWords'] = tw
            return len(add)
    e['triggerWords'] = tw + [r'/§预载｜[^\n]{0,400}(?:%s)/' % '|'.join(PL.esc(n) for n in names)]
    if 'assistant' not in (e.get('triggerRange') or []):
        e['triggerRange'] = list(e.get('triggerRange') or []) + ['assistant']
    e['scanDepth'] = max(int(e.get('scanDepth') or 1), 2)
    return len(names)


def comm_names(title):
    """委托·结算台｜回来之后 → 委托·结算台、结算台。"""
    head = re.sub(r'（[^）]*）', '', title.split('｜', 1)[0]).strip()
    out = [head] + [x for x in head.split('·')[1:] if len(x) >= 3]
    return list(dict.fromkeys(out))


def preload_extra(lb, nb=NB):
    """回 {'钥匙': n, '委托': n, '动兵器': n}。套过一回再套不重复添。"""
    st = collections.Counter()
    for prefix, names in EXTRA_KEYS:
        st['钥匙'] += _add_preload(lb[find(lb, prefix, nb)], names)
    for prefix in COMBAT_FOR:
        e = lb[find(lb, prefix, nb)]
        if COMBAT_RX not in e['triggerWords']:
            assert (e.get('triggerWordsType') or 'OR') == 'OR' and set(e.get('triggerRange') or []) == {'user', 'assistant'}, prefix
            e['triggerWords'] = list(e['triggerWords']) + [COMBAT_RX]
            st['动兵器'] += 1
    for i in range(min(nb, len(lb))):
        e = lb[i]
        if e.get('folder') != FOLDER_COMM:
            continue
        words = [w for w in e.get('triggerWords') or [] if w]
        if any(w.startswith('/§预载') for w in words):
            continue
        assert e.get('triggerRange') == ['user'] and (e.get('triggerWordsType') or 'OR') == 'OR' and not any(w.startswith('/') for w in words), ('委托那一组的触发变了样', i)
        names = [n for n in comm_names(title_of(e)) if n not in words]
        e['triggerWords'] = [r'/§预载｜[^\n]{0,400}(?:%s)/' % '|'.join(PL.esc(w) for w in names + words),
                             r'/^%s[\s\S]{0,3000}(?:%s)/' % (PL.NOT_REPLY, '|'.join(PL.esc(w) for w in words))]
        e['triggerRange'] = ['user', 'assistant']
        e['scanDepth'] = max(int(e.get('scanDepth') or 1), 2)
        st['委托'] += 1
    return dict(st)


def _add_bl(e, words):
    assert (e.get('blackListWordsType') or 'OR') == 'OR' or not e.get('blackListWords'), ('原有黑名单是同时满足，不能直接追加', title_of(e))
    bl = list(e.get('blackListWords') or [])
    add = [w for w in words if w not in bl]
    if add:
        e['blackListWords'] = bl + add
        e['blackListWordsType'] = 'OR'
        assert len(e['blackListWords']) <= 20, ('黑名单超过二十个', title_of(e))
    return len(add)


def era_gate(lb, nb=NB):
    """回 [(下标, 标题, 添了哪几纪, 缘故)]。"""
    # 锚的写法要跟卡里现成的一样：前传那一条卡里应当有三百多条在用
    n_pre = sum(1 for i in range(min(nb, len(lb))) if ANCHOR['迷宫纪'] in (lb[i].get('blackListWords') or []))
    assert n_pre >= 100, ('挡前传的那一条黑名单在卡里对不上了（瘦身的写法变了？）', n_pre)
    log = []
    for prefix, eras, why in GATE:
        i = find(lb, prefix, nb)
        bl0 = list(lb[i].get('blackListWords') or [])
        if _add_bl(lb[i], [ANCHOR[x] for x in eras]):
            log.append((i, title_of(lb[i]), [x for x in eras if ANCHOR[x] not in bl0], why))
    for folder, (eras, why) in FOLDER_GATE.items():
        for i in range(min(nb, len(lb))):
            e = lb[i]
            if e.get('folder') != folder or not [w for w in e.get('triggerWords') or [] if w]:
                continue
            bl0 = list(e.get('blackListWords') or [])
            add = [x for x in eras if ANCHOR[x] not in bl0]
            if not add:
                continue
            if (bl0 and (e.get('blackListWordsType') or 'OR') != 'OR') or len(bl0) + len(add) > 20:
                log.append((i, title_of(e), [], '没挡成：原有黑名单是同时满足，或者添上就过二十个（' + folder + '）'))
                continue
            _add_bl(e, [ANCHOR[x] for x in add])
            log.append((i, title_of(e), add, '整个文件夹：' + why))
    return log


def race_gate(lb, nb=NB):
    """种族那一组：凭证里只认【二·种族胎骨】那一节。回改了几条。"""
    n = 0
    for i in range(min(nb, len(lb))):
        e = lb[i]
        if e.get('folder') != FOLDER_RACE or e.get('triggerRange') != ['user'] or (e.get('triggerWordsType') or 'OR') != 'OR':
            continue
        words = [w for w in e.get('triggerWords') or [] if w]
        if not words or any(w.startswith('/') for w in words) or any(s in w for w in words for s in RACE_SKIP):
            continue
        rx = '/命途已确认[\\s\\S]{0,2000}【二·种族胎骨】(?![^【]{0,300}(?:%s))/' % '|'.join(PL.esc(w) for w in words)
        re.compile(rx[1:-1])
        if len(rx) > 1000:
            continue
        n += _add_bl(e, [rx])
    return n


def cred_1001(lb, nb=NB):
    n = 0
    for prefix in CRED_1001_FOR:
        e = lb[find(lb, prefix, nb)]
        if CRED_1001_OLD not in e['triggerWords']:
            assert (e.get('triggerWordsType') or 'OR') == 'OR', prefix
            e['triggerWords'] = list(e['triggerWords']) + [CRED_1001_OLD]
            n += 1
    return n


# ---------------- 三、1001 年的目录条 ----------------
def index_1001(lb):
    n = 0
    for e in lb:
        if INDEX_1001.search(title_of(e)):
            e['triggerWords'] = [PS1.ERA_1001, PS1.CRED]
            e['triggerWordsType'] = 'OR'
            e['blackListWords'] = list(PS1.BLACK)
            e['blackListWordsType'] = 'OR'
            e['triggerRange'] = ['user', 'assistant']
            e['scanDepth'] = max(2, int(e.get('scanDepth') or 2))
            n += 1
    return n


# ---------------- 四、核对 ----------------
HEAD = '命途已确认，请记录我的《奥尔德兰》角色建档：'
NOTE = '※ 凡标注「未记录／未选择」的项，由 AI 在首轮按已确定的内容补全，并在开场时用一句话说明补了哪些。'


def _seal(era, y, isk):
    """建档页 shell.js sealInfo() 各纪各年写进凭证的那一句。"""
    y = y or 9999
    if era == '月银纪':
        return '无（月银纪没有旅印，诗人还没唱你的名字）'
    if era == '纷争纪':
        return '无（233年以前还没有军册）' if y < 233 else '无（这一纪没有旅印，墙上认军册，名字、姓或家、族三栏见出身那一行）'
    if era == '山铜纪':
        return '无（这一纪没有旅印，30年前后才有头一个有名字的团）' if y < 30 else '无（这一纪没有旅印）｜还没有团' + ('｜行会的档次 没挂号' if y >= 60 else '')
    if y < 3:
        return '无（3年霜降月以前还没有公会）'
    if y < 420:
        return ('白石旅印' if y < 20 else '山铜旅印') + '（不分阶）｜公会的档次 还没入会' + ('｜担保 未写' if y >= 7 else '')
    return '无印（未登记）' if isk else '见习'


def full_cred(era, y, open_line, where, isk):
    """一份只有套话的整份凭证：建档页 credential() 每一份都会写的句子，玩家自己挑的东西一样不带。"""
    panel = era == '迷宫纪' and (y or 0) >= 420
    L = [open_line, '', HEAD, '', '【一·灵魂形态】']
    L += ['降临之魂 · 身穿（连人带身跌入）', '来处：未详述（降临者报不出这里的出身）'] if isk else ['本地之魂（生于此世）', '金血：无']
    L += ['', '【二·种族胎骨】', '未选择', '', '【三·命路倾向】']
    if era == '月银纪':
        L += ['兵器：未认兵', '法门与手艺：未选择｜学派：未选择', '职业格：未认兵（这一纪没有命路，认人看兵器和哪一家教的）']
    else:
        L += ['未选择（由 AI 照这一纪的本事和我的来处定一个方向）']
    L += ['', '【四·姓名容貌】', '姓名：某某', '年龄：未填写（' + ('落地多大就多大，' if isk else '') + '由 AI 按容貌与经历定一个，开场用一句话说明，不得默认十八岁）', '性别：未填写', '容貌：未详述',
          '体态数据：身高 未记录（由AI按种族与出身补全）｜体型 未记录（由AI补全）　（静态资产，状态栏逐轮照抄，正文不主动报数）', '立绘：无', '自定义设定：（无）',
          '初始实力：启源·初识（启源位阶 · 初识能级｜LVL 1-7）｜' + ('面板照得出' if panel else era + '看得出的') + '：还没做成过什么', NOTE, '', '【五·命星天赋】',
          'Passive/Special：某一颗星(Special | Epic)：Special。说明一句。　%s：这一纪的说明一句。　迷宫纪1001年叫另一个名字｜Passive 未选择（照这一纪的规矩来，由 AI 补一颗，开场说明）' % era,
          'Art/Active：某一门技艺(Art | Rare)：Art。说明一句。　%s：这一纪的说明一句。　迷宫纪1001年叫另一门技艺' % era,
          '', '【六·誓心与赐物】' if isk else '【六·誓心与出身】', '誓心阵营：随便（由世界照我的来处推一个，开场明说是推的）', '出身：登记｜名字 某某',
          '这一段的本事：未选择（由 AI 照这一纪的本事和我的来处定一个方向）']
    if isk:
        L += ['神殿赐物：未选择（拒绝了她的馈赠）']
    L += ['六维（起点给的底子＋自由分配）：STR 15（上限30） / DEX 15（上限30） / MANA 15（上限30） / MIND 15（上限30） / VGR 15（上限30） / FTH 15（上限30）', '当前分配：90/90｜六维总上限：180',
          '属性经验：各项从0起，阈值＝属性×100｜潜力：各项100%（建档起点，下限10%，上不封顶）', '单项上限依据：启源位阶（单项基础上限30）',
          '攻防与装备：建档未写定，首轮照骨架的算法结算 ATK、PV、DV，主手、副手写 名〔品阶·类型·×修正〕，甲写 名〔品阶·轻/中/重·耐久%〕，没有就写无｜' + (
              '开局只有穿越时身上那一套，没有别的兵器' if isk else '照起点与' + ('兵器' if era == '月银纪' else '命路') + '配一套跟这一纪相称的装备，开场一句话说明'),
          '【面板状态】' + (('尚未觉醒，开局先去公会登记、觉醒面板。' if isk else '尚未觉醒，开局先去公会完成成年登记与面板觉醒。') if panel else '这一年没有面板，位阶、六维和命星照旧在底座里记，这一纪的人看不见。'), '',
          '【七·现在何处】', '现在所在：' + where, '当前处境：' + ('刚从死之神殿落下来，身上只有穿越时那一身。' if isk else '这一纪生下来的人，从这一条主线的开局起头。'),
          '旅印：' + _seal(era, y, isk), '', '【八·冒险初心】', '还没想好（先走着看，头一轮不必追问）', '', '开始游戏。', '', '入局：先补前半生']   # 11-26 外壳凭证末尾添的这一行
    return '\n'.join(L)


def creds(root):
    """[(纪, 名, 凭证, 回复或 None)]：slim_card.cases 的每一种，身穿、本地各一份；1001 年那一份原样。"""
    out = []
    for era, name, old, new, reply in SC.cases(root):
        if era not in ERAS:
            out.append((era, name, old, None))
            continue
        open_line = new.split('\n', 1)[0]
        m = re.search(r'现在所在：([^\n]*)', new)
        ym = re.search(r'纪元：%s(元|\d+)年' % era, open_line)
        y = (1 if ym.group(1) == '元' else int(ym.group(1))) if ym else None
        for isk in (True, False):
            out.append((era, name + ('·身穿' if isk else '·本地'), full_cred(era, y, open_line, m.group(1) if m else '', isk), reply if isk else None))
    return out


def _woke(e, msg, role):
    if not e.get('enabled', True) or role not in (e.get('triggerRange') or []):
        return False
    return SC._hit(e.get('triggerWords'), e.get('triggerWordsType'), msg) and not SC._hit(e.get('blackListWords'), e.get('blackListWordsType'), msg)


def cred_sim(lb, root):
    """回 (各纪凭证数, {下标: {纪: 醒了几种凭证}}, {下标: {纪: 几种回复}})，只看底卡侧（文件夹号 40 以下、90 以上）。"""
    idx = base_side(lb)
    by = collections.defaultdict(collections.Counter)
    byr = collections.defaultdict(collections.Counter)
    n = collections.Counter()
    for era, name, cred, reply in creds(root):
        n[era] += 1
        for i in idx:
            if _woke(lb[i], cred, 'user'):
                by[i][era] += 1
            if reply and _woke(lb[i], reply, 'assistant'):
                byr[i][era] += 1
    return n, by, byr


def keep_of(e):
    if folder_no(e) >= 90:
        return '功能开关，哪一纪都用'
    t = title_of(e)
    for k in KEEP:
        if t.startswith(k):
            return KEEP_WHY.get(k, '四纪通用的规矩，建档那一轮要用')
    if is_index(t):
        return '目录条，这一纪的局里常驻'
    return None


def report(lb, root, path=None):
    """别纪头一轮里还醒着的底卡侧条目，分「该醒」「没分过类」。回 (行, 没分过类的条数)。"""
    n, by, byr = cred_sim(lb, root)
    L = ['# 别纪头一轮里醒的底卡侧条目（gate_1125.report；凭证 %s，一种凭证身穿、本地各一份，只带建档页写死的套话）' % '、'.join('%s %d' % kv for kv in n.items()),
         '# 下标\t文件夹\t标题\t字数\t各纪醒了几种凭证\t该不该醒']
    unknown = 0
    for i in sorted(by):
        e = lb[i]
        eras = {k: v for k, v in by[i].items() if k in ERAS}
        if not eras:
            continue
        why = keep_of(e)
        if not why:
            unknown += 1
        L.append('#%d\t%s\t%s\t%d\t%s\t%s' % (i, e.get('folder'), title_of(e)[:40], len(e.get('content') or ''), '，'.join('%s %d/%d' % (k, eras[k], n[k]) for k in ERAS if k in eras),
                                           why or '没分过类：看一眼该不该醒，该醒添进 gate_1125.KEEP，不该醒添进 GATE'))
    L.append('# 回复底座（只有底座加一句正文）叫醒的底卡侧条目')
    for i in sorted(byr):
        eras = {k: v for k, v in byr[i].items() if k in ERAS}
        if eras:
            L.append('#%d\t%s\t%s\t%d\t%s\t%s' % (i, lb[i].get('folder'), title_of(lb[i])[:40], len(lb[i].get('content') or ''), '，'.join('%s %d' % kv for kv in eras.items()),
                                               keep_of(lb[i]) or '没分过类'))
    if path:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(L) + '\n')
    return L, unknown


def check_index(lb, root):
    """卡里的目录条跟 make_index 现在该出的比。回 (少了的, 不一样的, 卡里一共几条)。"""
    d = os.path.join(root, '底稿', 'DLC', 'tools')
    if d not in sys.path:
        sys.path.insert(0, d)
    import make_index as MI
    exp = MI.expected(lb)
    norm = lambda s: '\n'.join(l.rstrip() for l in s.split('\n') if l.strip())
    have = {}
    for e in lb:
        t = title_of(e)
        if is_index(t):
            have[t] = norm((e.get('content') or '').split('\n', 1)[1] if '\n' in (e.get('content') or '') else '')
    miss = [t for t in exp if t not in have]
    diff = [t for t in exp if t in have and norm(exp[t]) != have[t]]
    return miss, diff, len(have)


# ---------------- 五、格式刷新的口语叫法（11-26 格式崩坏核对） ----------------
# 玩家不按菜单里的「格式刷新」，自己打一句“格式乱了，修一下”的时候，【格式刷新】那一条原来醒不了，模型没有章法，照着坏掉的上一条乱修。
# 添几个口语的说法（只扫玩家这一句，深度照旧 1），条目里【调用】那一句也认这种话（four_era_prompt.DRIVER_EDITS[1396]）
REFRESH_TITLE = '功能命令｜格式刷新'
REFRESH_WORDS = ['格式乱', '格式错', '格式崩', '格式坏', '格式出错', '修复格式', '格式修复', '修一下格式', '重整格式', '整理格式',
                 '状态栏乱', '状态栏错', '状态栏崩', '状态栏坏', '界面乱', '界面崩', '界面坏', 'UI乱', 'UI崩', 'ui乱', 'ui崩', '显示错误', '面板乱了', '串台']


def refresh_words(lb, nb=NB):
    e = lb[find(lb, REFRESH_TITLE, nb)]
    add = [w for w in REFRESH_WORDS if w not in e['triggerWords']]
    e['triggerWords'] = e['triggerWords'] + add
    return len(add)


def apply(lb, nb=NB, root=None, outdir=None):
    st = {'预载': preload_extra(lb, nb)}
    st['格式刷新口语'] = refresh_words(lb, nb)
    log = era_gate(lb, nb)
    st['别纪的门'] = len(log)
    st['门的细目'] = log
    st['种族只认胎骨那一节'] = race_gate(lb, nb)
    st['1001老凭证'] = cred_1001(lb, nb)
    st['1001目录条'] = index_1001(lb)
    if root:
        L, unknown = report(lb, root, os.path.join(outdir, '别纪头一轮_底卡.txt') if outdir else None)
        st['别纪头一轮还醒'] = len([x for x in L if x.startswith('#') and not x.startswith('# ')])
        st['没分过类'] = unknown
        miss, diff, n = check_index(lb, root)
        st['目录条'] = (n, miss, diff)
    return st
