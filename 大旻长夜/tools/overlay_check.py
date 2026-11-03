# 补充条目自查：python3 -I -X utf8 大旻长夜/tools/overlay_check.py 文件.md [原卡.json]
# 查：设置能不能读、正则安不安全、触发词撞不撞常用字、篇幅、跟原卡标题重不重、腔调黑名单。
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overlay import parse, regex_problems
text = open(sys.argv[1], encoding='utf-8').read()
items = parse(text)
titles = set()
if len(sys.argv) > 2:
    card = json.load(open(sys.argv[2], encoding='utf-8'))
    for e in card['world_book']:
        h = e['value'].strip().split('\n')[0].lstrip('# ').strip(); titles.add(h)
BLACK = ['一丝', '不易察觉', '嘴角', '眼中闪过', '仿佛', '宛如', '这一刻', '那一瞬间', '某种', '难以言喻', '莫名', '真正的', '与其说', '不是', '——']
def top_alts(r):
    """按最外层的 | 切开。"""
    out, depth, cur, i = [], 0, '', 0
    while i < len(r):
        c = r[i]
        if c == '\\':
            cur += r[i:i + 2]; i += 2; continue
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        if c == '|' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += c
        i += 1
    out.append(cur)
    return out
def bare_alts(r):
    """最外层每一项；整项是 (?:…) 的再往里剥一层。只有整项就是一两个字的才算太短。"""
    def wraps_whole(a):
        if not a.startswith('(?:') or not a.endswith(')'): return False
        depth, i = 0, 0
        while i < len(a):
            c = a[i]
            if c == '\\': i += 2; continue
            if c == '(': depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0: return i == len(a) - 1
            i += 1
        return False
    res = []
    for a in top_alts(r):
        a = a.strip()
        res += top_alts(a[3:-1]) if wraps_whole(a) else [a]
    return res
probs, n, total = [], 0, 0
for kind, cfg, body in items:
    if kind != '条目': continue
    n += 1; head = body.split('\n')[0].lstrip('# ').strip(); total += len(body)
    for key in ('folder', 'priority', 'user'):
        if key not in cfg: probs.append('%s 缺设置 %s' % (head, key))
    for w in [cfg.get('user', '')] + cfg.get('anchors', []) + cfg.get('black', []):
        for p in regex_problems(w): probs.append('%s 正则「%s…」%s' % (head, w[:30], p))
    u = cfg.get('user', '')
    for x in bare_alts(u):
        if re.fullmatch(r'[一-鿿]{1,2}', x):
            probs.append('%s 触发词「%s」单独成一项，太短，会到处醒' % (head, x))
    if not (80 <= len(body) <= 1200): probs.append('%s 篇幅 %d 字' % (head, len(body)))
    if head in titles: probs.append('%s 跟原卡标题重了' % head)
    for b in BLACK:
        if b in body and not (b == '不是' and '不是……而是' not in body and re.search(r'不是[^。]{1,24}而是', body) is None):
            probs.append('%s 腔调「%s」' % (head, b))
for p in probs: print(p)
print('条目 %d 条，正文 %d 字，问题 %d 条' % (n, total, len(probs)))
