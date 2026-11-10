# 四纪大框（11-08）：图床地址、立绘、Boss 图。make_four_era_card.py 读。
# 图都在 GitHub 公开仓库 waitlist886-cloud/aldran-img，走 jsDelivr，清单在 底稿/状态栏/comfy/out/图床/gh_<套>.json（文件名 → url）。
#
# 立绘照这一条回复的纪认人（.sz-era 那一枚记号）：同一个名字在几纪是几个样子，1001年和前传也分开。
# 一纪里同一个人几页样子不一样的，照记号上的年份（data-y，位数编码见 make_rules_frame.py 认纪元那一段）挑；
# 同一页里凝名前后两套的，角色签的位阶写着传奇就换传奇那一套（对话框里认不出位阶，照凝名前那一套）。
# 神：正神和七支柱是行走人世三格（常服、私服、正装），魔神是神座一格；衣着写 显像（或者战斗）换神明显像那一张。
# 史诗战：一个对手几阶各一张，照名号里认得出的那一段（神是名字，兽是名号）和第几阶；一个对手几场仗样子不一样的，照年份挑那一场。
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
COMFY = os.path.join(HERE, '..', 'comfy')
HOST = os.path.join(COMFY, 'out', '图床')
CAST = os.path.join(COMFY, 'cast')
GODS = os.path.join(HERE, '..', '..', '神名', '神名表.tsv')
R = '.rili-markdown-renderer:has(.sz-hud)'
CLS = {'moon': 'era-moon', 'strife': 'era-strife', 'bronze': 'era-bronze', 'pre': 'era-pre', 'maze': 'era-maze'}
ERA_OF = {'月银纪': 'moon', '纷争纪': 'strife', '山铜纪': 'bronze', '迷宫纪前传': 'pre', '迷宫纪': 'pre'}
# 各页管的年份（立绘挑哪一套用）。月银纪史诗一歌一页，年份照那一歌的主线
PAGES = {
    'pre': {1: 2, 2: 101, 3: 318, 4: 600, 5: 850, 6: 971},
    'bronze': {1: 2, 2: 301, 3: 580, 4: 661, 5: 742, 6: 862},
    'strife': {1: 1, 2: 121, 3: 301, 4: 1051, 5: 4501, 6: 8801, 7: 10801},
}
SONG = {1: 1, 2: 1001, 3: 1100, 4: 1205, 5: 1350, 6: 1449, 7: 1690, 8: 1721, 9: 2390, 10: 2499, 11: 2620, 12: 2800, 13: 2899, 14: 2950, 15: 3000}
END = {'moon': 10081, 'strife': 11034, 'bronze': 947, 'pre': 1000, 'maze': 99999}
CN = '一二三四五六七八九十'


def manifest(name):
    return {k: v['url'] for k, v in json.load(open(os.path.join(HOST, 'gh_%s.json' % name), encoding='utf-8')).items()}


URL = {}
for _f in glob.glob(os.path.join(HOST, 'gh_*.json')):
    URL.update(manifest(os.path.basename(_f)[3:-5]))


# ---------------- 年份：位数编码的前缀 ----------------
LETTERS = 'abcde'


def _blocks(a, b, L):
    out = []
    while a <= b:
        k = 0
        while k < L - 1 and a % 10 ** (k + 1) == 0 and a + 10 ** (k + 1) - 1 <= b:
            k += 1
        out.append(str(a)[:L - k])
        a += 10 ** k
    return out


def yprefixes(lo, hi):
    """lo..hi 这几年，写成 data-y 的前缀"""
    out = []
    for L in range(1, 6):
        a, b = max(lo, 10 ** (L - 1) if L > 1 else 1), min(hi, 10 ** L - 1)
        if a > b:
            continue
        head = LETTERS[:5 - L + 1]     # 五位数写在 a 后头，四位数写在 b 后头……
        out += [head + p for p in _blocks(a, b, L)]
    return out


def scope(era, lo=None, hi=None):
    if lo is None:
        return '%s:has(.sz-era.%s)' % (R, CLS[era])
    ps = yprefixes(lo, hi)
    return '%s:has(.sz-era.%s:is(%s))' % (R, CLS[era], ','.join('[data-y^="%s"]' % p for p in ps))


def scope_any(eras):
    return '%s:has(.sz-era:is(%s))' % (R, ','.join('.' + CLS[e] for e in eras))


def keysel(keys, base=':is(.sz-npc,.sz-say)'):
    ks = sorted(set(keys))
    if len(ks) == 1:
        return '%s[data-portrait="%s"]' % (base, ks[0])
    return '%s:is(%s)' % (base, ','.join('[data-portrait="%s"]' % k for k in ks))


