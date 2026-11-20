#!/usr/bin/env python3
# 迷宫纪前传剧情铺开走 API 批处理（11-19）。照 底稿/迷宫纪前传/剧情大纲/铺开计划.md 分拨，一拨一个 batch。
#   python -I -X utf8 tools/api/pukai_batch.py build 1      看第一拨各份请求多大
#   python -I -X utf8 tools/api/pukai_batch.py submit 1     交第一拨，批号记在 底稿/迷宫纪前传/剧情铺开/batch_1.json
#   python -I -X utf8 tools/api/pukai_batch.py wait 1       等完了取结果，写 底稿/迷宫纪前传/剧情铺开/交稿/<份名>.md
# 写手看不到仓库，材料直接喂进请求。密钥照 claude_api.key() 取，不打印。
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import review_batch as rb  # noqa: E402

ROOT = rb.ROOT
WORK = os.path.join(ROOT, '底稿', '迷宫纪前传', '剧情铺开')
OUT = os.path.join(WORK, '交稿')
MAT = os.path.join(ROOT, '底稿', '审稿', '迷宫纪前传', '材料')
SAMP = os.path.join(ROOT, '底稿', '迷宫纪前传', '剧情大纲')
SK = os.environ.get('SKX') or os.path.join(os.environ.get('TEMP', ''), 'skx')
PAGES = {1: '一_探井', 2: '二_共约', 3: '三_繁荣', 4: '四_深井', 5: '五_黑潮', 6: '六_垂暮'}
CN = '一二三四五六'


def rd(*p):
    return rb.rd(*p)


def page_text(n):
    import glob
    f = glob.glob(os.path.join(ROOT, '迷宫纪前传', '迷宫纪前传时段_%s*.md' % PAGES[n]))[0]
    return open(f, encoding='utf-8').read().replace('\r\n', '\n')


def entries(text, prefix):
    out = []
    for m in re.finditer(r'(?m)^## ' + re.escape(prefix), text):
        rest = text[m.start() + 1:]
        s = re.search(r'(?m)^## (?!裁定锁)', rest)
        out.append(text[m.start():m.start() + 1 + (s.start() if s else len(rest))].rstrip() + '\n')
    return out


def card_entries(ids):
    d = json.load(open(os.path.join(ROOT, 'src', 'rili_v7.json'), encoding='utf-8'))
    L = d['prompt']['lorebook']
    return '\n\n'.join(L[i]['content'] for i in ids)


def sec(text, a, b):
    return rb.section(text, a, b)


SYSTEM_HEAD = '''你是这张卡的写手，全程用中文。这一回是迷宫纪前传剧情铺开的一份活，照剧情大纲第一版和用户认过的两条样稿写。你看不到仓库，要读的东西都附在用户消息里了。

要守的，按要紧的次序：
1. 剧情大纲第一版（附在后面），尤其第二节大敌线、第五节写法和末尾用户 11-19 补的三条：主线和条目是给主持的 AI 看的骨架，不是小说；超凡的表现力照位阶表写，先写天地和远处的人看见什么；大迷宫照底卡的层带写，一个层带是一个生态圈或一座被吞下去的异世界，层号只当位置，不写哪一层塌了、哪几层断了。
2. 底卡的层带条目（附在后面）一个字不改它，你写的东西要跟它对得上：层带的样子、楼层主、安全区、位阶曲线、残响的性质、残响异界里救世残影的规矩。
3. 写作口径整节（附在下面），卡面的标点、禁词、月相字、东方语感的字、玩家在场、什么杀得死传奇、起名，一条一条照守。
4. 四份写作 skill（附在下面），写之前读完。

卡面的规矩：
- 不用——、—、；、…、！、...，冒号只在标签行（八个字以内）。对白用“”。
- 那一位恶神不点名，卡面和备注都不点，只写那一位。表层不说井在吃什么，“消化”“胃”这一层只给 AI，照底卡的口径。
- 新起的设定在卡面句末标（★）。原稿里“（#46）”这类底卡出处的括号照留。
- 条目设置那一行的格式照原稿抄，只改触发里要跟着改的名字，打包脚本只读到“深度 N。”为止，条目设置里别套括号。
- 起了新名字的，在设计备注里列出来，主会话会去查撞名。

'''


