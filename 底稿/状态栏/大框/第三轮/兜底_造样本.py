# 11-25 兜底那一轮的样本：判、家业、宠 三种记录各几条写歪的，写到 大框/样本_兜底_11-25.txt；
# 另出几份看检定面板主角那一边头像的（第三轮/样本_主角头像_*.txt）。底子是 第三轮/样本_四样同屏.txt 和 样本_检定演出.txt。
#   python -I -X utf8 底稿/状态栏/大框/第三轮/兜底_造样本.py
# 一轮至多两张 §判 是给模型的规矩，这里一条回复里放十二张是为了出图。每一行歪在哪写在那一行末一栏里。
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BT = '`'
F3 = BT * 3


def read(p):
    return io.open(p, encoding='utf-8').read().replace('\r', '')


def write(p, t):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
    print('ok', os.path.relpath(p, UP), len(t))


half = lambda s: s.replace('｜', '|')
L = read(os.path.join(HERE, '样本_四样同屏.txt')).split('\n')
J = [l for l in L if l.startswith('§判｜')]
E = [l for l in L if l.startswith('§家业｜')]
P = [l for l in L if l.startswith('§宠｜')]
assert len(J) == 4 and len(E) == 7 and len(P) == 2, (len(J), len(E), len(P))


def tail(line, text):
    """末一栏换成一句说明"""
    c = line.split('｜')
    return '｜'.join(c[:-1] + [text])


c0 = J[0].split('｜')      # §判、类·事、出手方、出手方几项、应对方、应对方几项、定档、骰、结果、后果
LOCK = '§判｜开锁·撬开营地的铁匣｜洛恩·维斯特 共鸣·凝华 LVL 38｜DEX 38、Skill 开锁·共鸣2阶↑、装备 一根弯了的铁签↓｜三簧铜锁 矮人的手艺，难｜无'
JUDGE = [
    # 一、竖线
    tail(J[0], '竖线全写成半角、两边带空格').replace('｜', ' | '),
    # 二、行首记号
    tail(J[1], '行首的记号漏了')[1:],
    '＃' + half(tail(J[2], '行首写成井号，竖线又是半角')[1:]),
    '【判】' + tail(J[3], '名目写成方括号，末尾多一道竖线')[3:] + '｜',
    # 三、包着
    BT + tail(J[0], '整行包在反引号里') + BT,
    F3 + '\n' + tail(J[1], '上下各一行代码围栏') + '\n' + F3,
    '“' + tail(J[2], '整行包在引号里，后果里自己的“引号”留着') + '”',
    # 四、栏数
    LOCK + '｜不利｜差一点｜骰那一栏整个没写，当没掷骰',
    '｜'.join(tail(J[1], '')[:-1].split('｜')),                                  # 少后果：到结果为止
    '｜'.join(c0[:5] + c0[6:9]) + '｜少了应对方的几项，末尾又多一栏｜备注：多出来的并进这一句',
    '｜'.join(c0[:2] + ['不利', '第六颗 4']) + '｜结果那一栏没写、骰后头直接是这一句后果的，出简版，不出绶带',
    '｜'.join(c0[:6] + ['还行'] + c0[7:9]) + '｜定档不在五个词里，照旧落成原样一行',
]
JUDGE[8] = '｜'.join(J[1].split('｜')[:9])
WORDS = ['钟声第三下落定的时候，回廊尽头那排骸骨同时抬起了头。', '贝拉还攥着那本名册不肯往闸门外退。', '薇拉的弦已经拉满了。', '艾莉娅的火线擦着你的肩头过去。',
         '枪阵又压上来一步。', '名册在她手里攥出了褶子。', '钟绳在穹顶上晃。', '营地那只铁匣还锁着。', '闸门外头的风灌进来。', '第二排骸骨补了上来。', '照明杖的光暗了一截。', '钟又响了一下。']
