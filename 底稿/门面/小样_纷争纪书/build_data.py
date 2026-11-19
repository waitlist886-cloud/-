#!/usr/bin/env python3
# 纷争纪这一本书的数据：二十一张牌（二十一篇，一张牌一个时代）从七页源稿和二十二张第七版里抽成 data/strife.json，时代页照它排。
# 只搬运，不改字。抽法照月银纪那一本（小样_月银纪书/build_data.py），那边的函数直接借来用，这里只管纷争纪不一样的地方：
#   一页源稿管三四张牌，主线照题那一行的篇名归到牌上；旅伴照标题括号里写的主线归；相遇照主线正文提没提到归；
#   传奇照 tools/strife_legends.py 那张表（一张牌一行在世的传奇）；史诗那一栏是这张牌的牌文，牌角、谁唱、页边照二十二张第七版。
#   python -I -X utf8 build_data.py            写 data/strife.json 和 data/prof/，报每张牌抽到了什么
#   python -I -X utf8 build_data.py --show s04 把这一张抽到的全文打出来看
import glob
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
_spec = importlib.util.spec_from_file_location('moon_build', os.path.join(ROOT, '底稿', '门面', '小样_月银纪书', 'build_data.py'))
MB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MB)          # 它自己把 stdout 换成了 utf-8
CAST = MB.CAST
cn = MB.cn

# 七页：页名照第十八张那首歌排的。牌从第几张到第几张，年份
PAGES = [('灰的年月', 1, 3, '元年至 120 年'), ('白石的年月', 4, 7, '121 年至 300 年'), ('灯的年月', 8, 10, '301 年至 1050 年'), ('炮的年月', 11, 13, '1051 年至 4500 年'),
         ('浮塔的年月', 14, 16, '4501 年至 8800 年'), ('铁狼的年月', 17, 18, '8801 年至 10800 年'), ('号角的年月', 19, 21, '10801 年至 11034 年')]
# 二十一篇的名字和年份（月银纪与纷争纪合篇_篇章方向稿.md 第四节下部），一篇一张牌
PIAN = ['点燃长夜的人', '背着书卷穿过灰烬', '敌人也有名字', '在赤原许下明年', '七扇门为一人开启', '同行的另一半', '以独臂合拢长垒', '一年挂上一根鹿角', '向残卷借一盏灯', '神流下第一滴血',
        '为明天留一炉火', '光去往南方', '白马驮回空鞍', '当高塔离开大地', '倒扣的血碗', '落日整夜不沉', '在无神的南线立柱', '替死去的神守夜', '勇者路过的早晨', '向自己的神举刃', '门洞火边的摇篮']
YEARS = ['元年', '元年 — 40', '40 — 120', '120 — 180', '180 — 200', '200 — 230', '230 — 300', '300 — 700', '700 — 980', '980 — 1050', '1050 — 1500', '1500 — 3000', '3000 — 4500',
         '4500 — 6000', '6000 — 7500', '7500 — 8800', '8800 — 9800', '9800 — 10800', '10800 — 10990', '10990 — 10993', '10993 — 山铜纪元年']
Y0 = [1, 1, 40, 120, 180, 200, 230, 300, 700, 980, 1050, 1500, 3000, 4500, 6000, 7500, 8800, 9800, 10800, 10990, 10993]      # 这张牌从哪一年起
BASE = 10080          # 月银纪一万零八十一年，纷争纪 N 年是总的第 10080+N 年
NO_TITLE = {'博尔·焦砧', '露卡·铃尾'}          # 传奇表上没有传奇之名、名字自己带姓的
DEEP = re.compile(r'表层|深层|真容|真相层|面甲底下是')      # 只在深层的事（诺伦的真容这一类）不上页
REF2 = re.compile(r'，?(?:往后的事|往后)?照(?:凡世至强|人物)[^，。]{0,24}那[一两三]条')      # 指到别的条目的话，页上用不着
HASH = re.compile(r'（#[0-9]+(?:、#[0-9]+)*）')      # 底卡条目号的出处括号（第七页的源稿里带着），页上不要
REF3 = re.compile(r'，?(?:[0-9]+年起)?照[^，。“”]{1,12}那[一两]条(?:旅伴条)?')      # “照他那一条旅伴条”“照太阳王冠那一条”这一类
EXACT = [('第四页艾格尼丝那一路', '艾格尼丝那一路')]      # 零星的页码出处
# 传奇用哪一套立绘：同一个人画了年轻和后来两套的，传奇表上用后来那一套；岑瓦只画了十岁那一套，传奇表上不放图
LEG_KEY = {'茨维娅': 'z1_zvia_b', '加兹': 'z3_gaz', '康斯坦策': 'z3_konstanze_old', '岑瓦': ''}
CAST_KEY = {('s10', '康斯坦策'): 'z3_konstanze_old'}      # 这一张里她六十岁


