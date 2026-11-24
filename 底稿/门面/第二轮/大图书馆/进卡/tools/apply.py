#!/usr/bin/env python3
# 大图书馆进卡（11-24）：把 著作行.md 里拟的著作行插进各人物条，把 书目条目.md 放进通用条目。只用标准库。
#   python -I -X utf8 底稿/门面/第二轮/大图书馆/进卡/tools/apply.py --dry [--keep]   只报：每一处插在哪一行、前后各是什么，临时目录里套一遍再拿 tools/check_protected.py 对
#   python -I -X utf8 底稿/门面/第二轮/大图书馆/进卡/tools/apply.py --apply --yes   真套（先跑一遍 --dry 的全部检查，有一处不对就不写）
#
# 放哪里：
#   一、著作行：照 著作行.md 每一节的「文件」「条目」「插在」插进源稿，只添行，不改原有的行。
#      底卡那几位（凡世至强、旅途同行，迷宫纪1001年那一局）插在 底卡洗稿/ 的洗稿层里（打包照洗稿层换底卡正文）；
#      前传、山铜纪的人物条插在各纪 补卷/ 和 底卡新条目_四纪大框/、底卡新条目/；
#      各纪页上的旅途同行、凡世至强插在分段源稿（纷争纪/parts*、山铜纪/parts*、迷宫纪前传/parts*）或者本来就是源稿的页
#      （月银纪史诗/第X歌、萨尔维斯/萨尔维斯时段_X），套完照末尾报的命令重拼那几页。
#   二、书目条目：进卡/书目条目.md 拿掉「> 待全本写完再改」那几行，写成 通用条目/大图书馆_书目.md。
#      通用条目四纪和1001年都收（general_entries.apply_general），门控写在各条的触发正则里，不靠纪元目录。
#      这一份文件只进四纪大框，1001 年切片和风月版不收（make_1001_slice 不读 通用条目/）。
# 插法（著作行.md 头上也写了）：声口前／行前「P」／行后「P」／末行后「P」。条目的范围：底卡洗稿 是到下一个「## #号」，别的文件到下一个「## 」。
# 只添行：套完逐个文件拿 tools/check_protected.py 对（条目设置、固定锚定、底座、体态数据、## 标题、### 星标题），
#   再自己比一遍，新文件比旧文件正好多出拟的那几行，旧的行一行没少、次序没变。
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
JK = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(JK, '..', '..', '..', '..', '..'))
GEN_OUT = os.path.join(ROOT, '通用条目', '大图书馆_书目.md')


def read_blocks():
    text = open(os.path.join(JK, '著作行.md'), encoding='utf-8').read().replace('\r\n', '\n')
    blocks = []
    for m in re.finditer(r'^### (\d+) (.+?)\n(.*?)^```text\n(.*?)^```', text, re.S | re.M):
        head = m.group(3)
        f = {}
        for k in ('文件', '条目', '插在', '管的年份', '书'):
            mm = re.search(r'^- %s｜(.+)$' % k, head, re.M)
            assert mm, ('著作行.md 第 %s 节少了 %s' % (m.group(1), k))
            f[k] = mm.group(1).strip()
        lines = m.group(4).rstrip('\n').split('\n')
        blocks.append(dict(no=m.group(1), who=m.group(2), lines=lines, **f))
    return blocks


def load(path):
    raw = open(path, 'rb').read().decode('utf-8')
    crlf = '\r\n' in raw
    return raw.replace('\r\n', '\n').split('\n'), crlf


def save(path, lines, crlf):
    s = '\n'.join(lines)
    if crlf:
        s = s.replace('\n', '\r\n')
    open(path, 'wb').write(s.encode('utf-8'))


def entry_range(L, rel, head):
    hits = [i for i, l in enumerate(L) if l.startswith(head)]
    if len(hits) != 1:
        raise ValueError('条目标题对上 %d 处：%s' % (len(hits), head))
    s = hits[0]
    if rel.startswith('底卡洗稿/'):
        stop = re.compile(r'^## (#\d+ |[一二三四五六七八九十]+、)')
    else:
        stop = re.compile(r'^## ')
    e = s + 1
    while e < len(L) and not stop.match(L[e]):
        e += 1
    return s, e


