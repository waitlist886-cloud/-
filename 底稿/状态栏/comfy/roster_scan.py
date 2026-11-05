#!/usr/bin/env python3
# 立绘铺开（11-05）：从各纪的页上抽要画的人，写 底稿/立绘/名册.json 和 名册.md。
# 抽三样：旅伴条（## 旅途同行：名（纪·主线名）），凡世至强条（## 凡世至强：名号 · 名（…）），人物条（## …（人物），一条里常写好几个人，列出条目和行号，交给写资料的人自己分）。
# 一纪一个时代往前排：迷宫纪前传 → 山铜纪 → 纷争纪 → 萨尔维斯 → 诸国期 → 月银纪史诗；页里倒着排（往前铺）。
#   python roster_scan.py <仓库根>
import json
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
ERAS = [
    ('前传', '迷宫纪前传', '迷宫纪前传时段_', ['六', '五', '四', '三', '二', '一']),
    ('山铜纪', '山铜纪', '山铜纪时段_', ['六', '五', '四', '三', '二', '一']),
    ('纷争纪', '纷争纪', '纷争纪时段_', ['七', '六', '五', '四', '三', '二', '一']),
    ('萨尔维斯', '萨尔维斯', '萨尔维斯时段_', ['六', '五', '四', '三', '二', '一']),
    ('诸国期', '诸国期', '诸国期时段_', ['六', '五', '四', '三', '二', '一']),
    ('月银纪史诗', '月银纪史诗', '第', ['十五', '十四', '十三', '十二', '十一', '十', '九', '八', '七', '六', '五', '四', '三', '二', '一']),
]
FIELDS = ('固定锚定', '外貌', '容貌评价', '体态数据', '装束', '仪容与印象', '底座', '位阶与职责')


def page_files(folder, prefix, order):
    names = sorted(os.listdir(os.path.join(ROOT, folder)))
    out = []
    for o in order:
        hit = [n for n in names if n.startswith(prefix + o + '_') and n.endswith('.md')]
        if prefix == '第':
            hit = [n for n in names if n.startswith('第' + o + '歌_') and n.endswith('.md')]
        out += hit[:1]
    return out


def field(lines, name):
    for l in lines:
        m = re.match(r'(?:\*\*)?' + name + r'(?:[｜：:])(.*)', l)
        if m:
            return m.group(1).strip().strip('*')[:600]
    return ''


rows = []
for era, folder, prefix, order in ERAS:
    for fn in page_files(folder, prefix, order):
        path = os.path.join(ROOT, folder, fn)
        L = open(path, encoding='utf-8').read().split('\n')
        heads = [i for i, l in enumerate(L) if l.startswith('## ')]
        for n, i in enumerate(heads):
            h = L[i][3:].strip()
            j = heads[n + 1] if n + 1 < len(heads) else len(L)
            body = L[i + 1:j]
            kind = name = None
            m = re.match(r'旅途同行：(.+?)（(.+?)）$', h)
            if m and '背景' not in h:
                kind, name = '旅伴', m.group(1)
            elif h.startswith('凡世至强'):
                kind = '凡世至强'
                m = re.search(r'·\s*([^·（]+?)(?:（|$)', h)
                name = m.group(1).strip() if m else h
            elif h.endswith('（人物）'):
                kind, name = '人物', h[:-4]
            if not kind:
                continue
            r = {'era': era, 'page': os.path.join(folder, fn).replace('\\', '/'), 'kind': kind, 'name': name, 'head': h, 'lines': [i + 1, j]}
            for f in FIELDS:
                v = field(body, f)
                if v:
                    r[f] = v
            if kind == '人物':   # 条里一行一个人的写法：- 名｜…
                r['bullets'] = [re.split(r'[｜]', l[2:], 1)[0][:30] for l in body if l.startswith('- ') and '｜' in l[:40]]
            rows.append(r)

D = os.path.join(ROOT, '底稿', '立绘')
os.makedirs(D, exist_ok=True)
json.dump(rows, open(os.path.join(D, '名册.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# 摘要：一纪一节，一页一行数
out = ['# 立绘铺开名册（roster_scan.py 抽的，11-05）', '', '旅伴、凡世至强一条一个人；人物条一条里常写好几个人，后头列着条里“- 名｜”那几行的名字，写资料的时候自己分。', '']
for era, *_ in ERAS:
    er = [r for r in rows if r['era'] == era]
    pages = []
    for r in er:
        if r['page'] not in pages:
            pages.append(r['page'])
    out.append('## %s（旅伴 %d，凡世至强 %d，人物条 %d）' % (era, sum(r['kind'] == '旅伴' for r in er), sum(r['kind'] == '凡世至强' for r in er), sum(r['kind'] == '人物' for r in er)))
    out.append('')
    for p in pages:
        pr = [r for r in er if r['page'] == p]
        out.append('- %s：旅伴 %s；凡世至强 %s；人物条 %d 条' % (os.path.basename(p)[:-3], '、'.join(r['name'] for r in pr if r['kind'] == '旅伴') or '无', '、'.join(r['name'] for r in pr if r['kind'] == '凡世至强') or '无', sum(r['kind'] == '人物' for r in pr)))
    out.append('')
open(os.path.join(D, '名册.md'), 'w', encoding='utf-8').write('\n'.join(out))
print(len(rows), 'rows')
for era, *_ in ERAS:
    er = [r for r in rows if r['era'] == era]
    names = {r['name'] for r in er if r['kind'] != '人物'}
    print(era, '旅伴', sum(r['kind'] == '旅伴' for r in er), '凡世至强', sum(r['kind'] == '凡世至强' for r in er), '人物条', sum(r['kind'] == '人物' for r in er), '人物条里的人', sum(len(r.get('bullets', [])) for r in er), '不同名字（旅伴加凡世至强）', len(names))
