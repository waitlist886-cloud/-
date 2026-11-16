#!/usr/bin/env python3
# 全卡精炼洗稿：审稿人删掉的句子里，有没有其实是原稿别的节里的事（11-16）。在仓库根上跑：
#   python -I -X utf8 底稿/洗稿/全卡精炼/查误删.py <份名…> [--min 0.5]
# 缘故：洗稿的人照“一件事只住一处”把默认收束里各人的下场挪进了各人的条目，审稿人只对着同一节的原稿看，
# 会把挪进来的句子当成“添出来的东西”删掉（诸国期晚祷上：皮帕看见了金冕城的屋顶、埃米尔的儿子孙子、贡特埋在哪）。一页分给两位审稿人的时候更容易犯。
# 做法：拿 稿_Codex原样/ 跟 稿/ 比，找出审稿以后没了的句子，再看这一句的四字串有多少在整份原稿里找得到。
# 找得到一半以上、洗后全文里又找不到的，印出来给主会话看（连它在洗稿里原来待的那一节）。只报不改。
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = 'C:/Users/waitl/codex_work/wash_1115'
FROZEN = re.compile(r'史诗|传唱|设计备注|传奇表|凡世至强')


def read(p):
    return open(p, encoding='utf-8').read().replace('\r\n', '\n')


def sections(text):
    idx = [m.start() for m in re.finditer(r'^## ', text, re.M)] + [len(text)]
    return [(text[a:text.index('\n', a)][3:].strip(), text[a:b]) for a, b in zip(idx, idx[1:])]


def sents(body):
    out = []
    for line in body.split('\n'):
        if line.startswith(('#', '>')):
            continue
        for s in re.split(r'(?<=[。？])', line):
            s = s.strip()
            if len(re.findall(r'[\u4e00-\u9fff]', s)) >= 8:
                out.append(s)
    return out


def grams(s, n=4):
    h = ''.join(re.findall(r'[\u4e00-\u9fff0-9]', s))
    return [h[i:i + n] for i in range(len(h) - n + 1)]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    lo = 0.5
    if '--min' in sys.argv:
        k = sys.argv[sys.argv.index('--min') + 1]
        lo = float(k)
        args.remove(k)
    for job in args:
        d = BASE + '/' + job
        meta = json.load(open(d + '/job.json', encoding='utf-8'))
        for base in meta['files']:
            old, cdx, new = read(d + '/原/' + base), read(d + '/稿_Codex原样/' + base), read(d + '/稿/' + base)
            # 冻住的节不进卡里“活”的正文的不算数：设计备注、传奇表里有这件事，不等于卡里还有
            live_new = ''.join(b for t, b in sections(new) if not re.search(r'设计备注|传奇表', t))
            g_old = set(grams(old))
            g_new = set(grams(live_new))
            sn = dict(sections(new))
            hits = []
            for t, body in sections(cdx):
                if FROZEN.search(t) or t not in sn or '命星' in t:          # 命星一节不看：Special 的头一段是脚本照原稿还原的，句句都“没了”
                    continue
                now = set(sents(sn[t]))
                for s in sents(body):
                    if s in now:
                        continue
                    g = grams(s)
                    if len(g) < 5:
                        continue
                    in_old = sum(1 for x in g if x in g_old) / len(g)
                    in_new = sum(1 for x in g if x in g_new) / len(g)
                    if in_old >= lo and in_new < 0.6:
                        hits.append((t, s, in_old, in_new))
            print('== %s｜%s：审稿以后没了、原稿别处其实有的句子 %d 句' % (job, base, len(hits)))
            for t, s, a, b in hits:
                print('  [%s]（原稿里对得上 %d%%，洗后别处对得上 %d%%）' % (t[:26], a * 100, b * 100))
                print('     ' + s[:200])


if __name__ == '__main__':
    main()
