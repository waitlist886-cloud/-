# 11-23 主提示词重写第一段（方向稿 根目录 主提示词重写_方向稿.md 第四节，用户回“都照倾向”）：
# 主提示词里只属于迷宫纪 1001 年的三块（世界硬锚里的 1001 年那几句、手边的东西、名录）搬进新开的一条
# 「迷宫纪·常驻｜这一局在迷宫纪1001年」，主提示词留四纪通用的。搬的字从主提示词里切，一个字不改；新写的只有 NEW_* 那几句。
# make_four_era_card.py 最后一步套（主提示词前头还要过 features_1110、fix_1112，所以放最后）。只进四纪大框，1001 年切片和风月不跟。
import copy
import re

HEAD_1001 = '# 迷宫纪·常驻｜这一局在迷宫纪1001年'
HEAD_PRE = '# 迷宫纪·常驻｜这一局在迷宫纪前传'
# 回复的底座（新写法带「纪元：」；旧 HTML 状态栏和不带「纪元：」的底座也认），1001 年以后
ERA_1001 = '/(?:<br>|hud-meta">|纪元：|§底座｜)迷宫纪(?:100[1-9]|10[1-9]\\d|1[1-9]\\d\\d)年/'
# 1001 年的建档凭证头一行没有「纪元：」（别的四纪都有），认「命途已确认」，同一条消息里带别纪纪元的挡掉
CRED = '命途已确认'
BLACK = ['纪元：月银纪', '纪元：纷争纪', '纪元：山铜纪', '/纪元：迷宫纪(?:元|[2-9]|[1-9]\\d|[1-9]\\d\\d|1000)年|纪元：迷宫纪｜开局时段：/']

NEW_ANCHOR = '这是奥尔德兰。哪一纪、哪一年照 §底座 的纪元那一段，这一纪有哪些国、哪些神、用什么钱、技术到了哪一步，照这一纪的常驻，不拿别的纪的东西来填。'
NEW_HAND = '手边的东西照这一纪、这个地方写，不混，一场戏挑一两样这样的小东西写实；这一纪的人手边有什么，照这一纪的常驻。'
NEW_NAMES_HEAD = '# 固定名词（常驻·四纪通用）'
NEW_MONTHS = ('十二月名（顺序固定）：萌芽月／花信月／清露月／长曦月／炎潮月／蝉鸣月／金穗月／坠叶月／霜降月／初雪月／寒星月／归寂月。'
              '四季：萌芽—清露为春，长曦—蝉鸣为夏，金穗—霜降为秋，初雪—归寂为冬。月名后头的风俗各纪不一样，照这一纪的常驻。')
NEW_NAMES_TAIL = ('任务名、人名、地名照这一纪的常驻和醒着的条目写，不自造。这一纪的主线名、有立绘的人是哪些，都在这一纪的常驻里；'
                  '别处说的【名录与固定名词】指迷宫纪1001年常驻里的那一节，别的纪的局没有这张表。')
NEW_RES_INTRO = ('这一局在迷宫纪1001年以后。下面是这一局每轮都要用的世界硬锚、手边的东西和名录，'
                 '主提示词和别的条目说的【名录与固定名词】就是末一节。月银纪、纷争纪、山铜纪、迷宫纪前传的局不用这一条。')


def _cut(s, a, what):
    assert s.count(a) == 1, ('第一段对不上', what, s.count(a), a[:50])
    i = s.index(a)
    return s[:i], s[i + len(a):]


