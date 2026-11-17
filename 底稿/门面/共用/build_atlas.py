# -*- coding: utf-8 -*-
"""图鉴的数据（11-17）：一本书出一份 data/atlas.json。

    python -I -X utf8 底稿/门面/共用/build_atlas.py            四本书都出
    python -I -X utf8 底稿/门面/共用/build_atlas.py moon strife  只出这几本

从哪里抽：
- 人物：各本书 data/<纪>.json 里每个时代页的 cast、meet、legends（同一个人跨几个时代并成一条，at 记他在哪几段、是哪一类）。
- 强敌：史诗战（底稿/状态栏/comfy/epic/prompts/<份>.json 和 阶段表.json），图走图床（out/图床/gh_epic.json 的地址）。
  落到哪一段：月银纪照时代页里灾祸之兽的名字，再照出处里的第几歌；纷争纪照对手那一行写的年份；山铜纪、迷宫纪照书里的 bosses。
- 神：神名表、两纪神谱（聚成、倒下的年份），图走图床（gh_godsx.json，神明显像）。月银纪只有正神（照聚成年份），纷争纪正神和魔神（照倒下年份），
  山铜纪、迷宫纪是七神加书里时代页列着的那几位。
- 生物：各纪的魔物与首领（纷争纪另加魔兽），兽与人那一张表里的坐骑。
只搬运，字照源稿，去掉给作者看的出处括号和★。
"""
import json, os, re, sys, csv

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.dirname(HERE)                      # 底稿/门面
R = os.path.dirname(os.path.dirname(F))        # 仓库根
COMFY = os.path.join(R, '底稿', '状态栏', 'comfy')

BOOKS = {
    'moon': dict(dir='小样_月银纪书', data='moon.json', era='月银纪', name='传唱录', sub='月银纪图鉴 · 诗人唱过的人、兽与神',
                 epic=['moon'], mon=['月银纪补卷/魔物_01_魔物与首领.md'], mount='月银纪补卷/风土_14_兽与人.md',
                 axis=lambda e, i: 'assets/%s.webp' % e['id']),
    'strife': dict(dir='小样_纷争纪书', data='strife.json', era='纷争纪', name='墙上的名字', sub='纷争纪图鉴 · 战报、伤亡册和圣牌上的人、兽与神',
                   epic=['strife_god1', 'strife_god2', 'strife_other'], mon=['纷争纪/补卷/补卷_78_魔物与首领.md', '纷争纪/补卷/补卷_08_西边与魔兽.md'],
                   mount='纷争纪/补卷/补卷_87_兽与人.md', axis=lambda e, i: 'assets/card/c%02d.webp' % (i + 1)),
    'bronze': dict(dir='小样_山铜纪书', data='bronze.json', era='山铜纪', name='拓本', sub='山铜纪图鉴 · 碑匠拓下来的人、兽与神',
                   epic=['bronze'], mon=['山铜纪/补卷/补卷_46_魔物与首领.md'], mount='山铜纪/补卷/补卷_54_兽与人.md',
                   axis=lambda e, i: 'assets/cg/e%d.webp' % (i + 1)),
    'maze': dict(dir='小样_迷宫纪书', data='maze.json', era='迷宫纪', name='公会名录', sub='迷宫纪图鉴 · 挂号册、首杀板和楼层主',
                 epic=['maze'], mon=['迷宫纪前传/补卷/补卷_52_魔物与首领.md'], mount='迷宫纪前传/补卷/补卷_59_兽与人.md',
                 axis=lambda e, i: 'assets/mural/%s_a.webp' % e['id']),
}
GROUP_KEY = {'离弦': 'lixian', '负山': 'fushan', '翻页': 'fanye', '返青': 'fanqing', '立边': 'libian', '静光': 'jingguang', '不退': 'butui'}
CN_NUM = {c: i for i, c in enumerate('〇一二三四五六七八九', 0)}


def J(*p):
    return json.load(open(os.path.join(*p), encoding='utf-8'))