e = [x.split('｜') for x in E]
ESTATE = [
    ' | '.join(e[0][:-1] + ['欠着 竖线全写成半角、两边带空格']),
    '｜'.join(e[1][:-1] + ['欠着 行首的记号漏了'])[1:],
    '＃' + '|'.join(e[2][:-1] + ['合击 行首写成井号，竖线半角'])[1:],
    BT + '｜'.join(e[3][:-1] + ['这一季 整行包在反引号里']) + BT,
    '“' + '｜'.join(e[4][:-1] + ['这一旬 整行包在引号里，末尾还多一道竖线']) + '｜”',
    F3 + '\n' + '｜'.join(e[5][:-1] + ['风险 两行一起包在代码围栏里']) + '\n' + '【家业】' + '｜'.join(e[6][1:-1] + ['风险 名目写成方括号']) + '\n' + F3,
    '家业|产业|城北马车行',
]
p = [x.split('｜') for x in P]
PETS = [
    '|'.join(p[0][:-1] + ['此刻 行首的记号漏了，竖线全是半角'])[1:],
    BT + '｜'.join(p[1][:-1] + ['此刻 整行包在反引号里']) + BT + ' ',
    '※宠｜灰背｜驮蜥·成体｜坐骑·同行｜此刻 行首写成别的符号，状态那一栏没写｜',
]


def build():
    out, ji, done_e, done_p = [], 0, False, False
    for l in L:
        if l.startswith('§判｜'):
            # 四张原来的位置上各放三张
            for k in range(3):
                out += [JUDGE[ji], '', WORDS[ji], '']
                ji += 1
            while out and out[-1] == '':
                out.pop()
            out.pop()            # 最后那一句不要，原来的正文接着
            continue
        if l.startswith('§家业｜'):
            if not done_e:
                out += ESTATE
                done_e = True
            continue
        if l.startswith('§宠｜'):
            if not done_p:
                out += PETS
                done_p = True
            continue
        out.append(l)
    assert ji == 12 and done_e and done_p
    return '\n'.join(out)


write(os.path.join(UP, '样本_兜底_11-25.txt'), build())

# ---- 主角头像：身份那一行换种族性别、添立绘那一行、出手方写成「你」、主角在应对那一边 ----
B = read(os.path.join(HERE, '样本_检定演出.txt'))
ID = '§面板｜身份｜洛恩·维斯特｜人类｜22岁｜男｜守住身后的人｜白鹿书堡旧学徒'
assert B.count(ID) == 1
JB = [l for l in B.split('\n') if l.startswith('§判｜')]


def pc(name, race='人类', sex='男', art=None, edit=None):
    t = B.replace(ID, '§面板｜身份｜洛恩·维斯特｜%s｜22岁｜%s｜守住身后的人｜白鹿书堡旧学徒' % (race, sex) + ('\n§面板｜立绘｜' + art if art else ''))
    if edit:
        t = edit(t)
    write(os.path.join(HERE, '样本_主角头像_%s.txt' % name), t)


pc('剪影_人类男')
pc('剪影_精灵女_没画的预设', '精灵', '女', '预设·高等精灵·女·纤细｜衣着:常服')
pc('剪影_魔族夜翼', '魔族', '女', '预设·夜翼系·女·均匀｜衣着:战斗')
pc('剪影_矮人男_立绘写无', '矮人', '男', '无')
pc('预设_晨曦人男健壮', '人类', '男', '预设·晨曦人·男·健壮｜衣着:常服')
pc('自己的图', '人类', '女', 'http://127.0.0.1:8791/por_pc_h_cx_f2.webp｜头像:http://127.0.0.1:8791/face_one.webp｜衣着:常服')
# 出手方写成「你」；第二张换成敌人打主角（主角在右边）
swap = JB[0].split('｜')
swapped = '｜'.join([swap[0], '攻防·枪卫一枪刺向你的肋下', swap[4], 'DEX 30、ATK 71↑、地形 枪阵封住回廊↑', swap[2], 'VGR 42、PV 41、DV 33↑、装备 潮骨回廊·Legend↑', '不利', '第三颗 8', '擦中', '枪尖从盾沿滑过去，你 HP −36，架势 −20'])
pc('写成你_和_主角在右边', '兽耳族', '女', None, lambda t: t.replace(JB[0], JB[0].replace('｜洛恩·维斯特 共鸣·凝华 LVL 38｜', '｜你 共鸣·凝华 LVL 38｜', 1)).replace(JB[1], swapped))