def split(sp):
    """返回 (新主提示词, 1001 常驻正文, 账)。sp 是打卡各步都套完的主提示词。"""
    # 一、世界硬锚：一行，三截。头一截（1001 年的国和神）、末一截（技术和三币）搬走，中间那一截（位阶和魔法）留下
    pre, rest = _cut(sp, '## 世界硬锚\n', '硬锚标题')
    line, rest = rest.split('\n', 1)
    assert line.startswith('迷宫纪1001年。东方：') and line.endswith('山铜便士。'), line[:40]
    a1, mid = _cut(line, 'LVL1—300与启源', '硬锚中段')
    mid = 'LVL1—300与启源' + mid
    mid, a3 = _cut(mid, '科技为魔导工业', '硬锚末段')
    a3 = '科技为魔导工业' + a3
    assert mid.endswith('过载必结算代价。'), mid[-20:]
    sp = pre + '## 世界硬锚\n' + NEW_ANCHOR + mid + '\n' + rest
    anchor_1001 = a1 + a3

    # 二、手边的东西：骨架末尾那一行整行搬
    m = re.findall(r'^手边的东西照地方写，不混：[^\n]*$', sp, re.M)
    assert len(m) == 1, len(m)
    hand = m[0]
    assert '联邦这一边' in hand and '黑耀那一边' in hand and hand.endswith('细目见【日用器物】。'), hand[-30:]
    sp = sp.replace(hand, NEW_HAND)

    # 三、名录：整节在主提示词末尾。四纪通用的三行（纪元长度、能级、Unique 独占律）留下，月名另写一行不带风俗的，别的整节搬
    main, names = _cut(sp, '# 名录与固定名词（常驻·只给名字与名词，细节仍看各自条目）\n', '名录标题')
    assert '\n# ' not in names, '名录后头还有别的大节'
    lines = names.rstrip('\n').split('\n')
    keep, move = {}, []
    for ln in lines:
        if ln.startswith('纪元长度（正史口径）：'):
            keep['len'] = ln
        elif ln.startswith('能级：'):
            keep['tier'] = ln
        elif ln.startswith('Unique 独占律：'):
            keep['uniq'] = ln
        else:
            move.append(ln)
    assert set(keep) == {'len', 'tier', 'uniq'}, keep.keys()
    tail_len = '迷宫纪1001年至今。当前＝迷宫纪1001年。'
    assert keep['len'].endswith(tail_len), keep['len'][-40:]
    month_old = [ln for ln in move if ln.startswith('十二月名（顺序固定）：')]
    assert len(month_old) == 1
    for mn in re.findall(r'[^／：。]+月(?=／|。)', NEW_MONTHS.split('。')[0] + '。'):
        assert mn + '·' in month_old[0], mn
    assert '四季：萌芽—清露为春，长曦—蝉鸣为夏，金穗—霜降为秋，初雪—归寂为冬。' in month_old[0]
    new_names = '\n'.join([NEW_NAMES_HEAD, NEW_MONTHS, keep['len'][:-len(tail_len)] + '迷宫纪至今。', keep['tier'], keep['uniq'], NEW_NAMES_TAIL])
    sp = main + new_names + '\n'
    moved_names = '\n'.join(move).strip('\n')
    for must in ('写任务名只能从这张表里取', '## 六大地区主线', '## 主城三幕', '## 旅伴羁绊', '## 世界主线与终局', '十兆名（当前为兆一）',
                 '旅印七阶（低→高）', '## 预设短名', '旅伴专武（名器'):
        assert moved_names.count(must) == 1, must

    res = '\n'.join([
        HEAD_1001, NEW_RES_INTRO, '',
        '## 世界硬锚', anchor_1001, '',
        '## 手边的东西', hand, '',
        '# 名录与固定名词（迷宫纪1001年·只给名字与名词，细节仍看各自条目）', moved_names, ''])
    acct = {'硬锚搬': len(anchor_1001), '手边搬': len(hand), '名录搬': len(moved_names),
            '新写': len(NEW_ANCHOR) + len(NEW_HAND) + len(NEW_NAMES_HEAD) + len(NEW_MONTHS) + len(NEW_NAMES_TAIL) + len(NEW_RES_INTRO)}
    return sp, res, acct


