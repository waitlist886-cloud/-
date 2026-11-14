#!/usr/bin/env python3
# 给写场面的人出任务单（scenes/任务单/mNN.md）和示例（scenes/示例_m07.json）。
#   python -I -X utf8 make_tasks.py          出任务单（只用标准库）
#   <带 PIL 的 python> make_tasks.py demo    出示例（要 import gpt_cg）
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
ZG = ['晨祷', '午祷上', '午祷下', '晚祷上', '晚祷下', '夜祷']
SA = ['崛起上', '崛起下', '帝国', '魔族之世', '末年上', '末年下']


def cn(i):
    return NUM[i - 1] if i <= 10 else '十' + NUM[i - 11]


def page_of(eid):
    i = int(eid[1:])
    if i <= 15:
        d = os.path.join(ROOT, '月银纪史诗')
        f = [x for x in os.listdir(d) if x.startswith('第' + cn(i) + '歌_')][0]
        return os.path.join(d, f), '第' + cn(i) + '歌'
    if i <= 21:
        return os.path.join(ROOT, '诸国期', '诸国期时段_%s_%s.md' % (cn(i - 15), ZG[i - 16])), ZG[i - 16]
    return os.path.join(ROOT, '萨尔维斯', '萨尔维斯时段_%s_%s.md' % (cn(i - 21), SA[i - 22])), SA[i - 22]


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
    """这个时代每条主线四幕的键。只有一条主线的用 n1..n4，几条的用 a1..a4、b1..b4。"""
    out = []
    for k, l in enumerate(era['lines']):
        pre = 'n' if len(era['lines']) == 1 else 'abcdefgh'[k]
        acts = [a.split('｜')[0] for a in l['acts'] if not a.startswith('幕间')]
        out.append((l['name'], [(a, '%s_%s%d' % (era['id'], pre, i + 1)) for i, a in enumerate(acts)]))
    return out


