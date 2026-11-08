# 大框各页的样式（11-04，用户要各模块像游戏界面：有自己的元素、不累眼、看着惊艳）。make_css_frame.py 读进去，占位符由它换。
# 路子：平时只看图标和大数字，细节悬停或点开才出；不再框中套框、不再满屏虚线；一页一个主角（面板是人和部位，背包是格子，伟业是天赋盘，
# 同行是立绘，见闻是一块告示板，记忆是分类的记事簿，战斗是敌人）。道具图是一张雪碧图，样式按道具名里的字认图标，AI 不用写图标名。
# 第六行是记忆和见闻各类的小标（MARKS）。立绘表 portraits.json 是从现卡的样式里抄的（短名 → 图地址），新图往里添。
import json
import os
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))

# 雪碧图 12 列 6 行，排法见 comfy/gpt_icons.py；后写的盖先写的，所以越具体的词越往后放，武器和衣服盖过材料
ICONS = [
    ((10, 4), []),
    ((7, 3), ['牙', '骨', '爪', '角']), ((0, 3), ['矿', '石']), ((1, 3), ['锭', '铁块', '钢块']), ((2, 3), ['晶', '魔石', '宝石']), ((3, 3), ['木', '柴']),
    ((4, 3), ['皮毛', '兽皮', '毛皮', '皮料']), ((5, 3), ['线', '绳', '布料']), ((6, 3), ['瓶']), ((8, 3), ['鳞']), ((9, 3), ['羽']), ((10, 3), ['菇']), ((11, 3), ['磨刀']),
    ((1, 2), ['肉']), ((0, 2), ['饼', '面包', '粮']), ((2, 2), ['水囊', '皮囊', '水壶', '水袋']), ((3, 2), ['药', '血']), ((4, 2), ['魔力', '法力', '以太']), ((5, 2), ['解毒', '毒']),
    ((6, 2), ['草', '叶', '花']), ((7, 2), ['绷带']), ((8, 2), ['火把']), ((9, 2), ['灯', '烛']), ((10, 2), ['酒']), ((11, 2), ['果']),
    ((5, 4), ['钱', '币']), ((3, 4), ['图']), ((1, 4), ['信', '凭条', '文书', '契', '委托', '纸']), ((0, 4), ['卷', '残页']), ((2, 4), ['书', '册', '手册', '笔记']), ((4, 4), ['钥']),
    ((7, 4), ['撬', '开锁']), ((8, 4), ['牌', '身份']), ((9, 4), ['匣', '箱', '盒']), ((11, 4), ['遗物', '残片', '碑']),
    ((11, 1), ['衣', '裤', '衫', '内衬']), ((10, 1), ['徽', '章', '扣', '印']), ((9, 1), ['链', '坠', '护符', '怀表', '颈']), ((8, 1), ['戒']), ((7, 1), ['腰带', '束腰']), ((6, 1), ['斗篷', '披风', '外套']),
    ((5, 1), ['靴', '鞋']), ((4, 1), ['手套', '护手']), ((3, 1), ['盔', '帽', '冠']), ((2, 1), ['袍', '法衣', '制服']), ((0, 1), ['甲', '铠']), ((1, 1), ['皮甲', '硬皮', '皮护']),
    ((0, 0), ['剑']), ((1, 0), ['匕', '短刀', '短刃']), ((6, 4), ['小刀', '折叠刀']), ((2, 0), ['枪', '矛', '戟']), ((3, 0), ['斧']), ((4, 0), ['锤', '槌']), ((5, 0), ['弓']), ((9, 0), ['弩']),
    ((6, 0), ['杖']), ((7, 0), ['盾']), ((8, 0), ['大剑', '巨剑']), ((10, 0), ['铳', '火枪']), ((11, 0), ['法书', '魔导书', '咒语书']),
    ((7, 3), ['碎骨', '骨片', '黑牙', '獠牙']), ((10, 1), ['旅印', '银印', '铜印', '金印']),
    # 月银纪的家当：曜核、称过的银块、盐砖、封核的月银罐、仓签、狼皮、金痂、镰刀
    ((2, 3), ['曜核']), ((1, 3), ['银块']), ((0, 3), ['盐砖']), ((6, 3), ['月银罐']), ((3, 3), ['仓签']), ((4, 3), ['狼皮']), ((11, 4), ['金痂']), ((3, 0), ['镰']),
    # 纷争纪的军需：上弦钥匙、晶匣、令哨、硬饼、白烛、肋骨、名单
    ((9, 4), ['晶匣']), ((10, 1), ['令哨', '铜铃']), ((7, 3), ['肋骨']), ((1, 4), ['名字']),
    # 山铜纪的家当：山铜铆钉和碎块、揭下来的活、灰之魔女的约、旗角、老滩的盐、旧机兵的指节、熏鱼
    ((1, 3), ['铆钉', '山铜碎块']), ((1, 4), ['揭下来的活', '的约', '熏鱼的凭条']), ((5, 3), ['旗角']), ((0, 3), ['盐']), ((7, 3), ['指节']), ((1, 0), ['烙铁']),
]
PART = {'主手': (0, 0), '副手': (7, 0), '甲': (0, 1), '外层': (6, 1), '内层': (11, 1), '足': (5, 1), '配饰': (9, 1), '饰品': (8, 1)}
SPOT = {'主手': (0, 0), '甲': (0, 1), '外层': (0, 2), '内层': (0, 3), '副手': (1, 0), '配饰': (1, 1), '饰品': (1, 2), '足': (1, 3), '饰品二': (.74, 2)}
FILT = {'全部': (10, 4), '未装备': (0, 0), '消耗': (3, 2), '贵重': (9, 4), '材料': (2, 3), '不可丢弃': (8, 4)}
QUAL = [('#7d8088', ['粗糙', '破损', '低劣']), ('#5fae7b', ['优', '精良', 'Uncommon']), ('#4f8fd8', ['稀有', 'Rare']), ('#a06be0', ['史诗', 'Epic', '名器']),
        ('#e0a63c', ['传说', '传奇', 'Legend']), ('#e25a4e', ['神话', '神器', '遗物', 'Unique'])]
ORDER = ['未装备', '消耗', '贵重', '材料', '不可丢弃']
ABC = ['命星', 'Art', 'Passive', 'Active', 'Skill', '职业能力']
ABIC = {'命星': "M16 2l3.2 10.8L30 16l-10.8 3.2L16 30l-3.2-10.8L2 16l10.8-3.2z", 'Art': "M4 7c4-2 8-2 12 0c4-2 8-2 12 0v19c-4-2-8-2-12 0c-4-2-8-2-12 0zM16 7v19",
        'Passive': "M16 3l11 4v9c0 7-5 11-11 13C10 27 5 23 5 16V7z", 'Active': "M18 2L6 18h8l-2 12 14-18h-9z",
        'Skill': "M26 3l3 3-14 14-3-3zM11 18l3 3-3 3 2 2-2 2-2-2-3 3-2-2 3-3-2-2 2-2 2 2z", '职业能力': "M16 2l4 7h8l-4 7 4 7h-8l-4 7-4-7H4l4-7-4-7h8z"}
TIERN = ['启源', '共鸣', '灵格', '极境', '英雄', '传奇', '凡极']
THREAT = [('碾压', '#6fa86f'), ('占优', '#8fae5f'), ('相当', '#c9b15a'), ('棘手', '#d98f4a'), ('危险', '#d9603f'), ('致命', '#c8324a')]
MARKS = {'核心': 0, '未结因果': 1, '短期': 2, '长期': 3, '已完成': 4, '修正': 5, '全部': 6, '在办': 7, '已知情报': 8, '流言风闻': 9, '可接': 10, '线索': 11}
MEMC = [('核心', 'mc', '#f0cf7e'), ('未结因果', 'my', '#ef8f5c'), ('短期', 'ms', '#7fc0e6'), ('长期', 'ml', '#a99bea'), ('已完成', 'md', '#86c79a'), ('修正', 'mf', '#a8a8b4')]
NT = ['形象', '关系', '属性', '行装', '能力']
CHARM = [('平平', '#8f8f99'), ('耐看', '#6fa883'), ('出众', '#5f9bdc'), ('惊艳', '#a877e6'), ('绝世', '#e5aa3a')]
CRED = [('低', 1, '#d9735a'), ('中', 2, '#d9b45a'), ('高', 3, '#7fc08f'), ('极高', 4, '#6fd0b0')]


def _svg(body, vb='0 0 32 32'):
    s = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='%s'>%s</svg>" % (vb, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' -.,()")


def ring():
    """面板那个人背后慢慢转的星盘"""
    t = ''.join("<path d='M100 %s v%s' transform='rotate(%d 100 100)'/>" % ('4' if a % 30 == 0 else '6', '8' if a % 30 == 0 else '4', a) for a in range(0, 360, 6))
    st = ''.join("<path d='M100 26l1.6 5 5 1.6-5 1.6-1.6 5-1.6-5-5-1.6 5-1.6z' transform='rotate(%d 100 100)' fill='#e9cf8a' stroke='none'/>" % a for a in range(0, 360, 60))
    return _svg("<g fill='none' stroke='#d6b26a' stroke-width='.7'><circle cx='100' cy='100' r='97'/><circle cx='100' cy='100' r='84' stroke-dasharray='1 5'/><circle cx='100' cy='100' r='68' stroke-opacity='.55'/>"
                "<path d='M100 32L159 134H41zM100 168L41 66H159z' stroke-opacity='.35'/>%s</g>%s" % (t, st), '0 0 200 200')


def hexgrid():
    pts = lambda r: ' '.join('%.1f,%.1f' % p for p in [(50, 50 - r), (50 + r * .866, 50 - r / 2), (50 + r * .866, 50 + r / 2), (50, 50 + r), (50 - r * .866, 50 + r / 2), (50 - r * .866, 50 - r / 2)])
    return _svg("<g fill='none' stroke='#d6b26a'><polygon points='%s' stroke-opacity='.55' stroke-width='.7' fill='#d6b26a' fill-opacity='.05'/><polygon points='%s' stroke-opacity='.28' stroke-width='.5'/><polygon points='%s' stroke-opacity='.28' stroke-width='.5'/>"
                "<path d='M50 3V97M9.3 26.5L90.7 73.5M9.3 73.5L90.7 26.5' stroke-opacity='.2' stroke-width='.5'/></g>" % (pts(47), pts(31.3), pts(15.7)), '0 0 100 100')


HEX = 'polygon(50% 0,100% 25%,100% 75%,50% 100%,0 75%,0 25%)'


def radar_clip():
    r = lambda n: 'calc(var(--a%d) / var(--M))' % n
    p = [('50%', 'calc(50%% - 47%% * %s)' % r(1)), ('calc(50%% + 40.7%% * %s)' % r(2), 'calc(50%% - 23.5%% * %s)' % r(2)), ('calc(50%% + 40.7%% * %s)' % r(3), 'calc(50%% + 23.5%% * %s)' % r(3)),
         ('50%', 'calc(50%% + 47%% * %s)' % r(4)), ('calc(50%% - 40.7%% * %s)' % r(5), 'calc(50%% + 23.5%% * %s)' % r(5)), ('calc(50%% - 40.7%% * %s)' % r(6), 'calc(50%% - 23.5%% * %s)' % r(6))]
    return 'polygon(' + ','.join('%s %s' % q for q in p) + ')'


