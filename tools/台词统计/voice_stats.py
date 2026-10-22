#!/usr/bin/env python3
"""按说话人统计台词的形状：句长、语气词、自称、称呼、文言虚字、标点。
用法：python3 -I -X utf8 voice_stats.py OUT_DIR [最少句数]
读 OUT_DIR 下的 lines*.jsonl，写 OUT_DIR/stats_speakers.tsv。
"""
import glob, json, os, re, sys, statistics
from collections import defaultdict, Counter
OUT = sys.argv[1]; MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 80
PART = ['呢', '吧', '啊', '呀', '哦', '嘛', '啦', '哟', '喔', '咯', '哇', '嘞', '罢了', '而已', '么', '哈']
SELF = ['本小姐', '本大爷', '本姑娘', '本座', '在下', '吾', '老夫', '咱', '人家', '鄙人', '本王', '朕', '余', '小女子', '老身', '我们', '我']
ADDR = ['旅行者', '阁下', '您', '大人', '先生', '小姐', '伙伴', '朋友', '小家伙', '各位', '诸位', '汝', '你们', '你']
CLASS = '之乎者也矣焉哉亦其乃汝尔甚岂莫勿毋皆此彼故遂且犹'
INTJ = re.compile(r'^(嗯|啊|哦|唔|欸|诶|哈|呼|嘿|咳|哼|呵|哎|唉|嗨|呃|咦|嘁|哇)')
def feats(lines):
    n = len(lines)
    L = [len(re.sub(r'[\s「」『』，。！？…、：；“”‘’（）—\-]', '', x)) for x in lines]
    tail = Counter(); selfc = Counter(); addr = Counter()
    for x in lines:
        for s in re.split(r'[。！？…]+', x):
            s = s.strip('，、 「」')
            if re.search(r'(什|怎|这|那|多|要|干)么$', s):
                continue  # 什么、怎么这一类的么不是语气词
            for p in PART:
                if s.endswith(p):
                    tail[p] += 1; break
        tmp = x
        for w in SELF:
            c = tmp.count(w); selfc[w] += c; tmp = tmp.replace(w, '')
        tmp = x
        for w in ADDR:
            c = tmp.count(w); addr[w] += c; tmp = tmp.replace(w, '')
    chars = sum(L) or 1
    return dict(n=n, med=statistics.median(L) if L else 0, short=sum(1 for v in L if v <= 8) / n, long=sum(1 for v in L if v >= 40) / n,
                part=sum(tail.values()) / n, top_part=' '.join(f'{k}{v}' for k, v in tail.most_common(4)),
                ell=sum(x.count('…') for x in lines) / n, exc=sum(x.count('！') for x in lines) / n, q=sum(x.count('？') for x in lines) / n,
                dash=sum(x.count('——') for x in lines) / n, quote=sum(x.count('「') for x in lines) / n,
                cls=sum(sum(x.count(c) for c in CLASS) for x in lines) / chars * 100,
                intj=sum(1 for x in lines if INTJ.match(x)) / n,
                self=' '.join(f'{k}{v}' for k, v in selfc.most_common(4) if v), addr=' '.join(f'{k}{v}' for k, v in addr.most_common(4) if v))
by = defaultdict(lambda: defaultdict(list))
for f in glob.glob(os.path.join(OUT, 'lines*.jsonl')):
    for l in open(f, encoding='utf-8'):
        e = json.loads(l)
        if e['src'] == 'voice':
            by[e['speaker']]['voice'].append(e['text'])
        elif e['src'] in ('quest', 'idle') and not e.get('player'):
            by[e['speaker']]['story'].append(e['text'])
cols = ['n', 'med', 'short', 'long', 'part', 'top_part', 'ell', 'exc', 'q', 'dash', 'quote', 'cls', 'intj', 'self', 'addr']
with open(os.path.join(OUT, 'stats_speakers.tsv'), 'w', encoding='utf-8') as w:
    w.write('speaker\tkind\t' + '\t'.join(cols) + '\n')
    for sp, d in sorted(by.items(), key=lambda kv: -sum(len(v) for v in kv[1].values())):
        for kind in ('voice', 'story'):
            ls = d.get(kind, [])
            if len(ls) < (40 if kind == 'voice' else MIN):
                continue
            ft = feats(ls)
            w.write(f'{sp}\t{kind}\t' + '\t'.join(f'{ft[c]:.2f}' if isinstance(ft[c], float) else str(ft[c]) for c in cols) + '\n')
print('ok')
