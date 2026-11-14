#!/usr/bin/env python3
# 给写场面的人出任务单（scenes/任务单/sNN.md）：这张牌的源稿在哪、主线各幕和键、这一段的人和立绘键、神和魔神的显像、史诗战里对得上的参考图。
#   python -I -X utf8 make_tasks.py          出二十一张牌的任务单（只用标准库）
import glob
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)
ROOT = os.path.normpath(os.path.join(BOOK, '..', '..', '..'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
NUM = '一二三四五六七八九十'
PAGES = ['灰的年月', '白石的年月', '灯的年月', '炮的年月', '浮塔的年月', '铁狼的年月', '号角的年月']


def rel(p):
    return os.path.relpath(p, ROOT).replace('\\', '/')


def cast_index():
    idx = {}
    for f in glob.glob(os.path.join(COMFY, 'cast', '**', '*.json'), recursive=True):
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        for x in (d if isinstance(d, list) else []):
            if isinstance(x, dict) and x.get('en'):
                idx[x['en']] = (x, rel(f))
    return idx


def keys_of(era):
    """这张牌每条主线四幕的键。只有一条主线的用 n1..n4，几条的用 a1..a4、b1..b4。"""
    out = []
    for k, l in enumerate(era['lines']):
        pre = 'n' if len(era['lines']) == 1 else 'abcdefgh'[k]
        acts = [a.split('｜')[0] for a in l['acts'] if not a.startswith('幕间')]
        out.append((l['name'], [(a, '%s_%s%d' % (era['id'], pre, i + 1)) for i, a in enumerate(acts)]))
    return out


def gods_table():
    rows = open(os.path.join(ROOT, '底稿', '神名', '神名表.tsv'), encoding='utf-8').read().splitlines()
    keys = rows[0].split('\t')
    gods = [dict(zip(keys, r.split('\t'))) for r in rows[1:] if r.strip()]
    show = {}
    for f in ('gods_zheng', 'gods_mo'):
        for x in json.load(open(os.path.join(COMFY, 'epic', 'prompts', f + '.json'), encoding='utf-8')):
            for g in gods:
                if g['神'] and x['name'].endswith(g['神']):
                    show[g['神']] = x['key']
    return gods, show


def bosses():
    out = []
    for part in ('strife_god1', 'strife_god2', 'strife_other'):
        for b in json.load(open(os.path.join(COMFY, 'epic', 'prompts', part + '.json'), encoding='utf-8')):
            pics = [p['key'] for p in b.get('phases', []) if os.path.exists(os.path.join(COMFY, 'out', '史诗战', part, p['key'] + '.png'))]
            names = ['%s %s' % (p['key'], p.get('name', '')) for p in b.get('phases', []) if p['key'] in pics]
            out.append({'part': part, 'block': b['block'], 'tag': b.get('tag') or '', 'pics': names})
    return out


def tasks():
    data = json.load(open(os.path.join(BOOK, 'data', 'strife.json'), encoding='utf-8'))
    cast = cast_index()
    gods, show = gods_table()
    boss = bosses()
    os.makedirs(os.path.join(HERE, '任务单'), exist_ok=True)
    for era in data['eras']:
        pi = era['part']
        path = os.path.join(ROOT, '纷争纪', '纷争纪时段_%s_%s.md' % (NUM[pi], PAGES[pi]))
        src = open(path, encoding='utf-8').read().split('\n')
        heads = [(i + 1, t[3:].strip()) for i, t in enumerate(src) if t.startswith('## ')]
        o = ['# 任务单 %s｜%s %s｜纷争纪 %s%s' % (era['id'], era['label'], era['title'], era['years'], '' if era['years'].endswith('年') else ' 年'), '',
             '- 源稿：`%s`（%d 行，这一页管 %s 这几张牌，只读下面点到的节）' % (rel(path), len(src), '、'.join(e['title'] for e in data['eras'] if e['part'] == pi)),
             '- 这张牌的牌面、牌文：`纷争纪/天黑以后_二十二张_第七版.md` 里“%s”那一节（牌面不用你画，读一遍知道这一段的调子）' % era['title'],
             '- 交：`底稿/门面/小样_纷争纪书/scenes/%s.json`' % era['id'], '']
        o += ['## 主线、各幕和键', '']
        text = ''
        for name, acts in keys_of(era):
            line = [l for l in era['lines'] if l['name'] == name][0]
            at = [n for n, t in heads if '主线｜' + name == t or t.endswith('主线｜' + name)]
            if at:
                nxt = [n for n, t in heads if n > at[0] and not t.startswith('裁定锁')]
                end = nxt[0] - 1 if nxt else len(src)
                text += '\n'.join(src[at[0]:end])
            o.append('### %s（源稿第 %s 行起）' % (name, '、'.join(map(str, at)) or '？'))
            o.append('')
            o.append('题：%s　年份：纷争纪 %s 年' % (line.get('ti', ''), line.get('year', '')))
            o.append('')
            hd = {a.split('｜')[0]: a for a in line['acts']}
            for a, key in acts:
                o.append('- `%s`　%s' % (key, hd[a]))
            for a in line['acts']:
                if a.startswith('幕间'):
                    o.append('- （幕间不配图）%s' % a[:60])
            o.append('')
        o += ['## 这一段的人', '', '年纪是这张牌里他头一条主线开头那一年的，死的时候几岁照源稿算。有键的人出图时拿立绘当长相参考。', '']
        for kind, title in (('cast', '旅伴'), ('meet', '相遇')):
            if not era.get(kind):
                continue
            o.append('### %s' % title)
            o.append('')
            for c in era[kind]:
                at = [n for n, t in heads if c['name'] in t and (t.startswith('旅途同行') or t.endswith('（人物）') or t.startswith('凡世至强'))]
                o.append('- **%s**｜键 `%s`｜%s｜%s 岁%s｜源稿第 %s 行' % (
                    c['name'], c.get('key') or '没有立绘', c.get('race', ''), c.get('age', '？'),
                    '｜这几条主线：' + '、'.join(c['seg']) if c.get('seg') else '', '、'.join(map(str, at[:5])) or '？'))
                x = cast.get(c.get('key') or '')
                if x:
                    e = x[0]
                    o.append('  - who：%s' % e.get('who', '').strip())
                    if e.get('palette'):
                        o.append('  - palette：%s' % e['palette'])
                    flags = [k for k in ('minor', 'teen', 'child') if e.get(k)]
                    o.append('  - 立绘资料：`%s`%s' % (x[1], '（资料标了 %s）' % '、'.join(flags) if flags else ''))
            o.append('')
        leg = [c for c in era.get('legends', []) if c.get('key')]
        if leg:
            o.append('### 这一段在世的传奇里有立绘的（要入画才用，源稿里他们的条目是“凡世至强”和“（人物）”那几节）')
            o.append('')
            o.append('、'.join('%s%s `%s`' % ((c['title'] + '·') if c.get('title') else '', c['name'], c['key']) for c in leg))
            o.append('')
        o += ['## 神、魔神和大东西的参考图', '',
              '`beast` 那一栏填下面的名字（一幅至多一张）。`god_` 打头的是神明显像（那一位全力的样子），`strife_` 打头的是史诗战的图（k 是第几阶，照这一幕它是什么样子挑）。只管样子，画法照光锥。', '']
        named = [g for g in gods if g['神'] and g['神'] in text]
        if named:
            o.append('这几条主线的正文提到的神和魔神：')
            o.append('')
            for g in named:
                o.append('- %s｜%s%s｜显像 %s' % ('魔神' if g['正魔'] == '魔' else ('七支柱' if g['正魔'] == '柱' else '正神'), g['神号'], g['神'],
                                              ('`%s`' % show[g['神']]) if g['神'] in show and os.path.exists(os.path.join(COMFY, 'out', '神明显像', show[g['神']] + '.png')) else '没有'))
            o.append('')
        shorts = [l['name'].split('·', 1)[-1] for l in era['lines']]
        hit = [b for b in boss if any(s in b['block'] for s in shorts) or (b['tag'] and b['tag'] in text and b['pics'])]
        if hit:
            o.append('史诗战里对得上这几条主线的对手（英文设计在 `底稿/状态栏/comfy/epic/prompts/strife_god1.json`、`strife_god2.json`、`strife_other.json` 里同名的 block，design 那一段）：')
            o.append('')
            for b in hit:
                o.append('- %s｜%s' % (b['block'], '、'.join('`%s`' % p.split(' ')[0] + p[len(p.split(' ')[0]):] for p in b['pics']) or '没有图'))
            o.append('')
        if not named and not hit:
            o.append('这一段没有对得上的参考图，照源稿用字写。')
            o.append('')
        o += ['## 源稿的节（跳着读用）', '']
        for n, t in heads:
            o.append('- %d　%s' % (n, t[:60]))
        open(os.path.join(HERE, '任务单', era['id'] + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(o) + '\n')
        print(era['id'], era['title'], len(o), '行', '神', len(named), '对手', len(hit))


if __name__ == '__main__':
    tasks()
