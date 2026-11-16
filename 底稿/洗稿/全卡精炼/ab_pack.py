#!/usr/bin/env python3
# 全卡精炼洗稿：洗前洗后各主持一轮，比戏有没有变薄（11-16）。
#   python -I -X utf8 底稿/洗稿/全卡精炼/ab_pack.py <卡.json> <场景.json> <输出文件夹>
# 照日里的做法算这一轮会醒哪些世界书条目（深度圈最近几条消息、按范围挑、一条一条单独判，加权条目照固定的种子抽一张），
# 把主提示词、后置词、醒了的条目、上一轮回复、玩家这一句写进一个文件夹，再配一份 任务.md，交给模型写这一轮的回复。
# 同一个场景拿洗前、洗后两张卡各搭一个文件夹，上一轮回复和玩家的话一样，差别只在世界书。
# 跑：bash tools/gemini_try/run_agy.sh <文件夹…>（Gemini 4 Argon），或者派 Claude 子任务照 任务.md 写。
# 场景.json：{"name": 名, "msgs": [["user"|"assistant", 文本或 "@相对仓库根的文件"], …], "seed": 7, "note": 看什么}
import io
import json
import os
import random
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
han = lambda s: len(re.findall(r'[一-鿿]', s))
RX = {}


def rx(t):
    m = re.match(r'^/([\s\S]*)/([a-z]*)$', t)
    if not m:
        return None
    fl = 0
    for ch in m.group(2):
        fl |= {'i': re.I, 'm': re.M, 's': re.S}.get(ch, 0)
    try:
        return re.compile(m.group(1), fl)
    except re.error:
        return None


def hit(words, typ, msg):
    if not words:
        return False
    res = []
    for w in words:
        if w not in RX:
            RX[w] = rx(w) if w.startswith('/') else None
        r = RX[w]
        res.append(bool(r.search(msg)) if r else (w in msg))
    return all(res) if typ == 'AND' else any(res)


def main():
    card = json.load(open(sys.argv[1], encoding='utf-8'))
    scen = json.load(open(sys.argv[2], encoding='utf-8'))
    out = sys.argv[3]
    msgs = []
    for role, t in scen['msgs']:
        if t.startswith('@'):
            t = open(os.path.join(ROOT, t[1:]), encoding='utf-8').read().replace('\r\n', '\n')
        msgs.append((role, t))
    assert msgs[-1][0] == 'user'
    p = card['prompt']
    sp, rear, head = p.get('systemPrompt') or '', p.get('rearPrompt') or '', p.get('headPrompt') or ''
    rnd = random.Random(scen.get('seed', 7))
    woke = []
    for i, e in enumerate(p['lorebook']):
        if not e.get('enabled', True):
            continue
        d = e.get('scanDepth', 1) or 1
        rng = e.get('triggerRange') or []
        pool = [(r, t) for r, t in msgs[-d:] if r in rng]
        if 'system' in rng:
            pool.append(('system', sp))
        ok = any(hit(e.get('triggerWords'), e.get('triggerWordsType', 'OR'), t) and not hit(e.get('blackListWords'), e.get('blackListWordsType', 'OR'), t) for _, t in pool)
        if not ok:
            continue
        pr = e.get('probability', 100) or 100
        roll = rnd.uniform(0, 100)                  # 每条都掷一回，两张卡条目先后一样的地方掷出来的也一样
        if pr < 100 and roll > pr:
            continue
        if e.get('contentMethod') == 'weighted':
            acc, c0 = 0, None
            for c in e['contents']:
                acc += c['probability']
                if roll <= acc:
                    c0 = c['content']
                    break
            body = c0 if c0 is not None else e['contents'][-1]['content']
        else:
            body = e.get('content') or ''
        woke.append((e.get('priority', 0), i, body, e.get('impactRange') or ['system'], e.get('folder') or ''))
    woke.sort(key=lambda x: (x[0], x[1]))
    os.makedirs(out, exist_ok=True)

    def w(name, text):
        open(os.path.join(out, name), 'w', encoding='utf-8', newline='\n').write(text)

    w('系统提示词.md', sp + '\n\n（以下是每轮贴在玩家消息后面的后置提示）\n' + rear + (('\n\n（以下是每轮贴在玩家消息前面的前置提示）\n' + head) if head else ''))
    w('世界书_本轮.md', '\n\n=====\n\n'.join(c for _, _, c, _, _ in woke))
    hist = msgs[:-1]
    w('前面的对话.md', '\n\n'.join('【%s】\n%s' % ('玩家' if r == 'user' else '你上一轮的回复', t) for r, t in hist) if hist else '（这是开局第一轮，前面没有对话。）')
    w('玩家输入.md', msgs[-1][1])
    w('任务.md', '''这是一张文字冒险角色卡的回归测试，只做一件事：写出这张卡这一轮的回复。

1. 读「系统提示词.md」和「世界书_本轮.md」。这两份合起来是这张卡此刻的全部规则和设定，你就是照它运行的叙事模型。
2. 读「前面的对话.md」（前面几轮，有你上一轮写的回复）和「玩家输入.md」（玩家这一轮发来的话）。
3. 照系统提示词写出这一轮完整的回复，从第一行 §底座 写到最后一行，原样写进本文件夹的「回复.md」。

不要解释，不要评价这张卡，不要改别的文件，不要运行命令。回复.md 里只有这一轮的回复本身。
''')
    kinds = {}
    for _, _, c, _, f in woke:
        k = f.split('｜')[-1] if f else '别的'
        kinds[k] = kinds.get(k, 0) + han(c)
    tot = sum(han(c) for _, _, c, _, _ in woke)
    info = {'场景': scen['name'], '主提示词字数': han(sp), '醒了几条': len(woke), '世界书字数': tot,
            '各类': dict(sorted(kinds.items(), key=lambda x: -x[1])[:12]),
            '条目': [(c.strip().split('\n', 1)[0].lstrip('#= ').strip()[:40], han(c)) for _, _, c, _, _ in woke]}
    w('醒了哪些.json', json.dumps(info, ensure_ascii=False, indent=1))
    print('%s｜主提示词 %d 字｜醒了 %d 条 %.1f 万字｜%s' % (scen['name'], han(sp), len(woke), tot / 1e4, '，'.join('%s %.1f' % (k, v / 1e4) for k, v in list(info['各类'].items())[:7])))


if __name__ == '__main__':
    main()
