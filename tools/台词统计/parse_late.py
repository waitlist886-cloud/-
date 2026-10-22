#!/usr/bin/env python3
"""把补抓的 BinOutput/Talk/Quest 子任务文件解析成和 build_corpus.py 同样格式的台词。
用法：python3 -I -X utf8 parse_late.py RAW_DIR TALK_DIR OUT_DIR
字段名是混淆过的，按「值落在文本表里」自动认：内容、说话人名、下一句、角色。
"""
import glob, json, os, re, sys
from collections import defaultdict, Counter
RAW, TALK, OUT = sys.argv[1:4]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
TM = {}
for n in ('TextMapCHS.json', 'TextMap_MediumCHS.json'):
    TM.update(json.load(open(os.path.join(RAW, n), encoding='utf-8')))
def clean(s):
    if not s: return ''
    s = s.replace('\\n', '\n').replace('{NICKNAME}', '旅行者')
    s = re.sub(r'\{PLAYERAVATAR#SEXPRO\[[^\]]*\]\}', '她', s)
    s = re.sub(r'\{MATEAVATAR#SEXPRO\[[^\]]*\]\}', '哥哥', s)
    s = re.sub(r'\{F#([^}]*)\}\{M#[^}]*\}', r'\1', s)
    s = re.sub(r'\{M#[^}]*\}\{F#([^}]*)\}', r'\1', s)
    s = re.sub(r'\{LAYOUT_MOBILE#[^}]*\}\{LAYOUT_PC#([^}]*)\}\{LAYOUT_PS#[^}]*\}', r'\1', s)
    s = re.sub(r'</?color[^>]*>|</?i>|</?b>', '', s)
    s = re.sub(r'\{[A-Z_]+#[^}]*\}', '', s)
    return s.lstrip('#').strip()
t = lambda h: clean(TM.get(str(h), ''))
npc = {e['id']: t(e.get('nameTextMapHash')) for e in json.load(open(os.path.join(RAW, 'NpcExcelConfigData.json'), encoding='utf-8'))}
mq = {e['id']: e for e in json.load(open(os.path.join(RAW, 'MainQuestExcelConfigData.json'), encoding='utf-8'))}

def detect(dl):
    hit, tot, roles, nexts, ids = Counter(), Counter(), Counter(), Counter(), Counter()
    for e in dl:
        for k, v in e.items():
            if isinstance(v, dict) and '_type' in v: roles[k] += 1
            elif isinstance(v, list) and v and all(isinstance(x, int) for x in v): nexts[k] += 1
            elif isinstance(v, int) and v > 1000:
                tot[k] += 1
                if str(v) in TM: hit[k] += 1
                else: ids[k] += 1
    ranked = sorted((k for k in tot if hit[k]), key=lambda k: -hit[k])
    content = ranked[0] if ranked else None
    name = ranked[1] if len(ranked) > 1 else None
    return dict(role=roles.most_common(1)[0][0] if roles else None, next=nexts.most_common(1)[0][0] if nexts else None,
                content=content, name=name, id=ids.most_common(1)[0][0] if ids else None)

lines = open(os.path.join(OUT, 'lines_late.jsonl'), 'w', encoding='utf-8')
byq = defaultdict(list)
for f in sorted(glob.glob(os.path.join(TALK, '*.json')), key=lambda p: int(os.path.basename(p)[:-5])):
    sub = int(os.path.basename(f)[:-5]); main = sub // 100
    d = json.load(open(f, encoding='utf-8'))
    dl = next((v for v in d.values() if isinstance(v, list) and v and isinstance(v[0], dict)), [])
    if not dl: continue
    k = detect(dl)
    for e in dl:
        txt = t(e.get(k['content'])) if k['content'] else ''
        if not txt: continue
        role = e.get(k['role'], {}) if k['role'] else {}
        ty, rid = role.get('_type', ''), role.get('_id', '')
        nm = t(e.get(k['name'])) if k['name'] else ''
        if ty == 'TALK_ROLE_PLAYER': sp = '旅行者'
        elif 'BLACK_SCREEN' in ty: sp = '（黑屏旁白）'
        elif nm: sp = nm
        elif str(rid).isdigit(): sp = npc.get(int(rid)) or f'NPC{rid}'
        else: sp = '（未知）'
        byq[main].append((sub, sp, txt, ty == 'TALK_ROLE_PLAYER'))
QT = {'AQ': '魔神任务', 'LQ': '传说任务'}
outs = {k: open(os.path.join(OUT, f'quests_{k}_late.md'), 'w', encoding='utf-8') for k in QT}
for k, f in outs.items(): f.write(f'# {QT[k]}对话，后几国补抓（本地研读用）\n\n')
for main in sorted(byq):
    e = mq.get(main, {}); ty = e.get('type', 'AQ')
    if ty not in outs: continue
    title = t(e.get('titleTextMapHash')) or str(main)
    f = outs[ty]; f.write(f'## {title}（{main}）\n\n'); cur = None
    for sub, sp, txt, isp in byq[main]:
        if sub != cur: f.write(f'\n### 子任务 {sub}\n\n'); cur = sub
        f.write(f'{"〔选项〕" if isp else ""}{sp}：{txt}\n')
        lines.write(json.dumps(dict(src='quest', qtype=ty, qid=main, qtitle=title, talk=sub, speaker=sp, text=txt, player=isp), ensure_ascii=False) + '\n')
    f.write('\n')
print('ok', sum(len(v) for v in byq.values()))
