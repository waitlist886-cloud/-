#!/usr/bin/env python3
# 纷争纪主线改稿铺开（11-21，用户认了样稿和 12 件，照倾向铺）。照迷宫纪前传那一回：Fable 写、Opus 审、Fable 改、主会话收。
#   python -I -X utf8 tools/api/strife_pukai.py build|submit|wait <拨>
#   拨：1 主线初稿（一条一份，36 条，雨城的星、无名之柱用户认过的样稿不重写）
#       2 Opus 审初稿    3 Fable 照审稿改
# 交稿写 底稿/审稿/纷争纪/铺开/<拨>_<主线>.md。
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import review_batch as rb  # noqa: E402
import strife_review as SR  # noqa: E402
import pukai_batch as PB  # noqa: E402

D = SR.D
OUT = os.path.join(D, '铺开')
OL = os.path.join(D, '大纲_合并_第一版.md')
WRITER = 'claude-fable-5-2'
REVIEWER = 'claude-opus-5-5'
PAGE_CN = '一二三四五六七'
PART = {1: '灰', 2: '白石', 3: '灯', 6: '铁狼', 7: '号角'}
for p, names in [('炮上', ['箭与冠的秤', '最后一垄', '白鸢的天', '无继之光']), ('炮下', ['空鞍的白马', '第七座营垒', '不熄火', '锈花']),
                 ('浮塔上', ['北归道', '盐门', '离地', '塔与剑']), ('浮塔下', ['松开的锁链', '射主', '南七段', '三枚日轮', '落尽'])]:
    for n in names:
        PART[n] = p
SAMPLES = ['雨城的星', '无名之柱']


def mains():
    """[(页, 主线名, 原主线名)]，照合并稿的次序；断锁的原主线是鹿角纪年。"""
    t = SR.rd(OL)
    out, page = [], 0
    for line in t.split('\n'):
        m = re.match(r'^## 第(.)页·', line)
        if m:
            page = PAGE_CN.index(m.group(1)) + 1
            continue
        if line.startswith('## 附'):
            break
        m = re.match(r'^### (\S+?)（原判', line)
        if m and page:
            name = m.group(1)
            out.append((page, name, '鹿角纪年' if name == '断锁' else name))
    return out


def part_of(page, name):
    return PART.get(name) or PART[page]


def outline_of(name):
    t = SR.rd(OL)
    m = re.search(r'^### ' + re.escape(name) + r'（[^\n]*$', t, re.M)
    n = re.search(r'^#{2,3} ', t[m.end():], re.M)
    return t[m.start():m.end() + (n.start() if n else len(t))]


def page_sec(page):
    t = SR.rd(OL)
    a = t.index('## 第%s页·' % PAGE_CN[page - 1])
    b = t.index('\n### ', a)
    return t[a:b]


def appendix(no, page):
    t = SR.rd(OL)
    a = t.index('## 附%s' % no)
    b = t.find('\n## ', a + 5)
    s = t[a:b if b > 0 else len(t)]
    if page is None:
        return s
    k = s.find('**第%s页' % PAGE_CN[page - 1])
    if k < 0:
        return ''
    e = s.find('\n**第', k + 5)
    return s[k:e if e > 0 else len(s)]


def main_with_companions(t, name):
    """原主线连同裁定锁，再加它后头的旅伴条全文（到下一条主线为止）。"""
    bs = SR.blocks(t)
    out, on = [], False
    for h, b in bs:
        if h.startswith('## 纷争纪·主线｜'):
            if on:
                break
            on = h.split('·', 2)[-1].strip() == name
        if on and (h.startswith(('## 纷争纪·主线｜', '## 裁定锁', '## 旅途同行', '## 这一段旅伴之间'))):
            out.append(b)
        elif on and out and h.startswith(('## 这一代的', '## 这一段的传奇表', '## 设计备注', '## 凡世至强', '## 纷争纪·时段')):
            break
    assert out, name
    return ''.join(out)


