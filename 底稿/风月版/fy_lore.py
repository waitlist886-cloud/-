#!/usr/bin/env python3
# 风月版：按纪切世界书，门控转成风月的钥匙（fy_gate.py）。
# 用法（仓库根上）：
#   python -I -X utf8 底稿/风月版/fy_lore.py <纪…> [--src 全本.json] [--base core|std|all]
#     纪：pre（迷宫纪前传）、now（迷宫纪此刻：底卡 1001 年那一局）、moon、strife、bronze，也认 前传、此刻、目录名；不写就是五张都做
#     --src   日里全本，默认 out/发布卡_四纪大框/奥尔德兰_四纪大框_原介绍页_全本.json
#     --base  月银纪、纷争纪、山铜纪、迷宫纪前传四张带底卡的哪些文件夹（此刻那一张底卡全带）：
#             core（默认）规则核：00 01 05 06 07 08 09 10 18 19 20 21 90 91 92
#             std  再加 02 公开历史、03 隐藏真相、04 神祇
#             all  文件夹不挑，这一纪的局里醒得了的都带
# 出：out/发布卡_风月_四纪/<纪名>/世界书_转换.json（风月世界书的条目，多带 _src、_title、_part 三栏，打包时去掉）、
#     转换报告.json、转换清单.md。条数过 5000 就停（--force 照出，给人看数）。
# 怎么切：
#   · 文件夹带这一纪名字的全带；带别纪名字、可这一纪的局里也醒得了的（活过纪元交界的人和传奇）也带。
#   · 不带纪名的（底卡、通用规则、1001 年新添的）：此刻那一张底卡全带，别的照门控，这张卡的锚全叫黑名单挡了、或者只认别纪年份的不带；
#     另外四张底卡只带 --base 那几个文件夹里醒得了的。
#   · 迷宫纪两张（11-25 拆的）文件夹都带“迷宫纪”，“这一纪”的条目照日里的判法分：这一张的年份里醒不了的（年份窗空了），
#     或者照日里的判法在这一张的局里醒不了、在另一张的局里醒得了的（fy_msgs.Msgs.can_wake，逐年一年不落；前传的主线、旅伴只认前传的潮汐和开局时段，
#     1001 年的局里永远碰不上），是另一张的，不带、也不记进“没进卡”，数记在 sibling。两张都醒不了的两张都带（跟拆以前一样）。
#   · 醒不醒得了照门控转换的结果判（年份窗空了就是醒不了），跟日里“带锚的凭证和回复”那一头的判法是一回事，fy_sim.py 会拿消息再对一遍。
import collections
import datetime
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fy_gate as G     # noqa: E402
import fy_msgs as M     # noqa: E402

ROOT = G.ROOT
SRC = os.path.join(ROOT, 'out', '发布卡_四纪大框', '奥尔德兰_四纪大框_原介绍页_全本.json')
OUT = os.path.join(ROOT, 'out', '发布卡_风月_四纪')
BASE_SETS = dict(core={0, 1, 5, 6, 7, 8, 9, 10, 18, 19, 20, 21, 90, 91, 92})
BASE_SETS['std'] = BASE_SETS['core'] | {2, 3, 4}
LIMIT_N, LIMIT_VALUE = 5000, 40000
RG = {'system': 1, 'user': 2, 'assistant': 4}
RV = {'system': 1, 'headPrompt': 2, 'rearPrompt': 4}
# 风月保存时扫屏蔽词，命中自动下架（make_fy_card.py 的 BAN_RE，11-04 客服报的）。正文里碰上的照 make_fy_card.FY_TEXT 的办法换一个字，
# 只换风月这一份，一处一条写死在这里；表里没有的新碰上了就停。
BAN_RE = re.compile('rili|扣扣|日历|风月|fengyue', re.I)
BAN_FIX = [('山铜扣扣起来', '山铜扣系起来'), ('腰扣扣鞍磨得发亮', '腰扣挂鞍磨得发亮'), ('链扣扣好没有', '链扣系好没有'), ('窗扣扣没扣上', '窗扣搭没搭上'),
           ('链扣扣在哪一格', '链扣搭在哪一格'), ('钉钉、扣扣、量断处', '钉钉、搭扣、量断处'), ('把链扣扣到外一格', '把链扣搭到外一格')]


