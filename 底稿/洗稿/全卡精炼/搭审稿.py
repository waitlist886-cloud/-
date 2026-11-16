#!/usr/bin/env python3
# 全卡精炼洗稿：给一份活备好每一位审稿人的派活单。在仓库根上跑：
#   python -I -X utf8 底稿/洗稿/全卡精炼/搭审稿.py <份名…>
# 认三种活：
#   纷N甲…（纷争纪的页，分段稿）：照 搭活_纷争纪.py groups 的分法，OVERRIDE 里另写了分法的照 OVERRIDE。
#   铜N甲…、前N甲…（山铜纪、前传的页，分段稿）：照 搭活_分段.py groups 铜|前 的分法。
#   稿/ 里全是羁绊文件的（纷羁甲…）：照 BOND 的分法，没写的一位两万六千字以内照文件顺着分。
# 每一位在活的文件夹里得一份 派活_第N位.md，主会话派审稿人的时候只要叫他读这一份。
# 末尾印出每一位的一行（份名、第几位、文件、交什么），派活时照着起子任务。
import io
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'C:/Users/waitl/codex_work/wash_1115'
CN = '一二三四五六七八九'
han = lambda s: len(re.findall(r'[一-鿿]', s))

# 主线和它自己的星放给同一位审（11-16 第七拨起）
OVERRIDE = {
    '纷4丙': [
        ['t5c_gap_3600.md', 't6e_stars_3600.md'],
        ['t5d_gap_4200.md', 't6f_stars_4200.md'],
        ['t6_stars.md', 't6b_stars_2400.md', 't6c_stars_3400.md', 't6d_stars_1790.md'],
    ],
}

BOND = {
    '纷羁甲': [['补卷_42_羁绊_一.md', '补卷_43_羁绊_二.md'], ['补卷_45_羁绊_三.md']],
    '纷羁乙': [['补卷_46_羁绊_四.md', '补卷_47_羁绊_五.md'], ['补卷_48_羁绊_六.md']],
    '纷羁丙': [['补卷_49_羁绊_七.md'], ['补卷_50_羁绊_八.md']],
    '纷羁丁': [['补卷_51_羁绊_九.md'], ['补卷_52_羁绊_十.md']],
    '纷羁戊': [['补卷_53_羁绊_十一.md'], ['补卷_54_羁绊_十二.md']],
    '纷羁己': [['补卷_55_羁绊_十三.md', '补卷_56_羁绊_十四.md']],
    '纷羁庚': [['补卷_57_羁绊_十五.md', '补卷_58_羁绊_十六.md']],
}

ERA_NAME = {'纷': '纷争纪', '铜': '山铜纪', '前': '迷宫纪前传', '月': '月银纪'}

