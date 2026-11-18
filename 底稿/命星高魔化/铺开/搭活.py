# -*- coding: utf-8 -*-
"""旅伴与命星重审·铺开：照 全谱.tsv 和 旅伴表.tsv 排份、搭活的文件夹。

用法（仓库根上）：
  python -I -X utf8 底稿/命星高魔化/铺开/搭活.py plan            排份，写 分份.json、分份.md，报对不上的行
  python -I -X utf8 底稿/命星高魔化/铺开/搭活.py make 份名 …      搭这几份活的文件夹（已经有的不重搭，加 --force 才冲掉）
  python -I -X utf8 底稿/命星高魔化/铺开/搭活.py make --page 山铜纪_六

一份活管几位旅伴和他们名下的技艺。活的文件夹在仓库外头（WORK），里头是 原/（底本，不许动）、稿/（改这里）、
任务.md（给写的人看）、任务.json（给自查和收稿看）、写法说明.md、门表.md、自查.py。
收稿时只从 稿/ 里取这一份名下的块（星条、旅伴条和它的背景条），别处改了的一律不收。
"""
import io, os, re, sys, glob, json, shutil, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
QP = os.path.join(HERE, '..', '全谱')
WORK = 'C:/Users/waitl/codex_work/star_1117'
CN = '一二三四五六七八九十'
GAN = '甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥'
DUP = {'v6a_stars17.md', 'v6b_stars18.md', 'w6a_stars19.md', 'w6b_stars20.md', 'w6c_stars21.md'}
STAR = re.compile(r'^### (.+?) \((Art)\s*\|\s*(\w+)\)\s*$')
ANYSTAR = re.compile(r'^### (.+?) \((Art|Special|Passive|Active|Ability)\s*\|\s*(\w+)\)\s*$')
COMP = re.compile(r'^## 旅途同行：(.+?)(?:（.*)?$')
BACK = re.compile(r'^## 旅途同行·背景：(.+?)\s*$')

GATES = collections.OrderedDict([
    ('E1', '晨曦·971'), ('E2', '风铃·斩风剑律'), ('E3', '蔷薇·花雨剑舞'), ('E4', '月镜·星辰轨迹占卜术'),
    ('E5', '精灵·守望长律'), ('E6', '矮人·誓锤锻律'), ('E7', '龙裔·鳞誓承诵法'), ('E8', '圣堂·共祷法'), ('E9', '银帆·护道列舰法'),
    ('W1', '烬冠'), ('W2', '赤书'), ('W3', '绯庭'), ('W4', '长明'), ('W5', '渡桥'), ('W6', '坠星'), ('W7', '镇岳'), ('W8', '围索'), ('W9', '月汐'),
    ('W0', '黑耀的法与军阵'),
    ('X1', '行猎与猎魔'), ('X2', '岩息'), ('X3', '结环与真理'), ('X4', '传火与熔心'), ('X5', '沸血与锻体'),
    ('X6', '暗路'), ('X7', '信使与斥候'), ('X8', '驯兽'), ('X9', '潮与歌'),
    ('XA', '断罪与问'), ('XB', '探井'),
    ('C1', '锻造与符文'), ('C2', '炼药与解构'), ('C3', '鼎镬'), ('C4', '枯荣'), ('C5', '医'), ('C6', '碑与刻'),
    ('S', '散手'), ('N', '新立的门'), ('H', '行当'),
])


def gate_group(g):
    g = g.strip()
    if g.startswith('S'):
        return 'S'
    if g.startswith('N'):
        return 'N'
    m = re.match(r'([EWXC][0-9AB]|H)', g)
    return m.group(1) if m else '?'


def read_tsv(name):
    rows = [l.rstrip('\n').split('\t') for l in io.open(os.path.join(QP, name), encoding='utf-8')]
    h = rows[0]
    return [dict(zip(h, r + [''] * (len(h) - len(r)))) for r in rows[1:] if any(r)]


def safe_write(path, text):
    """写盘，碰上 OSError 隔两秒再试，至多五回。"""
    import time
    for k in range(5):
        try:
            with io.open(path, 'w', encoding='utf-8', newline='') as fo:
                fo.write(text)
            return
        except OSError:
            if k == 4:
                raise
            time.sleep(2)


