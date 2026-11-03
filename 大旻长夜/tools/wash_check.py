# 洗稿收稿校验：python3 -I -X utf8 大旻长夜/tools/wash_check.py <份N_输入.json> <份N_输出.json>
# 输出 JSON 是 {"键": "改后的文字", …}；没改的键可以不写。逐条查：键在不在、专名丢没丢、引号和【】里的词在不在、
# 数字和外文在不在、长短（改后对原文 0.5 到 1.3 倍）、腔调黑名单。有问题的逐条列出来，最后一行是合计。
import json, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = {x['k']: x['t'] for x in json.load(open(sys.argv[1], encoding='utf-8'))}
out = json.load(open(sys.argv[2], encoding='utf-8'))
names = json.load(open(os.path.join(ROOT, '洗稿', '专名表.json'), encoding='utf-8'))
BLACK = ['一丝', '不易察觉', '嘴角', '眼中闪过', '眸中', '仿佛', '宛如', '犹如', '这一刻', '那一瞬间', '倒吸一口凉气', '空气仿佛', '某种', '难以言喻', '莫名',
         '真正的', '与其说', '——', '；']
bad, n, ratio = [], 0, []
for k, t2 in out.items():
    if k not in src: bad.append('多出来的键 %s' % k); continue
    t = src[k]; n += 1
    if not isinstance(t2, str) or not t2.strip(): bad.append('%s 空了' % k); continue
    r = len(t2) / max(len(t), 1); ratio.append(r)
    if r > 1.3 or r < 0.5: bad.append('%s 长短 %.2f 倍' % (k, r))
    for nm in names:
        if nm in t and nm not in t2: bad.append('%s 丢了专名「%s」' % (k, nm))
    for q in re.findall(r'[“【「]([^”】」]{1,30})[”】」]', t):
        if q not in t2: bad.append('%s 丢了引号里的「%s」' % (k, q))
    for a in re.findall(r'[0-9A-Za-z][0-9A-Za-z.·\-%]*', t):
        if a not in t2: bad.append('%s 丢了「%s」' % (k, a))
    for b in BLACK:
        c0, c1 = t.count(b), t2.count(b)
        if (c1 > c0 and b != '；') or (c1 and b in ('一丝', '不易察觉', '嘴角', '眼中闪过', '这一刻', '真正的')):
            bad.append('%s 腔调「%s」%d→%d' % (k, b, c0, c1))
semi0 = sum(src[k].count('；') for k in out if k in src); semi1 = sum(v.count('；') for v in out.values())
for b in bad: print(b)
print('改了 %d 条 / 输入 %d 条；平均长短 %.2f；分号 %d→%d；问题 %d 条' % (n, len(src), sum(ratio) / max(len(ratio), 1), semi0, semi1, len(bad)))