def num(i):
    one = '一二三四五六七八九'
    if i <= 9:
        return one[i - 1]
    if i == 10:
        return '十'
    if i < 20:
        return '十' + one[i - 11]
    return '二十' + (one[i - 21] if i > 20 else '')


def page_of(card):
    for i, (_, a, b, _) in enumerate(PAGES):
        if a <= card <= b:
            return i
    raise ValueError(card)


def load_cards():
    """二十二张第七版：牌角、年岁、回目、谁唱、牌面、牌文（一节一节）、页边。"""
    text = open(os.path.join(ROOT, '纷争纪', '天黑以后_二十二张_第七版.md'), encoding='utf-8').read().replace('\r\n', '\n')
    out = []
    for title, body in MB.blocks(text.split('\n')):
        m = re.match(r'^([一二三四五六七八九十]+)(?:　(.+))?$', title)
        if not m:
            continue
        c = {'name': m.group(2) or '', 'no': '', 'years_cn': '', 'hui': '', 'sung': '', 'face': '', 'text': [], 'margin': ''}
        sec, stanza = '', []
        for l in body:
            s = l.strip()
            if s.startswith('### '):
                if sec == '牌文' and stanza:
                    c['text'].append(stanza)
                sec, stanza = s[4:], []
                continue
            if not sec:
                for tag, k in (('- 牌角：', 'no'), ('- 年岁：', 'years_cn'), ('- 回目：', 'hui'), ('- 谁唱：', 'sung')):
                    if s.startswith(tag):
                        c[k] = s[len(tag):]
            elif sec == '牌面' and s:
                c['face'] += s
            elif sec == '牌文':
                if s:
                    stanza.append(s)
                elif stanza:
                    c['text'].append(stanza)
                    stanza = []
            elif sec == '页边' and s:
                c['margin'] = s
        if sec == '牌文' and stanza:
            c['text'].append(stanza)
        for k in ('no', 'hui', 'sung'):
            if c[k] == '没有':
                c[k] = ''
        out.append(c)
    assert len(out) == 22, len(out)
    return out


def load_legends():
    src = open(os.path.join(ROOT, 'tools', 'strife_legends.py'), encoding='utf-8').read()
    ns = {}
    exec(src[src.index('L = ['):src.index('CN = ')], ns)      # 只取那张表，和结尾那一张的标法（END：不知所终、往后不给）
    end = ns.get('END', {})
    out = []
    for full, race, a, b in ns['L']:
        alias, raw = '', full
        if full.endswith('）'):
            full, alias = full[:-1].split('（', 1)
        seg = full.split('·')
        if full in NO_TITLE or len(seg) == 1:
            title, name = '', full
        else:
            title, name = seg[0], '·'.join(seg[1:])
        how = end.get(raw) or end.get(full) or ''
        out.append({'name': name, 'title': title, 'alias': alias, 'race': race, 'a': a, 'b': b or 99, 'gone': how == '不知所终', 'mute': how == '往后不给'})
    return out


def load_legend_notes():
    """传奇的档案和“传奇之陨”（11-12）：scenes/legends/g?.json，子任务起稿、主会话审过（review_legends.py）。
    回（名字 → 这个人是谁、各张牌里在做什么、说过的话，名字 → 陨落那一条）。"""
    leg, falls = {}, {}
    for p in sorted(glob.glob(os.path.join(HERE, 'scenes', 'legends', 'g?.json'))):
        d = json.load(open(p, encoding='utf-8'))
        leg.update(d.get('legends', {}))
        for f in d.get('falls', []):
            falls[f['death']] = f
    return leg, falls


ALLZ = None


