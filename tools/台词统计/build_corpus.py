#!/usr/bin/env python3
"""把 AnimeGameData 的几张表拼成带说话人的中文台词语料。

用法：python3 -I -X utf8 build_corpus.py RAW_DIR OUT_DIR
产物：
  lines.jsonl        每行一句：src, qtype, qid, qtitle, talk, speaker, text
  voice.md           角色语音（按角色，带称号、所属、神之眼）
  quests_<类型>.md   任务对话（AQ 魔神、LQ 传说、WQ 世界、EQ 活动、IQ 委托）
  npc_idle.md        不挂任务的 NPC 闲谈
  reminders.md       野外提示语（说话人：一句）
  mails.md           邮件
语料版权归米哈游，只在本地研读手法。
"""
import json, os, re, sys
from collections import defaultdict

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

def load(name):
    with open(os.path.join(RAW, name), encoding='utf-8') as f:
        return json.load(f)

TM = {}
for n in ('TextMapCHS.json', 'TextMap_MediumCHS.json'):
    TM.update(load(n))

def clean(s):
    if not s:
        return ''
    s = s.replace('\\n', '\n').replace('{NICKNAME}', '旅行者')
    s = re.sub(r'\{PLAYERAVATAR#SEXPRO\[[^|\]]*\|([^\]]*)\]\}', lambda m: '她' if 'SHE' in m.group(1) else ('妹妹' if 'SISTER' in m.group(1) else '她'), s)
    s = re.sub(r'\{MATEAVATAR#SEXPRO\[[^|\]]*\|([^\]]*)\]\}', lambda m: '哥哥' if 'BROTHER' in m.group(0) else '他', s)
    s = re.sub(r'\{F#([^}]*)\}\{M#[^}]*\}', r'\1', s)
    s = re.sub(r'\{M#[^}]*\}\{F#([^}]*)\}', r'\1', s)
    s = re.sub(r'\{LAYOUT_MOBILE#[^}]*\}\{LAYOUT_PC#([^}]*)\}\{LAYOUT_PS#[^}]*\}', r'\1', s)
    s = re.sub(r'</?color[^>]*>', '', s)
    s = re.sub(r'</?i>|</?b>', '', s)
    s = re.sub(r'\{[A-Z_]+#[^}]*\}', '', s)
    return s.strip()

def t(h):
    return clean(TM.get(str(h), ''))

npc = {e['id']: t(e.get('nameTextMapHash')) for e in load('NpcExcelConfigData.json')}
avatars = {e['id']: e for e in load('AvatarExcelConfigData.json')}
aname = {i: t(e.get('nameTextMapHash')) for i, e in avatars.items()}
info = {e['avatarId']: e for e in load('FetterInfoExcelConfigData.json')}

out_lines = open(os.path.join(OUT, 'lines.jsonl'), 'w', encoding='utf-8')
def emit(**kw):
    out_lines.write(json.dumps(kw, ensure_ascii=False) + '\n')

# 角色语音
fet = defaultdict(list)
for e in load('FettersExcelConfigData.json'):
    fet[e['avatarId']].append(e)
with open(os.path.join(OUT, 'voice.md'), 'w', encoding='utf-8') as f:
    f.write('# 原神角色语音（本地研读用）\n\n')
    for aid in sorted(fet, key=lambda a: (a not in info, a)):
        nm = aname.get(aid) or str(aid)
        inf = info.get(aid, {})
        meta = '｜'.join(x for x in [t(inf.get('avatarTitleTextMapHash')), t(inf.get('avatarNativeTextMapHash')),
                                       inf.get('avatarAssocType', '').replace('ASSOC_TYPE_', ''),
                                       t(inf.get('avatarVisionBeforTextMapHash')),
                                       t(inf.get('avatarConstellationBeforTextMapHash'))] if x)
        f.write(f'## {nm}\n\n{meta}\n\n')
        for e in sorted(fet[aid], key=lambda e: (e['type'], e['fetterId'])):
            title, text = t(e.get('voiceTitleTextMapHash')), t(e.get('voiceFileTextTextMapHash'))
            if not text:
                continue
            kind = '语音' if e['type'] == 1 else '战斗'
            f.write(f'- 〔{kind}〕{title}：{text}\n')
            emit(src='voice', qtype=kind, qid=aid, qtitle=title, talk=e['fetterId'], speaker=nm, text=text)
        f.write('\n')

# 任务对话
mq = {e['id']: e for e in load('MainQuestExcelConfigData.json')}
dialogs = {}
for e in load('DialogExcelConfigData.json'):
    dialogs[e['GFLDJMJKIKE']] = e
