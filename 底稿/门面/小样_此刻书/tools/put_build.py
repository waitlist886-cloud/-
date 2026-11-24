#!/usr/bin/env python3
# 此刻那一本接建档（11-24）：把迷宫纪 1001 年的建档资料写进 小样_外壳/data/build.json 的“此刻那一格”。只动这两处，别的一个字不碰：
#   1. eras.maze.periods 里 id 为 1001 的那一段：种族、出身册子、本事照垂暮的年月（1001 页建档器的种族就是这十二族，见 old1001.html 的 raceList），
#      note 写这一年。外壳的建档照迷宫纪走（book 照旧是 maze，at 是 1001），420 年以后的面板、七阶旅印、命路就职都照迷宫纪那一套。
#   2. eras.maze.now：此刻那一本的十处起点（1001 页建档器的 arrivalSites，字照门面口气重写过，src/road_text.json 的 sites）。
#      书里挑了哪一处，enter 消息带 line = '迷宫纪1001年·<起点>'、site、ti，凭证头一行就是 纪元：迷宫纪1001年｜开局时段：<起点>。
#   python -I -X utf8 底稿/门面/小样_此刻书/tools/put_build.py
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)
P = os.path.normpath(os.path.join(BOOK, '..', '小样_外壳', 'data', 'build.json'))

D = json.load(open(P, encoding='utf-8'))
E = D['eras']['maze']
cm = next(p for p in E['periods'] if p['id'] == 'chuimu')
p = next(p for p in E['periods'] if p['id'] == '1001')
p.update(name='此刻', sheet=cm['sheet'], races=list(cm['races']), absent=[], skills=list(cm['skills']), race_notes={},
         note='黑潮退去的第三十一年，两位王各守半块大陆，剑都在鞘里。公会的面板照得出位阶，旅印分七阶，十八岁成年登记、觉醒面板。山里的兽群这一年成片下山。')
rt = json.load(open(os.path.join(BOOK, 'src', 'road_text.json'), encoding='utf-8'))
E['now'] = {'name': '此刻', 'year': 1001, 'line_prefix': '迷宫纪1001年·',
            'note': '此刻那一本的十处起点。书里挑一处，enter 带 at=1001、line=迷宫纪1001年·<起点>、site=<起点>、ti=<那一处的一句>；凭证头一行 纪元：迷宫纪1001年｜开局时段：<起点>。',
            'sites': rt['sites']}
s = json.dumps(D, ensure_ascii=False, indent=1) + '\n'
open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('build.json：1001 那一段', len(p['races']), '族', len(p['skills']), '样本事；起点', len(rt['sites']), '处')
