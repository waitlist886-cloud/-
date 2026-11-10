# 11-10 基本算式（用户回“甲，其余也都按倾向来”）：
# 1. 通用条目/*.md 里「## 奥尔德兰·X｜Y」起的节，四纪和 1001 年都用，不挡纪元，接在世界书末尾（apply_general）。
# 2. 底卡新条目/*.md（1001 年的路程、产业）进四纪大框：触发改成同时满足 1001 年以后的底座和原来的字眼，别纪的局里不醒（apply_1001_new）。
#    日里一条消息一条消息分开算，回复里写着底座，所以这两样要在同一条回复里同时出现，玩家刚问的这一轮慢一轮。
# 读法借 new_base.py（节末一行「> 条目设置」，或者紧跟标题底下那一行）。
import re

import new_base as NB

GEN_HEAD = re.compile(r'^## 奥尔德兰·(.+)$')
GEN_DIR = NB.os.path.join(NB.ROOT, '通用条目')
ERA_1001 = '/(?:<br>|hud-meta">|纪元：)迷宫纪(?:100[1-9]|10[1-9]\\d|1[1-9]\\d\\d)年/'


def _with_head(head, fn, *a):
    old = NB.HEAD
    NB.HEAD = head
    try:
        return fn(*a)
    finally:
        NB.HEAD = old


def apply_general(card, n_base=1397):
    lb = card['prompt']['lorebook']
    new = _with_head(GEN_HEAD, NB.entries, lb[:n_base], GEN_DIR)
    lb.extend(new)
    return len(new)


def _one_regex(words):
    parts = []
    for w in words:
        if len(w) > 2 and w.startswith('/') and w.endswith('/'):
            parts.append(w[1:-1])
        else:
            parts.append(re.escape(w))
    rx = '/(?:%s)/' % '|'.join(parts)
    re.compile(rx[1:-1])
    return rx


def apply_1001_new(card, n_base=1397):
    lb = card['prompt']['lorebook']
    new = NB.entries(lb[:n_base])
    for e in new:
        e['triggerWords'] = [ERA_1001, _one_regex(e['triggerWords'])]
        e['triggerWordsType'] = 'AND'
        e['triggerRange'] = ['user', 'assistant']
        e['scanDepth'] = max(2, e['scanDepth'])
    lb.extend(new)
    return len(new)
