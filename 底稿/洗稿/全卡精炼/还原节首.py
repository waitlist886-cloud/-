#!/usr/bin/env python3
# 全卡精炼洗稿：把「## 这一代的命星」「## 这一代的人物」标题底下、头一颗星（### ）或下一个 ## 以前的那一段照原稿还原（11-16 添的）。
# 这一段是给作者看的（这一页几个旅伴、几颗星，借来的星出自哪一页、用的是哪一版），打包时不进卡
#（build 的 NON_ENTRY：命星一节头一颗星以前的字不收，人物一节整节跳过），洗稿不该动。洗过以后丢了出处，还冒出过原稿没有的话
#（第四页人物一节开头写成“西格蒙德在本纪凝名”）。
#   python -I -X utf8 底稿/洗稿/全卡精炼/还原节首.py --repo <仓库里的文件…> [--fix]     原稿取标签 详本_11-15
#   python -I -X utf8 底稿/洗稿/全卡精炼/还原节首.py <份名…> [--fix]                    活的文件夹里 稿/ 对 原/
# 不加 --fix 只报。行尾照洗后那个文件原样留（按字节读写）。标签以后改过名的星（RENAMES）在还原回来的那一段里照新名。
import io
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
BASE = 'C:/Users/waitl/codex_work/wash_1115'
TAG = '详本_11-15'
HEADS = ('这一代的命星', '这一代的人物', '星')
RENAMES = {'不折之腰': '刈龙之镰', '长风投掷': '随弦之臂'}


def spans(t):
    """回 {标题: (起, 止)}：标题那一行以后，到头一个 ### 、下一个 ## 、> 条目设置 或文件末尾。t 已经是 \\n 行尾。"""
    out = {}
    for h in HEADS:
        m = re.search(r'^## ' + re.escape(h) + r'[ \t]*\n', t, re.M)
        if not m:
            continue
        e = re.search(r'^(?:### |## |> 条目设置)', t[m.end():], re.M)
        out[h] = (m.end(), m.end() + (e.start() if e else len(t) - m.end()))
    return out


def fix_text(new_raw, old_raw, label, fix):
    nl = '\r\n' if '\r\n' in new_raw else '\n'
    new, old = new_raw.replace('\r\n', '\n'), old_raw.replace('\r\n', '\n')
    sn, so = spans(new), spans(old)
    n = 0
    for h in HEADS:
        if h not in sn or h not in so:
            continue
        a, b = sn[h]
        oa, ob = so[h]
        want = old[oa:ob]
        for k, v in RENAMES.items():
            want = want.replace(k, v)
        if new[a:b].strip() == want.strip():
            continue
        n += 1
        print('  %s｜%s｜洗后 %d 字 → 原稿 %d 字' % (label, h, len(re.findall(r'[一-鿿]', new[a:b])), len(re.findall(r'[一-鿿]', want))))
        new = new[:a] + want + new[b:]
        sn = spans(new)
    return (new.replace('\n', nl) if n else new_raw), n


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    fix = '--fix' in sys.argv
    tot = 0
    if '--repo' in sys.argv:
        for f in args:
            f = f.replace('\\', '/')
            p = os.path.join(ROOT, f)
            r = subprocess.run(['git', 'show', '%s:%s' % (TAG, f)], capture_output=True, cwd=ROOT)
            if r.returncode != 0:
                continue
            new_raw = open(p, 'rb').read().decode('utf-8')
            out, n = fix_text(new_raw, r.stdout.decode('utf-8'), f, fix)
            tot += n
            if n and fix:
                open(p, 'wb').write(out.encode('utf-8'))
    else:
        for job in args:
            d = '%s/%s' % (BASE, job)
            for fn in sorted(os.listdir(d + '/稿')):
                po = '%s/原/%s' % (d, fn)
                if not fn.endswith('.md') or not os.path.exists(po):
                    continue
                pn = '%s/稿/%s' % (d, fn)
                new_raw = open(pn, 'rb').read().decode('utf-8')
                out, n = fix_text(new_raw, open(po, 'rb').read().decode('utf-8'), '%s/%s' % (job, fn), fix)
                tot += n
                if n and fix:
                    open(pn, 'wb').write(out.encode('utf-8'))
    print('节首跟原稿不一样的 %d 处%s' % (tot, '，照原稿还原了' if fix else '（没写，加 --fix 才改）'))


main()