# ---------------- 人：七套 ----------------
def _page(era, f, src):
    b = os.path.basename(f)
    m = re.match(r'[a-z]+(\d+)', b)
    n = int(m.group(1)) if m else 1
    if era == 'moon':
        if b.startswith('ge'):
            return SONG[n]
        if b.startswith('zg'):
            return 3001 + (n - 1) * 500    # 诸国期六页
        if b.startswith('sa'):
            return 6007 + (n - 1) * 679    # 萨尔维斯六页
    return PAGES.get(era, {}).get(n, 1)


def people():
    """[(纪, 名字, 键, 这一页从哪年起, 凝名以后的那一套)]"""
    out = []
    sets = [('pre', '前传/*.json'), ('bronze', '山铜纪/*.json'), ('strife', '纷争纪/*.json'),
            ('moon', '月银纪史诗/*.json'), ('moon', '诸国期/*.json'), ('moon', '萨尔维斯/*.json')]
    for era, pat in sets:
        for f in sorted(glob.glob(os.path.join(CAST, pat))):
            for e in json.load(open(f, encoding='utf-8')):
                if not isinstance(e, dict) or 'en' not in e:
                    continue
                nm = re.split(r'[·（(]', e['name'])[0].strip()
                if e['en'].endswith('_bare'):
                    nm += '（真容）'       # 诺伦摘了盔的那一套，模型写 立绘:诺伦（真容） 才露
                out.append((era, nm, e['en'], _page(era, f, e.get('src', '')), str(e.get('legend')) == 'True'))
    for k, en in json.load(open(os.path.join(HERE, 'roster.json'), encoding='utf-8')).items():
        out.append(('maze', k, en, 1001, False))
    return out


def por_vals(en, extra=''):
    v = '--por:url("%s");--init:none;--ot:block' % URL['por_%s.webp' % en]
    if 'face_%s.webp' % en in URL:
        v += ';--face:url("%s")' % URL['face_%s.webp' % en]
    if 'art_%s.webp' % en in URL:   # 11-10 立绘点开放大用艺术照
        v += ';--art:url("%s");--artsw:inline-flex' % URL['art_%s.webp' % en]
    return v + extra


# 跨纪的人照写资料说明「已画的不重画」画在别的纪的文件夹里（CLAUDE.md 11-07 查图一轮那一条和各页 .md）：
# 这一纪没画的，活过几纪的人借别的纪那一套，先借1001年（老传奇守旧，跟1001一个样子），再借离这一纪最近的；下面两位照各页的说明指定
BORROW = {('strife', '芙莉莲'): ('bronze', 580), ('strife', '海塔'): ('bronze', 2)}
ORDER = ['moon', 'strife', 'bronze', 'pre', 'maze']


def people_css(w, log):
    groups = {}
    roster_e = set()
    for f in glob.glob(os.path.join(CAST, 'cast_E.json')):
        roster_e |= {re.split(r'[·（(]', e['name'])[0] for e in json.load(open(f, encoding='utf-8'))}
    for era, nm, en, start, leg in people():
        if 'por_%s.webp' % en not in URL:
            log.append('没上图床 %s' % en)
            continue
        groups.setdefault((era, nm), []).append((start, leg, en))
    # 借：画在两纪以上的（活过几纪的人），和1001那一批老传奇
    eras_of = {}
    for era, nm in groups:
        eras_of.setdefault(nm, set()).add(era)
    n_borrow = 0
    for nm, es in sorted(eras_of.items()):
        if len(es) < 2 and nm not in roster_e:
            continue
        for era in ORDER[:4]:
            if era in es:
                continue
            if (era, nm) in BORROW:
                src_era, start = BORROW[(era, nm)]
                vs = [v for v in groups[(src_era, nm)] if v[0] == start] or groups[(src_era, nm)]
            elif 'maze' in es:
                vs = groups[('maze', nm)]
            else:
                src_era = min(es, key=lambda e: (abs(ORDER.index(e) - ORDER.index(era)), -ORDER.index(e)))
                vs = groups[(src_era, nm)]
            plain = [v for v in vs if not v[1]] or vs
            w('%s %s{%s}' % (scope(era), keysel([nm]), por_vals(plain[0][2])))
            n_borrow += 1
    log.append('跨纪借图 %d 条' % n_borrow)
    n_rule = 0
    for (era, nm), vs in sorted(groups.items(), key=lambda x: (x[0][0], len(x[0][1]), x[0][1])):
        vs.sort()
        starts = sorted(set(s for s, _, _ in vs))
        for i, s in enumerate(starts):
            here = [v for v in vs if v[0] == s]
            plain = [v for v in here if not v[1]] or here
            legend = [v for v in here if v[1] and v not in plain[:1]]
            hi = (starts[i + 1] - 1) if i + 1 < len(starts) else END[era]
            sc = scope(era) if i == 0 else scope(era, s, hi)
            w('%s %s{%s}' % (sc, keysel([nm]), por_vals(plain[0][2])))
            n_rule += 1
            if len(plain) > 1:
                log.append('同一页两套都不是传奇，只用了头一套：%s %s' % (nm, [v[2] for v in plain]))
            if legend:
                sc2 = scope(era) if i == 0 else scope(era, s, hi)
                w('%s %s:has(.sz-npc-tags [data-v^="传奇"]){%s}' % (sc2, keysel([nm], '.sz-npc'), por_vals(legend[0][2])))
                n_rule += 1
    return n_rule, len(groups)