def system():
    cl = rd('CLAUDE.md')
    rules = sec(cl, r'^## 写作口径', r'^## 换账号接手')
    skills = []
    for n in ['western-fantasy-prose', 'chinese-prose-register', 'jrpg-lore-writing', 'genshin-dialogue-voice']:
        skills.append('# skill：%s\n\n%s' % (n, open(os.path.join(SK, n, 'SKILL.md'), encoding='utf-8').read()))
    return SYSTEM_HEAD + '# 写作口径（CLAUDE.md 整节）\n\n' + rules + '\n\n' + '\n\n'.join(skills)


MAZE_TASK = '''# 你的活

这一份是第一拨「迷宫的底子」里的 {name}：把迷宫纪前传第{pages}页里的 {n} 条迷宫条目（「## 迷宫纪·迷宫｜」开头的，全文附在后面）照底卡的层带重写。主线第二拨才改，这一回你只改迷宫条目，可要替第二拨把账算清楚。

用户 11-19 的原话：“按照底卡实际已经有了的迷宫分层生态来。每一个层带都相当于一个独立的异界，不是真的‘迷宫’。这么一细读我才怀疑写迷宫前传的时候是不是基本都没看迷宫纪1001底卡已有的设定……就是虽然迷宫的整体借来的是类似dnd那种地下城的设定，但是细则上不会存在这个层那个层塌方，从x层到xx层是一个层带，生态圈或者残响异界。”

怎么改：
1. 每一条先对层带：它写的那几层落在哪个层带里，那个层带在底卡里长什么样、有什么魔物、楼层主是谁、安全区在哪。原稿里前传自己编的地形（照井口捏的城、冰河断桥、烧着的平原、纷争纪长垒、会走的神殿、某一层的楼层主而底卡那一层没有楼层主……），换成那个层带里有的东西，或者那个层带里一处区域、一次遭遇。底卡写了楼层主在第几层的，前传的楼层主照那一层；前传写在没有楼层主的层上的“楼层主”，改成那个层带里有名有姓的精英、传奇残响或者一次遭遇，照底卡的位阶曲线定档。
2. 层带不随年代变（底卡：不变的是层数、层带主题、生态与敌人构成、机关类型、资源类别、层主、安全区在该层带内必定存在）。前传各年代能变的是：人走到了哪一层，安全区立没立起来、丢没丢，潮把层带里的东西染成了什么样，人在层带里建的营。
3. 每一条要有大敌线的那一笔（大纲第二节第 2 小节的表）：这一页井底下那一位学会了哪一手，在这一条的层带里露在哪。只给 AI 的那一层写进只给 AI 或者锁里。
4. 原稿里立得住的东西留着：人、年份、事、遗物、规矩的来历。条目名要是带着对不上的层号或者地形（比如“第五十一层的楼层主”“第二十层和往下那一道石阶”），可以改名，改了在备注里写明旧名到新名。
5. 详略照大纲第五节：给主持看的，写这个地方是什么、这一年代人到了哪、碰得上什么、要紧的一两样东西和规矩，不逐拍铺。一条比原稿短或者差不多。
6. 光复那一条要跟光复第三稿（附在后面）对得上，第三稿是用户认过的样子。

交什么：输出两块，前后不加别的话。
- 头一块：重写好的全部条目，一条一个「## 迷宫纪·迷宫｜」节，从标题写到「> 条目设置：」那一行。次序照原稿。
- 第二块从「## 设计备注」起，不进卡，写：
  - 逐条：旧名到新名（没改就写没改）、原来写的层和地形、改成了什么、落在底卡哪个层带的哪一样上。
  - 新起的设定和名字（标★）。
  - 给第二拨的账：这一页的主线里（主线全文附在后面）哪几条、哪几拍写到了跟层带对不上的层号或地形，一条一行，写清原来写的什么、要改成什么。这一块要全，第二拨的写手照它改主线。
  - 这一页的旅伴条、人物条、凡世至强条里你看得出来要跟着改的（主线里点到的就算）。
  - 拿不准的，要用户定的。
'''

