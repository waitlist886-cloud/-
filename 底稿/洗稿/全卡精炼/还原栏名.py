#!/usr/bin/env python3
# 全卡精炼洗稿：把洗稿换掉的栏名照原稿改回来（11-16）。
#   python -I -X utf8 底稿/洗稿/全卡精炼/还原栏名.py --job <份名…> [--dry]        活的文件夹：稿/ 对 原/
#   python -I -X utf8 底稿/洗稿/全卡精炼/还原栏名.py --repo <仓库里的文件…> [--dry]  仓库里的页，原稿取标签 详本_11-15
# 缘故：洗稿的人爱把行首的栏名换个说法（“注意什么”写成“留意”，“往后”写成“后来”“下场”，“身上的东西”写成“掉落”），
# 审稿人每一页都在改，改得不齐。栏名是全卡一套的，一页一个叫法，主持的模型读着就不是同一张表。
# 做法：一节一节比行首的栏名（`- 栏名：` 和 `栏名：`，八个字以内）。两边栏名的个数一样、只是有几个叫法不同的，照原稿改回；
# 个数不一样的（洗稿并了栏、添了栏）拿 difflib 对齐，对得上的那几段照改，对不上的印出来给主会话看，不动。
# 另外把行首标签后头的句号改回冒号（“古尔巴与玛格达。”→“古尔巴与玛格达：”），只改原稿同一位置是冒号标签的。
# 冻住的节不碰。
import difflib
import io
import json
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
BASE = 'C:/Users/waitl/codex_work/wash_1115'
TAG = '详本_11-15'
FROZEN = re.compile(r'史诗|传唱|设计备注|传奇表|凡世至强')
LAB = re.compile(r'^(- |\*\*)?([^：:。，、；\n\s][^：:。，；\n]{0,9})：')


def cut(text):
    idx = [m.start() for m in re.finditer(r'^## ', text, re.M)] + [len(text)]
    return text[:idx[0]], [text[a:b] for a, b in zip(idx, idx[1:])]


def labels(sec):
    """回 [(行号, 前缀, 栏名)]。星的 ### 标题、条目设置、引用行不算。"""
    out = []
    for i, l in enumerate(sec.split('\n')):
        if l.startswith(('#', '>', '【')):
            continue
        m = LAB.match(l)
        if m:
            out.append((i, m.group(1) or '', m.group(2)))
    return out


def fix(new, old, label):
    hn, sn = cut(new)
    _, so = cut(old)
    if len(sn) != len(so):
        print('  %s｜节数对不上，不动' % label)
        return new, 0
    n, out = 0, []
    for a, b in zip(so, sn):
        title = b[:b.index('\n')][3:].strip()
        if FROZEN.search(title):
            out.append(b)
            continue
        la, lb = labels(a), labels(b)
        na, nb = [x[2] for x in la], [x[2] for x in lb]
        if na != nb:
            lines = b.split('\n')
            for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, na, nb, autojunk=False).get_opcodes():
                if tag == 'replace' and i2 - i1 == j2 - j1:
                    for k in range(i2 - i1):
                        ln, pre, cur = lb[j1 + k]
                        want = na[i1 + k]
                        lines[ln] = lines[ln].replace(pre + cur + '：', pre + want + '：', 1)
                        n += 1
                        print('  %s｜%s：%s → %s' % (label, title[:18], cur, want))
                elif tag != 'equal':
                    print('  %s｜%s：栏对不齐，没动（原 %s｜稿 %s）' % (label, title[:18], '、'.join(na[i1:i2]) or '无', '、'.join(nb[j1:j2]) or '无'))
            b = '\n'.join(lines)
        # 声口里的“- 不写：”常叫洗稿并进“- 情绪：”那一行的末尾。原稿有、洗后没有的，照原稿把这一行接回情绪后头。
        # 情绪行末尾那一句要是带“不是、不只、不止、并非”，就是并进来的那一句，拿掉；认不出来的留着，印出来给人看。
        if re.search(r'^- 不写：', a, re.M) and not re.search(r'^- 不写', b, re.M):
            org = re.search(r'^- 不写：[^\n]*', a, re.M).group(0)
            m = re.search(r'^- 情绪：[^\n]*', b, re.M)
            if m:
                emo = m.group(0)
                parts = re.split(r'(?<=。)', emo)
                parts = [x for x in parts if x]
                tail = parts[-1] if len(parts) > 1 else ''
                if tail and re.search(r'不是|不只|不止|并非|不光', tail):
                    emo2 = ''.join(parts[:-1])
                    note = '拿掉了情绪末尾并进来的一句：' + tail
                else:
                    emo2 = emo
                    note = '情绪末尾认不出并进来的那一句，没动，自己看：' + (tail or emo[-30:])
                b = b[:m.start()] + emo2 + '\n' + org + b[m.end():]
                n += 1
                print('  %s｜%s：接回“不写”一行｜%s' % (label, title[:18], note[:70]))
        sq = re.sub(r'\n{5,}', '\n\n\n', b)          # 洗稿删掉整段以后常留下七八个连着的空行，收成两个
        if sq != b:
            n += 1
            print('  %s｜%s：收了连着的空行' % (label, title[:18]))
            b = sq
        out.append(b)
    return hn + ''.join(out), n


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry' in sys.argv
    jobs = []
    if '--job' in sys.argv:
        for job in args:
            d = BASE + '/' + job
            for base in json.load(open(d + '/job.json', encoding='utf-8'))['files']:
                jobs.append((d + '/稿/' + base, open(d + '/原/' + base, encoding='utf-8', newline='').read(), job + '/' + base[:14]))
    else:
        for f in args:
            old = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (TAG, f)], capture_output=True).stdout.decode('utf-8')
            jobs.append((os.path.join(ROOT, f), old, os.path.basename(f)[:16]))
    total = 0
    for p, old, label in jobs:
        raw = open(p, encoding='utf-8', newline='').read()
        crlf = '\r\n' in raw
        new, n = fix(raw.replace('\r\n', '\n'), old.replace('\r\n', '\n'), label)
        total += n
        if n and not dry:
            open(p, 'w', encoding='utf-8', newline='').write(new.replace('\n', '\r\n') if crlf else new)
    print('改回 %d 个栏名%s' % (total, '（--dry 没写）' if dry else ''))


if __name__ == '__main__':
    main()
