#!/usr/bin/env python3
# 把一份新写的场面（frag_*.json：{"nodes":[…], "notes":[…可不写]}）并进 scenes/nN.json。键已经有的不覆盖（加 --replace 才换）。
#   python -I -X utf8 merge.py frag_q3e.json [--replace]
# 写回去的样子照原来：一幕一行。
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SC = 'E:/aldran_art/底稿/门面/小样_迷宫纪书/scenes'
ORDER = ['key', 'line', 'act', 'name', 'lead', 'style', 'who', 'row', 'beast', 'like', 'young', 'minor', 'noface', 'raw', 'light', 'camera', 'text', 'note']


def dump(d):
    out = ['{', ' "era": %s,' % json.dumps(d['era'], ensure_ascii=False), ' "nodes": [']
    out.append(',\n'.join('  ' + json.dumps(s, ensure_ascii=False) for s in d['nodes']))
    out.append(' ],')
    out.append(' "notes": [')
    out.append(',\n'.join('  ' + json.dumps(s, ensure_ascii=False) for s in d.get('notes', [])))
    out.append(' ]')
    out.append('}')
    return '\n'.join(out) + '\n'


def main():
    frag = json.load(open(sys.argv[1], encoding='utf-8'))
    rep = '--replace' in sys.argv
    nodes = frag['nodes'] if isinstance(frag, dict) else frag
    notes = frag.get('notes', []) if isinstance(frag, dict) else []
    pages = {}
    for s in nodes:
        pages.setdefault(s['key'][1], []).append(s)
    for n, new in pages.items():
        p = '%s/n%s.json' % (SC, n)
        d = json.load(open(p, encoding='utf-8'))
        have = {s['key']: i for i, s in enumerate(d['nodes'])}
        for s in new:
            s = {k: s[k] for k in ORDER if k in s} | {k: v for k, v in s.items() if k not in ORDER}
            if s['key'] in have:
                if not rep:
                    print('已经有了，没动：', s['key'])
                    continue
                d['nodes'][have[s['key']]] = s
                print('换了', s['key'])
            else:
                d['nodes'].append(s)
                print('添了', s['key'], s['name'], len(s['text'].split()), '词')
        d['nodes'].sort(key=lambda s: (s['key'][:-1], int(s['key'][-1])))
        for t in notes:
            if t not in d.setdefault('notes', []):
                d['notes'].append(t)
        open(p, 'w', encoding='utf-8', newline='\n').write(dump(d))
        json.load(open(p, encoding='utf-8'))


main()
