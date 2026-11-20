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


MAIN_TASK = '''# 你的活

这一份是第二拨「主线」里的 {name}：重写迷宫纪前传第{page}页的 {n} 条主线（{lines}）。剧情大纲第一版第六节那张表里这几条各一行，写的是判定、对头、高潮挪到哪；分审意见里有改法方向、该留的几拍和毛病；照这三样写。

要守的：
1. 样子照用户认过的两条样稿（断门长桌第二稿、光复第三稿）：给主持看的骨架，每幕开头一句说这一幕要做成什么，下面五到八拍，一拍一两句，对头这一回出哪一手在拍里点明，对白一幕一两句要紧的，斗嘴吃饭点一句交给主持，默认收束一段话，玩家能改一条一两句。正文（开局到收束）三千字上下。
2. 每条一个有名有脸的对头出三回手，一回比一回狠，第三回是高潮里的正面交手；一半以上以打赢收，悲剧的也要先赢下一手。高潮是做出来的事，名字、碑、账、结案栏、一碗汤不当高潮，结案栏一页至多留一处。
3. 超凡的表现力照大纲第五节的位阶表：高阶出手先写天地和远处的人看见什么，再写招，正反两方一样，不写凡人对砍。凡人和低阶伙伴撑住、拽人、报方位、修东西。
4. 大迷宫照底卡的层带写，迷宫条目第一拨已经照层带重写了（附在后面，这是现行的），主线里的层号、地形、楼层主、安全区照它们改。第一拨的写手给你记了一本账（附在后面，那一页的设计备注里「给第二拨的账」），逐条照改。改了名的迷宫条目，主线里引用旧名的换成新名（改名表附在后面）。
5. 大敌线、沉灯会、渊染传奇照大纲第二节和补卷_84（附在后面，现行的）：这一页井底下那一位学会的那一手露在哪几条，沉灯会、渊染传奇在这几条里出手的地方照补卷_84 写，人名、年份对上。
6. 这一页的冒险团（附在后面）照大纲第三节进主线：跨两三条，先看见他们活着、笑着、斗嘴，再看见往后的事。
7. 第一拨定数（附在后面）照守。
8. 原稿的「## 迷宫纪·主线｜」标题、「题：」「章：」两行、「## 裁定锁」标题、条目设置那一行一个字不动。题诗的格式不许动。
9. 原稿立得住的几拍留着（分审「该留的几拍」）。前后对不上的地方照分审修。

交什么：输出两块，前后不加别的话。头一块是这 {n} 条主线的全文，一条一个「## 迷宫纪·主线｜」，从标题写到「> 条目设置：」那一行，次序照原稿。第二块从「## 设计备注」起：逐条写改了什么（对着分审）、对头三回出手各在哪一拍、新起的设定和名字（标★，请主会话查撞名）、这几条的旅伴条和人物条里要跟着改的（第三拨照它改）、要用户定的。
'''

