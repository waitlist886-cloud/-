# 风月四张外壳的提示词（11-25）。照四纪大框主提示词的源稿（底稿/状态栏/大框/主提示词/，prompt_src.py 读的那一套）出风月的切法：
#   风月的提示词分在前置提示（pre_pt）、前置词（ptx）、后置词（posttxt）和几条常驻世界书里。照 11-04 的切法：
#   01 角色声明那一大节进 pre_pt；02 统一运行驱动、03 骨架、04 单轮协议、05 正文输出档位、06 固定名词各一条常驻世界书
#   （钥匙是一条怎么都中的正则，范围玩家加回复，文件夹 00·核心运行，次序和深度照线上那张卡原来那五条）。
#   这一纪的常驻（日里那边靠底座上的纪元叫醒的那一条）也在这里：
#     月银纪、纷争纪、山铜纪、迷宫纪前传、迷宫纪此刻五张各只有一纪（一局），常驻直接做成怎么都中的一条；
#     （迷宫纪原来是一张，前传和 1001 年两局，两份常驻各认各的年份，钥匙 KEY_PRE、KEY_1001 留着，11-25 夜拆成两张以后不用了，自验照跑。）
#   单纪的卡里说别纪的那几句照这一张改（EDITS），一处对不上就停。日里的源稿这里不改。
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BIG = os.path.join(ROOT, '底稿', '状态栏', '大框')
if BIG not in sys.path:
    sys.path.insert(0, BIG)
sys.dont_write_bytecode = True
import prompt_src as PSRC        # noqa: E402
import prompt_stage2 as S2       # noqa: E402

GROUP = '00·核心运行'
ALWAYS = ['[\\s\\S]+', '[\\s\\S]{1,}', '[\\s\\S]{2,}', '[\\s\\S]{2,}', '[\\s\\S]{5,}']      # 线上那张卡五条常驻原来的钥匙，照旧
# 五条常驻：（源稿文件名的头两位，标题开头，次序，深度）
CONST = [('02', '# 统一运行驱动', 18, 1), ('03', '# 输出驱动·骨架（常驻·内部规格）', 24, 1), ('04', '# 单轮协议（承接·口径）', 48, 2),
         ('05', '# 正文输出档位（常驻·三档）', 49, 2), ('06', '# 固定名词（常驻·四纪通用）', 66, 2)]
ERA_NAME = {'moon': '月银纪', 'strife': '纷争纪', 'bronze': '山铜纪', 'pre': '迷宫纪前传', 'maze': '迷宫纪1001年'}
# 这一张卡没给凭证、上文也没有底座的局照哪里开（照日里那张卡输入框菜单里的开局口令）
DEFAULT_OPEN = {'moon': '月银纪1690年、万兽·焚原那一段', 'strife': '纷争纪元年、执式者那一段', 'bronze': '山铜纪2年、雨城清查那一段', 'pre': '迷宫纪2年、寻人那一段'}

# ---- 迷宫纪那一张：两份常驻各认各的年份。风月的钥匙是一条 RE2 正则，没有黑名单、不认前后顾 ----
# 前传：凭证头一行或者回复的底座上，纪元是迷宫纪 2 到 1000 年；前传的凭证也有只写“纪元：迷宫纪｜开局时段：”不带年份的
KEY_PRE = '纪元：迷宫纪(?:[2-9]|[1-9]\\d|[1-9]\\d\\d|1000)年|纪元：迷宫纪｜开局时段：'
# 1001 年：回复的底座（新记法带「纪元：」，旧 HTML 状态栏是 hud-meta"> 和 <br> 后头）或者凭证头一行，纪元是迷宫纪 1001 年以后；
# 再加老建档页的凭证（头一行没有「纪元：」，认「命途已确认」）。日里那边拿黑名单挡掉同一条消息里带着别的纪元的凭证，
# 这里写成“从头到「命途已确认」中间没出现过「纪元：」”：三个状态的自动机展开成的式子，RE2 认。
_NO_ERA = '(?:[^纪]|纪+(?:元纪+)*(?:[^纪元]|元[^纪：]))*(?:纪+(?:元纪+)*元?)?'
KEY_1001 = '(?:<br>|hud-meta">|纪元：|§底座｜)迷宫纪(?:100[1-9]|10[1-9]\\d|1[1-9]\\d\\d)年|^' + _NO_ERA + '命途已确认'
HEAD_PRE, HEAD_1001 = PSRC.HEAD_PRE, PSRC.HEAD_1001
HEADS = dict(S2.HEADS, **{'迷宫纪1001年': HEAD_1001})


