# -*- coding: utf-8 -*-
"""铺开·收稿：把一份活里名下的块并回仓库，别处一概不收。

用法（仓库根上）：
  python -I -X utf8 底稿/命星高魔化/铺开/收稿.py 份名 …             只报：自查的结果，要并回哪些块
  python -I -X utf8 底稿/命星高魔化/铺开/收稿.py 份名 … --apply     并回去。自查有错的不并，加 --force 才并
  python -I -X utf8 底稿/命星高魔化/铺开/收稿.py --post 页 [--apply]  一页的各份都并完以后跑：
        别处带【】的旧名换成新名，各节条目设置里“某某那一条要同时出现谁”跟着换名，列出要手看的地方
"""
import io, os, re, sys, json, subprocess, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import 搭活 as D

WORK = D.WORK
LOG = os.path.join(HERE, '收稿记录.tsv')


def bare_all(lines):
    return [x.rstrip('\r') for x in lines]


def selfcheck(d):
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, '自查.py'), d],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    out = r.stdout
    m = re.search(r'错 (\d+) 条', out)
    n = int(m.group(1)) if m else -1
    m2 = re.search(r'看 (\d+) 条', out)
    return n, (int(m2.group(1)) if m2 else -1), out


def merge(name, apply=False, force=False):
    d = os.path.join(WORK, name)
    J = json.load(io.open(os.path.join(d, '任务.json'), encoding='utf-8'))
    nerr, nlook, out = selfcheck(d)
    print('== %s｜自查 错 %d 看 %d' % (name, nerr, nlook))
    if nerr != 0:
        for l in out.splitlines():
            if l.startswith('  错'):
                print(l)
        if not force:
            print('   有错，不并。')
            return False
    done = []
    for f in J['files']:
        b = os.path.basename(f)
        rp = os.path.join(ROOT, f)
        R = io.open(rp, encoding='utf-8', newline='').read().split('\n')
        crlf = sum(1 for x in R if x.endswith('\r')) > len(R) / 2
        Rb = bare_all(R)
        O = bare_all(io.open(os.path.join(d, '原', b), encoding='utf-8', newline='').read().split('\n'))
        G = bare_all(io.open(os.path.join(d, '稿', b), encoding='utf-8', newline='').read().split('\n'))
        ops = []
        for a in J['arts']:
            if os.path.basename(a['file']) != b:
                continue
            new, old = a['new'], a['old']
            so = D.star_block(O, old)
            sr = D.star_block(Rb, old)
            if a.get('share') == '从':
                if old == new:
                    continue
                if not sr:
                    print('   %s：仓库里原来的块 ### %s 已经没有了，跳过' % (new, old))
                    continue
                if so and Rb[sr[0]:sr[1]] != O[so[0]:so[1]]:
                    print('   %s：仓库里这一块跟搭活时不一样，没有删' % new)
                    continue
                ops.append((sr[0], sr[1], [], '删星条 ' + old))
                continue
            sg = D.star_block(G, new)
            if not sg:
                print('   %s：稿里没有这一条，没有并' % new)
                continue
            if not sr:
                if old != new and D.star_block(Rb, new):
                    print('   %s：仓库里已经是新的，跳过' % new)
                else:
                    print('   %s：仓库里找不到原来的块 ### %s' % (new, old))
                continue
            if so and Rb[sr[0]:sr[1]] != O[so[0]:so[1]]:
                if Rb[sr[0]:sr[1]] == G[sg[0]:sg[1]]:
                    continue
                print('   %s：仓库里这一块跟搭活时不一样，没有并' % new)
                continue
            ops.append((sr[0], sr[1], G[sg[0]:sg[1]], '星条 %s←%s' % (new, old)))
        cbo, cbr, cbg = D.comp_blocks(O), D.comp_blocks(Rb), D.comp_blocks(G)
        for c in J['comps']:
            if os.path.basename(c['file']) != b:
                continue
            n = c['name']
            if n not in cbr or n not in cbg or n not in cbo:
                print('   旅伴条 %s：三处有一处找不到，没有并' % n)
                continue
            ro, rr, rg = cbo[n], cbr[n], cbg[n]
            if Rb[rr[0]:rr[1]] != O[ro[0]:ro[1]]:
                if Rb[rr[0]:rr[1]] == G[rg[0]:rg[1]]:
                    continue
                print('   旅伴条 %s：仓库里这一块跟搭活时不一样，没有并' % n)
                continue
            if O[ro[0]:ro[1]] == G[rg[0]:rg[1]]:
                continue
            ops.append((rr[0], rr[1], G[rg[0]:rg[1]], '旅伴条 ' + n))
        ops.sort(key=lambda x: x[0])
        for k in range(1, len(ops)):
            if ops[k][0] < ops[k - 1][1]:
                print('   %s：两块叠在一起了（%s／%s），这个文件没有并' % (b, ops[k - 1][3], ops[k][3]))
                ops = []
                break
        print('   %s：%d 块%s' % (b, len(ops), '' if apply else '（没加 --apply，只报）'))
        if not apply or not ops:
            continue
        for s, e, new_lines, what in reversed(ops):
            R[s:e] = [x + ('\r' if crlf else '') for x in new_lines]
            done.append((b, what))
        D.safe_write(rp, '\n'.join(R))
    if apply and done:
        with io.open(LOG, 'a', encoding='utf-8', newline='\n') as fo:
            t = datetime.datetime.now().strftime('%m-%d %H:%M')
            for b, what in done:
                fo.write('\t'.join([t, name, J['page'], b, what]) + '\n')
    return True


