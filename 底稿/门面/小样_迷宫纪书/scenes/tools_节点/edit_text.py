#!/usr/bin/env python3
# 改场面稿里某一幅的 text：python edit_text.py edits.json
# edits.json: [{"key": "q1_b4", "old": "...", "new": "...", "note_add": "..."}]，old 必须在 text 里正好出现一回；old 为空就把 new 接在 text 末尾
import json
import sys
_src = open('E:/aldran_art/底稿/门面/小样_迷宫纪书/scenes/tools_节点/merge.py', encoding='utf-8').read()
_ns = {}
exec(_src[_src.index('def dump'):_src.index('def main')], {'json': json}, _ns)
dump = _ns['dump']

SC = 'E:/aldran_art/底稿/门面/小样_迷宫纪书/scenes'
edits = json.load(open(sys.argv[1], encoding='utf-8'))
by_page = {}
for e in edits:
    by_page.setdefault(e['key'][1], []).append(e)
for n, es in by_page.items():
    p = '%s/n%s.json' % (SC, n)
    d = json.load(open(p, encoding='utf-8'))
    idx = {s['key']: s for s in d['nodes']}
    for e in es:
        s = idx[e['key']]
        if e.get('old'):
            assert s['text'].count(e['old']) == 1, (e['key'], s['text'].count(e['old']))
            s['text'] = s['text'].replace(e['old'], e['new'])
        else:
            s['text'] = s['text'].rstrip() + ' ' + e['new']
        if e.get('note_add'):
            s['note'] = s.get('note', '') + e['note_add']
        print('改了', e['key'])
    open(p, 'w', encoding='utf-8', newline='\n').write(dump(d))