def clean(s, n=None):
    """去掉给作者看的东西：（★）、（第二歌:712）这类出处括号、条目里的 ★。"""
    if not s:
        return ''
    s = re.split(r'画法\s*★?\s*[：:，]', s)[0]                  # 史诗战本体里给出图的人看的那一段
    s = re.sub(r'(?:神谱只写|神谱里只写|页上没写|页上只写)[^，。]*[，。]', '', s)
    s = re.sub(r'（[^（）]*?(?:★|[:：]\s*\d|第[一二三四五六七八九十]+歌:|补\d|帝国史|支线_|只给 AI|照[^（）]{0,30}那一条)[^（）]*）', '', s)
    s = s.replace('★', '').replace('**', '').strip()
    s = re.sub(r'\s+', ' ', s)
    if n and len(s) > n:
        cut = s[:n]
        k = max(cut.rfind('。'), cut.rfind('，'))
        s = (cut[:k] if k > n * 0.5 else cut) + '。' if not cut.endswith('。') else cut
        s = s.rstrip('，') if s.endswith('，。') else s
    return s


def year_of(s):
    if not s:
        return None
    s = str(s)
    if '元年' in s and not re.search(r'\d', s.split('元年')[0]):
        return 1
    m = re.search(r'(\d{1,5})', s)
    return int(m.group(1)) if m else None


def era_ranges(vol, eras):
    """每个时代页的年份起止（含），月银纪的十五歌只写一年，照下一段的起点往前推。"""
    out = []
    for i, e in enumerate(eras):
        if 'y0' in e:
            out.append((e['y0'], e['y1']))
            continue
        ys = str(e.get('years') or '')
        parts = [p.strip() for p in re.split(r'—|-', ys) if p.strip()]
        y0 = year_of(parts[0]) if parts else None
        if len(parts) > 1:
            y1 = 11034 if '山铜纪' in parts[1] else year_of(parts[1])
        else:
            y1 = None
        out.append([y0 or 1, y1])
    for i, r in enumerate(out):
        if r[1] is None:
            nxt = out[i + 1][0] if i + 1 < len(out) else (10081 if vol == 'moon' else 11034)
            r[1] = max(r[0], nxt - 1)
    return [tuple(r) for r in out]


def eras_in(ranges, ids, y0, y1):
    return [ids[i] for i, (a, b) in enumerate(ranges) if not (b < y0 or a > y1)]


# ---------------- 神 ----------------
def load_gods():
    rows = list(csv.DictReader(open(os.path.join(R, '底稿', '神名', '神名表.tsv'), encoding='utf-8'), delimiter='\t'))
    keys = {}
    for f in ('gods_zheng.json', 'gods_mo.json'):
        for x in J(COMFY, 'epic', 'prompts', f):
            keys[x['name']] = x['key']
    url = {k[:-5]: v['url'] for k, v in J(COMFY, 'out', '图床', 'gh_godsx.json').items()}
    gods = []
    for r in rows:
        nm, hao = r['神'], r['神号']
        full = next((n for n in keys if n.endswith(nm)), None)
        key = keys.get(full) if full else None
        gods.append(dict(n=nm, tag=hao, side=r['正魔'], grp=r['柱'], key=key, img=url.get(key or '', ''), honor=r['尊号']))
    # 两纪神谱：聚成、倒下、管什么、样子
    def scan(paths, pre):
        info = {}
        for p in paths:
            s = open(p, encoding='utf-8').read().replace('\r', '')
            for m in re.finditer(r'(?m)^## %s·神谱｜(.+)$' % pre, s):
                body = s[m.end():s.find('\n## ', m.end()) if s.find('\n## ', m.end()) > 0 else len(s)]
                head = m.group(1).strip()
                g = next((x for x in gods if head.endswith(x['n'])), None)
                if not g:
                    continue
                d = info.setdefault(g['n'], {})
                for lab in ('是谁', '聚成', '倒下', '样子', '殿', '留下的', '没了', '除名', '清算'):
                    mm = re.search(r'(?m)^- %s：(.+)$' % lab, body)
                    if mm:
                        d[lab] = mm.group(1).strip()
                if '倒下' not in d:            # 没写倒下的那几位：没了、除名、清算，或者一行“约2700年：”
                    alt = d.get('没了') or d.get('除名') or d.get('清算')
                    mm = re.search(r'(?m)^- (约?\d{3,5}年)：(.+)$', body)
                    if alt:
                        d['倒下'] = alt
                    elif mm:
                        d['倒下'] = mm.group(1) + '，' + mm.group(2).strip()
        return info
    moon = scan(sorted(glob(os.path.join(R, '月银纪补卷', '神谱_0*.md'))), '月银纪')
    strf = scan(sorted(glob(os.path.join(R, '纷争纪', '补卷', '补卷_6[0-7]_神谱_*.md'))), '纷争纪')
    for g in gods:
        a, b = moon.get(g['n'], {}), strf.get(g['n'], {})
        who = b.get('是谁') or a.get('是谁') or ''
        mm = re.search(r'管([^。]{1,40})。', who)
        g['rule'] = ('管' + mm.group(1)) if mm else ''
        g['look'] = clean(b.get('样子') or a.get('样子') or '', 150)
        jc = a.get('聚成', '')
        g['since'] = 1 if (not jc or '葬火纪' in jc or '开纪' in jc) else (year_of(jc) or 1)
        dx = b.get('倒下', '')
        g['fell'] = year_of(dx) if dx and not re.match(r'^(没有|不倒|还在|未)', dx) else None
        g['fellText'] = clean(dx, 120) if g['fell'] else ''
    return gods


