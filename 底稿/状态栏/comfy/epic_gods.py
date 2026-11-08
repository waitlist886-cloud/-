#!/usr/bin/env python3
# 神名清单拆成一位一条（11-07），给写神明显像提示词的子任务；顺带给史诗战那六份输入添“可能是谁”（有立绘的人）。
#   python epic_gods.py
# 写 epic/in/gods_zheng.json（七支柱加正神六十五）、epic/in/gods_mo.json（魔神七十二）；
# 改 epic/in/<份>.json：对手的名字里带着某个有立绘的人的名字，就在那一块添 person_candidates（键、哪一套、名字、出处页），子任务逐个认是不是同一个人。
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, '底稿', '立绘', '神名清单.md')
PILLAR = {'离弦': 'lixian', '负山': 'fushan', '翻页': 'fanye', '返青': 'fanqing', '立边': 'libian', '静光': 'jingguang', '不退': 'butui'}
FIELD = re.compile(r'^- ([^：]{1,16})：(.*)$')


def gods():
    lines = open(SRC, encoding='utf-8').read().split('\n')
    sec = pillar = None
    cur = None
    out = {'七支柱': [], '正神': [], '魔神': []}
    for line in lines:
        if line.startswith('## '):
            sec = '七支柱' if '七支柱' in line else '正神' if '正神' in line else '魔神' if '魔神' in line else None
            cur = None
            continue
        if sec is None:
            continue
        if line.startswith('### '):
            h = line[4:].strip()
            if sec == '七支柱':
                pillar = h.split('·')[0]
                cur = {'name': h.split('·', 1)[1], 'pillar': pillar, 'kind': '七支柱'}
                out[sec].append(cur)
            else:
                pillar = h
                cur = None
            continue
        m = re.match(r'^\*\*(.+?)\*\*\s*$', line)
        if m and sec in ('正神', '魔神'):
            cur = {'name': m.group(1), 'pillar': pillar, 'kind': sec}
            out[sec].append(cur)
            continue
        m = FIELD.match(line)
        if m and cur is not None:
            cur[m.group(1)] = m.group(2).strip()
    n = {}
    for sec, lst in out.items():
        for g in lst:
            p = PILLAR.get(g['pillar'], 'x')
            n[(sec, p)] = n.get((sec, p), 0) + 1
            g['key'] = 'god_%s_%s_%02d' % ({'七支柱': 'p', '正神': 'z', '魔神': 'm'}[sec], p, n[(sec, p)])
    return out


def cast_names():
    """各纪资料里有立绘的人：名字、键、哪一套（cast 下的文件夹，没有就是 1001 那一套）、出处。"""
    out = []
    for p in glob.glob(os.path.join(HERE, 'cast', '**', '*.json'), recursive=True):
        rel = os.path.relpath(p, os.path.join(HERE, 'cast')).replace(os.sep, '/')
        if rel.startswith(('覆盖', '名册')):
            continue
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception:   # noqa: BLE001
            continue
        items = d if isinstance(d, list) else [dict(v, en=k) for k, v in d.items() if isinstance(v, dict)]
        cset = rel.split('/')[0] if '/' in rel else '1001'
        for c in items:
            if isinstance(c, dict) and c.get('name') and c.get('en'):
                folder = os.path.join(HERE, 'out', '立绘_' + cset if cset != '1001' else '立绘_v3', c['en'])
                out.append({'key': c['en'], 'set': cset, 'name': c['name'], 'src': c.get('src', ''),
                            'has_battle': os.path.exists(os.path.join(folder, 'cell_battle.png'))})
    return out


def add_candidates(people):
    for p in sorted(glob.glob(os.path.join(HERE, 'epic', 'in', '*.json'))):
        if os.path.basename(p).startswith('gods_'):
            continue
        d = json.load(open(p, encoding='utf-8'))
        hits = 0
        for b in d:
            head = re.sub(r'^[A-Za-z0-9·\-]+\s*', '', b['block'])
            head = re.sub(r'（.*$', '', head)
            cands = []
            for c in people:
                first = re.sub(r'[（(].*$', '', c['name']).split('·')[0].strip()
                if len(first) >= 2 and first in head and c['has_battle']:
                    cands.append({k: c[k] for k in ('key', 'set', 'name', 'src')})
            b['person_candidates'] = cands
            hits += bool(cands)
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(os.path.basename(p), '有候选的块', hits)


if __name__ == '__main__':
    g = gods()
    os.makedirs(os.path.join(HERE, 'epic', 'in'), exist_ok=True)
    json.dump(g['七支柱'] + g['正神'], open(os.path.join(HERE, 'epic', 'in', 'gods_zheng.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(g['魔神'], open(os.path.join(HERE, 'epic', 'in', 'gods_mo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('七支柱', len(g['七支柱']), '正神', len(g['正神']), '魔神', len(g['魔神']))
    people = cast_names()
    print('有立绘的人', len(people), '其中有战斗格的', sum(c['has_battle'] for c in people))
    add_candidates(people)