HEAD1 = '''你是这张卡的写手，全程用中文。这一回是纷争纪主线改稿的铺开，一条主线一份，写成卡面稿。用户看过两条样稿（附在下面「用户认过的样稿」）说认了，口气、分量、格式、拍子的密度照那两条，内容别抄。你看不到仓库，要读的东西都附在用户消息里了。

要守的，按要紧的次序：
1. 改稿大纲合并稿里你这一条（附在用户消息里）：新骨架、对手和他的三手、三幕、收束、传奇和凝名、玩家能干的、照留的原拍、跟着要改的。大纲里〔待用户定〕的地方，用户已经认了照倾向写。大纲里【量级】【高潮】这类标注是给你看的，不写上卡面。
2. 歌、二十二张、碑是正史，一个字不动，你写的要跟它们对得上。原主线里大纲说照留的拍子照留，能用原句的用原句。传奇的档、死法、凝名和到传奇的年份照附五跨份对齐表和大纲「传奇和凝名」。
3. 主线是给主持的骨架，不是小说：一幕三到五拍，一拍一两句，台词只留最要紧的一两句。英雄、传奇出手先写天地和远处的人看见什么。对手有名有脸，玩家当面碰得上，出三回手，高潮是做出来的事。
4. 写作口径整节（附在下面），卡面的标点、禁词、月相字、东方语感的字、玩家在场、什么杀得死传奇、怎么踏进传奇、起名，一条一条照守。
5. 四份写作 skill（附在下面），写之前读完。

卡面的规矩：
- 不用——、—、；、…、！、...，冒号只在标签行（八个字以内）。对白用“”。
- 神用祂。那一位恶神不点名。四执政不入场。
- 新起的设定在卡面句末标（★）。
- 「」只给真条目名。引页上的人物条、凡世至强条，写名字，不加「」，不写“页尾”“那一页”。
- 格式照原主线：## 标题、【调用】、题和篇、引语、开局、世道、一幕二幕三幕（每幕一拍一条，末一条幕终）、收束、默认收束、玩家能改、碰得上的人、## 裁定锁、条目设置。条目设置那一行照原稿抄，只改触发里要跟着改的名字。新拆出来的主线（断锁）照同页别的主线的条目设置写法起一行，年份照它自己的年份。

交什么：直接输出 Markdown，前后不加别的话。
1. 改好的整条主线，连同裁定锁和条目设置。
2. 大纲里新起的对手（名字带★、原页没有人物条的）各写一条人物条，格式照原页人物条（## 纷争纪·人物｜……（人物）那一种，连条目设置）。原页已有人物条或凡世至强条的人不重写，写进设计备注。
3. 末尾一节「## 设计备注（不进卡）」：改了什么，新起的名字和设定，自己拿的主意，锁加了什么、开了什么，跟着要改的地方（旅伴条、人物条、凡世至强、时段总纲、页头，一句一处，写清改成什么）。
'''


def system1():
    cl = PB.rd('CLAUDE.md')
    rules = PB.sec(cl, r'^## 写作口径', r'^## 换账号接手')
    skills = ['# skill：%s\n\n%s' % (n, open(os.path.join(PB.SK, n, 'SKILL.md'), encoding='utf-8').read())
              for n in ['western-fantasy-prose', 'chinese-prose-register', 'jrpg-lore-writing', 'genshin-dialogue-voice']]
    samples = '\n\n'.join('## 样稿：%s\n\n%s' % (n, SR.rd(os.path.join(D, '样稿_%s.md' % n))) for n in SAMPLES)
    return (HEAD1 + '\n# 写作口径（CLAUDE.md 整节）\n\n' + rules + '\n\n' + '\n\n'.join(skills)
            + '\n\n# 用户认过的样稿（口气、分量、格式照这两条）\n\n' + samples)


