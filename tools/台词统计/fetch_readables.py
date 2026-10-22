#!/usr/bin/env python3
"""抓书信、日记、笔记、留言、告示这一类读物（Readable/CHS/*.txt），拼成 readables.md。
用法：python3 -I -X utf8 fetch_readables.py RAW_DIR READ_DIR OUT_DIR
"""
import json, os, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
RAW, READ, OUT = sys.argv[1:4]
os.makedirs(READ, exist_ok=True)
TM = {}
for n in ('TextMapCHS.json', 'TextMap_MediumCHS.json'):
    TM.update(json.load(open(os.path.join(RAW, n), encoding='utf-8')))
doc = json.load(open(os.path.join(RAW, 'DocumentExcelConfigData.json'), encoding='utf-8'))
loc = {e['id']: e for e in json.load(open(os.path.join(RAW, 'LocalizationExcelConfigData.json'), encoding='utf-8'))}
pat = re.compile('信|笔记|日记|留言|便条|纸条|手记|告示|传单|遗书|字条|书信|日志|手账|备忘|告白|账本|手稿|随笔|记录|公告|启事|通缉|悬赏|留给|致')
BASE = 'https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/Readable/CHS/'
jobs = []
for e in doc:
    title = TM.get(str(e.get('titleTextMapHash')), '')
    if not title or 'test' in title.lower() or not pat.search(title):
        continue
    for lid in e.get('questIDList', []):
        L = loc.get(lid)
        if not L:
            continue
        path = next((v for v in L.values() if isinstance(v, str) and '/Readable/CHS/' in v), '')
        if path:
            jobs.append((e['id'], title, path.rsplit('/', 1)[1]))
def get(j):
    _, _, name = j
    p = os.path.join(READ, name + '.txt')
    if not os.path.exists(p):
        try:
            with urllib.request.urlopen(BASE + name + '.txt', timeout=60) as r:
                open(p, 'wb').write(r.read())
        except Exception:
            return j, ''
    return j, open(p, encoding='utf-8', errors='replace').read()
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(get, jobs))
with open(os.path.join(OUT, 'readables.md'), 'w', encoding='utf-8') as f, open(os.path.join(OUT, 'lines_read.jsonl'), 'w', encoding='utf-8') as lj:
    f.write('# 书信、日记、留言、告示（本地研读用）\n\n')
    for (did, title, name), txt in res:
        txt = re.sub(r'</?color[^>]*>|</?i>|</?b>', '', txt).replace('{NICKNAME}', '旅行者').strip()
        if not txt or txt.startswith('<!DOCTYPE'):
            continue
        f.write(f'## {title}（{did}·{name}）\n\n{txt}\n\n')
        lj.write(json.dumps(dict(src='readable', qtype='READ', qid=did, qtitle=title, talk=name, speaker='', text=txt), ensure_ascii=False) + '\n')
print(len(jobs), 'jobs', sum(1 for _, t in res if t and not t.startswith('<!DOCTYPE')), 'texts')