# ---------------- 神 ----------------
def god_names():
    """神号名 → 名（神名表的 神 那一栏）"""
    rows = [l.rstrip('\r\n').split('\t') for l in open(GODS, encoding='utf-8') if l.strip()][1:]
    return {r[5] + r[2] if len(r) > 5 else r[2]: r[2] for r in rows if len(r) > 2}, [r[2] for r in rows if len(r) > 2]


def bare_of(name, bares):
    hit = [b for b in bares if name.endswith(b)]
    return max(hit, key=len) if hit else name


THREE = ';--pw:450%;--p0:7.1429%;--pk:42.8571%;--hw:300%;--hk:50%'
ONE = ';--pw:150%;--p0:50%;--pk:0%;--hw:100%;--hk:0%;--oc:0'


def gods_css(w, log):
    _, bares = god_names()
    show = {}
    for f in ('gods_zheng.json', 'gods_mo.json'):
        for g in json.load(open(os.path.join(COMFY, 'epic', 'prompts', f), encoding='utf-8')):
            show[g['name']] = URL.get(g['key'] + '.webp')
    n = 0
    for f in ('行走_上.json', '行走_下.json', '神座.json'):
        for e in json.load(open(os.path.join(CAST, '神明', f), encoding='utf-8')):
            en, name = e['en'], e['name']
            if 'por_%s.webp' % en not in URL:
                log.append('神没上图床 %s' % en)
                continue
            keys = [name, bare_of(name, bares)]
            walk = not en.startswith('gt_')
            if walk:
                eras = {'月银纪': ['moon'], '纷争纪': ['strife']}.get(e.get('era'), ['moon', 'strife'])
                vals = por_vals(en, THREE)
            else:
                eras = ['strife', 'bronze']
                vals = '--por:url("%s");--init:none;--ot:block;--face:url("%s");--fsz:100%% auto' % (URL['por_%s.webp' % en], URL['art_%s.webp' % en]) + ONE
            sc = scope_any(eras)
            w('%s %s{%s}' % (sc, keysel(keys), vals))
            if walk:
                w('%s %s:is([data-o^="正"],[data-o*="礼"]){--oc:2}' % (sc, keysel(keys, '.sz-npc')))
            u = show.get(name)
            if u:
                w('%s %s:is([data-o^="显"],[data-o^="战"],[data-o^="冒"]){--por:url("%s")%s}' % (sc, keysel(keys, '.sz-npc'), u, ONE))
            else:
                log.append('没有显像 %s' % name)
            n += 1
    return n


# ---------------- 真龙原形（11-08） ----------------
# 用户：“为包括阿蕾缇娅在内的有档案的真龙角色补上真龙形态的立绘”。§角色 的衣着写 龙形（或者原形、真身）就换这一张，一张图走 ONE。
# 图是 comfy/gpt_dragon.py 出的，传在图床 dragon 那一套。名字认 立绘:名 写的那一个：四纪的局写凡人名（恩雅、苏薇），龙名也认上。
DRAGONS = [(['阿蕾缇娅'], ['maze', 'pre'], 'dragon_aletia.webp'),
           (['恩雅', '布伦塔赫'], ['strife'], 'dragon_brunta.webp'),
           (['苏薇', '赫莉昂黛'], ['bronze'], 'dragon_helion.webp')]
DRAGON_SEL = ':is([data-o^="龙"],[data-o*="原形"],[data-o*="真身"])'


def dragons_css(w, log, eras_ok=None):
    n = 0
    for keys, eras, fn in DRAGONS:
        if eras_ok:
            eras = [e for e in eras if e in eras_ok]
            if not eras:
                continue
        u = URL.get(fn)
        if not u:
            log.append('真龙原形没上图床 %s' % fn)
            continue
        w('%s %s%s{--por:url("%s")%s}' % (scope_any(eras), keysel(keys, '.sz-npc'), DRAGON_SEL, u, ONE))
        n += 1
    return n