def all_cast():
    global ALLZ
    if ALLZ is None:
        ALLZ = []
        for f in sorted(glob.glob(os.path.join(CAST, '纷争纪', 'z*.json'))):
            for c in json.load(open(f, encoding='utf-8')):
                if c.get('en', '').endswith('_bare'):       # 未穿甲那一套是深层的样子，不上页
                    continue
                m = re.match(r'^(.*\.md):(\d+)$', c.get('src', ''))
                ALLZ.append({'name': c.get('name', ''), 'en': c.get('en', ''), 'file': os.path.basename(m.group(1)) if m else '', 'line': int(m.group(2)) if m else 0})
    return ALLZ


def key_at(name, fname, line):
    """旅伴条对上立绘资料：同名的几条（年轻时和后来）照资料里记的源稿行号挑最近的那一条。"""
    short = name.split('·')[0]
    c = [x for x in all_cast() if x['name'] == name or x['name'].split('·')[0] == short or x['name'].split('（')[0] == name]
    if not c:
        return ''
    c.sort(key=lambda x: (x['file'] != fname, abs(x['line'] - line)))
    return c[0]['en']


def year_of(open_text, card):
    m = re.search(r'纷争纪(约)?(元|\d+)年', open_text)
    if not m:
        m2 = re.search(r'山铜纪元年', open_text)
        return ('11034', 11034) if m2 else ('', Y0[card - 1])
    if m.group(2) == '元':
        return '元', 1
    return ('约 ' if m.group(1) else '') + m.group(2), int(m.group(2))


def born_abs(body):
    for l in body:
        if l.strip().startswith('固定锚定：'):
            m = re.search(r'生于(月银纪|纷争纪)(前)?(\d+)年', l)
            if m:
                n = int(m.group(3))
                return (BASE + n) if m.group(1) == '纷争纪' else ((1 - n) if m.group(2) else n)
    return None


GODS = None
GROUP_GODS = {'止戈那一年': '魔'}      # 标题里没有本名的一群魔神


def gods_in(title):
    """人物条写的是神或魔神的（标题里有神谱上的本名）：回 [(本名, 正还是魔)]。"""
    global GODS
    if GODS is None:
        rows = open(os.path.join(ROOT, '底稿', '神名', '神名表.tsv'), encoding='utf-8').read().splitlines()
        keys = rows[0].split(chr(9))
        GODS = {}
        for r in rows[1:]:
            if r.strip():
                d = dict(zip(keys, r.split(chr(9))))
                GODS[d['神']] = '魔' if d['正魔'] == '魔' else '正'
    return [(n, GODS[n]) for n in GODS if n and n in title]


SHOW = None


def show_of(god):
    """这位神或魔神的显像图的键（comfy/out/神明显像/键.png），没有回空。"""
    global SHOW
    if SHOW is None:
        SHOW = {}
        comfy = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
        for f in ('gods_zheng', 'gods_mo'):
            for x in json.load(open(os.path.join(comfy, 'epic', 'prompts', f + '.json'), encoding='utf-8')):
                if os.path.exists(os.path.join(comfy, 'out', '神明显像', x['key'] + '.png')):
                    SHOW[x['name']] = x['key']
    for full, k in SHOW.items():
        if full.endswith(god):
            return k
    return ''


def person_s(title, body, cast, legend_names):
    """纷争纪的人物条标题是“称号，说明，名字”，名字在最后；两段的是一群人，名字在前头。"""
    t = title[:-len('（人物）')].strip()
    seg = t.split('，')
    if len(seg) >= 3:
        name, tag, who = seg[-1], seg[0], '，'.join(seg[1:-1])
        if '的' in name and name.split('的')[-1] in legend_names:      # 最后骑了一回马的希波诺
            who, name = who + '，' + name[:name.rfind('的') + 1].rstrip('的'), name.split('的')[-1]
    elif len(seg) == 2:
        name, tag, who = seg[0], '', seg[1]
    else:
        name, tag, who = t, '', ''
    gs = gods_in(t) or ([('', GROUP_GODS[name])] if name in GROUP_GODS else [])
    key, pset = MB.find_cast(name, cast) if (len(seg) >= 3 and not gs) else ('', '')
    for n, _ in gs:               # 神和魔神的像用神明显像那一套（全力的样子），一条里写着几位的用头一位
        if n and show_of(n):
            key, pset = show_of(n), '神明显像'
            break
    return {'name': name, 'tag': tag, 'who': who, 'key': key, 'pset': pset, 'prof': MB.prof_meet(title, body), 'gods': gs}


