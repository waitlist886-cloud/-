# 背包格子（11-23，状态栏第三轮）。用户：“卡中已有的道具装备遗物神器啥的都有一个自己的图标……更加的‘游戏化’的感觉”，
# 格子的样子照用户给的原神背包截图学排法：品阶的渐变底、物件居中、底下一条写数量、角上的小记号、选中时的亮边。
#
# 做法：
# - 记录行不改（§物品、§背包、§装备 照旧）。规则只添一条「背包格·类型」，把 §物品 那一行的类型抄进格子的 data-t，名字认不出的照类型挑图标。
# - 图标三层：通用一张 bagi.webp（12 列 18 行，上六行是旧的 72 格、行列没动，下十二行是 11-23 的 144 格），
#   专属器物一纪一张 bagr_<纪>.webp（129 件，照名字认），原画一件一张 ra_<键>.webp（只在小卡显出来的时候才取）。
#   图是 第三轮/bag_bake.py 烘的，排法两头都读这里的 relic_layout()。
# - 认图标的次序（后写的盖先写的）：类别兜底 → 类型兜底 → 名字里的字（材料、吃喝药、文书杂物、衣甲、兵器，一类里泛的在前细的在后）→ 回补 → 各纪的家当
#   → 备用的兵器衣甲照类型 → 专属器物。兵器照品阶挑寻常、精良、附魔三行，附魔那一行一件一种元素，名字里带了别的元素就退到精良那一行。
# - 品阶的样子都走变量（--q 颜色、--qp 几颗星、--sx 流光、--ux Unique 的光晕、--ubg Unique 的底），专属器物照清单上的品阶把这几样钉死，模型写错品阶也不走样。
import json
import os
import sys
from urllib.parse import quote

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
R = '.rili-markdown-renderer:has(.sz-hud)'
SH = ':root:has(#conversation)'

# ---------------- 规则 ----------------
# 接在「物品·带数」「物品」两条后头哪里都行（整页拼完以后也行）：认的是它们展开出来的那一格，从格子开头到小卡里那一行小字都在同一行、中间没有 §
RULES = [
    ('背包格·类型', r'/(<span class="sz-it sz-cell" data-c="[^"<>]{0,8}" data-q="[^"<>]{0,8}" data-n="[^"<>]{1,24}")(>[^§\n]{0,700}?<span class="sz-tip-h"><i class="sz-ic"><\/i><b>[^<\n]{0,40}<\/b><small>[^<\n"]{0,8} · ([^<\n"]{1,40})<\/small>)/g',
     '$1 data-t="$3"$2'),
]


def rules():
    return [{"name": n, "regex": rx, "replaceString": rep, "enabled": True, "messageRole": "assistant", "applyMode": "front-end"} for n, rx, rep in RULES]


# ---------------- 专属器物 ----------------
ERAS = [('月银纪', 'm', 'bagr_moon.webp'), ('纷争纪', 's', 'bagr_strife.webp'), ('山铜纪', 'b', 'bagr_bronze.webp'), ('迷宫纪', 'z', 'bagr_maze.webp'), ('底卡', 'k', 'bagr_base.webp')]
TIERC = {'Epic': '#a06be0', 'Legend': '#e0a63c', 'Unique': '#e25a4e'}
# 小卡原画角上那一行小字里的形制。清单里名器那一批没写形制、弓那一批抽歪了，这里照原画一件一件定
FORM = {
    'r001': '剑', 'r002': '弓', 'r003': '骑枪', 'r004': '大剑', 'r005': '护符', 'r007': '剑', 'r008': '长弓', 'r009': '枪', 'r010': '大剑', 'r011': '竖琴',
    'r013': '剑', 'r014': '弓', 'r015': '长枪', 'r016': '大剑', 'r017': '口弦', 'r019': '剑', 'r020': '大剑', 'r021': '弓', 'r022': '镯', 'r023': '枪', 'r024': '骨笛',
    'r026': '剑', 'r027': '短剑', 'r028': '阔刀', 'r029': '剑', 'r030': '锤', 'r031': '剑', 'r032': '短剑', 'r033': '剑', 'r034': '剑', 'r035': '骨剑', 'r036': '长剑', 'r037': '银剑',
    'r038': '大剑', 'r039': '大剑', 'r040': '大剑', 'r041': '大剑', 'r042': '大剑', 'r043': '大剑', 'r044': '重剑', 'r045': '阔剑', 'r046': '大剑', 'r047': '长刃', 'r048': '大剑',
    'r049': '舞剑', 'r050': '巨剑', 'r051': '杖', 'r052': '矛', 'r053': '槊', 'r054': '长枪', 'r055': '长戟', 'r056': '长枪', 'r057': '投枪', 'r058': '短枪', 'r059': '铦',
    'r060': '长枪', 'r061': '银杖', 'r062': '长枪', 'r063': '典籍', 'r064': '杖', 'r065': '灯', 'r066': '匣', 'r067': '秤杖', 'r068': '书', 'r069': '杯', 'r070': '镜', 'r071': '冠',
    'r072': '抄本', 'r073': '歌谱', 'r074': '果', 'r075': '琴', 'r076': '铃', 'r077': '符', 'r078': '弓', 'r079': '弓', 'r080': '弓', 'r081': '弓', 'r082': '弓', 'r083': '弓',
    'r084': '弓', 'r085': '弓', 'r086': '弓', 'r087': '弓', 'r088': '弓', 'r089': '弓', 'r090': '机括弓', 'r091': '弓', 'r092': '弓', 'r093': '巨剑', 'r094': '巨枪',
    'r095': '饰品', 'r096': '饰品', 'r097': '饰品', 'r098': '饰品', 'r099': '长刀', 'r100': '灯', 'r101': '锅', 'r102': '靴', 'r103': '短刀', 'r104': '手套', 'r105': '斗篷',
    'r106': '裘', 'r107': '断剑', 'r108': '弓', 'r109': '牌串', 'r110': '缰', 'r111': '锅', 'r112': '贝饰', 'r113': '翼具', 'r114': '枪', 'r115': '铃', 'r116': '塔盾',
    'r117': '灯', 'r118': '裘', 'r119': '长绳', 'r120': '剑', 'r121': '咒语书', 'r122': '钟', 'r123': '铳', 'r124': '斗篷', 'r125': '灯', 'r126': '灯', 'r127': '镐',
    'r128': '锤', 'r129': '弓', 'r130': '枪', 'r131': '塔盾', 'r132': '斗篷', 'r133': '剑',
}
BASE_NAMED = {'r100', 'r101', 'r102', 'r103', 'r104', 'r105'}   # 底卡里“在世的名器”那六件，别的是遗物


