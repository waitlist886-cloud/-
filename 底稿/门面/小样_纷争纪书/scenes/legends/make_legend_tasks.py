#!/usr/bin/env python3
# 给写传奇的人出任务单（scenes/legends/任务单/gX.md）：这一组的传奇各在哪几张牌上、殁在哪一张、立绘键和英文长相、总表里他那一行、
# 源稿里他的条目和提到他的行、对得上的神和魔神的参考图、各张牌已有的图名。
#   python -I -X utf8 make_legend_tasks.py          出七组的任务单（只用标准库）
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = os.path.dirname(HERE)
BOOK = os.path.dirname(SCENES)
sys.path.insert(0, SCENES)
import make_tasks as MT  # noqa: E402    它一进来就把 stdout 包成 utf-8 了，这里不再包一回

ROOT, COMFY = MT.ROOT, MT.COMFY
TABLE = os.path.join(ROOT, '纷争纪', '纷争纪_旅伴与传奇总表.md')

# 七组：照殁在哪一页分，活过纷争纪的另成一组（希尔妲、霍布跟第一、二页的并一组）
GROUPS = {
    'gA': ['奥伦修斯', '费格', '赛弗', '赫拉娜', '哈尔加·石踵', '茨维娅', '希尔妲', '霍布'],
    'gB': ['缇里安', '莉尔缇', '瑞恩·无名', '法隆', '古尔巴', '托卡', '费利克斯·修灯'],
    'gC': ['维兰达', '狄昂', '凯兰', '艾德蒙德·长笛', '诺伦·晨曦', '加兹', '希波诺', '康斯坦策·鹭桥'],
    'gD': ['茵妮', '西格蒙德·兰佩', '诗蔻蒂·罗森戴尔', '乌尔德·缪恩米洛', '塔妮丝', '罗特鲁德', '海蒂', '扎伊娜·赤脊', '伊奥'],
    'gE': ['约恩', '薇儿丹蒂·岚身', '雅克', '比亚尔尼·斯诺里松', '珂伦娜', '维斯洛', '卡尔泽因'],
    'gF': ['欧德', '卡尔戈·玄鳞', '席恩', '博尔·焦砧', '菲恩瑞丝', '露卡·铃尾', '瓦尔克斯', '萨鲁斯', '克萨韦尔·库尔茨'],
    'gH': ['凯恩', '珀拉', '卡兰缇娅', '艾瑟莉娅·维洛恩', '岑瓦', '辛美尔', '芙莉莲·银露', '海塔', '艾冯'],
}
SUFFIX = {'奥伦修斯': 'orentius', '克萨韦尔·库尔茨': 'xaver', '比亚尔尼·斯诺里松': 'bjarni', '康斯坦策·鹭桥': 'konstanze', '茨维娅': 'zvia'}
SEVEN = {'博尔·焦砧', '菲恩瑞丝', '露卡·铃尾', '瓦尔克斯', '萨鲁斯'}
OLD_DIRS = [('月银纪史诗', '*.md'), ('诸国期', '诸国期时段_*.md'), ('萨尔维斯', '萨尔维斯时段_*.md')]


def fall_key(name, key, card):
    suf = SUFFIX.get(name) or (key.split('_', 1)[1] if '_' in key else key)
    return 's%02d_f_%s' % (card, suf)


def collect():
    data = json.load(open(os.path.join(BOOK, 'data', 'strife.json'), encoding='utf-8'))
    leg = {}
    for e in data['eras']:
        n = int(e['id'][1:])
        for g in e['legends']:
            x = leg.setdefault(g['name'], {'title': g.get('title', ''), 'key': g.get('key', ''), 'pset': g.get('pset', ''), 'cards': [], 'end': None, 'new': None})
            x['cards'].append(n)
            if g.get('end'):
                x['end'] = (n, g['end'])
            if g.get('new'):
                x['new'] = n
    return data, leg