def tables():
    out = []
    w = out.append
    for (x, y), kws in ICONS:
        if kws:
            w(','.join('.sz-it[data-n*="%s"]' % k for k in kws) + '{--ix:%d;--iy:%d}' % (x, y))
    for s, (x, y) in PART.items():
        w('.sz-sk[data-s="%s"]{--ix:%d;--iy:%d}' % (s, x, y))
    head = out[:]
    out.clear()
    for s, (x, y) in PART.items():
        w('.sz-sl[data-s^="%s"]{--ix:%d;--iy:%d}' % (s, x, y))
    tail = out[:]
    out.clear()
    for s, (x, y) in SPOT.items():
        w('[data-s^="%s"]{--x:%s;--y:%s}' % (s, x, y))
    for s, (x, y) in FILT.items():
        w('.sz-filter [data-f="%s"]{--ix:%d;--iy:%d}' % (s, x, y))
    for c, kws in QUAL:
        w(','.join('.sz-it[data-q*="%s"]' % k for k in kws) + '{--q:%s}' % c)
    for i, c in enumerate(ORDER):
        w('.sz-it[data-c="%s"]>*{order:%d}' % (c, i + 1))
        w('.p-bag:has([data-f="%s"] input:checked) .sz-it:not([data-c="%s"]){display:none}' % (c, c))
        w('.p-bag:not(:has(.sz-it[data-c="%s"])) [data-f="%s"]{display:none}' % (c, c))
    # 技能书：书签选哪一类翻到哪一类；没选过就翻到头一个有东西的类；这一局没有的类，书签不出
    prev = ''
    for c in ABC:
        w('.sz-book:not(:has(.sz-ab[data-c="%s"])) .sz-cat[data-c="%s"]{display:none}' % (c, c))
        w('.sz-it[data-c="%s"],.sz-cat[data-c="%s"]{--ai:%s}' % (c, c, _svg("<path d='%s'/>" % ABIC[c])))
        now = '.sz-book:has(.sz-cat[data-c="%s"] input:checked)' % c
        dft = '.sz-book:not(:has(.sz-cat input:checked))' + prev + ':has(.sz-ab[data-c="%s"])' % c
        for b in (now, dft):
            w(b + ' .sz-ab[data-c="%s"]{display:contents}' % c)
            w(b + ' .sz-chap::before{content:"%s"}' % c)
            w(b + ' .sz-cat[data-c="%s"]{--act:1}' % c)
            # 宽屏上右页不留白：这一类里没选、也没悬停，就摆头一枚
            w('@media (min-width:1100px){%s:not(:has(.sz-ab[data-c="%s"] .sz-face input:checked)):not(:has(.sz-ab[data-c="%s"]:hover)) .sz-ab[data-c="%s"]:nth-child(1 of .sz-ab[data-c="%s"]) .sz-tip{display:block}}' % (b, c, c, c, c))
        prev += ':not(:has(.sz-ab[data-c="%s"]))' % c
    for i, t in enumerate(TIERN):
        n = i + 1
        w('.p-deed:has(.sz-goal[data-t^="%s"]) .sz-path i:nth-child(-n+%d){--on:1}' % (t, n))
        w('.p-deed:has(.sz-goal[data-t^="%s"]) .sz-path i:nth-child(%d){--cur:1}' % (t, n))
    for t, c in THREAT:
        w('.sz-foe[data-th="%s"]{--t:%s}' % (t, c))
    for k, x in MARKS.items():
        w('[data-k="%s"]{--ix:%d;--iy:5}' % (k, x))
    # 记忆：一类一个计数器；点上头那一排只看这一类（藏起来的别用 display:none，不然就不算数了）
    for k, c, col in MEMC:
        w('[data-k="%s"]{--mc:%s}' % (k, col))
        w('.sz-mm[data-k="%s"]{counter-increment:ma %s}' % (k, c))
        w('.sz-mt[data-k="%s"]>em::before,.sz-mh[data-k="%s"]>em::before{content:counter(%s)}' % (k, k, c))
        w('.p-mem:not(:has(.sz-mm[data-k="%s"])) .sz-mh[data-k="%s"]{display:none}' % (k, k))
        w('.p-mem:not(:has(.sz-mm[data-k="%s"])) .sz-mt[data-k="%s"]{opacity:.4;pointer-events:none}' % (k, k))
        w('.p-mem:has(.sz-mt[data-k="%s"] input:checked) .sz-mm:not([data-k="%s"]){position:absolute;visibility:hidden}' % (k, k))
        w('.p-mem:has(.sz-mt[data-k="%s"] input:checked) .sz-mh:not([data-k="%s"]){display:none}' % (k, k))
    w('.sz-mt[data-k="全部"]{--mc:#e9cf8a}')
    w('.sz-mt[data-k="全部"]>em::before{content:counter(ma)}')
    w('.p-mem:not(:has(.sz-mm[data-k="修正"])) .sz-mt[data-k="修正"]{display:none}')
    # 同行底下分页：默认第一页；这个人没有的那一页，签不出
    for t in NT:
        w('.sz-npc-b:has(.sz-nt[data-t="%s"] input:checked) .sz-nc[data-t="%s"]{display:block}' % (t, t))
        w('.sz-npc-b:not(:has(.sz-nc[data-t="%s"])) .sz-nt[data-t="%s"]{display:none}' % (t, t))
    w('.sz-npc-b:not(:has(.sz-nt input:checked)) .sz-nc[data-t="形象"]{display:block}')
    w('.sz-charm{--cc:#8f8f99}')
    for k, c in CHARM:
        w('.sz-charm[data-c^="%s"]{--cc:%s}' % (k, c))
    w('.in-i{--n:2;--cr:#d9b45a}')
    for k, n, c in CRED:
        w('.in-i[data-c*="%s"]{--n:%d;--cr:%s}' % (k, n, c))
    w('.sz-rel{--rc:#d6b26a}.sz-rel[data-k*="变化"]{--rc:#7fc0e6}.sz-rel[data-k*="承诺"]{--rc:#e5b45e}.sz-rel[data-k*="矛盾"]{--rc:#e0755a}')
    w('.sz-ga{--ai:%s}' % _svg("<path d='%s'/>" % ABIC['命星']))
    # 史诗战：第几阶段几颗菱形（罗马数字和数字都认）；Boss 的立绘按名号认
    ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI']
    for n, r in enumerate(ROMAN, 1):
        w('@R@ .sz-pips:is([data-t="%d"],[data-t="%s"]) i:nth-child(n+%d){display:none}' % (n, r, n + 1))
        w('.sz-pips:is([data-p="%d"],[data-p="%s"]) i:nth-child(-n+%d){--on:1}' % (n, r, n))
        w('.sz-pips:is([data-p="%d"],[data-p="%s"]) i:nth-child(%d){--now:1}' % (n, r, n))
    for k, c in [('已识别', '#86c79a'), ('未破解', '#ef7f6a'), ('场地', '#e0b060'), ('地盘', '#e0b060'), ('身后的火', '#f4cf94'), ('殿光', '#f4dfa0'), ('出墙的门', '#e39a58'), ('保护', '#7fb6e6'), ('撤退', '#b0a6d8'), ('协战', '#f08fb0'), ('庇护', '#f2d48a'), ('抬人', '#f2d48a'), ('担架', '#f2d48a')]:
        w('.sz-bi[data-k="%s"]{--bc:%s}' % (k, c))
    for i, k in enumerate(['已识别', '未破解', '场地', '地盘', '身后的火', '殿光', '出墙的门', '保护', '撤退', '协战', '庇护', '抬人', '担架']):
        w('.p-war .sz-bi[data-k="%s"]{order:%d}' % (k, i + 3))
    # 一张图的写成字符串；分阶段的写成 {"1": 图, "2": 图}，转阶段图跟着换（每张图只写一处，写进样式的 data: 不重复）
    for k, u in json.load(open(os.path.join(HERE, 'boss_art.json'), encoding='utf-8')).items():
        if isinstance(u, str):
            w('.sz-boss[data-n*="%s"]{--bart:url("%s");--bf:none}' % (k, u))
            continue
        w('.sz-boss[data-n*="%s"]{--bf:none}' % k)
        for n, v in u.items():
            w('.sz-boss[data-n*="%s"]:is([data-p="%s"],[data-p="%s"]){--bart:url("%s")}' % (k, n, ROMAN[int(n) - 1], v))
    for k, c in [('杂兽', '#8f8f99'), ('共鸣兽', '#6fa883'), ('灵格兽', '#5f9bdc'), ('极境兽', '#a877e6'), ('领主', '#e5aa3a'), ('灾祸', '#e25a4e'), ('元素君王', '#e25a4e'), ('寻常', '#8f8f99'), ('成队', '#6fa883'), ('成群', '#5f9bdc'), ('镇将', '#a877e6'), ('有名者', '#e5aa3a'), ('传奇', '#e25a4e'), ('魔神', '#e25a4e')]:
        w('.sz-kill[data-g="%s"]{--kc:%s}' % (k, c))
    for k, c in [('春', '#9ad48c'), ('夏', '#f0c060'), ('秋', '#e39a58'), ('冬', '#a6d0f2')]:
        w('.sz-sea[data-s="%s"]{--sc:%s}' % (k, c))
    # 立绘和表情（11-05，用户说原来那一批太腻，先拿掉，portraits.json 留着不用）：短名认图，一位两张。por_英文名 是四套衣着排成一行（常服、私服、战斗、正装），face_英文名 是九格表情（对话框和同行的小头像用）。
    # 没有图的留影子和名字头一个字，有图的不再露那个字
    for k, en in json.load(open(os.path.join(HERE, 'roster.json'), encoding='utf-8')).items():
        w(':is(.sz-npc,.sz-say)[data-portrait="%s"]{--por:url("__ART__/por_%s.webp");--face:url("__ART__/face_%s.webp");--init:none;--ot:block}' % (k, en, en))
    w('.sz-por-t::after{content:"常服"}')
    w('.sz-por-t:is([data-o^="显"])::after{content:"显像"}')
    w('.sz-por-t:is([data-o^="龙"],[data-o*="原形"],[data-o*="真身"])::after{content:"龙形"}')   # 11-08 真龙的原形（four_era_art 的 DRAGON_SEL 同一组字）
    for sel, oc, lab in [(':is([data-o^="私"],[data-o*="便"])', 1, '私服'), (':is([data-o^="战"],[data-o^="冒"])', 2, '战斗装'), (':is([data-o^="正"],[data-o*="礼"])', 3, '正装')]:
        w('.sz-npc%s{--oc:%d}' % (sel, oc))
        w('.sz-por-t%s::after{content:"%s"}' % (sel, lab))
    # 九格表情的位置，模型写了近义的字也认。后写的盖先写的
    for sel, x, y in [('笑', 1, 0), ('开怀|大笑|欢|喜', 2, 0), ('认真|肃|坚|决|冷|沉', 0, 1), ('怒|气', 1, 1), ('悲|哀|哭|泪|伤心|难过', 2, 1), ('惊|愕|诧', 0, 2), ('羞|赧|脸红', 1, 2), ('痛|受伤|咬牙', 2, 2)]:
        w('.sz-say:is(%s){--fx:%d;--fy:%d}' % (','.join('[data-em*="%s"]' % k for k in sel.split('|')), x, y))
    # 同行：数这一页有几个人（手机上头像一排横着滑，档案那一块要占满这几格才粘得住）
    for k in range(1, 25):
        w('.sz-npcs:has(>.sz-npc:nth-child(%d of .sz-npc)){--nn:%d}' % (k, k))
    # 正文里的专名：表在 glossary.tsv
    for g in (l.rstrip('\r\n').split('\t') for l in open(os.path.join(HERE, 'glossary.tsv'), encoding='utf-8') if l.strip() and not l.startswith('#')):
        w('.sz-t>.sz-tip[data-t="%s"]{--c:" · %s";--g:"%s"}' % (g[0], g[1], g[2]))
    # 地图：地标的位置、颜色、标名字的门槛、点开的卡片；玩家在哪认地名。后写的盖先写的，泛的在前
    MAP = json.load(open(os.path.join(HERE, 'map_data.json'), encoding='utf-8'))
    def cs(v):
        return '"%s"' % v.replace('\\', '').replace('"', '＂').replace('\n', ' ')
    w('.sz-map{--map-img:url("%s")}' % MAP['img'])
    ZC = {'center': '#E1B85C', 'east': '#5CD6D2', 'west': '#C96A6A', 'old': '#85E6A8', 'polar': '#BFD7FF', 'town': '#A78BFA', 'geo': '#9AA0C0'}
    for z, c in ZC.items():
        w('.ml [data-z="%s"]{--c:%s}' % (z, c))
    for l in MAP['lands']:
        w('.m[data-l="%s"]{--x:%s%%;--y:%s%%;--c:%s;--t:%s}' % (l['n'], l['x'], l['y'], ZC[l['z']], l['t']))
        w('.sz-map:has(.m[data-l="%s"] input:checked){--fx:%s;--fy:%s;--n:%s;--r:%s;--lv:%s;--d:%s%s}' % (
            l['n'], round(l['x'] / 100, 4), round(l['y'] / 100, 4), cs(l['n']), cs(l['r']), cs(l['lv']), cs(l['d']),
            ';--art:url("%s");--ad:block' % l['art'] if l['art'] else ''))
    seen = {}
    def where(l, k):
        seen[k] = l
    for l in sorted(MAP['lands'], key=lambda a: a['o']):
        for k in l['low']:
            where(l, k)
    for l in sorted(MAP['lands'], key=lambda a: a['o']):
        for k in sorted(l['keys'], key=len):
            where(l, k)
    for l in sorted(MAP['lands'], key=lambda a: a['o']):
        for k in sorted(l['high'], key=len):
            where(l, k)
    for k, l in seen.items():
        w('.sz-map[data-loc*="%s"]{--hx:%s;--hy:%s;--z0:2;--hd:block}' % (k, round(l['x'] / 100, 4), round(l['y'] / 100, 4)))
    for c in range(10):
        w('.sz-map:has(.mg label:nth-child(10n+%d) input:checked){--fx:%s}' % (c + 1, round((c + .5) / 10, 3)))
    for r in range(6):
        w('.sz-map:has(.mg label:nth-child(n+%d):nth-child(-n+%d) input:checked){--fy:%s}' % (r * 10 + 1, r * 10 + 10, round((r + .5) / 6, 3)))
    return '\n'.join(tail + head + out)