M0_TASK = '''# 你的活

这一份是第一拨「迷宫的底子」里的 M0：照剧情大纲第一版第二节，新写几条进卡的条目，放进前传补卷新开的一份「补卷_84_大敌线与沉灯会」。

要写的（一条一个节，格式照附在后面的几条同类条目，各带【调用】、正文、只给 AI 的一层、裁定锁、条目设置）：
1. 迷宫纪·规则｜井底下的那一位（标题你可以照起名口径另起一个，只要是规则那一类）：大纲第二节第 1 到 3 小节。表层这一千年怎么叫它、一页学会了哪一手、人一页还了它哪一手、每回大迷宫潮的潮头。真相层（投影、冲着双王、十兆）照底卡那几条，只给 AI，表层说到“潮的来处”为止。管 2 年到 1000 年，年份黑名单照这一纪的写法（看附的条目怎么写）。文件夹 42·迷宫纪｜规则。
2. 迷宫纪·势力｜沉灯会：大纲第二节第 4 小节。480 年起头（一座城自己的井那一条里的议长），每页出手的人和事，黑潮里开的门，969 年冬被连根拔、会首没抓到，970 年光复第五十七层门前的事照光复第三稿。文件夹 48·迷宫纪｜势力。
3. 迷宫纪·规则｜渊染传奇：大纲第二节第 5 小节，伪造和污染两种做法，诅咒型专长怎么写（名字、效果、界限三栏，界限写井的价钱），克系的样子，回头那扇门，死照什么杀得死传奇，名录的数不动。照底卡传奇凝名与专长锻铸总则、位阶传奇、月银纪的渊染（附在后面）接上。文件夹 42·迷宫纪｜规则。
4. 人物四条，文件夹 46·迷宫纪｜人物，格式照附的冒险团条和人物条：
   - 博尔卡·血纹（断门长桌第二稿里的对头，英雄，血纹帐），往后的下场你定一个，写进只给 AI 或者正史里的下场，黑潮那一页让血纹帐收一个下场。
   - 欧斯特里德·哈斯（沉灯会最后一个会首，渊染传奇，约 790 年那一件，970 年死在封印隘口前），他的诅咒型专长写两三样。
   - 黑潮那一页的两位渊染传奇：背靠背（903 年）里那个两边的号都会吹的统一指挥，九十九条（945 年）里那个也会照影、拿九十九座城当饵的。两人起名，背靠背、九十九条的原稿主线附在后面，照它们的年份、地方写，死在黑潮里，各写诅咒型专长两三样。
   - 头一位渊染传奇是谁：大纲铺开计划里定的是欧斯特里德本人（约 790 年），不另起。
5. 新名字起完列在备注里，主会话会查撞名。

详略照大纲第五节：给主持看的，一条两三千字以内。

交什么：输出两块，前后不加别的话。头一块是补卷_84 的全文，文件头照附的补卷写法（一行标题、一段说明是第几份、几条、进哪几个文件夹），后面一条一节。第二块从「## 设计备注」起，写新起的设定和名字（标★）、借了什么、跟第二拨主线要接的地方（哪条主线要给这几个人留哪几拍）、要用户定的。
'''


def maze_job(name, pages):
    body = []
    n = 0
    for p in pages:
        t = page_text(p)
        es = entries(t, '迷宫纪·迷宫｜')
        n += len(es)
        body.append('# 第%s页的迷宫条目（%d 条）\n\n' % (CN[p - 1], len(es)) + '\n'.join(es))
    heads = ['# 第%s页的页头和时段总纲\n\n' % CN[p - 1] + open(os.path.join(MAT, 'p%d_页头与总纲.md' % p), encoding='utf-8').read() for p in pages]
    mains = ['# 第%s页的主线全文（只读，这一回不改，给第二拨记账用）\n\n' % CN[p - 1] + open(os.path.join(MAT, 'p%d_主线.md' % p), encoding='utf-8').read() for p in pages]
    task = MAZE_TASK.format(name=name, pages='、'.join(CN[p - 1] for p in pages), n=n)
    extra = []
    if 5 in pages:
        extra.append('# 光复第三稿（用户认过）\n\n' + open(os.path.join(SAMP, '样稿_光复_第三稿.md'), encoding='utf-8').read())
    base = [task, '# 剧情大纲第一版\n\n' + rd('迷宫纪前传剧情大纲_第一版.md'),
            '# 底卡的层带条目（一个字不改，照它写）\n\n' + card_entries([1019, 1022, 1055, 1099, 1100, 1101, 1102, 1103, 1104])]
    return name, base + heads + body + mains + extra


