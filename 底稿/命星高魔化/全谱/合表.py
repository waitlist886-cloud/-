# -*- coding: utf-8 -*-
"""把 分段/ 里各段的判表合成四纪的全谱和旅伴表。
用法（仓库根上）：python -I -X utf8 底稿/命星高魔化/全谱/合表.py [--check] [--liao 料目录]
--check 只核行数和栏数，不写文件。
"""
import io, os, re, sys, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
SEG = os.path.join(HERE, '分段')
ART_COLS = ['页', '技艺', '现阶', '持有人', '归门', '卷', '法门', '新档', '并进', '缺什么或做到头的', '凭什么']
COMP_COLS = ['页', '主线', '旅伴', '族', '年纪', '位阶', '去留', '年纪调整', '位阶走势', '下场添一句', '升传奇', '说明']
ERAS = ['月银纪', '纷争纪', '山铜纪', '迷宫纪前传']

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

def era_of(page):
    if page.startswith('第') or page.startswith('诸国期') or page.startswith('萨尔维斯'):
        return '月银纪'
    if page.startswith('纷争纪'):
        return '纷争纪'
    if page.startswith('山铜纪'):
        return '山铜纪'
    if page.startswith('迷宫纪'):
        return '迷宫纪前传'
    return '?'

def norm_page(seg, label):
    """各段填的页名写法不一样，照段名归成一种：第九歌、诸国期_二、萨尔维斯_二、纷争纪_五、山铜纪_六、迷宫纪前传_四。"""
    label = label.strip()
    nums = [c for c in label if c in '一二三四五六七']
    last = nums[-1] if nums else '?'
    if seg.startswith('月1'):
        m = re.search(r'第(十?[一二三四五六七八九]?)歌', label)
        return ('第%s歌' % m.group(1)) if m else label
    if seg.startswith('月2'):
        if '萨尔' in label:
            return '萨尔维斯_' + last
        if '诸国' in label:
            return '诸国期_' + last
        return label
    if seg.startswith('纷'):
        return '纷争纪_' + last
    if seg.startswith('铜3'):
        return ('迷宫纪前传_一' if ('前' in label or '迷宫' in label) else '山铜纪_六')
    if seg.startswith('铜'):
        return '山铜纪_' + last
    if seg.startswith('前'):
        return '迷宫纪前传_' + last
    return label

CN = '一二三四五六七八九十'
def page_key(page):
    m = re.match(r'第(十?[一二三四五六七八九]?)歌', page)
    if m:
        s = m.group(1)
        n = 10 + (CN.index(s[1]) + 1 if len(s) > 1 else 0) if s.startswith('十') else CN.index(s) + 1
        return (0, n)
    m = re.search(r'_([一二三四五六七])$', page) or re.search(r'时段_([一二三四五六七])_', page)
    k = CN.index(m.group(1)) + 1 if m else 99
    base = 1 if page.startswith('诸国期') else 2 if page.startswith('萨尔维斯') else 3
    return (base, k)

def read_tsv(path, cols):
    rows, bad = [], []
    lines = io.open(path, encoding='utf-8-sig').read().replace('\r\n', '\n').split('\n')
    lines = [l for l in lines if l.strip()]
    for i, l in enumerate(lines):
        cells = l.split('\t')
        if i == 0 and cells[0].strip() == cols[0]:
            continue
        if len(cells) != len(cols):
            bad.append((i + 1, len(cells), l[:60]))
            cells = (cells + [''] * len(cols))[:len(cols)]
        rows.append(dict(zip(cols, [c.strip() for c in cells])))
    return rows, bad

def gate_group(g):
    g = g.strip()
    if g.startswith('S'):
        return 'S'
    if g.startswith('N'):
        return 'N'
    m = re.match(r'([EWXC][0-9AB]|H)', g)
    return m.group(1) if m else '?'

WALK_HEADS = ('开局',)
ADD_HEADS = ('想过有限的人生', '时代没给路', '性子和经历')