def once(s, a, b, what=''):
    assert s.count(a) == 1, ('对不上', what, s.count(a), a[:60])
    return s.replace(a, b)


def edits(card_key):
    """主提示词里说别纪的那几句，照这一张卡改。返回 [(哪一节, 说明, 原句, 新句)]"""
    A = '下面每一行的样子照迷宫纪1001年写。别的纪里哪几行的栏写法不一样（日期、潮汐、地点、旅印和钱、职业、路、立绘、任务名、委托的档、日报），照那一纪的常驻，名目和栏序不变。'
    B = '凭证没写纪元、上文也没有底座的局，照迷宫纪1001年开）'
    C = '月银纪、纷争纪早年没有命路的局，几项里照那一纪的叫法写（法门、兵器加风格），栏不变。'
    D = '别处说的【名录与固定名词】指迷宫纪1001年常驻里的那一节，别的纪的局没有这张表。'
    E = '别的四纪的旅伴条、凡世至强条里写的专属羁绊只是章名'
    F = '玩家点一下就填进输入框，所以写成他会说的那句话'
    out = [('03', '分支点不了', F, '玩家照着说或者自己改，所以写成他会说的那句话')]
    if card_key == 'now':
        # 此刻那一张只有 1001 年那一局：骨架的例子本来就照它写，说别纪的半句拿掉；“没写纪元的局照 1001 年开”照旧
        out += [('03', '骨架开头', A, '下面每一行的样子照迷宫纪1001年写，这一张卡的局就在迷宫纪1001年以后。'),
                ('03', '没有命路的局', C, ''),
                ('06', '名录', D, '别处说的【名录与固定名词】指迷宫纪1001年常驻里的那一节。'),
                ('02', '羁绊章名', E, '这一纪的旅伴条、凡世至强条里写的专属羁绊只是章名')]
    elif card_key == 'maze':
        out += [('03', '骨架开头', A, '下面每一行的样子照迷宫纪1001年写。迷宫纪前传（迷宫纪2年到1000年）的局里哪几行的栏写法不一样（日期、潮汐、地点、旅印和钱、职业、路、立绘、任务名、委托的档、日报），照前传的常驻，名目和栏序不变。'),
                ('03', '没有命路的局', C, ''),
                ('06', '名录', D, '别处说的【名录与固定名词】指迷宫纪1001年常驻里的那一节，前传的局没有这张表。'),
                ('02', '羁绊章名', E, '前传的旅伴条、凡世至强条里写的专属羁绊只是章名')]
    else:
        n = ERA_NAME[card_key]
        out += [('03', '骨架开头', A, '下面每一行的样子是照迷宫纪1001年举的例。这一张卡的局在%s，哪几行的栏写法不一样（日期、潮汐、地点、旅印和钱、职业、路、立绘、任务名、委托的档、日报），照%s的常驻，名目和栏序不变。' % (n, n)),
                ('03', '没写纪元的局', B, '凭证没写纪元、上文也没有底座的局，照%s开）' % DEFAULT_OPEN[card_key]),
                ('03', '没有命路的局', C, {'moon': '这一纪没有命路，几项里照这一纪的叫法写（法门、兵器加风格），栏不变。',
                                         'strife': '纷争纪早年没有命路的局，几项里照这一纪的叫法写（法门、兵器加风格），栏不变。', 'bronze': '', 'pre': ''}[card_key]),
                ('06', '名录', D, '别处说的【名录与固定名词】是迷宫纪1001年那一局的表，这一张卡里没有。'),
                ('02', '羁绊章名', E, '这一纪的旅伴条、凡世至强条里写的专属羁绊只是章名')]
    return out


def resident_from_card(rili_card, era):
    head = HEADS[{'moon': '月银纪', 'strife': '纷争纪', 'bronze': '山铜纪', 'pre': '迷宫纪前传'}[era]]
    hit = [e for e in rili_card['prompt']['lorebook'] if (e.get('content') or '').startswith(head + '\n')]
    assert len(hit) == 1, (era, len(hit))
    return hit[0]['content']