PAGE_NOTES = {
    ('纷', 4): [
        '诺伦·晨曦在叙述和人物嘴里一律作男性（他），真容只在锁里、不点破。洗后别把锁里的话挪进正文。',
        '那几场神战（谁在场、换掉的是谁、谁活过了那一仗）、神杀炮第一炮、珂伦娜的七座营垒，名字、数目、先后逐个对原稿。洗稿压短的时候最容易把在场的和倒下的写反。',
        '“命路”这个叫法、路册、各样机器头一回出现的年份，洗后不能比原稿早。',
    ],
    ('纷', 5): [
        '乌尔德、诗蔻蒂立国和南下的那几仗，塔妮丝那一箭，血誓的宴，日头停了一整夜的那一夜：谁在场、换掉的是谁、谁死在哪，逐个对原稿。',
        '浮空塔、机甲、星纱列车这些东西头一回出现的年份，洗后不能比原稿早。',
        '旧三国把冠交给金鸢城那几年的先后和缘故照原稿，洗后别写成谁发兵打下来的。',
    ],
    ('纷', 6): [
        '七柱碑那一仗：前一夜谁走到了墙这一边，第二天喊的次序，谁按进去的火，各人的下场，逐个对原稿。',
        '联军在死域里的机器叫发条机兵（军册上叫自律机兵），魔族那一边骨匠拼的兽叫铁狼。正文里不写“铁狗”。',
        '艾瑟莉娅、卡尔泽因、席恩这几位的年纪、凝名的年份和先后逐个对原稿。',
    ],
    ('纷', 7): [
        '辛美尔小队四个人是辛美尔、海塔、艾泽、芙莉莲。矮人叫艾泽，传奇之名砧音，原稿就是这样写的，别改成别的名字。亚蒙倒在这四个人手里，没有一位神在场。',
        '止戈那一段，两军之间那个女人不说名字，叙述和人物嘴里都不点破她是谁；雨城那一夜只给 AI 的话照原稿留在锁里，不挪进正文。',
        '主线开头的“题：”“篇：”两行一个字不动；收束里连着排的那四句（加了引号的）照原稿留着。',
        '反叛那一营：三尊魔神各是谁杀的、用了几天，这一营的下场，逐个对原稿。',
    ],
}
ERA_NOTES = {
    '铜': [
        '两个王这一纪还年轻：巴尔缇娜661年灰雨那一夜以前是灰雨城的魔女、没有凝名，索恩薇娅668年才凝名。“圣君”“凡极”“魔王”这些后来的名号，原稿没写的地方洗后也不许有。',
        '雨城那个不说名字的女人，叙述和人物嘴里都不点破她是谁，原稿只给 AI 的话洗后还得只在锁里。',
        '正文里引到碑名、碑上刻的字，照原稿一个字不动。主线开头的“题：”“章：”两行一个字不动。',
        '佣兵团、遗迹、有魔力的东西这一层是这一纪的戏，收短可以，不能洗成账和手续。',
    ],
    '前': [
        '委托单上的字（单头、正面、背面、结案栏）照原稿一个字不动。主线开头的“题：”“章：”两行一个字不动。',
        '井、层、雾门、深印、楼层主这些东西各自头一回出现的年份，洗后不能比原稿早；面板和旅印七阶是420年以后才有的。',
        '七神这一纪不现身，原稿写成梦、代行者、兆头的，洗后不许写成神本人到场。两个王只在原稿写到的地方出场。',
        '下井的戏在井下，照迷宫的路子写：规矩、守着的东西、最底下那一幅画面，收短可以，不能洗成柜台上的手续。',
    ],
}

TPL = '''# 派活｜{job}｜第 {k} 位审稿人

你是审稿人，全程用中文。先读 `E:/aldran_art/底稿/洗稿/全卡精炼/审稿_派活.md`，照它做。这一回审的是{era}第 {page} 页的分段稿，重点看它“审分段稿”那一节，再读它叫你先读的三份。

- 活的文件夹：`C:/Users/waitl/codex_work/wash_1115/{job}`
- 归你的文件：{files}。直接改 `稿/` 里这几个文件，对着 `原/` 里同名的文件一节一节审。这一份活里别的文件是另一位在审，一个字也别动。
- `稿_Codex原样/` 是洗稿的人交回来的原样，只读，量你补回了多少用。`自查_备审.txt` 是主会话跑过的自查和查栏目。
- 自查：在活的文件夹里跑 `python -I -X utf8 自查.py`，它报的是整份活的结果，你只管落在你这几个文件里的，报“错”的改到没有。
- 审稿写成 `审稿_{job}_{cn}.md`，放在活的文件夹里。
{star}

## 这一页另外要盯的

{notes}

## 通用的再提醒几句

- 你是查错，不是重洗。补回有上限：一节至多比接手时多出原稿的一成，一条至多换回三句。要动七八处以上的节，写进“要主会话定的事”。
- 洗后多出来一件事，先在 `原/` 整个文件夹里 Grep，别处有的不算添的。原稿哪里都没有的才删。
- 原稿世道一栏只写“世道照某某的时段总纲”的，洗后也只留这一句，从总纲抄过来的尺度句子删掉。
- “判定获得优势”“判定获得劣势”这类机制用语照原稿，一个字不换。星条【调用】开头的年月（“某某的年月里，”）照原稿留着。
- 条目里写着什么时候把某样东西（真名、龙名、一句话、一件信物）告诉玩家的，那样东西是什么得留在这一条里。
- `## 这一代的命星`、`## 这一代的人物` 标题底下到头一颗星、头一条人物以前的那一段是给作者看的，主会话已经照原稿还原，别动。
- 改完读一遍你改过的句子：别为了补回写出跟别处重的话，也别写出“不知道为什么”“没有人知道他”这一类满大街的现成话，换个自己的说法。
- 不提交，不改仓库里的任何文件，不动 `原/`、`稿_Codex原样/` 和别人的文件。

{report}
'''