def table_rows(short, name):
    src = open(TABLE, encoding='utf-8').read().split('\n')
    a = next(i for i, l in enumerate(src) if l.startswith('## 二、'))
    b = next(i for i, l in enumerate(src) if l.startswith('## 五、'))
    out = []
    for i in range(a, b):
        l = src[i]
        if not l.startswith('| '):
            continue
        first = l.split('|')[1]
        if short in first or (name in SEVEN and first.strip().startswith('七柱碑上的另外五位')):
            out.append((i + 1, l))
    nine = next(i for i, l in enumerate(src) if l.startswith('## 九、'))
    extra = [(i + 1, l) for i in range(nine, len(src)) if short in src[i]]
    one = next(i for i, l in enumerate(src) if l.startswith('## 一、'))
    extra = [(i + 1, l) for i in range(one, a) if short in src[i] and l.startswith('- **圣座**')] + extra
    return out, extra


def mentions(short):
    """纷争纪七页和补卷里：标题带他名字的节（他的条目），和正文里提到他的行号。"""
    out = []
    files = sorted(glob.glob(os.path.join(ROOT, '纷争纪', '纷争纪时段_*.md'))) + sorted(glob.glob(os.path.join(ROOT, '纷争纪', '补卷', '补卷_*.md')))
    for f in files:
        src = open(f, encoding='utf-8').read().split('\n')
        heads = [(i + 1, l[3:].strip()) for i, l in enumerate(src) if l.startswith('## ')]
        own = [(n, t) for n, t in heads if short in t and ('凡世至强' in t or t.endswith('（人物）') or t.startswith('旅途同行'))]
        cut = next((i for i, l in enumerate(src) if l.startswith('## ') and ('设计备注' in l or '传奇表' in l)), len(src))
        lines = [i + 1 for i, l in enumerate(src[:cut]) if short in l and not l.startswith('## ') and not l.startswith('> ')]
        if own or lines:
            sec = {}
            for ln in lines:      # 归到哪一节底下
                h = [t for n, t in heads if n <= ln]
                sec.setdefault(h[-1] if h else '（页头）', []).append(ln)
            out.append((MT.rel(f), len(src), own, sec))
    return out


def old_entries(short):
    out = []
    for d, pat in OLD_DIRS:
        for f in sorted(glob.glob(os.path.join(ROOT, d, pat))):
            src = open(f, encoding='utf-8').read().split('\n')
            for i, l in enumerate(src):
                if l.startswith('## ') and short in l and ('凡世至强' in l or '旅途同行' in l or l.rstrip().endswith('（人物）')):
                    out.append('%s 第 %d 行「%s」' % (MT.rel(f), i + 1, l[3:].strip()[:40]))
    return out