def m0_job():
    p5 = open(os.path.join(MAT, 'p5_主线.md'), encoding='utf-8').read()
    p4 = open(os.path.join(MAT, 'p4_主线.md'), encoding='utf-8').read()
    p3 = open(os.path.join(MAT, 'p3_主线.md'), encoding='utf-8').read()

    def one(t, title):
        return sec(t, r'^## 迷宫纪·主线｜[^\n]*' + re.escape(title), r'^## 迷宫纪·主线｜')
    samples = [
        sec(rd('迷宫纪前传', '补卷', '补卷_16_规则战役与魔法.md'), r'^## 迷宫纪·规则｜各地的危险', r'^## 迷宫纪·规则｜以太风'),
        sec(rd('迷宫纪前传', '补卷', '补卷_01_联邦与晨曦.md'), r'^## 迷宫纪·势力｜两边的兵', r'^## (?!裁定锁)'),
        sec(rd('迷宫纪前传', '补卷', '补卷_77_冒险团_探井与共约.md'), r'^## 迷宫纪·冒险团｜雾海之王', r'^## 迷宫纪·冒险团｜长垒之王'),
    ]
    head77 = rd('迷宫纪前传', '补卷', '补卷_77_冒险团_探井与共约.md').split('\n## ')[0]
    moon = rd('moon', 'batch1', 'g4_beasts.md')
    moon = sec(moon, r'^=== 月银纪·渊染', r'^=== ')
    return 'M0', [M0_TASK, '# 剧情大纲第一版\n\n' + rd('迷宫纪前传剧情大纲_第一版.md'),
                  '# 底卡里要接上的几条（真相层、黑潮战史、凝名与专长、位阶传奇、恶神投影）\n\n' + card_entries([60, 51, 76, 116, 124, 1096]),
                  '# 月银纪的渊染（月银纪第一批里的条目）\n\n' + moon,
                  '# 补卷的文件头和同类条目的格式（照这几条写）\n\n' + head77 + '\n\n' + '\n\n'.join(samples),
                  '# 断门长桌第二稿（用户认过）\n\n' + open(os.path.join(SAMP, '样稿_断门长桌_第二稿.md'), encoding='utf-8').read(),
                  '# 光复第三稿（用户认过）\n\n' + open(os.path.join(SAMP, '样稿_光复_第三稿.md'), encoding='utf-8').read(),
                  '# 一座城自己的井（480 年，沉灯会起头的那一条，原稿）\n\n' + one(p3, '一座城自己的井'),
                  '# 一段残响、曜石审判、两边的名单、一枚金币（第四页沉灯会出手的几条，原稿）\n\n' + '\n\n'.join(one(p4, k) for k in ['一段残响', '曜石审判', '两边的名单', '一枚金币']),
                  '# 头一张撤离单、背靠背、九十九条（第五页，原稿）\n\n' + '\n\n'.join(one(p5, k) for k in ['头一张撤离单', '背靠背', '九十九条'])]


def cont_job(name, base, cut_title):
    # 上一回停在 max_tokens：附上已经写出来的，从 cut_title 那一条起接着写
    jn, parts = base
    prev = open(os.path.join(OUT, '%s.md' % name), encoding='utf-8').read()
    prev = prev[:prev.index('## 迷宫纪·迷宫｜' + cut_title)]
    note = ('# 这一回是续写\n\n你上一回写这一份，写到「## 迷宫纪·迷宫｜%s」那一条中间用完了输出的长度，断了。'
            '已经写好的前几条附在最后，那几条不要重写，也不要再输出。这一回只输出两块：'
            '从「## 迷宫纪·迷宫｜%s」那一条起，把没写完的那一条和后面的条目写完（它是原稿的第五十二层的楼层主那一条，后面还有原稿最后一条白银海湾外的口子，照原稿的次序），'
            '再写「## 设计备注」，备注要管这一份的全部条目，包括已经写好的那几条。思考少用一些，留够输出。') % (cut_title, cut_title)
    return name + '_续', parts + [note, '# 你上一回已经写好的几条（不要再输出）\n\n' + prev]


