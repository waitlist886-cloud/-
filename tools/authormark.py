# 卡面里漏进去的给作者看的话：出处括号、版本说明、分工的叫法
# 只看有「> 条目设置」的条目正文（## 标题到条目设置那一行），设计备注、传奇表这一类不进卡的节跳过
# 用法（在仓库根目录下）：python3 -I -X utf8 tools/authormark.py 文件...
import sys, re
PAT = re.compile(r'（(?:碑第一版|台词试稿|方向稿|方向与写法|计划|主会话|[A-IＡ-Ｉ一二三四五六七八九十]份|照计划|设计备注)'
                 r'|主会话|碑第一版|台词试稿|照计划|计划第|见设计备注|设计备注里|这一稿|交稿|拼页|等你拍板|[A-I]份')
SKIP = re.compile(r'^## (?:设计备注|这一份的设计备注|这一段的传奇表|这一代的命星)')
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
        if hits:
            tot += len(hits)
            print('==', f.split('/')[-1], '｜', m.group(0)[3:40])
            for h in hits[:8]:
                print('   ', h)
print('合计', tot)