MAIN_SHARES = [
    ('P1', 1, ['寻人', '第一次大迷宫潮', '头一回下井', '第三层的酒', '封井'], '审_探井.md', 'M1', ['补卷_77_冒险团_探井与共约.md']),
    ('P2', 2, ['一根绳', '叠好的装备', '头一车三币', '第二十层'], '审_共约.md', 'M1', ['补卷_77_冒险团_探井与共约.md']),
    ('P3a', 3, ['第七次大迷宫潮', '雷暴荒地的头一座塔', '屠林令', '头一回实习'], '审_繁荣.md', 'M2', ['补卷_78_冒险团_繁荣上.md', '补卷_79_冒险团_繁荣下.md', '补卷_72_比风更北.md']),
    ('P3b', 3, ['一座城自己的井', '三十七枚旧字', '外环那一条龙'], '审_繁荣.md', 'M2', ['补卷_78_冒险团_繁荣上.md', '补卷_79_冒险团_繁荣下.md']),
    ('P4a', 4, ['七重龙门', '第五十一层', '一段残响', '第五十六层的路标', '断崖'], '审_深井上.md', 'M2', ['补卷_80_冒险团_深井.md']),
    ('P4b', 4, ['七百个梦', '曜石审判', '两边的名单', '七日的锅'], '审_深井上.md|审_深井下.md', 'M2', ['补卷_80_冒险团_深井.md']),
    ('P4c', 4, ['没有门框的门', '第七次楼层主讨伐', '海墙', '一枚金币'], '审_深井下.md', 'M2', ['补卷_80_冒险团_深井.md']),
    ('P5a', 5, ['头一张撤离单', '头一回斩首', '白碑东门', '白碑第七夜', '背靠背'], '审_黑潮上.md', 'M3', ['补卷_81_冒险团_黑潮与垂暮.md']),
    ('P5b', 5, ['花雨', '九十九条', '坠龙航线'], '审_黑潮下.md', 'M3', ['补卷_81_冒险团_黑潮与垂暮.md']),
    ('P6', 6, ['空着的环', '无谬之城', '星形钥印'], '审_垂暮.md', 'M3', ['补卷_81_冒险团_黑潮与垂暮.md']),
]

P6_EXTRA = '''
另外这一份要新补两条主线（大纲第九节），写在原稿三条后头，标题照原稿的格式「## 迷宫纪·主线｜垂暮的年月·X」，题和章照原稿三条的格式起（题：奥尔德兰的旅印｜中部·第X章｜【X】，章：《X》｜一句），条目设置照原稿的写法起一个新的触发〔主线·垂暮的年月·X〕。约988年那一条写黑曜誓约照团章拒接一份要人牺牲的方案、自己找出另一条路，对头是署里写方案的人加上安全区里断手剩下还在动的一截东西；998到1000年那一条写交棒，剩下的几位老传奇和不灭之炎、黑曜誓约、日在中天这些新团头一回按在同一张单子上，新一辈自己打下来，收在1000年冬天井底下的光不对（十兆的头一道征兆）和门洞冬天比往年暖（只给 AI，归火的伏笔）。原稿三条的章名“地开以前的长夜”撞了，三条各换一个（题诗那一行格式不动，只换章名的字）。星形钥印卡面题作约定的钟点，标题照原稿不动。
'''


def main_job(name, page, lines, rev, mshare, teams):
    t = open(os.path.join(MAT, 'p%d_主线.md' % page), encoding='utf-8').read()
    secs = []
    for ln in lines:
        secs.append(sec(t, r'^## 迷宫纪·主线｜[^\n]*·' + re.escape(ln) + r'\s*$', r'^## 迷宫纪·主线｜'))
    revtxt = []
    for rf in rev.split('|'):
        r = open(os.path.join(ROOT, '底稿', '审稿', '迷宫纪前传', rf), encoding='utf-8').read()
        for blk in re.split(r'(?m)^(?=## )', r):
            h = blk.split('\n', 1)[0]
            if any(ln in h for ln in lines) or '共有的' in h:
                revtxt.append(blk)
    ms = open(os.path.join(OUT, '%s.md' % mshare), encoding='utf-8').read()
    ms_notes = ms[ms.index('## 设计备注'):]
    maze = '\n'.join(entries(page_text(page), '迷宫纪·迷宫｜'))
    tm = '\n\n'.join(rd('迷宫纪前传', '补卷', f) for f in teams)
    task = MAIN_TASK.format(name=name, page=CN[page - 1], n=len(lines), lines='、'.join(lines))
    if name == 'P6':
        task += P6_EXTRA
    return name, [task, '# 剧情大纲第一版\n\n' + rd('迷宫纪前传剧情大纲_第一版.md'),
                  '# 断门长桌第二稿（用户认过的样子）\n\n' + open(os.path.join(SAMP, '样稿_断门长桌_第二稿.md'), encoding='utf-8').read(),
                  '# 光复第三稿（用户认过的样子）\n\n' + open(os.path.join(SAMP, '样稿_光复_第三稿.md'), encoding='utf-8').read(),
                  '# 底卡的层带条目\n\n' + card_entries([1019, 1022, 1055, 1099, 1100, 1101, 1102, 1103, 1104]),
                  '# 第一拨定数\n\n' + open(os.path.join(WORK, '定数_第一拨.md'), encoding='utf-8').read(),
                  '# 迷宫条目改名表（旧名、新名）\n\n' + open(os.path.join(WORK, '改名_第一拨.tsv'), encoding='utf-8').read(),
                  '# 补卷_84 大敌线与沉灯会（现行）\n\n' + rd('迷宫纪前传', '补卷', '补卷_84_大敌线与沉灯会.md'),
                  '# 这一页的页头和时段总纲\n\n' + open(os.path.join(MAT, 'p%d_页头与总纲.md' % page), encoding='utf-8').read(),
                  '# 这一页现行的迷宫条目（第一拨重写过）\n\n' + maze,
                  '# 第一拨 %s 的设计备注（里头有给第二拨的账）\n\n' % mshare + ms_notes,
                  '# 这一页的冒险团\n\n' + tm,
                  '# 这几条的分审意见\n\n' + '\n'.join(revtxt),
                  '# 原稿主线（要重写的这几条）\n\n' + '\n'.join(secs)]