REVIEW_SYS = '''你是审稿人，全程用中文。这一回审迷宫纪前传剧情铺开第一拨交回来的一份稿，只审不改，看不到仓库，材料都附在用户消息里了。

量这几样，逐条写，指到哪一条哪一处，引原文一处不超过二十字：
1. 层带：写到的每一处层号和地形，对不对得上底卡的层带条目（层带的样子、楼层主在第几层、安全区、位阶曲线、一层至多一位传奇残响、残响异界的规矩）。有没有写某一层塌了、断了。
2. 跟大纲第一版对不对得上：大敌线一页学会一样、沉灯会、渊染传奇、详略（给主持看的骨架）、超凡的表现力（高阶出手先写天地，不写凡人对砍）。
3. 跟同一拨别的份、跟光复第三稿、断门长桌第二稿对不对得上（人名、年份、地点、谁死在哪）。
4. 卡面：那一位有没有点名，表层有没有说井在吃什么、消化、胃，给作者看的话有没有漏进卡面，玩家在场有没有写成改不了。
5. 设计备注里给第二拨的账全不全：对照附上的这一页主线，有没有漏掉的层号和地形。
6. 好的地方也写一两句。

交一份 Markdown，从一级标题写起，末尾一节「要主会话改的」，一条一行，写清改哪条哪一处、改成什么。前后不加别的话。思考少用一些，先把稿子从头到尾过一遍就动笔，留够输出的长度。'''


def review_job(name):
    sub = open(os.path.join(OUT, '%s.md' % name), encoding='utf-8').read()
    pages = {'M0': [3, 4, 5], 'M1': [1, 2], 'M2': [3, 4], 'M3': [5, 6]}[name]
    orig = []
    if name != 'M0':
        for p in pages:
            orig.append('# 第%s页原来的迷宫条目\n\n' % CN[p - 1] + '\n'.join(entries(page_text(p), '迷宫纪·迷宫｜')))
    mains = ['# 第%s页的主线全文\n\n' % CN[p - 1] + open(os.path.join(MAT, 'p%d_主线.md' % p), encoding='utf-8').read() for p in pages]
    others = ['# 同一拨的 %s（对照用）\n\n' % o + open(os.path.join(OUT, '%s.md' % o), encoding='utf-8').read()
              for o in ['M0', 'M1', 'M2', 'M3'] if o != name]
    parts = ['# 你审的这一份：%s\n\n' % name + sub, '# 剧情大纲第一版\n\n' + rd('迷宫纪前传剧情大纲_第一版.md'),
             '# 底卡的层带条目\n\n' + card_entries([1019, 1022, 1055, 1099, 1100, 1101, 1102, 1103, 1104]),
             '# 光复第三稿\n\n' + open(os.path.join(SAMP, '样稿_光复_第三稿.md'), encoding='utf-8').read(),
             '# 断门长桌第二稿\n\n' + open(os.path.join(SAMP, '样稿_断门长桌_第二稿.md'), encoding='utf-8').read()] + orig + mains + others
    return '审_' + name, parts


WAVES = {
    12: lambda: [review_job(n) for n in ['M0', 'M1', 'M2', 'M3']],
    13: lambda: [review_job(n) for n in ['M1', 'M2']],
    14: lambda: [revise_job('M0', m0_job()), revise_job('M1', maze_job('M1', [1, 2])), revise_job('M2', maze_job('M2', [3, 4])), revise_job('M3', maze_job('M3', [5, 6]))],1: lambda: [m0_job(), maze_job('M1', [1, 2]), maze_job('M2', [3, 4]), maze_job('M3', [5, 6])],
         11: lambda: [cont_job('M2', maze_job('M2', [3, 4]), '第五十层的殿后者（深井')]}


REVISE_NOTE = '''# 这一回是改稿

你上一回交的这一份稿（附在后面）审过了。四份审稿意见都附上了（你这一份的在最前面，别的几份里提到你这一份的也要照改），还有主会话定的「定数_第一拨」，跟审稿意见冲突的以定数为准。

照审稿「要主会话改的」和定数逐条改，没提到的地方别动。改完照原来的格式把这一份整份重新输出，两块：头一块全部条目，第二块「## 设计备注」（照原来的备注改，开头加一节「改稿改了什么」，一条一行对着审稿和定数的条目号；给第二拨的账照审稿补全）。审稿里要用户拍板的，照定数定了的就照定数，定数没定的照审稿建议的那一条写，并在备注末尾列出来。思考少用一些，留够输出的长度。'''


