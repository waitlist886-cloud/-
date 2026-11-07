# -*- coding: utf-8 -*-
"""照 底稿/神名/神名表.tsv 换神号（神名重审_方向稿第五节）。
用法：python3 -I -X utf8 tools/rename_gods.py .            只报（加 --solo 连单独出现的旧名号一起换）
      python3 -I -X utf8 tools/rename_gods.py . --apply    写盘
      python3 -I -X utf8 tools/rename_gods.py . --alone    列单独出现的旧名号（换完以后看）
换的：旧名号短写加神名连写（中间可隔·），神谱「是谁」那一行的〔旧〕名，## 标题。
不换：歌、诗、二十二张、碑、方向稿和说明这类记录、设计备注、史诗条、条目设置那一行（旧名留作触发）。
神谱条目自己的触发里添新神号（寻常字眼的不单添）。"""
import csv, os, re, sys
ROOT = sys.argv[1]; APPLY = '--apply' in sys.argv; ALONE = '--alone' in sys.argv; SOLO = '--solo' in sys.argv
os.chdir(ROOT)
rows = [r for r in csv.DictReader(open('底稿/神名/神名表.tsv', encoding='utf-8'), delimiter='\t')]
for r in rows: r['old'] = r['旧名号'].split('，')[0]
CH = [r for r in rows if r['old'] != r['神号']]
ORDINARY = {'死水', '归土', '卷云', '窃火', '悬息', '封冬', '积秽'}
SONG_OLD = {'渡石为桥者', '收兵者', '卷云者', '分穗者', '执灯者', '安眠者', '焚城者', '屠城者'}
EDIT_DIRS = ['月银纪史诗', '诸国期', '萨尔维斯', 'moon/batch1', 'moon/batch2', 'moon/batch3', '月银纪补卷',
             '纷争纪/parts', '纷争纪/parts2', '纷争纪/parts3', '纷争纪/parts4', '纷争纪/parts5', '纷争纪/parts6', '纷争纪/parts7',
             '纷争纪/补卷', '山铜纪/parts1', '山铜纪/parts2', '山铜纪/parts3', '山铜纪/parts4', '山铜纪/parts5', '山铜纪/parts6',
             '山铜纪/补卷', '迷宫纪前传/parts1', '迷宫纪前传/parts2', '迷宫纪前传/parts3', '迷宫纪前传/parts4', '迷宫纪前传/parts5',
             '迷宫纪前传/parts6', '迷宫纪前传/补卷', '底卡洗稿']
EXTRA = ['纷争纪/纷争纪_旅伴与传奇总表.md', 'Art传承表_定稿.md', '迷宫纪前传/迷宫纪前传_委托_第一版.md',
         'out/进卡_v12/tools/进卡补丁_rili_v12.py', 'out/进卡_v12/tools/build_v12.py', 'out/进卡_v12/tools/batch_edits_v12.py',
         'out/进卡_v12/tools/patch_strife.py', 'out/进卡_v12/tools/patch_truth.py', 'out/进卡_v12/tools/patch_bronze.py',
         'tools/strife_legends.py']
SKIP_NAME = re.compile(r'二十二张|碑_|天亮以后|天黑以前|方向稿|说明|计划|记录|检查稿|样稿|起名|研读笔记|notes|^p9|备注|润笔|回顾')
def files():
    out = []
    for d in EDIT_DIRS:
        if not os.path.isdir(d): continue
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if os.path.isfile(p) and f.endswith('.md') and not SKIP_NAME.search(f): out.append(p)
    # 不是拼出来的页（月银纪三卷）也在上面的目录里；拼出来的页（纷争纪、山铜纪、前传）改分段再重拼
    out += [p for p in EXTRA if os.path.exists(p)]
    return out
PAIR = re.compile('|'.join('(?:%s)[·的]?%s' % (re.escape(r['old']), re.escape(r['神'])) for r in sorted(CH, key=lambda r: -len(r['old']))))
BYKEY = {}
for r in CH:
    for s in ('', '·', '的'): BYKEY[r['old'] + s + r['神']] = r
ALL = {r['神']: r for r in rows}
WHO = re.compile(r'(是谁：)〔([^〕]*)〕(' + '|'.join(re.escape(r['神']) for r in sorted(rows, key=lambda r: -len(r['神']))) + r')，')
def sub_pair(m):
    r = BYKEY[m.group(0)]; return r['神号'] + r['神']