def folder_no(e):
    m = re.match(r'(\d+)·', e.get('folder') or '')
    return int(m.group(1)) if m else -1


def era_of(e):
    f = e.get('folder') or ''
    return next((x for x in G.ERAS if x in f), None) if folder_no(e) >= 40 else None


def base_count():
    return len(json.load(open(os.path.join(ROOT, 'src', 'rili_v7.json'), encoding='utf-8'))['prompt']['lorebook'])


def ban_fix(s, log):
    if not BAN_RE.search(s):
        return s
    for a, b in BAN_FIX:
        if a in s:
            log.append((a, b, s.count(a)))
            s = s.replace(a, b)
    return s


def known_opens(lb, msgs):
    """凭证“开局时段：”后头会写的东西：四本书每条主线的写法，加全卷触发词、黑名单里认过的。"""
    out = set(msgs.opens())
    for e in lb:
        for w in (e.get('triggerWords') or []) + (e.get('blackListWords') or []):
            if '开局时段：' not in w:
                continue
            for is_re, a in G.Ctx.alts_of(w):
                if a.startswith('开局时段：') and a != '开局时段：' and '｜年份：' not in a:
                    try:
                        out.update(x[len('开局时段：'):] for x in G.expand_literals(a if is_re else G.esc(a)))
                    except G.Unsupported:
                        pass
    return sorted(x for x in out if x)


def jbytes(o):
    return len(json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))


def build(card, lb, nb, mode):
    ctx = G.Ctx(card)
    era = ctx.era
    msgs = M.Msgs(card)
    ctx.known_tides = msgs.tides()
    ctx.known_opens = known_opens(lb, msgs)
    ctx.known_creds = msgs.creds()
    out, rep = [], dict(card=card, era=era, base=mode, picked=collections.Counter(), kinds=collections.Counter(), skipped=[], flags=[], left=[], ban=[],
                        split=0, weighted=0, sibling=0)
    twin = next((k for k, c in G.CARDS.items() if c['name'] == era and k != card), None)        # 迷宫纪前传、此刻两张共用一个纪名
    tmsgs = M.Msgs(twin) if twin else None
    for i, e in enumerate(lb):
        fera = era_of(e)
        fno = folder_no(e)
        if fera == era:
            cls = '这一纪'
        elif fera is not None:
            cls = '别纪文件夹、这一纪也醒'
        elif i < nb:
            cls = '底卡'
        else:
            cls = '底卡后头不带纪名的（通用规则、1001 年新添）'
        outs, info = ctx.convert(e, foreign=fera is not None and fera != era)
        title = M.title_of(e)
        dead = info['skip'] and info['skip'].startswith('这张卡里醒不了')
        if cls != '这一纪' and dead:
            continue
        if cls == '这一纪' and twin and (dead or (not info['skip'] and not msgs.can_wake(e) and tmsgs.can_wake(e))):
            rep['sibling'] += 1         # 另一张（前传／此刻）的
            continue
        if cls == '底卡' and not G.CARDS[card].get('fullbase') and mode != 'all' and fno not in BASE_SETS[mode]:
            if outs:
                rep['left'].append(dict(i=i, folder=e['folder'], title=title))
            continue
        if cls.startswith('别纪') and not outs:
            continue        # 别纪的条目转不了的不硬带（加权骰表之类）
        if info['skip']:
            if info['skip'].startswith('加权'):
                rep['weighted'] += 1
            rep['skipped'].append(dict(i=i, folder=e['folder'], title=title, why=info['skip'], cls=cls))
            continue
        rep['picked'][cls] += 1
        for k in info['kinds']:
            rep['kinds'][k] += 1
        for f in dict.fromkeys(info['flags']):
            rep['flags'].append(dict(i=i, folder=e['folder'], title=title, flag=f))
        if len(outs) > 1:
            rep['split'] += 1
        val = ban_fix(e['content'], rep['ban'])
        for key, region in outs:
            out.append(collections.OrderedDict(
                group=e.get('folder') or '', match_type=3, key=key, key_region=region, value_type=0, value=val, value_configs=[],
                value_region=sum(RV.get(x, 0) for x in e.get('impactRange') or []) or 1, sort=e['priority'], depth=max(1, int(e.get('scanDepth') or 1)),
                probability=e.get('probability', 100), enable=bool(e.get('enabled', True)),
                _src=i, _title=title, _part=({2: '玩家', 4: '回复'}[region] if len(outs) > 1 else None), _kinds=sorted(info['kinds'])))
    return out, rep