REVIEW2_SYS = '''你是审稿人，全程用中文。这一回审迷宫纪前传剧情铺开第二拨交回来的一份主线稿，只审不改，看不到仓库，材料都附在用户消息里了。

这一轮的尺子是用户认过的两条样稿（断门长桌第二稿、光复第三稿）和剧情大纲第一版。逐条主线量下面几样，指到哪一幕哪一拍，引原文一处不超过二十字：
1. 对头：有名有脸、出三回手、一回比一回狠，第三回是高潮里的正面交手。是不是以打赢收（悲剧的先赢下一手）。高潮是不是做出来的事，有没有又收在名字、碑、账、结案栏、一碗汤上。
2. 超凡的表现力：英雄、传奇、两个王、魔神将、真龙出手，有没有先写天地和远处的人看见什么；有没有写成凡人对砍（“一刀一刀”“打了几十下”）。位阶对不对。
3. 详略：是不是给主持看的骨架（每幕五到八拍、一拍一两句、对白一幕一两句），有没有又铺成小说，或者反过来只剩提纲看不出戏。
4. 层带：层号、地形、楼层主、安全区对不对得上附上的底卡层带条目和第一拨重写的迷宫条目，引用的迷宫条目名是不是新名。
5. 大敌线、沉灯会、渊染传奇：跟大纲和补卷_84 对不对得上（人名、年份、这一页它学会的那一手）。冒险团进没进主线，有没有先看见他们活着。
6. 王道 JRPG 的那几样：伙伴的日常和斗嘴、成长、热血、轻喜剧、情义，落了几样。
7. 卡面：那一位有没有点名，表层有没有说井在吃什么，给作者看的话有没有漏进卡面，玩家能改有没有写成改不了，标题、题、章、条目设置有没有被改。
8. 跟原稿和分审比：该留的几拍留没留，前后对不上的修没修，有没有改出新的前后不搭。
9. 好的地方也写。

每条主线一节，末尾一节「要写手改的」，一条一行，写清改哪条哪一拍、改成什么样。前后不加别的话。思考少用一些，留够输出。'''


def review2_job(name, page, lines, rev, mshare, teams):
    jn, parts = main_job(name, page, lines, rev, mshare, teams)
    sub = open(os.path.join(OUT, '%s.md' % name), encoding='utf-8').read()
    return '审_' + name, ['# 你审的这一份：%s（第%s页，%s）\n\n' % (name, CN[page - 1], '、'.join(lines)) + sub] + parts[1:]