def revise_job(name, base):
    jn, parts = base
    sub = open(os.path.join(OUT, '%s.md' % name), encoding='utf-8').read()
    revs = ['# 审稿：%s（你这一份）\n\n' % name + open(os.path.join(OUT, '审_%s.md' % name), encoding='utf-8').read()]
    revs += ['# 审稿：%s（别的份，提到你这一份的照改）\n\n' % o + open(os.path.join(OUT, '审_%s.md' % o), encoding='utf-8').read()
             for o in ['M0', 'M1', 'M2', 'M3'] if o != name]
    ding = open(os.path.join(WORK, '定数_第一拨.md'), encoding='utf-8').read()
    return name, parts + [REVISE_NOTE, '# 主会话定的\n\n' + ding, '# 你上一回交的稿\n\n' + sub] + revs


REVIEW_WAVES = {12, 13}
# 11-19 用户说额度放开用：写手 Fable 5.2，审稿 Opus 5.5（第一拨初稿是 Opus 写、Sonnet 审）
WRITER = 'claude-fable-5-2'
REVIEWER = 'claude-opus-5-5'


def build(w):
    rev = w in REVIEW_WAVES
    sysm = REVIEW_SYS if rev else system()
    reqs, names = [], []
    for name, parts in WAVES[w]():
        model = REVIEWER if rev else WRITER
        params = {'model': model, 'max_tokens': 128000, 'output_config': {'effort': 'high'},
                  'system': sysm, 'messages': [{'role': 'user', 'content': '\n\n'.join(parts)}]}
        if not model.startswith('claude-fable'):
            params['thinking'] = {'type': 'adaptive'}  # Fable 思考一直开着，不传
        reqs.append({'custom_id': 'w%d_%d' % (w, len(reqs)), 'params': params})
        names.append(name)
    return reqs, names


def bpath(w):
    return os.path.join(WORK, 'batch_%d.json' % w)


def submit(w):
    os.makedirs(OUT, exist_ok=True)
    reqs, names = build(w)
    for r, n in zip(reqs, names):
        print('%s：请求约 %d 字' % (n, len(r['params']['system']) + len(r['params']['messages'][0]['content'])))
    d = json.loads(rb.call(rb.API, {'requests': reqs}))
    json.dump({'id': d['id'], 'jobs': names, 'model': REVIEWER if w in REVIEW_WAVES else WRITER}, open(bpath(w), 'w', encoding='utf-8'), ensure_ascii=False)
    print('交上去了：', d['id'], d.get('processing_status'))


def status(w):
    b = json.load(open(bpath(w), encoding='utf-8'))
    d = json.loads(rb.call(rb.API + '/' + b['id']))
    print(d.get('processing_status'), d.get('request_counts'))
    return b, d


def fetch(b, d):
    out = rb.call(d['results_url'])
    tin = tout = 0
    for line in out.splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        name = b['jobs'][int(r['custom_id'].split('_')[1])]
        res = r['result']
        if res['type'] != 'succeeded':
            print('！%s 没成：%s' % (name, json.dumps(res, ensure_ascii=False)[:300]))
            continue
        msg = res['message']
        text = ''.join(c.get('text', '') for c in msg['content'] if c.get('type') == 'text')
        u = msg.get('usage', {})
        tin += u.get('input_tokens', 0)
        tout += u.get('output_tokens', 0)
        open(os.path.join(OUT, '%s.md' % name), 'w', encoding='utf-8').write(text.strip() + '\n')
        print('%s：%d 字，停在 %s，进 %d 出 %d' % (name, len(text), msg.get('stop_reason'), u.get('input_tokens', 0), u.get('output_tokens', 0)))
    pr = {'claude-fable-5-2': (8.0, 40.0), 'claude-opus-5-5': (4.0, 20.0), 'claude-sonnet-5-5': (2.0, 10.0)}[b.get('model', rb.MODEL)]
    print('合计进 %d、出 %d token（%s），批处理五折约 $%.2f' % (tin, tout, b.get('model', '?'), (tin * pr[0] + tout * pr[1]) / 1e6 / 2))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    cmd, w = sys.argv[1], int(sys.argv[2])
    if cmd == 'build':
        reqs, names = build(w)
        for r, n in zip(reqs, names):
            print(n, len(r['params']['system']), len(r['params']['messages'][0]['content']))
    elif cmd == 'submit':
        submit(w)
    elif cmd == 'status':
        status(w)
    elif cmd == 'wait':
        for _ in range(300):
            b, d = status(w)
            if d.get('processing_status') == 'ended':
                fetch(b, d)
                break
            time.sleep(60)
