# -*- coding: utf-8 -*-
"""卡片跟提交里的比，数一数改了什么（给发布说明和 CLAUDE.md 用）。
  python -I -X utf8 底稿/门面/卡片/工具/card_stats.py"""
import io, json, os, subprocess, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..')).replace('\\', '/') + '/'
D = '底稿/门面/卡片/'
tot = dict(files=0, new=0, gone=0, to_meet=0, to_cast=0, star=0, starp=0, tags=0, head=0, bg=0, other=0, people=0)
per = {}
for era in ['月银纪', '纷争纪', '山铜纪', '迷宫纪']:
    p = dict(tot); [p.__setitem__(k, 0) for k in p]
    for fn in sorted(os.listdir(ROOT + D + era)):
        if not fn.endswith('.json'):
            continue
        rel = D + era + '/' + fn
        new = json.load(open(ROOT + rel, encoding='utf-8'))
        r = subprocess.run(['git', '-C', ROOT, 'show', 'HEAD:' + rel], capture_output=True)
        old = json.loads(r.stdout.decode('utf-8')) if r.returncode == 0 else {'lines': {}, 'people': {}}
        if new == old:
            continue
        p['files'] += 1
        A, B = old.get('people', {}), new.get('people', {})
        p['new'] += len(set(B) - set(A)); p['gone'] += len(set(A) - set(B))
        for n in set(A) & set(B):
            a, b = A[n], B[n]
            if a == b:
                continue
            p['people'] += 1
            if a.get('kind') != b.get('kind'):
                p['to_meet' if b.get('kind') == 'meet' else 'to_cast'] += 1
            sa, sb = a.get('stars') or [], b.get('stars') or []
            if sa != sb:
                p['starp'] += 1
                p['star'] += max(len(sa), len(sb)) if len(sa) != len(sb) else sum(1 for x, y in zip(sa, sb) if x != y)
            if a.get('tags') != b.get('tags'):
                p['tags'] += 1
            if a.get('head') != b.get('head'):
                p['head'] += 1
            if a.get('bg') != b.get('bg'):
                p['bg'] += 1
    per[era] = p
    for k in tot:
        tot[k] += p[k]
    print(era, p)
print('合计', tot)