def revise2_job(name, page, lines, rev, mshare, teams):
    jn, parts = main_job(name, page, lines, rev, mshare, teams)
    sub = open(os.path.join(OUT, '%s.md' % name), encoding='utf-8').read()
    r = open(os.path.join(OUT, '审_%s.md' % name), encoding='utf-8').read()
    note = ('# 这一回是改稿\n\n你上一回交的这一份（附在后面）审过了，审稿意见附在后面。照「要写手改的」逐条改，'
            '审稿说好的、没提到的地方别动。改完照原来的格式整份重新输出两块，第二块设计备注开头加一节「改稿改了什么」，一条一行对着审稿的条目。'
            '审稿跟大纲、样稿、定数冲突的，以大纲、样稿、定数为准，在备注里写一句。')
    return name, parts + [note, '# 你上一回交的稿\n\n' + sub, '# 审稿意见\n\n' + r]


FIX_TASK = '''# 你的活

这一份是第三拨「跟着改的」里的 {name}：迷宫纪前传第{page}页的主线（第二拨）和迷宫条目（第一拨）已经照剧情大纲第一版重写完、拼进页里了（整页现行文本附在后面）。这一页别的条目（页头和委托凭证、时段总纲、旅伴条和旅伴背景、这一段旅伴之间、人物条、凡世至强条、案子、地点、公告板、命星的说明文字）里，有些地方跟新主线、新迷宫条目对不上了。你把它们找出来改掉。

先看第二拨各份设计备注里「要跟着改的（第三拨）」那几节和第一拨的设计备注（附在后面），那是写手记下的账，逐条照改；再自己通读整页，账上没记、你看出来对不上的也改：谁的下场变了（活下来了、死在别处、换了对手），哪一年的事挪了层带或者换了地方，引用了改了名的迷宫条目（改名表附在后面），引用主线里删掉的拍子，旅伴的初见、关系、正史里的下场、好感增减、裁定锁、年份黑名单跟主线对不上。

不动的：主线（## 迷宫纪·主线｜那几条）和迷宫条目（## 迷宫纪·迷宫｜那几条）这一回不改；每一条的标题一字不改；条目设置那一行只改触发里要跟着改的名字和黑名单年份；固定锁定、身份、底座、体态数据、### 星标题这些受保护的行不动，非改不可的在备注里写明。命星（## 星 下面那些 ### 星条）这一回不改，只在备注里记要改的。

新补的主线（第六页的第七条、最后一扇门）要是碰得上的人里点了旅伴而页上没有这个人的旅伴条，照这一页旅伴条的格式补写，一人一条加一条背景，放在你交的稿子末尾。第六页的页头和委托凭证里要把这两条登记进去（照原来三条的写法）。

卡面的规矩照写作口径：标点、禁词、那一位不点名、表层不说井在吃什么、玩家在场能改、容貌口径、台词照 genshin-dialogue-voice。改的地方照原条目的口气，别整条重写成另一个样子，改到对得上为止。

交什么：输出两块，前后不加别的话。头一块是改了的条目，每条从「## 标题」那一行写到它的「> 条目设置：」那一行（标题跟原来一字不差，主会话照标题换回去），没改的条目不输出；补写的新条目放在最后。第二块从「## 设计备注」起：逐条写改了什么、对着哪一笔账；命星要改的；拿不准的、要用户定的。
'''