def write_job(page, name, orig):
    t = SR.page_text(page)
    fx = SR.rd(os.path.join(rb.ROOT, '纷争纪', '纷争纪_方向与写法_第二版.md'))
    cards = rb.section(fx, r'^## 六、逐张', r'^## 七、')
    people = '\n'.join(b for h, b in SR.blocks(t) if ('（人物）' in h or h.startswith('## 纷争纪·凡世至强')))
    origs = [orig] + ([] if orig == name else [])
    parts = [
        '# 你的活\n\n写纷争纪第%s页的主线「%s」，照改稿大纲合并稿铺开成卡面稿。' % (PAGE_CN[page - 1], name)
        + ('这一条是从鹿角纪年原第三幕拆出来的新主线，鹿角纪年由别的写手改，你只写断锁，鹿角纪年的原稿附在下面是给你对账、抄可用的原句。' if name == '断锁' else ''),
        '# 改稿大纲合并稿里你这一条\n\n' + outline_of(name),
        '# 改稿大纲合并稿里这一页的本页通盘\n\n' + page_sec(page),
        '# 附五　跨份对齐表\n\n' + appendix('五', None),
        '# 附四里这一页的账\n\n' + (appendix('四', page) or '无'),
        '# 附三里这一页的合并备注\n\n' + (appendix('三', page) or '无'),
        '# 方向稿第六节 逐张（二十二张，正史）\n\n' + cards,
        '# 这一页的页头和时段总纲\n\n' + SR.head_of(t),
        '# 这一页的史诗（歌，正史）\n\n' + '\n'.join(b for h, b in SR.blocks(t) if '（史诗·纷争纪）' in h),
        '# 这一条的审稿（11-21 那一份，你这一条那几节）\n\n' + SR.rd(os.path.join(D, '审_%s.md' % part_of(page, name))),
    ]
    for o in origs:
        parts.append('# 原主线「%s」（带裁定锁和它的旅伴条全文）\n\n' % o + main_with_companions(t, o))
    parts.append('# 这一页的人物条和凡世至强（对账用）\n\n' + people)
    return parts


REVIEW_SYS = '''你是审稿人，全程用中文。这一回审纷争纪主线改稿铺开交回来的一条主线稿，只审不改，看不到仓库，材料都附在用户消息里了。

这一轮的尺子是用户认过的两条样稿（附在下面）、改稿大纲合并稿里这一条、写作口径。量下面几样，指到哪一幕哪一拍，引原文一处不超过二十字：
1. 对手：有名有脸、玩家当面碰得上、出三回手、一回比一回狠，第三回是高潮里的正面交手。高潮是不是做出来的事，有没有收在名字、碑、账、一碗汤上。对手和三手跟大纲对不对得上。
2. 超凡的表现力：英雄、传奇、魔神、机兵、炮出手，有没有先写天地和远处的人看见什么；有没有写成凡人对砍；尺度（亿万级的仗、墙从雪山连到雪山）出没出来。位阶和档对不对。
3. 传奇：死法落没落在四样上（同档三位围杀或克制或高一档、百位英雄、神性、十万军团，燃尽是自己选的），不走写没写为什么不走；凝名和到传奇两样各在哪一刻齐，跟附五对齐表对不对得上。寻常军队有没有伤到传奇。
4. 详略：是不是给主持看的骨架（一幕三到五拍、一拍一两句、对白一幕一两句），有没有铺成小说，或者只剩提纲看不出戏。
5. 正史：跟歌、二十二张对不对得上；大纲说照留的原拍留没留；有没有改出新的前后不搭（年份、谁死在哪、谁在场）。
6. 玩家在场：玩家能改有没有写成改不了、拦不下；锁有没有拿来限制玩家。
7. 卡面：标点（——、—、；、…、！）、冒号只在标签行、禁词和东方语感的字、月相字、神用祂、恶神不点名、四执政不入场、给作者看的话漏进卡面、「」用错、标题和条目设置被乱改。卡面检查脚本的结果附在后面，脚本报的也要写进「要写手改的」。
8. 新起的对手人物条：格式、条目设置、跟主线对不对得上。
9. 设计备注「跟着要改的」全不全：对着原页的旅伴条、人物条、凡世至强、时段总纲看，有没有漏的。
10. 好的地方也写一两句。

交一份 Markdown，从一级标题写起，末尾一节「要写手改的」，一条一行，写清改哪一幕哪一拍、改成什么样。前后不加别的话。思考少用一些，留够输出。'''