# ---------------- 史诗战 ----------------
ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']


def boss_key(label, bares):
    body = label.split(' ', 1)[1] if ' ' in label else label
    name = re.split(r'[（(]', body)[0].strip()
    parts = [p for p in name.split('，') if p]
    if len(parts) > 1 and parts[0].startswith('七曜兽的君王'):
        name = parts[1]
    else:
        name = parts[0]
    return bare_of(name, bares)


# 名号里没写年份的那几场：S36 是10992年萌芽月魔族最后那一批传奇反叛那一仗，S11 是最后一垄（1790年）
SCENE_YEAR = {'S36': (10992, 2), 'S11': (1790, 3)}


def boss_year(label):
    code = label.split(' ')[0]
    for s, y in SCENE_YEAR.items():
        if re.search(r'(?:^|·)%s(?:$|-)' % s, code):
            return y
    m = re.search(r'(约)?(\d{3,5})年', label) or re.search(r'（(\d{3,5})）', label)
    if not m:
        return None
    if m.re.pattern.startswith('（'):
        return int(m.group(1)), 3
    return int(m.group(2)), (20 if m.group(1) else 3)


def boss_css(w, log):
    _, bares = god_names()
    blocks = []
    for part in ('moon', 'strife_god1', 'strife_god2', 'strife_other', 'bronze', 'maze'):
        for b in json.load(open(os.path.join(COMFY, 'epic', 'prompts', part + '.json'), encoding='utf-8')):
            era = {'moon': 'moon', 'bronze': 'bronze', 'maze': 'pre'}.get(part, 'strife')
            imgs = {}
            for p in b['phases']:
                u = URL.get(p['key'] + '.webp')
                if u and p['no'] not in imgs:
                    imgs[p['no']] = u
            if not imgs:
                log.append('Boss 没有图 %s' % b['block'])
                continue
            code = b['block'].split(' ')[0]
            blocks.append((era, boss_key(b['block'], bares), '·' in code, boss_year(b['block']), imgs, b['block']))
    # 同一纪同一个名字：没带场次的那一套是底子，带场次、写了年份的照年份；带场次没写年份的不用
    by = {}
    for x in blocks:
        by.setdefault((x[0], x[1]), []).append(x)
    n = 0
    for (era, key), xs in sorted(by.items(), key=lambda t: (t[0][0], len(t[0][1]), t[0][1])):
        base = [x for x in xs if not x[2]] or [x for x in xs if x[3] is None] or xs[:1]
        for x in [base[0]] + [x for x in xs if x is not base[0]]:
            if x is base[0]:
                sc = scope(era)
            elif x[3]:
                y, d = x[3]
                sc = scope(era, max(1, y - d), y + d)
            else:
                log.append('Boss 另一场没写年份，不用：%s' % x[5])
                continue
            sel = '%s .sz-boss[data-n*="%s"]' % (sc, key)
            w('%s{--bf:none;--bart:url("%s")}' % (sel, x[4][min(x[4])]))
            for no, u in sorted(x[4].items()):
                w('%s:is([data-p="%d"],[data-p="%s"]){--bart:url("%s")}' % (sel, no, ROMAN[no - 1], u))
            n += 1
    return n, len(by)


# ---------------- 规则和样式 ----------------
def rules(rules):
    return rules


DROP_LINE = re.compile(r'^:is\(\.sz-npc,\.sz-say\)\[data-portrait=|\.sz-boss\[data-n\*="(?:焚原|亚蒙|葛摩恩)"\]')


def css(frame):
    lines = [l for l in frame.split('\n') if not DROP_LINE.search(l)]
    out = '\n'.join(lines)
    for fn, u in URL.items():
        out = out.replace('__ART__/' + fn, u)
    left = sorted(set(re.findall(r'__ART__/([^")]+)', out)))
    assert not left, ('图床上没有的图', left[:20])
    add, log = [], []
    w = add.append
    w('/* ==== 四纪的立绘、神、史诗战的图（four_era_art.py） ==== */')
    a, b = people_css(w, log)
    g = gods_css(w, log)
    c, d = boss_css(w, log)
    dr = dragons_css(w, log)
    print('立绘 %d 条（%d 个名字），神 %d 位，史诗战 %d 个对手（%d 个名字），真龙原形 %d 头' % (a, b, g, c, d, dr))
    for l in log[:40]:
        print('  ', l)
    if len(log) > 40:
        print('   ……还有', len(log) - 40, '条')
    return out + '\n' + '\n'.join(add)
