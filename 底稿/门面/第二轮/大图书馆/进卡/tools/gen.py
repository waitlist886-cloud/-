#!/usr/bin/env python3
# 大图书馆进卡（11-24）：照 books.py 出 清点.md、清点.json、书目条目.md，只用标准库。
#   python -I -X utf8 底稿/门面/第二轮/大图书馆/进卡/tools/gen.py
# 书目条目.md 是能进卡的源稿格式（通用条目那一套，「## 奥尔德兰·」起的节，节末一行「> 条目设置」，
# 读法见 底稿/状态栏/大框/general_entries.py 借的 new_base.py）。apply.py 把它放进 通用条目/。
# 门控：一条一个触发正则，书一本一组「这一局底座上的纪元年份不早于成书那一年」加「书名」，同一条消息里两样都在才醒
#   （日里一条消息一条消息分开算，跟 general_entries.apply_1001_new、各纪页「触发（同时满足）」是同一个道理）。
#   写成 /^(?:(?=[\s\S]*门控甲)[\s\S]*(?:书名…)|(?=[\s\S]*门控乙)[\s\S]*(?:书名…))/，一个正则，OR 型触发也读得对，new_base 不用改。
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(OUT, '..', '..', '..', '..', '..'))
sys.path.insert(0, HERE)
import books as BK  # noqa: E402

ERA = {'M': '月银纪', 'S': '纷争纪', 'B': '山铜纪', 'L': '迷宫纪'}
LATER = {'M': ['纷争纪', '山铜纪', '迷宫纪'], 'S': ['山铜纪', '迷宫纪'], 'B': ['迷宫纪'], 'L': []}
PRE = '(?:<br>|hud-meta">|纪元：)'
HALL_OF = {'圆厅': '圆厅', '命路厅': '命路厅', '奥法与工程厅': '奥法与工程厅', '孩子的一架': '孩子的一架',
           '山铜纪廊': '山铜纪廊', '戏台与说书': '戏台与说书', '星冠圣堂厅': '星冠圣堂厅', '月银纪廊': '月银纪廊',
           '神与魔神厅': '神与魔神厅', '纷争纪廊': '纷争纪廊', '行当的歌': '行当的歌', '迷宫纪廊': '迷宫纪廊'}


def ge(n, maxd=5):
    """不小于 n 的正整数（至多 maxd 位，不带前导零）的正则"""
    s = str(n)
    d = len(s)
    rep = lambda k: '' if k == 0 else ('\\d' if k == 1 else '\\d{%d}' % k)
    parts = [s]                       # 正好是它
    for i in range(d):                # 前 i 位一样，第 i 位大一些，往后随便
        digit = int(s[i])
        if digit < 9:
            nxt = digit + 1
            cls = '9' if nxt == 9 else '[%d-9]' % nxt
            parts.append(s[:i] + cls + rep(d - i - 1))
    for k in range(d + 1, maxd + 1):  # 位数更多的
        parts.append('[1-9]' + rep(k - 1))
    rx = '(?:%s)' % '|'.join(parts)
    # 自测
    c = re.compile('^%s$' % rx)
    for t in (n - 1, n, n + 1, n * 10, 99999):
        if 0 < t < 10 ** maxd:
            assert bool(c.match(str(t))) == (t >= n), (n, t, rx)
    return rx


def gate(era, year):
    if era == 'S' and year <= 1:
        own = '纷争纪'
    elif era == 'B' and year <= 1:
        own = '山铜纪'
    else:
        own = ERA[era] + ge(year) + '年'
    alts = [own] + LATER[era]
    return PRE + ('(?:%s)' % '|'.join(alts) if len(alts) > 1 else alts[0])


def title_rx(t, strict):
    e = re.escape(t)
    if strict:
        return '《%s》|%s(?:这|那)一?(?:本|部|册)' % (e, e)
    return e


def era_text(era, year):
    return '%s%s年' % (ERA[era], year)


def rows():
    out = []
    for r in BK.B:
        stem, title, g, era, year, au, when, summ, ai, alias, strict, pend = r
        out.append(dict(stem=stem, title=title, group=g, era=era, year=year, author=au, when=when,
                        summary=summ, ai=ai, alias=alias, strict=strict, pending=pend,
                        hall=stem.split('_')[0]))
    return out


