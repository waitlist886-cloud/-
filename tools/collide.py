# 用法：python -X utf8 tools/collide.py 词1 词2 ... —— 在底卡、月银纪三批、各页、原神语料里查撞名（子串也算）
# 根目录是 tools/ 的上一级；语料放在根目录的 语料/ 下（不在包里，要用就用 genshin-item-lore 的抓取脚本重抓）
import sys, os, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = {}
d = json.load(open(os.path.join(ROOT, 'src', 'rili_v7.json'), encoding='utf-8'))
lb = d.get('prompt', {}).get('lorebook') or []
src['底卡'] = d.get('prompt', {}).get('systemPrompt', '') + '\n'.join((e.get('content') or '') for e in lb)
for b in ['batch1', 'batch2', 'batch3']:
    src['moon/' + b] = '\n'.join(open(f, encoding='utf-8').read() for f in glob.glob(os.path.join(ROOT, 'moon', b, '*.md')))
for sub in ['月银纪史诗', '诸国期', '萨尔维斯']:
    src[sub] = '\n'.join(open(f, encoding='utf-8').read() for f in glob.glob(os.path.join(ROOT, sub, '*.md')))
corpus = os.path.join(ROOT, '语料')
if os.path.isdir(corpus):
    src['原神语料'] = '\n'.join(open(f, encoding='utf-8').read() for f in glob.glob(os.path.join(corpus, '**', '*.md'), recursive=True))
for w in sys.argv[1:]:
    hits = []
    for k, t in src.items():
        n = t.count(w)
        if n:
            i = t.find(w)
            hits.append('%s×%d「%s」' % (k, n, t[max(0, i - 12):i + len(w) + 12].replace('\n', ' ')))
    print(w, '：', '无' if not hits else '；'.join(hits))
