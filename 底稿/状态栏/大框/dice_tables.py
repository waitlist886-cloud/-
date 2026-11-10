# 11-10 夜 骨骼补完（用户：骰表“做”，极端天气照 Elona 的以太风往里做）：
# 仓库根上 骰表/*.md 里「## 纪名·骰表｜表名」一节是一张加权条目，节里一行「- 项」是一项，平台每轮从里头抽一项给模型看。
# 一张表的项数要整除 100（十、二十、二十五项），各项概率一样。骰表不写【调用】、裁定锁和条目设置，触发在这里配：
#   路上·X      这一纪的底座在就醒（常亮，一轮两项，一项一百来字）
#   天气·暖季   同时满足这一纪的底座和萌芽月到蝉鸣月；天气·冷季 金穗月到归寂月（底座的日期里有月名）
#   差事·X      同时满足这一纪的底座和回复里写到酒馆、公会、板子、军需处这一类字
#   迷宫馈赠·X  同时满足迷宫纪的底座和面板的层级不是无（人在迷宫里）
#   迷宫纪那几张（路上、天气、差事、迷宫馈赠）前传和 1001 年以后各接一份，1001 年那一份的底座用 general_entries.ERA_1001
# 纪的底座正则从这一纪的路程那一条取（# X纪·规则｜路程 的头一个触发），所以要排在四纪条目都进了世界书以后。
# 怎么用写在主提示词「检定与命运骰」那一节（features_1110.DICE 末尾那一条）。
import glob
import os
import re

import general_entries as GE
import new_base as NB

DIR = os.path.join(NB.ROOT, '骰表')
HEAD = re.compile(r'^## (月银纪|纷争纪|山铜纪|迷宫纪)·骰表｜(.+)$')
WARM = '/萌芽月|花信月|清露月|长曦月|炎潮月|蝉鸣月/'
COLD = '/金穗月|坠叶月|霜降月|初雪月|寒星月|归寂月/'
JOBS = '/酒馆|公会|悬赏|委托板|号墙|军需|军册|差事|找活|接活|板上|集市/'
INSIDE = '/层级｜(?!无)/'
BAD = re.compile(r'[—；…！★]|\.\.\.')
PRIO = 8157
FOLDER = '60·%s｜骰表'


def load(dir_=DIR):
    """[(文件名, 纪, 表名, [项…])]"""
    out = []
    for f in sorted(glob.glob(os.path.join(dir_, '*.md'))):
        cur = None
        for raw in open(f, encoding='utf-8').read().replace('\r\n', '\n').split('\n'):
            m = HEAD.match(raw)
            if m:
                cur = (os.path.basename(f), m.group(1), m.group(2).strip(), [])
                out.append(cur)
            elif raw.startswith('#'):
                cur = None
            elif cur is not None and raw.startswith('- '):
                cur[3].append(raw[2:].strip())
    return out


def check(tables):
    """回 [问题…]，空的就是都对"""
    bad = []
    seen = set()
    for fn, era, name, items in tables:
        w = '%s %s·骰表｜%s' % (fn, era, name)
        if (era, name) in seen:
            bad.append('%s 重了' % w)
        seen.add((era, name))
        if len(items) not in (10, 20, 25):
            bad.append('%s 有 %d 项，要十、二十或者二十五项' % (w, len(items)))
        if not re.match(r'(路上|天气·(暖季|冷季)|差事|迷宫馈赠)', name):
            bad.append('%s 表名认不出（路上·X、天气·暖季、天气·冷季、差事·X、迷宫馈赠·X）' % w)
        if len(set(items)) != len(items):
            bad.append('%s 有一字不差的重项' % w)
        for k, it in enumerate(items, 1):
            if not it.startswith('【'):
                bad.append('%s 第 %d 项行首没有【表名】' % (w, k))
            if not 30 <= len(it) <= 180:
                bad.append('%s 第 %d 项 %d 字（三十到一百八）' % (w, k, len(it)))
            m = BAD.search(it)
            if m:
                bad.append('%s 第 %d 项有禁用的标点或记号 %s' % (w, k, m.group(0)))
    return bad


def _gate(lb, era):
    head = '# %s·规则｜路程' % era
    for e in lb:
        if (e.get('content') or '').startswith(head):
            g = e['triggerWords'][0]
            assert g.startswith('/') and e.get('triggerWordsType') == 'AND', (era, g[:40])
            return g
    raise AssertionError('找不到这一纪的路程条目，取不到底座正则：' + era)


def _entry(era, trig, items):
    p = 100 // len(items)
    return {'enabled': True, 'triggerWords': list(trig), 'triggerWordsType': 'AND' if len(trig) > 1 else 'OR',
            'blackListWords': [], 'blackListWordsType': 'OR', 'folder': FOLDER % era, 'priority': PRIO, 'probability': 100,
            'scanDepth': 2, 'triggerRange': ['user', 'assistant'], 'impactRange': ['system'], 'contentMethod': 'weighted',
            'contents': [{'content': it, 'probability': p} for it in items]}


def apply(card):
    """接在世界书末尾，回 (几张表, 几条条目)"""
    lb = card['prompt']['lorebook']
    tables = load()
    bad = check(tables)
    assert not bad, bad[:8]
    gates = {}
    new = []
    for fn, era, name, items in tables:
        if era not in gates:
            gates[era] = _gate(lb, era)
        # 迷宫纪那几张，前传一份，1001 年以后的局再接一份（牌上写着哪一段年月，对不上的模型不用，主提示词里说了）
        for g in [gates[era]] + ([GE.ERA_1001] if era == '迷宫纪' else []):
            if name.startswith('路上'):
                new.append(_entry(era, [g], items))
            elif name.startswith('天气·暖季'):
                new.append(_entry(era, [g, WARM], items))
            elif name.startswith('天气·冷季'):
                new.append(_entry(era, [g, COLD], items))
            elif name.startswith('差事'):
                new.append(_entry(era, [g, JOBS], items))
            else:
                new.append(_entry(era, [g, INSIDE], items))
    for e in new:
        for w in e['triggerWords']:
            re.compile(w[1:-1])
    lb.extend(new)
    return len(tables), len(new)