REVISE_NOTE = ('# 这一回是改稿\n\n你上一回交的这一条（附在后面）审过了，审稿意见附在后面。照「要写手改的」逐条改，'
               '审稿说好的、没提到的地方别动。改完照原来的格式整份重新输出（主线、裁定锁、新起的对手人物条、设计备注），'
               '设计备注开头加一节「改稿改了什么」，一条一行对着审稿的条目。审稿跟大纲、样稿、写作口径冲突的，以大纲、样稿、口径为准，在备注里写一句。')


def scan_of(name):
    p = os.path.join(OUT, '扫_%s.txt' % name)
    return SR.rd(p) if os.path.exists(p) else '（没跑）'


FIX_TASK = '''# 你的活

纷争纪第{page}页的主线已经照改稿大纲重写完、拼进页里了（新的主线附在后面）。这一页别的条目有些地方跟新主线对不上了，你把它们改掉。{scope}。

先看各条主线设计备注里「跟着要改的」那几节（附在后面），那是写手记下的账，逐条照改；再对着附五跨份对齐表和大纲这一页的「本页通盘」「跟着要改的」核传奇的档、死法、凝名和到传奇的年份；再自己通读整页，账上没记、你看出来对不上的也改：谁的下场变了，谁换了对手，引了改了名的人和东西（换名表附在后面），引了主线里删掉的拍子，旅伴的初见、关系、正史里的下场、好感增减、裁定锁、年份黑名单跟主线对不上。

不动的：主线（## 纷争纪·主线｜那几条和紧跟的裁定锁）这一回不改；新起的对手人物条（标题里带★或者这一回刚接进页的）不改；每一条的标题一字不改；条目设置那一行只改触发里要跟着改的名字和黑名单年份；固定锚定、身份那一行的人名、底座、体态数据、### 星标题这些受保护的行不动，非改不可的在备注里写明。命星（这一代的命星那一节）这一回不改，只在备注里记要改的。歌（史诗）一个字不动。

卡面的规矩照写作口径。改的地方照原条目的口气，别整条重写成另一个样子，改到对得上为止。

交什么：输出两块，前后不加别的话。头一块是改了的条目，每条从「## 标题」那一行写到它的「> 条目设置：」那一行（标题跟原来一字不差，主会话照标题换回去；时段总纲连着它后头的裁定锁写到裁定锁末尾的条目设置），没改的条目不输出。第二块从「## 设计备注」起：逐条写改了什么、对着哪一笔账；命星要改的；页头那一段说明要改的（写出改后的整句）；拿不准的、要用户定的。
'''


def notes_of(name):
    p = os.path.join(D, '样稿_%s.md' % name) if name in SAMPLES else os.path.join(OUT, '3_%s.md' % name)
    s = SR.rd(p)
    k = s.find('## 设计备注')
    return '## 主线「%s」的设计备注\n\n' % name + (s[k:] if k >= 0 else '（没有）')


def common(page):
    ol = SR.rd(OL)
    return ['# 换名表\n\n' + ol[ol.index('## 换名表'):ol.index('## 第一页')],
            '# 附五　跨份对齐表\n\n' + appendix('五', None),
            '# 附四里这一页的账\n\n' + (appendix('四', page) or '无')]


def fix_comp_job(page, name):
    """一条主线的旅伴条、背景、旅伴之间。"""
    t = SR.page_text(page)
    return ('旅伴_' + name, [FIX_TASK.format(page=PAGE_CN[page - 1], scope=SCOPE_COMP.format(name=name)),
                             notes_of(name), '# 改稿大纲合并稿里这一条\n\n' + outline_of(name)]
            + ([notes_of('断锁'), '# 改稿大纲合并稿里断锁（从鹿角纪年原第三幕拆出的新主线，加兹是它的主角，他的旅伴条挂在鹿角纪年下面，两条的账都归你这一份）\n\n'
                + outline_of('断锁'), '# 新主线断锁（现行，这一份不改它）\n\n' + main_with_companions(t, '断锁')] if name == '鹿角纪年' else [])
            + common(page)
            + ['# 这一页的时段总纲（对账用，这一份不改它）\n\n' + SR.head_of(t),
               '# 这一条主线（新的）连同它的旅伴条、旅伴背景、这一段旅伴之间（现行）\n\n' + main_with_companions(t, name)])