def apply(card):
    pr = card['prompt']
    lb = pr['lorebook']
    old = pr['systemPrompt']
    sp, res, acct = split(old)
    # 搬走的字都在常驻里，留下的字都还在主提示词里：两边合起来不少字（月名那一行的风俗跟着原行进了常驻）
    pre = [e for e in lb if (e.get('content') or '').startswith(HEAD_PRE)]
    assert len(pre) == 1, len(pre)
    assert not [e for e in lb if (e.get('content') or '').startswith(HEAD_1001)], '1001 常驻已经有了'
    e = copy.deepcopy(pre[0])
    e['content'] = res
    e['triggerWords'] = [ERA_1001, CRED]
    e['triggerWordsType'] = 'OR'
    e['blackListWords'] = list(BLACK)
    e['blackListWordsType'] = 'OR'
    e['triggerRange'] = ['user', 'assistant']
    e['impactRange'] = ['system']
    e['scanDepth'] = 4          # 哪一轮回复没写底座，往回再看一条回复，常驻不掉
    e['priority'] = pre[0]['priority'] + 1
    assert not [x for x in lb if x.get('priority') == e['priority'] and x.get('folder') == e.get('folder')], '优先级撞了'
    for w in e['triggerWords'] + e['blackListWords']:
        if w.startswith('/'):
            re.compile(w[1:w.rfind('/')])
    lb.append(e)
    pr['systemPrompt'] = sp
    acct.update({'主提示词': (len(old), len(sp)), '常驻': len(res)})
    return acct


def _rx(w):
    if len(w) > 2 and w.startswith('/') and w.rfind('/') > 0:
        return re.compile(w[1:w.rfind('/')])
    return re.compile(re.escape(w))


def wakes(e, msgs):
    """msgs 是最近几条消息（新的在前），照平台一条一条分开判"""
    for m in msgs[:e['scanDepth']]:
        if any(_rx(w).search(m) for w in e['triggerWords']) and not any(_rx(b).search(m) for b in e['blackListWords']):
            return True
    return False


def check(card, cases):
    """cases 是 slim_card.cases(ROOT)：四本书每条主线的凭证和回复、自己报年份的凭证、1001 年的凭证。
    1001 常驻只在 1001 年的局里醒：凭证那一轮、往后每一轮、漏了一轮底座的那一轮；别的四纪一条也不醒。"""
    lb = card['prompt']['lorebook']
    e = [x for x in lb if (x.get('content') or '').startswith(HEAD_1001)]
    assert len(e) == 1
    e = e[0]
    bad, n = [], 0
    reply_1001 = '§底座｜纪元：迷宫纪1001年·春·萌芽月·上旬3日 · 09:20 上午 · 阿卡迪亚·公会总部 · 第一兆·魔兽离巢·平潮 · 防抢话 开 · 难度 普通 · 节奏 均衡 · 调子 史诗 · 档位 很长\n正文。'
    reply_bare = '正文写坏了，没有底座。'
    for era, name, old, new, reply in cases:
        n += 1
        if era == '迷宫纪1001':
            cred = old
            for what, msgs in (('凭证那一轮', [cred]), ('第二轮', ['我去柜台', reply_1001, cred]), ('往后', ['我往东走', reply_1001, '我去柜台', reply_1001]),
                               ('漏了一轮底座', ['我往东走', reply_bare, '我去柜台', reply_1001]),
                               ('一千一百年', ['走', reply_1001.replace('1001年', '1104年')])):
                if not wakes(e, msgs):
                    bad.append(('该醒没醒', what))
            if wakes(e, ['我往东走', reply_bare, '我去柜台', reply_bare, '嗯', reply_1001]):
                bad.append(('连漏两轮还醒着，深度不对', ''))
            continue
        for what, cred in (('旧凭证', old), ('新凭证', new)):
            if cred and wakes(e, [cred]):
                bad.append(('别纪的凭证叫醒了', era + name + what))
        if reply and wakes(e, ['我往东走', reply, '开始', new or old]):
            bad.append(('别纪的回复叫醒了', era + name))
    # 别的四份常驻在 1001 年的局里照旧不醒，四纪的局里照旧醒（这一步没动它们，核一遍防手滑）
    return n, bad