def page_files(page):
    def num(s):
        return CN.index(s) + 1
    if page.startswith('第'):
        g = glob.glob(os.path.join(ROOT, '月银纪史诗', page + '_*.md'))
    elif page.startswith('诸国期_'):
        g = glob.glob(os.path.join(ROOT, '诸国期', '诸国期时段_%s_*.md' % page[-1]))
    elif page.startswith('萨尔维斯_'):
        g = glob.glob(os.path.join(ROOT, '萨尔维斯', '萨尔维斯时段_%s_*.md' % page[-1]))
    elif page.startswith('纷争纪_'):
        n = num(page[-1])
        g = glob.glob(os.path.join(ROOT, '纷争纪', 'parts' if n == 1 else 'parts%d' % n, '*.md'))
    elif page.startswith('山铜纪_'):
        g = glob.glob(os.path.join(ROOT, '山铜纪', 'parts%d' % num(page[-1]), '*.md'))
    elif page.startswith('迷宫纪前传_'):
        g = glob.glob(os.path.join(ROOT, '迷宫纪前传', 'parts%d' % num(page[-1]), '*.md'))
    else:
        g = []
    out = []
    for f in sorted(g):
        b = os.path.basename(f)
        if b in DUP or b.endswith('_notes.md') or 'notes' in b:
            continue
        out.append(f)
    return out


def read_lines(f):
    return io.open(f, encoding='utf-8', newline='').read().split('\n')


def bare(s):
    return s.rstrip('\r')


def star_block(lines, name):
    """星条那一块的起止行号（不含下一块的标题、不含节末的条目设置）。找不到回 None。"""
    for i, l in enumerate(lines):
        m = STAR.match(bare(l))
        if m and m.group(1).strip() == name:
            j = i + 1
            while j < len(lines):
                t = bare(lines[j])
                if t.startswith('### ') or t.startswith('## ') or t.startswith('> 条目设置'):
                    break
                j += 1
            return i, j, m.group(3)
    return None


def comp_blocks(lines):
    """这个文件里的旅伴条：名字 → (起, 止)。止到背景条的末尾（紧跟着的同一个人的背景条算进来）。"""
    heads = [i for i, l in enumerate(lines) if bare(l).startswith('## ')]
    out = collections.OrderedDict()
    for k, i in enumerate(heads):
        m = COMP.match(bare(lines[i]))
        if not m or bare(lines[i]).startswith('## 旅途同行·背景'):
            continue
        name = m.group(1).strip()
        end = heads[k + 1] if k + 1 < len(heads) else len(lines)
        if k + 1 < len(heads):
            mb = BACK.match(bare(lines[heads[k + 1]]))
            if mb and same_person(mb.group(1), name):
                end = heads[k + 2] if k + 2 < len(heads) else len(lines)
        out[name] = (i, end)
    return out


def same_person(a, b):
    a, b = a.strip(), b.strip()
    if not a or not b:
        return False
    return a == b or a.startswith(b) or b.startswith(a) or a.split('·')[0] == b.split('·')[0]


def holders_of(s):
    s = re.sub(r'（.*?）', '', s).replace('★', '')
    return [x.strip() for x in re.split(r'[、，,]', s) if x.strip()]


def old_title(r):
    return r['原技艺'] or r['旧名'] or r['技艺']


def short(page):
    return (page.replace('迷宫纪前传_', '前').replace('山铜纪_', '铜').replace('纷争纪_', '纷')
            .replace('诸国期_', '诸').replace('萨尔维斯_', '萨'))


def code(page):
    if page.startswith('第'):
        s = page[1:-1]
        n = (10 + (CN.index(s[1]) + 1 if len(s) > 1 else 0)) if s.startswith('十') else CN.index(s) + 1
        return '月%d' % n
    return short(page)[0] + str(CN.index(page[-1]) + 1)


