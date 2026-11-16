#!/usr/bin/env python3
# 旅伴条里三样照留的东西，洗稿删了的照原稿补回（11-16 夜，Claude 洗稿人头一拨删过）：
#   手写活人层（### 手写活人层｜… 底下的各条）：条数比原稿少了，整块换回原稿。
#   【独立声口】的台词样例：引号里的话跟原稿不是同一串（少了、改了字），换回原稿那一行；整行没了的接回声口块末尾。
#   【好感增减】：加、减、坎、破裂几项少了，分数变了，或者坎少了一样，整块换回原稿。
# 洗稿说明第五节那张表：“声口照留只收字，手写活人层照留，好感照留”。只收了字、条数和分数都对的不动。
#   python -I -X utf8 底稿/洗稿/全卡精炼/还原活人层.py <份名…> [--dir 稿] [--apply]
#   python -I -X utf8 底稿/洗稿/全卡精炼/还原活人层.py --repo <仓库里的文件…> [--apply]   （原稿取标签 详本_11-15）
# 不加 --apply 只报。只看标题是“旅途同行：”起头的节（背景条不管）。
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
STOP = ('### ', '## ', '【', '> ', '专属羁绊')
QUOTE = re.compile(r'“([^”]*)”')
NUM = re.compile(r'[+＋−-]\s?\d+')

args = [a for a in sys.argv[1:] if not a.startswith('--')]
APPLY = '--apply' in sys.argv
REPO = '--repo' in sys.argv
DIR = '稿'
if '--dir' in sys.argv:
    DIR = sys.argv[sys.argv.index('--dir') + 1]
    args = [a for a in args if a != DIR]
# --skip 名字,名字：这几个人不动（用户认过的样稿里改过的，比如第七歌麦伦的台词样例）
SKIP = set()
if '--skip' in sys.argv:
    v = sys.argv[sys.argv.index('--skip') + 1]
    SKIP = set(x for x in re.split(r'[,，、]', v) if x)
    args = [a for a in args if a != v]


def sections(lines):
    out, cur = [], None
    for i, ln in enumerate(lines):
        if ln.startswith('## '):
            cur = [ln[3:].strip(), i, len(lines)]
            if out:
                out[-1][2] = i
            out.append(cur)
    return out


def companions(lines):
    return {t: (a, b) for t, a, b in sections(lines) if t.startswith('旅途同行：')}


def block_live(lines, a, b):
    for i in range(a, b):
        if lines[i].startswith('### 手写活人层'):
            j = i + 1
            while j < b and not lines[j].startswith(STOP):
                j += 1
            while j > i + 1 and not lines[j - 1].strip():
                j -= 1
            return i, j
    return None


def block_fav(lines, a, b):
    for i in range(a, b):
        if lines[i].startswith('【好感增减'):
            j = i + 1
            while j < b and lines[j].startswith('- '):
                j += 1
            return i, j
    return None


def line_said(lines, a, b):
    for i in range(a, b):
        s = lines[i].lstrip('- ')
        if s.startswith('台词样例'):
            return i
    return None


def voice_end(lines, a, b):
    for i in range(a, b):
        if lines[i].startswith('【独立声口'):
            j = i + 1
            while j < b and lines[j].startswith('- '):
                j += 1
            return j
    return None


def fav_bad(old, new):
    pre = lambda ls: [l.split('：', 1)[0] for l in ls[1:]]
    if pre(old) != pre(new):
        return '少了一项' if len(new) < len(old) else '项目不一样'
    if NUM.findall(''.join(old)) != NUM.findall(''.join(new)):
        return '分数变了'
    for o, n in zip(old[1:], new[1:]):
        if o.split('：', 1)[0].endswith('坎') and o.count('｜') != n.count('｜'):
            return '坎少了一样'
    return ''