def scrub(v):
    """只在深层的话整句拿掉。"""
    if isinstance(v, str):
        v = REF3.sub('', HASH.sub('', REF2.sub('', v)))
        for x, y in EXACT:
            v = v.replace(x, y)
        return ''.join(s for s in MB.sentences(v) if not DEEP.search(s)).strip() if DEEP.search(v) else v
    if isinstance(v, list):
        return [x for x in (scrub(x) for x in v) if x not in ('', None)]
    if isinstance(v, dict):
        return {k: scrub(x) for k, x in v.items()}
    return v


def build():
    cards = load_cards()
    legends = load_legends()
    leg_notes, leg_falls = load_legend_notes()
    rows = open(os.path.join(ROOT, '底稿', '地图', '地点谱', '纷争纪.tsv'), encoding='utf-8').read().replace('\r\n', '\n').split('\n')
    keys = rows[0].split('\t')
    table = [dict(zip(keys, r.split('\t'))) for r in rows[1:] if r.strip()]
    fp = os.path.join(HERE, 'fate_table.json')
    fate_all = json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {}
    eras = []
    for i in range(1, 22):
        c = cards[i - 1]
        eras.append({'id': 's%02d' % i, 'part': page_of(i), 'label': '第' + num(i) + '张', 'no': c['no'], 'title': c['name'], 'years': YEARS[i - 1], 'set': '纷争纪',
                     'pian': PIAN[i - 1], 'pianDesc': '', 'card': {'hui': c['hui'], 'sung': c['sung'], 'text': c['text'], 'margin': c['margin']},
                     'lines': [], 'cast': [], 'meet': [], 'legends': [], 'gods': [], 'beasts': [], 'places': [], '_text': '', '_bg': {}})
    report = []
    for pi, (pname, a, b, _) in enumerate(PAGES):
        fname = '纷争纪时段_%s_%s.md' % (cn(pi + 1), pname)
        lines = open(os.path.join(ROOT, '纷争纪', fname), encoding='utf-8').read().replace('\r\n', '\n').split('\n')
        heads = [n for n, l in enumerate(lines, 1) if l.startswith('## ')]
        bl = MB.blocks(lines)
        assert len(heads) == len(bl)
        page_cast = ([x for x in all_cast() if x['file'] == fname] + [x for x in all_cast() if x['file'] != fname], '纷争纪')
        mine = [e for e in eras if e['part'] == pi]
        by_line, people = {}, []
        for (title, body), ln in zip(bl, heads):
            if '主线｜' in title:
                l = MB.mainline(title, body)
                if l['pian'] not in PIAN:
                    report.append('主线没有对上篇：%s｜%s' % (l['name'], l['pian']))
                    continue
                k = PIAN.index(l['pian']) + 1
                l['year'], l['_y'] = year_of(l['open'], k)
                e = eras[k - 1]
                e['lines'].append(l)
                e['pianDesc'] = e['pianDesc'] or l['pianDesc']
                e['_text'] += '\n'.join(x for x in body if not x.startswith('【调用】'))
                by_line[l['name'].split('·', 1)[-1]] = (k, l)
            elif title.startswith('旅途同行·背景：'):
                nm = re.sub(r'（.*', '', title.split('：', 1)[1]).strip()
                for e in mine:
                    e['_bg'].setdefault(nm, MB.background(body))
        for (title, body), ln in zip(bl, heads):
            if title.startswith('旅途同行：'):
                c = MB.companion(title, body, page_cast)
                seg = re.search(r'（纷争纪·([^）]+)）', title)
                segs = [s.strip() for s in seg.group(1).split('、')] if seg else []
                c['key'] = key_at(c['name'], fname, ln) or c['key']
                c['pset'] = '纷争纪' if c['key'].startswith('z') else c['pset']
                c['born'] = born_abs(body)
                hit = [by_line[s] for s in segs if s in by_line]
                if not hit:
                    report.append('旅伴没有对上主线：%s %s' % (c['name'], segs))
                for k in sorted({k for k, _ in hit}):
                    y = min(l['_y'] for kk, l in hit if kk == k)
                    d = dict(c, prof=dict(c['prof']))
                    d['seg'] = [s for s in segs if s in by_line and by_line[s][0] == k]
                    d['age'] = (BASE + y - c['born']) if c['born'] is not None else None
                    d['key'] = CAST_KEY.get(('s%02d' % k, c['name'].split('·')[0]), d['key'])
                    eras[k - 1]['cast'].append(d)
            elif title.endswith('（人物）'):
                people.append(person_s(title, body, page_cast, {g['name'].split('·')[0] for g in legends}))
        for p in people:          # 相遇照主线正文提没提到归到牌上，哪一张都没提到的归到提得最多的那一页里头一张
            nm = p['name'].split('·')[0]
            cnt = [(e['_text'].count(nm), e) for e in mine]
            if p['gods']:                 # 神和魔神照本名找（一条里写着几位的，提到哪一位都算）
                cnt = [(sum(e['_text'].count(n) for n, _ in p['gods'] if n) + e['_text'].count(nm), e) for e in mine]
                if p['name'] == '止戈那一年':
                    cnt = [(1 if e['id'] == 's20' else 0, e) for e in mine]
            got = [e for n, e in cnt if n > 0] or [max(cnt, key=lambda x: x[0])[1]]
            for e in got:
                d = dict(p, prof=dict(p['prof']))
                gs = d.pop('gods')
                if gs:
                    d['side'] = '魔' if all(s == '魔' for _, s in gs) else '正'
                    e['gods'].append(d)
                else:
                    e['meet'].append(d)
    for i, e in enumerate(eras, 1):
        e['lines'].sort(key=lambda l: l['_y'])
        alive = [g for g in legends if g['a'] <= i <= g['b']]
        old = {g['name'].split('·')[0] for g in alive if g['a'] < i}
        new = {g['name'].split('·')[0] for g in alive if g['a'] == i}      # 这一张里凝名的：他是这一段的主角，不照年纪挪到相遇
        keep, grown, moved, seen = [], [], [], set()
        for c in e['cast']:
            short = c['name'].split('·')[0]
            if short in seen:
                continue
            seen.add(short)
            mortal = bool(re.match(r'^(人类|半身人|兽耳|半兽人|狼耳|犬耳|狐耳|猫耳)', c['race']))
            if short in old or (c.get('role') == '传奇' and any(g['name'].split('·')[0] == short for g in alive)):
                moved.append((c['name'], '传奇', c['age']))
                continue
            if c.get('role') == '相遇':        # 11-18 起照旅伴条里“类别”那一行（旅伴表定的），不再照年纪估
                grown.append({'name': c['name'], 'tag': '', 'who': c['who'], 'key': c['key'], 'pset': c['pset'], 'race': c['race'], 'age': c['age'], 'prof': c.get('prof')})
                moved.append((c['name'], '相遇', c['age']))
                continue
            keep.append(c)
        mine = {c['name'].split('·')[0] for c in keep} | {g['name'].split('·')[0] for g in grown}
        lg = []
        for g in alive:
            if g['name'].split('·')[0] in mine:      # 这一张里才到传奇的那一位不在表上露底
                continue
            key, pset = MB.find_cast(g['name'], ([x for x in all_cast()], '纷争纪'))
            short = g['name'].split('·')[0]
            if short in LEG_KEY:
                key, pset = LEG_KEY[short], ('纷争纪' if LEG_KEY[short] else '')
            x = {'name': g['name'], 'title': g['title'], 'tier': '', 'key': key, 'pset': pset, '_race': g['race']}
            if g['b'] == i and not g.get('mute'):      # 页上没写往后怎样的那几位（往后不给）不标下落
                x['end'] = '不知所终' if g['gone'] else '殁于这一段'
            if g['a'] == i and i > 1:
                x['new'] = 1
            lg.append(x)
        names = [g['name'].split('·')[0] for g in lg]
        e['cast'] = keep
        e['meet'] = grown + [m for m in e['meet'] if not any(n in (m['name'] + m['tag']) for n in names)]
        e['legends'] = lg
        e['moved'] = moved
        for c in e['cast']:
            c.pop('born', None)
            c.pop('role', None)
        MB.take_profiles(e, e.pop('_bg'), fate_all.get(e['id'], {}))
        for g in e['gods']:           # 神和魔神的档案照人物条搬，另记一类
            p = g.pop('prof', None)
            if p and (p.get('sec') or p.get('fate')):
                p['kind'] = 'god'
                if g.get('tag'):
                    p['tag'] = g['tag']
                MB.PROFS[e['id']][g['name']] = {k: v for k, v in p.items() if v not in ('', [], None, False)}
                g['p'] = 1
        for x in e['legends']:        # 传奇的档案：这个人是谁、这一段里在做什么、说过的话；殁在这一段的另记“传奇之陨”（时候、地方、经过，图名）
            race, d = x.pop('_race', ''), leg_notes.get(x['name'])
            if not d:
                report.append('传奇没有档案：%s %s' % (e['id'], x['name']))
                continue
            now = [s['text'] for s in d.get('at', []) if s['cards'][0] <= i <= s['cards'][1]]
            if not now:
                report.append('传奇这一张没有近况：%s %s' % (e['id'], x['name']))
            p = {'kind': 'legend', 'tag': x['title'], 'race': race, 'who': d.get('who', ''), 'now': now[0] if now else '', 'lines': d.get('quotes') or []}
            f = leg_falls.get(x['name']) if x.get('end') else None
            if x.get('end') and not f:
                report.append('殁在这一段的传奇没有陨落那一条：%s %s' % (e['id'], x['name']))
            if f:
                p['fall'] = {k: f[k] for k in ('when', 'where', 'how', 'label', 'name') if f.get(k)}
            MB.PROFS.setdefault(e['id'], {})[x['name']] = {k: v for k, v in p.items() if v not in ('', [], None, False)}
            x['p'] = 1
        e['places'] = MB.places_of(e.pop('_text'), table)
        for l in e['lines']:
            l.pop('_y', None)
    last = cards[21]
    data = {'era': '纷争纪', 'total': '一万一千零三十四年',
            'parts': [{'name': n, 'sub': '纷争纪 ' + y, 'a': a, 'b': b} for n, a, b, y in PAGES],
            'eras': eras, 'last': {'face': last['face'], 'margin': last['margin']}}
    return scrub(data), report


