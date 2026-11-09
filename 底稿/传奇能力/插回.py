#!/usr/bin/env python3
# 把 底稿/传奇能力/份N.md 里的【能力】一节和体态数据插回洗稿层（11-09）。
# 用法（在仓库根目录下）：python -I -X utf8 底稿/传奇能力/插回.py 底稿/传奇能力/份1.md … [--base 不带洗稿层的底本卡.json] [--apply]
#   不加 --apply 只报，不写。
# 一位做三样：
#   1. 档案里【能力｜X】那一块整块换成新的（新块里该原样留的旧行，查稿.py 已经查过）。
#   2. 体态数据那一行插在「容貌评价：」那一行后头，原来有体态数据就换掉。
#   3. 旧名字和别的只在旧块里有的东西（wash_check 认的那几样：数、【】、「」、#号、Feat），新条里没有了的，添进「- 放行：」。
# 条目数、围栏外的行、标题行都不动，CRLF 照原样。
import json
import os
import re
import runpy
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.getcwd()
W = os.path.join(ROOT, '底卡洗稿')
BASE = r'C:/Users/waitl/AppData/Local/Temp/claude/85a810c2c0993c77/e22307d9-b63e-4d31-ad24-f0ffb0fc6126/scratchpad/v12_nowash/奥尔德兰_日里版_四纪全卷_测试v12.json'
C = runpy.run_path(os.path.join(HERE, '查稿.py'), run_name='lib')
WC = runpy.run_path(os.path.join(ROOT, 'tools', 'wash_check.py'), run_name='lib')


def main():
    args = sys.argv[1:]
    apply = '--apply' in args
    base = BASE
    if '--base' in args:
        base = args[args.index('--base') + 1]
        args.remove('--base')
        args.remove(base)
    files = [a for a in args if a != '--apply']
    lb = WC['load_lorebook'](base)
    todo = {}
    for f in files:
        for b in C['parse'](f):
            if not b['to'] or not b['ab'] or not b['body']:
                print('#%d 缺补到、能力块或体态数据，跳过' % b['n'])
                continue
            todo.setdefault(b['to'][0], []).append(b)
    problems = 0
    for fn, blocks in sorted(todo.items()):
        p = os.path.join(W, fn)
        raw = open(p, encoding='utf-8', newline='').read()
        crlf = '\r\n' in raw
        s = raw.replace('\r\n', '\n')
        n0 = s.count('\n## #')
        for b in blocks:
            n = b['n']
            m = re.search(r'(?m)^## #%d .*$' % n, s)
            f1 = s.index('\n````\n', m.end()) + 5
            f2 = s.index('\n````', f1)
            head = s[m.end():f1]
            body = s[f1:f2]
            old_ab, who, _ = C['ability'](body)
            if old_ab is None:
                print('#%d 找不到【能力】那一块' % n)
                problems += 1
                continue
            new = body.replace(old_ab, b['ab'], 1)
            lines = new.split('\n')
            if any(l.startswith('体态数据｜') for l in lines):
                lines = [b['body'] if l.startswith('体态数据｜') else l for l in lines]
                where = '换掉原来的体态数据'
            else:
                k = [i for i, l in enumerate(lines) if l.startswith('容貌评价：')]
                if len(k) != 1:
                    print('#%d 容貌评价那一行有 %d 处，体态数据插不进去' % (n, len(k)))
                    problems += 1
                    continue
                lines.insert(k[0] + 1, b['body'])
                where = '接在容貌评价后头'
            new = '\n'.join(lines)
            # 放行：底本里有、新条里没有了的，只收旧块里本来就有的那几样
            src = lb[n]['content']
            fs, fnw = WC['facts'](src), WC['facts'](new)
            plain = new.replace('**', '')
            allow_m = re.search(r'(?m)^- 放行：(.*)$', head)
            allow = [a.strip() for a in allow_m.group(1).split('、')] if allow_m else []
            add, lost = [], []
            for k_, v in fs.items():
                if fnw.get(k_, 0) >= 1:
                    continue
                kind, val = k_.split(' ', 1)
                if kind in ('条目', '名', 'Feat') and val in plain:
                    continue
                if val in WC['LABELS']:
                    continue
                if any(val in a or a in val for a in allow + add if a):
                    continue
                if val in old_ab or kind == '名' and val in b['pass']:
                    add.append(val)
                else:
                    lost.append(k_)
            for x in b['pass']:
                if x not in allow and x not in add and x not in plain:
                    add.append(x)
            if lost:
                print('#%d 旧块以外少了东西：%s' % (n, '、'.join(lost)))
                problems += 1
            if add:
                if allow_m:
                    head = head.replace(allow_m.group(0), allow_m.group(0) + '、' + '、'.join(add), 1)
                else:
                    hm = re.search(r'(?m)^- 底本哈希：.*$', head)
                    head = head[:hm.end()] + '\n- 放行：' + '、'.join(add) + head[hm.end():]
            s = s[:m.end()] + head + new + s[f2:]
            print('#%d %s｜能力 %d → %d 字｜体态数据%s｜放行添 %s' % (
                n, who, len(re.sub(r'\s', '', old_ab)), len(re.sub(r'\s', '', b['ab'])), where, '、'.join(add) or '无'))
        assert s.count('\n## #') == n0, fn
        if apply:
            out = s.replace('\n', '\r\n') if crlf else s
            open(p, 'w', encoding='utf-8', newline='').write(out)
            print('写了', fn)
    print('问题', problems, '' if apply else '（没加 --apply，什么也没写）')


if __name__ == '__main__':
    main()