def anchor(L, s, e, how):
    """返回插入的行号（插在这一行前头）"""
    def skip_blank_before(k):
        return k - 1 if k - 1 > s and L[k - 1].strip() == '' else k
    if how == '声口前':
        ks = [k for k in range(s, e) if L[k].startswith('【独立声口')]
        if not ks:
            raise ValueError('条目里没有【独立声口')
        return skip_blank_before(ks[0])
    m = re.match(r'^(行前|行后|末行后)「(.+)」$', how)
    if not m:
        raise ValueError('认不出插法 %s' % how)
    kind, p = m.groups()
    ks = [k for k in range(s, e) if L[k].startswith(p)]
    if not ks:
        raise ValueError('条目里没有以「%s」起头的行' % p)
    if kind == '行前':
        return skip_blank_before(ks[0])
    k = ks[0] if kind == '行后' else ks[-1]
    j = k + 1
    while j < e and L[j].startswith('  ') and L[j].strip():
        j += 1
    return j


def plan(blocks, workdir):
    """在 workdir 里套一遍，返回 [(块, 文件, 插入行号, 前一行, 后一行, 状态)]，和改过的文件"""
    rep, touched = [], {}
    for b in blocks:
        rel = b['文件']
        src = os.path.join(ROOT, rel)
        dst = os.path.join(workdir, rel)
        if rel not in touched:
            if not os.path.exists(src):
                rep.append((b, rel, -1, '', '', '文件不在')); continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            touched[rel] = load(src)
        L, crlf = load(dst)
        try:
            s, e = entry_range(L, rel, b['条目'])
            if any(l.strip() and l.strip() in (x.strip() for x in L[s:e]) for l in b['lines']):
                rep.append((b, rel, -1, '', '', '已经有了，跳过')); continue
            k = anchor(L, s, e, b['插在'])
        except ValueError as ex:
            rep.append((b, rel, -1, '', '', '错：%s' % ex)); continue
        L[k:k] = b['lines']
        save(dst, L, crlf)
        rep.append((b, rel, k + 1, L[k - 1] if k > 0 else '', L[k + len(b['lines'])] if k + len(b['lines']) < len(L) else '', 'ok'))
    return rep, touched


def check_files(touched, workdir, blocks):
    bad = 0
    out = []
    want = {}
    for b in blocks:
        want.setdefault(b['文件'], []).extend(b['lines'])
    for rel, (old, _) in touched.items():
        new, _ = load(os.path.join(workdir, rel))
        tmp_old = os.path.join(workdir, '_old_' + re.sub(r'[\\/]', '_', rel))
        save(tmp_old, old, False)
        r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(ROOT, 'tools', 'check_protected.py'), tmp_old,
                            os.path.join(workdir, rel)], capture_output=True, text=True, encoding='utf-8')
        res = ' '.join(r.stdout.split())
        ok = 'protected OK' in res and ('能力 stars OK' in res)
        # 只多了拟的那几行：旧的行是新的行的子序列，多出来的正好是拟的行
        i, extra = 0, []
        for l in new:
            if i < len(old) and l == old[i]:
                i += 1
            else:
                extra.append(l)
        sub_ok = i == len(old) and sorted(extra) == sorted(want.get(rel, []))
        if not (ok and sub_ok):
            bad += 1
        out.append('%s %s｜%s｜多了 %d 行%s' % ('  ' if ok and sub_ok else '!!', rel, res, len(extra),
                                             '' if sub_ok else '，跟拟的不一样'))
    return bad, out


