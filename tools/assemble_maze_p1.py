"""拼迷宫纪前传第一页探井的年月。

usage: python3 -I -X utf8 tools/assemble_maze_p1.py REPO_ROOT [--dry]

迷宫纪前传/parts1/ 里：
  p0_head.md            页头和这一页的四张委托（第〇到第三张，带条目设置）
  p1_overview.md        时段总纲
  a_ 到 e_*.md          五份主线（主线、旅伴、旅伴之间 | ## 星 | 人物、迷宫、地点、案子、凡世至强 | ## 这一份的设计备注）
  p6_stars_head.md      命星一节的开头一段，末行是整节的条目设置
  p7_people_mine.md     主会话写的人物
  p5_board_mine.md      公告板、口子与井口、案子（主会话写的）
  p8_legends.md         传奇表
  p9_notes.md           设计备注（主会话写的，五份的备注接在后头）
拼出 迷宫纪前传/迷宫纪前传时段_一_探井的年月.md。照山铜纪第一页的拼法：五份的星拆出来，去掉每颗星后头各自的条目设置行，
整节只留 p6_stars_head.md 末尾那一行。人物（标题以（人物）收尾）并进人物一节，凡世至强接在传奇表后头，别的条目并进公告板那一节。
"""
import sys, os, re, glob

root = sys.argv[1]
dry = '--dry' in sys.argv
P = os.path.join(root, '迷宫纪前传', 'parts1')
rd = lambda n: open(os.path.join(P, n), encoding='utf-8').read().rstrip('\n') + '\n'

forks = []
for k in 'abcde':
    fs = sorted(glob.glob(os.path.join(P, k + '_*.md')))
    assert len(fs) == 1, (k, fs)
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
    m, s, r, n = split_fork(path)
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
    fnotes.append((k, '\n'.join(n[1:]).strip('\n')))

head6 = rd('p6_stars_head.md').rstrip('\n').rsplit('\n', 1)
out = []
out.append(rd('p0_head.md'))
out.append(rd('p1_overview.md'))
out += [m + '\n' for m in mains]
out.append(head6[0] + '\n')
out += [s + '\n' for s in stars if s.strip()]
out.append(head6[1] + '\n')
out.append('## 这一代的人物\n\n这一页的人物，五段主线里碰得上的，加上这一百年里还在走的几位。公告板、迷宫、地点和案子接在人物后头。\n')
out.append(rd('p7_people_mine.md'))
out += [p + '\n' for p in people]
out.append(rd('p5_board_mine.md'))
out += [s + '\n' for s in sites]
out.append(rd('p8_legends.md'))
out += [l + '\n' for l in legends]
notes = rd('p9_notes.md')
for k, n in fnotes:
    notes += '\n### %s份的备注\n\n%s\n' % (k.upper(), re.sub(r'^#{2,3} ', '#### ', n, flags=re.M))
out.append(notes)
page = '\n'.join(x.rstrip('\n') + '\n' for x in out)
page = re.sub(r'\n{3,}', '\n\n', page)
dst = os.path.join(root, '迷宫纪前传', '迷宫纪前传时段_一_探井的年月.md')
print('mains', len(mains), 'star blocks', sum(s.count('\n### ') + s.startswith('### ') for s in stars),
      'people', len(people), 'sites', len(sites), 'legends', len(legends), 'lines', page.count('\n'))
for k, se in settings_all:
    print('settings in', k, len(se))
for k, it in intros:
    if it:
        print('intro text in', k, ':', ' '.join(it)[:200])
if not dry:
    open(dst, 'w', encoding='utf-8').write(page)
    print('wrote', dst)
