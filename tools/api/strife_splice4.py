#!/usr/bin/env python3
# 纷争纪铺开第四步收稿（11-21）：照标题把交稿里改过的条目换回 纷争纪/parts*/ 的分段。
# 一条从「## 标题」换到它后面第一个「> 条目设置：」为止（时段总纲连着它的裁定锁），标题要跟原来一字不差。
#   python -I -X utf8 tools/api/strife_splice4.py [--apply]     读 底稿/审稿/纷争纪/铺开/4_*.md
# 主线（## 纷争纪·主线｜）和这一回新接进去的对手人物条不许换，交稿里有也跳过、报出来。
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import splice_entries as SE  # noqa: E402
import strife_pukai as SP  # noqa: E402
import strife_splice as SS  # noqa: E402

ROOT = SE.ROOT


def main():
    apply = '--apply' in sys.argv
    newp = set()
    for _, name, _ in SP.mains():
        _, ppl = SS.split_draft(SS.draft(name, 3))
        newp.update(p.split('\n', 1)[0].strip() for p in ppl)
    total = 0
    for src in sorted(glob.glob(os.path.join(SP.OUT, '4_*.md'))):
        job = os.path.basename(src)[2:-3]
        page = int(job[2:]) if job.startswith('页_') else [m[0] for m in SP.mains() if m[1] == job[3:]][0]
        files = glob.glob(os.path.join(ROOT, '纷争纪', SS.PARTS[page], '*.md'))
        n, miss, skip = 0, [], []
        for fn, title, body in SE.blocks(open(src, encoding='utf-8').read()):
            if title.startswith('## 纷争纪·主线｜') or title in newp:
                skip.append(title)
                continue
            hit = SE.replace_in(files, title, body + ('' if body.endswith('\n') else ''), apply)
            if len(hit) == 1:
                n += 1
            elif hit:
                miss.append('不止一处：' + title)
            else:
                miss.append('找不到：' + title)
        total += n
        print('%-14s 换 %d 条%s' % (job, n, ''.join('\n    ' + m for m in miss + ['跳过：' + s for s in skip])))
    print('合计换了 %d 条%s' % (total, '' if apply else '（没写盘，加 --apply 才写）'))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