def zhuzuo_map():
    """读 著作行.md：书名 -> [文件｜条目]"""
    p = os.path.join(OUT, '著作行.md')
    m = {}
    cur = {}
    for l in open(p, encoding='utf-8').read().split('\n'):
        if l.startswith('### '):
            cur = {'who': l[4:].strip()}
        for k in ('文件', '条目', '书'):
            if l.startswith('- %s｜' % k):
                cur[k] = l.split('｜', 1)[1].strip()
        if '书' in cur and '条目' in cur and '文件' in cur and not cur.get('_done'):
            cur['_done'] = 1
            for b in BK.B:
                if b[1] in cur['书'] or b[1].replace('·', '') in cur['书']:
                    m.setdefault(b[1], []).append('%s｜%s（%s）' % (cur['文件'], cur['条目'][3:], cur['who'].split(' ', 1)[1]))
    return m


def bullet(r):
    t = r['title']
    shown = '《%s》' % t
    if r['stem'].startswith('命路厅_战斗的艺术'):
        shown = '《战斗的艺术》971修订版'
    if r['stem'].startswith('奥法与工程厅_机巧与魔导'):
        shown = '《机巧与魔导·两陆工业小史》'
    line = '- %s｜%s，%s。%s' % (shown, r['when'], r['author'], r['summary'])
    out = [line]
    if r['ai']:
        out.append('  - 只给 AI｜%s' % r['ai'])
    if r['pending']:
        out.append('> 待全本写完再改：《%s》这一条照目录本写的，全本写完照全本改摘要。apply.py 进卡时把这一行拿掉。' % t)
    return out


def trigger(rs):
    pairs = {}
    for r in rs:
        pairs.setdefault(gate(r['era'], r['year']), []).append(title_rx(r['title'], r['strict']))
        for a in r['alias']:
            an, ae, ay = a
            pairs.setdefault(gate(ae, ay), []).append(title_rx(an, r['strict']))
    alts = []
    for g, ts in pairs.items():
        alts.append('(?=[\\s\\S]*%s)[\\s\\S]*(?:%s)' % (g, '|'.join(ts)))
    rx = '/^(?:%s)/' % '|'.join(alts)
    re.compile(rx[1:-1])
    return rx