MODULES = r'''
/* ==== 各页：像游戏界面，平时只看图标和大数字，细节悬停或点开才出 ==== */
@SH@:has(.sz-hud){--sz-sprite:url("__ART__/items.webp");--sz-doll:url("__ART__/doll.webp")}
.sz-it{--q:#8fa0b3}
.sz-foe{--t:#c9b15a}
@TABLES@
@R@ .sz-ic{display:block;background-image:var(--sz-sprite);background-repeat:no-repeat;background-size:1200% 600%;background-position:calc(var(--ix, 10) * 100% / 11) calc(var(--iy, 4) * 100% / 5)}
@R@ .sz-cat input,@R@ .sz-it input,@R@ .sz-arch-t input,@R@ .sz-nt input,@R@ .sz-av input,@R@ .sz-filter input,@R@ .sz-mt input,@R@ .m-fold input{display:none!important}
/* ---------- 一页的头：不再框中套框，题头一行，页底一枚大纹 ---------- */
@R@ .sz-pane{position:relative;padding:2px 2px 20px;isolation:isolate;animation:sz-up .45s ease-out both}
@keyframes sz-up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@R@ .sz-pane::before{content:"";position:absolute;right:-8px;top:-10px;width:210px;height:210px;z-index:-1;opacity:.04;background:var(--fm-acc);-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat;pointer-events:none}
@R@ .sz-pane-head{display:flex;align-items:center;gap:12px;margin:0 0 18px}
@R@ .sz-pane-head i{position:relative;flex:none;width:36px;height:36px;border-radius:50%;box-shadow:inset 0 0 0 1px var(--fm-edge2);background:radial-gradient(circle at 50% 28%, color-mix(in srgb, var(--fm-acc) 26%, transparent), transparent 72%)}
@R@ .sz-pane-head i::before{content:"";position:absolute;inset:8px;background:var(--fm-acc2);-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}
@R@ .sz-pane-head b{font-family:var(--fm-serif);font-size:21px!important;font-weight:700!important;letter-spacing:.16em;color:var(--fm-head)!important}
@R@ .sz-pane-head::after{content:"";flex:1;order:1;height:1px;background:linear-gradient(90deg, var(--fm-line), transparent)}
@R@ .sz-x{order:2;font-size:12px;color:var(--fm-ink2);cursor:pointer;border-radius:999px;padding:3px 13px 3px 10px;box-shadow:inset 0 0 0 1px var(--fm-line);transition:color .15s, box-shadow .15s}
@R@ .sz-x::before{content:"‹ "}
@R@ .sz-x:hover{color:var(--fm-ink);box-shadow:inset 0 0 0 1px var(--fm-acc)}
@R@ .sz-f:not(.d){display:block}
/* 推演底座：九行，一行几小格，格名和值分开 */
@R@ .sz-f.d>b>i{margin-right:5px;font-style:normal;font-weight:400;opacity:.65}
@R@ .sz-dl{display:flex;flex-wrap:wrap;gap:2px 14px}
@R@ .sz-dl>i{font-style:normal}
@R@ .sz-dl>i>b{margin-right:5px;font-size:11px!important;font-weight:500!important;letter-spacing:.04em;opacity:.85}
@R@ .sz-row{grid-column:1 / -1;display:grid!important;grid-template-columns:4.6em 1fr;gap:10px;padding:6px 0;font-size:13px;line-height:1.7;color:var(--fm-ink)}
@R@ .sz-row>b{color:var(--fm-acc);font-weight:600}
@R@ small{font-size:inherit}

/* ---------- 一条条的进度：细、圆头、亮头 ---------- */
@R@ :is(.sz-lvm,.sz-res-bars,.sz-foe,.sz-bagtop,.sz-nexp,.b-bars) .sz-bar{display:grid;grid-template-columns:auto 1fr;grid-template-rows:auto 6px;align-items:center;column-gap:8px;row-gap:4px;font-size:12px;color:var(--fm-ink2)}
@R@ :is(.sz-lvm,.sz-res-bars,.sz-foe,.sz-bagtop,.sz-nexp,.b-bars) .sz-bar>b{font-size:11.5px!important;font-weight:600!important;letter-spacing:.06em;color:var(--fm-ink)!important}
@R@ :is(.sz-lvm,.sz-res-bars,.sz-foe,.sz-bagtop,.sz-nexp,.b-bars) .sz-bar>em{justify-self:end;font-style:normal;font-variant-numeric:tabular-nums}
@R@ :is(.sz-lvm,.sz-res-bars,.sz-foe,.sz-bagtop,.sz-nexp,.b-bars) .sz-bar .sz-trk{grid-column:1 / -1;height:6px}
@R@ .sz-bar .sz-trk,@R@ .sz-bond .sz-trk{background:color-mix(in srgb, var(--fm-ink) 12%, transparent);box-shadow:inset 0 0 0 1px rgb(0 0 0 / .18)}
@R@ .sz-bar .sz-trk::after{box-shadow:0 0 8px color-mix(in srgb, var(--c) 60%, transparent)}
@R@ .sz-bar.ex{--c:#e6c67a}
@R@ .sz-bar.xu{--c:#d08a5e}
@R@ .sz-bar.wt{--c:#93a1b8}

/* ---------- 一张卡：悬停或点开才出，头上是这件东西的品阶色和大图 ---------- */
@R@ .sz-tip{display:none;z-index:30;cursor:default}
@R@ .sz-tip-in{position:relative;display:block;border-radius:12px;overflow:hidden;background:linear-gradient(180deg, var(--fm-band), var(--fm-band2));box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--q) 60%, var(--fm-edge2)), 0 18px 44px rgb(0 0 0 / .55);color:#d9d2c0;animation:sz-tip .18s ease-out both}
@keyframes sz-tip{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@R@ .sz-tip-h{position:relative;display:block;min-height:88px;padding:13px 86px 12px 15px;background:linear-gradient(115deg, color-mix(in srgb, var(--q) 62%, var(--fm-band2)), color-mix(in srgb, var(--q) 14%, var(--fm-band2)) 80%)}
@R@ .sz-tip-h b{display:block;font-family:var(--fm-serif);font-size:16.5px!important;font-weight:700!important;line-height:1.35;color:#fff6df!important}
@R@ .sz-tip-h small{display:block;margin-top:7px;font-size:11.5px;letter-spacing:.05em;color:rgb(255 255 255 / .74)}
@R@ .sz-tip-h .sz-ic{position:absolute;right:9px;top:50%;width:70px;height:70px;margin-top:-35px;filter:drop-shadow(0 4px 8px rgb(0 0 0 / .5))}
@R@ .sz-tip-s{display:block;padding:11px 15px 0;font-size:12.5px;line-height:1.6;color:#efd594}
@R@ .sz-tip-b{display:block;padding:9px 15px 15px;font-size:13px;line-height:1.75}
@R@ .sz-tip-x{display:none}
@R@ .sz-it:has(>.sz-face input:checked) .sz-tip,@R@ .sz-cell:has(>.sz-face input:checked) .sz-tip{display:block}
@media (hover:hover){
  @R@ .sz-it:hover .sz-tip{display:block}
  @R@ :is(.sz-gridit,.sz-abs,.p-panel .sz-pane-body):has(.sz-it:hover) .sz-it:not(:hover) .sz-tip{display:none}
}

/* ---------- 面板：左边一个人和他身上每个部位，右边名字、等级、几条；底下六维的盘和攻防 ---------- */
@R@ .p-panel .sz-pane-body{position:relative;display:grid;grid-template-columns:300px minmax(0,1fr);column-gap:22px;align-items:start}
@R@ .sz-doll{grid-column:1;grid-row:1 / span 4;position:relative;height:338px}
@R@ .sz-doll-ring{position:absolute;left:50%;top:46%;width:236px;height:236px;margin:-118px 0 0 -118px;background:@RING@ center/contain no-repeat;opacity:.5;animation:sz-spin 160s linear infinite}
@keyframes sz-spin{to{transform:rotate(360deg)}}
@R@ .sz-doll-fig{position:absolute;left:50%;top:6px;width:186px;height:318px;margin-left:-93px;background:var(--sz-doll) center/contain no-repeat;filter:drop-shadow(0 10px 18px rgb(0 0 0 / .5))}
@R@ :is(.sz-sl,.sz-sk){position:absolute;left:calc(var(--x, 0) * 242px);top:calc(var(--y, 0) * 84px);width:58px;height:58px}
@R@ .sz-sk{border-radius:12px;box-shadow:inset 0 0 0 1px var(--fm-line);background:color-mix(in srgb, var(--fm-ink) 4%, transparent)}
@R@ .sz-sk .sz-ic{position:absolute;inset:9px;opacity:.2;filter:grayscale(1) brightness(1.5)}
@R@ .sz-sk small,@R@ .sz-part{position:absolute;left:-6px;right:-6px;top:61px;text-align:center;font-size:11px;letter-spacing:.08em;color:var(--fm-ink2);font-style:normal;pointer-events:none}
@R@ .sz-sl{z-index:2}
@R@ .sz-sl:hover,@R@ .sz-sl:has(>.sz-face input:checked){z-index:20}
@R@ .sz-sl .sz-face{position:absolute;inset:0;display:block;border-radius:12px;cursor:pointer;background:radial-gradient(circle at 50% 28%, color-mix(in srgb, var(--q) 42%, #14143a), #0c0c26 78%);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--q) 72%, transparent), 0 5px 14px rgb(0 0 0 / .4);transition:transform .16s, box-shadow .16s}
@R@ .sz-sl .sz-face .sz-ic{position:absolute;inset:5px}
@R@ .sz-sl:hover .sz-face,@R@ .sz-sl:has(>.sz-face input:checked) .sz-face{transform:translateY(-2px);box-shadow:inset 0 0 0 1px var(--q), 0 0 18px color-mix(in srgb, var(--q) 60%, transparent), 0 6px 16px rgb(0 0 0 / .45)}
@R@ .sz-cl .sz-face{--q:#8f8676}
@R@ .sz-sl .sz-tip{position:absolute;left:66px;top:-8px;width:272px}
/* 右边：名字、标签、等级章、几条 */
@R@ .sz-idc{grid-column:2;grid-row:1;margin-bottom:14px}
@R@ .sz-who{display:block;font-family:var(--fm-serif);font-size:27px!important;font-weight:700!important;line-height:1.25;letter-spacing:.06em;color:var(--fm-head)!important}
@R@ .sz-tags{display:flex;flex-wrap:wrap;gap:5px 6px;margin-top:8px}
@R@ .sz-tags i{font-style:normal;font-size:11.5px;line-height:21px;padding:0 9px;border-radius:11px;background:color-mix(in srgb, var(--fm-acc) 12%, transparent);color:var(--fm-ink2)}
@R@ .sz-tags i:empty{display:none}
@R@ .sz-tags i.vow{background:none;color:var(--fm-acc2);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc) 50%, transparent)}
@R@ .sz-lv{grid-column:2;grid-row:2;display:grid!important;grid-template-columns:64px 1fr;gap:14px;align-items:center;margin-bottom:14px}
@R@ .sz-lvl{position:relative;isolation:isolate;display:flex;flex-direction:column;align-items:center;justify-content:center;width:64px;height:72px;clip-path:@HEX@;background:linear-gradient(170deg, var(--fm-acc2), var(--fm-acc) 50%, color-mix(in srgb, var(--fm-acc) 40%, #0d0d28))}
@R@ .sz-lvl::before{content:"";position:absolute;inset:1.5px;z-index:-1;clip-path:@HEX@;background:radial-gradient(circle at 50% 26%, color-mix(in srgb, var(--fm-acc) 34%, var(--fm-band)), var(--fm-band2) 80%)}
@R@ .sz-lvl small{font-size:9.5px;letter-spacing:.14em;color:var(--fm-acc)}
@R@ .sz-lvl b{font-family:var(--fm-serif);font-size:26px!important;font-weight:700!important;line-height:1;color:#fff0cc!important}
@R@ .sz-lvm{display:grid;gap:7px}
@R@ .sz-tier{font-family:var(--fm-serif);font-size:15px!important;font-weight:600!important;letter-spacing:.08em;color:var(--fm-head)!important}
@R@ .sz-note{font-size:11.5px;color:var(--fm-ink2)}
@R@ .sz-res{grid-column:2;grid-row:3;margin-bottom:12px}
@R@ .sz-res-bars{display:grid;grid-template-columns:1fr 1fr;gap:10px 16px}
@R@ .sz-chips{display:flex;flex-wrap:wrap;gap:4px 12px;margin-top:9px;font-size:11.5px;color:var(--fm-ink2)}
@R@ .sz-chips i{font-style:normal}
@R@ .sz-chips i:empty{display:none}
@R@ .sz-seal{grid-column:2;grid-row:4;display:flex!important;flex-wrap:wrap;align-items:center;gap:7px 14px;margin-bottom:12px}
@R@ .sz-sealb{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;color:var(--fm-ink)}
@R@ .sz-sealb b{font-weight:600!important;color:var(--fm-head)!important}
@R@ .sz-sealb i{width:22px;height:22px;background-image:var(--sz-sprite);background-size:1200% 600%;background-position:calc(10 * 100% / 11) calc(1 * 100% / 5)}
@R@ .sz-coins{display:inline-flex;gap:12px}
@R@ .sz-coins i{display:inline-flex;align-items:center;gap:5px;font-style:normal;font-size:13px;font-weight:600;font-variant-numeric:tabular-nums;color:var(--fm-ink)}
@R@ .sz-coins i::before{content:"";width:13px;height:13px;border-radius:50%;background:radial-gradient(circle at 35% 30%, #fff8d8, #e4b94e 55%, #8f6a1f);box-shadow:0 0 6px rgb(228 185 78 / .45)}
@R@ .sz-coins i.c-s::before{background:radial-gradient(circle at 35% 30%, #fff, #bfc6d0 55%, #6d7480);box-shadow:0 0 6px rgb(191 198 208 / .35)}
@R@ .sz-coins i.c-p::before{background:radial-gradient(circle at 35% 30%, #ffe2c4, #c47f4c 55%, #6f3f1f);box-shadow:0 0 6px rgb(196 127 76 / .35)}
@R@ .sz-coins b{font-size:10.5px!important;font-weight:500!important;color:var(--fm-ink2)!important}
/* 六维的盘，攻防四个大数 */
@R@ .sz-six{grid-column:1;grid-row:5 / span 3;position:relative;height:266px;--M:max(var(--a1),var(--a2),var(--a3),var(--a4),var(--a5),var(--a6),1)}
@R@ .sz-radar{position:absolute;left:50%;top:50%;width:176px;height:176px;margin:-88px 0 0 -88px;filter:drop-shadow(0 0 10px color-mix(in srgb, var(--fm-acc2) 45%, transparent))}
@R@ .sz-radar .r-g{position:absolute;inset:0;background:@HEXGRID@ center/contain no-repeat}
@R@ .sz-radar .r-v{position:absolute;inset:0;clip-path:@RADAR@;background:radial-gradient(circle, color-mix(in srgb, var(--fm-acc2) 22%, transparent), color-mix(in srgb, var(--fm-acc2) 62%, transparent))}
@R@ .sz-cells{position:absolute;inset:0}
@R@ .sz-cells>i{position:absolute;display:flex;flex-direction:column;align-items:center;width:62px;font-style:normal;transform:translate(-50%,-50%);outline:0;cursor:default}
@R@ .sz-cells>i:nth-child(1){left:50%;top:20px}
@R@ .sz-cells>i:nth-child(2){left:calc(50% + 112px);top:72px}
@R@ .sz-cells>i:nth-child(3){left:calc(50% + 112px);top:194px}
@R@ .sz-cells>i:nth-child(4){left:50%;top:246px}
@R@ .sz-cells>i:nth-child(5){left:calc(50% - 112px);top:194px}
@R@ .sz-cells>i:nth-child(6){left:calc(50% - 112px);top:72px}
@R@ .sz-cells>i>b{font-size:10px!important;font-weight:600!important;letter-spacing:.12em;color:var(--fm-acc)!important}
@R@ .sz-cells>i>strong{font-family:var(--fm-serif);font-size:20px;line-height:1.15;font-weight:700;color:var(--fm-head)}
@R@ .sz-cells>i>small{display:none;position:absolute;top:100%;left:50%;transform:translateX(-50%);z-index:6;white-space:nowrap;padding:3px 9px;border-radius:7px;font-size:11px;color:#e9e2cf;background:var(--fm-band2);box-shadow:inset 0 0 0 1px var(--fm-edge2)}
@R@ .sz-cells>i:hover>small,@R@ .sz-cells>i:focus>small{display:block}
@R@ .sz-atk{grid-column:2;grid-row:5;margin-bottom:12px}
@R@ .sz-atks{display:grid;grid-template-columns:1fr 1fr;gap:8px}
@R@ .sz-atks>i{display:flex;align-items:baseline;justify-content:space-between;padding:9px 14px;border-radius:10px;font-style:normal;background:linear-gradient(120deg, color-mix(in srgb, var(--fm-acc) 13%, transparent), transparent);box-shadow:inset 0 0 0 1px var(--fm-line)}
@R@ .sz-atks>i>b{font-size:11.5px!important;font-weight:600!important;letter-spacing:.12em;color:var(--fm-acc)!important}
@R@ .sz-atks>i>strong{font-family:var(--fm-serif);font-size:25px;line-height:1.15;font-weight:700;color:var(--fm-head)}
@R@ .sz-resist{display:block;margin-top:9px;font-size:11px;line-height:1.75;color:var(--fm-ink2)}
/* ---- 月银纪：名号是诗人唱出来的，唱到第三个国就定了；说一个人厉害，说他斩过什么 ---- */
@R@ .sz-song{display:inline-flex;align-items:center;gap:8px;font-size:12.5px;color:var(--fm-ink)}
@R@ .sz-song[data-s="无"]{display:none}
@R@ .sz-song small{font-size:10.5px;letter-spacing:.14em;color:var(--fm-acc)}
@R@ .sz-song b{font-weight:600!important;color:var(--fm-head)!important}
@R@ .sz-song em{font-style:normal;font-size:11.5px;color:var(--fm-acc2)}
@R@ .sz-song-t{display:inline-flex;gap:4px;margin:0 1px}
@R@ .sz-song-t i{width:8px;height:8px;transform:rotate(45deg);box-shadow:inset 0 0 0 1px var(--fm-edge2)}
@R@ .sz-song[data-g^="第一"] .sz-song-t i:nth-child(1),@R@ .sz-song[data-g^="第二"] .sz-song-t i:nth-child(-n+2),@R@ .sz-song[data-g^="第三"] .sz-song-t i{background:var(--fm-acc2);box-shadow:0 0 6px var(--fm-acc2)}
@R@ .sz-slain{display:flex;align-items:flex-start;gap:12px;margin:-8px 0 16px;padding:0 14px}
@R@ .sz-slain>small{flex:none;padding-top:5px;font-size:10.5px;letter-spacing:.1em;color:var(--fm-acc)}
@R@ .sz-kills{display:flex;flex-wrap:wrap;gap:6px 8px;min-width:0}
@R@ .sz-kill{display:inline-flex;align-items:center;gap:7px;padding:0 11px 0 9px;border-radius:13px;font-size:12.5px;line-height:25px;background:color-mix(in srgb, var(--kc, var(--fm-acc)) 15%, transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--kc, var(--fm-acc)) 45%, transparent)}
@R@ .sz-kill i{width:8px;height:8px;transform:rotate(45deg);background:var(--kc, var(--fm-acc))}
@R@ .sz-kill b{font-weight:600!important;color:var(--fm-head)!important}
@R@ .sz-kill small{font-size:10.5px;color:var(--fm-ink2)}
@R@ .sz-road,@R@ .sz-job{grid-column:2;grid-row:6;display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:10px}
@R@ :is(.sz-road,.sz-job,.sz-goal)>span{display:block;min-width:0}
@R@ :is(.sz-road,.sz-job,.sz-goal) small{display:block;font-size:10.5px;letter-spacing:.1em;color:var(--fm-acc)}
@R@ :is(.sz-road,.sz-job,.sz-goal) b{display:block;margin-top:2px;font-size:13px!important;font-weight:600!important;line-height:1.4;color:var(--fm-ink)!important}
/* 容貌和姿态：点那个人脚下的小牌，右边这一栏换成档案，在页里排开，什么也不叠 */
@R@ .sz-arch-t{position:absolute;left:50%;bottom:0;z-index:3;transform:translateX(-50%);display:inline-flex;align-items:center;padding:3px 13px;border-radius:999px;font-size:11.5px;letter-spacing:.08em;white-space:nowrap;color:var(--fm-acc2);cursor:pointer;background:color-mix(in srgb, var(--fm-band2) 82%, transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc) 60%, transparent);transition:box-shadow .15s}
@R@ .sz-arch-t span::before{content:"容貌 · 姿态"}
@R@ .sz-arch-t:has(input:checked) span::before{content:"收起档案"}
@R@ .sz-arch-t:hover,@R@ .sz-arch-t:has(input:checked){box-shadow:inset 0 0 0 1px var(--fm-acc2), 0 0 12px color-mix(in srgb, var(--fm-acc2) 42%, transparent)}
@R@ .sz-arch{display:none;grid-column:2;grid-row:2 / span 3;align-self:start;margin-bottom:12px;animation:sz-up .3s ease-out both}
@R@ .p-panel:has(.sz-arch-t input:checked) .sz-arch{display:block}
@R@ .p-panel:has(.sz-arch-t input:checked) :is(.sz-lv,.sz-res,.sz-seal){display:none!important}
/* 宽屏上档案比那个人高：六维的盘挪上来填左边那一块，攻防、命路、委托排满一行 */
@media (min-width:1100px){
  @R@ .p-panel:has(.sz-arch-t input:checked) .sz-arch{min-height:548px}
  @R@ .p-panel:has(.sz-arch-t input:checked) .sz-six{grid-row:2 / span 3;align-self:end;margin-bottom:12px}
  @R@ .p-panel:has(.sz-arch-t input:checked) :is(.sz-atk,.sz-road,.sz-qcard){grid-column:1 / -1}
  @R@ .p-panel:has(.sz-arch-t input:checked) .sz-atks{grid-template-columns:repeat(4,minmax(0,1fr))}
}
/* 档案里的小块：一道小题头，格名在上、值在下 */
@R@ .sz-ht{display:flex;align-items:center;gap:10px;margin:16px 0 9px;font-family:var(--fm-serif);font-size:13.5px!important;font-weight:700!important;letter-spacing:.16em;color:var(--fm-acc2)!important}
@R@ .sz-ht::after{content:"";flex:1;height:1px;background:linear-gradient(90deg, var(--fm-line), transparent)}
@R@ :is(.sz-nc,.sz-arch)>.sz-ht:first-child{margin-top:0}
@R@ .sz-kv{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px 16px;margin-bottom:9px}
@R@ .sz-kv>i{display:block;min-width:0;font-style:normal;font-size:13px;line-height:1.6;color:var(--fm-ink)}
@R@ .sz-kv>i.w{grid-column:1 / -1}
@R@ .sz-kv small{display:block;font-size:10.5px;line-height:1.5;letter-spacing:.14em;color:var(--fm-acc)}
@R@ .sz-charm{display:flex;align-items:flex-start;gap:10px;margin-top:2px;font-size:12.5px;line-height:1.7;color:var(--fm-ink)}
@R@ .sz-charm em{flex:none;padding:0 11px;border-radius:11px;font-style:normal;font-size:12px;font-weight:700;line-height:22px;letter-spacing:.14em;color:#fff;background:linear-gradient(120deg, var(--cc), color-mix(in srgb, var(--cc) 55%, #0c0c26));box-shadow:0 0 12px color-mix(in srgb, var(--cc) 50%, transparent)}
@R@ .sz-eval{display:block;margin:9px 0 2px;padding-left:12px;border-left:2px solid var(--fm-acc);font-family:var(--fm-serif);font-size:13.5px;line-height:1.7;color:var(--fm-ink2)}
@R@ .sz-arct{display:block;font-size:13px;line-height:1.75;color:var(--fm-ink)}
/* 面板上那张委托 */
@R@ .sz-qcard{grid-column:2;grid-row:7;display:grid;grid-template-columns:38px minmax(7.5em,1fr) auto;column-gap:10px;row-gap:7px;align-items:center;margin-bottom:10px;padding:9px 14px 11px 10px;border-radius:12px;background:linear-gradient(115deg, color-mix(in srgb, var(--fm-acc) 15%, transparent), transparent 85%);box-shadow:inset 0 0 0 1px var(--fm-line)}
@R@ .sz-qcard>.sz-ic{width:38px;height:38px;filter:drop-shadow(0 2px 4px rgb(0 0 0 / .4))}
@R@ .q-n{min-width:7.5em}
@R@ .q-n small{display:block;font-size:10.5px;letter-spacing:.14em;color:var(--fm-acc)}
@R@ .q-n b{display:block;font-family:var(--fm-serif);font-size:15px!important;font-weight:700!important;line-height:1.35;color:var(--fm-head)!important}
@R@ .sz-qcard>em{max-width:13em;padding:2px 10px;border-radius:11px;font-style:normal;font-size:11.5px;line-height:18px;color:var(--fm-acc2);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc) 55%, transparent)}
@R@ .q-f{grid-column:1 / -1;display:grid;grid-template-columns:minmax(0,1fr);gap:4px;font-size:12px;line-height:1.6;color:var(--fm-ink)}
@R@ .q-f i{font-style:normal}
@R@ .q-f small{margin-right:7px;font-size:10.5px;letter-spacing:.1em;color:var(--fm-acc)}

/* ---------- 背包：钱和负重在头上，一格一样东西，右边是选中那一样的卡 ---------- */
@R@ .sz-bagtop{display:flex;align-items:center;gap:20px;margin-bottom:12px}
@R@ .sz-bagtop .sz-bar{flex:1;max-width:220px;margin-left:auto}
@R@ .sz-filter{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}
@R@ .sz-filter label{display:inline-flex;align-items:center;gap:5px;padding:3px 12px 3px 7px;border-radius:999px;font-size:12px;letter-spacing:.06em;color:var(--fm-ink2);cursor:pointer;box-shadow:inset 0 0 0 1px var(--fm-line);transition:color .15s, box-shadow .15s}
@R@ .sz-filter label b{font-weight:500!important;color:inherit!important}
@R@ .sz-filter .sz-ic{width:20px;height:20px}
@R@ .sz-filter label:hover{color:var(--fm-ink)}
@R@ .sz-filter label:has(input:checked),@R@ .sz-filter:not(:has(input:checked)) [data-f="全部"]{color:var(--fm-acc2);box-shadow:inset 0 0 0 1px var(--fm-acc);background:color-mix(in srgb, var(--fm-acc) 12%, transparent)}
/* 一张网格，最右一栏是卡；卡是粘住的，翻长的背包时它不走 */
@R@ .sz-gridit{position:relative;display:grid;grid-template-columns:repeat(5,70px) minmax(0,1fr);column-gap:8px;row-gap:0;align-items:start}
@R@ .sz-gridit::before{content:"";grid-column:6;grid-row:1 / span 40;order:-1}
@R@ .sz-gridit .sz-it{display:contents}
@R@ .sz-gridit .sz-tip{grid-column:6;grid-row:1 / span 40;position:sticky;top:116px;height:0;margin-left:8px}
@R@ .sz-gridit .sz-bagn,@R@ .sz-gridit .sz-row{grid-column:1 / 6;order:90}
@media (min-width:1100px) and (hover:hover){
  @R@ .sz-gridit:not(:has(.sz-face input:checked)):not(:has(.sz-it:hover)) .sz-it:first-of-type .sz-tip{display:block}
}
@media (min-width:1100px) and (hover:none){
  @R@ .sz-gridit:not(:has(.sz-face input:checked)) .sz-it:first-of-type .sz-tip{display:block}
}
@R@ .sz-cell .sz-face{position:relative;display:block;margin-bottom:9px;cursor:pointer}
@R@ .sz-pad{position:relative;display:block;width:70px;height:70px;border-radius:12px;background:linear-gradient(160deg, color-mix(in srgb, var(--q) 58%, #16163a), color-mix(in srgb, var(--q) 20%, #0c0c26));box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--q) 78%, transparent), inset 0 10px 14px -8px rgb(255 255 255 / .22), 0 5px 12px rgb(0 0 0 / .32);transition:transform .16s, box-shadow .16s}
@R@ .sz-pad .sz-ic{position:absolute;inset:6px;filter:drop-shadow(0 2px 3px rgb(0 0 0 / .45));transition:transform .16s}
@R@ .sz-ct{position:absolute;right:5px;bottom:3px;font-style:normal;font-size:11.5px;font-weight:700;font-variant-numeric:tabular-nums;color:#fff;text-shadow:0 1px 2px #000, 0 0 3px #000}
@R@ .sz-ct::before{content:"×";font-weight:400;opacity:.8;margin-right:1px}
@R@ .sz-nm{display:block;margin-top:5px;font-size:11px!important;font-weight:400!important;line-height:1.3;text-align:center;color:var(--fm-ink2)!important;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@R@ .sz-it:hover .sz-pad,@R@ .sz-it:has(>.sz-face input:checked) .sz-pad{transform:translateY(-2px);box-shadow:inset 0 0 0 1.5px var(--q), inset 0 10px 14px -8px rgb(255 255 255 / .3), 0 0 18px color-mix(in srgb, var(--q) 65%, transparent)}
@R@ .sz-it:hover .sz-pad .sz-ic{transform:scale(1.07)}
@R@ .sz-it:hover .sz-nm,@R@ .sz-it:has(>.sz-face input:checked) .sz-nm{color:var(--fm-ink)!important}
@R@ .sz-bagn{margin-top:8px;font-size:12px!important;color:var(--fm-ink2)}

/* ---------- 伟业：七境一条路，底下下一境的门槛；能力一个一枚六角，右边是卡 ---------- */
@R@ .sz-path{position:relative;display:flex;justify-content:space-between;margin:2px 6px 16px}
@R@ .sz-path::before{content:"";position:absolute;left:14px;right:14px;top:13px;height:1px;background:linear-gradient(90deg, var(--fm-acc), var(--fm-line) 60%)}
@R@ .sz-path i{position:relative;display:flex;flex-direction:column;align-items:center;gap:6px;width:48px;font-style:normal}
@R@ .sz-path i::before{content:"";width:calc(13px + var(--cur, 0) * 8px);height:calc(13px + var(--cur, 0) * 8px);margin-top:calc(6.5px - var(--cur, 0) * 4px);transform:rotate(45deg);background:color-mix(in srgb, var(--fm-acc2) calc(var(--on, 0) * 100%), var(--fm-band));box-shadow:inset 0 0 0 1px var(--fm-edge2), 0 0 calc(var(--cur, 0) * 16px) var(--fm-acc2)}
@R@ .sz-path i b{font-size:12px!important;font-weight:calc(400 + var(--cur, 0) * 300)!important;letter-spacing:.08em;color:color-mix(in srgb, var(--fm-head) calc(35% + var(--on, 0) * 65%), transparent)!important}
@R@ .sz-goal{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px 14px;margin-bottom:18px;padding:12px 14px;border-radius:12px;background:linear-gradient(120deg, color-mix(in srgb, var(--fm-acc) 11%, transparent), transparent);box-shadow:inset 0 0 0 1px var(--fm-line)}
@R@ .sz-goal .g-to b{font-family:var(--fm-serif);font-size:15px!important;color:var(--fm-head)!important}
@R@ .sz-job{margin:-6px 0 18px;padding:0 14px;display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px 14px}
/* 技能书：皮面、两页纸、当中一道装订的折，书签一排插在上头。一次翻开一类，左页一枚一枚，右页是选中的那一枚 */
@R@ .sz-book{position:relative;isolation:isolate;margin:0 4px 16px}
@R@ .sz-book::before{content:"";position:absolute;left:-7px;right:-7px;top:30px;bottom:-12px;z-index:-1;border-radius:10px;background:linear-gradient(170deg, #4a2d1a, #281609);box-shadow:inset 0 0 0 1px rgb(214 178 106 / .4), inset 0 0 0 4px rgb(0 0 0 / .18), 0 16px 30px rgb(0 0 0 / .45)}
@R@ .sz-marks{position:relative;z-index:1;display:flex;gap:3px;padding:0 14px}
@R@ .sz-cat{--act:0;position:relative;display:flex;align-items:center;gap:5px;padding:6px 11px 8px 8px;border-radius:9px 9px 0 0;cursor:pointer;color:color-mix(in srgb, #3a2410 calc(var(--act) * 100%), #dcccab);background:linear-gradient(180deg, color-mix(in srgb, #f7eed8 calc(var(--act) * 100%), #57382a), color-mix(in srgb, #f2e8cf calc(var(--act) * 100%), #3a2415));box-shadow:inset 0 0 0 1px rgb(214 178 106 / calc(.3 - var(--act) * .3));transform:translateY(calc((1 - var(--act)) * 4px));transition:transform .15s}
@R@ .sz-cat:has(input:checked){--act:1}
@R@ .sz-cat:hover{transform:translateY(calc((1 - var(--act)) * 1px))}
@R@ .sz-cat i{flex:none;width:15px;height:15px;background:currentColor;-webkit-mask:var(--ai) center/contain no-repeat;mask:var(--ai) center/contain no-repeat}
@R@ .sz-cat b{font-size:12px!important;font-weight:600!important;letter-spacing:.05em;color:inherit!important;white-space:nowrap}
@R@ .sz-abs{--cx:356px;position:relative;display:grid;grid-template-columns:repeat(4,76px) minmax(0,1fr);column-gap:6px;row-gap:4px;align-items:start;align-content:start;min-height:404px;padding:20px 18px 24px 20px;border-radius:4px;color:#2f2415;background:linear-gradient(90deg, transparent calc(var(--cx) - 34px), rgb(80 50 20 / .2) calc(var(--cx) - 1px), rgb(60 36 12 / .42) var(--cx), rgb(80 50 20 / .14) calc(var(--cx) + 1px), transparent calc(var(--cx) + 30px)),linear-gradient(90deg, rgb(120 90 50 / .2), transparent 20px, transparent calc(100% - 20px), rgb(120 90 50 / .2)),@PAPER@ 0 0/180px 180px,linear-gradient(180deg, #f3ead2, #e6d8b7);box-shadow:0 2px 0 #d9c9a6, 0 4px 0 #cbba92, 0 6px 0 #bba97f}
@R@ .sz-chap{grid-column:1 / 5;display:flex;align-items:center;gap:10px;margin:0 0 8px;font-family:var(--fm-serif);font-size:16px!important;font-weight:700!important;letter-spacing:.2em;color:#5b3a1e!important}
@R@ .sz-chap::after{content:"";flex:1;height:0;border-top:3px double rgb(91 58 30 / .35)}
@R@ .sz-abs .sz-ab{display:none}
@R@ .sz-abs .sz-row{grid-column:1 / 5;order:90;color:#2f2415}
@R@ .sz-abs .sz-row>b{color:#7a2e1d}
@R@ .sz-ab .sz-face{position:relative;display:flex;flex-direction:column;align-items:center;margin-bottom:10px;cursor:pointer}
@R@ .sz-hx{position:relative;display:block;width:56px;height:63px;clip-path:@HEX@;background:linear-gradient(170deg, color-mix(in srgb, var(--q) 90%, #fff), color-mix(in srgb, var(--q) 45%, #0c0c26));transition:transform .16s, filter .16s}
@R@ .sz-hx::before{content:"";position:absolute;inset:1.5px;clip-path:@HEX@;background:radial-gradient(circle at 50% 28%, color-mix(in srgb, var(--q) 48%, #14143a), #0c0c26 82%)}
@R@ .sz-hx::after{content:"";position:absolute;inset:16px 14px;background:color-mix(in srgb, var(--q) 70%, #fff);-webkit-mask:var(--ai) center/contain no-repeat;mask:var(--ai) center/contain no-repeat}
@R@ .sz-it:hover .sz-hx,@R@ .sz-it:has(>.sz-face input:checked) .sz-hx{transform:translateY(-2px) scale(1.05);filter:drop-shadow(0 0 7px var(--q))}
@R@ .sz-ab .sz-nm{width:76px;margin-top:6px;font-size:12px!important;font-weight:500!important;line-height:1.3;white-space:normal;color:#3f2f1a!important}
@R@ .sz-abs .sz-it:hover .sz-nm,@R@ .sz-abs .sz-it:has(>.sz-face input:checked) .sz-nm{color:#7a2e1d!important}
/* 右页：墨写的一页，头上一枚大纹章 */
@R@ .sz-abs .sz-tip{grid-column:5;grid-row:1 / span 40;position:sticky;top:116px;height:0;margin-left:24px}
@R@ .sz-abs .sz-tip-in{background:none;box-shadow:none;border-radius:0;overflow:visible;color:#2f2415}
@R@ .sz-abs .sz-tip-h{min-height:0;padding:0 0 10px;text-align:center;background:none;border-bottom:3px double rgb(91 58 30 / .35)}
@R@ .sz-abs .sz-tip-h .sz-ic{position:static;display:block;width:58px;height:58px;margin:0 auto 8px;background:color-mix(in srgb, var(--q) 78%, #2a1a0c);-webkit-mask:var(--ai) center/contain no-repeat;mask:var(--ai) center/contain no-repeat;filter:none}
@R@ .sz-abs .sz-tip-h b{font-size:21px!important;letter-spacing:.06em;color:#2a1a0c!important}
@R@ .sz-abs .sz-tip-h small{margin-top:4px;font-size:12px;color:color-mix(in srgb, var(--q) 62%, #3a2c18)}
@R@ .sz-abs .sz-tip-s{padding:10px 0 0;font-size:12.5px;font-weight:600;line-height:1.6;text-align:center;color:#7a2e1d}
@R@ .sz-abs .sz-tip-b{padding:8px 0 0;font-family:var(--fm-serif);font-size:14px;font-weight:500;line-height:1.8;color:#241a0e}

/* ---------- 同行：头像一排，点谁看谁；左边一幅立绘，右边状态，底下分页，一次只看一页 ---------- */
@R@ .sz-npcs{display:grid;grid-template-columns:repeat(auto-fill,68px);justify-content:start;gap:0 8px}
@R@ .sz-npc{display:contents}
@R@ .sz-av{grid-row:1;display:flex;flex-direction:column;align-items:center;gap:5px;cursor:pointer;margin-bottom:16px}
@R@ .sz-av i{position:relative;display:grid;place-items:center;width:54px;height:54px;border-radius:50%;font-style:normal;font-family:var(--fm-serif);font-size:22px;color:var(--fm-head);background:var(--face, none) 0 0/var(--fsz, 300% 300%) no-repeat, radial-gradient(circle at 50% 28%, var(--fm-por1), var(--fm-por2));box-shadow:inset 0 0 0 1px var(--fm-edge2), 0 4px 12px rgb(0 0 0 / .35);transition:transform .16s, box-shadow .16s}
@R@ .sz-av i::before{content:attr(data-n);display:var(--init, block);width:1em;overflow:hidden;white-space:nowrap}
@R@ .sz-av b{max-width:68px;font-size:11.5px!important;font-weight:500!important;color:var(--fm-ink2)!important;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@R@ .sz-av:hover i{transform:translateY(-2px)}
@R@ .sz-npc:has(>.sz-av input:checked)>.sz-av i,@R@ .sz-npcs:not(:has(.sz-av input:checked)) div[hidden] + .sz-npc>.sz-av i{box-shadow:inset 0 0 0 1.5px var(--fm-acc2), 0 0 0 3px color-mix(in srgb, var(--fm-acc) 25%, transparent), 0 0 18px color-mix(in srgb, var(--fm-acc2) 50%, transparent)}
@R@ .sz-npc:has(>.sz-av input:checked)>.sz-av b,@R@ .sz-npcs:not(:has(.sz-av input:checked)) div[hidden] + .sz-npc>.sz-av b{color:var(--fm-acc2)!important}
@R@ .sz-npc-b{display:none;grid-row:2;grid-column:1 / -1;grid-template-columns:232px minmax(0,1fr);column-gap:22px;align-items:start;animation:sz-up .3s ease-out both}
@R@ .sz-npc:has(>.sz-av input:checked)>.sz-npc-b,@R@ .sz-npcs:not(:has(.sz-av input:checked)) div[hidden] + .sz-npc>.sz-npc-b{display:grid}
@R@ .sz-npc-b>*{grid-column:-2 / -1;min-width:0}
@R@ .sz-npc[data-walkon] .sz-npc-b{grid-template-columns:minmax(0,1fr)}
@R@ .sz-npc[data-walkon] .sz-por{display:none}
/* 立绘位：2:3，翻长的档案时它跟着。有图（portraits.json）就是图，没有图先留一个披斗篷的影子和名字头一个字 */
@R@ .sz-npc-b>.sz-por{grid-column:1;grid-row:1 / span 30;position:sticky;top:116px;align-self:start;aspect-ratio:2 / 3;border-radius:14px;overflow:hidden;isolation:isolate;background:var(--por, none) calc(var(--p0, 5%) + var(--oc, 0) * var(--pk, 30%)) 0/var(--pw, 600%) 150% no-repeat, radial-gradient(circle at 50% 26%, var(--fm-por1), var(--fm-por2));transition:background-size .28s ease, background-position .28s ease;box-shadow:0 16px 34px rgb(0 0 0 / .5)}
@R@ .sz-por::before{content:"";position:absolute;inset:7px;z-index:2;pointer-events:none;--l:linear-gradient(var(--fm-acc2),var(--fm-acc2));background:var(--l) 0 0/15px 1px no-repeat,var(--l) 0 0/1px 15px no-repeat,var(--l) 100% 0/15px 1px no-repeat,var(--l) 100% 0/1px 15px no-repeat,var(--l) 0 100%/15px 1px no-repeat,var(--l) 0 100%/1px 15px no-repeat,var(--l) 100% 100%/15px 1px no-repeat,var(--l) 100% 100%/1px 15px no-repeat}
@R@ .sz-por::after{content:"";position:absolute;inset:0;z-index:2;border-radius:inherit;pointer-events:none;box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc) 80%, transparent), inset 0 0 0 5px rgb(8 8 28 / .22), inset 0 -90px 60px -60px rgb(8 8 28 / .6)}
@R@ .sz-por>i{position:absolute;inset:0;display:var(--init, grid);place-items:center;font-style:normal}
@R@ .sz-por>i::before{content:"";position:absolute;inset:7% 0 0;background:var(--sz-doll) center bottom/auto 100% no-repeat;opacity:.3}
@R@ .sz-por>i::after{content:attr(data-n);position:relative;width:1em;overflow:hidden;white-space:nowrap;font-family:var(--fm-serif);font-size:58px;line-height:1.2;color:var(--fm-head);opacity:.85;text-shadow:0 2px 14px rgb(0 0 0 / .6)}
/* 立绘平时看到大腿，悬停看全身；底下一块小牌写这会儿穿的是哪一套 */
@R@ .sz-npc-b>.sz-por:hover{background-size:var(--hw, 400%) 100%, auto;background-position:calc(var(--oc, 0) * var(--hk, 33.3333%)) 0, 0 0}
@R@ .sz-por-t{position:absolute;left:50%;bottom:12px;z-index:3;display:var(--ot, none);transform:translateX(-50%);padding:2px 14px;border:1px solid color-mix(in srgb, var(--fm-acc) 75%, transparent);border-radius:2px;background:color-mix(in srgb, var(--fm-band) 86%, transparent);font-size:12px!important;font-weight:500!important;letter-spacing:.14em;color:var(--fm-head)!important;white-space:nowrap}
/* 对话框：头像（九格表情挪一格）、名牌、一句话 */
@R@ .sz-say{display:grid;grid-template-columns:100px minmax(0,1fr);column-gap:16px;margin:8px 0 26px}
/* 11-08：对话框的头像只认 .sz-say 底下那一个。11-05 写成光秃秃的 .sz-face，撞了背包、技能书、装备格里早就叫 .sz-face 的那一层（label），道具外头套上了圆圈和虚线圈 */
@R@ .sz-say>.sz-face{position:relative;display:grid;place-items:center;width:88px;height:88px;margin:6px;border-radius:50%;font-style:normal;background:var(--face, none) calc(var(--fx, 0) * 50%) calc(var(--fy, 0) * 50%)/var(--fsz, 300% 300%) no-repeat, radial-gradient(circle at 50% 30%, var(--fm-por1), var(--fm-por2));box-shadow:0 0 0 2px var(--fm-acc2), 0 0 0 4px color-mix(in srgb, var(--fm-band) 82%, #000), 0 0 0 5px color-mix(in srgb, var(--fm-acc) 60%, transparent), 0 8px 18px rgb(0 0 0 / .4)}
@R@ .sz-say>.sz-face::before{content:"";position:absolute;inset:-10px;border:1px dashed color-mix(in srgb, var(--fm-acc) 45%, transparent);border-radius:50%}
@R@ .sz-say>.sz-face::after{content:attr(data-n);display:var(--init, block);width:1em;overflow:hidden;white-space:nowrap;font-family:var(--fm-serif);font-size:34px;line-height:1.2;color:var(--fm-head)}
@R@ .sz-say-b{min-width:0;padding-top:2px}
@R@ .sz-say-n{display:inline-block;margin:0 0 7px 2px;padding:2px 16px 2px 12px;border:1px solid color-mix(in srgb, var(--fm-acc) 70%, transparent);border-left:3px solid var(--fm-acc2);background:linear-gradient(90deg, color-mix(in srgb, var(--fm-acc) 26%, var(--fm-band)), color-mix(in srgb, var(--fm-acc) 6%, var(--fm-band)));font-family:var(--fm-serif);font-size:14px!important;font-weight:700!important;letter-spacing:.08em;color:var(--fm-head)!important}
@R@ .sz-prose .sz-say-b>p{position:relative;margin:0!important;padding:12px 18px;border:1px solid color-mix(in srgb, var(--fm-acc) 42%, transparent);border-radius:4px 14px 14px 14px;background:linear-gradient(180deg, color-mix(in srgb, var(--fm-acc) 10%, transparent), color-mix(in srgb, var(--fm-acc) 3%, transparent));font-size:16px;line-height:1.85}
@R@ .sz-prose .sz-say-b>p::before{content:"";position:absolute;left:-6px;top:14px;width:9px;height:9px;transform:rotate(45deg);background:var(--fm-acc2)}
/* 专名：底下一道虚线，悬停或点一下出小卡。卡的位置拿 anchor() 对准那个词，不越过这一段的左右边；不认 anchor() 的浏览器，卡落在这一行底下 */
@R@ .sz-prose p{position:relative}
@R@ .sz-t{color:var(--fm-head);text-decoration:underline dotted color-mix(in srgb, var(--fm-acc) 80%, transparent) 1px;text-underline-offset:.3em;cursor:help;outline:0;anchor-name:--szt;anchor-scope:--szt}
@R@ .sz-t:is(:hover,:focus){color:var(--fm-acc2)}
/* 11-08：专名小卡只认 .sz-t 底下那一个。11-05 写成光秃秃的 .sz-tip，撞了背包、技能书、装备的卡：它们被设成 display:block 又透明，
   点了看不见，手机上每一件底下垫一块看不见的卡，一排一排被撑开 */
@R@ .sz-t>.sz-tip{position:absolute;z-index:30;left:0;right:auto;top:auto;bottom:auto;display:block;width:min(300px, 100%);padding:9px 13px 10px;border:1px solid color-mix(in srgb, var(--fm-acc) 75%, transparent);border-radius:8px;background:color-mix(in srgb, var(--fm-band) 94%, #000);box-shadow:0 10px 26px rgb(0 0 0 / .5);font-family:var(--fm-sans, inherit);font-style:normal;font-weight:400;text-indent:0;letter-spacing:0;white-space:normal;opacity:0;visibility:hidden;pointer-events:none;transform:translateY(4px);transition:opacity .14s ease, transform .14s ease}
@R@ .sz-t>.sz-tip{left:clamp(0px, calc(anchor(--szt center) - 150px), calc(100% - min(300px, 100%)));bottom:calc(anchor(--szt top) + 6px)}
@R@ .sz-t:is(:hover,:focus)>.sz-tip{opacity:1;visibility:visible;transform:none}
@R@ .sz-t>.sz-tip::before{content:attr(data-t) var(--c, "");display:block;margin-bottom:3px;font-family:var(--fm-serif);font-size:13.5px;font-weight:700;line-height:1.5;letter-spacing:.04em;color:var(--fm-acc2)}
@R@ .sz-t>.sz-tip::after{content:var(--g, attr(data-g));display:block;font-size:13px;line-height:1.65;color:var(--fm-ink)}
@R@ .sz-npc-name{order:1;display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 12px;margin-bottom:8px}
@R@ .sz-npc-name>b{font-family:var(--fm-serif);font-size:24px!important;font-weight:700!important;letter-spacing:.06em;color:var(--fm-head)!important}
@R@ .sz-npc-name>span{font-size:12px;color:var(--fm-ink2)}
@R@ .sz-npc-tags{order:2;display:flex;flex-wrap:wrap;gap:5px 6px;margin-bottom:12px}
@R@ .sz-npc-tags span{font-size:11.5px;line-height:21px;padding:0 9px;border-radius:11px;background:color-mix(in srgb, var(--fm-acc) 12%, transparent);color:var(--fm-ink2)}
@R@ .sz-npc-tags span.lv{color:var(--fm-acc2);font-weight:600}
@R@ .sz-npc-tags span:empty{display:none}
@R@ p.sz-npc-say{order:3;position:relative;margin:0 0 14px!important;padding:10px 16px 11px 36px;border-radius:4px 14px 14px 14px;font-family:var(--fm-serif);font-size:15px;line-height:1.7;color:var(--fm-ink);background:linear-gradient(120deg, color-mix(in srgb, var(--fm-acc) 11%, transparent), transparent)}
@R@ p.sz-npc-say::before{content:"“";position:absolute;left:10px;top:-2px;font-size:34px;line-height:1.15;color:var(--fm-acc)}
@R@ .sz-npc-st{order:4;margin-bottom:12px}
/* 伤、污染、异常：有才出，一种一个颜色 */
@R@ .sz-cond{display:flex;flex-wrap:wrap;gap:5px 6px;margin-top:9px}
@R@ .sz-cond i{font-style:normal;font-size:11.5px;line-height:21px;padding:0 10px;border-radius:11px;color:#f6d6cb;background:rgb(200 84 66 / .24)}
@R@ .sz-cond i small{margin-right:5px;font-size:10.5px;opacity:.72}
@R@ .sz-cond i[data-k="污染"]{color:#ddcdf6;background:rgb(130 90 205 / .26)}
@R@ .sz-cond i[data-k="异常"]{color:#f4e6bb;background:rgb(190 150 60 / .24)}
@R@ .sz-cond i:empty{display:none}
@R@ .sz-bond{order:5;display:grid;grid-template-columns:18px auto minmax(0,1fr) auto;grid-template-rows:auto 6px auto;align-items:center;gap:5px 8px;margin-bottom:12px;font-size:12.5px;color:var(--fm-ink)}
@R@ .sz-bond>i{width:17px;height:17px;background:#e0729a;-webkit-mask:@HEART@ center/contain no-repeat;mask:@HEART@ center/contain no-repeat}
@R@ .sz-bond>b{font-family:var(--fm-serif);font-size:14px!important;color:#f0a0bc!important}
@R@ .sz-bond>em{font-style:normal;font-size:12px;color:var(--fm-ink2);font-variant-numeric:tabular-nums}
@R@ .sz-bond .sz-trk{grid-column:1 / -1;height:6px;border-radius:3px;position:relative;overflow:hidden}
@R@ .sz-bond .sz-trk::after{content:"";position:absolute;left:0;top:0;bottom:0;width:calc(min(var(--v), var(--m)) / var(--m) * 100%);border-radius:3px;background:linear-gradient(90deg, #b34f78, #f08fb0);box-shadow:0 0 8px rgb(240 143 176 / .6)}
@R@ .sz-bondx{grid-column:1 / -1;display:flex;flex-wrap:wrap;gap:3px 16px;font-size:12px;line-height:1.6;color:var(--fm-ink)}
@R@ .sz-bondx i{font-style:normal}
@R@ .sz-bondx small{margin-right:6px;font-size:10.5px;letter-spacing:.08em;color:#f0a0bc}
/* 分页签 */
@R@ .sz-nts{order:6;display:flex;gap:2px;margin:2px 0 14px;box-shadow:inset 0 -1px 0 var(--fm-line)}
@R@ .sz-nt{position:relative;flex:1 1 0;display:block;padding:7px 2px 9px;text-align:center;cursor:pointer}
@R@ .sz-nt b{font-size:12.5px!important;font-weight:500!important;letter-spacing:.12em;color:var(--fm-ink2)!important;transition:color .15s}
@R@ .sz-nt:hover b{color:var(--fm-ink)!important}
@R@ .sz-nt:has(input:checked) b,@R@ .sz-nts:not(:has(input:checked)) .sz-nt[data-t="形象"] b{color:var(--fm-acc2)!important;font-weight:700!important}
@R@ .sz-nt:has(input:checked)::after,@R@ .sz-nts:not(:has(input:checked)) .sz-nt[data-t="形象"]::after{content:"";position:absolute;left:16%;right:16%;bottom:0;height:2px;border-radius:2px;background:var(--fm-acc2);box-shadow:0 0 8px var(--fm-acc2)}
@R@ .sz-nc{order:10;display:none;margin-bottom:14px;animation:sz-up .25s ease-out both}
@R@ .sz-nc[data-k="私产"],@R@ .sz-nc[data-k="职业"]{order:11}
@R@ .sz-nc[data-k="职业能力"]{order:12}
/* 关系：三张小笺，一种一个颜色；都没有就说一句 */
@R@ .sz-rel{position:relative;margin-bottom:9px;padding:9px 14px 10px 16px;border-radius:10px;background:linear-gradient(100deg, color-mix(in srgb, var(--rc) 13%, transparent), transparent 82%)}
@R@ .sz-rel::before{content:"";position:absolute;left:0;top:9px;bottom:9px;width:2px;border-radius:2px;background:var(--rc);box-shadow:0 0 6px var(--rc)}
@R@ .sz-rel small{display:block;margin-bottom:2px;font-size:10.5px;letter-spacing:.14em;color:var(--rc)}
@R@ .sz-rel span{display:block;font-size:13.5px;line-height:1.7;color:var(--fm-ink)}
@R@ .sz-rels:not(:has(.sz-rel))::before{content:"眼下没有要记的事。";font-size:12.5px;color:var(--fm-ink2)}
/* 属性：EXP 一条，六维的盘，攻防几个大数 */
@R@ .sz-nexp{display:block;margin-bottom:4px}
@R@ .sz-nc .sz-six{height:266px;max-width:330px;margin:0 auto}
@R@ .sz-nc .sz-atks{grid-template-columns:repeat(auto-fit,minmax(70px,1fr))}
@R@ .sz-nc .sz-atks>i{flex-direction:column;align-items:center;padding:6px 6px 5px}
/* 行装：一件一行，图标、名字、品阶；私产一颗一颗 */
@R@ .sz-gears{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px 12px}
@R@ .sz-gr{display:flex;align-items:center;gap:10px;min-width:0}
@R@ .sz-gr>.sz-ic{flex:none;width:46px;height:46px;border-radius:10px;background-color:color-mix(in srgb, var(--q) 30%, #10102e);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--q) 72%, transparent)}
@R@ :is(.sz-gr,.sz-ga)>span{display:block;min-width:0}
@R@ :is(.sz-gr,.sz-ga) b{display:block;font-size:13px!important;font-weight:600!important;line-height:1.4;color:var(--fm-ink)!important}
@R@ :is(.sz-gr,.sz-ga) small{display:block;font-size:11px;line-height:1.5;color:color-mix(in srgb, var(--q) 62%, var(--fm-ink2))}
@R@ :is(.sz-gr,.sz-ga) em{display:block;margin-top:2px;font-style:normal;font-size:12.5px;line-height:1.6;color:var(--fm-ink2)}
@R@ .sz-purse{display:flex;margin-bottom:10px}
@R@ .sz-owns{display:flex;flex-wrap:wrap;gap:7px}
@R@ .sz-own{display:inline-flex;align-items:center;gap:6px;padding:3px 11px 3px 5px;border-radius:999px;background:color-mix(in srgb, var(--fm-acc) 10%, transparent);box-shadow:inset 0 0 0 1px var(--fm-line)}
@R@ .sz-own .sz-ic{flex:none;width:24px;height:24px}
@R@ .sz-own b{font-size:12px!important;font-weight:500!important;color:var(--fm-ink)!important}
/* 能力：一个一枚六角，名字和一句话 */
@R@ .sz-gabs{display:grid;gap:11px}
@R@ .sz-ga{display:flex;align-items:flex-start;gap:11px;min-width:0}
@R@ .sz-ga>.sz-hx{flex:none;width:40px;height:45px}
@R@ .sz-ga>.sz-hx::after{inset:11px 10px}
@R@ .sz-jl b{display:block;font-size:13.5px!important;font-weight:600!important;color:var(--fm-ink)!important}
@R@ .sz-jl small{display:block;margin-top:2px;font-size:12px;line-height:1.6;color:var(--fm-ink2)}

/* ---------- 见闻：一块告示板，一种东西一种样子 ---------- */
@R@ .p-news .sz-pane-body{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:18px 16px;align-items:start}
@R@ .sz-nw{position:relative;min-width:0;font-size:13.5px;line-height:1.75;color:var(--fm-ink)}
@R@ .sz-nwt{display:flex;align-items:center;gap:7px;font-size:12.5px!important;font-weight:700!important;letter-spacing:.16em;color:var(--fm-acc)!important}
@R@ .sz-nwt .sz-ic{flex:none;width:30px;height:30px;filter:drop-shadow(0 2px 3px rgb(0 0 0 / .45))}
@R@ .sz-card{grid-column:1 / -1;padding:12px 14px;border-radius:10px;background:var(--fm-panel);box-shadow:inset 0 0 0 1px var(--fm-line)}
/* 在办：任务追踪，一枚罗盘 */
@R@ .sz-track{grid-column:1 / -1;grid-row:1;display:flex;flex-wrap:wrap;align-items:center;gap:6px 26px;padding:10px 18px 11px 11px;border-radius:14px;background:linear-gradient(100deg, color-mix(in srgb, var(--fm-acc) 24%, transparent), transparent 90%);box-shadow:inset 0 0 0 1px var(--fm-edge2), 0 6px 18px rgb(0 0 0 / .2)}
@R@ .sz-track>.sz-ic{flex:none;width:46px;height:46px;filter:drop-shadow(0 3px 5px rgb(0 0 0 / .45))}
@R@ .t-c{flex:1 1 190px;min-width:0}
@R@ .t-c[data-v^="无"],@R@ .t-c[data-v^="暂无"]{display:none}
@R@ .t-c small{display:block;font-size:10.5px;letter-spacing:.14em;color:var(--fm-acc)}
@R@ .t-c b{display:block;font-family:var(--fm-serif);font-size:16px!important;font-weight:700!important;line-height:1.4;color:var(--fm-head)!important}
/* 日报：钉在板上的一张纸，一条一条，渠道盖成章 */
@R@ .sz-daily{grid-column:1;grid-row:2 / span 2;align-self:stretch;display:flex;flex-direction:column;min-height:190px;padding:24px 22px 16px;border-radius:3px;transform:rotate(-.4deg);color:#241a0e;font-family:var(--fm-serif);font-size:14px;font-weight:500;line-height:1.75;background:@PAPER@ 0 0/180px 180px, linear-gradient(180deg, #f3ead3, #e3d4b3);box-shadow:0 14px 30px rgb(0 0 0 / .4), inset 0 0 44px rgb(120 84 40 / .16)}
@R@ .sz-daily::before{content:"";position:absolute;left:50%;top:-8px;width:18px;height:18px;margin-left:-9px;border-radius:50%;background:radial-gradient(circle at 35% 30%, #e88a6a, #a3321f 60%, #5e1a0e);box-shadow:0 3px 5px rgb(0 0 0 / .45)}
@R@ .d-t{display:block;margin-bottom:8px;padding-bottom:8px;font-size:18px!important;font-weight:700!important;letter-spacing:.4em;text-indent:.4em;text-align:center;color:#5b3a1e!important;border-bottom:3px double rgb(91 58 30 / .45)}
@R@ .d-i{position:relative;display:block;padding:7px 0 7px 16px}
@R@ .d-i::before{content:"";position:absolute;left:2px;top:15px;width:6px;height:6px;transform:rotate(45deg);background:#8a5a2a}
@R@ .d-i + .d-i{border-top:1px dashed rgb(91 58 30 / .28)}
@R@ .sz-stamp{align-self:flex-end;margin:auto 0 0;transform:rotate(-6deg) translateY(4px);padding:2px 9px;border:1.5px solid rgb(160 44 30 / .72);border-radius:4px;font-style:normal;font-size:12px;font-weight:700;letter-spacing:.14em;color:rgb(160 44 30 / .82);mix-blend-mode:multiply}
/* 已知情报：一只皮面卷宗，一条一条，来源和可信度写在底下 */
@R@ .sz-intel{grid-column:2;grid-row:2;--c:#7fa6d6}
@R@ .sz-intel>.sz-nwt{display:inline-flex;margin-bottom:-1px;padding:4px 18px 4px 7px;border-radius:11px 11px 0 0;color:#d4e3f6!important;background:color-mix(in srgb, var(--c) 30%, var(--fm-band2))}
@R@ .in-b{display:block;padding:6px 14px 6px;border-radius:0 12px 12px 12px;background:linear-gradient(170deg, color-mix(in srgb, var(--c) 30%, var(--fm-band2)), color-mix(in srgb, var(--c) 9%, var(--fm-band2)));box-shadow:0 10px 22px rgb(0 0 0 / .3)}
@R@ .in-i{padding:8px 0 9px;font-size:13.5px;line-height:1.7;color:#e8edf4}
@R@ .in-i + .in-i{border-top:1px solid color-mix(in srgb, var(--c) 30%, transparent)}
@R@ .in-i>small{display:flex;flex-wrap:wrap;align-items:center;gap:2px 10px;margin-top:4px;font-size:11px;color:#adc1da}
@R@ .in-s{font-style:normal}
@R@ .in-s::before{content:"来源 ";opacity:.7}
@R@ .in-i em{display:inline-flex;align-items:center;gap:6px;margin-left:auto;font-style:normal}
@R@ .in-i em i{width:26px;height:6px;border-radius:3px;background:linear-gradient(90deg, var(--cr) calc(var(--n) * 25%), rgb(255 255 255 / .16) 0)}
/* 流言风闻：一只乌鸦，几句不知真假的话 */
@R@ .sz-rumor{grid-column:2;grid-row:3;--c:#a58fd6}
@R@ .sz-rumor>.sz-nwt{margin-bottom:6px;color:#cfc2f2!important}
@R@ .ru-i{display:block;margin:0 0 9px 8px;padding:9px 15px 10px;border-radius:15px 15px 15px 3px;font-family:var(--fm-serif);font-size:13.5px;line-height:1.75;color:var(--fm-ink);background:color-mix(in srgb, var(--c) 17%, transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--c) 34%, transparent)}
@R@ .ru-i small{display:block;margin-top:2px;font-family:inherit;font-size:11px;letter-spacing:.06em;color:#cfc2f2}
@R@ .ru-i small::before{content:"—— "}
/* 可接：委托板上一块一块挂着的木牌 */
@R@ .sz-board{grid-column:1 / -1;grid-row:4}
@R@ .sz-slips{display:grid;grid-template-columns:repeat(auto-fill,minmax(198px,1fr));gap:12px;margin-top:8px}
@R@ .sz-slip{position:relative;display:block;padding:21px 14px 12px;border-radius:5px 5px 9px 9px;color:#f5ead4;background:repeating-linear-gradient(92deg, rgb(255 255 255 / .025) 0 3px, transparent 3px 9px), linear-gradient(170deg, #7d5c3a, #533a20);box-shadow:0 8px 16px rgb(0 0 0 / .35), inset 0 0 0 1px rgb(255 224 170 / .24);transform-origin:50% 8px;transition:transform .2s}
@R@ .sz-slip::before{content:"";position:absolute;left:50%;top:7px;width:9px;height:9px;margin-left:-4.5px;border-radius:50%;background:#1a1226;box-shadow:inset 0 1px 1px #000, 0 0 0 1.5px rgb(255 224 170 / .42)}
@R@ .sz-slip:hover{transform:rotate(-1.4deg)}
@R@ .sz-slip b{display:block;font-family:var(--fm-serif);font-size:14.5px!important;font-weight:700!important;line-height:1.4;color:#fff3da!important}
@R@ .sz-slip i{display:inline-block;margin:7px 9px 0 0;padding:0 8px;border-radius:9px;font-style:normal;font-size:11px;line-height:19px;color:#2a1c0c;background:#e7c98a}
@R@ .sz-slip em{font-style:normal;font-size:12px;color:#f3d48c}
/* 线索：撕下来的一角小纸，一枚红钉、一截红线 */
@R@ .sz-clue{grid-column:1 / -1;grid-row:5}
@R@ .sz-notes{display:grid;grid-template-columns:repeat(auto-fill,minmax(216px,1fr));gap:14px;margin-top:9px;filter:drop-shadow(0 7px 9px rgb(0 0 0 / .35))}
@R@ .sz-note{position:relative;display:block;padding:15px 16px 18px 20px;color:#20252f;font-family:var(--fm-serif);font-size:13.5px;font-weight:500;line-height:23px;background:repeating-linear-gradient(180deg, transparent 0 22px, rgb(70 90 130 / .16) 22px 23px) 0 15px, linear-gradient(170deg, #eceef0, #d7dbdf);clip-path:polygon(0 0,100% 0,100% calc(100% - 5px),94% 100%,86% calc(100% - 6px),77% 100%,66% calc(100% - 4px),55% 100%,44% calc(100% - 6px),33% 100%,22% calc(100% - 4px),11% 100%,0 calc(100% - 5px))}
@R@ .sz-note:nth-child(even){transform:rotate(.6deg)}
@R@ .sz-note:nth-child(odd){transform:rotate(-.4deg)}
@R@ .sz-note::before{content:"";position:absolute;left:7px;top:8px;z-index:1;width:9px;height:9px;border-radius:50%;background:radial-gradient(circle at 35% 30%, #f09a86, #b32d1e 62%, #6b170d)}
@R@ .sz-note::after{content:"";position:absolute;left:12px;top:12px;width:130%;height:1px;background:#b32d1e;opacity:.55;transform:rotate(-5deg);transform-origin:0 0}

/* ---------- 记忆：页头一排数，点一个只看这一类；一类一块、一类一种样子 ---------- */
@R@ .p-mem .sz-pane-body{position:relative;display:flex;flex-direction:column;counter-reset:ma mc my ms ml md mf}
@R@ .sz-mts{order:-1;display:grid;grid-template-columns:repeat(auto-fit,minmax(86px,1fr));gap:8px;margin-bottom:6px}
@R@ .sz-mt{position:relative;display:grid;grid-template-columns:36px minmax(0,1fr);grid-template-rows:auto auto;column-gap:5px;align-items:center;padding:7px 8px 7px 6px;border-radius:12px;cursor:pointer;background:linear-gradient(150deg, color-mix(in srgb, var(--mc) 15%, transparent), transparent 85%);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--mc) 26%, transparent);transition:box-shadow .15s, transform .15s}
@R@ .sz-mt>.sz-ic{grid-row:1 / span 2;width:36px;height:36px;filter:drop-shadow(0 2px 4px rgb(0 0 0 / .4))}
@R@ .sz-mt>em{font-style:normal;font-family:var(--fm-serif);font-size:22px;font-weight:700;line-height:1.05;color:var(--fm-head)}
@R@ .sz-mt>b{font-size:11px!important;font-weight:500!important;letter-spacing:.04em;line-height:1.3;color:var(--fm-ink2)!important;white-space:nowrap}
@R@ .sz-mt:hover{transform:translateY(-1px)}
@R@ .sz-mt:has(input:checked),@R@ .sz-mts:not(:has(input:checked)) .sz-mt[data-k="全部"]{background:linear-gradient(150deg, color-mix(in srgb, var(--mc) 30%, transparent), color-mix(in srgb, var(--mc) 8%, transparent));box-shadow:inset 0 0 0 1.5px var(--mc), 0 0 14px color-mix(in srgb, var(--mc) 36%, transparent)}
@R@ .sz-mh{display:flex;align-items:center;gap:8px;margin:14px 0 9px}
@R@ .sz-mh>.sz-ic{flex:none;width:24px;height:24px}
@R@ .sz-mh>b{font-family:var(--fm-serif);font-size:14px!important;font-weight:700!important;letter-spacing:.14em;color:var(--mc)!important}
@R@ .sz-mh::after{content:"";order:1;flex:1;height:1px;background:linear-gradient(90deg, color-mix(in srgb, var(--mc) 45%, transparent), transparent)}
@R@ .sz-mh>em{order:2;font-style:normal;font-family:var(--fm-serif);font-size:13px;color:var(--mc)}
@R@ .sz-mh[data-k="核心"]{order:100}
@R@ .sz-mh[data-k="未结因果"]{order:200}
@R@ .sz-mh[data-k="短期"]{order:1000}
@R@ .sz-mh[data-k="长期"]{order:2000}
@R@ .sz-mh[data-k="已完成"]{order:3000}
@R@ .sz-mh[data-k="修正"]{order:4000}
@R@ .sz-mm{position:relative;order:5000;font-size:13.5px;line-height:1.75;color:var(--fm-ink)}
@R@ .m-w{display:flex;flex-wrap:wrap;align-items:baseline;gap:1px 10px;margin-bottom:3px}
@R@ .m-w time{font-size:11.5px;letter-spacing:.02em;color:var(--mc);font-variant-numeric:tabular-nums}
@R@ .m-w small{font-size:12px;font-weight:600;color:var(--fm-ink)}
@R@ .m-t{display:block}
@R@ .sz-ar{display:inline-block;width:7px;height:7px;margin:0 8px 1px 4px;border-top:1.5px solid var(--mc);border-right:1.5px solid var(--mc);transform:rotate(45deg)}
/* 长期和核心一条两三百字：露三行，点一下展开 */
@R@ .m-fold{display:block;cursor:pointer}
@R@ .m-fold .m-t{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:3;overflow:hidden}
@R@ .m-fold:has(input:checked) .m-t{display:block}
@R@ .m-fold::after{content:"";position:absolute;right:13px;bottom:9px;width:7px;height:7px;border-right:1.5px solid var(--mc);border-bottom:1.5px solid var(--mc);transform:rotate(45deg);transition:transform .15s}
@R@ .m-fold:has(input:checked)::after{transform:rotate(-135deg)}
/* 核心：一块发光的琥珀 */
@R@ .sz-mm[data-k="核心"]{order:101;margin-bottom:10px;padding:13px 30px 14px 18px;border-radius:12px;background:radial-gradient(130% 150% at 0 0, color-mix(in srgb, var(--mc) 30%, transparent), transparent 64%);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--mc) 72%, transparent), 0 0 22px color-mix(in srgb, var(--mc) 16%, transparent)}
@R@ .sz-mm[data-k="核心"] .m-t{font-family:var(--fm-serif);font-size:14.5px;color:var(--fm-head)}
/* 未结因果：一根红线还没剪 */
@R@ .sz-th{order:201;margin-bottom:10px;padding:10px 14px 11px 24px;border-radius:10px;background:linear-gradient(105deg, color-mix(in srgb, var(--mc) 15%, transparent), transparent 85%);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--mc) 36%, transparent)}
@R@ .sz-th::before{content:"";position:absolute;left:8px;top:9px;bottom:9px;width:8px;background:@THREAD@ center top/8px 26px repeat-y}
@R@ .sz-th .m-t{margin-top:2px}
@R@ .th-h{display:flex;flex-wrap:wrap;align-items:center;gap:2px 10px}
@R@ .th-h b{font-family:var(--fm-serif);font-size:14.5px!important;font-weight:700!important;color:var(--fm-head)!important}
@R@ .th-h i{font-style:normal;font-size:12px;color:var(--fm-ink2)}
@R@ .th-h em{margin-left:auto;padding:0 9px;border-radius:10px;font-style:normal;font-size:11px;line-height:20px;white-space:nowrap;color:var(--mc);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--mc) 55%, transparent)}
@R@ .th-f{display:flex;flex-wrap:wrap;gap:1px 16px;margin-top:5px;font-size:12px;line-height:1.6;color:var(--fm-ink2)}
@R@ .th-f i{font-style:normal}
@R@ .th-f small{margin-right:5px;font-size:10.5px;letter-spacing:.08em;color:var(--mc)}
/* 短期：一条时间线，最新的在最上头 */
@R@ .sz-mm[data-k="短期"]{order:calc(1999 - var(--n, 0));padding:0 0 14px 36px}
@R@ .sz-mm[data-k="短期"]::before{content:"";position:absolute;left:12px;top:24px;bottom:0;width:1px;background:linear-gradient(var(--mc), color-mix(in srgb, var(--mc) 18%, transparent))}
@R@ .m-n{position:absolute;left:0;top:0;display:grid;place-items:center;width:25px;height:25px;border-radius:50%;font-style:normal;font-family:var(--fm-serif);font-size:12.5px;font-weight:700;color:#0e1a2a;background:radial-gradient(circle at 35% 30%, #e6f5ff, var(--mc));box-shadow:0 0 10px color-mix(in srgb, var(--mc) 55%, transparent)}
/* 长期：一页夹着书签的书 */
@R@ .sz-mm[data-k="长期"]{order:2001;margin-bottom:10px;padding:11px 32px 13px 17px;border-radius:4px 12px 12px 4px;background:linear-gradient(100deg, color-mix(in srgb, var(--mc) 16%, transparent), transparent 90%);box-shadow:inset 3px 0 0 color-mix(in srgb, var(--mc) 80%, transparent), inset 0 0 0 1px color-mix(in srgb, var(--mc) 22%, transparent)}
@R@ .sz-mm[data-k="长期"]::before{content:"";position:absolute;right:12px;top:0;width:11px;height:20px;background:var(--mc);clip-path:polygon(0 0,100% 0,100% 100%,50% 76%,0 100%)}
/* 已完成：打过钩的一行 */
@R@ .sz-mm[data-k="已完成"]{order:3001;display:flex;flex-wrap:wrap;align-items:baseline;gap:1px 10px;padding:6px 2px 7px 22px;font-size:12.5px;line-height:1.6;color:var(--fm-ink2);box-shadow:inset 0 -1px 0 color-mix(in srgb, var(--fm-line) 55%, transparent)}
@R@ .sz-mm[data-k="已完成"]::before{content:"";position:absolute;left:4px;top:11px;width:10px;height:5px;border-left:2px solid var(--mc);border-bottom:2px solid var(--mc);transform:rotate(-45deg)}
@R@ .sz-mm[data-k="已完成"] b{font-weight:600!important;color:var(--fm-ink)!important}
@R@ .sz-mm[data-k="已完成"] em{margin-left:auto;font-style:normal;font-size:12px;color:var(--mc)}
@R@ .sz-mm[data-k="修正"]{order:4001;font-size:12.5px}

/* ---------- 普通战斗：遭遇题、敌人一张张，威胁一色 ---------- */
@R@ .sz-enc{display:flex;align-items:baseline;justify-content:center;gap:12px;margin:0 0 16px;padding:10px 12px;border-radius:10px;background:linear-gradient(90deg, transparent, rgb(150 110 80 / .24), transparent)}
@R@ .sz-enc small{font-size:11px;letter-spacing:.2em;color:#e6c8a4}
@R@ .sz-enc b{font-family:var(--fm-serif);font-size:18px!important;font-weight:700!important;letter-spacing:.1em;color:var(--fm-head)!important}
@R@ .sz-enc span{font-size:11.5px;letter-spacing:.14em;color:#e6c8a4}
@R@ .sz-foe{position:relative;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:18px;margin:0 0 12px;padding:12px 16px 12px 18px;border-radius:10px;overflow:hidden;background:linear-gradient(100deg, color-mix(in srgb, var(--t) 15%, transparent), transparent 70%);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--t) 45%, transparent)}
@R@ .sz-foe::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--t);box-shadow:0 0 10px var(--t)}
@R@ .sz-foe .f-h{grid-column:1 / -1;display:flex;align-items:baseline;gap:10px;margin-bottom:9px}
@R@ .sz-foe .f-h b{font-family:var(--fm-serif);font-size:16.5px!important;font-weight:700!important;color:var(--fm-head)!important}
@R@ .sz-foe .f-h small{font-size:11.5px;color:var(--fm-ink2)}
@R@ .sz-foe .f-h em{margin-left:auto;padding:0 10px;border-radius:10px;font-style:normal;font-size:11.5px;line-height:20px;letter-spacing:.1em;color:#fff;background:color-mix(in srgb, var(--t) 72%, #000)}
@R@ .sz-foe p{grid-column:1 / -1;margin:8px 0 0!important;font-size:13px;line-height:1.7;color:var(--fm-ink2)}
@R@ .sz-wn{display:grid;grid-template-columns:3em 1fr;gap:10px;padding:6px 2px;font-size:13px;line-height:1.7;color:var(--fm-ink)}
@R@ .sz-wn>b{color:#f0a070;font-weight:600}
@R@ .sz-wn:not(:has(>b)){display:block}
@R@ .p-war:has(.sz-boss) .sz-wn{grid-column:1 / -1;order:20}
/* ---------- 史诗战：一整幅 Boss，名号、第几阶段、势条压在画上；底下乐章和几张情报 ---------- */
@R@ .p-war:has(.sz-boss) .sz-pane-body{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;align-items:stretch}
@R@ .p-war:has(.sz-boss) .sz-pane-head b{color:#ffdcc0!important;text-shadow:0 0 14px rgb(255 96 60 / .55)}
@R@ .sz-boss{grid-column:1 / -1;position:relative;isolation:isolate;display:flex;align-items:flex-end;min-height:388px;border-radius:14px;overflow:hidden;background:radial-gradient(90% 120% at 78% 26%, rgb(130 30 30 / .5), transparent 70%), linear-gradient(180deg, #170b1e, #0a0612);box-shadow:inset 0 0 0 1px rgb(226 124 84 / .6), 0 0 30px rgb(200 60 40 / .26), 0 16px 34px rgb(0 0 0 / .5)}
@R@ .sz-boss-art{position:absolute;top:0;right:0;bottom:0;width:66%;z-index:-1;background:var(--bart, var(--sz-doll)) 50% 10%/cover no-repeat;filter:var(--bf, hue-rotate(135deg) saturate(1.5) brightness(.62));-webkit-mask:linear-gradient(90deg, transparent, #000 42%);mask:linear-gradient(90deg, transparent, #000 42%)}
@R@ .sz-boss::after{content:"";position:absolute;left:0;right:0;bottom:0;height:62%;z-index:-1;background:linear-gradient(transparent, rgb(8 4 14 / .94) 72%);pointer-events:none}
@R@ .sz-boss-in{position:relative;width:100%;padding:20px 20px 16px}
@R@ .b-k{display:block;font-size:10.5px;letter-spacing:.34em;color:#ff9c7a}
@R@ .b-n{display:block;margin-top:4px;font-family:var(--fm-serif);font-size:34px!important;font-weight:700!important;line-height:1.15;letter-spacing:.08em;color:#fff0dc!important;text-shadow:0 0 18px rgb(255 96 60 / .65), 0 2px 6px #000}
@R@ .b-f{display:flex;flex-wrap:wrap;gap:0 12px;margin-top:4px;font-size:12px;letter-spacing:.06em;color:#e8c8b8}
@R@ .b-f i{font-style:normal}
@R@ .b-f i:empty{display:none}
@R@ .b-ph{display:flex;align-items:center;gap:10px;margin-top:10px}
@R@ .b-ph em{font-style:normal;font-size:12.5px;letter-spacing:.1em;color:#ffd9b8}
@R@ .sz-pips{display:inline-flex;align-items:center;gap:7px}
@R@ .sz-pips i{display:block;width:10px;height:10px;transform:rotate(45deg) scale(calc(1 + var(--now, 0) * .3));background:color-mix(in srgb, color-mix(in srgb, #ffcf8a calc(var(--now, 0) * 100%), #a8703f) calc(var(--on, 0) * 100%), transparent);box-shadow:inset 0 0 0 1px rgb(255 196 150 / .65), 0 0 calc(var(--now, 0) * 12px) #ff9c5a}
@R@ .b-pn{display:block;margin-top:5px;font-family:var(--fm-serif);font-size:16px;line-height:1.45;letter-spacing:.04em;color:#ffe9d2;text-shadow:0 1px 4px #000}
@R@ .b-bars{display:grid;gap:9px;margin-top:14px}
@R@ .b-bars .sz-bar{grid-template-rows:auto 11px}
@R@ .b-bars .sz-bar>b{color:#ffe0c8!important}
@R@ .b-bars .sz-bar>em{color:#ffd0b0}
@R@ .b-bars .sz-bar.bl{--c:#e0523f}
@R@ .b-bars .sz-bar.bl .sz-trk{height:11px;border-radius:2px;background:rgb(0 0 0 / .5);box-shadow:inset 0 0 0 1px rgb(255 200 160 / .5), 0 0 12px rgb(220 60 40 / .4)}
@R@ .b-bars .sz-bar.bl .sz-trk::after{border-radius:1px;background:linear-gradient(180deg, #ff8a6a, #d23a2a 55%, #8e1f18);box-shadow:0 0 10px rgb(240 80 50 / .7)}
@R@ .b-bars .sz-bar.bp{--c:#e8a25a;grid-template-rows:auto 5px}
@R@ .b-bars .sz-bar.bp .sz-trk{height:5px;background:rgb(0 0 0 / .5)}
/* 乐章：一道金线的谱 */
@R@ .sz-canto{grid-column:1 / -1;order:2;position:relative;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px 18px;padding:12px 16px 13px;border-radius:12px;color:#f4ead0;background:repeating-linear-gradient(180deg, transparent 0 8px, rgb(240 210 140 / .1) 8px 9px) 0 8px/100% 45px no-repeat, linear-gradient(110deg, rgb(200 160 80 / .26), rgb(70 45 100 / .22));box-shadow:inset 0 0 0 1px rgb(230 190 110 / .55), 0 0 20px rgb(230 190 110 / .14)}
@R@ .c-t{grid-column:1 / -1;display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 10px}
@R@ .c-t small{font-size:11px;letter-spacing:.2em;color:#e6c98c}
@R@ .c-t b{font-family:var(--fm-serif);font-size:17px!important;font-weight:700!important;letter-spacing:.06em;color:#fff3d6!important}
@R@ .c-l{font-size:12.5px;color:#f2d48a}
@R@ .c-t em{margin-left:auto;padding:0 9px;border-radius:10px;font-style:normal;font-size:11px;line-height:20px;color:#fff3d6;background:rgb(230 180 90 / .34)}
@R@ .sz-canto[data-v^="无"] .c-t em{color:#d8c8a4;background:none;box-shadow:inset 0 0 0 1px rgb(230 190 110 / .35)}
@R@ .c-side{display:block;font-size:13px;line-height:1.65;color:#f4ead0}
@R@ .c-side small{display:block;font-size:10.5px;letter-spacing:.14em;color:#e6c98c}
/* 情报：一类一个颜色 */
@R@ .sz-bi{--bc:#d6b26a;min-width:0;padding:10px 13px 11px;border-radius:10px;background:linear-gradient(140deg, color-mix(in srgb, var(--bc) 14%, transparent), transparent 80%);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--bc) 34%, transparent)}
@R@ .sz-bi>b{display:block;margin-bottom:4px;font-size:11.5px!important;font-weight:700!important;letter-spacing:.16em;color:var(--bc)!important}
@R@ .b-i{display:block;font-size:13px;line-height:1.65;color:var(--fm-ink)}
@R@ .b-i + .b-i{margin-top:5px}
@R@ .b-i b{margin-right:7px;font-weight:600!important;color:var(--fm-head)!important}
@R@ .sz-ward{grid-column:1 / -1;display:flex;align-items:center;gap:12px;padding:8px 13px}
@R@ .sz-ward>b{margin:0}
@R@ .sz-ward>span{font-size:13px;color:var(--fm-ink)}
/* 手札页头上的入场卡：开战那一轮才有 */
@R@ .sz-bintro{display:flex;flex-direction:column;align-items:center;gap:1px;margin:4px 0 14px;padding:13px 12px 14px;text-align:center;background:linear-gradient(90deg, transparent, rgb(190 50 40 / .34) 26%, rgb(190 50 40 / .34) 74%, transparent);box-shadow:0 -1px 0 rgb(255 170 130 / .35), 0 1px 0 rgb(255 170 130 / .35)}
@R@ .sz-bintro small{font-size:11px;letter-spacing:.42em;color:#ff9c7a}
@R@ .sz-bintro b{font-family:var(--fm-serif);font-size:27px!important;font-weight:700!important;letter-spacing:.14em;color:#fff0dc!important;text-shadow:0 0 18px rgb(255 96 60 / .6)}
@R@ .sz-bintro span{font-size:12.5px;letter-spacing:.1em;color:#ffc9b0}
@L@:has(.p-war) .t-war{color:#ff9c84;animation:sz-war 2s ease-in-out infinite}
@L@:has(.sz-boss) .t-war{color:#ffd28a;animation:sz-war2 1.5s ease-in-out infinite}
@keyframes sz-war2{50%{filter:drop-shadow(0 0 10px #ff8a3a) drop-shadow(0 0 3px #ffd28a)}}
@keyframes sz-war{50%{filter:drop-shadow(0 0 7px #ff6b4a)}}
@media (prefers-reduced-motion:reduce){@R@ .sz-doll-ring,@L@ .t-war{animation:none!important}@R@ :is(.sz-pane,.sz-npc-b,.sz-tip-in){animation:none!important}}

/* ---------- 手机：一列；点一下才出卡，卡长在那一排底下；再点卡上的叉收起 ---------- */
@media (max-width:1099px){
  @R@ .sz-pane-head{margin-bottom:14px}
  @L@ details.sz-hud>summary.sz-head{grid-template-columns:50px minmax(0,1fr);column-gap:10px;padding:8px 10px 10px 8px!important}
  @L@ .sz-dial{width:50px;height:50px}
  @L@ .sz-time{font-size:12px}
  @L@ .sz-sub{padding-right:44px}
  @L@ .sz-place{font-size:12px;letter-spacing:.04em}
  @L@ .sz-place b:last-child{font-size:17px;letter-spacing:.06em}
  @L@ .sz-dl1{font-size:11.5px;gap:1px 8px}
  @L@ .sz-quest{font-size:12px}
  @R@ .p-panel .sz-pane-body{grid-template-columns:minmax(0,1fr);max-width:420px;margin:0 auto}
  @R@ .sz-doll{grid-column:1;grid-row:1;height:338px}
  @R@ :is(.sz-sl,.sz-sk){left:calc(var(--x, 0) * (100% - 58px))}
  @R@ .sz-sk{left:calc(var(--x, 0) * (100% - 58px))}
  @R@ .sz-sl .sz-tip{left:0;top:64px;width:min(280px, calc(100vw - 48px))}
  @R@ .sz-sl[style],@R@ .sz-sl:is([data-s="副手"],[data-s="配饰"],[data-s^="饰品"],[data-s="足"]) .sz-tip{left:auto;right:0}
  @R@ .sz-tip-x{display:block;position:absolute;right:6px;top:6px;width:24px;height:24px;border-radius:50%;background:rgb(0 0 0 / .35);cursor:pointer}
  @R@ .sz-tip-x input{display:none!important}
  @R@ .sz-tip-x::before,@R@ .sz-tip-x::after{content:"";position:absolute;left:6px;right:6px;top:11px;height:2px;background:#fff;transform:rotate(45deg)}
  @R@ .sz-tip-x::after{transform:rotate(-45deg)}
  @R@ .sz-tip-h{padding-right:96px}
  @R@ .sz-tip-h .sz-ic{right:30px}
  @R@ .sz-idc{grid-column:1;grid-row:2}
  @R@ .sz-lv{grid-column:1;grid-row:3}
  @R@ .sz-res{grid-column:1;grid-row:4}
  @R@ .sz-seal{grid-column:1;grid-row:5}
  @R@ .sz-six{grid-column:1;grid-row:6;width:300px;max-width:100%;margin:0 auto}
  @R@ .sz-atk{grid-column:1;grid-row:7}
  @R@ .sz-road{grid-column:1;grid-row:8}
  @R@ .sz-arch{grid-column:1;grid-row:3 / span 3}
  @R@ .sz-qcard{grid-column:1;grid-row:9}
  @R@ .sz-gridit{grid-template-columns:repeat(5,minmax(0,1fr));column-gap:6px;grid-auto-flow:dense}
  @R@ .sz-gridit::before{display:none}
  @R@ .sz-gridit .sz-tip{grid-column:1 / -1;grid-row:auto;position:relative;top:auto;height:auto;margin:0 0 10px}
  @R@ .sz-gridit :is(.sz-bagn,.sz-row){grid-column:1 / -1}
  @R@ .sz-pad{width:100%;height:auto;aspect-ratio:1}
  @R@ .sz-ab .sz-nm{width:100%}
  @R@ .sz-hx{width:50px;height:56px}
  @R@ .sz-hx::after{inset:14px 12px}
  @R@ .sz-job{padding:0}
  @R@ .sz-book{margin:0 2px 14px}
  @R@ .sz-marks{gap:2px;padding:0 6px;justify-content:space-between}
  @R@ .sz-cat{padding:5px 6px 7px}
  @R@ .sz-cat i{display:none}
  @R@ .sz-cat b{font-size:11px!important;letter-spacing:0}
  @R@ .sz-abs{grid-template-columns:repeat(4,minmax(0,1fr));grid-auto-flow:dense;min-height:0;padding:14px 12px 18px;background:linear-gradient(90deg, rgb(120 90 50 / .2), transparent 14px, transparent calc(100% - 14px), rgb(120 90 50 / .2)),@PAPER@ 0 0/180px 180px,linear-gradient(180deg, #f3ead2, #e6d8b7)}
  @R@ .sz-chap{grid-column:1 / -1}
  @R@ .sz-abs .sz-row{grid-column:1 / -1}
  @R@ .sz-abs .sz-tip{grid-column:1 / -1;grid-row:auto;position:relative;top:auto;height:auto;margin:2px 0 10px;padding:12px;border-radius:8px;background:rgb(255 250 235 / .55);box-shadow:inset 0 0 0 1px rgb(91 58 30 / .22)}
  @R@ .p-war:has(.sz-boss) .sz-pane-body{grid-template-columns:minmax(0,1fr)}
  @R@ .sz-boss{min-height:340px}
  @R@ .sz-boss-art{width:100%;-webkit-mask:none;mask:none}
  @R@ .sz-boss::after{height:78%}
  @R@ .sz-boss-in{padding:16px 14px 14px}
  @R@ .b-n{font-size:27px!important}
  @R@ .sz-canto{grid-template-columns:minmax(0,1fr)}
  @R@ .sz-foe{grid-template-columns:minmax(0,1fr);row-gap:7px}
  @R@ .sz-bagtop{flex-wrap:wrap;gap:8px 14px}
  @R@ .sz-bagtop .sz-bar{flex:1 1 100%;max-width:none;margin:0}
  @R@ .sz-coins{gap:9px}
  @R@ .sz-goal{grid-template-columns:repeat(2,minmax(0,1fr))}
  @R@ .sz-path i{width:38px}
  @R@ .sz-path i b{font-size:11px!important;letter-spacing:0}
  @R@ .p-news .sz-pane-body{grid-template-columns:minmax(0,1fr)}
  @R@ .p-news .sz-nw{grid-column:1;grid-row:auto}
  @R@ .sz-track{order:-5}
  @R@ .sz-daily{order:-4;align-self:auto;min-height:0}
  @R@ .sz-board{order:-3}
  @R@ .sz-intel{order:-2}
  @R@ .sz-clue{order:-1}
  @R@ .sz-mts{grid-template-columns:repeat(3,minmax(0,1fr))}
  @R@ .sz-gears{grid-template-columns:minmax(0,1fr)}
  /* 同行的头像一排横着滑（11-08 用户：手机端上的角色那里做成可以横向滑动选取）。头像一人一格排第一行（几个人就几格，--nn 照人数数），
     档案那一块在第二行占满这几格，粘在窗口左边（sticky），滑头像时它不跟着走；宽用 100cqw（这一排自己的宽），不认 cqw 的退回屏宽减边 */
  @R@ .sz-npcs{container-type:inline-size;grid-template-columns:repeat(var(--nn, 1), 62px);grid-auto-columns:62px;column-gap:6px;overflow-x:auto;overflow-y:hidden;overscroll-behavior-x:contain;scrollbar-width:none}
  @R@ .sz-npcs::-webkit-scrollbar{display:none}
  @R@ .sz-av{margin-bottom:12px}
  @R@ .sz-av b{max-width:62px}
  @R@ .sz-npc-b{position:sticky;left:0;width:calc(100vw - 60px);width:100cqw;grid-template-columns:104px minmax(0,1fr);column-gap:12px}
  @R@ .sz-npc-b>*{grid-column:1 / -1}
  @R@ .sz-npc-b>.sz-por{grid-column:1;grid-row:1 / span 2;position:relative;top:auto;margin-bottom:12px}
  @R@ .sz-npc-b>:is(.sz-npc-name,.sz-npc-tags){grid-column:2}
  @R@ .sz-npc[data-walkon] .sz-npc-b{grid-template-columns:minmax(0,1fr)}
  @R@ .sz-npc[data-walkon] .sz-npc-b>:is(.sz-npc-name,.sz-npc-tags){grid-column:1}
  @R@ .sz-por>i::after{font-size:38px}
  @R@ .sz-por-t{bottom:8px;padding:1px 8px;font-size:11px!important}
  @R@ .sz-say{grid-template-columns:70px minmax(0,1fr);column-gap:12px;margin-bottom:20px}
  @R@ .sz-say>.sz-face{width:58px;height:58px;margin:5px}
  @R@ .sz-say>.sz-face::before{inset:-7px}
  @R@ .sz-say>.sz-face::after{font-size:24px}
  @R@ .sz-prose .sz-say-b>p{padding:9px 13px;font-size:15px;line-height:1.75}
  @R@ .sz-road,@R@ .sz-job{gap:8px}
  @R@ .sz-npc-name>b{font-size:19px!important;flex:1 1 100%}
  @R@ .sz-nt b{font-size:12px!important;letter-spacing:.04em}
}
/* ---- 月银纪这一条回复自己的样子，放在最后，压过上面同权重的 ---- */
@RM@ .sz-sealb{display:none}
/* 这一纪到天灾为止，路上五个节点是人认的：认兵、成式、名器、冠名 */
@RM@ .sz-path i::after{font-size:10.5px;line-height:1;letter-spacing:.04em;white-space:nowrap;color:color-mix(in srgb, var(--fm-ink2) calc(55% + var(--on, 0) * 45%), transparent)}
@RM@ .sz-path i[data-t="启源"]::after{content:"跟着打杂"}
@RM@ .sz-path i[data-t="共鸣"]::after{content:"认兵"}
@RM@ .sz-path i[data-t="灵格"]::after{content:"成式"}
@RM@ .sz-path i[data-t="极境"]::after{content:"名器"}
@RM@ .sz-path i[data-t="英雄"]::after{content:"冠名"}
@RM@ .sz-path i[data-t="传奇"]::after{content:"到天灾为止"}
/* 诗人在唱：一张歌谱，不是报纸。头上一架小竖琴替了图钉，唱的人写在末尾 */
@RM@ .sz-daily{background:repeating-linear-gradient(180deg, transparent 0 25px, rgb(91 58 30 / .1) 25px 26px) 0 58px no-repeat, @PAPER@ 0 0/180px 180px, linear-gradient(180deg, #efe3c7, #dccbaa)}
@RM@ .sz-daily::before{top:-13px;width:30px;height:30px;margin-left:-15px;border-radius:0;box-shadow:none;background:@LYRE@ center/contain no-repeat}
@RM@ .d-t{letter-spacing:.3em;text-indent:.3em;border-bottom:1px solid rgb(91 58 30 / .4)}
@RM@ .sz-stamp{transform:none;padding:0;border:0;border-radius:0;font-weight:600;letter-spacing:.08em;color:#6b4a26;mix-blend-mode:normal}
/* 悬赏板：一块钉在墙上的木板，羊皮纸一张一张钉上去，上头写兽和赏格 */
@RM@ .sz-slips{padding:16px 14px 18px;border-radius:6px;background:repeating-linear-gradient(90deg, rgb(0 0 0 / .16) 0 1px, transparent 1px 96px), repeating-linear-gradient(92deg, rgb(255 255 255 / .02) 0 3px, transparent 3px 9px), linear-gradient(170deg, #594530, #3a2b1b);box-shadow:inset 0 0 0 1px rgb(255 224 170 / .16), inset 0 10px 18px rgb(0 0 0 / .3)}
@RM@ .sz-slip{padding:20px 13px 11px;border-radius:2px;color:#2a1c0c;background:@PAPER@ 0 0/180px 180px, linear-gradient(175deg, #efe3c7, #d9c8a6);box-shadow:0 6px 12px rgb(0 0 0 / .42);transform:rotate(-.7deg)}
@RM@ .sz-slip:nth-child(even){transform:rotate(.8deg)}
@RM@ .sz-slip::before{background:radial-gradient(circle at 35% 30%, #cfd4dc, #6a6f78 60%, #33363c);box-shadow:0 1px 2px rgb(0 0 0 / .6)}
@RM@ .sz-slip b{color:#2a1c0c!important}
@RM@ .sz-slip i{color:#f6e7cf;background:#7a2f1e}
@RM@ .sz-slip em{color:#5b3a1e}
/* ---- 纷争纪这一条回复自己的样子，放在最后，压过上面同权重的 ---- */
@RS@ .sz-sealb{display:none}
/* 墙上量一个人：一条路到传奇为止，节点下头写墙上怎么看这一档 */
@RS@ .sz-path i::after{font-size:10.5px;line-height:1;letter-spacing:.04em;white-space:nowrap;color:color-mix(in srgb, var(--fm-ink2) calc(55% + var(--on, 0) * 45%), transparent)}
@RS@ .sz-path i[data-t="启源"]::after{content:"新兵"}
@RS@ .sz-path i[data-t="共鸣"]::after{content:"寻常的兵"}
@RS@ .sz-path i[data-t="灵格"]::after{content:"老兵"}
@RS@ .sz-path i[data-t="极境"]::after{content:"一方镇将"}
@RS@ .sz-path i[data-t="英雄"]::after{content:"改写一场会战"}
@RS@ .sz-path i[data-t="传奇"]::after{content:"战报留名"}
/* 战报：军册上撕下来的一页，左边一道红线，头上一枚段城的火漆，写的人落在末尾 */
@RS@ .sz-daily{background:linear-gradient(90deg, transparent 26px, rgb(150 44 28 / .5) 26px 27.5px, transparent 27.5px) 0 0 no-repeat, repeating-linear-gradient(180deg, transparent 0 25px, rgb(70 50 34 / .12) 25px 26px) 0 58px no-repeat, @PAPER@ 0 0/180px 180px, linear-gradient(180deg, #e7dcc4, #d3c3a4)}
@RS@ .sz-daily::before{top:-12px;width:28px;height:28px;margin-left:-14px;border-radius:50%;background:radial-gradient(circle at 38% 32%, #d0553d, #8a2418 62%, #5e140c);box-shadow:0 2px 5px rgb(0 0 0 / .5), inset 0 0 0 3px rgb(0 0 0 / .14)}
@RS@ .d-t{letter-spacing:.3em;text-indent:.3em;border-bottom:1px solid rgb(70 50 34 / .4)}
@RS@ .sz-stamp{transform:none;padding:0;border:0;border-radius:0;font-weight:600;letter-spacing:.08em;color:#7a2c1c;mix-blend-mode:normal}
/* 段城门口的赏格：一面白石墙，告示拿铁钉钉上去，上头写要对上的东西和赏格 */
@RS@ .sz-slips{padding:16px 14px 18px;border-radius:4px;background:repeating-linear-gradient(0deg, rgb(0 0 0 / .26) 0 1px, transparent 1px 46px), repeating-linear-gradient(90deg, rgb(0 0 0 / .16) 0 1px, transparent 1px 104px), linear-gradient(170deg, #5b5c66, #393a43);box-shadow:inset 0 0 0 1px rgb(255 255 255 / .1), inset 0 10px 18px rgb(0 0 0 / .32)}
@RS@ .sz-slip{padding:20px 13px 11px;border-radius:2px;color:#2a1c0c;background:@PAPER@ 0 0/180px 180px, linear-gradient(175deg, #e7dcc4, #cfbf9f);box-shadow:0 6px 12px rgb(0 0 0 / .46);transform:rotate(-.6deg)}
@RS@ .sz-slip:nth-child(even){transform:rotate(.7deg)}
@RS@ .sz-slip::before{background:radial-gradient(circle at 35% 30%, #b9bcc4, #5a5d66 60%, #2b2d33);box-shadow:0 1px 2px rgb(0 0 0 / .6)}
@RS@ .sz-slip b{color:#2a1c0c!important}
@RS@ .sz-slip i{color:#f6e7cf;background:#7c2a1a}
@RS@ .sz-slip em{color:#5e3a22}
/* ---- 山铜纪这一条回复自己的样子，放在最后，压过上面同权重的 ---- */
@RB@ .sz-sealb{display:none}
/* 碑上量一个人：节点下头写这一纪怎么看这一档，走到传奇才上碑的正面 */
@RB@ .sz-path i::after{font-size:10.5px;line-height:1;letter-spacing:.04em;white-space:nowrap;color:color-mix(in srgb, var(--fm-ink2) calc(55% + var(--on, 0) * 45%), transparent)}
@RB@ .sz-path i[data-t="启源"]::after{content:"刚拿起家什"}
@RB@ .sz-path i[data-t="共鸣"]::after{content:"接得了活"}
@RB@ .sz-path i[data-t="灵格"]::after{content:"团里的顶梁"}
@RB@ .sz-path i[data-t="极境"]::after{content:"一方有名"}
@RB@ .sz-path i[data-t="英雄"]::after{content:"改得了一件事"}
@RB@ .sz-path i[data-t="传奇"]::after{content:"碑的正面"}
/* 碑和传唱：一块拓片，黑纸白字，上头圆一点像碑顶，碑匠的落款在末尾 */
@RB@ .sz-daily{transform:none;border-radius:64px 64px 4px 4px / 26px 26px 4px 4px;color:#ebe7dd;background:radial-gradient(70% 34% at 50% 0, rgb(255 255 255 / .06), transparent 72%), @PAPER@ 0 0/180px 180px, linear-gradient(176deg, #2e2f35, #1c1d21);box-shadow:0 14px 30px rgb(0 0 0 / .5), inset 0 0 0 1px rgb(201 162 108 / .32), inset 0 0 0 5px rgb(0 0 0 / .18), inset 0 0 44px rgb(0 0 0 / .42)}
@RB@ .sz-daily::before{top:9px;width:9px;height:9px;margin-left:-4.5px;border-radius:0;transform:rotate(45deg);background:#c9a26c;box-shadow:0 0 8px rgb(242 203 142 / .5)}
@RB@ .d-t{margin-top:8px;letter-spacing:.3em;text-indent:.3em;color:#f2cb8e!important;border-bottom:1px solid rgb(201 162 108 / .4)}
@RB@ .sz-stamp{transform:none;padding:0;border:0;border-radius:0;font-weight:600;letter-spacing:.08em;color:#c9a26c;mix-blend-mode:normal}
/* 号墙：行会门口一面灰石墙，活一张一张拿山铜钉钉上去，纸角写着要对上什么和给多少 */
@RB@ .sz-slips{padding:16px 14px 18px;border-radius:4px;background:repeating-linear-gradient(0deg, rgb(0 0 0 / .24) 0 1px, transparent 1px 44px), repeating-linear-gradient(90deg, rgb(0 0 0 / .14) 0 1px, transparent 1px 98px), linear-gradient(170deg, #4a4b52, #2f3036);box-shadow:inset 0 0 0 1px rgb(255 255 255 / .08), inset 0 10px 18px rgb(0 0 0 / .32)}
@RB@ .sz-slip{padding:20px 13px 11px;border-radius:2px;color:#2a2013;background:@PAPER@ 0 0/180px 180px, linear-gradient(175deg, #e6e0d0, #cec5ae);box-shadow:0 6px 12px rgb(0 0 0 / .46);transform:rotate(-.6deg)}
@RB@ .sz-slip:nth-child(even){transform:rotate(.7deg)}
@RB@ .sz-slip::before{background:radial-gradient(circle at 35% 30%, #efcf9a, #a97d45 60%, #5c4122);box-shadow:0 1px 2px rgb(0 0 0 / .6)}
@RB@ .sz-slip b{color:#2a2013!important}
@RB@ .sz-slip i{color:#f6ecd8;background:#3a3b42}
@RB@ .sz-slip em{color:#6d5128}
/* 团和碑：团名一格，档次一枚小牌，碑背面刻过几块 */
@R@ .sz-troop[data-s="无"]{display:inline-flex}
@R@ .sz-troop u{padding:0 8px;border-radius:3px;text-decoration:none;font-size:11px;line-height:19px;color:#1b1c20;background:var(--fm-acc)}
@R@ .sz-troop u:empty{display:none}
@R@ .sz-troop em{padding:0 8px;border-radius:9px;line-height:20px;color:var(--fm-acc2);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc2) 40%, transparent)}
/* 手机上这几纪的页头字多，收一点，返回钮不折行 */
@media (max-width:639px){@RS@ .sz-pane-head>b,@RM@ .sz-pane-head>b,@RB@ .sz-pane-head>b{font-size:17px;letter-spacing:.05em}}
/* 战报那一格：写过几回，像册子边上的一道批注 */
@R@ .sz-disp em{padding:0 8px;border-radius:9px;line-height:20px;color:var(--fm-acc2);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc2) 40%, transparent)}
/* 蓄势还没有的时候，EXP 底下一行小字 */
@R@ .sz-lvn{display:block;margin-top:5px;font-size:11.5px;letter-spacing:.06em;color:var(--fm-ink2)}
/* 角色签写「无」的不出 */
@R@ .sz-npc-tags span:is([data-v="无"],[data-v="暂无"],[data-v=" 无"],[data-v="无 "]){display:none}
/* ---- 地图：--z 倍数，--fx --fy 对准哪儿（0 到 1），--hx --hy 玩家在哪。没点过就对准玩家；地名没认出来就看全图、不插旗 ---- */
@R@ .sz-map{--z:var(--z0, 1);--fx:var(--hx, .5);--fy:var(--hy, .5);display:flex;flex-direction:column;gap:10px}
@R@ .sz-map:has(.mz-1 input:checked){--z:1}
@R@ .sz-map:has(.mz-2 input:checked){--z:2}
@R@ .sz-map:has(.mz-3 input:checked){--z:3.4}
@R@ .mwhere{display:flex;align-items:baseline;gap:8px;min-width:0;font-size:14px;color:var(--fm-ink)}
@R@ .mwhere small{flex:none;font-size:11.5px;letter-spacing:.1em;color:var(--fm-acc)}
@R@ .mwhere b{font-weight:600}
@R@ .mv{position:relative;aspect-ratio:8000/5091;overflow:hidden;border-radius:10px;background:radial-gradient(ellipse at 50% 50%, #17204a, #0b1024 70%);box-shadow:inset 0 0 0 1px var(--fm-line), 0 8px 22px rgb(0 0 0 / .35)}
@R@ .mi{position:absolute;inset:0;transform-origin:0 0;transform:translate(clamp(calc((1 - var(--z)) * 100%), calc(50% - var(--z) * var(--fx) * 100%), 0%), clamp(calc((1 - var(--z)) * 100%), calc(50% - var(--z) * var(--fy) * 100%), 0%)) scale(var(--z));transition:transform .55s cubic-bezier(.22,.7,.2,1)}
@R@ .mi::before{content:"";position:absolute;inset:0;background:var(--map-img) center/100% 100% no-repeat;filter:saturate(.94) brightness(.97);pointer-events:none}
@R@ .mg{position:absolute;inset:0;display:grid;grid-template-columns:repeat(10,1fr);grid-template-rows:repeat(6,1fr)}
@R@ .mg label{display:block;cursor:crosshair}
@R@ .mg input,@R@ .m input,@R@ .mzb input{display:none}
@R@ .m{position:absolute;left:var(--x);top:var(--y);z-index:2;display:block;width:22px;height:22px;margin:-11px 0 0 -11px;cursor:pointer;transform:scale(calc(1 / var(--z)));transition:transform .55s cubic-bezier(.22,.7,.2,1)}
@R@ .m::before{content:"";position:absolute;left:50%;top:50%;width:calc(11px - min(var(--t), 1.5) * 2.5px);aspect-ratio:1;border-radius:50%;background:var(--c);transform:translate(-50%,-50%);box-shadow:0 0 0 1.5px rgb(11 16 36 / .78), 0 0 8px 2px color-mix(in srgb, var(--c) 55%, transparent);transition:box-shadow .2s}
@R@ .m::after{content:attr(data-l);position:absolute;left:50%;top:calc(100% - 2px);padding:1px 5px;border-radius:3px;white-space:nowrap;font-size:11px;line-height:1.35;letter-spacing:.02em;color:#f4f1fa;background:rgb(8 12 30 / .8);box-shadow:inset 0 0 0 1px rgb(42 53 102 / .9);transform:translateX(-50%);opacity:clamp(0, calc((var(--z) - var(--t) * var(--tq, 1)) * 100 + 1), 1);pointer-events:none;transition:opacity .25s}
@R@ .m:hover{z-index:5}
@R@ .m:hover::after{opacity:1}
@R@ .m:has(input:checked){z-index:7}
@R@ .m:has(input:checked)::before{box-shadow:0 0 0 2.5px var(--fm-acc2), 0 0 16px 5px color-mix(in srgb, var(--fm-acc2) 60%, transparent)}
@R@ .m:has(input:checked)::after{opacity:1;color:#fff;box-shadow:inset 0 0 0 1px var(--fm-acc)}
@R@ .mhere{position:absolute;left:calc(var(--hx, .5) * 100%);top:calc(var(--hy, .5) * 100%);z-index:6;display:var(--hd, none);width:0;height:0;pointer-events:none;transform:scale(calc(1 / var(--z)));transition:transform .55s cubic-bezier(.22,.7,.2,1)}
@R@ .mhere::before{content:"";position:absolute;left:-15px;top:-15px;width:30px;height:30px;border-radius:50%;box-shadow:0 0 0 2px #fff3c8, 0 0 14px 4px rgb(255 226 150 / .85);animation:sz-mhere 1.9s ease-out infinite}
@R@ .mhere::after{content:"";position:absolute;left:-6px;top:-6px;width:12px;height:12px;background:#ffe9a8;transform:rotate(45deg);box-shadow:0 0 0 2px #7a5a1c, 0 0 10px 3px rgb(255 226 150 / .9)}
@R@ .mhere b{position:absolute;left:0;top:-36px;padding:2px 7px;border-radius:3px;white-space:nowrap;font-size:11.5px;font-weight:600;line-height:1.4;color:#2a1c05;background:#ffe9a8;transform:translateX(-50%);box-shadow:0 2px 6px rgb(0 0 0 / .5)}
@keyframes sz-mhere{0%{opacity:.95;transform:scale(.55)}70%{opacity:0;transform:scale(1.35)}100%{opacity:0;transform:scale(1.35)}}
@media (prefers-reduced-motion:reduce){@R@ .mhere::before{animation:none}@R@ :is(.mi,.m,.mhere){transition:none}}
@R@ .mz{position:absolute;right:8px;top:8px;z-index:9;display:flex;flex-direction:column;gap:5px}
@R@ .mzb{display:block;min-width:40px;padding:3px 7px;border-radius:7px;text-align:center;cursor:pointer;font-size:12px;line-height:1.5;color:var(--fm-ink);background:rgb(8 12 30 / .82);box-shadow:inset 0 0 0 1px var(--fm-line)}
@R@ .mzb b{font-weight:500}
@R@ .mzb:hover{color:var(--fm-acc2);box-shadow:inset 0 0 0 1px var(--fm-acc)}
@R@ .mzb:has(input:checked){color:#241a07;background:var(--fm-acc2)}
@R@ .mme{display:var(--hd, none)}
@R@ .ml{display:flex;flex-wrap:wrap;gap:3px 12px;font-size:11px;color:var(--fm-ink2)}
@R@ .ml span{display:inline-flex;align-items:center;gap:5px}
@R@ .ml i{width:7px;height:7px;border-radius:50%;background:var(--c)}
@R@ .mc{display:flex;gap:14px;min-height:96px;padding:12px 14px;border-radius:10px;background:var(--fm-panel);box-shadow:inset 0 0 0 1px var(--fm-line)}
@R@ .mc-a{flex:none;display:var(--ad, none);width:152px;align-self:stretch;min-height:96px;border-radius:7px;background:var(--art, none) center/cover no-repeat, rgb(0 0 0 / .25)}
@R@ .mc-t{min-width:0;display:block}
@R@ .mc-n{display:block;font-family:var(--fm-serif);font-size:16px!important;font-weight:600;color:var(--fm-head)}
@R@ .mc-n::before{content:var(--n, "点地图上的点，看那里的风土")}
@R@ .mc-r{display:block;margin-top:2px;font-size:11.5px;color:var(--fm-ink2)}
@R@ .mc-r::before{content:var(--r, "点别的地方，地图就移到那里。缩放在右上角")}
@R@ .mc-lv{display:block;margin-top:2px;font-style:normal;font-size:11.5px;color:var(--fm-acc)}
@R@ .mc-lv::before{content:var(--lv, "")}
@R@ .mc-d{display:block;margin-top:6px;font-size:13px;line-height:1.7;color:var(--fm-ink)}
@R@ .mc-d::before{content:var(--d, "")}
@media (max-width:639px){@R@ .sz-map{--tq:1.6}@R@ .mc{flex-direction:column}@R@ .mc-a{width:100%;height:140px}@R@ .m::after{font-size:10.5px}@R@ .mz{right:6px;top:6px;flex-direction:row;gap:4px}@R@ .mzb{min-width:0;padding:2px 7px;font-size:11.5px}}
/* 迷宫里的层级：所在、第几层、离安全层多远、好不好撤，跟命路一个样子 */
@R@ .sz-road.sz-floor{grid-row:8;grid-template-columns:repeat(4,minmax(0,1fr))}
@media (max-width:639px){@R@ .sz-road.sz-floor{grid-column:1;grid-row:10;grid-template-columns:repeat(2,minmax(0,1fr))}}
/* 不是施法者没有 MAG，三个数排一行 */
@R@ .p-panel .sz-atks:not(:has([data-a="mag"])){grid-template-columns:repeat(3,minmax(0,1fr))}
/* 功能命令轮（存档、差评、校准）：一道小题，底下照 Markdown 排。它不带 sz-hud，上一条回复的页签和整页都不动 */
.sz-fnh{display:flex;align-items:center;gap:8px;margin:0 0 10px;padding:0 0 6px;font-size:13px;letter-spacing:.12em;color:var(--fm-acc, inherit);border-bottom:1px solid var(--fm-line, rgb(128 128 128 / .3))}
.sz-fnh i{width:7px;height:7px;transform:rotate(45deg);background:currentColor}
@SH@:has(.sz-hud) .is-assistant:has(.sz-fnh),@SH@:has(.sz-hud) .is-assistant:has(.sz-fnh) div:has(.rili-markdown-renderer){background:transparent!important;border-color:transparent!important;box-shadow:none!important;width:100%!important;max-width:100%!important;padding-left:0!important;padding-right:0!important;margin-left:0!important;margin-right:0!important}
@SH@:has(.sz-hud) .rili-markdown-renderer:has(.sz-fnh){color:var(--fm-ink);font-size:15px;line-height:1.8;width:min(100%, 640px);margin-inline:auto}
@SH@:has(.sz-hud) .rili-markdown-renderer:has(.sz-fnh) pre{white-space:pre-wrap;word-break:break-word;max-height:60dvh;overflow:auto;padding:12px 14px;border-radius:8px;background:rgb(0 0 0 / .28);box-shadow:inset 0 0 0 1px var(--fm-line)}
@SH@:has(.sz-hud) .rili-markdown-renderer:has(.sz-fnh) :is(pre,code){color:var(--fm-ink);background-color:transparent}
'''


