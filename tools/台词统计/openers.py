#!/usr/bin/env python3
"""数开口的第一句：每段对话头一句，和每个人在一段对话里头一回开口，是什么动作。
用法：python3 -I -X utf8 openers.py OUT_DIR"""
import glob, json, os, re, sys
from collections import defaultdict, Counter
OUT = sys.argv[1]
VOC = re.compile(r'^[^，。！？…]{1,8}[，！]')
INTJ = re.compile(r'^(嗯|啊|哦|唔|欸|诶|哈|呼|嘿|咳|哼|呵|哎|唉|嗨|呃|咦|哇|喂|哟)')
TITLE = ('旅行者', '派蒙', '大人', '先生', '小姐', '阁下', '老板', '大哥', '大姐', '姐姐', '哥哥', '朋友', '各位', '诸位', '喂', '这位', '小家伙')
def kind(x):
    first = re.split(r'(?<=[。！？…])', x.strip())[0]
    if INTJ.match(first): return '叹词起头'
    m = VOC.match(first)
    if m and (any(t in m.group(0) for t in TITLE) or len(m.group(0)) <= 5 and m.group(0)[-1] in '，！' and re.match(r'^[一-鿿·「」]{2,6}[，！]$', m.group(0))):
        return '先叫人'
    if first.endswith('？'): return '先发问'
    if first.endswith('！'): return '先喊一句'
    if re.match(r'^(来|走|快|别|不要|请|等|看|听|让|帮|跟|小心|当心|记得|去)', first): return '先叫人做事'
    if re.match(r'^(我|我们|咱)', first): return '先说自己'
    if re.match(r'^(这|那|此|这里|那边|前面|这个|那个)', first): return '先指眼前'
    return '先说事'
talk = defaultdict(list)
for f in glob.glob(os.path.join(OUT, 'lines*.jsonl')):
    for l in open(f, encoding='utf-8'):
        e = json.loads(l)
        if e['src'] in ('quest', 'idle'):
            talk[(e['src'], e['qtype'], e['talk'])].append(e)
scene, first_turn = Counter(), Counter()
by_src = defaultdict(Counter)
opener_sp = Counter()
for k, ls in talk.items():
    ls = [e for e in ls if not e.get('player')]
    if not ls: continue
    opener_sp[ls[0]['speaker']] += 1
    scene[kind(ls[0]['text'])] += 1
    by_src[k[1]][kind(ls[0]['text'])] += 1
    seen = set()
    for e in ls:
        if e['speaker'] in seen: continue
        seen.add(e['speaker']); first_turn[kind(e['text'])] += 1
tot = sum(scene.values())
print('一段对话的头一句，共', tot)
for k, v in scene.most_common(): print(f'  {k} {v/tot:.2f}')
tot2 = sum(first_turn.values())
print('每个人在一段里头一回开口，共', tot2)
for k, v in first_turn.most_common(): print(f'  {k} {v/tot2:.2f}')
print('按来源的头一句')
for s, c in by_src.items():
    t = sum(c.values()); print(' ', s, t, ' '.join(f'{k}{v/t:.2f}' for k, v in c.most_common()))
print('谁最常开场', opener_sp.most_common(15))
