# -*- coding: utf-8 -*-
"""铺开·自查。在活的文件夹里跑：python -I -X utf8 自查.py
拿 稿/ 对 原/ 和 任务.json。印出「错」（一定要改）和「看」（请看一眼，对的就留着）。错是 0 才能交。
主会话收稿也跑这一支：python -I -X utf8 自查.py <活的文件夹>
"""
import io, os, re, sys, json, difflib, subprocess, collections

HERE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else os.path.dirname(os.path.abspath(__file__))
REPO = 'E:/aldran_art'
STAR = re.compile(r'^### (.+?) \((Art)\s*\|\s*(\w+)\)\s*$')
COMP = re.compile(r'^## 旅途同行：(.+?)(?:（.*)?$')
BACK = re.compile(r'^## 旅途同行·背景：(.+?)\s*$')
TIERS = ('共鸣', '灵格', '极境', '英雄', '传奇')
BANP = ['——', '—', '；', '…', '！', '...', '!']
MOON = ['新月', '满月', '残月', '月牙', '弦月', '月亮', '月光']
BANW = ['学宫', '客栈', '朝廷', '门客', '时辰', '掌柜', '百官', '丫头', '宗门', '长老', '功法', '镖局', '一丝', '一抹', '不禁',
        '威压', '修为', '登记', '军令', '条例', '晋升', '量子', '坐标', '频率', '能量', '系统', '师父', '徒弟', '爹', '江湖', '内力',
        '伙计', '街坊', '灶', '晌午', '汉子', '媳妇', '闺女', '规则', '概念', '法则', '因果']
errs, looks = [], []


def E(s):
    errs.append(s)


def W(s):
    looks.append(s)


def rl(p):
    return [x.rstrip('\r') for x in io.open(p, encoding='utf-8', newline='').read().split('\n')]


def same_person(a, b):
    a, b = a.strip(), b.strip()
    if not a or not b:
        return False
    return a == b or a.startswith(b) or b.startswith(a) or a.split('·')[0] == b.split('·')[0]


def star_block(lines, name):
    for i, l in enumerate(lines):
        m = STAR.match(l)
        if m and m.group(1).strip() == name:
            j = i + 1
            while j < len(lines):
                t = lines[j]
                if t.startswith('### ') or t.startswith('## ') or t.startswith('> 条目设置'):
                    break
                j += 1
            return i, j, m.group(3)
    return None


def comp_blocks(lines):
    heads = [i for i, l in enumerate(lines) if l.startswith('## ')]
    out = collections.OrderedDict()
    for k, i in enumerate(heads):
        if lines[i].startswith('## 旅途同行·背景'):
            continue
        m = COMP.match(lines[i])
        if not m:
            continue
        name = m.group(1).strip()
        end = heads[k + 1] if k + 1 < len(heads) else len(lines)
        if k + 1 < len(heads):
            mb = BACK.match(lines[heads[k + 1]])
            if mb and same_person(mb.group(1), name):
                end = heads[k + 2] if k + 2 < len(heads) else len(lines)
        out[name] = (i, end)
    return out


def tool(name, f, extra=()):
    try:
        r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(REPO, 'tools', name), f] + list(extra),
                           capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=REPO, timeout=300)
        return r.stdout
    except Exception as e:
        return '（没跑成：%s）' % e


def tool_num(out, key):
    for l in reversed(out.splitlines()):
        m = re.search(key + r'\s*(\d+)', l)
        if m:
            return int(m.group(1))
    return None


