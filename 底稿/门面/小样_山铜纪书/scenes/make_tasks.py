#!/usr/bin/env python3
# 给写场面的人出任务单（scenes/任务单/pN.md）：这一页的源稿在哪、主线各幕和键、这一段的碑、这一段的人和立绘键、魔神的显像、史诗战里这一段的对手。
#   python -I -X utf8 make_tasks.py          出六页的任务单（只用标准库，先跑 build_data.py）
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
NUM = '一二三四五六'
PAGES = ['犁的年月', '长夜的年月', '白鸦的年月', '黎明的年月', '七城的年月', '麦的年月']
SIDE = {'west': '墙北（事出在墙西）', 'east': '墙南（事出在墙东）', 'wall': '墙脚（墙上的事，两边都有份）'}


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


# 后添的主线钉死键的字母，别的主线照年份顺着排、跳过这几个字母，原来那些主线的键照旧（11-14 第五页插进三段）
LATE = {'p5': {'七城的年月·门楣': 'k', '七城的年月·分潮': 'l', '七城的年月·开岭': 'm'}}


def line_letters(era):
    late = LATE.get(era['id'], {})
    free = [c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in late.values()]
    out, i = [], 0
    for l in era['lines']:
        if l['name'] in late:
            out.append(late[l['name']])
        else:
            out.append(free[i])
            i += 1
    return out


def keys_of(era):
    """这一页每条主线各幕的键。只有一条主线的用 n1..n4，几条的用 a1..a4、b1..b4……（幕间不配）。"""
    out = []
    lets = line_letters(era)
    for k, l in enumerate(era['lines']):
        pre = 'n' if len(era['lines']) == 1 else lets[k]
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


def tasks():
    data = json.load(open(os.path.join(BOOK, 'data', 'bronze.json'), encoding='utf-8'))
    cast = cast_index()
    gods, show = gods_table()
    os.makedirs(os.path.join(HERE, '任务单'), exist_ok=True)
    for era in data['eras']:
        pi = era['no'] - 1
        path = os.path.join(ROOT, '山铜纪', '山铜纪时段_%s_%s.md' % (NUM[pi], PAGES[pi]))
        src = open(path, encoding='utf-8').read().split('\n')
        heads = [(i + 1, t[3:].strip()) for i, t in enumerate(src) if t.startswith('## ')]
        o = ['# 任务单 %s｜%s｜山铜纪 %s 年｜%s《%s》' % (era['id'], era['title'], era['years'], era['chap'], era['chapName']), '',
             '- 源稿：`%s`（%d 行，只读下面点到的节）' % (rel(path), len(src)),
             '- 这一章：《%s》｜%s' % (era['chapName'], era['chapDesc']),
             '- 交：`底稿/门面/小样_山铜纪书/scenes/%s.json`' % era['id'], '']
        o += ['## 这一段的碑（不用你画，读一遍知道这一段落在哪几件事上；收束那一幅可以落在碑上）', '']
        for s in era['steles']:
            at = [n for n, t in heads if t == '山铜纪·碑｜' + s['name']]
            o.append('- **%s**｜%s 年立｜%s｜源稿第 %s 行｜%s' % (s['name'], s['year'], SIDE[s['side']], '、'.join(map(str, at)) or '？', s.get('where', '')))
        o.append('')
        o += ['## 主线、各幕和键', '']
        text = ''
        for name, acts in keys_of(era):
            line = [l for l in era['lines'] if l['name'] == name][0]
            at = [n for n, t in heads if t == '山铜纪·主线｜' + name]
            if at:
                nxt = [n for n, t in heads if n > at[0] and not t.startswith('裁定锁')]
                end = nxt[0] - 1 if nxt else len(src)
                text += '\n'.join(src[at[0]:end])
            o.append('### %s（源稿第 %s 行起）' % (name, '、'.join(map(str, at)) or '？'))
            o.append('')
            o.append('任务名：【%s】　%s　年份：山铜纪 %s 年' % (line.get('task', ''), line.get('chap', ''), line.get('year', '')))
            o.append('')
            hd = {a.split('｜')[0]: a for a in line['acts']}
            for a, key in acts:
                o.append('- `%s`　%s' % (key, hd[a]))
            for a in line['acts']:
                if a.startswith('幕间'):
                    o.append('- （幕间不配图）%s' % a[:60])
            o.append('')
        o += ['## 这一段的人', '', '年纪是这一页里他头一条主线开头那一年的，死的时候几岁照源稿算。有键的人出图时拿立绘当长相参考。', '']
        for kind, title in (('cast', '旅伴'), ('meet', '相遇')):
            if not era.get(kind):
                continue
            o.append('### %s' % title)
            o.append('')
            for c in era[kind]:
                at = [n for n, t in heads if c['name'] in t and (t.startswith('旅途同行') or t.endswith('（人物）'))]
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
            o.append('### 这一段在世的传奇里有立绘的（要入画才用）')
            o.append('')
            o.append('、'.join('%s%s `%s`' % ((c['title'] + '·') if c.get('title') else '', c['name'], c['key']) for c in leg))
            o.append('')
        o += ['## 魔神、对手和大东西的参考图', '',
              '`beast` 那一栏填下面的名字（一幅至多一张）。`god_` 打头的是神明显像（那一尊全力的样子），`bronze_` 打头的是史诗战的图（末一位是第几阶，照这一幕它是什么样子挑）。只管样子，画法照光锥。', '']
        named = [g for g in gods if g['神'] and g['神'] in text and g['正魔'] == '魔']
        if named:
            o.append('这几条主线的正文提到的魔神：')
            o.append('')
            for g in named:
                o.append('- %s%s｜显像 %s' % (g['神号'], g['神'], ('`%s`' % show[g['神']]) if g['神'] in show and os.path.exists(os.path.join(COMFY, 'out', '神明显像', show[g['神']] + '.png')) else '没有'))
            o.append('')
        if era.get('bosses'):
            o.append('史诗战里这一段的对手（英文设计在 `底稿/状态栏/comfy/epic/prompts/bronze.json` 里同名的 block，design 那一段；名号和本体在 `底稿/立绘/史诗战名号/山铜纪.md`）：')
            o.append('')
            for b in era['bosses']:
                o.append('- %s %s（%s 年）｜%s｜%s' % (b['code'], b['name'], b['year'], b['what'], '、'.join('`%s` %s' % (k, p) for k, p in zip(b['imgs'], b['phases'])) or '没有图'))
            o.append('')
        if not named and not era.get('bosses'):
            o.append('这一段没有对得上的参考图，照源稿用字写。')
            o.append('')
        o += ['## 源稿的节（跳着读用）', '']
        for n, t in heads:
            o.append('- %d　%s' % (n, t[:60]))
        open(os.path.join(HERE, '任务单', era['id'] + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(o) + '\n')
        print(era['id'], era['title'], len(o), '行', '魔神', len(named), '对手', len(era.get('bosses', [])), '节点', sum(len(a) for _, a in keys_of(era)))


if __name__ == '__main__':
    tasks()
