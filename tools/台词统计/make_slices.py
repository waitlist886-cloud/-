#!/usr/bin/env python3
"""把语料切成几份给细读用。用法：python3 -I -X utf8 make_slices.py OUT_DIR RAW_DIR SLICE_DIR"""
import json, os, re, sys, random
from collections import defaultdict
OUT, RAW, SL = sys.argv[1:4]
random.seed(7)
TM = {}
for n in ('TextMapCHS.json', 'TextMap_MediumCHS.json'):
    TM.update(json.load(open(os.path.join(RAW, n), encoding='utf-8')))
t = lambda h: TM.get(str(h), '').replace('\\n', ' ')
avatars = {e['id']: t(e.get('nameTextMapHash')) for e in json.load(open(os.path.join(RAW, 'AvatarExcelConfigData.json'), encoding='utf-8'))}
meta = {}
for e in json.load(open(os.path.join(RAW, 'FetterInfoExcelConfigData.json'), encoding='utf-8')):
    nm = avatars.get(e['avatarId'], '')
    if nm:
        meta[nm] = (t(e.get('avatarTitleTextMapHash')), t(e.get('avatarNativeTextMapHash')), e.get('avatarAssocType', '').replace('ASSOC_TYPE_', ''), t(e.get('avatarVisionBeforTextMapHash')), t(e.get('avatarDetailTextMapHash')))
with open(os.path.join(SL, 'characters.md'), 'w', encoding='utf-8') as f:
    f.write('# 角色速查：名字｜称号｜所属｜地区｜神之眼｜游戏内简介\n\n')
    for nm, m in meta.items():
        f.write(f'- {nm}｜' + '｜'.join(m) + '\n')
V = defaultdict(lambda: defaultdict(list))
for l in open(os.path.join(OUT, 'lines.jsonl'), encoding='utf-8'):
    e = json.loads(l)
    if e['src'] != 'voice' or e['speaker'] == '旅行者':
        continue
    ti = re.sub(r'…+$', '', e['qtitle']); sp = e['speaker']
    if e['qtype'] == '战斗': k = 'V4'
    elif re.match(r'^(初次见面|闲聊|下雨|雨过天晴|下雪|打雷|阳光|刮大风|起风|在沙漠|暴风|早上好|中午好|晚上好|晚安)', ti): k = 'V1'
    elif re.match(r'^关于(我们|「神之眼」)', ti) or ti.startswith(f'关于{sp}') or re.match(r'^(有什么想要分享|感兴趣的见闻|想要了解|喜欢的食物|讨厌的食物|收到赠礼|生日|突破的感受)', ti) or re.search(r'的(爱好|烦恼)', ti): k = 'V2'
    elif ti.startswith('关于'): k = 'V3'
    else: k = 'V2'
    V[k][sp].append(f'〔{ti}〕{e["text"]}')
for k, d in V.items():
    with open(os.path.join(SL, f'{k}.md'), 'w', encoding='utf-8') as f:
        for sp, ls in d.items():
            m = meta.get(sp)
            f.write(f'## {sp}' + (f'（{m[0]}｜{m[1]}）' if m else '') + '\n' + '\n'.join(ls) + '\n\n')
# 剧情抽样
def pick_quests(path, titles):
    txt = open(path, encoding='utf-8').read()
    parts = re.split(r'(?m)^## ', txt)
    keep = [p for p in parts[1:] if any(p.startswith(ti) for ti in titles)]
    return '\n'.join('## ' + p for p in keep)
AQ = ['送仙', '归终', '孤芳', '御前决斗', '愿望', '已然来临的花神诞祭', '因果命运的花神诞祭', '如凯旋的英雄一般', '审判日', '终幕礼', '黑潮与白露的歌剧', '当一切镌刻成碑', '众望所归', '在终曲之前', '尾声的尾声', '幕切——倾奇之末', '渊底不期的再会']
s1 = pick_quests(os.path.join(OUT, 'quests_AQ.md'), AQ) + '\n' + pick_quests(os.path.join(OUT, 'quests_AQ_late.md'), AQ)
open(os.path.join(SL, 'S1_AQ.md'), 'w', encoding='utf-8').write('# 魔神任务抽样\n\n' + s1)
lq = open(os.path.join(OUT, 'quests_LQ.md'), encoding='utf-8').read() + open(os.path.join(OUT, 'quests_LQ_late.md'), encoding='utf-8').read()
parts = re.split(r'(?m)^## ', lq)[1:]
random.shuffle(parts)
s2, size = [], 0
for p in parts:
    if size > 330000: break
    s2.append('## ' + p); size += len(p)
open(os.path.join(SL, 'S2_LQ.md'), 'w', encoding='utf-8').write('# 传说任务抽样\n\n' + '\n'.join(s2))
idle = re.split(r'(?m)^### ', open(os.path.join(OUT, 'npc_idle.md'), encoding='utf-8').read())[1:]
random.shuffle(idle)
wq = re.split(r'(?m)^## ', open(os.path.join(OUT, 'quests_WQ.md'), encoding='utf-8').read())[1:]
random.shuffle(wq)
iq = re.split(r'(?m)^## ', open(os.path.join(OUT, 'quests_IQ.md'), encoding='utf-8').read())[1:]
random.shuffle(iq)
rem = open(os.path.join(OUT, 'reminders.md'), encoding='utf-8').read().splitlines()[2:]
def take(parts, cap, prefix):
    out, size = [], 0
    for p in parts:
        if size > cap: break
        out.append(prefix + p); size += len(p)
    return '\n'.join(out)
s3 = '# NPC 闲谈抽样\n\n' + take(idle, 130000, '### ') + '\n\n# 世界任务抽样\n\n' + take(wq, 110000, '## ') + '\n\n# 委托抽样\n\n' + take(iq, 50000, '## ') + '\n\n# 野外提示语抽样\n\n' + '\n'.join(random.sample(rem, 900))
open(os.path.join(SL, 'S3_NPC.md'), 'w', encoding='utf-8').write(s3)
rd = re.split(r'(?m)^## ', open(os.path.join(OUT, 'readables.md'), encoding='utf-8').read())[1:]
random.shuffle(rd)
s4 = '# 读物抽样（书信、日记、笔记、留言、告示）\n\n' + take(rd, 260000, '## ') + '\n\n' + open(os.path.join(OUT, 'mails.md'), encoding='utf-8').read()
open(os.path.join(SL, 'S4_TEXT.md'), 'w', encoding='utf-8').write(s4)
print('ok')