def main():
    data, leg = collect()
    cast = MT.cast_index()
    gods, show = MT.gods_table()
    boss = MT.bosses()
    cg = json.load(open(os.path.join(BOOK, 'cg_table.json'), encoding='utf-8'))
    used = {}
    for stem, t in cg.items():
        if t.get('name'):
            used.setdefault(stem.split('_')[0], []).append(t['name'])
    missing = [n for n in leg if not any(n in v for v in GROUPS.values())]
    assert not missing, missing
    os.makedirs(os.path.join(HERE, '任务单'), exist_ok=True)
    spec = {}
    for gid, names in GROUPS.items():
        o = ['# 任务单 %s｜传奇：%s' % (gid, '、'.join(n.split('·')[0] for n in names)), '',
             '- 交：`底稿/门面/小样_纷争纪书/scenes/legends/%s.json`' % gid,
             '- 总表：`纷争纪/纷争纪_旅伴与传奇总表.md`（第一节口径先读一遍；你这几位的行抄在下面了）',
             '- 源稿七页：`纷争纪/纷争纪时段_一_灰的年月.md` 到 `纷争纪时段_七_号角的年月.md`，很长，照下面给的行号跳着读', '']
        o += ['## 二十一张牌', '', '一张牌一个时代。at 里的 cards 写的就是这个号。', '']
        for e in data['eras']:
            o.append('- %d｜%s %s｜纷争纪 %s%s｜%s' % (int(e['id'][1:]), e['no'], e['title'], e['years'], '' if e['years'].endswith('年') else ' 年', data['parts'][e['part']]['name']))
        o += ['', '## 这一组的传奇', '']
        for name in names:
            x = leg[name]
            short = name.split('·')[0]
            c0, c1 = x['cards'][0], x['cards'][-1]
            assert x['cards'] == list(range(c0, c1 + 1)), (name, x['cards'])
            o.append('### %s%s' % ((x['title'] + '·') if x['title'] else '', name))
            o.append('')
            o.append('- 在表上：第 %d 到第 %d 张（at 要正好盖住这 %d 张）%s' % (c0, c1, len(x['cards']), '；第 %d 张里凝名（新上表）' % x['new'] if x['new'] else ''))
            fk = ''
            if x['end']:
                fk = fall_key(name, x['key'], x['end'][0])
                o.append('- 下落：第 %d 张%s。要写 falls 一条，键 `%s`%s' % (x['end'][0], x['end'][1], fk, '（只写时候、地方、经过，不出图：`"noart": true`，不写 style、text 这些）' if short == '奥伦修斯' else ''))
            else:
                o.append('- 下落：活过纷争纪，不写 falls')
            spec[name] = {'group': gid, 'cards': [c0, c1], 'fall': fk, 'key': x['key'], 'end': x['end'][1] if x['end'] else ''}
            ent = cast.get(x['key'] or '')
            if ent:
                e = ent[0]
                flags = [k for k in ('minor', 'teen', 'child') if e.get(k)]
                o.append('- 立绘键 `%s`（%s 那一套）%s' % (x['key'], x['pset'], '｜**资料标了 %s：照未成年的规矩画**' % '、'.join(flags) if flags else ''))
                o.append('  - who：%s' % e.get('who', '').strip())
                if e.get('palette'):
                    o.append('  - palette：%s' % e['palette'])
                o.append('  - 立绘资料：`%s`（四套衣服各一段）' % ent[1])
            else:
                o.append('- 没有立绘（%s）。falls 的 who 里不写他，text 里照源稿把样子写清楚' % (x['key'] or '没有键'))
            rows, extra = table_rows(short, name)
            for ln, l in rows:
                o.append('- 总表第 %d 行：%s' % (ln, l))
            for ln, l in extra:
                o.append('- 总表第 %d 行里也提到他：%s' % (ln, l[:260] + ('…' if len(l) > 260 else '')))
            for rel, n, own, sec in mentions(short):
                o.append('- `%s`（%d 行）' % (rel, n))
                for hn, t in own:
                    o.append('  - **他的条目** 第 %d 行「%s」' % (hn, t[:50]))
                for t, lns in list(sec.items())[:14]:
                    o.append('  - 「%s」里第 %s 行%s' % (t[:34], '、'.join(map(str, lns[:10])), ' 等 %d 处' % len(lns) if len(lns) > 10 else ''))
            old = old_entries(short)
            if old:
                o.append('- 月银纪里他的条目（写 who 那一句用）：' + '；'.join(old[:4]))
            text = ' '.join(l for _, l in rows)
            named = [g for g in gods if g['神'] and g['神'] in text]
            for g in named:
                k = show.get(g['神'])
                has = k and os.path.exists(os.path.join(COMFY, 'out', '神明显像', k + '.png'))
                bs = [b for b in boss if g['神'] in b['block'] and b['pics']]
                o.append('- 参考图｜%s %s%s｜显像 %s%s' % ('魔神' if g['正魔'] == '魔' else ('七支柱' if g['正魔'] == '柱' else '正神'), g['神号'], g['神'], ('`%s`' % k) if has else '没有',
                                                    ''.join('｜史诗战 %s' % '、'.join('`%s`' % p.split(' ')[0] for p in b['pics']) for b in bs[:1])))
            o.append('')
        o += ['## 各张牌已有的图名（falls 的 name 别跟同一张牌里的重）', '']
        for eid in sorted(used):
            o.append('- %s：%s' % (eid, '、'.join(used[eid])))
        open(os.path.join(HERE, '任务单', gid + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(o) + '\n')
        print(gid, len(names), '位，', len(o), '行，at 共', sum(len(leg[n]['cards']) for n in names), '张次，falls', sum(1 for n in names if leg[n]['end']))
    open(os.path.join(HERE, 'spec.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(spec, ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    main()