def tidy(comps):
    """判表里串了栏的几种写法收一下：位阶走势写进了添一句那一栏的，添一句写进了升传奇那一栏的。"""
    n = 0
    for r in comps:
        if r['下场添一句'].startswith(WALK_HEADS) and not r['位阶走势']:
            r['位阶走势'], r['下场添一句'] = r['下场添一句'], ''
            n += 1
        if r['升传奇'].startswith(ADD_HEADS) and not r['下场添一句']:
            r['下场添一句'], r['升传奇'] = r['升传奇'], ''
            n += 1
        if r['升传奇'] == r['旅伴']:
            r['升传奇'] = ''
            n += 1
    if n:
        print('串栏收了 %d 处' % n)

def apply_overrides(arts, comps):
    """主会话的改判：改判.tsv，栏是 表、页、名、栏、新值、理由。页空着就只认名字。"""
    p = os.path.join(HERE, '改判.tsv')
    if not os.path.exists(p):
        return
    n = miss = 0
    last_why = ''
    TAB = chr(9)
    for i, l in enumerate(io.open(p, encoding='utf-8-sig').read().splitlines()):
        if not l.strip() or l.startswith('表' + TAB) or l.startswith('表｜') or l.startswith('#'):
            continue
        c = ((l.split(TAB) if TAB in l else l.split('｜', 5)) + [''] * 6)[:6]
        tab, page, name, col, val, why = [x.strip() for x in c]
        if why == '同上':
            why = last_why
        else:
            last_why = why
        rows = arts if tab == '技艺' else comps
        key = '技艺' if tab == '技艺' else '旅伴'
        hit = [r for r in rows if (r[key] == name or r[key].startswith(name)) and (not page or r['页'] == page)]
        if not hit:
            print('  改判没对上：第 %d 行 %s %s %s' % (i + 1, tab, page, name))
            miss += 1
            continue
        for r in hit:
            if col not in r:
                print('  改判栏名不对：第 %d 行 %s' % (i + 1, col))
                continue
            r[col] = val
            if why and why not in r.get('改判', ''):
                r['改判'] = ((r.get('改判', '') + '；') if r.get('改判') else '') + why
            n += 1
    print('改判套了 %d 处，没对上 %d 行' % (n, miss))

FILL_COLS = ['页', '原技艺', '补法', '补上的技艺', '归门', '卷', '法门', '新档', '用处和限制', '凭什么']

def apply_fill(arts):
    """撤掉的技艺一人补一门：补艺.tsv。只动判成撤的那几行。"""
    p = os.path.join(HERE, '补艺.tsv')
    if not os.path.exists(p):
        return
    n = miss = 0
    for i, l in enumerate(io.open(p, encoding='utf-8-sig').read().splitlines()):
        if not l.strip() or l.startswith('#') or l.startswith('页｜'):
            continue
        c = l.split('｜')
        if len(c) != len(FILL_COLS):
            print('  补艺栏数不对：第 %d 行 %d 栏' % (i + 1, len(c)))
            miss += 1
            continue
        d = dict(zip(FILL_COLS, [x.strip() for x in c]))
        hit = [r for r in arts if r['页'] == d['页'] and r['技艺'] == d['原技艺'] and r['新档'] == '撤']
        if len(hit) != 1:
            print('  补艺没对上：第 %d 行 %s %s（对上 %d 行）' % (i + 1, d['页'], d['原技艺'], len(hit)))
            miss += 1
            continue
        r = hit[0]
        r['原技艺'] = r['技艺']
        r['补法'] = d['补法']
        r['技艺'] = d['补上的技艺']
        r['归门'], r['卷'], r['法门'], r['新档'] = d['归门'], d['卷'], d['法门'], d['新档']
        r['缺什么或做到头的'] = d['用处和限制']
        r['凭什么'] = d['凭什么']
        n += 1
    left = sum(1 for r in arts if r['新档'] == '撤')
    print('补艺套了 %d 门，没对上 %d 行，还撤着的 %d 门' % (n, miss, left))

def fill_note(r):
    b = r.get('补法')
    if not b:
        return ''
    if b == '改回':
        return '〔判表撤了，改回〕'
    if b == '同门':
        return '〔同门共用，顶替原来的%s〕' % r['原技艺']
    return '〔新起，顶替原来的%s〕' % r['原技艺']