def plan():
    arts = read_tsv('全谱.tsv')
    comps = read_tsv('旅伴表.tsv')
    pages = []
    for r in arts + comps:
        if r['页'] not in pages:
            pages.append(r['页'])
    jobs, miss, manual = [], [], []
    for page in pages:
        files = page_files(page)
        if not files:
            miss.append('页找不到文件：%s' % page)
            continue
        L = {f: read_lines(f) for f in files}
        CB = {f: comp_blocks(L[f]) for f in files}
        # 旅伴：表里的名字对到文件里的旅伴条
        units = []  # (file, start, name_in_file, row)
        used = set()
        for r in [c for c in comps if c['页'] == page]:
            hit = None
            for f in files:
                for name, (a, b) in CB[f].items():
                    if (f, name) in used:
                        continue
                    if name == r['旅伴'] or name.split('·')[0] == r['旅伴'].split('·')[0]:
                        hit = (f, a, name)
                        break
                if hit:
                    break
            if not hit:
                miss.append('旅伴条没找到：%s %s' % (page, r['旅伴']))
                continue
            used.add((hit[0], hit[2]))
            units.append({'file': hit[0], 'pos': hit[1], 'name': hit[2], 'row': r})
        units.sort(key=lambda u: (files.index(u['file']), u['pos']))
        # 技艺：对到星条
        A = []
        for r in [a for a in arts if a['页'] == page]:
            t = old_title(r)
            hit = None
            for f in files:
                sb = star_block(L[f], t)
                if sb:
                    hit = (f, sb[0], sb[2])
                    break
            if not hit:
                miss.append('星条没找到：%s ### %s（现在叫 %s，%s）' % (page, t, r['技艺'], r['持有人']))
                continue
            hs = holders_of(r['持有人'])
            owner = None
            for h in hs:
                for u in units:
                    if same_person(u['name'], h):
                        owner = u
                        break
                if owner:
                    break
            A.append({'row': r, 'file': hit[0], 'pos': hit[1], 'old': t, 'old_tier': hit[2], 'owner': owner, 'holders': hs})
        # 同页同名的并成一条：不是补上去的那一行当主，没有就取头一行
        groups = collections.defaultdict(list)
        for a in A:
            groups[a['row']['技艺']].append(a)
        for name, g in groups.items():
            if len(g) == 1:
                g[0]['share'] = ''
                continue
            g.sort(key=lambda a: (1 if a['row']['补法'] in ('同门', '新起') else 0, files.index(a['file']), a['pos']))
            g[0]['share'] = '主'
            for a in g[1:]:
                a['share'] = '从'
        # 排份
        chunks, cur, w = [], [], 0
        def weight(u):
            return 1 + sum(1 for a in A if a['owner'] is u)
        i = 0
        while i < len(units):
            f = units[i]['file']
            grp = [u for u in units[i:] if u['file'] == f]
            # 同一个文件里的人尽量放一份；文件太大再从中间断
            for u in grp:
                wu = weight(u)
                if cur and (w + wu > 16):
                    chunks.append(cur)
                    cur, w = [], 0
                cur.append(u)
                w += wu
            i += len(grp)
            nxt = units[i]['file'] if i < len(units) else None
            if nxt:
                wn = sum(weight(u) for u in units[i:] if u['file'] == nxt)
                if w + wn > 16 and w >= 8:
                    chunks.append(cur)
                    cur, w = [], 0
        if cur:
            chunks.append(cur)
        loose = [a for a in A if a['owner'] is None]
        for a in loose:
            manual.append('%s｜%s（原块 %s）｜%s｜持有人不是这一页的旅伴，%s' % (page, a['row']['技艺'], a['old'], a['row']['持有人'], os.path.basename(a['file'])))
        if not chunks and loose:
            chunks.append([])
        pc = code(page)
        for k, ch in enumerate(chunks):
            name = pc + (GAN[k] if len(chunks) > 1 else '')
            my_arts = [a for a in A if a['owner'] is not None and any(a['owner'] is u for u in ch)]
            # 没主的技艺放进含它那个文件的头一份，没有就放末一份
            for a in loose:
                home = [kk for kk, c2 in enumerate(chunks) if any(u['file'] == a['file'] for u in c2)]
                if (home and home[0] == k) or (not home and k == len(chunks) - 1):
                    my_arts.append(a)
            fs = []
            for u in ch:
                if u['file'] not in fs:
                    fs.append(u['file'])
            for a in my_arts:
                if a['file'] not in fs:
                    fs.append(a['file'])
            jobs.append({
                'name': name, 'page': page,
                'files': [os.path.relpath(f, ROOT).replace('\\', '/') for f in fs],
                'comps': [{'name': u['name'], 'file': os.path.relpath(u['file'], ROOT).replace('\\', '/'), 'row': u['row']} for u in ch],
                'arts': [{'new': a['row']['技艺'], 'tier': a['row']['新档'], 'old': a['old'], 'old_tier': a['old_tier'],
                          'file': os.path.relpath(a['file'], ROOT).replace('\\', '/'), 'holders': a['holders'],
                          'owner': a['owner']['name'] if a['owner'] else '', 'share': a.get('share', ''), 'row': a['row']} for a in my_arts],
            })
    json.dump(jobs, io.open(os.path.join(HERE, '分份.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    out = ['# 铺开·分份（搭活.py plan 排的）', '', '一份活管几位旅伴和他们名下的技艺。', '',
           '| 份 | 页 | 旅伴 | 技艺 | 文件 |', '|---|---|---|---|---|']
    for j in jobs:
        out.append('| %s | %s | %d | %d | %s |' % (j['name'], j['page'], len(j['comps']), len(j['arts']), '、'.join(os.path.basename(f) for f in j['files'])))
    out += ['', '## 对不上的（%d）' % len(miss), ''] + ['- ' + m for m in miss]
    out += ['', '## 持有人不是旅伴的技艺（%d，能力行由主会话手改）' % len(manual), ''] + ['- ' + m for m in manual]
    io.open(os.path.join(HERE, '分份.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    na = sum(len(j['arts']) for j in jobs)
    nc = sum(len(j['comps']) for j in jobs)
    print('份 %d，旅伴 %d / %d，技艺 %d / %d，对不上 %d，没主的技艺 %d' % (len(jobs), nc, len(comps), na, len(arts), len(miss), len(manual)))
    for m in miss[:60]:
        print('  ', m)
    return jobs


def task_md(j, arts_all):
    o = ['# %s｜%s' % (j['name'], j['page']), '']
    o.append('先读同一个文件夹里的 写法说明.md。你只改 稿/ 里的文件，原/ 是底本，不许动。只动下面列的星条和旅伴条（连它的背景条），别处一个字不动，动了也不收。')
    o.append('')
    o.append('文件：' + '、'.join('稿/' + os.path.basename(f) for f in j['files']))
    o.append('')
    o.append('## 一、技艺 %d 门' % len(j['arts']))
    o.append('')
    gates_seen = []
    for k, a in enumerate(j['arts'], 1):
        r = a['row']
        g = gate_group(r['归门'])
        if g not in gates_seen:
            gates_seen.append(g)
        o.append('### %d. %s (Art | %s)' % (k, a['new'], a['tier']))
        o.append('- 原来的块：`### %s (Art | %s)`，在 稿/%s' % (a['old'], a['old_tier'], os.path.basename(a['file'])))
        o.append('- 持有人：%s' % '、'.join(a['holders']))
        o.append('- 归门：%s %s%s｜卷：%s｜法门：%s' % (g, GATES.get(g, ''), ('（%s）' % r['归门']) if g in ('S', 'N') else '', r['卷'], r['法门']))
        if r['补法'] == '新起':
            o.append('- 来路：判表把原来那一门行当「%s」撤了，这个人另补一门新的。整块重写，旧块里的行当写进身份行（身份行里本来就有的不用再添）。' % r['原技艺'])
        elif r['补法'] == '同门':
            o.append('- 来路：判表把原来那一门行当「%s」撤了，这个人改拿同一脉现成的这一门，他手里只是头几课或者同一卷。' % r['原技艺'])
        elif r['补法'] == '改回':
            o.append('- 来路：原来就是这一门，档落到 %s。' % a['tier'])
        elif r['旧名']:
            o.append('- 来路：原来叫「%s」，名字换了，本事照旧。旧名退进首段当俗名（兵、匠人、车夫嘴里的叫法）。' % r['旧名'])
        else:
            o.append('- 来路：名字没动。')
        if a['share'] == '主':
            o.append('- 这一页还有别人共用这一门，条目由你这一条写，写的时候把共用的人也照顾到。')
        elif a['share'] == '从':
            o.append('- **这一页同名的条目别人已经写了（或者由别的份写）。你把原来的块整块删掉，不另写条目，只改这个人的能力行。**')
        if r['并进']:
            o.append('- 是哪一门的上游或同一脉：%s' % r['并进'])
        lab = '用处和限制' if a['tier'] == 'Rare' else ('三样各是什么' if a['tier'] == 'Legend' else '缺什么或做到头的')
        o.append('- %s：%s' % (lab, r['缺什么或做到头的']))
        if r['显相']:
            o.append('- 练到这一版的顶上看得见什么：%s' % r['显相'])
        if r['凭什么']:
            o.append('- 判的依据：%s' % r['凭什么'])
        o.append('')
    if gates_seen:
        o.append('### 这几门在四纪里的别的条目（写传承那一行时对一遍上下游，别的页不用你改）')
        o.append('')
        for g in gates_seen:
            if g in ('S', 'H'):
                continue
            rs = [x for x in arts_all if gate_group(x['归门']) == g]
            o.append('- %s %s：%s' % (g, GATES.get(g, ''), '；'.join('%s·%s（%s，%s，%s）' % (short(x['页']), x['技艺'], re.sub(r'（.*?）', '', x['持有人']), x['新档'], x['卷']) for x in rs)))
        o.append('')
    o.append('## 二、旅伴 %d 位' % len(j['comps']))
    o.append('')
    for k, c in enumerate(j['comps'], 1):
        r = c['row']
        o.append('### %d. %s（稿/%s）' % (k, c['name'], os.path.basename(c['file'])))
        o.append('- 表里：%s，%s，%s｜主线 %s' % (r['族'], r['年纪'], r['位阶'], r['主线']))
        o.append('- 去留：%s%s' % (r['去留'], ('｜' + r['说明']) if r['说明'] else ''))
        o.append('- 年纪调整：%s' % (r['年纪调整'] or '不动'))
        o.append('- 位阶走势：%s' % (r['位阶走势'] or '不添'))
        o.append('- 下场添一句：%s' % (r['下场添一句'] or '不添'))
        if r['升传奇']:
            o.append('- 升传奇：%s（这一栏你不写，主会话另写。别的栏照做。）' % r['升传奇'])
        mine = [a['new'] for a in j['arts'] if c['name'] in a['holders'] or any(same_person(c['name'], h) for h in a['holders'])]
        o.append('- 名下的技艺：%s' % ('、'.join(mine) if mine else '这一轮没有要动的'))
        o.append('')
    return '\n'.join(o) + '\n'


def make(names, force=False):
    jobs = json.load(io.open(os.path.join(HERE, '分份.json'), encoding='utf-8'))
    arts_all = read_tsv('全谱.tsv')
    by = {j['name']: j for j in jobs}
    for n in names:
        if n not in by:
            print('没有这一份：', n)
            continue
        j = by[n]
        d = os.path.join(WORK, n)
        if os.path.exists(d):
            if not force:
                print('已经有了，不重搭：', d)
                continue
            shutil.rmtree(d)
        os.makedirs(os.path.join(d, '原'))
        os.makedirs(os.path.join(d, '稿'))
        for f in j['files']:
            src = os.path.join(ROOT, f)
            shutil.copy2(src, os.path.join(d, '原', os.path.basename(f)))
            shutil.copy2(src, os.path.join(d, '稿', os.path.basename(f)))
        io.open(os.path.join(d, '任务.md'), 'w', encoding='utf-8', newline='\n').write(task_md(j, arts_all))
        json.dump(j, io.open(os.path.join(d, '任务.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        for extra in ('写法说明.md', '自查.py'):
            p = os.path.join(HERE, extra)
            if os.path.exists(p):
                shutil.copy2(p, os.path.join(d, extra))
        shutil.copy2(os.path.join(QP, '门表.md'), os.path.join(d, '门表.md'))
        shutil.copy2(os.path.join(HERE, '..', '样稿_第三版_卡面检查稿.md'), os.path.join(d, '样稿_定稿四门.md'))
        print('搭好了', d, '旅伴', len(j['comps']), '技艺', len(j['arts']), '文件', len(j['files']))


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == 'plan':
        plan()
    elif sys.argv[1] == 'make':
        args = [a for a in sys.argv[2:] if not a.startswith('--')]
        force = '--force' in sys.argv
        if '--page' in sys.argv:
            pg = sys.argv[sys.argv.index('--page') + 1]
            jobs = json.load(io.open(os.path.join(HERE, '分份.json'), encoding='utf-8'))
            args = [j['name'] for j in jobs if j['page'] == pg]
        make(args, force)
