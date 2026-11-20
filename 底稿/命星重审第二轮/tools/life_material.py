#!/usr/bin/env python3
# 门面按主线细分（11-20）：一页一份生卒材料，写 材料/生_<页>.md，交 batch.py life。
#   python -I -X utf8 底稿/命星重审第二轮/tools/life_material.py
# 每个人一段：旅伴条（连同它的背景条）、人物条（一条里有几个人的整条给，写手自己拆），
# 只留带年份、岁数、生死、凝名、位阶的行，台词、声口、好感、能力、星条不给。凡世至强不给（传奇另有数据）。
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.path.normpath(os.path.join(W, '..', '..'))
MAT = os.path.join(W, '材料')
NL = chr(10)
KEEP = re.compile(r'\d+年|元年|生于|岁|死|殁|亡|凝|传奇|LVL|位阶|启源|共鸣|灵格|极境|英雄|老|种族|身份|固定锚定|底座|下场|寿|活到|活过|去世|葬|走了|突破|跨进|跨过')
DROP = re.compile(r'^(台词样例|- 台词|【独立声口|【好感|能力：|兼修：|- 句式|- 注意|- 称谓|- 情绪|- 不写|- 加：|- 减：|- 坎：|- 破裂|技艺走势|> 条目设置|体态数据|容貌评价|装束|外貌)')


def entries(t):
    pos = [m.start() for m in re.finditer(r'(?m)^## (?!裁定锁)', t)]
    return [t[s:(pos[i + 1] if i + 1 < len(pos) else len(t))] for i, s in enumerate(pos)]


def trim(e, cap=3200):
    out = []
    for l in e.split(NL)[1:]:
        s = l.strip()
        if not s or DROP.match(s) or not KEEP.search(s):
            continue
        out.append(s[:420])
    t = NL.join(out)
    return t[:cap]


def main():
    idx = json.load(open(os.path.join(MAT, '索引.json'), encoding='utf-8'))
    tot = 0
    for key, v in idx.items():
        t = open(os.path.join(ROOT, v['file']), encoding='utf-8').read().replace(chr(13) + NL, NL)
        es = entries(t)
        bg = {}
        for e in es:
            h = e.split(NL, 1)[0]
            if h.startswith('## 旅途同行·背景：'):
                nm = re.sub(r'（.*', '', h.split('：', 1)[1]).strip()
                bg[nm] = bg.get(nm, '') + NL + trim(e, 1600)
        parts = []
        for e in es:
            h = e.split(NL, 1)[0]
            if h.startswith('## 旅途同行：'):
                nm = re.match(r'## 旅途同行：([^（\n]+)', h).group(1).strip()
                body = trim(e) + (NL + '（背景条）' + bg[nm] if nm in bg else '')
                parts.append('=' * 20 + NL + '【旅伴条】' + h[3:] + NL + body)
            elif h.endswith('（人物）') or '·人物｜' in h:
                body = trim(e, 4200)
                if body:
                    parts.append('=' * 20 + NL + '【人物条】' + h[3:] + NL + body)
        head = '# %s（%s）：%d 条' % (key, v['file'], len(parts)) + NL
        open(os.path.join(MAT, '生_%s.md' % key), 'w', encoding='utf-8', newline=NL).write(head + NL.join(parts) + NL)
        tot += len(parts)
    print('写了', tot, '条')


if __name__ == '__main__':
    main()