def apply_rename(arts):
    """改名和 Epic 的显相：改名.tsv。套在改判和补艺以后，原名认的是那时候表里的名字。"""
    p = os.path.join(HERE, '改名.tsv')
    if not os.path.exists(p):
        return
    n = m = miss = 0
    for i, l in enumerate(io.open(p, encoding='utf-8-sig').read().splitlines()):
        if not l.strip() or l.startswith('#') or l.startswith('原名｜'):
            continue
        c = [x.strip() for x in l.split('｜')]
        if len(c) != 4:
            print('  改名栏数不对：第 %d 行 %d 栏' % (i + 1, len(c)))
            miss += 1
            continue
        old, new, page, show = c
        hit = [r for r in arts if r['技艺'] == old and not r.get('旧名') and (not page or r['页'] == page)]
        if not hit:
            print('  改名没对上：第 %d 行 %s' % (i + 1, old))
            miss += 1
            continue
        for r in hit:
            if new and new != old:
                r['旧名'] = old
                r['技艺'] = new
                n += 1
            if show and r['新档'] == 'Epic':
                r['显相'] = show
                m += 1
    bare = [r for r in arts if r['新档'] == 'Epic' and not r.get('显相')]
    print('改名套了 %d 行，显相写了 %d 行，没对上 %d 行，Epic 里没写显相的 %d 行' % (n, m, miss, len(bare)))
    for r in bare[:20]:
        print('  没写显相：%s %s' % (r['页'], r['技艺']))
    # 改完以后同一个名字落在不同的门上，多半是撞了
    seen = collections.defaultdict(set)
    for r in arts:
        seen[r['技艺']].add(gate_group(r['归门']))
    for k, v in seen.items():
        if len(v) > 1:
            print('  同名不同门：%s %s' % (k, sorted(v)))

def name_note(r):
    return ('〔原名%s〕' % r['旧名']) if r.get('旧名') else ''

def short_page(page):
    return page.replace('迷宫纪前传_', '前传').replace('山铜纪_', '山铜纪').replace('纷争纪_', '纷争纪').replace('诸国期_', '诸国期').replace('萨尔维斯_', '萨尔维斯')

