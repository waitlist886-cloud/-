"""拼七城的年月那一页（山铜纪第五页），照 assemble_shantong_p4.py 改的。

usage: python3 -I -X utf8 tools/assemble_shantong_p5.py REPO_ROOT [--dry]

山铜纪/parts5/ 里：
  p0_head.md            页头和九块碑
  p1_overview.md        时段总纲
  a_ 到 i_*.md          九份主线（主线、旅伴、旅伴之间 | ## 星 | 人物、遗迹、案子 | ## 这一份的设计备注），D 份两段主线
  各份里写的 ## 山铜纪·碑｜ 条目不收，碑一律从 p0_head.md 进页
  p6_stars_head.md      命星一节的开头一段，末行是整节的条目设置
  p7_people_mine.md     主会话写的人物
  p5_board_mine.md      号墙和主会话写的案子
  p8_legends.md         传奇表
  p9_notes.md           设计备注（主会话写的，九份的备注接在后头）
拼出 山铜纪/山铜纪时段_五_七城的年月.md，另把九份的星拆出来，去掉每颗星后头各自的条目设置行，
整节只留 p6_stars_head.md 末尾那一行条目设置，打包脚本只认这一行。
"""
import sys, os, re, glob

root = sys.argv[1]
dry = '--dry' in sys.argv
P = os.path.join(root, '山铜纪', 'parts5')
rd = lambda n: open(os.path.join(P, n), encoding='utf-8').read().rstrip('\n') + '\n'

forks = []
for k in 'abcdefghi':
    fs = sorted(glob.glob(os.path.join(P, k + '_*.md')))
    assert len(fs) == 1, (k, fs)
    forks.append((k, fs[0]))

def split_fork(path):
    t = open(path, encoding='utf-8').read().replace('\r', '')
    lines = t.split('\n')
    i_star = next(i for i, l in enumerate(lines) if l.strip() == '## 星')
    i_note = next(i for i, l in enumerate(lines) if l.startswith('## 这一份的设计备注'))
    main = lines[:i_star]
    # 星从 ## 星 下一行起，到下一个 ## 为止
    j = i_star + 1
    while j < len(lines) and not (lines[j].startswith('## ') and j != i_star):
        j += 1
    stars = lines[i_star + 1:j]
    rest = lines[j:i_note]
    notes = lines[i_note:]
    return main, stars, rest, notes

def clean_stars(lines):
    out, settings = [], []
    for l in lines:
        if l.startswith('> 条目设置：'):
            settings.append(l)
            continue
        out.append(l)
    # 去掉开头的说明段（第一颗 ### 以前的）
    k = next((i for i, l in enumerate(out) if l.startswith('### ')), len(out))
    intro = [l for l in out[:k] if l.strip()]
    return out[k:], settings, intro

def entries(lines):
    """把一段按 ## 切成条目"""
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

mains, stars, people, sites, fnotes, settings_all, intros = [], [], [], [], [], [], []
for k, path in forks:
    m, s, r, n = split_fork(path)
    mains.append('\n'.join(m).strip('\n'))
    st, se, it = clean_stars(s)
    stars.append('\n'.join(st).strip('\n'))
    settings_all.append((k, se))
    intros.append((k, it))
    for e in entries(r):
        h = e[0]
        body = '\n'.join(e).strip('\n')
        if h.startswith('## 山铜纪·碑｜'):
            print('skip stele in', k, ':', h.strip(), '(p0 holds the steles)')
            continue
        if h.rstrip().endswith('（人物）'):
            people.append(body)
        else:
            sites.append(body)
    fnotes.append((k, '\n'.join(n[1:]).strip('\n')))

out = []
out.append(rd('p0_head.md'))
out.append(rd('p1_overview.md'))
out += [m + '\n' for m in mains]
out.append(rd('p6_stars_head.md').rstrip('\n').rsplit('\n', 1)[0] + '\n')  # 开头一段，末行条目设置挪到最后
out += [s + '\n' for s in stars]
out.append(rd('p6_stars_head.md').rstrip('\n').rsplit('\n', 1)[1] + '\n')
out.append('## 这一代的人物\n\n这一页的人物，十段主线里碰得上的，加上这一百二十年里还在走的几位。号墙、遗迹和案子接在人物后头。\n')
out.append(rd('p7_people_mine.md'))
out += [p + '\n' for p in people]
out.append(rd('p5_board_mine.md'))
out += [s + '\n' for s in sites]
out.append(rd('p8_legends.md'))
notes = rd('p9_notes.md')
for k, n in fnotes:
    notes += '\n### %s份的备注\n\n%s\n' % (k.upper(), re.sub(r'^## ', '#### ', re.sub(r'^### ', '#### ', n, flags=re.M), flags=re.M))
out.append(notes)
page = '\n'.join(x.rstrip('\n') + '\n' for x in out)
page = re.sub(r'\n{3,}', '\n\n', page)
dst = os.path.join(root, '山铜纪', '山铜纪时段_五_七城的年月.md')
print('mains', len(mains), 'star blocks', sum(s.count('\n### ') + s.startswith('### ') for s in stars),
      'people', len(people), 'sites', len(sites), 'lines', page.count('\n'))
for k, se in settings_all:
    print('settings in', k, len(se))
for k, it in intros:
    if it:
        print('intro text in', k, ':', ' '.join(it)[:200])
if not dry:
    open(dst, 'w', encoding='utf-8').write(page)
    print('wrote', dst)
