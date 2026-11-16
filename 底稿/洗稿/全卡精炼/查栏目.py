#!/usr/bin/env python3
# 全卡精炼洗稿：洗后的页对原稿，查两类自查和审稿都容易漏的（11-16 第三歌校验时查出来的）。在仓库根上跑：
#   python -I -X utf8 底稿/洗稿/全卡精炼/查栏目.py <仓库里的文件…>            原稿取标签 详本_11-15
#   python -I -X utf8 底稿/洗稿/全卡精炼/查栏目.py --job <份名…>               活的文件夹里 稿/ 对 原/
# 一、乔装的神：人物条“是谁”“样子”这类栏原稿用他、她，洗后写成了祂（把身份说早了）。
# 二、凡世至强（传奇）条：原稿有的栏洗后没了（凝名伟业、相关的事、传奇之名、凝名纪年、位阶这些行首标签），
#     专属那一行的“｜效果：｜界限：｜说法：”三栏被压成了一句，使用规则里这一条独有的规矩（“下落这一卷不写”）没了。
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
FROZEN = re.compile(r'史诗|传唱|设计备注|传奇表')
LABEL = re.compile(r'^(?:- )?(?:\*\*)?([^：｜，。\s]{2,8})：')


def sections(text):
    out, cur, buf = [], '', []
    for l in text.split('\n'):
        if l.startswith('## '):
            out.append((cur, buf))
            cur, buf = l[3:].strip(), [l]
        else:
            buf.append(l)
    out.append((cur, buf))
    return out


def check(label, old, new):
    so, sn = sections(old), dict(sections(new))
    bad = 0
    for t, lo in so:
        if not t or FROZEN.search(t) or t not in sn:
            continue
        ln = sn[t]
        # 一、祂
        for key in ('是谁', '样子', '做派', '身份', '外貌'):
            ao = [l for l in lo if re.match(r'^(?:- )?' + key + '：', l)]
            an = [l for l in ln if re.match(r'^(?:- )?' + key + '：', l)]
            if ao and an and '祂' in an[0] and '祂' not in ao[0]:
                print('  ！%s｜%s｜“%s”一栏原稿不用祂，洗后用了：%s' % (label, t[:24], key, an[0][:50]))
                bad += 1
        # 二、行首标签
        lab_o = [m.group(1) for l in lo for m in [LABEL.match(l)] if m]
        lab_n = set(m.group(1) for l in ln for m in [LABEL.match(l)] if m)
        lost = []
        for k in lab_o:
            if k not in lab_n and k not in lost:
                lost.append(k)
        legend = '凡世至强' in t or '传奇' in t
        if lost and (legend or len(lost) >= 1):
            print('  %s%s｜%s｜原稿有、洗后没了的行首标签：%s' % ('！' if legend else '看 ', label, t[:24], '、'.join(lost[:10])))
            bad += legend
        for part in ('｜效果：', '｜界限：', '｜说法：'):
            co, cn = sum(l.count(part) for l in lo), sum(l.count(part) for l in ln)
            if cn < co:
                print('  ！%s｜%s｜专属那一行的“%s”少了（%d → %d）' % (label, t[:24], part.strip('｜：'), co, cn))
                bad += 1
        for rule in ('这一卷不写', '不写他的下落', '下落不给', '不裁定'):
            if sum(l.count(rule) for l in lo) > sum(l.count(rule) for l in ln) and legend:
                print('  看 %s｜%s｜“%s”这一句原稿有、洗后少了' % (label, t[:24], rule))
    return bad


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    total = 0
    if '--job' in sys.argv:
        for j in args:
            d = BASE + '/' + j
            for base in json.load(open(d + '/job.json', encoding='utf-8'))['files']:
                old = open(d + '/原/' + base, encoding='utf-8').read().replace('\r\n', '\n')
                new = open(d + '/稿/' + base, encoding='utf-8').read().replace('\r\n', '\n')
                total += check(j + '/' + base[:6], old, new)
    else:
        for f in args:
            old = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (TAG, f)], capture_output=True).stdout.decode('utf-8').replace('\r\n', '\n')
            new = open(os.path.join(ROOT, f), encoding='utf-8').read().replace('\r\n', '\n')
            total += check(os.path.basename(f)[:6], old, new)
    print('带 ！ 的 %d 处' % total)


if __name__ == '__main__':
    main()