def fix(orig_text, new_text, label):
    crlf = '\r\n' in new_text
    o = orig_text.replace('\r\n', '\n').split('\n')
    n = new_text.replace('\r\n', '\n').split('\n')
    co = companions(o)
    notes = []
    # 从后往前改，前头的行号不挪
    for title, (na, nb) in sorted(companions(n).items(), key=lambda kv: -kv[1][0]):
        if title not in co:
            continue
        oa, ob = co[title]
        who = re.sub(r'（.*$', '', title.split('：', 1)[1])
        if who in SKIP or who.split('·')[0] in SKIP:
            continue
        # 好感
        fo, fn = block_fav(o, oa, ob), block_fav(n, na, nb)
        if fo:
            old = o[fo[0]:fo[1]]
            if not fn:
                notes.append('%s｜好感整块没了，没法自动补，手补' % who)
            else:
                why = fav_bad(old, n[fn[0]:fn[1]])
                if why:
                    n[fn[0]:fn[1]] = old
                    notes.append('%s｜好感%s，换回原稿' % (who, why))
        # 活人层
        lo, ln_ = block_live(o, oa, ob), block_live(n, na, nb)
        if lo:
            old = o[lo[0]:lo[1]]
            if not ln_:
                notes.append('%s｜活人层整块没了，没法自动补，手补' % who)
            else:
                new = n[ln_[0]:ln_[1]]
                c_old = sum(1 for x in old[1:] if x.strip())
                c_new = sum(1 for x in new[1:] if x.strip())
                if c_new < c_old:
                    n[ln_[0]:ln_[1]] = old
                    notes.append('%s｜活人层 %d 条剩 %d 条，换回原稿' % (who, c_old, c_new))
        # 台词样例
        so = line_said(o, oa, ob)
        if so is not None:
            sn = line_said(n, na, nb)
            if sn is None:
                ve = voice_end(n, na, nb)
                if ve is None:
                    notes.append('%s｜台词样例和声口块都没了，手补' % who)
                else:
                    n.insert(ve, o[so])
                    notes.append('%s｜台词样例整行没了，接回声口块末尾' % who)
            elif QUOTE.findall(n[sn]) != QUOTE.findall(o[so]):
                k_old, k_new = len(QUOTE.findall(o[so])), len(QUOTE.findall(n[sn]))
                n[sn] = o[so]
                notes.append('%s｜台词样例 %d 句%s，换回原稿' % (who, k_old, ('剩 %d 句' % k_new) if k_new < k_old else '改了字'))
    out = '\n'.join(n)
    if crlf:
        out = out.replace('\n', '\r\n')
    return out, notes[::-1]


def run_one(orig_text, path, label):
    new_text = open(path, encoding='utf-8', newline='').read()
    out, notes = fix(orig_text, new_text, label)
    for x in notes:
        print('%s｜%s' % (label, x))
    if APPLY and out != new_text:
        # Windows 上别的进程正映射着这个文件时会报 Errno 22，隔一会儿再写
        import time
        for k in range(8):
            try:
                open(path, 'w', encoding='utf-8', newline='').write(out)
                break
            except OSError:
                if k == 7:
                    raise
                time.sleep(2)
    return len(notes)


total = 0
if REPO:
    for p in args:
        rel = os.path.relpath(os.path.abspath(p), ROOT).replace('\\', '/')
        r = subprocess.run(['git', 'show', '%s:%s' % (TAG, rel)], cwd=ROOT, capture_output=True)
        if r.returncode:
            print('%s｜标签里没有这个文件，跳过' % rel)
            continue
        total += run_one(r.stdout.decode('utf-8'), os.path.join(ROOT, rel), rel)
else:
    for job in args:
        d = '%s/%s' % (BASE, job)
        for f in json.load(open(d + '/job.json', encoding='utf-8'))['files']:
            fn = os.path.basename(f)
            p = '%s/%s/%s' % (d, DIR, fn)
            if not os.path.exists(p):
                continue
            total += run_one(open('%s/原/%s' % (d, fn), encoding='utf-8', newline='').read(), p, '%s/%s/%s' % (job, DIR, fn))
print('一共 %d 处%s' % (total, '，改了' if APPLY else '（只报，加 --apply 才改）'))
