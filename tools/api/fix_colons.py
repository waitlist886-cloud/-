#!/usr/bin/env python3
# 交稿的卡面部分（「## 设计备注」以前）去多余的冒号和分号：标签行只留第一个、标签八个字以内的那个冒号，别的改逗号；分号改逗号。
# 反引号里的正则不动。用法：python -I -X utf8 tools/api/fix_colons.py 文件…   原地改，印改了几处。
import re
import sys


def fix_line(line):
    parts = re.split(r'(`[^`]*`)', line)
    out = []
    first = True
    for seg in parts:
        if seg.startswith('`'):
            out.append(seg)
            continue
        buf = ''
        for ch in seg:
            if ch == '；':
                ch = '，'
            elif ch == '：':
                head = re.sub(r'^[\s>\-*#]*', '', buf if not out else ''.join(out) + buf)
                ok = first and len(head) <= 8 and not re.search(r'[，。、（）“”]', head)
                first = False
                if not ok:
                    ch = '，'
            buf += ch
        out.append(buf)
    return ''.join(out)


def fix(path):
    t = open(path, encoding='utf-8').read()
    i = t.find('## 设计备注')
    card, rest = (t[:i], t[i:]) if i >= 0 else (t, '')
    new = '\n'.join(fix_line(l) for l in card.split('\n'))
    n = sum(1 for a, b in zip(card, new) if a != b)
    open(path, 'w', encoding='utf-8').write(new + rest)
    print(path, '改了', n, '处')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for p in sys.argv[1:]:
        fix(p)