def fix_page_job(page):
    """一页的时段总纲、人物条、凡世至强。"""
    t = SR.page_text(page)
    ms = [m for m in mains() if m[0] == page]
    bs = SR.blocks(t)
    mains_txt = []
    for i, (h, b) in enumerate(bs):
        if h.startswith('## 纷争纪·主线｜'):
            mains_txt.append(b + ''.join(bb for hh, bb in bs[i + 1:i + 3] if hh.startswith('## 裁定锁')))
    people = '\n'.join(b for h, b in bs if ('（人物）' in h or h.startswith('## 凡世至强') or h.startswith('## 纷争纪·凡世至强')))
    return ('页_%d' % page, [FIX_TASK.format(page=PAGE_CN[page - 1], scope=SCOPE_PAGE),
                            '# 各条主线的设计备注\n\n' + '\n\n'.join(notes_of(n) for _, n, _ in ms),
                            '# 改稿大纲合并稿里这一页（本页通盘和各条，看「传奇和凝名」「跟着要改的」）\n\n' + page_whole(page)] + common(page)
            + ['# 这一页的页头、时段总纲和它的裁定锁（现行）\n\n' + SR.head_of(t),
               '# 这一页的主线（新的，这一份不改，对账用）\n\n' + '\n'.join(mains_txt),
               '# 这一页的人物条和凡世至强（现行）\n\n' + people])


SCOPE_COMP = '这一份只管主线「{name}」的旅伴条、旅伴背景和这一段旅伴之间（附在最后）'
SCOPE_PAGE = '这一份只管这一页的时段总纲和它的裁定锁、人物条、凡世至强条（附在最后），旅伴条由别的写手改'


def page_whole(page):
    t = SR.rd(OL)
    a = t.index('## 第%s页·' % PAGE_CN[page - 1])
    b = t.index('\n## ', a + 5)
    return t[a:b]


def jobs(w):
    if w == 4:
        pages = [int(x) for x in os.environ.get('PAGES', '1,2,3,4,5,6,7').split(',')]
        return [fix_page_job(p) for p in pages] + [fix_comp_job(pg, n) for pg, n, _ in mains() if pg in pages and n != '断锁']
    ms = [m for m in mains() if m[1] not in SAMPLES]
    only = os.environ.get('ONLY')
    if only:
        ms = [m for m in ms if m[1] in only.split(',')]
    out = []
    for m in ms:
        name = m[1]
        parts = write_job(*m)
        if w == 1:
            out.append((name, parts))
        elif w == 2:
            sub = SR.rd(os.path.join(OUT, '1_%s.md' % name))
            out.append((name, ['# 你审的这一条：%s（纷争纪第%s页）\n\n' % (name, PAGE_CN[m[0] - 1]) + sub,
                               '# 卡面检查脚本的结果\n\n' + scan_of(name)] + parts[1:]))
        elif w == 3:
            out.append((name, parts + [REVISE_NOTE, '# 你上一回交的稿\n\n' + SR.rd(os.path.join(OUT, '1_%s.md' % name)),
                                       '# 审稿意见\n\n' + SR.rd(os.path.join(OUT, '2_%s.md' % name))]))
        else:
            raise SystemExit('拨号不认：%s' % w)
    return out


