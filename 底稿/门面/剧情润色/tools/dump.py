#!/usr/bin/env python3
# 门面剧情润色：四纪交稿合成一份给人看的 md（门面剧情润色_全稿.md），也给 ngram 用。
import glob, json, os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
D = os.path.join(ROOT, '底稿', '门面', '剧情润色')
out = ['# 门面剧情润色｜全稿（11-21）', '', '四纪 177 条主线：介绍一段，每幕“幕名 — 描述”。稿子在 底稿/门面/剧情润色/<纪>/<时代 id>.json。', '']
for ji in ['月银纪', '纷争纪', '山铜纪', '迷宫纪']:
    out += ['## ' + ji, '']
    for fp in sorted(glob.glob(os.path.join(D, ji, '*.json'))):
        J = json.load(open(fp, encoding='utf-8'))
        for nm, v in J.items():
            out += ['### %s｜%s%s' % (os.path.basename(fp)[:-5], nm, ('　【' + v['task'] + '】') if v.get('task') else ''), '', '> ' + v['intro'], '']
            out += ['- %s｜%s — %s' % (a['tag'], a['name'], a['desc']) for a in v['acts']]
            out.append('')
open(os.path.join(ROOT, '门面剧情润色_全稿.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print(len(out), '行')
