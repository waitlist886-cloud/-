# 卡面里漏进去的给作者看的话：出处括号、版本说明、分工的叫法
# 只看有「> 条目设置」的条目正文（## 标题到条目设置那一行），设计备注、传奇表这一类不进卡的节跳过
# 用法（在仓库根目录下）：python3 -I -X utf8 tools/authormark.py 文件...
import sys, re
PAT = re.compile(r'（(?:碑第一版|台词试稿|方向稿|方向与写法|计划|主会话|[A-IＡ-Ｉ一二三四五六七八九十]份|照计划|设计备注)'
                 r'|主会话|碑第一版|台词试稿|照计划|计划第|见设计备注|设计备注里|这一稿|交稿|拼页|等你拍板|[A-I]份')
SKIP = re.compile(r'^## (?:设计备注|这一份的设计备注|这一段的传奇表|这一代的命星)')
# 照打包脚本 build_moon_v8.py 的 strip_marks 先去掉作者记号，再看剩下的括号
AUTHOR_MARK = re.compile(r'（[★#][^）]*）')
AUTHOR_TAIL = re.compile(r'（([^（）]*?)[，、]\s*★）')
AUTHORISH = re.compile(r'(?:页[一二三四五六七八九十]|第[一二三四五六七八九十]+[页歌份]|歌|[^（）]*的年月|介绍页|碑第一版|台词试稿|总表[^（）]*|方向[^（）]*|计划[^（）]*|接?底卡[^（）]*|[^（）]*#\d[^（）]*)')
def _tail(m):
    inner = m.group(1).strip()
    if not inner or AUTHORISH.fullmatch(inner):
        return ''
    return '（' + inner + '）'
PAGE_REF = re.compile(r'（(?:(?:页[一二三四五六七八九十]+|第[一二三四五六七八九十]+[页歌](?:第\d+行)?|总表|介绍页)[、，]?)+）')
def strip_marks(t):
    t = AUTHOR_TAIL.sub(_tail, t)
    t = PAGE_REF.sub('', t)
    return AUTHOR_MARK.sub('', t).replace('★', '')
# 去掉记号以后还留在卡面上的出处括号：页名、介绍页、碑和纷争纪条目的简写、空括号、多出来的逗号
LEAK = re.compile(r'（(?:介绍页|[^（）]*的年月|碑[^（）·｜]*|纷争纪[^（）·][^（）]*那一[条段]|页[一二三四五六七八九十]|第[一二三四五六七八九十]+页|总表[^（）]*|底卡[^（）]*)）|（[^（）]*[，、]）|（）')
# 山铜纪的文件里，带不带照字，指到纷争纪条目的都算跨纪
# 山铜纪的局里纷争纪的条目醒不了，指过去的话要么删，要么把那一句事实写进句子
CROSS = re.compile(r'(?:照|（)纷争纪·[^，。（）]*?那一[条段]')
tot = 0
for f in sys.argv[1:]:
    s = open(f, encoding='utf-8').read().replace('\r', '')
    heads = [m for m in re.finditer(r'(?m)^## .+$', s)]
    for i, m in enumerate(heads):
        if SKIP.match(m.group(0)):
            continue
        end = heads[i+1].start() if i+1 < len(heads) else len(s)
        body = s[m.end():end]
        k = body.find('\n> 条目设置')
        if k < 0:
            continue
        body = body[:k]
        hits = [body[max(0, mm.start()-14):mm.end()+10].replace('\n', ' ') for mm in PAT.finditer(body)]
        clean = strip_marks(body)
        # 规则条里「2到300年（犁的年月）」这一类拿页名当时段名的标签不算
        hits += ['漏|' + clean[max(0, mm.start()-14):mm.end()+4].replace('\n', ' ') for mm in LEAK.finditer(clean)
                 if not (clean[max(0, mm.start()-1):mm.start()] == '年' and mm.group().endswith('的年月）'))]
        if '山铜纪' in f:
            hits += ['跨纪|' + clean[max(0, mm.start()-8):mm.end()+4].replace('\n', ' ') for mm in CROSS.finditer(clean)]
        if hits:
            tot += len(hits)
            print('==', f.split('/')[-1], '｜', m.group(0)[3:40])
            for h in hits[:8]:
                print('   ', h)
print('合计', tot)
