# 城镇硬数插回底卡洗稿层（11-10）：照 硬数.tsv（Codex 起稿、主会话审过）给每一处城镇添一行只给 AI 的硬数。
# 一行接在条目标题底下（洗稿层每一节 ```` 里的头一行），已经插过的跳过。
# 用法（仓库根上）：python -I -X utf8 底稿/底卡新条目/硬数插回.py 底稿/底卡新条目/硬数.tsv [--apply]
import csv, glob, re, sys

COLS = ['人口', '守备', '靠什么吃饭', '物价', '治安', '公会', '交通']
LABEL = '- 硬数（只给 AI，叙述里用比法，人物嘴里不报大数）｜'
BAN = re.compile(r'[…！—；：:\t]')


def line_of(r):
    cells = []
    for k in COLS:
        v = r[k].strip()
        assert v and not BAN.search(v), (r['名字'], k, v)
        cells.append('%s %s' % (k, v))
    return LABEL + '｜'.join(cells)


def main():
    tsv, apply = sys.argv[1], '--apply' in sys.argv
    rows = list(csv.DictReader(open(tsv, encoding='utf-8'), delimiter='\t'))
    want = {int(r['序号'].lstrip('#')): r for r in rows}
    done, skip = 0, 0
    for f in sorted(glob.glob('底卡洗稿/*.md')):
        raw = open(f, 'rb').read()
        crlf = b'\r\n' in raw
        s = raw.decode('utf-8').replace('\r\n', '\n')
        changed = False
        for m in list(re.finditer(r'(?m)^## #(\d+) [^\n]*\n', s))[::-1]:
            idx = int(m.group(1))
            if idx not in want:
                continue
            k = s.index('````\n', m.end()) + 5
            e = s.index('\n', k)
            nxt = s[e + 1:e + 1 + len(LABEL)]
            if nxt == LABEL:
                skip += 1
                continue
            s = s[:e + 1] + line_of(want[idx]) + '\n' + s[e + 1:]
            done += 1
            changed = True
        if changed and apply:
            out = s.replace('\n', '\r\n') if crlf else s
            open(f, 'wb').write(out.encode('utf-8'))
    print('表 %d 处，插 %d 处，已有 %d 处%s' % (len(want), done, skip, '' if apply else '（没写盘，加 --apply 写）'))
    assert done + skip == len(want), '表里有的条在洗稿层里没找到'


if __name__ == '__main__':
    main()
