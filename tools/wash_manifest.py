"""底卡洗稿的分批清单（10-25，照 底卡洗稿与命名重审_方向稿_第三版.md 第一节第6条）。

用法：python3 -I -X utf8 tools/wash_manifest.py 批 [份数] [--card 打好的卡.json]
  批是 1 到 6，份数不给就照字数自己分（一份四五万字上下）。
清单写到 底稿/洗稿/底卡洗稿_第N批_清单.md：每份一节，一条一行，#号、文件夹、标题、字数、底本哈希，
节头写这一份的洗稿文件写到哪里（底卡洗稿/批次_文件夹_名_份.md）。
底本是打完补丁的那一版底卡（打好的卡前一千三百九十七条，照 #号排），哈希跟 tools/wash_check.py 一个算法。
"""
import sys, os, json, hashlib, re

DEFAULT_CARD = 'out/进卡_v9/奥尔德兰_日里版_三纪全卷_测试v9.json'
BATCHES = {
    1: ['16', '15', '27', '20'],
    2: ['02', '03', '04', '06', '08', '09', '10', '11'],
    3: ['12', '13', '14', '17', '18', '19'],
    4: ['21', '22', '23', '24', '25', '26', '28'],
    5: ['07'],
    6: ['00', '01', '05', '90', '91'],
}
CN = '一二三四五六七八九十'


def cn(i):
    i += 1
    if i <= 10:
        return CN[i - 1]
    if i < 20:
        return '十' + CN[i - 11]
    return CN[i // 10 - 1] + '十' + (CN[i % 10 - 1] if i % 10 else '')
SHARE_CHARS = 45000


def load_lorebook(path):
    card = json.load(open(path, encoding='utf-8'))

    def find(c):
        if isinstance(c, dict):
            for v in c.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and 'content' in v[0]:
                    return v
                r = find(v)
                if r:
                    return r
    return find(card)


def sha12(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]


def short_folder(folder):
    num, name = folder.split('·', 1)
    name = name.split('｜')[0]
    name = re.split(r'[、与]', name)[0]
    return num, name


def main(argv):
    card = DEFAULT_CARD
    args = []
    i = 0
    while i < len(argv):
        if argv[i] == '--card':
            card = argv[i + 1]; i += 2
        else:
            args.append(argv[i]); i += 1
    n = int(args[0])
    want = int(args[1]) if len(args) > 1 else None
    lb = load_lorebook(card)[:1397]
    rows = [(idx, e['folder'], e['content']) for idx, e in enumerate(lb) if e['folder'][:2] in BATCHES[n]]
    rows.sort(key=lambda r: (BATCHES[n].index(r[1][:2]), r[1], r[0]))
    total = sum(len(r[2]) for r in rows)
    k = want or max(1, round(total / SHARE_CHARS))
    target = total / k
    shares, cur, acc = [], [], 0
    for r in rows:
        if cur and acc + len(r[2]) / 2 > target * (len(shares) + 1) and len(shares) < k - 1:
            shares.append(cur); cur = []
        cur.append(r)
        acc += len(r[2])
    if cur:
        shares.append(cur)
    out = ['# 底卡洗稿 第%s批 清单' % cn(n - 1), '',
           '照 底卡洗稿与命名重审_方向稿_第三版.md 第一节、底稿/洗稿/底卡洗稿_计划.md 洗。%d 条，%d 字，分 %d 份。' % (len(rows), total, len(shares)),
           '底本是 %s 前一千三百九十七条（v9 打完补丁的底卡），哈希是正文 sha1 前十二位，洗稿文件里照抄。' % card, '']
    for si, sh in enumerate(shares):
        nums = sorted(set(short_folder(r[1]) for r in sh), key=lambda x: x[0])
        fname = '底卡洗稿/批次_%s_%s.md' % ('_'.join(a + b for a, b in nums[:2]), cn(si))
        out.append('## 第%s份（%d 条，%d 字）→ %s' % (cn(si), len(sh), sum(len(r[2]) for r in sh), fname))
        out.append('')
        out.append('| # | 文件夹 | 标题 | 字数 | 底本哈希 |')
        out.append('|---|---|---|---|---|')
        for idx, folder, content in sh:
            title = content.split('\n')[0].lstrip('# ').strip()
            out.append('| %d | %s | %s | %d | %s |' % (idx, folder, title.replace('|', '｜')[:40], len(content), sha12(content)))
        out.append('')
    os.makedirs('底稿/洗稿', exist_ok=True)
    path = '底稿/洗稿/底卡洗稿_第%s批_清单.md' % cn(n - 1)
    open(path, 'w', encoding='utf-8').write('\n'.join(out))
    print('%s：%d 条，%d 字，%d 份' % (path, len(rows), total, len(shares)))
    for si, sh in enumerate(shares):
        print('  第%d份 %d 条 %d 字' % (si + 1, len(sh), sum(len(r[2]) for r in sh)))


if __name__ == '__main__':
    main(sys.argv[1:])