TPL_BOND = '''# 派活｜{job}｜第 {k} 位审稿人

你是审稿人，全程用中文。先读 `E:/aldran_art/底稿/洗稿/全卡精炼/审稿_派活.md`，照它做。这一回审的是{era}的羁绊补卷，重点看它“审补卷”那一节，再读它叫你先读的 `审稿说明.md` 和 `审稿_另外盯的几件.md`（`命星表_说明.md` 这一回用不着）。

- 活的文件夹：`C:/Users/waitl/codex_work/wash_1115/{job}`
- 归你的文件：{files}。直接改 `稿/` 里这几个文件，对着 `原/` 里同名的文件一章一章审。这一份活里别的文件是另一位在审，一个字也别动。
- `稿_Codex原样/` 是洗稿的人交回来的原样，只读。`自查_备审.txt` 是主会话跑过的自查。
- 自查：在活的文件夹里跑 `python -I -X utf8 自查.py`，它报的是整份活的结果，你只管落在你这几个文件里的，报“错”的改到没有。
- 审稿写成 `审稿_{job}_{cn}.md`，放在活的文件夹里。
- 专名表：照 `E:/aldran_art/底稿/洗稿/全卡精炼/专名表_说明.md`，一个文件交一份 `专名表_<文件名去掉.md>.tsv`，只盘不改。

## 羁绊的章要盯的

- 章名（某某之章）、题（【】里的字）、`### ` 小标题一个字不动。紧跟 `## ` 标题的两行（“某某之章：【题】”那一行，和“【人名】一句话是谁·种族·位阶……·比玩家强还是弱”那一行）照原稿一字不动。
- 核心结、抉择点的几条路、结算里的伟业和信物、失败怎么算，洗后都得在。示范对白、主题候选、“一幕一层”的提要并掉是对的。
- 引号里的台词不许改字，只许整句删。删到一章里一句这个人的原话也不剩的，照原稿留回一两句最像他的。
- 门（这一章哪一年到哪一年开、光提名字开不开）和这个人正史里的死年，逐个对原稿。门窄的（只开活着那几年的）别洗宽了。
- 这一纪的口径：{era_bond}
- 改完读一遍你改过的句子：别写出“不知道为什么”“没有人知道他”这一类满大街的现成话，换个自己的说法。
- 不提交，不改仓库里的任何文件，不动 `原/`、`稿_Codex原样/` 和别人的文件。

{report}
'''

ERA_BOND = {
    '纷': '诺伦·晨曦在叙述和人物嘴里一律作男性（他），真容只在锁里；辛美尔小队的矮人叫艾泽，传奇之名砧音；联军在死域里的机器叫发条机兵，不写“铁狗”；止戈那一位、雨城那个孩子是谁，原稿不点破的洗后也不点破；神用祂。',
    '铜': '两个王这一纪还年轻，“圣君”“凡极”“魔王”这些后来的名号原稿没写的地方洗后也不许有；雨城那个不说名字的女人不点破；碑名和碑上的字照原稿。',
    '前': '委托单上的字照原稿；七神这一纪不现身；面板和旅印七阶420年以后才有；井、层、雾门这些东西头一回出现的年份不能比原稿早。',
    '月': '这一纪没有面板、公会和命路；神下凡扮成凡人的，叙述照原稿用他、她；月亮和月相的字眼不写。',
}

REPORT = ('最后一条消息写短，细目都在审稿文件里，不用重复：一行总评（看了几节或几章，小改几节，要重洗几节），'
          '补回、换回、删掉添的各几处，自查错几条；“要主会话定的事”逐条写全（没有就写无）；'
          '{extra}一共不超过三百字。')


def era_of(job):
    return job[0] if job[0] in ERA_NAME else '纷'


def is_bond(job):
    fs = os.listdir('%s/%s/稿' % (BASE, job))
    return bool(fs) and all('羁绊' in f for f in fs)


