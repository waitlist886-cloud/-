#!/usr/bin/env python3
# 把活的文件夹里 稿/ 的某几节整节退回 原/ 的样子（洗坏了、又没有人能重洗的节，先照原稿留着）。
#   python -I -X utf8 底稿/洗稿/全卡精炼/还原节.py <份名> <文件名> <节标题开头…> [--apply]
# 节照 `## ` 切，标题拿“开头”认（给够能认出唯一一节的字就行）。不加 --apply 只报。行尾照 稿/ 里那个文件原来的。
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/codex_work/wash_1115'
APPLY = '--apply' in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith('--')]
job, fn, heads = args[0], args[1], args[2:]


def split(t):
    out, cur = [], ['', []]
    for ln in t.split('\n'):
        if ln.startswith('## '):
            out.append(cur)
            cur = [ln, []]
        else:
            cur[1].append(ln)
    out.append(cur)
    return out


pn = '%s/%s/稿/%s' % (BASE, job, fn)
po = '%s/%s/原/%s' % (BASE, job, fn)
raw = open(pn, 'rb').read().decode('utf-8')
nl = '\r\n' if '\r\n' in raw else '\n'
new = split(raw.replace('\r\n', '\n'))
old = split(open(po, 'rb').read().decode('utf-8').replace('\r\n', '\n'))
n = 0
for h in heads:
    hit_n = [i for i, s in enumerate(new) if s[0].startswith('## ' + h)]
    hit_o = [i for i, s in enumerate(old) if s[0].startswith('## ' + h)]
    if len(hit_n) != 1 or len(hit_o) != 1:
        raise SystemExit('认不出唯一的一节：%s（稿 %d 处，原 %d 处）' % (h, len(hit_n), len(hit_o)))
    a, b = new[hit_n[0]], old[hit_o[0]]
    print('%s｜%s｜%d 行 → 原稿的 %d 行%s' % (fn, a[0][3:40], len(a[1]), len(b[1]), '' if a[1] != b[1] else '（本来就一样）'))
    new[hit_n[0]] = [b[0], list(b[1])]
    n += 1
if APPLY:
    lines = []
    for k, s in enumerate(new):
        if k > 0:
            lines.append(s[0])
        lines.extend(s[1])
    t = '\n'.join(lines)
    open(pn, 'wb').write(t.replace('\n', nl).encode('utf-8'))
print('%s %d 节' % ('退回了' if APPLY else '（没写）要退回', n))