SUPP_TASK = '''# 你的活

这一份是第三拨「跟着改的」里的 C7：迷宫纪前传六页的主线和迷宫条目已经照剧情大纲第一版重写完。前传补卷、委托第一版里有些条目跟着对不上了，附在后面的是要查的这几份的全文。你把对不上的地方改掉：

1. 引用了改了名的迷宫条目的（改名表附在后面），换成新名，引用的内容跟着新条目改。
2. 史诗战对手（补卷_55）里各页楼层主、潮头、对手的阶段名号和打法，照新主线和新迷宫条目改：前传各条主线新起的对头和潮头要是该进史诗战对手的，照补卷_55 的格式补进去。名号照底卡楼层主的名号口径（逗号连的名词短语）。
3. 冒险团（补卷_72、_77 到 _81）：主线里写了冒险团哪一年在哪、跟谁斗嘴、谁死在哪，冒险团条目里对不上的照主线改，人物的长相、年份、名字不动。
4. 支线（补卷_22、_65、_66）、第一项的常驻与纪元钟、势力与地点、委托第一版：跟新主线、新迷宫条目、补卷_84 对不上的地方改掉。纪元钟里写到的层号和事照新的走。
5. 卡面规矩照写作口径。

不动的：每条的标题一字不改，条目设置只改触发里要跟着改的名字，受保护的行不动。

交什么：输出两块。头一块是改了的条目，标注它在哪一份文件里：每条前面单起一行「〔文件：补卷_55_史诗战对手.md〕」，下面从「## 标题」写到「> 条目设置：」（委托第一版里的委托张不是这个格式的，照原来的格式整张输出，前面一样标文件）；新补的条目也这样标。没改的不输出。第二块「## 设计备注」：逐条写改了什么、拿不准的。
'''

FIX_PAGES = [(1, ['P1'], 'M1'), (2, ['P2'], 'M1'), (3, ['P3a', 'P3b'], 'M2'), (4, ['P4a', 'P4b', 'P4c'], 'M2'), (5, ['P5a', 'P5b'], 'M3'), (6, ['P6'], 'M3')]


def notes_of(name):
    t = open(os.path.join(OUT, '%s.md' % name), encoding='utf-8').read()
    return t[t.index('## 设计备注'):] if '## 设计备注' in t else ''


def fix_job(page, pshares, mshare):
    name = 'C%d' % page
    base = [FIX_TASK.format(name=name, page=CN[page - 1]),
            '# 剧情大纲第一版\n\n' + rd('迷宫纪前传剧情大纲_第一版.md'),
            '# 第一拨定数\n\n' + open(os.path.join(WORK, '定数_第一拨.md'), encoding='utf-8').read(),
            '# 迷宫条目改名表（旧名、新名）\n\n' + open(os.path.join(WORK, '改名_第一拨.tsv'), encoding='utf-8').read(),
            '# 补卷_84 大敌线与沉灯会（现行）\n\n' + rd('迷宫纪前传', '补卷', '补卷_84_大敌线与沉灯会.md'),
            '# 底卡的层带条目\n\n' + card_entries([1099, 1100, 1101])]
    base += ['# 第二拨 %s 的设计备注\n\n' % p + notes_of(p) for p in pshares]
    if page == 1:
        base.append('# 断门长桌第二稿的设计备注\n\n' + open(os.path.join(SAMP, '样稿_断门长桌_第二稿.md'), encoding='utf-8').read().split('## 设计备注', 1)[1])
    if page == 5:
        base.append('# 光复第三稿的设计备注\n\n' + open(os.path.join(SAMP, '样稿_光复_第三稿.md'), encoding='utf-8').read().split('## 设计备注', 1)[1])
    base.append('# 第一拨 %s 的设计备注\n\n' % mshare + notes_of(mshare))
    base.append('# 第%s页整页现行文本\n\n' % CN[page - 1] + page_text(page))
    return name, base


SUPP_FILES = ['补卷_55_史诗战对手.md', '补卷_72_比风更北.md', '补卷_77_冒险团_探井与共约.md', '补卷_78_冒险团_繁荣上.md', '补卷_79_冒险团_繁荣下.md',
              '补卷_80_冒险团_深井.md', '补卷_81_冒险团_黑潮与垂暮.md', '补卷_22_支线聚落.md', '补卷_65_支线_探井与共约的传奇.md',
              '补卷_66_支线_繁荣的传奇.md', '第一项_常驻与纪元钟.md', '第一项_势力与地点.md']