REASSEMBLE = [
    (r'^纷争纪/parts(\d?)/', lambda m: 'bash tools/assemble_strife.sh %s' % (m.group(1) or '1')),
    (r'^山铜纪/parts(\d)/', lambda m: 'python -I -X utf8 tools/assemble_shantong_p%s.py .' % m.group(1)),
    (r'^迷宫纪前传/parts(\d)/', lambda m: 'python -I -X utf8 tools/assemble_maze.py . %s' % m.group(1)),
]


def shumu(workdir):
    src = os.path.join(JK, '书目条目.md')
    lines = open(src, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
    pend = [l for l in lines if l.startswith('> 待全本写完再改')]
    keep = [l for l in lines if not l.startswith('> 待全本写完再改')]
    dst = os.path.join(workdir, '通用条目', '大图书馆_书目.md')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'w', encoding='utf-8').write('\n'.join(keep))
    # 照打包的读法读一遍，文件夹要在底卡里
    sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', '大框'))
    import new_base as NB
    NB.HEAD = re.compile(r'^## 奥尔德兰·(.+)$')
    card = json.load(open(os.path.join(ROOT, 'src', 'rili_v7.json'), encoding='utf-8'))
    ents = NB.entries(card['prompt']['lorebook'][:1397], os.path.dirname(dst))
    ents = [e for e in ents if e['content'].startswith('## 大图书馆｜')]
    for e in ents:
        assert e['triggerWords'] and all(w.startswith('/') for w in e['triggerWords'])
        re.compile(e['triggerWords'][0][1:-1])
    return dst, len(ents), pend, sum(len(e['content']) for e in ents)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--dry'
    assert mode in ('--dry', '--apply'), '用 --dry 或 --apply'
    if mode == '--apply' and '--yes' not in sys.argv:
        sys.exit('--apply 要再加 --yes 才写盘（这一回只交 --dry）')
    blocks = read_blocks()
    work = tempfile.mkdtemp(prefix='lib_apply_')
    rep, touched = plan(blocks, work)
    print('著作行 %d 处，改 %d 个文件' % (len(blocks), len(touched)))
    errs = 0
    for b, rel, k, before, after, st in rep:
        if st != 'ok':
            errs += st.startswith(('错', '文件不在'))
        print('  %s %s %s｜%s｜第 %s 行｜%s' % ('  ' if st == 'ok' else '!!', b['no'], b['who'], rel, k, st))
        if st == 'ok':
            print('       前｜%s' % before[:50])
            print('       插｜%s' % b['lines'][0][:50])
            print('       后｜%s' % after[:50])
    bad, out = check_files(touched, work, [b for (b, rel, k, x, y, st) in rep if st == 'ok'])
    print('受保护的行（tools/check_protected.py）和只多了这几行：')
    for o in out:
        print('  ' + o)
    dst, n, pend, size = shumu(work)
    print('书目条目：%d 条，正文 %d 字，写到 %s' % (n, size, os.path.relpath(GEN_OUT, ROOT)))
    for p in pend:
        print('  拿掉的标记｜' + p[:60])
    redo = sorted(set(f(m) for rel in touched for rx, f in REASSEMBLE for m in [re.match(rx, rel)] if m))
    if redo:
        print('套完要重拼的页：')
        for r in redo:
            print('  ' + r)
    if errs or bad:
        print('有 %d 处没对上、%d 个文件对不上，不写。' % (errs, bad))
        sys.exit(1)
    if mode == '--dry':
        if '--keep' in sys.argv:
            print('--dry：只在临时目录里套了一遍（%s，--keep 留着），源稿没动。' % work)
        else:
            shutil.rmtree(work, ignore_errors=True)
            print('--dry：只在临时目录里套了一遍，套完删了（要看加 --keep），源稿没动。')
        return
    for rel in touched:
        shutil.copyfile(os.path.join(work, rel), os.path.join(ROOT, rel))
    shutil.copyfile(dst, GEN_OUT)
    print('写好了：%d 个源稿文件，加 %s。重拼上面那几页，再照「11-17 机械瘦身」第 8 条的先后打卡。' % (len(touched), os.path.relpath(GEN_OUT, ROOT)))


if __name__ == '__main__':
    main()