def glob(p):
    import glob as G
    return G.glob(p)


# ---------------- 强敌 ----------------
def load_epic(parts):
    gh = {k[:-5]: v['url'] for k, v in J(COMFY, 'out', '图床', 'gh_epic.json').items()}
    table = {}
    for x in J(COMFY, 'epic', '阶段表.json'):
        table.setdefault((x['part'], x['block']), []).append(x)
    out = []
    for part in parts:
        for b in J(COMFY, 'epic', 'prompts', part + '.json'):
            rows = table.get((part, b['block']), [])
            body = next((r['body'] for r in rows if r.get('body')), '') or ''
            phs = []
            for ph in b['phases']:
                row = next((r for r in rows if r['name'] == ph['name']), None)
                phs.append(dict(nm=ph['name'], img=gh.get(ph['key'], ''), key=ph['key'], look=clean((row or {}).get('look', ''), 160)))
            head = b['block']
            out.append(dict(part=part, block=head, tag=b.get('tag'), what=clean(body, 160), ph=phs,
                            refs=' '.join((r.get('body') or '') + (r.get('look') or '') for r in rows)))
    return out


def ref_years(refs):
    """出处写成「支线_03:262」「帝国史_15:9」的，翻到那一行所在的条目，取【调用】里头一个「N到M年」。"""
    for kind, no, ln in re.findall(r'(支线|帝国史)_(\d+):(\d+)', refs):
        pat = os.path.join(R, '月银纪补卷', '支线_%s_*.md' % no) if kind == '支线' else os.path.join(R, '萨尔维斯', '补卷', '帝国史_%s*.md' % no)
        fs = glob(pat)
        if not fs:
            continue
        lines = open(fs[0], encoding='utf-8').read().replace('\r', '').split('\n')
        i = min(int(ln), len(lines)) - 1
        while i >= 0 and not lines[i].startswith('## '):
            i -= 1
        for j in range(max(i, 0), min(i + 12, len(lines))):
            mm = re.search(r'(\d{1,5})(?:年)?到(\d{1,5})年', lines[j])
            if mm:
                return int(mm.group(1)), int(mm.group(2))
    return None


def qiyao_year(elem):
    fs = glob(os.path.join(R, '萨尔维斯', '补卷', '帝国史_15*.md'))
    if not fs:
        return None
    mm = re.search(r'(?m)^\s*- %s，约?(\d{4})年' % re.escape(elem), open(fs[0], encoding='utf-8').read())
    return int(mm.group(1)) if mm else None


