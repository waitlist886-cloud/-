"""拼迷宫纪前传的时段页（第二页起用这一份，第一页照旧用 assemble_maze_p1.py，两份拼法一样）。

usage: python3 -I -X utf8 tools/assemble_maze.py REPO_ROOT N [--dry]

迷宫纪前传/partsN/ 里：
  p0_head.md            页头和这一页的几张委托（带条目设置）
  p1_overview.md        时段总纲
  a_ 到 f_*.md          几份主线（主线、旅伴、旅伴之间 | ## 星 | 人物、迷宫、地点、案子、凡世至强 | ## 这一份的设计备注）
  p6_stars_head.md      命星一节的开头一段，末行是整节的条目设置
  p7_*.md               人物（Z份写的）
  p5_*.md               公告板、迷宫、案子、地点（Z份写的）
  p8_legends.md         传奇表
  p9_notes.md           设计备注（主会话写的）
  z_notes.md            Z份的设计备注（接在主会话备注后头）
拼出 迷宫纪前传/迷宫纪前传时段_N_页名.md。几份的星拆出来，去掉每颗星后头各自的条目设置行，整节只留 p6 末尾那一行。
主线份里标题以（人物）收尾的并进人物一节，凡世至强接在传奇表后头，别的条目并进公告板那一节。
"""
import sys, os, re, glob

PAGES = {
    1: ('一', '探井的年月', '这一百年'),
    2: ('二', '共约的年月', '这两百多年'),
    3: ('三', '繁荣的年月', '这两百八十年'),
    4: ('四', '深井的年月', '这两百五十年'),
    5: ('五', '黑潮的年月', '这一百二十年'),
}
NUM = '〇一二三四五六七八九'

root = sys.argv[1]
n = int(sys.argv[2])
dry = '--dry' in sys.argv
cn, pname, span = PAGES[n]
P = os.path.join(root, '迷宫纪前传', 'parts%d' % n)
rd = lambda name: open(os.path.join(P, name), encoding='utf-8').read().rstrip('\n') + '\n'

forks = []
for k in 'abcdefgh':
    fs = sorted(glob.glob(os.path.join(P, k + '_*.md')))
    assert len(fs) <= 1, (k, fs)
    if fs:
        forks.append((k, fs[0]))

def split_fork(path):
    t = open(path, encoding='utf-8').read().replace('\r', '')
    lines = t.split('\n')
    i_star = next(i for i, l in enumerate(lines) if l.strip() == '## 星')
    i_note = next(i for i, l in enumerate(lines) if l.startswith('## 这一份的设计备注'))
    j = i_star + 1
    while j < len(lines) and not lines[j].startswith('## '):
        j += 1
    return lines[:i_star], lines[i_star + 1:j], lines[j:i_note], lines[i_note:]

def clean_stars(lines):
    out, settings = [], []
    for l in lines:
        if l.startswith('> 条目设置：'):
            settings.append(l)
            continue
        out.append(l)
    k = next((i for i, l in enumerate(out) if l.startswith('### ')), len(out))
    intro = [l for l in out[:k] if l.strip()]
    return out[k:], settings, intro

def entries(lines):
    cur, res = None, []
    for l in lines:
        if l.startswith('## ') and not l.startswith('## 裁定锁'):
            if cur:
                res.append(cur)
            cur = [l]
        elif cur is not None:
            cur.append(l)
    if cur:
        res.append(cur)
    return res

mains, stars, people, sites, legends, fnotes, settings_all, intros = [], [], [], [], [], [], [], []
for k, path in forks:
    m, s, r, nt = split_fork(path)
    mains.append('\n'.join(m).strip('\n'))
    st, se, it = clean_stars(s)
    stars.append('\n'.join(st).strip('\n'))
    settings_all.append((k, se))
    intros.append((k, it))
    for e in entries(r):
        h = e[0].rstrip()
        body = '\n'.join(e).strip('\n')
        if h.endswith('（人物）'):
            people.append(body)
        elif h.startswith('## 凡世至强'):
            legends.append(body)
        else:
            sites.append(body)
    fnotes.append((k, '\n'.join(nt[1:]).strip('\n')))

def globone(pat):
    fs = sorted(glob.glob(os.path.join(P, pat)))
    return [open(f, encoding='utf-8').read().rstrip('\n') + '\n' for f in fs]

head6 = rd('p6_stars_head.md').rstrip('\n').rsplit('\n', 1)
out = []
out.append(rd('p0_head.md'))
out.append(rd('p1_overview.md'))
out += [m + '\n' for m in mains]
out.append(head6[0] + '\n')
out += [s + '\n' for s in stars if s.strip()]
out.append(head6[1] + '\n')
out.append('## 这一代的人物\n\n这一页的人物，%s段主线里碰得上的，加上%s里还在走的几位。公告板、迷宫、地点和案子接在人物后头。\n' % (NUM[len(forks)], span))
out += globone('p7_*.md')
out += [p + '\n' for p in people]
out += globone('p5_*.md')
out += [s + '\n' for s in sites]
out.append(rd('p8_legends.md'))
out += [l + '\n' for l in legends]
notes = rd('p9_notes.md')
zn = os.path.join(P, 'z_notes.md')
if os.path.exists(zn):
    z = open(zn, encoding='utf-8').read().strip('\n')
    z = re.sub(r'^# .*\n', '', z)
    notes += '\n### Z份的备注\n\n%s\n' % re.sub(r'^#{2,3} ', '#### ', z, flags=re.M)
for k, nt in fnotes:
    notes += '\n### %s份的备注\n\n%s\n' % (k.upper(), re.sub(r'^#{2,3} ', '#### ', nt, flags=re.M))
out.append(notes)
page = '\n'.join(x.rstrip('\n') + '\n' for x in out)
page = re.sub(r'\n{3,}', '\n\n', page)
dst = os.path.join(root, '迷宫纪前传', '迷宫纪前传时段_%s_%s.md' % (cn, pname))
print('mains', len(mains), 'star blocks', sum(s.count('\n### ') + s.startswith('### ') for s in stars),
      'people', len(people), 'sites', len(sites), 'legends', len(legends), 'lines', page.count('\n'))
for k, se in settings_all:
    print('settings in', k, len(se))
for k, it in intros:
    if it:
        print('intro text in', k, ':', ' '.join(it)[:120])
if not dry:
    open(dst, 'w', encoding='utf-8').write(page)
    print('wrote', dst)