def who(m):
    r = ALL[m.group(3)]
    s = '%s%s，尊号%s，平常叫祂%s%s。' % (m.group(1), r['神'], r['尊号'], r['神号'], r['神'])
    if r['old'] in SONG_OLD: s += '歌里也叫祂%s。' % r['old']
    return s
NOSOLO = {'日轮', '止血', '海渊', '活水', '巧遇', '第一道伤'}
SOLO_RE = re.compile('|'.join(re.escape(r['old']) for r in sorted(CH, key=lambda r: -len(r['old'])) if r['old'] not in NOSOLO))
OLD2 = {r['old']: r for r in CH}
KEEP_BEFORE = ('叫祂', '也叫', '旧名号', '羁')
QUOTES = []
CUR = ['']
SONG_ERA = ('月银纪史诗', '诸国期', '萨尔维斯', 'moon')  # 这几卷照歌叫，歌里的旧叫法单写时照留
def solo(line):
    out, last, depth = [], 0, 0
    for m in SOLO_RE.finditer(line):
        pre = line[:m.start()]
        if pre.count('“') > pre.count('”'):
            QUOTES.append(line); continue
        if any(pre.endswith(k) for k in KEEP_BEFORE): continue
        if m.group(0) in SONG_OLD and CUR[0].startswith(SONG_ERA): continue
        out.append(line[last:m.start()]); out.append(OLD2[m.group(0)]['神号']); last = m.end()
    out.append(line[last:])
    return ''.join(out)
def transform(p, t):
    CUR[0] = p
    out, prot, title, n = [], False, '', 0
    py = p.endswith('.py')
    for line in t.split('\n'):
        if not py and (line.startswith('## ') or line.startswith('# ')):
            h = line.lstrip('#').strip()
            if '设计备注' in h and line.startswith('## ') or line.startswith('# 设计备注'): prot = 'eof'
            elif prot != 'eof': prot = ('史诗' in h and line.startswith('## ')) or h.startswith('设计备注')
            title = line
        if prot or line.startswith('> 条目设置') or (py and '条目设置' in line):
            if line.startswith('> 条目设置') and '神谱｜' in title and not prot:
                for r in CH:
                    if (r['old'] + r['神'] in title or r['神号'] + r['神'] in title) and r['神号'] not in line and r['神号'] not in ORDINARY:
                        line = re.sub(r'`/', '`/' + r['神号'] + '|', line, count=1); n += 1
            out.append(line); continue
        new = WHO.sub(who, line) if not py else line
        new = PAIR.sub(sub_pair, new)
        if SOLO and not py:
            if new.startswith('【调用】'):
                # 说到、问起那一串是别名，旧名号留着；同一行别处照换
                parts = re.split(r'((?:说到|说起|问起|讲起|提到|碰上)[^。]*?的时候)', new)
                new = ''.join(x if i % 2 else solo(x) for i, x in enumerate(parts))
            else:
                new = solo(new)
        if new != line: n += 1
        if line.startswith('## '): title = new
        out.append(new)
    return '\n'.join(out), n
tot = 0; changed = []
for p in files():
    t = open(p, encoding='utf-8').read()
    t2, n = transform(p, t)
    if t2 != t:
        changed.append((p, n)); tot += n
        if APPLY: open(p, 'w', encoding='utf-8').write(t2)
for p, n in changed: print(n, p)
if QUOTES:
    print('引号里留着的', len(QUOTES))
    for q in QUOTES: print('  ', q[:160])
print('改行', tot, '文件', len(changed), '（已写）' if APPLY else '（只报）')
if ALONE:
    OLD = re.compile('|'.join(re.escape(r['old']) for r in sorted(CH, key=lambda r: -len(r['old']))))
    for p in files():
        prot = False
        for i, line in enumerate(open(p, encoding='utf-8').read().split('\n'), 1):
            if line.startswith('## ') or line.startswith('# '):
                h = line.lstrip('#').strip(); prot = ('史诗' in h and line.startswith('## ')) or '设计备注' in h or prot == 'eof'
            if prot or line.startswith('> 条目设置'): continue
            for m in OLD.finditer(line):
                print('%s:%d\t%s\t%s' % (p, i, m.group(0), line[max(0, m.start()-14):m.end()+14]))