def short_name(block):
    s = re.sub(r'^[A-Z]?\d+[-·\dA-Z]*\s*', '', block)
    s = re.sub(r'（.*$', '', s).strip()
    s = re.sub(r'·[A-Z]\d+[a-z]?\s*', '·', s)          # 一块里分出来的场次编号（P25a 这一类）
    return s


# ---------------- 生物 ----------------
def load_monsters(paths, era_name):
    out = []
    for rel in paths:
        s = open(os.path.join(R, rel), encoding='utf-8').read().replace('\r', '')
        for m in re.finditer(r'(?m)^## (?:%s|迷宫纪)·(魔物|魔兽)｜(.+)$' % era_name, s):
            nm = m.group(2).strip()
            if '这一纪' in nm or '墙外' in nm or '神性污染' in nm:
                continue
            end = s.find('\n## ', m.end())
            body = s[m.end(): end if end > 0 else len(s)]
            body = body.split('\n### 裁定锁')[0].split('\n> 条目设置')[0]
            call = re.search(r'【调用】(.+)', body)
            y0, y1 = None, None
            if call:
                mm = re.search(r'(\d{1,5})(?:年)?到(\d{1,5})年', call.group(1))
                if mm:
                    y0, y1 = int(mm.group(1)), int(mm.group(2))
            lab = {k: (re.search(r'(?m)^(?:-\s*)?%s：(.+)$' % k, body) or [None, ''])[1] for k in ('所在', '位阶', '曜属', '底座', '体型')}
            if not lab['位阶'] and lab['底座']:
                lab['位阶'] = lab['底座']
            paras = [p.strip() for p in body.split('\n\n') if p.strip()]
            desc, skills, way, drop = '', [], '', ''
            for p in paras:
                if p.startswith(('【调用】', '所在：', '位阶：', '曜属：', '底座：', '体型：', '>', '#', '- ')):
                    continue
                mm = re.match(r'\*\*(.+?)\*\*\s*(.*)', p, re.S)
                if mm:
                    skills.append(dict(nm=mm.group(1).rstrip('。'), t=clean(mm.group(2), 120)))
                elif p.startswith('打得过的路'):
                    way = clean(re.sub(r'^打得过的路[：。]\s*', '', p), 140)
                elif p.startswith('身上的东西'):
                    drop = clean(re.sub(r'^身上的东西[：。]\s*', '', p), 120)
                elif not desc:
                    desc = clean(p, 160)
            out.append(dict(n=nm, kind=m.group(1), where=clean(lab['所在'], 90), rank=clean(lab['位阶'], 30), elem=clean(lab['曜属'], 20), size=clean(lab['体型'], 60),
                            what=desc, sk=skills[:3], way=way, drop=drop, y0=y0, y1=y1))
    return out


def load_mounts(rel):
    s = open(os.path.join(R, rel), encoding='utf-8').read().replace('\r', '')
    out = []
    for line in s.split('\n'):
        if not line.startswith('|') or '---' in line or '样子与用处' in line:
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 3:
            continue
        nm = cells[0]
        tier = ''
        mm = re.match(r'(.+?)，(Rare|Epic|Legend|Unique|Normal)$', nm)
        if mm:
            nm, tier = mm.group(1), mm.group(2)
        since = re.search(r'约?(\d{2,5})年(?:起|以后|才)', cells[2])
        out.append(dict(n=clean(nm, 24), tier=tier, what=clean(cells[1], 130), src=clean(cells[2], 110), since=int(since.group(1)) if since else None))
    return out


