#!/usr/bin/env python3
# 把播放器的源稿接进外壳（11-27）：bgm_shell.js → 小样_外壳/shell.js 的 // <bgm> … // </bgm>，bgm_shell.css → shell.css 的 /* <bgm> */ … /* </bgm> */；
# 再照 make_bgm.py 写下的 bgm_tracks.json 出 小样_外壳/data/bgm.json（场景到文件、曲名、循环点、场景名）。
#   python -I -X utf8 底稿/门面/载入页/音乐/sync_bgm.py
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SHELL = os.path.normpath(os.path.join(HERE, '..', '..', '小样_外壳'))


def splice(dst, src, a, b):
    s = open(dst, encoding='utf-8').read()
    body = open(src, encoding='utf-8').read().strip('\n')
    i = s.index(a) + len(a); j = s.index(b)
    new = s[:i] + '\n' + body + '\n' + s[j:]
    if new != s:
        open(dst, 'w', encoding='utf-8', newline='').write(new)
    print(os.path.basename(dst), '换了' if new != s else '没变')


splice(os.path.join(SHELL, 'shell.js'), os.path.join(HERE, 'bgm_shell.js'), '// <bgm>', '// </bgm>')
splice(os.path.join(SHELL, 'shell.css'), os.path.join(HERE, 'bgm_shell.css'), '/* <bgm> */', '/* </bgm> */')
T = json.load(open(os.path.join(HERE, 'bgm_tracks.json'), encoding='utf-8'))
LABEL = {'table': '死之神殿', 'gate': '死之神殿', 'moon': '月银纪', 'strife': '纷争纪', 'bronze': '山铜纪', 'maze': '迷宫纪·前传', 'now': '迷宫纪·此刻', 'library': '大图书馆', 'build': '建档'}
scenes = {'gate': T['gate']['src'], 'table': T['gate']['src']}
for k in ('moon', 'strife', 'bronze', 'maze', 'now', 'library', 'build'):
    scenes[k] = T[k]['src']
conf = {
    '说明': '门面的背景音乐（11-27 起是 Suno 定稿的八首）。scenes：场景到文件（gate 是载入页，table 是死之神殿的牌桌，跟 gate 同一首；moon、strife、bronze、maze、now 是五本书，library 是大图书馆，build 是建档）。'
          'tracks：每个文件的曲名（播放器上显示英文原名）、循环点 loop [X, N]（放到 N 秒样本级跳回 X 秒，make_bgm.py 量的，文件末尾已经跟前奏交叉好了）。labels：场景给人看的名字（播放器曲名底下那一行）。'
          '文件在 assets/bgm/，图床上另放一段 front_bgm（地址照 data/bgm_cdn.json 的提交号换）。vol 是曲子本身的音量（再乘播放器上的音量），fade 是换曲交叉淡入淡出的秒数。off 为 true 时整个不放、喇叭不露。'
          '这一份是 底稿/门面/载入页/音乐/sync_bgm.py 照 bgm_tracks.json 出的。',
    'vol': 0.5, 'fade': 2, 'off': False,
    'scenes': scenes,
    'labels': LABEL,
    'tracks': {T[k]['src']: {'title': T[k]['from'][:-4], 'loop': T[k]['loop'], 'scene': T[k]['说']} for k in T},
}
p = os.path.join(SHELL, 'data', 'bgm.json')
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(conf, ensure_ascii=False, indent=1) + '\n')
print('bgm.json 写好了', len(conf['tracks']), '首')