CALL = {   # 单纪的卡：常驻头上【调用】那一行说“凭证里写着……就是这一局”的话换掉（这一张卡每一轮都用）。认不出原句就不动，记一笔
    'moon': (r'^【调用】局在月银纪的每一轮都用。[^\n]*?就是这一局。', '【调用】这一张卡只有月银纪，每一轮都用。'),
    'strife': (r'^【调用】局在纷争纪的每一轮都用。[^\n]*?就是这一局。', '【调用】这一张卡只有纷争纪，每一轮都用。'),
    'bronze': (r'^【调用】局在山铜纪的每一轮都用。[^\n]*$', '【调用】这一张卡只有山铜纪，每一轮都用。山铜纪从2年萌芽月起，元年那一个月是纷争纪的最后一个月，在纷争纪那一张卡里。'),
    'pre': (r'^【调用】局在迷宫纪前传的每一轮都用。[^\n]*$', '【调用】这一张卡只有迷宫纪前传，每一轮都用。前传从迷宫纪2年萌芽月起，元年那一个月是山铜纪的最后一个月，在山铜纪那一张卡里；'
            '前传写到1000年为止，§底座 的纪元到了迷宫纪1001年以后是底卡写的那一局，在迷宫纪1001年那一张卡里。'),
}


def entry(key, value, sort, depth):
    return {'group': GROUP, 'match_type': 3, 'key': key, 'key_region': 6, 'value_type': 0, 'value': value, 'value_configs': [],
            'value_region': 1, 'sort': sort, 'depth': depth, 'probability': 100, 'enable': True}


def build(card_key, eras, rili_card):
    """返回 {pre_pt, ptx, posttxt, wb: [常驻条目], heads: [各条的标题], acct}"""
    names = PSRC.parts()
    sec = {n[:2]: PSRC._read(n) for n in names}
    assert sorted(sec) == ['01', '02', '03', '04', '05', '06'], sorted(sec)
    assert ''.join(sec[k] for k in sorted(sec)) == PSRC.system()
    for k, head, _, _ in CONST:
        assert sec[k].startswith(head + '\n'), (k, sec[k][:30])
    acct = {'改': [], '提醒': []}
    for k, what, a, b in edits(card_key):
        sec[k] = once(sec[k], a, b, what)
        acct['改'].append(what)
    rear = PSRC.rear()
    if card_key in ('maze', 'now'):
        # 线上老档里还有带标签的旧回复，发给模型的历史里是原样的 HTML（风月改不了库里的旧回复）
        rear = once(rear, '面板、角色、见闻、记忆也一样。', '面板、角色、见闻、记忆也一样，历史里带标签的旧回复不要照抄。', '后置词')
    wb, heads = [], []
    for (k, head, sort, depth), key in zip(CONST, ALWAYS):
        wb.append(entry(key, sec[k].strip(), sort, depth))
        heads.append(head)
    if card_key == 'maze':
        pre = resident_from_card(rili_card, 'pre')
        r1001 = PSRC.resident_1001()
        r1001 = once(r1001, '月银纪、纷争纪、山铜纪、迷宫纪前传的局不用这一条。', '迷宫纪前传（迷宫纪2年到1000年）的局不用这一条。', '1001 常驻')
        wb.append(entry(KEY_PRE, pre.strip(), 67, 2))
        wb.append(entry(KEY_1001, r1001.strip(), 68, 4))      # 深度 4：哪一轮回复没写底座，往回再看一条回复，常驻不掉
        heads += [HEAD_PRE, HEAD_1001]
    elif card_key == 'now':
        r1001 = once(PSRC.resident_1001(), '月银纪、纷争纪、山铜纪、迷宫纪前传的局不用这一条。', '这一张卡只有这一局，每一轮都用。', '1001 常驻')
        wb.append(entry('[\\s\\S]{3,}', r1001.strip(), 67, 2))
        heads.append(HEAD_1001)
    else:
        res = resident_from_card(rili_card, card_key)
        rx, new = CALL[card_key]
        res2, n = re.subn(rx, new, res, count=1, flags=re.M)
        if n != 1:
            acct['提醒'].append('常驻头上【调用】那一行认不出原句，没改')
        wb.append(entry('[\\s\\S]{3,}', res2.strip(), 67, 2))
        heads.append(res.split('\n', 1)[0])
    pre_pt = sec['01'].strip()
    # 核一遍：记录行的格式串（反引号里以 § 起头的）一个不少；没有旧 HTML 状态栏的写法；单纪的卡里不再有“别的纪”“那一纪”
    allt = pre_pt + '\n' + '\n'.join(e['value'] for e in wb)
    lost = [f for f in PSRC.formats(PSRC.system()) if f not in allt]
    assert not lost, ('格式串少了', lost[:3])
    tags = re.compile(r'<div|<details|<span|class=|data-arc|arc-(?:hud|prose|panel|boss|npc|memory|daily|bag|deed)|hud-meta')
    for nm, t in [('pre_pt', pre_pt), ('posttxt', rear)] + [(h, e['value']) for h, e in zip(heads, wb)]:
        assert not tags.search(t), ('提示词里有旧写法', nm, tags.search(t).group(0))
    if card_key != 'maze':
        ok = ('不拿别的纪的东西来填', '落在更早的纪就写那一纪')      # 这两句单纪的卡里照样说得通
        for k in ('01', '02', '03', '04', '05', '06'):
            t = sec[k]
            for x in ok:
                t = t.replace(x, '')
            for w in ('别的纪', '那一纪', '别的四纪'):
                if w in t:
                    acct['提醒'].append('%s 节里还有「%s」' % (k, w))
    core = len(pre_pt) + len(rili_card['prompt']['headPrompt']) + len(rear) + sum(len(e['value']) for e in wb[:5])
    acct.update({'pre_pt': len(pre_pt), '常驻': [len(e['value']) for e in wb], '后置词': len(rear),
                 '每轮常驻合计': ({'前传的局': core + len(wb[5]['value']), '1001年的局': core + len(wb[6]['value'])} if card_key == 'maze' else core + len(wb[5]['value']))})
    return {'pre_pt': pre_pt, 'ptx': rili_card['prompt']['headPrompt'], 'posttxt': rear, 'wb': wb, 'heads': heads, 'acct': acct}


