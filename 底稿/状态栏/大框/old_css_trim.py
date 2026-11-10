# 11-10 清样式（用户：“style里面你可以看看清理去除掉那些已经用不上了的旧东西”）：底卡原来那一段样式（旧对话的 HTML 状态栏用的），
# 11-04 起旧回复先经转换那一组规则变成 § 记录、再照大框展开，旧的类名（arc-* 那一套）在页面上不再出现，认它们的样式白占地方。
# 做法：旧词表 = 底卡原来骨架里写的类名 + 旧回复样本里出现的类名 + 一切 arc- 开头的；活的 = 卡里规则展开出来会有的类名 + 大框样式里认的类名。
# 旧词表减去活的，就是死了的类名。一条样式所有选择器都要一个死了的类名才删；@keyframes、@font-face、@media 里头照这个规矩一条一条看。
import re


def _classes(sel):
    return set(re.findall(r'\.([a-zA-Z_][\w-]*)', re.sub(r'"[^"]*"|\'[^\']*\'', '', sel)))


def split_top(css):
    """顶层切成一条一条（选择器{…}、@规则{…}）；注释扔掉"""
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    out, i, depth, start, q = [], 0, 0, 0, None
    while i < len(css):
        c = css[i]
        if q:
            if c == '\\':
                i += 1
            elif c == q:
                q = None
        elif c in '"\'':
            q = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                out.append(css[start:i + 1].strip())
                start = i + 1
        elif c == ';' and depth == 0:
            out.append(css[start:i + 1].strip())
            start = i + 1
        i += 1
    tail = css[start:].strip()
    if tail:
        out.append(tail)
    return [x for x in out if x]


def split_sel(s):
    parts, d, cur, q = [], 0, '', None
    for c in s:
        if q:
            cur += c
            if c == q:
                q = None
            continue
        if c in '"\'':
            q = c
        if c in '([':
            d += 1
        if c in ')]':
            d -= 1
        if c == ',' and d == 0:
            parts.append(cur)
            cur = ''
        else:
            cur += c
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def trim(css, dead):
    """把所有选择器都认死类名的样式删掉；返回 (留下的样式, 删了几条, 删了多少字)"""
    kept, n, chars = [], 0, 0
    for blk in split_top(css):
        if blk.startswith('@media') or blk.startswith('@supports'):
            head, body = blk.split('{', 1)
            inner, k, c2 = trim(body[:-1], dead)
            n += k
            chars += c2
            if inner.strip():
                kept.append(head + '{' + inner + '}')
            continue
        if blk.startswith('@'):
            kept.append(blk)
            continue
        if '{' not in blk:
            kept.append(blk)
            continue
        sel, body = blk.split('{', 1)
        sels = split_sel(sel)
        live = [s for s in sels if not (_classes(s) & dead)]   # 认死类名的那几个选择器拿掉，一个不剩整条删
        if not live:
            n += 1
            chars += len(blk)
            continue
        if len(live) < len(sels):
            nb = ','.join(live) + '{' + body
            chars += len(blk) - len(nb)
            blk = nb
        kept.append(blk)
    return '\n'.join(kept), n, chars


def dead_classes(old_vocab, live):
    return {c for c in old_vocab if c not in live} | set()


def live_classes(rules, css_texts):
    live = set()
    for r in rules:
        for m in re.finditer(r'class="([^"]*)"', r.get('replaceString', '')):
            live |= set(m.group(1).split())
    for t in css_texts:
        live |= _classes(re.sub(r'/\*[\s\S]*?\*/', '', t))
    return live


def old_vocab(texts):
    v = set()
    for t in texts:
        for m in re.finditer(r'class=\\?"([^"\\]*)', t):
            v |= set(m.group(1).split())
    return v


def for_card(old, rules, new_css):
    """四纪大框用：旧词表从底卡原来的主提示词、世界书、介绍页和旧回复样本里取，活的从这一张的规则和新样式里取。返回 (留下的样式, 删了几条, 少了几个字)"""
    import glob
    import json
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.abspath(os.path.join(here, '..', '..', '..'))
    base = json.load(open(os.path.join(repo, 'src', 'rili_v7.json'), encoding='utf-8'))
    texts = [base['prompt'].get(k, '') or '' for k in ('systemPrompt', 'rearPrompt', 'headPrompt')]
    texts += [e.get('content') or '' for e in base['prompt']['lorebook']]
    samples = (glob.glob(os.path.join(here, '发布', '试写', 'old_*.html')) + glob.glob(os.path.join(repo, '底稿', '状态栏', '样张', '样本_*.html'))
               + glob.glob(os.path.join(repo, 'moon', 'samples', '*.html')) + [os.path.join(here, '发布', '试写', '写混了的回复.txt')])
    texts += [open(f, encoding='utf-8').read() for f in samples if os.path.exists(f)]
    intro = open(os.path.join(repo, 'src', 'intro_v7.html'), encoding='utf-8').read()
    vocab = old_vocab(texts) | {c for c in _classes(old) if c.startswith('arc-')} | _classes(re.sub(r'/\*[\s\S]*?\*/', '', intro)) | old_vocab([intro])
    live = live_classes(rules, [new_css])
    return trim(old, {c for c in vocab if c not in live})