def main():
    rs = rows()
    zm = zhuzuo_map()
    # ---------- 清点.json ----------
    data = []
    for r in rs:
        data.append({'书名': r['title'], '文件': '书稿/%s.md' % r['stem'], '厅': r['hall'], '作者': r['author'],
                     '成书': r['when'], '纪': ERA[r['era']], '门控年': r['year'], '门控': '%s起' % era_text(r['era'], r['year']),
                     '一句话': r['summary'].split('。')[0] + '。', '只给AI': r['ai'], '待全本': bool(r['pending']),
                     '进卡条目': [g[1] for g in BK.GROUPS if g[0] == r['group']][0],
                     '作者在卡里的条目': zm.get(r['title'], [])})
    json.dump(data, open(os.path.join(OUT, '清点.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # ---------- 清点.md ----------
    L = ['# 大图书馆进卡｜清点（11-24，gen.py 出的，改 tools/books.py 再重跑）', '',
         '> 书稿在 `../书稿/`，一百九十六个文件，971 上中下合一本、`廊_往前往后` 不是书，共一百九十三本。成书照各本扉页前那几行「成书｜」写，门控是这本书在世上有了的那一年（初版、合订、起记的日志照起记那一年），书目条目照它挡早的局。',
         '> 作者在卡里的条目照 `著作行.md`（拟了著作行的那几处）。没列的作者卡里没有自己的条目，或者有条目但年份对不上，原因在 著作行.md 第四节。', '']
    n_auth = sum(1 for d in data if d['作者在卡里的条目'])
    L.append('一共 %d 本，%d 本的作者在卡里有条目、拟了著作行，%d 本待全本。' % (len(data), n_auth, sum(d['待全本'] for d in data)))
    L.append('')
    cur = None
    for d, r in zip(data, rs):
        if d['厅'] != cur:
            cur = d['厅']
            L += ['', '## %s' % cur, '', '| 书名 | 作者 | 成书 | 门控 | 一句话 | 作者在卡里的条目 |', '|---|---|---|---|---|---|']
        ents = '<br>'.join(d['作者在卡里的条目']) or '无'
        L.append('| 《%s》%s | %s | %s | %s | %s | %s |' % (d['书名'], '（待全本）' if d['待全本'] else '', d['作者'], d['成书'], d['门控'],
                                                    d['一句话'], ents))
    open(os.path.join(OUT, '清点.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    # ---------- 书目条目.md ----------
    E = ['# 通用条目｜大图书馆的书（11-24 草稿，tools/gen.py 照 tools/books.py 出）', '',
         '> 这一节是说明，不进卡。介绍页大图书馆一百九十三本书进卡的那一层，一间厅、或一间厅一段年月一条，三十一条。打包只读「## 奥尔德兰·」起的节，节末一行「> 条目设置」，读法在 底稿/状态栏/大框/general_entries.py。',
         '> 门控：触发是一个正则，一本书一组，要同一条消息里既有书名、又有不早于成书那一年的底座纪元（`纪元：X纪N年`、旧样子的 `<br>X纪N年`），所以只在那一年以后的局里醒，跑卡的模型在回复里写到书名的那一轮带着底座醒。玩家刚问的那一轮慢一轮，跟四纪大框别的「同时满足」一样。书名寻常、或撞了卡里主线、技艺、纪元名字的，只认《X》和“X这本、那部”。',
         '> 一条里各本成书年份不一样，条里每本都写了成书那一年，【调用】叫模型照这一局的年份看，没写成的不提。',
         '> 「> 待全本写完再改」那几行是给人看的标记，apply.py 放进 通用条目/ 时拿掉。', '']
    for g, name, folder in BK.GROUPS:
        rs_g = [r for r in rs if r['group'] == g]
        hall = rs_g[0]['hall']
        E.append('## 奥尔德兰·大图书馆｜%s' % name)
        E.append('')
        tail = ''
        if any(r['stem'] in ('圆厅_万物的清点', '圆厅_向长夜索春', '神与魔神厅_七十二域') for r in rs_g):
            tail = '注明只在馆里的那几本，局里的人没读过。'
        E.append('【调用】回复里写到下面哪一本书的书名，或者有人问书里写了什么、是谁写的、哪一年写的时候用。四纪通用。每本写着成书那一年，这一局的年份早于它的，那本书世上还没有，不提不引，还在写的只写到这一局的年份为止。%s' % tail)
        E.append('')
        for r in rs_g:
            E += bullet(r)
        E.append('')
        E.append('> 条目设置：文件夹 %s，触发 `%s`，黑名单 无，范围 用户与AI，深度 2。' % (folder, trigger(rs_g)))
        E.append('')
    E += ['## 设计备注', '',
          '- 不进卡。条目标题、文件夹、门控、哪几本拿不准，见 清点.md 和交回去的那一段话。',
          '- 只给 AI 那几句照书稿里〔剧透〕和青墨注写，书稿的剧透开关后面那一层。照卡里的锁不写的（七神圣歌那六句是谁接上的这一类），只放在只给 AI 里。',
          '- 《以太导论》《天象历》《奥尔德兰大陆地理》《高等元素论》《魔晶学》《热与蒸汽》六本11-24补成了全本，摘要照全本重写。', '']
    open(os.path.join(OUT, '书目条目.md'), 'w', encoding='utf-8').write('\n'.join(E))
    print('书 %d 本，条目 %d 条，作者在卡里有条目的书 %d 本' % (len(rs), len(BK.GROUPS), n_auth))
    lens = []
    for g, name, folder in BK.GROUPS:
        rs_g = [r for r in rs if r['group'] == g]
        lens.append((name, len(rs_g), len(trigger(rs_g))))
    for x in lens:
        print('  %s｜%d 本｜触发 %d 字' % x)


if __name__ == '__main__':
    main()