def groups_of(job):
    if job in OVERRIDE:
        return OVERRIDE[job]
    if job in BOND:
        return BOND[job]
    if is_bond(job):
        gs, cur, w = [], [], 0
        for f in sorted(os.listdir('%s/%s/原' % (BASE, job))):
            n = han(open('%s/%s/原/%s' % (BASE, job, f), encoding='utf-8').read())
            if cur and w + n > 26000:
                gs.append(cur)
                cur, w = [], 0
            cur.append(f)
            w += n
        if cur:
            gs.append(cur)
        return gs
    e = era_of(job)
    if e == '纷':
        cmd = [os.path.join(HERE, '搭活_纷争纪.py'), 'groups', job]
    else:
        cmd = [os.path.join(HERE, '搭活_分段.py'), 'groups', e, job]
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8'] + cmd, capture_output=True)
    out = r.stdout.decode('utf-8', 'replace')
    gs = []
    for ln in out.splitlines():
        m = re.match(r'^第 \d+ 位｜可洗 \d+ 字｜(.+)$', ln.strip())
        if m:
            gs.append([x if x.endswith('.md') else x + '.md' for x in m.group(1).split('、')])
    return gs


def page_of(job):
    m = re.match(r'^.(\d)', job)
    return int(m.group(1)) if m else 0


def has_star(job, files):
    for f in files:
        p = '%s/%s/原/%s' % (BASE, job, f)
        if os.path.exists(p) and re.search(r'^### .+\((?:Special|Passive|Art|Active)', open(p, encoding='utf-8').read(), re.M):
            return True
    return False


rows = []
for job in sys.argv[1:]:
    d = '%s/%s' % (BASE, job)
    if not os.path.isdir(d):
        print('！没有这个活的文件夹：', job)
        continue
    have = set(os.listdir(d + '/稿'))
    gs = groups_of(job)
    flat = [f for g in gs for f in g]
    if set(flat) != have or len(flat) != len(set(flat)):
        print('！%s 的分法跟 稿/ 里的文件对不上：多 %s，少 %s' % (job, sorted(set(flat) - have), sorted(have - set(flat))))
        continue
    e = era_of(job)
    bond = is_bond(job)
    page = page_of(job)
    for k, g in enumerate(gs, 1):
        cn = CN[k - 1]
        files = '、'.join('`%s`' % f for f in g)
        if bond:
            rep = REPORT.format(extra='专名表里白话名标“是”的有几条也报一下；')
            txt = TPL_BOND.format(job=job, k=k, cn=cn, era=ERA_NAME[e], files=files, era_bond=ERA_BOND.get(e, ''), report=rep)
            st = False
        else:
            st = has_star(job, g)
            star = ('- 命星表：你的文件里有 `### ` 星条，交 `命星表_%s_%s.tsv`（照 `E:/aldran_art/底稿/洗稿/全卡精炼/命星表_说明.md`，一颗有 `### ` 标题的星一行，“文件”那一栏填星所在的文件名，只盘不改。判星映不映这个人的命，对着他“正史里的下场”那一栏看，下场不在你的文件里的，去 `原/` 别的文件或者仓库里同一页的分段稿里只读地查）。' % (job, cn)
                    if st else '- 你的文件里没有命星条，不交命星表。')
            notes = PAGE_NOTES.get((e, page)) or ERA_NOTES.get(e) or ['照审稿_派活.md 和审稿_另外盯的几件.md。']
            rep = REPORT.format(extra='交了命星表的报几颗星，Special 里映着、沾边、没映各几颗；' if st else '')
            txt = TPL.format(job=job, k=k, cn=cn, era=ERA_NAME[e], page=page, files=files, star=star,
                             notes='\n'.join('- ' + x for x in notes), report=rep)
        open('%s/派活_第%d位.md' % (d, k), 'w', encoding='utf-8', newline='\n').write(txt)
        rows.append((job, k, cn, g, '交专名表' if bond else ('交命星表' if st else '不交表')))
for job, k, cn, g, what in rows:
    print('%s｜第 %d 位｜%s｜%s' % (job, k, '、'.join(g), what))
print('一共 %d 位' % len(rows))