def main():
    check = '--check' in sys.argv
    liao = None
    if '--liao' in sys.argv:
        liao = sys.argv[sys.argv.index('--liao') + 1]
    arts, comps = [], []
    for p in sorted(glob.glob(os.path.join(SEG, '*_技艺.tsv'))):
        seg = os.path.basename(p)[:-len('_技艺.tsv')]
        rows, bad = read_tsv(p, ART_COLS)
        exp = ''
        if liao:
            lp = os.path.join(liao, seg + '_技艺料.md')
            if os.path.exists(lp):
                exp = len(re.findall(r'(?m)^## \d+\. ', io.open(lp, encoding='utf-8').read()))
        print('技艺 %-18s %3d 行%s%s' % (seg, len(rows), ('（料 %s）' % exp) if exp != '' else '', ('  栏数不对 %d 行 %s' % (len(bad), bad[:3])) if bad else ''))
        for r in rows:
            r['段'] = seg
            r['页'] = norm_page(seg, r['页'])
        arts += rows
    for p in sorted(glob.glob(os.path.join(SEG, '*_旅伴.tsv'))):
        seg = os.path.basename(p)[:-len('_旅伴.tsv')]
        rows, bad = read_tsv(p, COMP_COLS)
        exp = ''
        if liao:
            lp = os.path.join(liao, seg + '_旅伴料.md')
            if os.path.exists(lp):
                exp = len(re.findall(r'(?m)^## \d+\. ', io.open(lp, encoding='utf-8').read()))
        print('旅伴 %-18s %3d 行%s%s' % (seg, len(rows), ('（料 %s）' % exp) if exp != '' else '', ('  栏数不对 %d 行 %s' % (len(bad), bad[:3])) if bad else ''))
        for r in rows:
            r['段'] = seg
            r['页'] = norm_page(seg, r['页'])
        comps += rows
    tidy(comps)
    apply_overrides(arts, comps)
    n_che = sum(1 for r in arts if r['新档'] == '撤')
    apply_fill(arts)
    apply_rename(arts)
    for r in arts:
        if r.get('改判'):
            r['凭什么'] = (r['凭什么'] + ' ' if r['凭什么'] else '') + '〔主会话改判：%s〕' % r['改判']
    for r in comps:
        if r.get('改判'):
            r['说明'] = (r['说明'] + ' ' if r['说明'] else '') + '〔主会话改判：%s〕' % r['改判']
    print('合计 技艺 %d 旅伴 %d' % (len(arts), len(comps)))
    # 统计
    c_old = collections.Counter(r['现阶'] for r in arts)
    c_new = collections.Counter(r['新档'] for r in arts)
    c_gate = collections.Counter(gate_group(r['归门']) for r in arts)
    print('现阶', dict(c_old))
    print('新档', dict(c_new))
    print('归门', dict(c_gate))
    c_stay = collections.Counter(r['去留'] for r in comps)
    print('去留', dict(c_stay))
    print('年纪要动的', sum(1 for r in comps if r['年纪调整']), '升传奇人选', sum(1 for r in comps if r['升传奇']), '添一句', sum(1 for r in comps if r['下场添一句']))
    if check:
        return
    # 合出的 tsv
    with io.open(os.path.join(HERE, '全谱.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(['纪'] + ART_COLS + ['补法', '原技艺', '旧名', '显相']) + '\n')
        for r in arts:
            f.write('\t'.join([era_of(r['页'])] + [r[c] for c in ART_COLS] + [r.get('补法', ''), r.get('原技艺', ''), r.get('旧名', ''), r.get('显相', '')]) + '\n')
    # 改名对照：照门排，一门一条，手机上看得全
    out = ['# 技艺改名对照（11-17，等过目）', '']
    out.append('设计稿，不进卡。前一半是判成 Epic 的那些门，后一半是 Rare，都照归的门排。粗体是现在的名字，后头写原来叫什么。Epic 的下一行是这一门练到这一版的顶上看得见什么，名字没动的也列着，好一眼看全。Rare 只列换了名字的，没动的一门一行并在各门末尾。起名的规矩在 过目单.md 第二节末尾，要换哪个名字改 改名.tsv 再重跑合表。')
    out.append('')
    out.append('# 一、Epic 的名字')
    out.append('')
    E = [r for r in arts if r['新档'] == 'Epic']
    out.append('- Epic 一共 %d 行。换了名字的 %d 行，名字没动的 %d 行。' % (len(E), sum(1 for r in E if r.get('旧名')), sum(1 for r in E if not r.get('旧名'))))
    out.append('')
    for g, gname in GATES.items():
        R = [r for r in E if gate_group(r['归门']) == g]
        if not R:
            continue
        R.sort(key=lambda r: (ERAS.index(era_of(r['页'])) if era_of(r['页']) in ERAS else 9, page_key(r['页']), r['技艺']))
        groups = collections.OrderedDict()
        for r in R:
            groups.setdefault(r['技艺'], []).append(r)
        out.append('## %s %s（%d 门）' % (g, gname, len(groups)))
        out.append('')
        for name, rs in groups.items():
            old = rs[0].get('旧名')
            who = '，'.join('%s·%s' % (short_page(r['页']), re.sub(r'（.*?）', '', r['持有人']) or '没写') for r in rs)
            out.append('- **%s**　%s｜%s' % (name, ('原名 %s' % old) if old else '名字没动', who))
            show = rs[0].get('显相', '')
            if show:
                out.append('  %s。' % show.rstrip('。'))
        out.append('')
    # Rare：只列换了名字的，没动的并成一行
    RR = [r for r in arts if r['新档'] == 'Rare']
    out.append('# 二、Rare 的名字')
    out.append('')
    out.append('尺子是底卡池子里 Rare 的名字：出处或身份，加手法，加门类字（皇家宫廷剑术、精灵弦音弓术、见习骑士冲锋阵、矮人铁砧锻打法）。不往大里起。两三个字的土话包进了名字里，前头添是谁家、哪一处的，后头添门类字，旧名多半还在新名字里头，往后退进条目首段当俗名。Rare 不写练到顶上那一句，用处和限制在各纪的全谱里。')
    out.append('')
    out.append('- Rare 一共 %d 行。换了名字的 %d 行，名字没动的 %d 行。' % (len(RR), sum(1 for r in RR if r.get('旧名')), sum(1 for r in RR if not r.get('旧名'))))
    out.append('')
    for g, gname in GATES.items():
        R = [r for r in RR if gate_group(r['归门']) == g]
        if not R:
            continue
        R.sort(key=lambda r: (ERAS.index(era_of(r['页'])) if era_of(r['页']) in ERAS else 9, page_key(r['页']), r['技艺']))
        groups = collections.OrderedDict()
        for r in R:
            groups.setdefault(r['技艺'], []).append(r)
        ch = [(k, v) for k, v in groups.items() if v[0].get('旧名')]
        keep = [k for k, v in groups.items() if not v[0].get('旧名')]
        out.append('## %s %s（%d 门，换名 %d 门）' % (g, gname, len(groups), len(ch)))
        out.append('')
        for name, rs in ch:
            who = '，'.join('%s·%s' % (short_page(r['页']), re.sub(r'（.*?）', '', r['持有人']) or '没写') for r in rs)
            out.append('- **%s**　原名 %s｜%s' % (name, rs[0]['旧名'], who))
        if keep:
            out.append('- 名字没动的：%s' % '、'.join(keep))
        out.append('')
    io.open(os.path.join(HERE, '改名对照.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    with io.open(os.path.join(HERE, '旅伴表.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(['纪'] + COMP_COLS) + '\n')
        for r in comps:
            f.write('\t'.join([era_of(r['页'])] + [r[c] for c in COMP_COLS]) + '\n')
    # 各纪全谱
    for era in ERAS:
        A = [r for r in arts if era_of(r['页']) == era]
        out = ['# 全谱·%s（11-17 第一稿，等过目）' % era, '']
        out.append('设计稿，不进卡。一门技艺一行，照归的门排。门的说明在 门表.md，判的尺子在 旅伴与命星重审_方向稿_第三版.md 第二节。带★的是新添的连接。')
        out.append('')
        cn = collections.Counter(r['新档'] for r in A)
        co = collections.Counter(r['现阶'] for r in A)
        out.append('- 这一纪技艺 %d 条。原来的档：%s。' % (len(A), '，'.join('%s %d' % (k, co[k]) for k in ['Rare', 'Epic', 'Legend', 'Unique'] if co[k])))
        out.append('- 判下来：%s。' % '，'.join('%s %d' % (k, cn[k]) for k in ['Legend', 'Epic', 'Rare', '撤', 'Unique'] if cn[k]))
        out.append('')
        for g, gname in GATES.items():
            R = [r for r in A if gate_group(r['归门']) == g]
            if not R:
                continue
            R.sort(key=lambda r: (page_key(r['页']), r['技艺']))
            out.append('## %s %s（%d）' % (g, gname, len(R)))
            out.append('')
            out.append('| 页 | 技艺 | 持有人 | 原档 | 新档 | 卷 | 法门 | 练到这一版的顶上 | 缺什么或做到头的 | 凭什么 |')
            out.append('|---|---|---|---|---|---|---|---|---|---|')
            for r in R:
                name = r['技艺'] + (('（并进%s）' % r['并进']) if r['并进'] else '') + name_note(r) + fill_note(r)
                gate_note = r['归门'] if g in ('S', 'N') else ''
                page = re.sub(r'^(纷争纪|山铜纪|迷宫纪前传|诸国期|萨尔维斯)时段_', r'\1', r['页'])
                out.append('| %s | %s%s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                    page, name, ('〔%s〕' % gate_note) if gate_note else '', r['持有人'], r['现阶'], r['新档'], r['卷'], r['法门'],
                    r.get('显相', ''), r['缺什么或做到头的'].replace('|', '｜'), r['凭什么'].replace('|', '｜')))
            out.append('')
        rest = [r for r in A if gate_group(r['归门']) == '?']
        if rest:
            out.append('## 归门没认出来的（%d）' % len(rest))
            for r in rest:
                out.append('- %s｜%s｜%s' % (r['页'], r['技艺'], r['归门']))
        io.open(os.path.join(HERE, '全谱_%s.md' % era), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    # 各纪旅伴表
    for era in ERAS:
        C = [r for r in comps if era_of(r['页']) == era]
        out = ['# 旅伴表·%s（11-17 第一稿，等过目）' % era, '']
        cs = collections.Counter(r['去留'] for r in C)
        out.append('设计稿，不进卡。一条旅伴一行，照页和主线排。去留、年纪调整、位阶走势、添一句、升传奇的判法在 旅伴与命星重审_方向稿_第三版.md 第四节。')
        out.append('')
        out.append('- 这一纪旅伴 %d 条：%s。' % (len(C), '，'.join('%s %d' % (k, v) for k, v in cs.most_common())))
        out.append('- 年纪要动的 %d 位，升传奇的人选 %d 位，下场添一句的 %d 位。' % (
            sum(1 for r in C if r['年纪调整']), sum(1 for r in C if r['升传奇']), sum(1 for r in C if r['下场添一句'])))
        out.append('')
        pages = sorted(set(r['页'] for r in C), key=page_key)
        for pg in pages:
            R = [r for r in C if r['页'] == pg]
            out.append('## %s（%d）' % (pg, len(R)))
            out.append('')
            out.append('| 主线 | 旅伴 | 族，年纪，位阶 | 去留 | 年纪调整 | 位阶走势 | 添一句 | 升传奇 | 说明 |')
            out.append('|---|---|---|---|---|---|---|---|---|')
            last = None
            for r in R:
                ml = r['主线'] if r['主线'] != last else ''
                last = r['主线']
                out.append('| %s | %s | %s，%s，%s | %s | %s | %s | %s | %s | %s |' % (
                    ml, r['旅伴'], r['族'], r['年纪'], r['位阶'], r['去留'], r['年纪调整'], r['位阶走势'], r['下场添一句'], r['升传奇'], r['说明'].replace('|', '｜')))
            out.append('')
        io.open(os.path.join(HERE, '旅伴表_%s.md' % era), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    # 总览
    out = ['# 全谱与旅伴表·总览（11-17 第一稿，等过目）', '']
    out.append('设计稿，不进卡。数是 合表.py 从 分段/ 的判表里数出来的，判表改了重跑就跟上。')
    out.append('')
    out.append('## 一、技艺')
    out.append('')
    out.append('| 纪 | 条数 | 原 Rare | 原 Epic | 原 Legend | 原 Unique | 新 Legend | 新 Epic | 新 Rare | 撤 | 照原 Unique |')
    out.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for era in ERAS + ['合计']:
        A = arts if era == '合计' else [r for r in arts if era_of(r['页']) == era]
        co = collections.Counter(r['现阶'] for r in A)
        cn = collections.Counter(r['新档'] for r in A)
        out.append('| %s | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d |' % (
            era, len(A), co['Rare'], co['Epic'], co['Legend'], co['Unique'], cn['Legend'], cn['Epic'], cn['Rare'], cn['撤'], cn['Unique']))
    out.append('')
    out.append('### 各门各纪几条')
    out.append('')
    out.append('| 门 | ' + ' | '.join(ERAS) + ' | 合计 |')
    out.append('|---|' + '---|' * (len(ERAS) + 1))
    for g, gname in GATES.items():
        cnt = [sum(1 for r in arts if gate_group(r['归门']) == g and era_of(r['页']) == e) for e in ERAS]
        if sum(cnt):
            out.append('| %s %s | %s | %d |' % (g, gname, ' | '.join(str(x) if x else '' for x in cnt), sum(cnt)))
    out.append('')
    out.append('### 判成 Legend 的')
    out.append('')
    for r in arts:
        if r['新档'] == 'Legend':
            out.append('- %s｜%s（%s）｜%s｜%s' % (era_of(r['页']), r['技艺'], r['持有人'], r['归门'], r['缺什么或做到头的']))
    out.append('')
    out.append('### 原来是 Legend、判下来落回去的')
    out.append('')
    for r in arts:
        if r['现阶'] == 'Legend' and r['新档'] not in ('Legend', 'Unique'):
            out.append('- %s｜%s（%s）｜落到 %s｜%s' % (era_of(r['页']), r['技艺'], r['持有人'], r['新档'], r['缺什么或做到头的']))
    out.append('')
    F = [r for r in arts if r.get('补法')]
    if F:
        out.append('### 判表撤掉的 %d 门，一人补了一门' % n_che)
        out.append('')
        cb = collections.Counter(r['补法'] for r in F)
        ct = collections.Counter(r['新档'] for r in F)
        out.append('补法：%s。补上以后的档：%s。原来的行当都写进身份行和 Skill。' % (
            '，'.join('%s %d' % (k, cb[k]) for k in ['新起', '同门', '改回'] if cb[k]),
            '，'.join('%s %d' % (k, ct[k]) for k in ['Epic', 'Rare'] if ct[k])))
        out.append('')
        out.append('| 纪 | 页 | 持有人 | 原来的 | 补上的 | 补法 | 档 | 门 | 卷 | 用处和限制 | 凭什么 |')
        out.append('|---|---|---|---|---|---|---|---|---|---|---|')
        for r in sorted(F, key=lambda r: (ERAS.index(era_of(r['页'])), page_key(r['页']))):
            out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                era_of(r['页']), r['页'], r['持有人'], r['原技艺'], r['技艺'], r['补法'], r['新档'], r['归门'], r['卷'],
                r['缺什么或做到头的'].replace('|', '｜'), r['凭什么'].replace('|', '｜')))
        out.append('')
    out.append('### 新立的门')
    out.append('')
    cN = collections.Counter(r['归门'] for r in arts if gate_group(r['归门']) == 'N')
    for k, v in cN.most_common():
        out.append('- %s（%d）：%s' % (k, v, '、'.join(r['技艺'] for r in arts if r['归门'] == k)))
    out.append('')
    out.append('## 二、旅伴')
    out.append('')
    out.append('| 纪 | 条数 | 留 | 降 | 归传奇类 | 年纪要动 | 添一句 | 升传奇人选 |')
    out.append('|---|---|---|---|---|---|---|---|')
    for era in ERAS + ['合计']:
        C = comps if era == '合计' else [r for r in comps if era_of(r['页']) == era]
        cs = collections.Counter(r['去留'] for r in C)
        out.append('| %s | %d | %d | %d | %d | %d | %d | %d |' % (
            era, len(C), cs['留'], cs['降'], cs['归传奇类'], sum(1 for r in C if r['年纪调整']),
            sum(1 for r in C if r['下场添一句']), sum(1 for r in C if r['升传奇'])))
    out.append('')
    out.append('### 年纪那一条（长生种年纪大、位阶还在灵格以下的）')
    out.append('')
    groups = collections.OrderedDict((k, []) for k in ['改年轻', '精灵照族里的成年线，不动', '年纪牵着旧事，抬位阶', '年纪不动，添一句说明', '降成配角'])
    for r in comps:
        t = r['年纪调整']
        if not t:
            continue
        if r['去留'] == '降':
            k = '降成配角'
        elif t.startswith(('改成', '收到', '跟着')):
            k = '改年轻'
        elif '抬到极境' in t:
            k = '年纪牵着旧事，抬位阶'
        elif '精灵' in t or '百岁上墙' in t:
            k = '精灵照族里的成年线，不动'
        else:
            k = '年纪不动，添一句说明'
        groups[k].append(r)
    for k, v in groups.items():
        out.append('**%s（%d）**' % (k, len(v)))
        out.append('')
        for r in v:
            out.append('- %s｜%s｜%s（%s，%s，%s）｜%s' % (era_of(r['页']), r['主线'], r['旅伴'], r['族'], r['年纪'], r['位阶'], r['年纪调整']))
        out.append('')
    out.append('### 升传奇的人选')
    out.append('')
    for r in comps:
        if r['升传奇']:
            out.append('- %s｜%s｜%s（%s，%s，%s）｜%s' % (era_of(r['页']), r['主线'], r['旅伴'], r['族'], r['年纪'], r['位阶'], r['升传奇']))
    out.append('')
    out.append('### 降成配角的')
    out.append('')
    for era in ERAS:
        names = ['%s（%s）' % (r['旅伴'], r['年纪']) for r in comps if era_of(r['页']) == era and r['去留'] == '降']
        out.append('- %s %d 位：%s' % (era, len(names), '、'.join(names)))
    out.append('')
    io.open(os.path.join(HERE, '总览_自动.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('写好了 全谱_*.md、旅伴表_*.md、总览_自动.md、全谱.tsv、旅伴表.tsv')

if __name__ == '__main__':
    main()