def system4():
    cl = PB.rd('CLAUDE.md')
    rules = PB.sec(cl, r'^## 写作口径', r'^## 换账号接手')
    skills = ['# skill：%s\n\n%s' % (n, open(os.path.join(PB.SK, n, 'SKILL.md'), encoding='utf-8').read())
              for n in ['western-fantasy-prose', 'chinese-prose-register', 'jrpg-lore-writing', 'genshin-dialogue-voice']]
    return ('你是这张卡的写手，全程用中文。这一回是纷争纪主线改稿以后「跟着改的」那一拨，活在用户消息开头。你看不到仓库，材料都附在用户消息里了。'
            '\n\n# 写作口径（CLAUDE.md 整节）\n\n' + rules + '\n\n' + '\n\n'.join(skills))


def system2():
    samples = '\n\n'.join('## 样稿：%s\n\n%s' % (n, SR.rd(os.path.join(D, '样稿_%s.md' % n))) for n in SAMPLES)
    cl = PB.rd('CLAUDE.md')
    rules = PB.sec(cl, r'^## 写作口径', r'^## 换账号接手')
    return REVIEW_SYS + '\n\n# 写作口径（CLAUDE.md 整节）\n\n' + rules + '\n\n# 用户认过的样稿\n\n' + samples


def build(w):
    reqs, names = [], []
    sysm = system2() if w == 2 else system4() if w == 4 else system1()
    model = REVIEWER if w == 2 else WRITER
    for name, parts in jobs(w):
        params = {'model': model, 'max_tokens': 128000, 'output_config': {'effort': 'high'},
                  'system': [{'type': 'text', 'text': sysm, 'cache_control': {'type': 'ephemeral'}}],
                  'messages': [{'role': 'user', 'content': '\n\n'.join(parts)}]}
        if model == REVIEWER:
            params['thinking'] = {'type': 'adaptive'}
        reqs.append({'custom_id': 'w%d_%d' % (w, len(reqs)), 'params': params})
        names.append(name)
    return reqs, names


def bpath(w):
    return os.path.join(OUT, 'batch_%d.json' % w)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    cmd, w = sys.argv[1], int(sys.argv[2])
    os.makedirs(OUT, exist_ok=True)
    if cmd == 'build':
        reqs, names = build(w)
        print('system', len(reqs[0]['params']['system'][0]['text']))
        for r, n in zip(reqs, names):
            print(n, len(r['params']['messages'][0]['content']))
    elif cmd == 'submit':
        reqs, names = build(w)
        d = json.loads(rb.call(rb.API, {'requests': reqs}))
        json.dump({'id': d['id'], 'jobs': names, 'model': reqs[0]['params']['model']}, open(bpath(w), 'w', encoding='utf-8'), ensure_ascii=False)
        print('交上去了：', d['id'], len(reqs), '份')
    elif cmd == 'wait':
        b = json.load(open(bpath(w), encoding='utf-8'))
        while True:
            d = json.loads(rb.call(rb.API + '/' + b['id']))
            if d.get('processing_status') == 'ended':
                break
            time.sleep(60)
        pr = {'claude-fable-5-2': (8.0, 40.0), 'claude-opus-5-5': (4.0, 20.0)}[b['model']]
        tin = tout = 0
        for line in rb.call(d['results_url']).splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            name = b['jobs'][int(r['custom_id'].split('_')[1])]
            if r['result']['type'] != 'succeeded':
                print('！没成', name, json.dumps(r['result'], ensure_ascii=False)[:300])
                continue
            msg = r['result']['message']
            u = msg['usage']
            tin += u['input_tokens'] + u.get('cache_creation_input_tokens', 0) * 1.25 + u.get('cache_read_input_tokens', 0) * 0.1
            tout += u['output_tokens']
            text = ''.join(c.get('text', '') for c in msg['content'] if c.get('type') == 'text')
            open(os.path.join(OUT, '%d_%s.md' % (w, name)), 'w', encoding='utf-8', newline='\n').write(text.strip() + '\n')
            print('%s：%d 字，停在 %s，出 %d' % (name, len(text), msg.get('stop_reason'), u['output_tokens']))
        print('约 $%.2f' % ((tin * pr[0] + tout * pr[1]) / 1e6 / 2))