if __name__ == '__main__':
    data, report = build()
    if len(sys.argv) > 2 and sys.argv[1] == '--show':
        e = [x for x in data['eras'] if x['id'] == sys.argv[2]][0]
        print(json.dumps(e, ensure_ascii=False, indent=1))
        print(json.dumps(scrub(MB.PROFS.get(sys.argv[2], {})), ensure_ascii=False, indent=1)[:6000])
        sys.exit(0)
    os.makedirs(os.path.join(HERE, 'data', 'prof'), exist_ok=True)
    js = json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n'
    open(os.path.join(HERE, 'data', 'strife.json'), 'w', encoding='utf-8', newline='\n').write(js)
    print('写了 data/strife.json', len(js), '字')
    tot = 0
    for eid, ps in MB.PROFS.items():
        pj = json.dumps(scrub(ps), ensure_ascii=False, separators=(',', ':')) + '\n'
        open(os.path.join(HERE, 'data', 'prof', eid + '.json'), 'w', encoding='utf-8', newline='\n').write(pj)
        tot += len(pj)
    print('写了 data/prof/', len(MB.PROFS), '份，', sum(len(v) for v in MB.PROFS.values()), '人，', tot, '字')
    for e in data['eras']:
        nokey = [c['name'] for c in e['cast'] + e['meet'] if not c.get('key') and c.get('p')]
        print(e['id'], e['no'], e['title'], '｜', e['pian'], '｜ 主线', len(e['lines']), '旅伴', len(e['cast']), '相遇', len(e['meet']), '传奇', len(e['legends']), '神', len(e['gods']), '地', len(e['places']),
              ('｜ 挪了：' + '、'.join('%s→%s(%s岁)' % m for m in e['moved'])) if e['moved'] else '')
        print('      主线', ' ／ '.join('%s(%s)' % (l['name'].split('·', 1)[-1], l['year']) for l in e['lines']))
        print('      旅伴', ' '.join('%s(%s,%s)' % (c['name'], c.get('age'), c.get('key') or '无图') for c in e['cast']))
        print('      相遇', ' '.join('%s(%s)' % (c['name'], c.get('key') or '无图') for c in e['meet']))
        if e['gods']:
            print('      神与魔神', ' '.join('%s%s(%s)' % (c['tag'] + '·' if c['tag'] else '', c['name'], c['side']) for c in e['gods']))
        print('      传奇', ' '.join('%s(%s)' % (c['name'], c.get('key') or '无图') for c in e['legends']))
        if nokey:
            print('      有档案没立绘：', '、'.join(nokey))
        for l in e['lines']:
            if not (l['ti'] and l['open'] and l['acts'] and l['ending']):
                print('    缺', l['name'], {k: bool(l[k]) for k in ('ti', 'hooks', 'open', 'acts', 'ending')})
    for r in report:
        print('！', r)