def main():
    J = json.load(io.open(os.path.join(HERE, '任务.json'), encoding='utf-8'))
    files = [os.path.basename(f) for f in J['files']]
    O = {b: rl(os.path.join(HERE, '原', b)) for b in files}
    D = {b: rl(os.path.join(HERE, '稿', b)) for b in files}
    # 任务以外的地方不许动：两边把任务名下的块挖掉以后要一样
    cut_o = collections.defaultdict(list)
    cut_d = collections.defaultdict(list)
    for a in J['arts']:
        b = os.path.basename(a['file'])
        so = star_block(O[b], a['old'])
        if so:
            cut_o[b].append((so[0], so[1]))
        for nm in {a['new'], a['old']}:
            sd = star_block(D[b], nm)
            if sd:
                cut_d[b].append((sd[0], sd[1]))
    for c in J['comps']:
        b = os.path.basename(c['file'])
        for src, cut in ((O, cut_o), (D, cut_d)):
            cb = comp_blocks(src[b])
            if c['name'] in cb:
                cut[b].append(cb[c['name']])
            else:
                E('旅伴条的标题不见了或者改了：%s（%s）' % (c['name'], b))
    for b in files:
        def strip(lines, cuts):
            keep = [True] * len(lines)
            for s, e in cuts:
                for i in range(s, e):
                    keep[i] = False
            return [l for l, k in zip(lines, keep) if k]
        a1, a2 = strip(O[b], cut_o[b]), strip(D[b], cut_d[b])
        # 挖掉块以后连着的空行可能多一行少一行，不算
        n1 = [l for l in a1 if l.strip()]
        n2 = [l for l in a2 if l.strip()]
        if n1 != n2:
            df = [x for x in difflib.unified_diff(n1, n2, lineterm='', n=0) if x[:1] in '+-' and x[:3] not in ('+++', '---')]
            E('%s：任务以外的地方动了 %d 行，改回去。头几处：%s' % (b, len(df), '｜'.join(x[:70] for x in df[:4])))
    # 技艺
    for a in J['arts']:
        b = os.path.basename(a['file'])
        new, old, tier = a['new'], a['old'], a['tier']
        if a.get('share') == '从':
            if star_block(D[b], old) and old != new:
                E('%s：这一门跟别人共用一条，原来的块 ### %s 要整块删掉' % (new, old))
            blk = None
        else:
            sd = star_block(D[b], new)
            if not sd:
                E('星条没找到：### %s (Art | %s)，在 稿/%s。标题要一字不差' % (new, tier, b))
                continue
            if sd[2] != tier:
                E('%s：标题里的档是 %s，表里是 %s' % (new, sd[2], tier))
            if old != new and star_block(D[b], old):
                E('%s：旧块 ### %s 还在，要换掉' % (new, old))
            blk = D[b][sd[0]:sd[1]]
            body = '\n'.join(blk)
            heads = [l.split('：')[0] for l in blk if l.startswith('- ') and '：' in l[:12]]
            if not any(l.startswith('【调用】') for l in blk):
                E('%s：少了【调用】那一行' % new)
            if not any(l.startswith('【%s】' % new) for l in blk):
                E('%s：首段要拿【%s】起头' % (new, new))
            if '- 定位' in heads:
                E('%s：还留着「定位」那一行，要拆成新的几行' % new)
            if tier == 'Rare':
                for need in ('- 用处', '- 限制', '- 传承'):
                    if need not in heads:
                        E('%s：Rare 要有「%s」那一行' % (new, need[2:]))
                for bad in ('- 法门', '- 战法', '- 练法', '- 修行重点', '- 世界反应', '- 修行关联'):
                    if bad in heads:
                        E('%s：Rare 只写用处、限制、传承三行，不要「%s」' % (new, bad[2:]))
                use = [l for l in blk if l.startswith('- 用处')]
                if use and any(t in use[0] for t in TIERS):
                    W('%s：Rare 的用处里出现了位阶的字，Rare 不随位阶长' % new)
                if len(re.findall(r'[一-鿿]', body)) > 420:
                    W('%s：Rare 这一条有 %d 个字，偏长，照底卡的 Rare 两三行就够' % (new, len(re.findall(r'[一-鿿]', body))))
            elif tier in ('Epic', 'Legend'):
                for need in ('- 法门', '- 战法', '- 练法', '- 限制', '- 传承'):
                    if need not in heads:
                        E('%s：%s 要有「%s」那一行' % (new, tier, need[2:]))
                if '- 用处' in heads:
                    E('%s：%s 不写「用处」，写法门、战法、练法' % (new, tier))
                three = '\n'.join(l for l in blk if l.startswith(('- 法门', '- 战法', '- 练法')))
                if tier == 'Epic' and ('英雄' in three or '传奇' in three):
                    W('%s：Epic 的三样里写到了英雄或传奇，Epic 只写到极境。是在说别人的事就留着' % new)
                if tier == 'Epic' and '极境' not in three:
                    W('%s：Epic 的三样里没有写到极境，顶上那一层照任务里「练到这一版的顶上」写进去' % new)
                if tier == 'Legend' and '英雄' not in three:
                    W('%s：Legend 的三样里没有写到英雄以上' % new)
                fm = a['row'].get('法门', '')
                fl = [l for l in blk if l.startswith('- 法门')]
                if fl:
                    t = fl[0]
                    if fm.startswith('呼吸') and '呼吸' not in t:
                        E('%s：表里法门是「%s」，法门那一行要写明呼吸一门、哪一曜' % (new, fm))
                    if fm.startswith('呼吸·') and fm.split('·')[1][:2] not in t:
                        W('%s：法门那一行没写曜的名字（%s）' % (new, fm))
                    for k in ('冥想', '祷告', '饮血'):
                        if fm.startswith(k) and k not in t:
                            E('%s：表里法门是「%s」，法门那一行要写明是%s一门' % (new, fm, k))
            if blk and blk[-1].strip():
                E('%s：星条末尾要留一个空行，别贴着下一块' % new)
            # 新写的字的卡面字眼
            for l in blk:
                for p in BANP:
                    if p in l:
                        E('%s：禁用的标点「%s」：%s' % (new, p, l[:40]))
                        break
                for wd in MOON:
                    if wd in l:
                        E('%s：月相的字「%s」' % (new, wd))
                for wd in BANW:
                    if wd in l:
                        W('%s：口径上要留神的字「%s」：%s' % (new, wd, l[max(0, l.find(wd) - 12):l.find(wd) + 14]))
                m = re.match(r'^- ([^：]{9,})：', l)
                if m:
                    E('%s：冒号前头的标签过了八个字：%s' % (new, m.group(1)))
        # 能力行和底座
        for c in J['comps']:
            if not any(same_person(c['name'], h) for h in a['holders']):
                continue
            cb = os.path.basename(c['file'])
            blo, bld = comp_blocks(O[cb]).get(c['name']), comp_blocks(D[cb]).get(c['name'])
            if not blo or not bld:
                continue
            lo, ld = O[cb][blo[0]:blo[1]], D[cb][bld[0]:bld[1]]
            ab = [l for l in ld if l.startswith('能力：')]
            if not ab:
                E('%s：%s 的能力行不见了' % (new, c['name']))
                continue
            if not re.search(r'Art【%s】\s*[（(]\s*%s' % (re.escape(new), tier), ab[0]):
                E('%s：%s 的能力行要写成 Art【%s】(%s，……)' % (new, c['name'], new, tier))
            if old != new and re.search(r'(?<!之章)【%s】' % re.escape(old), '\n'.join(ld)):
                E('%s：%s 的条目里还有【%s】，换成新名字' % (new, c['name'], old))
            bo = [l for l in lo if l.startswith('底座：')]
            bd = [l for l in ld if l.startswith('底座：')]
            _rx = r'法门 %s(?![^\s｜])' % re.escape(old)
            if bo and bd and old != new and re.search(_rx, bo[0]) and re.search(_rx, bd[0]):
                E('%s：%s 底座里的「法门 %s」要换成「法门 %s」' % (new, c['name'], old, new))
    # 旅伴
    for c in J['comps']:
        b = os.path.basename(c['file'])
        r = c['row']
        blo, bld = comp_blocks(O[b]).get(c['name']), comp_blocks(D[b]).get(c['name'])
        if not blo or not bld:
            continue
        lo, ld = O[b][blo[0]:blo[1]], D[b][bld[0]:bld[1]]
        cat = [l for l in ld if l.startswith('类别：')]
        if r['去留'] == '降':
            if not any(l.startswith('类别：相遇') for l in cat):
                E('%s：降成配角的要添一行「类别：相遇｜一句缘故」，紧跟在固定锚定那一行后头' % c['name'])
        elif r['去留'] == '归传奇类':
            if not any(l.startswith('类别：传奇') for l in cat):
                E('%s：归传奇类的要添一行「类别：传奇｜一句缘故」' % c['name'])
        elif cat:
            E('%s：他是留下的旅伴，不添类别那一行' % c['name'])
        pz = [l for l in ld if l.startswith('位阶走势：')]
        if r['位阶走势'] and not pz:
            E('%s：表里有位阶走势，要在底座那一行后头添一行「位阶走势：……」' % c['name'])
        if not r['位阶走势'] and pz:
            W('%s：表里没给位阶走势，你添了一行，照页上写得出依据就留着' % c['name'])

        def sect(lines, head):
            out, on = [], False
            for l in lines:
                if l.startswith('### '):
                    on = l.startswith(head)
                    continue
                if on and (l.startswith('【好感增减') or l.startswith('> 条目设置') or l.startswith('## ')):
                    on = False
                if on:
                    out.append(l)
            return [x for x in out if x.strip()]
        if r['下场添一句'] and sect(lo, '### 正史里的下场') == sect(ld, '### 正史里的下场'):
            E('%s：表里有下场添一句（%s），正史里的下场那一节没有动' % (c['name'], r['下场添一句'][:24]))
        fo = [l for l in lo if l.startswith('固定锚定：')]
        fd = [l for l in ld if l.startswith('固定锚定：')]
        aged = r['年纪调整'].startswith(('改成', '收到', '跟着'))
        if aged and fo == fd:
            E('%s：年纪要改（%s），固定锚定里的生年没有动' % (c['name'], r['年纪调整'][:30]))
        if not aged and fo != fd:
            E('%s：固定锚定那一行不许动（这个人年纪不改）' % c['name'])
        for key in ('体态数据', '> 条目设置'):
            ko = [l for l in lo if l.startswith(key)]
            kd = [l for l in ld if l.startswith(key)]
            if key == '> 条目设置':
                def norm(x):
                    return re.sub(r'[一-鿿·]+那一条要同时出现[一-鿿·]+，?', '', x)
                if [norm(x) for x in ko] != [norm(x) for x in kd]:
                    E('%s：条目设置那一行不许动' % c['name'])
            elif ko != kd and not aged:
                E('%s：%s那一行不许动' % (c['name'], key))
        if [l for l in lo if l.startswith('## ')] != [l for l in ld if l.startswith('## ')]:
            E('%s：## 标题不许动' % c['name'])
        # 别的行动了多少
        ok_pre = ('能力：', '底座：', '位阶走势：', '类别：')
        age_pre = ('【调用】', '固定锚定：', '身份：', '外貌：', '容貌评价：', '体态数据', '装束：')
        lock = set(sect(lo, '### 裁定锁')) | set(sect(lo, '### 正史里的下场'))
        gone = [l for l in lo if l.strip() and l not in set(ld)]
        odd = []
        for l in gone:
            if l.startswith(ok_pre) or l in lock:
                continue
            if aged and (l.startswith(age_pre) or re.search(r'\d{2,5}年|岁', l)):
                continue
            if r['去留'] in ('降', '归传奇类') and l.startswith('【调用】'):
                continue
            if any(('【%s】' % a['old']) in l or a['old'] in l for a in J['arts'] if any(same_person(c['name'], h) for h in a['holders'])):
                continue
            odd.append(l)
        if odd:
            W('%s：这几行也动了，跟任务对不上就改回去：%s' % (c['name'], '｜'.join(x[:36] for x in odd[:5])))
        for l in [x for x in ld if x.strip() and x not in set(lo)]:
            for p in BANP:
                if p in l:
                    E('%s：新写的行里有禁用的标点「%s」：%s' % (c['name'], p, l[:40]))
                    break
            for wd in MOON:
                if wd in l:
                    E('%s：新写的行里有月相的字「%s」' % (c['name'], wd))
    # 仓库里的卡面检查，稿不许比原多
    for b in files:
        po, pd = os.path.join(HERE, '原', b), os.path.join(HERE, '稿', b)
        for name, key, extra in (('cardscan.py', '合计', ()), ('check_people_v7.py', '硬问题合计', (REPO,)), ('authormark.py', '合计', ())):
            oo, od = tool(name, po, extra), tool(name, pd, extra)
            no, nd = tool_num(oo, key), tool_num(od, key)
            if no is None or nd is None:
                W('%s：%s 没跑出数' % (b, name))
            elif nd > no:
                detail = [l for l in od.splitlines() if l.strip() and l not in set(oo.splitlines())][:8]
                E('%s：%s 报的比原稿多（%d → %d）：%s' % (b, name, no, nd, '｜'.join(x[:80] for x in detail)))
    print('== 自查 %s ==' % J['name'])
    print('错 %d 条' % len(errs))
    for x in errs:
        print('  错｜' + x)
    print('看 %d 条' % len(looks))
    for x in looks:
        print('  看｜' + x)
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