# ---- 钥匙自己验一遍（Python 的 re 跟 RE2 在这几条用到的写法上是一个意思；RE2 不认的前后顾、反向引用这里没有） ----
def selftest():
    import random
    pre, k1001 = re.compile(KEY_PRE), re.compile(KEY_1001)
    for k in (KEY_PRE, KEY_1001):
        assert not re.search(r'\(\?[=!<]|\\[1-9]', k), 'RE2 不认的写法'
    base = lambda y: '§底座｜纪元：迷宫纪%s年·春·萌芽月·上旬三日 · 09:20 上午 · 阿卡迪亚·公会总部 · 平潮 · 防抢话 开 · 档位 很长\n正文。' % y
    cred_new = '纪元：迷宫纪1001年｜开局时段：阿卡迪亚\n\n【角色建档】\n命途已确认。'
    cred_old = '【角色建档】\n姓名：阿尔\n命途已确认。\n自定义设定：纪元：无'
    cred_pre = '纪元：迷宫纪2年｜开局时段：寻人\n\n【角色建档】\n命途已确认。'
    cred_pre2 = '纪元：迷宫纪｜开局时段：空白委托｜年份：350\n命途已确认。'
    J = '\n'.join
    cases = [   # (说明, 扫到的字, 前传该不该醒, 1001 该不该醒)
        ('1001 新凭证', cred_new, False, True), ('1001 老凭证', cred_old, False, True),
        ('前传凭证', cred_pre, True, False), ('前传凭证不带年份', cred_pre2, True, False),
        ('前传第二轮', J([cred_pre, base(2), '我去号墙']), True, False), ('前传往后', J([base(999), '走', base(1000), '走']), True, False),
        ('1001 第二轮', J([cred_old, base(1001), '我去柜台']), False, True), ('1001 往后', J(['走', base(1019), '走', base(1104)]), False, True),
        ('旧 HTML 状态栏', '<span class="hud-meta">迷宫纪1001年·春</span>', False, True), ('前传走到 1001 年', J([base(1000), '过年', base(1001)]), True, True),
        ('别的话', '我往东走。纪元是什么？', False, False),
    ]
    bad = [(w, bool(pre.search(t)), bool(k1001.search(t))) for w, t, a, b in cases if bool(pre.search(t)) != a or bool(k1001.search(t)) != b]
    assert not bad, bad
    # “从头到「命途已确认」中间没出现过「纪元：」”那一段拿随机串对一遍
    rx = re.compile('^' + _NO_ERA + '命途已确认')
    rnd = random.Random(7)
    for _ in range(20000):
        s = ''.join(rnd.choice('纪元：纪元命途已确认甲\n') for _ in range(rnd.randint(0, 14))) + rnd.choice(['命途已确认', '', '纪元：命途已确认', '纪命途已确认', '纪元命途已确认'])
        i = s.find('命途已确认')
        want = i >= 0 and '纪元：' not in s[:i]
        assert bool(rx.search(s)) == want, (s, want)
    return len(cases)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    print('钥匙自验', selftest(), '种')