def build():
    s = MODULES
    for a, b in [('@TABLES@', tables()), ('@RING@', ring()), ('@HEXGRID@', hexgrid()), ('@RADAR@', radar_clip()), ('@HEX@', HEX),
                 ('@HEART@', _svg("<path d='M16 28C8 21 3 16 3 10.500A7 7 0 0 1 16 7a7 7 0 0 1 13 3.500C29 16 24 21 16 28z'/>")),
                 ('@PAPER@', 'url("data:image/svg+xml,%s")' % quote("<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.75' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .35 0 0 0 0 .22 0 0 0 0 .08 0 0 0 .13 0'/></filter><rect width='100%' height='100%' filter='url(#n)'/></svg>", safe="/:=' -.,()")),
                 ('@LYRE@', _svg("<g fill='none' stroke='#5b3a1e' stroke-width='1.8' stroke-linecap='round'><path d='M9 28h14M10 28C6 20 5 12 8 5c1-2 3-2 4 0M22 28c4-8 5-16 2-23c-1-2-3-2-4 0'/><path d='M7 9h18' stroke-width='2.4'/><path d='M13 9v19M16 9v19M19 9v19' stroke-width='1'/></g>")),
                 ('@THREAD@', _svg("<path d='M4 0C8 6 0 7 4 13C8 19 0 20 4 26' fill='none' stroke='#d8452f' stroke-width='1.4' stroke-linecap='round'/>", '0 0 8 26'))]:
        s = s.replace(a, b)
    return s
