# 卡面禁词与标点扫描：只看条目正文（## 月银纪·/纷争纪·/山铜纪·/迷宫纪· 起，到条目设置行），跳过设计备注
# 用法（在仓库根目录下）：python3 -I -X utf8 tools/cardscan.py 文件...
import sys, re
BAN_PUNCT = ['——', '—', '；', '…', '！', '...']
MOON = r'新月|满月|残月|月牙|弦月|月亮|月光|月相'
CN = r'时辰|节气|冬至|春分|守岁|碗筷|宜忌|汤屋|茶|祠|庙|龛|灶|长明灯|仪轨|会盟|诸侯|城主|管事|史馆|内侍|诏书|学塾|驿卒|官道|佃户|师门|长衫|袄|庄子|伙计|街坊|太爷爷|学宫|客栈|朝廷|门客|掌柜|百官|丫头|宗门|长老|功法|镖局|一丝|一抹|不禁|威压|修为|登记|军令|条例|晋升|量子|熵|坐标|频率|能量|系统|除籍|担山'
FORBID = r'厄洛伽|四执政'
def entries(s):
    for m in re.finditer(r'(?m)^## ((?:月银纪|纷争纪|山铜纪|迷宫纪)·.+)$', s):
        body = s[m.end():]
        k = body.find('\n> 条目设置')
        if k < 0:
            continue
        yield m.group(1), body[:k]
tot = 0
for f in sys.argv[1:]:
    s = open(f, encoding='utf-8').read().replace('\r', '')
    for title, body in entries(s):
        hits = []
        for p in BAN_PUNCT:
            if p in body:
                hits.append('标点' + p + '×%d' % body.count(p))
        for rx, tag in ((MOON, '月相'), (CN, '口径'), (FORBID, '禁名')):
            for mm in re.finditer(rx, body):
                ctx = body[max(0, mm.start()-12):mm.end()+12].replace('\n', ' ')
                hits.append('%s|%s|%s' % (tag, mm.group(), ctx))
        for mm in re.finditer(r'米', body):
            ctx = body[max(0, mm.start()-6):mm.end()+6]
            if not re.search(r'米亚赫|米罗妮|库米|米莉|米娅|米拉|米尔|米诺|米卡|埃米|米勒|米哈|米迦|米雅|米凯|米恩|米昂|阿米|塞米|米赫|米珂|萨米|德米|缪恩米洛', ctx):
                hits.append('口径|米|' + ctx.replace('\n', ' '))
        for line in body.split('\n'):
            t = line.strip()
            if not t or t.startswith('>'):
                continue
            core = re.sub(r'^[-*]\s*|\*\*', '', t)
            for mm in re.finditer('：', core):
                label = core[:mm.start()]
                if len(label) > 8 or '：' in core[mm.end():]:
                    hits.append('冒号|' + core[:40])
                    break
        for mm in re.finditer(r'「([^」]+)」', body):
            hits.append('引号「」|' + mm.group(1))
        if hits:
            tot += len(hits)
            print('==', f.split('/')[-1], '｜', title)
            for h in hits[:12]:
                print('   ', h)
print('合计', tot)