# ---------------- 一本书 ----------------
def build(vol):
    cfg = BOOKS[vol]
    bdir = os.path.join(F, cfg['dir'])
    d = J(bdir, 'data', cfg['data'])
    eras = d['eras']
    ids = [e['id'] for e in eras]
    ranges = era_ranges(vol, eras)
    pa = J(bdir, 'data', 'pa.json')
    have = J(bdir, 'data', 'have.json')
    hps = set(have.get('ps') or [])

    periods = []
    for i, e in enumerate(eras):
        img = cfg['axis'](e, i)
        periods.append(dict(id=e['id'], t=e['title'], lb=e.get('label') or '', y=str(e.get('years') or ''), y0=ranges[i][0], y1=ranges[i][1],
                            img=img if os.path.exists(os.path.join(bdir, img)) else '', part=e.get('part')))

    # 人物
    people, idx = [], {}
    KIND = {'cast': '旅伴', 'meet': '相遇', 'legends': '传奇'}
    for e in eras:
        for grp in ('cast', 'meet', 'legends'):
            for c in e.get(grp) or []:
                k = (c['name'], c.get('key') or '')
                if k not in idx:
                    idx[k] = len(people)
                    people.append(dict(n=c['name'], key=c.get('key') or '', at={}, prof=[]))
                p = people[idx[k]]
                p['at'][e['id']] = KIND[grp]
                if c.get('p'):
                    p['prof'].append(e['id'])
                for f, g in (('who', 'who'), ('race', 'race'), ('title', 'title'), ('tier', 'tier'), ('tag', 'tag')):
                    if c.get(f) and not p.get(g):
                        p[g] = clean(c[f], 70)
    for p in people:
        k = p['key']
        if k:
            for sheet, a in pa.items():
                if k in a['k']:
                    p['pa'] = [sheet, a['k'].index(k)]
                    break
        p['spr'] = 1 if k and k in hps else 0
        if not p['prof']:
            del p['prof']
    pa_dim = {s: [a['c'], a.get('r') or (len(a['k']) + a['c'] - 1) // a['c']] for s, a in pa.items()}

    # 强敌
    foes = []
    for b in load_epic(cfg['epic']):
        sn = short_name(b['block'])
        at = []
        if vol == 'moon':
            for i, e in enumerate(eras):
                if any(sn and sn in (x.get('name') or '') for x in e.get('beasts') or []):
                    at.append(e['id'])
            if not at and not sn.startswith('七曜兽的君王'):
                for i, e in enumerate(eras):
                    if e.get('label') and re.search(re.escape(e['label']) + r'[:：]', b['refs']):
                        at.append(e['id'])
                        break
            if not at and sn.startswith('七曜兽的君王'):     # 七曜的君王：照帝国史七曜君王座那一条，哪一座几时锁住；没拿下的两座落在萨尔维斯那几段
                elem = re.sub(r'^七曜兽的君王·', '', sn).split('，')[0]
                yy = qiyao_year(elem)
                at = eras_in(ranges, ids, yy, yy) if yy else [e['id'] for e in eras if (e.get('part') == 2)]
            if not at:                     # 出处在支线、帝国史里的：照那一条【调用】写的年份
                yy = ref_years(b['refs'])
                if yy:
                    at = eras_in(ranges, ids, yy[0], yy[1])
        elif vol == 'strife':
            y = year_of(re.sub(r'^[^（]*', '', b['block'])) or year_of(b['block'])
            if '元年' in b['block'] and not y:
                y = 1
            if y:
                at = eras_in(ranges, ids, y, y)
        else:
            code = b['block'].split(' ')[0]
            for e in eras:
                if any(x.get('code') == code for x in e.get('bosses') or []):
                    at.append(e['id'])
        m = re.search(r'（(.+)）', b['block'])
        if vol == 'moon':
            k = '灾祸之兽' if any(sn and sn in (x.get('name') or '') for e in eras for x in e.get('beasts') or []) else '七曜的君王' if sn.startswith('七曜') else '支线的对手'
        elif vol == 'strife':
            k = '魔神' if b['part'].startswith('strife_god') else '有名者与兽'
        else:
            k = '楼层主与强敌' if vol == 'maze' else '史诗战'
        note = ''
        if m:                                   # 括号里给作者看的那半句（；以后、玩家站哪一边才是对手这一类）不要，场次编号不要
            note = m.group(1).split('；')[0]
            note = re.sub(r'(?:^|(?<=[，、\s]))[A-Z]\d+(?:[-·]\d+)?[a-z]?\s*', '', note)
            note = re.sub(r'^(?:默认|原文)[，、]?', '', note).strip('，、 ')
            note = clean(note, 60)
        foes.append(dict(n=sn, k=k, full=b['ph'][-1]['nm'] if b['ph'] else sn, note=note, what=b['what'],
                         ph=[dict(nm=x['nm'], img=x['img'], look=x['look']) for x in b['ph']], at=at))
    # 月银纪的灾祸之兽：史诗战里没有的，照书里的字补一张没有图的卡
    if vol == 'moon':
        for e in eras:
            for x in e.get('beasts') or []:
                if not any(f['n'] and f['n'] in x['name'] for f in foes):
                    foes.append(dict(n=x['name'].split('，')[-1], k='灾祸之兽', full=x['name'], note=x.get('tier') or '', what=clean(x.get('size') or '', 120),
                                     ph=[], at=[e['id']], where=clean(x.get('where') or '', 60)))

    # 神
    gods_all = load_gods()
    gods = []
    for g in gods_all:
        if vol == 'moon':
            if g['side'] == '魔':
                continue
            at = eras_in(ranges, ids, g['since'], 10081)
        elif vol == 'strife':
            at = eras_in(ranges, ids, 1, g['fell'] if g['fell'] else 11034)
        else:
            if g['side'] != '柱':
                continue
            at = list(ids)
        if not at:
            continue
        x = dict(n=g['n'], tag=g['tag'], side=g['side'], grp=g['grp'], img=g['img'], rule=g['rule'], look=g['look'], at=at)
        if vol == 'moon' and g['since'] > 1:
            x['since'] = g['since']
        if vol == 'strife' and g['fell']:
            x['fell'] = g['fell']
            x['fellText'] = g['fellText']
        gods.append(x)
    # 书里时代页另列的神（山铜纪、迷宫纪的高座之主那一类，纷争纪个别）：并进来
    for e in eras:
        for c in e.get('gods') or []:
            hit = next((g for g in gods if g['n'] == c['name']), None)
            if hit:
                if e['id'] not in hit['at']:
                    hit['at'].append(e['id'])
                if c.get('p'):
                    hit.setdefault('prof', []).append(e['id'])
                continue
            gods.append(dict(n=c['name'], tag=c.get('tag') or '', side=c.get('side') or '正', grp='', img='', rule=clean(c.get('who') or '', 60),
                             look='', at=[e['id']], **({'prof': [e['id']]} if c.get('p') else {})))

    # 生物
    beasts = []
    for x in load_monsters(cfg['mon'], cfg['era']):
        y0, y1 = x.pop('y0'), x.pop('y1')
        x['at'] = eras_in(ranges, ids, y0, y1) if y0 else list(ids)
        beasts.append(x)
    for x in load_mounts(cfg['mount']):
        since = x.pop('since')
        x['at'] = eras_in(ranges, ids, since, 99999) if since else list(ids)
        x['kind'] = '坐骑'
        beasts.append(x)

    out = dict(vol=vol, era=cfg['era'], name=cfg['name'], sub=cfg['sub'], emblem='common/assets/ui/emblem_%s.webp' % vol,
               periods=periods, pa=pa_dim, people=people, foes=foes, gods=gods, beasts=beasts)
    path = os.path.join(bdir, 'data', 'atlas.json')
    json.dump(out, open(path, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, separators=(',', ':'))
    nofoe = sum(1 for f in foes if not f['at'])
    print('%-6s 时代 %2d｜人物 %3d｜强敌 %3d（没落到哪一段的 %d）｜神 %3d｜生物 %3d｜%5.0f KB'
          % (vol, len(periods), len(people), len(foes), nofoe, len(gods), len(beasts), os.path.getsize(path) / 1024))
    return out


if __name__ == '__main__':
    vols = [a for a in sys.argv[1:] if a in BOOKS] or list(BOOKS)
    for v in vols:
        build(v)