def check(out, rep):
    probs = []
    for x in out:
        bad = G.re2_problems(x['key'])
        if bad:
            probs.append('RE2 不认 #%d %s：%s' % (x['_src'], x['_title'], bad))
        if len(x['value']) > LIMIT_VALUE:
            probs.append('正文过四万字 #%d %s（%d 字）' % (x['_src'], x['_title'], len(x['value'])))
        for f in ('group', 'key', 'value'):
            m = BAN_RE.search(x[f])
            if m:
                probs.append('屏蔽词 #%d %s：%s 里有“%s”' % (x['_src'], x['_title'], f, x[f][max(0, m.start() - 8):m.end() + 8]))
        if not x['key']:
            probs.append('空钥匙 #%d %s' % (x['_src'], x['_title']))
    return probs


def pct(vals, p):
    vals = sorted(vals)
    return vals[min(len(vals) - 1, int(len(vals) * p))] if vals else 0


def write(card, out, rep, src_path, src_sha, force):
    d = os.path.join(OUT, G.CARDS[card]['dir'])
    os.makedirs(d, exist_ok=True)
    klen = [len(x['key']) for x in out]
    kb = [len(x['key'].encode('utf-8')) for x in out]
    size = sum(jbytes({k: v for k, v in x.items() if not k.startswith('_')}) + 1 for x in out)
    top = sorted(out, key=lambda x: -len(x['key']))[:12]
    R = dict(card=card, era=rep['era'], base=rep['base'], made=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), src=os.path.relpath(src_path, ROOT).replace(os.sep, '/'),
             src_sha256=src_sha, entries=len(out), src_entries=len({x['_src'] for x in out}), bytes=size, split=rep['split'], weighted=rep['weighted'],
             **({'sibling': rep['sibling']} if rep['sibling'] else {}),
             picked=dict(rep['picked']), kinds=dict(rep['kinds'].most_common()),
             key_chars=dict(p50=pct(klen, .5), p90=pct(klen, .9), p99=pct(klen, .99), max=max(klen or [0]), over600bytes=sum(b > 600 for b in kb),
                            over1200=sum(k > 1200 for k in klen), over3000=sum(k > 3000 for k in klen)),
             longest=[dict(i=x['_src'], title=x['_title'], chars=len(x['key'])) for x in top],
             skipped=rep['skipped'], flags=rep['flags'], left=rep['left'],
             ban=[dict(old=a, new=b, n=n) for a, b, n in rep['ban']], value_max=max((len(x['value']) for x in out), default=0))
    with open(os.path.join(d, '世界书_转换.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(dict(card=card, era=rep['era'], src_sha256=src_sha, entries=out), f, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(d, '转换报告.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(R, f, ensure_ascii=False, indent=1)
    L = ['# %s 风月世界书转换清单' % G.CARDS[card]['dir'], '', '%s 从 %s 转的。fy_lore.py 自己写的，重跑会盖掉。' % (R['made'], R['src']), '',
         '- 条目 %d 条（日里那边 %d 条，其中 %d 条拆成“只扫玩家”“只扫回复”两条），%.2f MB' % (R['entries'], R['src_entries'], R['split'], size / 1048576),
         '- 怎么来的：' + '；'.join('%s %d' % kv for kv in R['picked'].items()) + ('；文件夹带迷宫纪、可只在另一张的年份里醒的 %d 条不带' % R['sibling'] if R.get('sibling') else ''),
         '- 用到的改法（一条可以占几样）：' + '；'.join('%s %d' % kv for kv in R['kinds'].items()),
         '- 钥匙长度（字）：中位 %(p50)d，九成 %(p90)d，百里挑一 %(p99)d，最长 %(max)d；过 600 字节的 %(over600bytes)d 条，过 1200 字的 %(over1200)d 条，过 3000 字的 %(over3000)d 条' % R['key_chars'],
         '- 正文最长 %d 字（上限四万）' % R['value_max'], '']
    L += ['## 钥匙最长的几条', ''] + ['- #%(i)d %(title)s：%(chars)d 字' % x for x in R['longest']] + ['']
    by = collections.defaultdict(list)
    for s in R['skipped']:
        by[re.sub(r'：.*', '', s['why'])].append(s)
    L += ['## 没进卡的 %d 条' % len(R['skipped']), '']
    for why, lst in by.items():
        L += ['### %s（%d 条）' % (why, len(lst)), ''] + ['- #%d 〔%s〕%s%s' % (s['i'], s['folder'], s['title'], '｜' + s['why'] if '：' in s['why'] else '') for s in lst] + ['']
    fb = collections.defaultdict(list)
    for s in R['flags']:
        fb[re.sub(r'（.*?）|：.*', '', s['flag'])].append(s)
    L += ['## 转了、可有地方不是原样的 %d 处' % len(R['flags']), '']
    for why, lst in fb.items():
        L += ['### %s（%d 处）' % (why, len(lst)), ''] + ['- #%d 〔%s〕%s｜%s' % (s['i'], s['folder'], s['title'], s['flag']) for s in lst[:60]]
        L += (['- …另有 %d 处，见 转换报告.json' % (len(lst) - 60)] if len(lst) > 60 else []) + ['']
    if R['ban']:
        L += ['## 屏蔽词换掉的字（只换风月这一份）', ''] + ['- %s → %s（%d 处）' % (x['old'], x['new'], x['n']) for x in R['ban']] + ['']
    if R['left']:
        fc = collections.Counter(x['folder'] for x in R['left'])
        L += ['## 底卡里这一纪也醒得了、可没带的 %d 条（--base %s 以外的文件夹）' % (len(R['left']), R['base']), ''] + ['- %s：%d 条' % kv for kv in sorted(fc.items())] + ['']
    with open(os.path.join(d, '转换清单.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    return R


def main():
    argv = sys.argv[1:]

    def opt(k, dflt=None):
        if k in argv:
            i = argv.index(k)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return dflt
    src = opt('--src', SRC)
    mode = opt('--base', 'core')
    force = '--force' in argv
    cards = [G.card_of(a) for a in argv if not a.startswith('--')] or list(G.CARDS)
    assert mode in ('core', 'std', 'all'), '用法见文件头'
    raw = open(src, 'rb').read()
    sha = hashlib.sha256(raw).hexdigest()
    lb = json.loads(raw.decode('utf-8'))['prompt']['lorebook']
    nb = base_count()
    assert all(era_of(e) is None for e in lb[:nb]) and era_of(lb[nb]) is not None, '底卡那一段的条数跟 src/rili_v7.json 对不上'
    print('全本 %s：世界书 %d 条（底卡 %d）' % (os.path.basename(src), len(lb), nb))
    stop = False
    for card in cards:
        out, rep = build(card, lb, nb, mode)
        probs = check(out, rep)
        R = write(card, out, rep, src, sha, force)
        print('\n【%s】%d 条（日里 %d 条，拆两条的 %d），%.2f MB；没进卡 %d（加权 %d）；要看的 %d 处；钥匙最长 %d 字、过 1200 字 %d 条' % (
            G.CARDS[card]['dir'], R['entries'], R['src_entries'], R['split'], R['bytes'] / 1048576, len(R['skipped']), R['weighted'], len(R['flags']),
            R['key_chars']['max'], R['key_chars']['over1200']))
        print('   ' + '；'.join('%s %d' % kv for kv in R['picked'].items()))
        print('   ' + '；'.join('%s %d' % kv for kv in R['kinds'].items()))
        if R['left']:
            print('   底卡里这一纪也醒得了、没带的 %d 条（--base %s）' % (len(R['left']), mode))
        for p in probs[:20]:
            print('   ✗', p)
        if probs:
            stop = True
        if R['entries'] > LIMIT_N:
            print('   ✗ 过了风月世界书 %d 条的上限：%d 条。出路：--base 收窄；拆两条的 %d 条改成只扫玩家（不要 §预载 那一路）；或者这一纪再拆。' % (LIMIT_N, R['entries'], R['split']))
            stop = stop or not force
    if stop:
        sys.exit(1)


if __name__ == '__main__':
    main()
