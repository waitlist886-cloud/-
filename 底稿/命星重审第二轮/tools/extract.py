#!/usr/bin/env python3
# 命星重审第二轮（11-19 夜）：从四纪拼好的页里抽材料，一页一份，给 API 批处理喂进去。
#   python -I -X utf8 底稿/命星重审第二轮/tools/extract.py
# 写 底稿/命星重审第二轮/材料/筛_<页>.md（每位旅伴：旅伴条、背景条、能力行里那两颗生来的星的星条）
#    和 材料/rare_<页>.md（这一页每门 Rare 技艺的星条，前面带持有人的身份行和能力行）。
# 另写 材料/索引.json：页 → 文件、旅伴名单、Rare 名单。活到 1001 年、底卡里有真名的俗称（门面 star_true.json）标出来。
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
OUT = os.path.join(ROOT, '底稿', '命星重审第二轮', '材料')
GROUPS = [('月银纪', '月银纪史诗/第*歌*.md'), ('诸国期', '诸国期/诸国期时段_*.md'), ('萨尔维斯', '萨尔维斯/萨尔维斯时段_*.md'),
          ('纷争纪', '纷争纪/纷争纪时段_*.md'), ('山铜纪', '山铜纪/山铜纪时段_*.md'), ('迷宫纪前传', '迷宫纪前传/迷宫纪前传时段_*.md')]
CN = '一二三四五六七八九十'
STAR = re.compile(r'^### (\S+) \((Special|Passive|Art) \| (\w+)\)\n.*?(?=^### |^## |\Z)', re.S | re.M)


def order(f):
    b = os.path.basename(f)
    m = re.search(r'第([一二三四五六七八九十]+)歌', b) or re.search(r'时段_([一二三四五六七])', b)
    s = m.group(1)
    if len(s) == 1:
        return CN.index(s) + 1
    return 10 + (CN.index(s[1]) + 1 if s[0] == '十' else 0)


def blocks(t):
    """## 起的条目：标题 → 全文（到下一个不是裁定锁的 ## 为止）。"""
    out = []
    for m in re.finditer(r'(?m)^## (?!裁定锁)', t):
        out.append(m.start())
    res = []
    for i, s in enumerate(out):
        e = out[i + 1] if i + 1 < len(out) else len(t)
        res.append(t[s:e].rstrip() + '\n')
    return res


NL = chr(10)
KEEP = ('【调用】', '固定锚定', '类别：', '身份：', '底座：', '位阶走势', '能力：', '初见：')


def trim(c):
    """筛表用不着声口、好感、装束、体态：留调用、锚定、身份、底座、走势、能力、初见、正史里的下场、背景条正文。"""
    out, take = [], False
    lines = c.split(NL)
    out.append(lines[0])
    for l in lines[1:]:
        s = l.strip()
        if s.startswith('### 正史里的下场'):
            take = True
            out.append(l)
            continue
        if s.startswith('### ') or s.startswith('【') and not s.startswith('【调用】'):
            take = False
        if s.startswith('> 条目设置'):
            continue
        if take or s.startswith(KEEP) or (c.startswith('## 旅途同行·背景') and not s.startswith('>')):
            out.append(l)
    return NL.join(x for x in out if x.strip()) + NL


def main():
    os.makedirs(OUT, exist_ok=True)
    true = json.load(open(os.path.join(ROOT, '底稿', '门面', '共用', 'data', 'star_true.json'), encoding='utf-8'))
    keep = {s['n']: s['tn'] for s in true['stars']}
    index = {}
    for era, pat in GROUPS:
        for f in sorted(glob.glob(os.path.join(ROOT, pat)), key=order):
            t = open(f, encoding='utf-8').read().replace('\r\n', '\n')
            stars = {}
            for m in STAR.finditer(t):
                stars.setdefault((m.group(1), m.group(2)), m.group(0).rstrip() + '\n')
            bl = blocks(t)
            cast = [b for b in bl if b.startswith('## 旅途同行：')]
            bgs = [b for b in bl if b.startswith('## 旅途同行·背景：')]
            key = '%s_%02d' % (era, order(f))
            parts, names, rares = [], [], []
            holder = {}
            for c in cast:
                name = re.match(r'## 旅途同行：([^（\n]+)', c).group(1).strip()
                short = name.split('·')[0]
                ab = re.search(r'^能力：(.*)$', c, re.M)
                ab = ab.group(1) if ab else ''
                ident = re.search(r'^身份：(.*)$', c, re.M)
                for kind, nm, tier in re.findall(r'(Special|Passive|Art)【([^】]+)】\((\w+)', ab):
                    if kind == 'Art' and tier == 'Rare':
                        holder.setdefault(nm, []).append('持有人：%s｜身份：%s｜能力：%s' % (name, ident.group(1) if ident else '', ab))
                gen = [(k, n, ti) for k, n, ti in re.findall(r'(Special|Passive)【([^】]+)】\((\w+)', ab)]
                if not gen:
                    continue
                names.append(name)
                bg = [b for b in bgs if re.match(r'## 旅途同行·背景：' + re.escape(short), b)]
                seg = ['=' * 20, '【旅伴】%s' % name]
                locked = ['%s→%s' % (n, keep[n]) for _, n, _ in gen if n in keep]
                if locked:
                    seg.append('【真名层，名字和档都不动，只看写法】' + '、'.join(locked))
                seg.append(trim(c))
                seg += [trim(b) for b in bg]
                for k, n, ti in gen:
                    s = stars.get((n, k))
                    seg.append(s if s else '（这一页没有【%s】的星条，能力行里那一句就是全部）\n' % n)
                parts.append('\n'.join(seg))
            for (n, k), s in stars.items():
                if k == 'Art' and re.match(r'### \S+ \(Art \| Rare\)', s):
                    rares.append(n)
            if names:
                open(os.path.join(OUT, '筛_%s.md' % key), 'w', encoding='utf-8', newline='\n').write(
                    '# %s 第%s%s：旅伴 %d 位\n\n' % (era, order(f), '歌' if era == '月银纪' else '页', len(names)) + '\n\n'.join(parts))
            if rares:
                rp = []
                for n in rares:
                    rp.append('=' * 20)
                    rp += holder.get(n, ['持有人：（能力行里找不到，看星条正文）'])
                    rp.append(stars[(n, 'Art')])
                open(os.path.join(OUT, 'rare_%s.md' % key), 'w', encoding='utf-8', newline='\n').write(
                    '# %s 第%s%s：Rare 技艺 %d 门\n\n' % (era, order(f), '歌' if era == '月银纪' else '页', len(rares)) + '\n'.join(rp))
            index[key] = {'file': os.path.relpath(f, ROOT).replace('\\', '/'), 'cast': names, 'rare': rares}
            print('%-10s %-40s 旅伴 %3d  Rare %3d' % (key, os.path.basename(f), len(names), len(rares)))
    json.dump(index, open(os.path.join(OUT, '索引.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('合计 旅伴', sum(len(v['cast']) for v in index.values()), 'Rare', sum(len(v['rare']) for v in index.values()))


if __name__ == '__main__':
    main()
