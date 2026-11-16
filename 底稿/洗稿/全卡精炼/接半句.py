#!/usr/bin/env python3
# 把命星拟改里“留名接半句”的那半句接进页上 Special 的头一段。
#   python -I -X utf8 底稿/洗稿/全卡精炼/接半句.py <拟改.md…> [--pages 目录或文件…] [--apply] [--only 星名,星名]
# 不加 --apply 只试：每一条报接在哪、接完是什么样。对不上的报出来，一个字不写。
# 认两种写法（都在拟改稿里）：
#   ### 人｜星（留名）            下一行  > ……原句，**添的（★）**。原句……
#   - **人｜星**：……原句，**添的（★）**。原句……
# 接法：粗体前头那一截原句在头一段里正好出现一回，粗体接在它后头；粗体前后的标点照拟改稿（原稿是句号、拟改写成逗号的照拟改）。
# 行尾照原样留（按字节读写）。写完自己再读一遍核对。改名的（### 人｜新名 (Special | 档)）不归这一支管。
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PUNC = '。，、；：？！'
DEFAULT_PAGES = ['月银纪史诗', '诸国期', '萨尔维斯']


def strip_dots(s):
    return s.strip().strip('…').strip()


def parse(md):
    t = open(md, encoding='utf-8').read().replace('\r', '')
    out = []
    lines = t.split('\n')
    for i, ln in enumerate(lines):
        m = re.match(r'^- \*\*([^｜*]+)｜([^*]+)\*\*：(.*)$', ln)
        if m:
            out.append((m.group(1).strip(), m.group(2).strip(), m.group(3)))
            continue
        m = re.match(r'^### ([^｜]+)｜(.+?)（留名）\s*$', ln)
        if m:
            for nx in lines[i + 1:i + 5]:
                if nx.startswith('> '):
                    out.append((m.group(1).strip(), m.group(2).strip(), nx[2:]))
                    break
    return out


def find_star(pages, star):
    hits = []
    for p in pages:
        b = open(p, 'rb').read()
        t = b.decode('utf-8')
        m = re.search(r'^### ' + re.escape(star) + r' \(Special[^\n]*\r?\n', t, re.M)
        if m:
            hits.append((p, t, m))
    return hits


def lead_span(t, m):
    """星条里头一段的起止：【调用】那一行以后、头一个“- 被动”以前。"""
    j = len(t)
    for st in (r'^### ', r'^## ', r'^> 条目设置'):
        mm = re.search(st, t[m.end():], re.M)
        if mm:
            j = min(j, m.end() + mm.start())
    blk = t[m.end():j]
    k = re.search(r'^- 被动', blk, re.M)
    end = m.end() + (k.start() if k else len(blk))
    c = re.search(r'^【调用】[^\n]*\n', blk, re.M)
    start = m.end() + (c.end() if c else 0)
    return start, end


def splice(lead, body):
    parts = body.split('**')
    if len(parts) != 3:
        return None, '粗体不是正好一段（%d 段）' % (len(parts) // 2)
    B, A, C = strip_dots(parts[0]), parts[1].strip(), parts[2].strip()
    C = C[:-1].strip() if C.endswith('…') else C
    C = C.rstrip('…').strip()
    p1 = B[-1] if B and B[-1] in PUNC else ''
    bcore = B[:-1] if p1 else B
    key = bcore[-16:] if len(bcore) > 16 else bcore
    if not key:
        return None, '粗体前头没有原句'
    n = lead.count(key)
    if n != 1:
        return None, '原句“%s”在头一段里出现 %d 回' % (key, n)
    pos = lead.index(key) + len(key)
    q = lead[pos] if pos < len(lead) and lead[pos] in PUNC else ''
    rest = lead[pos + len(q):]
    p2 = C[0] if C and C[0] in PUNC else ''
    chead = C[len(p2):].lstrip()[:6]
    if chead and not rest.lstrip('\r\n ').startswith(chead):
        return None, '粗体后头“%s”跟原稿接下去的“%s”对不上' % (chead, rest.lstrip()[:8])
    if not chead and rest.strip() and not p2 and not A.endswith(tuple(PUNC)):
        return None, '粗体后头没有标点，原稿后头还有字'
    tail = p2 if p2 else ('' if A.endswith(tuple(PUNC)) else (q or '。'))
    new = lead[:pos] + (p1 or q or '，') + A + tail + rest
    return new, '接在“…%s”后头' % key[-10:]


def main():
    args = sys.argv[1:]
    apply = '--apply' in args
    only = None
    if '--only' in args:
        only = set(args[args.index('--only') + 1].split(','))
    pages_arg = []
    if '--pages' in args:
        k = args.index('--pages')
        for a in args[k + 1:]:
            if a.startswith('--'):
                break
            pages_arg.append(a)
    mds = [a for a in args if a.endswith('.md') and a not in pages_arg]
    pages = []
    for d in (pages_arg or DEFAULT_PAGES):
        pages += sorted(glob.glob(os.path.join(d, '*.md'))) if os.path.isdir(d) else [d]
    pages = [p for p in pages if not re.search(r'方向|细写方案|说明|样稿|名录|研读|天黑以前|天亮以后', os.path.basename(p))]
    ok = bad = 0
    writes = {}
    for md in mds:
        for who, star, body in parse(md):
            if only and star not in only:
                continue
            hits = find_star(pages, star)
            if len(hits) != 1:
                print('！%s｜%s：页上找到 %d 颗这个名字的 Special' % (who, star, len(hits)))
                bad += 1
                continue
            p, t, m = hits[0]
            t = writes.get(p, t)
            m = re.search(r'^### ' + re.escape(star) + r' \(Special[^\n]*\r?\n', t, re.M)
            a, b = lead_span(t, m)
            lead = t[a:b]
            added = body.split('**')[1].strip() if body.count('**') == 2 else ''
            if added and added in lead:
                print('  %s｜%s：已经接过了' % (who, star))
                ok += 1
                continue
            new, msg = splice(lead, body)
            if new is None:
                print('！%s｜%s｜%s：%s' % (who, star, os.path.basename(p), msg))
                bad += 1
                continue
            ok += 1
            print('  %s｜%s｜%s：%s' % (who, star, os.path.basename(p), msg))
            i = new.index(added)
            print('      …%s【%s】%s…' % (new[max(0, i - 14):i].replace('\n', '⏎'), added, new[i + len(added):i + len(added) + 12].replace('\n', '⏎').replace('\r', '')))
            writes[p] = t[:a] + new + t[b:]
    print('接得上 %d 条，对不上 %d 条' % (ok, bad))
    if apply:
        if bad:
            print('有对不上的，一个字没写。')
            return
        for p, t in writes.items():
            open(p, 'wb').write(t.encode('utf-8'))
            print('写了', p)


main()