def tasks():
    moon = json.load(open(os.path.join(BOOK, 'data', 'moon.json'), encoding='utf-8'))
    cast = cast_index()
    stages = json.load(open(os.path.join(COMFY, 'epic', '阶段表.json'), encoding='utf-8'))
    blocks = []
    for x in stages:
        if x['part'] == 'moon' and x['block'] not in [b['block'] for b in blocks]:
            blocks.append({'block': x['block'], 'text': ''})
        if x['part'] == 'moon':
            blocks[-1]['text'] += x.get('body', '') + x.get('look', '')
    for i, b in enumerate(blocks, 1):
        b['stem'] = 'moon_%03d' % i
        b['pics'] = sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(COMFY, 'out', '史诗战', 'moon', b['stem'] + '_?.png')))
    os.makedirs(os.path.join(HERE, '任务单'), exist_ok=True)
    for era in moon['eras']:
        if era['id'] == 'm07':
            continue
        path, label = page_of(era['id'])
        src = open(path, encoding='utf-8').read().split('\n')
        o = ['# 任务单 %s｜%s %s｜月银纪 %s 年' % (era['id'], era['label'], era['title'], era['years']), '',
             '- 源稿：`%s`（%d 行）' % (rel(path), len(src)),
             '- 交：`底稿/门面/小样_月银纪书/scenes/%s.json`' % era['id'], '']
        o += ['## 主线、各幕和键', '']
        for name, acts in keys_of(era):
            line = [l for l in era['lines'] if l['name'] == name][0]
            at = [i + 1 for i, t in enumerate(src) if t.startswith('## ') and '主线｜' + name in t]
            o.append('### %s（源稿第 %s 行起）' % (name, '、'.join(map(str, at)) or '？'))
            o.append('')
            o.append('题：%s　年份：%s' % (line.get('ti', ''), line.get('year', '')))
            o.append('')
            heads = {a.split('｜')[0]: a for a in line['acts']}
            for a, key in acts:
                o.append('- `%s`　%s' % (key, heads[a]))
            for a in line['acts']:
                if a.startswith('幕间'):
                    o.append('- （幕间不配图）%s' % a[:60])
            o.append('')
        o += ['## 这一段的人', '', '年纪是这一段主线开头那一年的，死的时候几岁照源稿算。有键的人出图时拿立绘当长相参考。', '']
        for kind, title in (('cast', '旅伴'), ('meet', '相遇')):
            if not era.get(kind):
                continue
            o.append('### %s' % title)
            o.append('')
            for c in era[kind]:
                at = [i + 1 for i, t in enumerate(src) if t.startswith('## ') and c['name'] in t]
                o.append('- **%s**｜键 `%s`｜%s｜%s 岁%s｜源稿第 %s 行' % (
                    c['name'], c.get('key') or '没有立绘', c.get('race', ''), c.get('age', '？'),
                    '｜这一条主线：' + c['seg'] if c.get('seg') else '', '、'.join(map(str, at[:4])) or '？'))
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
            o.append('、'.join('%s `%s`' % (c['name'], c['key']) for c in leg))
            o.append('')
        o += ['## 兽', '']
        for b in era.get('beasts', []):
            o.append('- %s｜%s｜%s｜%s' % (b.get('name', ''), b.get('tier', ''), b.get('where', ''), b.get('size', '')))
        at = [i + 1 for i, t in enumerate(src) if t.startswith('## ') and ('灾祸之兽' in t or '魔兽' in t)]
        if at:
            o.append('- 源稿里兽的条目在第 %s 行' % '、'.join(map(str, at)))
        hit = [b for b in blocks if label in b['text']]
        o.append('')
        if hit:
            o.append('这一段牵到的史诗战对手（`beast` 填参考图的名字；英文设计在 `底稿/状态栏/comfy/epic/prompts/moon.json` 里同名的 block）：')
            o.append('')
            for b in hit:
                o.append('- %s｜参考图 %s' % (b['block'], '、'.join('`%s`' % p for p in b['pics']) or '没有'))
        else:
            o.append('这一段没有对得上的史诗战参考图，兽照源稿用字写。')
        o += ['', '## 源稿的节（跳着读用）', '']
        for i, t in enumerate(src):
            if t.startswith('## '):
                o.append('- %d　%s' % (i + 1, t[3:60]))
        open(os.path.join(HERE, '任务单', era['id'] + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(o) + '\n')
        print(era['id'], len(o), '行', '兽图', len(hit))


def demo():
    sys.path.insert(0, COMFY)
    import gpt_cg as G
    table = json.load(open(os.path.join(BOOK, 'cg_table.json'), encoding='utf-8'))
    fates = json.load(open(os.path.join(BOOK, 'fate_table.json'), encoding='utf-8'))['m07']
    out = {'era': 'm07', 'nodes': [], 'fates': fates, 'deaths': [], 'notes': ['这是第七歌做完的样子，照它的写法和详略。beast 那一栏第七歌用的是另一套参考图，这里写成 moon_006_1 示意。']}
    for key, t in table.items():
        if not key.startswith('m07') or t.get('key'):
            continue
        s = G.S[key]
        e = {'key': key}
        if t.get('death'):
            e.update(death=t['death'], name=t['name'], age={'奥斯温': 19, '罗南': 18, '麦伦': 27}[t['death']], minor=False)
        else:
            e.update(line=t['line'], act=t['act'], name=t['name'])
        e['style'] = list(s['style'])
        if s.get('who'):
            e['who'] = [list(w) for w in s['who']]
        if s.get('dragon'):
            e['beast'] = 'moon_006_2' if 'fenyuan2' in str(s.get('extra')) else 'moon_006_1'
        e.update(light=s['light'], camera=s['camera'], text=s['text'])
        if s.get('raw'):
            e['raw'] = True
        (out['deaths'] if t.get('death') else out['nodes']).append(e)
    open(os.path.join(HERE, '示例_m07.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('写了 示例_m07.json', len(out['nodes']), '幅节点', len(out['deaths']), '幅死的那一刻')


if __name__ == '__main__':
    demo() if sys.argv[1:] == ['demo'] else tasks()
