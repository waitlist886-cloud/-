#!/usr/bin/env python3
# 纷争纪主线改稿收稿（11-21）：把定稿的主线（连同裁定锁）换回 纷争纪/parts*/ 的分段，新起的对手人物条接到那一页人物分段的末尾。
#   python -I -X utf8 tools/api/strife_splice.py [--apply] [拨号，默认 3]
# 定稿取 底稿/审稿/纷争纪/铺开/<拨>_<主线>.md；雨城的星、无名之柱取用户认过的样稿。
# 主线：分段里从「## 纷争纪·主线｜…·<名>」起，连同紧跟的「## 裁定锁」，换到下一个别的 ## 为止。
# 断锁是新拆的，写进 parts3/r3c_断锁.md（assemble_strife.sh 第三页次序里排在 r3 后头）。
# 人物条：交稿里「## 纷争纪·人物｜」那几条，标题在那一页已有的跳过（报出来），没有的接到人物分段末尾。
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import strife_review as SR  # noqa: E402
import strife_pukai as SP  # noqa: E402

ROOT = SR.ROOT
PARTS = {1: 'parts', 2: 'parts2', 3: 'parts3', 4: 'parts4', 5: 'parts5', 6: 'parts6', 7: 'parts7'}
PEOPLE = {1: 'p7_people', 2: 'q8_people', 3: 'r7_people', 4: 't7_people', 5: 'u7_people', 6: 'v7_people', 7: 'w7_people'}


def draft(name, w):
    if name in SP.SAMPLES:
        return SR.rd(os.path.join(SP.D, '样稿_%s.md' % name))
    return SR.rd(os.path.join(SP.OUT, '%d_%s.md' % (w, name)))


def split_draft(t):
    """回 (主线连同裁定锁, [人物条])。设计备注以后的不要。"""
    t = t.split('\n## 设计备注', 1)[0].rstrip() + '\n'
    bs = SR.blocks('\n' + t)
    main, people = [], []
    for h, b in bs:
        if h.startswith('## 纷争纪·主线｜') or (h.startswith('## 裁定锁') and main and not people):
            main.append(b)
        elif '（人物）' in h:
            people.append(b)
        else:
            raise SystemExit('认不出的块：%s' % h)
    return ''.join(main), people


def norm(s):
    return s.rstrip('\n') + '\n\n'


def part_file(page, name):
    d = os.path.join(ROOT, '纷争纪', PARTS[page])
    for f in sorted(os.listdir(d)):
        if f.endswith('.md') and re.search(r'^## 纷争纪·主线｜[^\n]*·' + re.escape(name) + r'\s*$', SR.rd(os.path.join(d, f)), re.M):
            return os.path.join(d, f)


def people_file(page):
    d = os.path.join(ROOT, '纷争纪', PARTS[page])
    fs = [f for f in sorted(os.listdir(d)) if f.startswith(PEOPLE[page])]
    return os.path.join(d, fs[0])


def main():
    apply = '--apply' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    w = int(args[0]) if args else 3
    writes = {}
    newpeople = {}
    for page, name, orig in SP.mains():
        m, ppl = split_draft(draft(name, w))
        if name == '断锁':
            f = os.path.join(ROOT, '纷争纪', PARTS[3], 'r3c_断锁.md')
            writes[f] = '\n' + norm(m)
            print('断锁 → 新分段 r3c_断锁.md，%d 字' % len(m))
        else:
            f = part_file(page, name)
            t = writes.get(f) or SR.rd(f)
            k = re.search(r'^## 纷争纪·主线｜[^\n]*·' + re.escape(name) + r'\s*$', t, re.M).start()
            e = k
            for h, b in SR.blocks(t[k:]):
                if h.startswith('## 纷争纪·主线｜') and e == k or h.startswith('## 裁定锁'):
                    e += len(b)
                else:
                    break
            old = t[k:e]
            writes[f] = t[:k] + norm(m) + t[e:]
            print('%-8s → %s，%d → %d 字' % (name, os.path.relpath(f, ROOT), len(old), len(m)))
        if ppl:
            newpeople.setdefault(page, []).extend((name, p) for p in ppl)
    for page, lst in newpeople.items():
        f = people_file(page)
        t = writes.get(f) or SR.rd(f)
        whole = SR.page_text(page)
        add = []
        for name, p in lst:
            h = p.split('\n', 1)[0]
            if h in whole or h in t:
                print('  人物条已有，跳过：%s（%s）' % (h, name))
                continue
            add.append(p)
            print('  人物条接进 %s：%s（%s）' % (os.path.basename(f), h[3:], name))
        if add:
            writes[f] = t.rstrip('\n') + '\n\n' + ''.join(norm(p) for p in add)
    if apply:
        for f, t in writes.items():
            open(f, 'w', encoding='utf-8', newline='\n').write(t)
        print('写了 %d 个文件' % len(writes))
    else:
        print('（没写盘，加 --apply 才写）')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