def post(page, apply=False):
    jobs = [j for j in json.load(io.open(os.path.join(HERE, '分份.json'), encoding='utf-8')) if j['page'] == page]
    ren, gone = {}, {}
    for j in jobs:
        for a in j['arts']:
            if a['old'] == a['new']:
                continue
            if a['row']['补法'] in ('新起', '同门'):
                gone[a['old']] = a['new']
            else:
                ren[a['old']] = a['new']
    files = D.page_files(page)
    tot = 0
    look = []
    for f in files:
        s = io.open(f, encoding='utf-8', newline='').read()
        s0 = s
        b = os.path.basename(f)
        for old, new in ren.items():
            rx = re.compile(r'(?<!之章)【%s】' % re.escape(old))      # 羁绊章的题跟旧星名同字的不换
            k = len(rx.findall(s))
            if k:
                s = rx.sub('【%s】' % new, s)
                tot += k
                print('   %s：【%s】→【%s】 %d 处' % (b, old, new, k))
            s2 = s.replace(old + '那一条要同时出现', new + '那一条要同时出现')
            if s2 != s:
                print('   %s：条目设置里 %s那一条 换名' % (b, old))
                s = s2
            # 正文里指着星条说的“照命星某某那一条”
            for pat in ('命星' + old, '照' + old + '那一条', '照这一页的星' + old):
                if pat in s:
                    print('   %s：%s 换名 %d 处' % (b, pat, s.count(pat)))
                    s = s.replace(pat, pat.replace(old, new))
        for old, new in gone.items():
            if re.search(r'(?<!之章)【%s】' % re.escape(old), s):
                look.append('%s：【%s】还在（这一门撤了，顶上的是 %s），手看' % (b, old, new))
            m = re.search(re.escape(old) + r'那一条要同时出现[^，。]+[，]?', s)
            if m:
                s = s.replace(m.group(0), '')
                print('   %s：条目设置里 %s那一条 拿掉（这一门撤了）' % (b, old))
        # 不带括号的旧名还剩多少，只报
        for old in list(ren) + list(gone):
            if len(old) < 3:
                continue
            for ln in s.split('\n'):
                t = ln.rstrip('\r')
                if old in t and '【%s】' % old not in t and not t.startswith('> 条目设置') and (ren.get(old) or gone.get(old)) not in t:
                    look.append('%s：还写着旧名 %s｜%s' % (b, old, t[max(0, t.find(old) - 18):t.find(old) + 24]))
        if apply and s != s0:
            D.safe_write(f, s)
    print('== %s：带括号的旧名换了 %d 处%s' % (page, tot, '' if apply else '（没加 --apply，只报）'))
    print('   要手看的 %d 处' % len(look))
    if '--verbose' in sys.argv:
        for x in look[:120]:
            print('   看｜' + x)
    else:
        for x in look:
            if '这一门撤了' in x:
                print('   看｜' + x)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    apply = '--apply' in sys.argv
    if '--post' in sys.argv:
        for pg in args:
            post(pg, apply)
    else:
        for n in args:
            merge(n, apply, '--force' in sys.argv)