by_talk = defaultdict(list)
for did, e in dialogs.items():
    by_talk[did // 100].append(did)
talks = load('TalkExcelConfigData_0.json') + load('TalkExcelConfigData_1.json')
talk_cfg = {e['id']: e for e in talks}

def speaker_of(e):
    role = e.get('talkRole', {})
    ty, rid = role.get('type', ''), role.get('id', '')
    nm = t(e.get('talkRoleNameTextMapHash'))
    if ty == 'TALK_ROLE_PLAYER':
        return '旅行者'
    if 'BLACK_SCREEN' in ty:
        return '（黑屏旁白）'
    if nm:
        return nm
    if ty == 'TALK_ROLE_NPC' and str(rid).isdigit():
        return npc.get(int(rid)) or f'NPC{rid}'
    if ty == 'TALK_ROLE_GADGET':
        return '（物件）'
    if ty == 'TALK_ROLE_MATE_AVATAR':
        return '（血亲）'
    return '（未知）'

def talk_lines(tid):
    seen = set()
    cfg = talk_cfg.get(tid)
    ids = sorted(by_talk.get(tid, []))
    start = cfg.get('initDialog') if cfg else None
    order = []
    if start in dialogs:
        stack = [start]
        while stack:
            d = stack.pop()
            if d in seen or d not in dialogs:
                continue
            seen.add(d)
            order.append(d)
            nx = dialogs[d].get('nextDialogs', [])
            stack.extend(reversed(nx))
    for d in ids:
        if d not in seen:
            order.append(d); seen.add(d)
    res = []
    for d in order:
        e = dialogs[d]
        txt = t(e.get('talkContentTextMapHash'))
        if not txt:
            continue
        sp = speaker_of(e)
        opt = len(dialogs.get(d, {}).get('nextDialogs', [])) > 1
        res.append((sp, txt, e.get('talkRole', {}).get('type', '') == 'TALK_ROLE_PLAYER'))
    return res

qtalks = defaultdict(list)
idle = defaultdict(list)
covered = set()
for tid, cfg in talk_cfg.items():
    if tid not in by_talk and cfg.get('initDialog', 0) // 100 not in by_talk:
        continue
    q = cfg.get('questId', 0)
    if q in mq:
        qtalks[q].append(tid)
    else:
        idle[tuple(cfg.get('npcId', [])[:1])].append(tid)
    covered.add(tid)
for tid in by_talk:
    if tid in covered:
        continue
    q = tid // 100
    if q in mq:
        qtalks[q].append(tid)
    else:
        idle[('?',)].append(tid)

QT = {'AQ': '魔神任务', 'LQ': '传说任务', 'WQ': '世界任务', 'EQ': '活动任务', 'IQ': '委托任务'}
files = {k: open(os.path.join(OUT, f'quests_{k}.md'), 'w', encoding='utf-8') for k in QT}
for k, f in files.items():
    f.write(f'# {QT[k]}对话（本地研读用）\n\n')
for q in sorted(qtalks):
    e = mq[q]
    ty = e.get('type')
    if ty not in files:
        continue
    title = t(e.get('titleTextMapHash')) or str(q)
    f = files[ty]
    body = []
    for tid in sorted(set(qtalks[q])):
        ls = talk_lines(tid)
        if not ls:
            continue
        body.append(f'### 对话 {tid}\n')
        for sp, txt, isp in ls:
            body.append(f'{"〔选项〕" if isp else ""}{sp}：{txt}')
            emit(src='quest', qtype=ty, qid=q, qtitle=title, talk=tid, speaker=sp, text=txt, player=isp)
        body.append('')
    if body:
        f.write(f'## {title}（{q}）\n\n' + '\n'.join(body) + '\n')
for f in files.values():
    f.close()

with open(os.path.join(OUT, 'npc_idle.md'), 'w', encoding='utf-8') as f:
    f.write('# 不挂任务的 NPC 闲谈（本地研读用）\n\n')
    for key in sorted(idle, key=str):
        nm = npc.get(key[0], '') if key and key[0] != '?' else '未挂 NPC'
        for tid in sorted(set(idle[key])):
            ls = talk_lines(tid)
            if not ls:
                continue
            f.write(f'### {nm}｜对话 {tid}\n\n')
            for sp, txt, isp in ls:
                f.write(f'{"〔选项〕" if isp else ""}{sp}：{txt}\n')
                emit(src='idle', qtype='NPC', qid=key[0] if key else 0, qtitle=nm, talk=tid, speaker=sp, text=txt, player=isp)
            f.write('\n')

# 提示语
rem = {e['id']: e for e in load('ReminderExcelConfigData.json')}
with open(os.path.join(OUT, 'reminders.md'), 'w', encoding='utf-8') as f:
    f.write('# 野外提示语（本地研读用）\n\n')
    for rid in sorted(rem):
        e = rem[rid]
        sp, txt = t(e.get('speakerTextMapHash')), t(e.get('contentTextMapHash'))
        if txt:
            f.write(f'- {sp or "（无名）"}：{txt}\n')
            emit(src='reminder', qtype='REM', qid=rid, qtitle='', talk=rid, speaker=sp or '（无名）', text=txt)

# 邮件
with open(os.path.join(OUT, 'mails.md'), 'w', encoding='utf-8') as f:
    f.write('# 邮件（本地研读用）\n\n')
    for e in load('MailExcelConfigData.json'):
        txt = t(e.get('contentTextMapHash'))
        if not txt:
            continue
        sender, title = t(e.get('senderTextMapHash')), t(e.get('titleTextMapHash'))
        f.write(f'## {title}｜{sender}｜{e.get("type")}\n\n{txt}\n\n')
        emit(src='mail', qtype=e.get('type'), qid=e['id'], qtitle=title, talk=e['id'], speaker=sender, text=txt)

out_lines.close()
print('done')