def relics():
    out = []
    for f in ('A', 'B'):
        out += json.load(open(os.path.join(ROOT, '底稿', '图标', 'relics', f + '.json'), encoding='utf-8'))
    out.sort(key=lambda r: r['key'])
    return out


def relic_layout():
    """键 → (哪一张, 列, 行)。一纪一张，12 列，照键的次序排"""
    lay, n = {}, {}
    sid = {e[0]: e[1] for e in ERAS}
    for r in relics():
        s = sid[r['era']]
        i = n.get(s, 0)
        lay[r['key']] = (s, i % 12, i // 12)
        n[s] = i + 1
    return lay


def _sheets():
    cnt = {}
    for s, _, _ in relic_layout().values():
        cnt[s] = cnt.get(s, 0) + 1
    out = {}
    for _, s, fname in ERAS:
        rows = -(-cnt[s] // 12)
        assert rows >= 2, s   # 只有一行的话样式里要除以零
        out[s] = (fname, rows)
    return out


SHEETS = _sheets()

# ---------------- 通用图标：照名字里的字认 ----------------
G0 = 6   # 144 格在 bagi.webp 里从第几行起


def g(n):
    """清单.tsv 的格号 → (列, 行)"""
    return ((n - 1) % 12, G0 + (n - 1) // 12)


FIRE, WATER, THUNDER, ICE, WIND, EARTH, DARK, HOLY = ['火', '炎', '焰', '熔', '赤'], ['水', '潮', '海'], ['雷', '电'], ['冰', '霜', '雪'], ['风', '岚', '翠', '青'], ['地', '岩', '土'], ['暗', '影', '渊', '黑'], ['圣', '光', '辉', '白']
# (格子, 名字里的字[, 还要带其中一个字])。后写的盖先写的
NAMES = [
    # ---- 材料 ----
    ((7, 3), ['牙', '骨', '爪', '角']), ((0, 3), ['矿', '石']), ((1, 3), ['锭', '钢块']), ((2, 3), ['晶', '魔石']), ((3, 3), ['木', '柴']),
    ((4, 3), ['皮毛', '兽皮', '毛皮', '皮料', '狼皮']), ((5, 3), ['线', '绳', '布料']), ((6, 3), ['瓶']), ((8, 3), ['鳞']), ((9, 3), ['羽']), ((10, 3), ['菇']),
    (g(84), ['爪']), (g(75), ['兽骨', '大骨', '腿骨', '骨头']), (g(76), ['头骨', '颅骨', '骷髅']), (g(77), ['甲壳', '背甲', '硬壳']), (g(78), ['凝胶', '黏液', '史莱姆']),
    (g(79), ['白毛皮', '霜皮', '雪皮', '霜狼']), (g(80), ['鳞皮', '蜥皮', '蛇皮']), (g(81), ['翼膜', '翅膜', '蝠翼', '翅']), (g(82), ['蛛丝', '茧', '丝线']),
    (g(46), ['魔眼', '眼珠', '之眼']), (g(47), ['心脏', '兽心', '龙心']),
    (g(45), ['核']), (g(37), ['核'], FIRE), (g(38), ['核'], WATER), (g(39), ['核'], THUNDER), (g(40), ['核'], ICE), (g(41), ['核'], WIND), (g(42), ['核'], EARTH), (g(43), ['核'], DARK), (g(44), ['核'], HOLY),
    (g(49), ['晶'], FIRE), (g(50), ['潮晶', '海晶', '水之晶', '水晶石']), (g(51), ['晶'], THUNDER), (g(52), ['晶'], ICE), (g(53), ['晶'], WIND), (g(54), ['晶'], EARTH), (g(54), ['琥珀']),
    (g(55), ['晶'], DARK), (g(55), ['黑曜']), (g(56), ['晶'], ['圣', '辉']), (g(58), ['魔晶', '炉心']), (g(57), ['以太']), (g(96), ['原石', '宝石', '红玉', '翠玉']),
    (g(61), ['鳞'], ['火', '炎', '赤']), (g(62), ['鳞'], ['冰', '霜', '白']), (g(63), ['鳞'], ['黑', '暗', '影']), (g(64), ['鳍', '水鳞', '鱼鳞', '海鳞']),
    (g(65), ['羽'], THUNDER), (g(66), ['羽'], ['风', '翠', '青']), (g(67), ['羽'], ['炎', '火', '赤', '凤']), (g(68), ['羽'], ['黑', '鸦', '暗']),
    (g(69), ['牙'], ['霜', '冰']), (g(71), ['角'], THUNDER), (g(72), ['角'], ['炎', '火', '熔']), (g(73), ['角'], ['魔', '暗', '黑']), (g(74), ['角'], ['独', '圣', '白']),
    (g(59), ['龙骨', '龙椎', '龙牙']),
    (g(90), ['铁锭', '铁块', '生铁']), (g(91), ['铜锭', '铜块']), (g(92), ['银锭', '银块']), (g(93), ['金锭', '金条']), (g(94), ['山铜']), (g(95), ['真银', '秘银', '月银']),
    (g(85), ['铜矿', '铜砂']), (g(86), ['银矿', '银砂']), (g(87), ['金矿', '金砂', '砂金', '金块']), (g(88), ['山铜矿', '山铜原石']), (g(89), ['真银矿', '秘银矿', '月银矿']),
    # ---- 吃喝药 ----
    ((1, 2), ['肉']), ((0, 2), ['饼', '面包', '粮']), ((2, 2), ['水囊', '皮囊', '水壶', '水袋']), ((6, 2), ['草', '叶', '花']), ((11, 2), ['果']),
    ((3, 2), ['药', '剂']), ((4, 2), ['魔力', '法力']), ((5, 2), ['解毒', '毒']), ((6, 2), ['药草', '草药', '止血草']),
    ((7, 2), ['绷带']), ((8, 2), ['火把']), ((9, 2), ['灯', '烛']), ((10, 2), ['酒']),
    (g(97), ['大瓶', '高级治疗', '强效治疗', '生命药']), (g(98), ['高级魔力', '强效魔力', '以太药', '大瓶魔力', '魔力药剂']), (g(99), ['耐力', '体力药', '活力']), (g(100), ['灵药', '万能药', '秘药']),
    (g(101), ['圣水', '净水']), (g(102), ['药膏', '软膏', '油膏', '药罐']), (g(103), ['口粮', '干粮', '硬饼', '饼干']), (g(104), ['烤肉', '熟肉', '肉排', '烤鸡', '烤鱼', '熟食']),
    (g(105), ['汤', '炖菜', '粥']), (g(106), ['麦酒', '啤酒', '蜜酒', '酒杯']), (g(107), ['茶', '咖啡']), (g(108), ['甜点', '蛋糕', '点心', '糖']),
    # ---- 文书、钥匙、箱子、杂物 ----
    ((5, 4), ['钱', '币']), ((3, 4), ['图']), ((1, 4), ['信', '凭条', '文书', '契', '委托', '纸']), ((0, 4), ['卷']), ((2, 4), ['书', '册', '手册', '笔记']), ((4, 4), ['钥']),
    ((7, 4), ['撬', '开锁']), ((8, 4), ['牌', '身份']), ((9, 4), ['匣', '箱', '盒']), ((11, 4), ['遗物', '残片', '碑']),
    (g(109), ['法术书', '魔导书', '咒语书', '术式书', '法书']), (g(110), ['日记', '手记', '札记']), (g(111), ['乐谱', '曲谱', '歌谱', '诗稿']), (g(112), ['海图', '藏宝图', '路线图', '迷宫图']),
    (g(113), ['契约', '合约', '盟约', '誓约']), (g(114), ['告示', '布告', '通缉', '悬赏']), (g(115), ['残页', '碎页', '残卷', '断章']), (g(116), ['画像', '肖像', '小像']),
    (g(117), ['图纸', '蓝图', '设计图']), (g(118), ['圣典', '祷书', '经文']), (g(119), ['密函', '密信', '密令']), (g(120), ['账本', '名册', '账册']), (g(144), ['委托单', '委托书', '任务单', '悬赏单']),
    (g(127), ['钥匙串']), (g(130), ['纸牌', '牌组', '塔罗']), (g(131), ['信物', '挂坠盒']), (g(129), ['骰']), (g(128), ['香炉', '熏香', '香料']), (g(125), ['工具', '钳', '锯', '凿']),
    (g(126), ['针线', '线轴', '缝衣针']), (g(132), ['发条', '齿轮', '游丝', '零件']), (g(123), ['琴']), (g(124), ['笛', '箫', '号角']), (g(60), ['神骸', '神骨']),
    # ---- 衣甲饰物 ----
    ((11, 1), ['衣', '裤', '衫', '内衬']), ((10, 1), ['徽', '章', '扣', '印']), ((9, 1), ['链', '坠', '护符', '怀表', '颈']), ((8, 1), ['戒']), ((7, 1), ['腰带', '束腰']),
    ((6, 1), ['斗篷', '披风', '外套']), ((5, 1), ['靴', '鞋']), ((4, 1), ['手套', '护手']), ((3, 1), ['盔', '帽', '冠']), ((2, 1), ['袍', '法衣', '制服']), ((0, 1), ['甲', '铠']),
    ((1, 1), ['皮甲', '硬皮', '皮护']), (g(121), ['耳坠', '耳环', '耳饰']), (g(122), ['手镯', '臂环', '手环']), (g(142), ['公会徽章', '冒险者徽章']), ((11, 1), ['袜']),
]
# 兵器十二种形制，列就是 144 格头三行的列；行照品阶（--w）走，附魔那一行的元素（ELEM 里第几种，0 是不挑）跟名字里的元素对不上就退一行
WEAPONS = [(0, ['剑'], 1), (1, ['刀'], 2), (4, ['枪', '矛', '戟', '槊'], 5), (5, ['斧'], 1), (6, ['锤', '槌'], 6), (7, ['弓'], 7), (8, ['弩'], 0), (9, ['杖'], 0), (10, ['盾'], 0),
           (2, ['短剑', '匕', '短刃', '短刀'], 3), (3, ['大剑', '巨剑', '双手剑', '重剑', '阔剑'], 4), (11, ['铳', '火枪'], 0)]
ELEM = [['炎', '火', '焰', '熔', '烬'], ['霜', '冰', '雪', '寒'], ['影', '暗', '渊', '夜'], ['圣', '光', '辉'], ['雷', '电'], ['岩', '地', '石'], ['风', '岚']]
# 兵器以后：旧表里盖在兵器上头的几样，跨了类、叫前头的单字盖错的细目，各纪的家当
LATE = [
    ((6, 4), ['小刀', '折叠刀']), ((3, 0), ['镰']), ((7, 2), ['绷带']), ((11, 3), ['磨刀']), (g(109), ['法书', '魔导书', '咒语书']), ((7, 3), ['碎骨', '骨片', '黑牙', '獠牙']), ((10, 1), ['旅印', '银印', '铜印', '金印']),
    (g(77), ['甲壳', '背甲']), (g(115), ['断章']), (g(70), ['毒牙', '蛇牙']), (g(83), ['毒囊', '毒腺']), (g(48), ['魔血', '兽血', '龙血', '血瓶']), (g(139), ['铳弹', '弹药', '弹匣']),
    (g(125), ['锤子', '匠具']), (g(60), ['神骸']),
    # 月银纪
    (g(133), ['曜核']), ((0, 3), ['盐砖']), (g(134), ['月银罐', '封核罐']), ((3, 3), ['仓签']), ((11, 4), ['金痂']), (g(135), ['王牙', '兽王之牙']),
    # 纷争纪
    (g(136), ['晶匣']), (g(137), ['上弦钥匙', '上弦', '发条钥匙']), (g(138), ['令哨', '军哨', '铜铃']), ((7, 3), ['肋骨']), ((1, 4), ['名字']),
    # 山铜纪
    (g(141), ['铆钉', '山铜碎块', '山铜片']), ((1, 4), ['揭下来的活', '的约', '熏鱼的凭条']), ((5, 3), ['旗角']), ((0, 3), ['盐']), (g(140), ['机兵', '指节', '魔导零件']), ((1, 0), ['烙铁']),
    # 迷宫纪
    (g(143), ['层带', '迷宫苔', '井壁']), (g(144), ['委托单']),
]
# 名字认不出的：先照 §物品 的类别（data-c），再照类型（data-t）
BY_CAT = [((3, 2), '消耗'), ((0, 3), '材料'), ((9, 4), '贵重'), ((11, 4), '不可丢弃')]
BY_TYPE = [
    (g(45), ['素材']), ((0, 3), ['矿']), (g(90), ['金属', '锭']), (g(58), ['晶']), ((4, 3), ['皮']), ((6, 3), ['容器']),
    ((3, 2), ['药', '剂']), ((7, 2), ['急救']), (g(103), ['口粮', '食', '粮']), ((10, 2), ['酒', '饮']), ((9, 2), ['照明']),
    ((1, 4), ['文书', '信', '凭']), ((2, 4), ['书', '典籍']), ((0, 4), ['卷轴']), ((3, 4), ['地图']), ((4, 4), ['钥匙']), ((5, 4), ['钱', '货币']), ((9, 4), ['箱', '匣']),
    (g(125), ['工具']), (g(123), ['乐器']), ((8, 1), ['首饰', '饰品']), ((10, 1), ['旅印', '徽']), ((11, 4), ['证物', '遗物']),
]
# 备用的兵器衣甲（类别是未装备）：类型说它是什么就是什么，名字起得再花也认得出
TYPE_GEAR = [((11, 1), ['衣', '裤', '衫']), ((0, 1), ['甲', '铠']), ((1, 1), ['皮甲']), ((2, 1), ['袍']), ((3, 1), ['盔', '帽', '冠']), ((4, 1), ['手套', '护手']), ((5, 1), ['靴', '鞋']),
             ((6, 1), ['斗篷', '披风']), ((7, 1), ['腰带']), ((8, 1), ['戒']), ((9, 1), ['项链', '护符', '坠'])]
# 品阶：颜色（--q）在 modules_css 的 QUAL 里，这里照同一组字给星数、兵器的行、底下那一条没有数量时写的字、流光
TIERS = [(['粗糙', '破损', '低劣'], '--qp:1;--ql:"粗糙"'), (['优', '精良', 'Uncommon'], '--qp:2;--w:1;--ql:"精良"'), (['稀有', 'Rare'], '--qp:3;--w:1;--ql:"Rare"'),
         (['史诗', 'Epic', '名器'], '--qp:4;--w:2;--ql:"Epic"'), (['传说', '传奇', 'Legend'], '--qp:5;--w:2;--ql:"Legend";--sx:""'), (['神话', '神器', '遗物', 'Unique'], None)]


def _svg(body, vb='0 0 32 32'):
    s = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='%s'>%s</svg>" % (vb, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' -.,()")


# 一纪一种底纹（格子和小卡的底上淡淡一层）：迷宫纪四芒星，月银纪铭环和点，纷争纪斜线和铆钉，山铜纪碑的刻框
PAT = {
    'maze': _svg("<g fill='#fff' fill-opacity='.13'><path d='M17 4l1.6 6.4L25 12l-6.4 1.6L17 20l-1.6-6.4L9 12l6.4-1.6z'/><circle cx='0' cy='29' r='1.2'/><circle cx='34' cy='29' r='1.2'/>"
                 "<path d='M0 0l.8 3 3 .8-3 .8-.8 3-.8-3-3-.8 3-.8zM34 0l.8 3 3 .8-3 .8-.8 3-.8-3-3-.8 3-.8z' fill-opacity='.08'/></g>", '0 0 34 34'),
    'moon': _svg("<g fill='none' stroke='#fff' stroke-opacity='.14'><circle cx='17' cy='17' r='10.5' stroke-width='.9'/><circle cx='17' cy='17' r='6' stroke-width='.6' stroke-dasharray='1.4 2.4'/></g>"
                 "<g fill='#fff' fill-opacity='.2'><circle cx='17' cy='6.5' r='1.1'/><circle cx='0' cy='0' r='1.2'/><circle cx='34' cy='0' r='1.2'/><circle cx='0' cy='34' r='1.2'/><circle cx='34' cy='34' r='1.2'/></g>", '0 0 34 34'),
    'strife': _svg("<g stroke='#fff' stroke-opacity='.1' stroke-width='1.2'><path d='M-4 12L12 -4M-4 30L30 -4M4 38L38 4M22 38L38 22'/></g><g fill='#fff' fill-opacity='.2'><circle cx='17' cy='17' r='1.5'/>"
                   "<circle cx='0' cy='0' r='1.5'/><circle cx='34' cy='0' r='1.5'/><circle cx='0' cy='34' r='1.5'/><circle cx='34' cy='34' r='1.5'/></g>", '0 0 34 34'),
    'bronze': _svg("<g fill='none' stroke='#fff' stroke-opacity='.13' stroke-width='.9'><path d='M5 5h24v24H5zM9 9h16v16H9z'/><path d='M17 12l5 5-5 5-5-5z' stroke-opacity='.18'/></g>"
                   "<g fill='#fff' fill-opacity='.2'><circle cx='5' cy='5' r='1'/><circle cx='29' cy='5' r='1'/><circle cx='5' cy='29' r='1'/><circle cx='29' cy='29' r='1'/></g>", '0 0 34 34'),
}
STAR = _svg("<path d='M8 .8l1.9 5.3 5.3 1.9-5.3 1.9L8 15.2 6.1 9.9.8 8l5.3-1.9z' fill='#ffc93a' stroke='#5a3608' stroke-width='1.3' stroke-linejoin='round'/><path d='M8 4.6l.9 2.5 2.5.9-2.5.9L8 11.4l-.9-2.5L4.6 8l2.5-.9z' fill='#fff3b8'/>", '0 0 16 16')
STAR_U = _svg("<path d='M8 .8l1.9 5.3 5.3 1.9-5.3 1.9L8 15.2 6.1 9.9.8 8l5.3-1.9z' fill='#fff1f0' stroke='#7a1024' stroke-width='1.1' stroke-linejoin='round'/><path d='M8 4.6l.9 2.5 2.5.9-2.5.9L8 11.4l-.9-2.5L4.6 8l2.5-.9z' fill='#ff8f7a'/>", '0 0 16 16')
# 角上的小记号：专属器物是一枚角花，绑定的东西是一把小锁
MARK_R = _svg("<path d='M1 1h19L1 20z' fill='#f6d27a' stroke='#4a3208' stroke-width='1.2' stroke-linejoin='round'/><path d='M3.4 3.4h10.2L3.4 13.6z' fill='#fff3c8' fill-opacity='.55'/>"
              "<path d='M7.2 3.6l1 2.6 2.6 1-2.6 1-1 2.6-1-2.6-2.6-1 2.6-1z' fill='#6a3d06'/>", '0 0 22 22')
MARK_L = _svg("<circle cx='9.5' cy='9.5' r='7.6' fill='#17142a' fill-opacity='.88' stroke='#efe6cf' stroke-opacity='.75' stroke-width='.9'/><path d='M7 8.8V7.4a2.5 2.5 0 015 0v1.4' fill='none' stroke='#efe6cf' stroke-width='1.3'/>"
              "<rect x='5.8' y='8.8' width='7.4' height='5.2' rx='1.1' fill='#efe6cf'/>", '0 0 22 22')
# 品阶的底：左上深、右下亮，顶上一片高光，中间一层这一纪的底纹
BGQ = ('radial-gradient(120% 78% at 50% 0%, rgb(255 255 255 / .34), transparent 64%), var(--bp) 50% 0/34px 34px, '
       'linear-gradient(165deg, color-mix(in srgb, var(--q) 50%, #15122c) 0%, color-mix(in srgb, var(--q) 94%, #fff) 100%)')
# Unique：不是这世上的东西。整格是夜色，正中一团从里往外的光，外头一圈会呼吸的虹
UBG = ('radial-gradient(62% 50% at 50% 42%, rgb(255 232 184 / .96) 0%, rgb(244 124 92 / .7) 34%, transparent 74%), var(--bp) 50% 0/34px 34px, '
       'linear-gradient(170deg, #2b0f2c, #71152f 52%, #170918)')
RINGS = 'repeating-radial-gradient(circle at 50% 46%, transparent 0 23px, rgb(255 255 255 / .055) 23px 24px)'
UTB = ('radial-gradient(60% 52% at 50% 46%, rgb(255 232 184 / .95) 0%, rgb(244 124 92 / .6) 36%, transparent 76%), ' + RINGS + ', '
       'linear-gradient(180deg, #2b0f2c, #5c1230 55%, #120713)')
# 这三样长，在外壳那一层写一回（--bag-ubg、--bag-utb、--bag-su），这里只引名字
UNIQUE = '--qp:5;--w:2;--ql:"Unique";--sx:"";--ux:"";--u:1;--ubg:var(--bag-ubg);--ust:#ffe9b8;--usb:linear-gradient(180deg, transparent, rgb(18 5 14 / .9) 55%);--utb:var(--bag-utb);--star:var(--bag-su)'
RESET = '--sx:initial;--ux:initial;--u:0;--ubg:initial;--ust:initial;--usb:initial;--utb:initial;--star:initial'   # 专属器物照清单的品阶来，记录里写成别的也不带过来


def _attr(a, words):
    return ','.join('[data-%s*="%s"]' % (a, k) for k in words)


def _sel(a, words, also=None, pre='.sz-it'):
    s = pre + ('[data-%s*="%s"]' % (a, words[0]) if len(words) == 1 else ':is(%s)' % _attr(a, words))
    if also:
        s += ':where(%s)' % _attr(a, also)
    return s


def _pos(xy):
    return '--ix:%d;--iy:%d' % xy


def _weapon(a, col, words, el, pre='.sz-it'):
    row = 'var(--w,0)' if not el else 'min(var(--w,0),2 - min(1,max(var(--e,0) - %d,%d - var(--e,0))) * min(1,var(--e,0)))' % (el, el)
    return '%s:where(:not([data-c="材料"])){--ix:%d;--iy:calc(%d + %s)}' % (_sel(a, words, pre=pre), col, G0, row)


def tables():
    o = []
    w = o.append
    for xy, c in BY_CAT:
        w('.sz-it[data-c="%s"]{%s}' % (c, _pos(xy)))
    w('.sz-it[data-c="不可丢弃"]{--cm:"";--cmi:var(--bag-ml)}')
    for xy, kws in BY_TYPE:
        w('%s{%s}' % (_sel('t', kws), _pos(xy)))
    for i, words in enumerate(ELEM):
        w('.sz-it:is(%s){--e:%d}' % (_attr('n', words), i + 1))
    for words, decl in TIERS:
        w('.sz-it:is(%s){%s}' % (_attr('q', words), decl or UNIQUE))
    w('.sz-it:is([data-n*="附魔"],[data-n*="符文"],[data-n*="魔导"]){--w:2}')
    for e in NAMES:
        w('%s{%s}' % (_sel('n', e[1], e[2] if len(e) > 2 else None), _pos(e[0])))
    for col, words, el in WEAPONS:
        w(_weapon('n', col, words, el))
    for e in LATE:
        w('%s{%s}' % (_sel('n', e[1]), _pos(e[0])))
    for xy, kws in TYPE_GEAR:
        w('.sz-it[data-c="未装备"]:where(%s){%s}' % (_attr('t', kws), _pos(xy)))
    for col, words, el in WEAPONS:
        row = 'var(--w,0)' if not el else 'min(var(--w,0),2 - min(1,max(var(--e,0) - %d,%d - var(--e,0))) * min(1,var(--e,0)))' % (el, el)
        w('.sz-it[data-c="未装备"]:where(%s){--ix:%d;--iy:calc(%d + %s)}' % (_attr('t', words), col, G0, row))
    # 专属器物：一组（纪、品阶）一条把图、颜色、星数、小卡上的字钉死，再一件一条给格子和原画
    lay = relic_layout()
    rs = relics()
    era_name = {e[1]: e[0] for e in ERAS}
    groups = {}
    for r in rs:
        s = lay[r['key']][0]
        lab = era_name[s] if s != 'k' else ('名器' if r['key'] in BASE_NAMED else '遗物')
        groups.setdefault((s, r['tier'], lab), []).append(r)
    for (s, tier, lab), items in groups.items():
        decl = '--isp:var(--bagr-%s);--iny:%d;--q:%s;--re:"%s · ";--rx:"";--rt:"%s";--ri:none;--rp:15px;--cm:"";--cmi:var(--bag-mr);' % (s, SHEETS[s][1] - 1, TIERC[tier], lab, tier)
        decl += {'Epic': RESET + ';--qp:4;--ql:"Epic"', 'Legend': RESET + ';--qp:5;--ql:"Legend";--sx:""', 'Unique': UNIQUE}[tier]
        w('.sz-it:is(%s){%s}' % (_attr('n', [r['name'] for r in items]), decl))
    for r in rs:
        _, x, y = lay[r['key']]
        w('.sz-it[data-n*="%s"]{--ix:%d;--iy:%d;--ra:url("__ART__/ra_%s.webp");--rk:"%s"}' % (r['name'], x, y, r['key'], FORM[r['key']]))
    return '\n'.join(o)


# 小卡显出来的那几种情形（跟 modules_css 里 .sz-tip 的 display:block 是同一组），原画的地址只挂在这上头，背包一打开不会把 129 张都取一遍
SHOWN = ['.sz-it:is(:hover,:focus-within,:has(>.sz-face input:checked)) .sz-tip-h::after', '.sz-gridit .sz-it:first-of-type .sz-tip-h::after']

CSS = r'''
/* ==== 背包格子（第三轮）：品阶的渐变底、图标居中、底下一条数量、角上的小记号；专属器物的小卡顶上是原画 ==== */
@SH@:has(.sz-hud){--sz-sprite:url("__ART__/bagi.webp");@SHEETVARS@;--bag-mr:@MARK_R@;--bag-ml:@MARK_L@}
@R@{--bp:@PAT_maze@;--bs:linear-gradient(180deg, #f5eede, #dfd5be);--br:7px;--bag-ubg:@UBG@;--bag-utb:@UTB@;--bag-su:@STAR_U@}
@R@:has(.era-moon){--bp:@PAT_moon@;--bs:linear-gradient(180deg, #f2f5fa, #d0d8e6);--br:10px}
@R@:has(.era-strife){--bp:@PAT_strife@;--bs:linear-gradient(180deg, #f2e4cd, #d5bd9c);--br:3px}
@R@:has(.era-bronze){--bp:@PAT_bronze@;--bs:linear-gradient(180deg, #f1ece2, #d2c8b4);--br:5px}
@TABLES@
@R@ .sz-ic{background-image:var(--isp, var(--sz-sprite));background-size:1200% calc((var(--iny, 17) + 1) * 100%);background-position:calc(var(--ix, 10) * 100% / 11) calc(var(--iy, 4) * 100% / var(--iny, 17))}
@R@ .sz-sealb i{background-size:1200% 1800%;background-position:calc(10 * 100% / 11) calc(1 * 100% / 17)}
/* ---------- 一格 ---------- */
@media (min-width:1100px){@R@ .sz-gridit{grid-template-columns:repeat(4,76px) minmax(0,1fr)}}
@R@ .sz-cell .sz-face{isolation:isolate;margin-bottom:10px;-webkit-tap-highlight-color:transparent}
@R@ .sz-pad{width:100%;height:auto;aspect-ratio:76 / 95;border-radius:var(--br);overflow:hidden;isolation:isolate;background:var(--bs);box-shadow:0 0 0 1px color-mix(in srgb, var(--q) 48%, #07060f), 0 5px 12px rgb(0 0 0 / .4)}
@R@ .sz-pad::before{content:"";position:absolute;z-index:-1;inset:0 0 calc(21px * (1 - var(--u, 0))) 0;border-radius:0 0 calc(19px * (1 - var(--u, 0))) 0;background:var(--ubg, @BGQ@);box-shadow:inset 0 1px 0 rgb(255 255 255 / .4), inset 0 -1px 0 rgb(0 0 0 / .18)}
@R@ .sz-pad .sz-ic{inset:3px auto auto calc(13.5px - 12.5%);width:calc(125% - 27px);height:auto;aspect-ratio:1;filter:drop-shadow(0 3px 3px rgb(0 0 0 / .42))}
@R@ :is(.sz-pad,.sz-sl>.sz-face,.sz-tip-h)>.sz-ic::after{content:"";position:absolute;left:50%;bottom:-8px;width:calc(var(--qp, 1) * 10px);height:11px;margin-left:calc(var(--qp, 1) * -5px);background:var(--star, @STAR@) 0 50%/10px 10px repeat-x;filter:drop-shadow(0 1px 1px rgb(0 0 0 / .55))}
@R@ .sz-pad .sz-ic::before{content:var(--cm);position:absolute;left:calc(12.5% - 13.5px);top:-3px;width:19px;height:19px;background:var(--cmi) 0 0/contain no-repeat}
@R@ .sz-ct{left:0;right:0;bottom:0;height:21px;padding-top:calc(4px * var(--u, 0));line-height:21px;text-align:center;font-size:12px;font-weight:800;font-variant-numeric:tabular-nums;letter-spacing:.02em;color:var(--ust, #2d2636);text-shadow:none;background:var(--usb, none)}
@R@ .sz-ct::before{font-size:10px;font-weight:600;margin-right:1px;opacity:.62}
@R@ .sz-cell .sz-face::before{content:var(--ql, "Normal");position:absolute;z-index:1;left:0;right:0;top:0;aspect-ratio:76 / 95;display:flex;align-items:flex-end;justify-content:center;padding-bottom:3px;font-family:var(--fm-serif);font-size:11px;font-weight:700;line-height:15px;letter-spacing:.06em;color:var(--ust, #3a3242);pointer-events:none}
@R@ .sz-cell .sz-face:has(.sz-ct)::before{content:none}
@R@ .sz-nm{margin-top:6px;color:color-mix(in srgb, var(--q) 26%, var(--fm-ink2))!important}
/* 流光：Legend 以上一道斜光隔一会儿扫过去 */
@R@ .sz-pad::after,@R@ .sz-sl .sz-face::after{content:var(--sx);position:absolute;top:-10%;bottom:-10%;left:0;width:46%;background:linear-gradient(100deg, transparent, rgb(255 255 255 / .62) 50%, transparent);transform:translateX(-140%) skewX(-18deg);animation:bag-sheen 4.6s ease-in-out infinite;pointer-events:none}
@R@ .sz-it:nth-child(3n+1) :is(.sz-pad,.sz-face)::after{animation-delay:-1.5s}
@R@ .sz-it:nth-child(3n+2) :is(.sz-pad,.sz-face)::after{animation-delay:-3.1s}
@keyframes bag-sheen{0%,58%{transform:translateX(-140%) skewX(-18deg)}100%{transform:translateX(360%) skewX(-18deg)}}
/* Unique：格子外头一圈虹，慢慢呼吸 */
@R@ .sz-cell .sz-face::after{content:var(--ux);position:absolute;z-index:-1;left:-5px;top:-5px;width:calc(100% + 10px);aspect-ratio:86 / 105;border-radius:11px;background:conic-gradient(from 210deg, #ff7a66, #ffd88a, #b78bff, #7fd6ff, #ff9ac2, #ff7a66);filter:blur(5px);opacity:.8;animation:bag-aura 3.2s ease-in-out infinite;pointer-events:none}
@keyframes bag-aura{0%,100%{opacity:.42;transform:scale(.97)}50%{opacity:.95;transform:scale(1.03)}}
/* 悬上去抬一下，选中的一圈亮边 */
@R@ .sz-it:hover .sz-pad{transform:translateY(-2px);box-shadow:0 0 0 1px color-mix(in srgb, var(--q) 60%, #fff), 0 0 16px color-mix(in srgb, var(--q) 70%, transparent), 0 8px 14px rgb(0 0 0 / .42)}
@R@ .sz-it:has(>.sz-face input:checked) .sz-pad{transform:translateY(-2px);box-shadow:0 0 0 1.5px #1b1730, 0 0 0 3.5px #fff6dc, 0 0 0 4.5px color-mix(in srgb, var(--q) 70%, #1b1730), 0 0 18px 3px color-mix(in srgb, var(--q) 80%, transparent)}
@R@ .sz-cell:hover .sz-face::before,@R@ .sz-cell:has(>.sz-face input:checked) .sz-face::before{transform:translateY(-2px)}
@R@ .sz-it:hover .sz-nm,@R@ .sz-it:has(>.sz-face input:checked) .sz-nm{color:var(--fm-ink)!important}
/* ---------- 身上的部位：同一种底，不带底下那一条 ---------- */
@R@ .sz-sl .sz-face{overflow:hidden;border-radius:calc(var(--br) + 3px);background:var(--ubg, @BGQ@);box-shadow:inset 0 1px 0 rgb(255 255 255 / .4), inset 0 0 0 1px rgb(255 255 255 / .12), 0 0 0 1px color-mix(in srgb, var(--q) 48%, #07060f), 0 5px 12px rgb(0 0 0 / .4)}
@R@ .sz-sl .sz-face .sz-ic{inset:3px 5px 7px;filter:drop-shadow(0 2px 3px rgb(0 0 0 / .45))}
@R@ .sz-sl>.sz-face>.sz-ic::after{bottom:-6px;height:9px;background-size:8px 8px;width:calc(var(--qp, 1) * 8px);margin-left:calc(var(--qp, 1) * -4px)}
@R@ .sz-cl .sz-ic::after,@R@ .sz-abs .sz-ic::after{content:none}
@R@ .sz-sl:hover .sz-face{box-shadow:inset 0 1px 0 rgb(255 255 255 / .4), 0 0 0 1px color-mix(in srgb, var(--q) 60%, #fff), 0 0 16px color-mix(in srgb, var(--q) 70%, transparent), 0 6px 14px rgb(0 0 0 / .45)}
@R@ .sz-sl:has(>.sz-face input:checked) .sz-face{box-shadow:inset 0 1px 0 rgb(255 255 255 / .4), 0 0 0 1.5px #1b1730, 0 0 0 3px #fff6dc, 0 0 16px 3px color-mix(in srgb, var(--q) 80%, transparent)}
@R@ .sz-gr>.sz-ic{background-color:color-mix(in srgb, var(--q) 46%, #14122c)}
/* ---------- 小卡：专属器物顶上一幅原画 ---------- */
@R@ .sz-tip-h{padding-right:var(--rp, 86px)}
@R@ .sz-tip-h .sz-ic{display:var(--ri, block)}
@R@ .sz-tip-h::before{content:var(--re) var(--rk, "");display:flex;align-items:flex-end;justify-content:flex-end;height:184px;margin:-13px -15px 12px;padding:0 12px 8px;font-family:var(--fm-serif);font-size:11.5px;letter-spacing:.16em;color:rgb(255 246 224 / .86);text-shadow:0 1px 3px #000;background:var(--utb, radial-gradient(64% 56% at 50% 46%, color-mix(in srgb, var(--q) 78%, #fff 6%) 0%, color-mix(in srgb, var(--q) 30%, transparent) 46%, transparent 76%), @RINGS@, linear-gradient(180deg, color-mix(in srgb, var(--q) 30%, #0b0a1c), #0b0a1c));box-shadow:inset 0 -1px 0 color-mix(in srgb, var(--q) 70%, transparent), inset 0 -22px 26px -18px rgb(0 0 0 / .7)}
@R@ .sz-tip-h::after{content:var(--rx);position:absolute;left:22px;right:22px;top:18px;height:142px;background:center/contain no-repeat;filter:drop-shadow(0 10px 12px rgb(0 0 0 / .62));animation:bag-float 5.2s ease-in-out infinite;pointer-events:none}
@SHOWN@{background-image:var(--ra)}
@keyframes bag-float{0%,100%{transform:translateY(3px)}50%{transform:translateY(-4px)}}
@R@ .sz-tip-in::before{content:var(--rt);position:absolute;z-index:2;left:10px;top:10px;padding:0 9px;border-radius:999px;font-family:var(--fm-serif);font-size:11px;font-weight:700;line-height:19px;letter-spacing:.14em;color:#17121f;background:linear-gradient(180deg, color-mix(in srgb, var(--q) 70%, #fff), var(--q));box-shadow:0 0 0 1px rgb(0 0 0 / .35), 0 0 12px color-mix(in srgb, var(--q) 70%, transparent)}
@R@ .sz-tip-in::after{content:var(--sx);position:absolute;z-index:2;top:0;left:0;width:34%;height:184px;background:linear-gradient(100deg, transparent, rgb(255 255 255 / .2) 50%, transparent);transform:translateX(-160%) skewX(-18deg);animation:bag-sheen2 6s ease-in-out infinite;pointer-events:none}
@keyframes bag-sheen2{0%,55%{transform:translateX(-160%) skewX(-18deg)}100%{transform:translateX(460%) skewX(-18deg)}}
@R@ .sz-abs .sz-tip-in::after,@R@ .sz-abs .sz-tip-in::before,@R@ .sz-abs .sz-tip-h::before,@R@ .sz-abs .sz-tip-h::after{content:none}
@media (max-width:1099px){
  @R@ .sz-tip-h{padding-right:var(--rp, 96px)}
  @R@ .sz-tip-h::before{height:200px}
  @R@ .sz-tip-h::after{height:164px}
  @R@ .sz-tip-in::after{height:200px}
  @R@ .sz-ct{font-size:11.5px}
}
@media (prefers-reduced-motion:reduce){@R@ :is(.sz-pad,.sz-face,.sz-tip-in,.sz-tip-h)::after{animation:none!important}}
'''


def css():
    rep = [('@TABLES@', tables()), ('@SHEETVARS@', ';'.join('--bagr-%s:url("__ART__/%s")' % (s, f) for s, (f, _) in SHEETS.items())),
           ('@MARK_R@', MARK_R), ('@MARK_L@', MARK_L), ('@STAR@', STAR), ('@STAR_U@', STAR_U), ('@BGQ@', BGQ), ('@UBG@', UBG), ('@UTB@', UTB), ('@RINGS@', RINGS),
           ('@SHOWN@', ','.join(R + ' ' + s for s in SHOWN))]
    out = CSS
    for k, v in rep:
        out = out.replace(k, v)
    for k in PAT:
        out = out.replace('@PAT_%s@' % k, PAT[k])
    out = out.replace('@SH@', SH).replace('@R@', R)
    assert '@' not in out.replace('@media', '').replace('@keyframes', ''), [m for m in out.split('@')[1:] if not m.startswith(('media', 'keyframes'))][:3]
    return out.strip() + '\n'


if __name__ == '__main__':
    json.dump(rules(), open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if len(sys.argv) > 2:
        open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(css())
    c = css()
    t = tables()
    print(len(RULES), '条规则', len(c), '字样式（其中认图标的表', len(t), '字，专属器物', sum(len(l) + 1 for l in t.split('\n') if 'ra_r' in l or '--isp' in l), '字）')