def supp_job():
    base = [SUPP_TASK, '# 剧情大纲第一版\n\n' + rd('迷宫纪前传剧情大纲_第一版.md'),
            '# 第一拨定数\n\n' + open(os.path.join(WORK, '定数_第一拨.md'), encoding='utf-8').read(),
            '# 迷宫条目改名表\n\n' + open(os.path.join(WORK, '改名_第一拨.tsv'), encoding='utf-8').read(),
            '# 补卷_84（现行）\n\n' + rd('迷宫纪前传', '补卷', '补卷_84_大敌线与沉灯会.md'),
            '# 底卡楼层主的名号口径和层带\n\n' + card_entries([1099])]
    for p in range(1, 7):
        t = page_text(p)
        ms = [s for s in re.split(r'(?m)^(?=## )', t) if s.startswith('## 迷宫纪·主线｜') or s.startswith('## 迷宫纪·迷宫｜')]
        base.append('# 第%s页现行的主线和迷宫条目\n\n' % CN[p - 1] + ''.join(ms))
    for f in SUPP_FILES:
        base.append('# 〔文件：%s〕全文\n\n' % f + rd('迷宫纪前传', '补卷', f))
    base.append('# 〔文件：迷宫纪前传_委托_第一版.md〕全文\n\n' + rd('迷宫纪前传', '迷宫纪前传_委托_第一版.md'))
    return 'C7', base


CONT3_NOTE = ('# 这一回是续写\n\n你上一回交这一份，写到一半用完了输出的长度，断了。已经写出来的附在最后，那些条不要再输出。'
              '这一回接着把还没写的条写完（账上要改的、你通读看出来的、要补写的新条），最后写「## 设计备注」，备注管这一份全部的条，包括上一回写好的。'
              '格式跟上一回一样。少想一些，直接写，留够输出的长度；一条改的地方不多的，照原条整条抄出来、只改那几处，别重新铺。')


def cont3_job(name, base):
    jn, parts = base
    prev = open(os.path.join(OUT, '%s.md' % name), encoding='utf-8').read()
    k = prev.rfind('\n> 条目设置：')
    prev = prev[:prev.index('\n', k + 1) + 1] if k >= 0 else prev
    open(os.path.join(OUT, '%s_上.md' % name), 'w', encoding='utf-8').write(prev)
    return name + '_续', parts + [CONT3_NOTE, '# 你上一回已经写好的（不要再输出）\n\n' + prev]


EFFORT = {31: 'medium'}

WAVES2 = {2: lambda: [main_job(*s) for s in MAIN_SHARES],
          31: lambda: [cont3_job('C%d' % s[0], fix_job(*s)) for s in FIX_PAGES if s[0] in (1, 2, 6)] + [cont3_job('C7', supp_job())],
          3: lambda: [fix_job(*s) for s in FIX_PAGES] + [supp_job()],
          21: lambda: [review2_job(*s) for s in MAIN_SHARES],
          22: lambda: [revise2_job(*s) for s in MAIN_SHARES]}

REVIEW_WAVES = {12, 13, 21}
# 11-19 用户说额度放开用：写手 Fable 5.2，审稿 Opus 5.5（第一拨初稿是 Opus 写、Sonnet 审）
WRITER = 'claude-fable-5-2'
REVIEWER = 'claude-opus-5-5'


def build(w):
    WAVES.update(WAVES2)
    rev = w in REVIEW_WAVES
    sysm = (REVIEW2_SYS if w == 21 else REVIEW_SYS) if rev else system()
    reqs, names = [], []
    for name, parts in WAVES[w]():
        model = REVIEWER if rev else WRITER
        params = {'model': model, 'max_tokens': 128000, 'output_config': {'effort': EFFORT.get(w, 'high')},
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
