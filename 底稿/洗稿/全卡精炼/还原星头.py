#!/usr/bin/env python3
# 全卡精炼洗稿：把 Special 命星的头一段照原稿还原（11-16 添的）。
# 缘故：用户 11-16 定了 Special 命星要映照这个人的命运。原稿里每颗 Special 的头一段（它是什么、那句“某地的老人说”、头一回露出来的那件事）
# 正是照着命的地方（狄昂不回首那一句“叫他回头，他不回，回了就走不动了”），洗稿的人当成套话删掉了不少。头一段一共一两百字，不值得洗，整段照原稿。
#   python -I -X utf8 还原星头.py <洗后的文件> <原稿文件> [--skip 星名,星名] [--dry]         活的文件夹里：稿/x.md 原/x.md
#   python -I -X utf8 还原星头.py --repo <仓库里的文件…> [--skip 星名,星名] [--dry]          仓库里的页，原稿取标签 详本_11-15
# 只动 Special。标题、【调用】、被动主动限制这些栏都不碰。原稿没有这颗星、或者洗后头一段本来就跟原稿一样的，跳过。
# 另外把标题里带“凡世至强”的节整节照原稿还原：传奇条的【能力】【传奇专长】【独立声口】是 11-09、11-13 两轮定的格式
#（专属那一行的“｜效果：｜界限：｜说法：”三栏，凝名伟业、相关的事，“下落这一卷不写”），洗的时候被压成了一句、丢了栏，整条不洗。
import io
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
TAG = '详本_11-15'


ALSO = set()          # --also 星名,星名：这几颗不是 Special 的也照原稿还原头一段（带着命的老话叫洗掉了的 Passive、Art）


def lead_spans(text):
    """回 {星名: (起, 止, 头一段)}：### 名字 (Special | 档) 底下头一行正文（跳过空行和【调用】那一行）。"""
    out = {}
    ls = text.split('\n')
    pos = [0]
    for l in ls:
        pos.append(pos[-1] + len(l) + 1)
    for i, l in enumerate(ls):
        m = re.match(r'^### (.+?) \((Special|Passive|Art) \| ', l)
        if not m or (m.group(2) != 'Special' and m.group(1) not in ALSO):
            continue
        for k in range(i + 1, min(i + 10, len(ls))):
            s = ls[k].strip()
            if s.startswith(('### ', '## ', '> ')):
                break
            if s and not s.startswith(('【调用】', '- ')):
                out[m.group(1)] = (pos[k], pos[k] + len(ls[k]), ls[k])
                break
    return out


def sections(text):
    """回 [(标题, 起, 止)]，照 ## 切。"""
    out, idx = [], [m.start() for m in re.finditer(r'^## ', text, re.M)] + [len(text)]
    for a, b in zip(idx, idx[1:]):
        out.append((text[a:text.index('\n', a)][3:].strip(), a, b))
    return out


def restore(new, old, skip, label):
    n = 0
    # 页首（头一个 ## 以前那一截：页的标题和给作者看的说明，不进卡）照原稿，洗稿的人有时候把它删了
    ho, hn = re.search(r'^## ', old, re.M), re.search(r'^## ', new, re.M)
    if ho and hn and old[:ho.start()] != new[:hn.start()]:
        new = old[:ho.start()] + new[hn.start():]
        n += 1
        print('  %s｜页首还原（%d 字 → %d 字）' % (label, hn.start(), ho.start()))
    so = {t: old[a:b] for t, a, b in sections(old)}
    for t, a, b in sorted(sections(new), key=lambda x: -x[1]):
        if '凡世至强' in t and t in so and new[a:b] != so[t] and b < len(new):
            new = new[:a] + so[t] + new[b:]          # 连节尾的空行一起照原稿（自查是整节逐字比的）
            n += 1
            print('  %s｜整节还原：%s（%d 字 → %d 字）' % (label, t[:30], b - a, len(so[t])))
    lo, ln = lead_spans(old), lead_spans(new)
    for name in sorted(ln, key=lambda x: -ln[x][0]):          # 从后往前换，位置不乱
        if name in skip or name not in lo:
            continue
        a, b, cur = ln[name]
        org = lo[name][2]
        if cur.strip() == org.strip():
            continue
        new = new[:a] + org + new[b:]
        n += 1
        print('  %s｜%s：%d 字 → %d 字' % (label, name, len(cur), len(org)))
    return new, n


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    skip = set()
    if '--skip' in sys.argv:
        k = sys.argv[sys.argv.index('--skip') + 1]
        skip = set(x for x in k.split(',') if x)
        args.remove(k)
    if '--also' in sys.argv:
        k = sys.argv[sys.argv.index('--also') + 1]
        ALSO.update(x for x in k.split(',') if x)
        args.remove(k)
    dry = '--dry' in sys.argv
    jobs = []
    if '--repo' in sys.argv:
        for f in args:
            old = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (TAG, f)], capture_output=True).stdout.decode('utf-8')
            jobs.append((os.path.join(ROOT, f), old, f))
    else:
        jobs.append((args[0], open(args[1], encoding='utf-8', newline='').read(), os.path.basename(args[0])))
    total = 0
    for p, old, label in jobs:
        raw = open(p, encoding='utf-8', newline='').read()
        crlf = '\r\n' in raw
        new, n = restore(raw.replace('\r\n', '\n'), old.replace('\r\n', '\n'), skip, label)
        total += n
        if n and not dry:
            open(p, 'w', encoding='utf-8', newline='').write(new.replace('\n', '\r\n') if crlf else new)
    print('还原了 %d 处（Special 的头一段和凡世至强的整节）%s' % (total, '（--dry 没写）' if dry else ''))


if __name__ == '__main__':
    main()
