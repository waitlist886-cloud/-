#!/usr/bin/env python3
# 把四纪大框拆成几份，分阶段导进日里（11-16）。
#   python -I -X utf8 底稿/门面/共用/split_card.py <卡.json> <输出目录> [--keep-intro] [--public] [--max-mb 9.5] [--tail-mb 4]
# <卡.json> 用 into_card.py 出的那一张（out/发布卡_四纪大框/奥尔德兰_四纪大框.json）。
#
# 日里编辑器上量到的（2026-11-15 读它的前端代码，细目在 底稿/门面/拼装_计划.md 第四节）：
#   · 顶栏“导入 → Rili”是整张替换：提示词、世界书、正则、样式、介绍页、快捷键、标签、可见性一起换，文件大小不设限，没有追加。
#   · 世界书那一栏自己的“导入”钮是往后追加，单个文件不过 20MB，认 {"prompt":{"lorebook":[…]}}（它自己“导出”的样子）。
#     跟已有条目一字不差的算重复，会弹一个框问全部导入还是跳过重复。
#   · 每点一次保存，整张卡一次 PUT 过去（不是只传新添的），客户端只等 90 秒。过了三十兆会时灵时不灵地回 503，多点几回能过。
# 所以拆法是：第 1 份是一张完整的卡，世界书只带底卡和功能那一部分，走顶栏导入；第 2 份起一纪一份世界书，走世界书那一栏的导入。
# 超过 --max-mb 的纪照文件夹切开；最后一纪照 --tail-mb 切得更细（平台上存过的最大一张是 35 兆上下，最后这一纪正好跨过去，步子小一点）。
# 条目在各份里的先后照原卡，优先级一条不动；合起来跟原卡一条不多一条不少（脚本末尾核）。
# 第 1 份的介绍页默认换成不带退路的薄壳（几千字，整张卡少两兆多）；带退路的那一版另存成 介绍页_带退路.html，全存稳了想要再贴。--keep-intro 照原样留着。
# --cards 月银纪+纷争纪,山铜纪+迷宫纪：不分批，照写的几纪各出一张完整的卡（提示词、正则、样式、介绍页、底卡，加这几纪的世界书），
#   一张卡一次顶栏导入、存一回。11-15 夜备着的退路（细目在 拼装_计划.md 第四节第 6、8 小节）：那时以为一张卡装不下，后来用户多点几回把 39.3MB 存上了，这一路没用上。
# 第 1 份的可见性默认写私密（平台顶栏上的叫法）：卡文件是从发布卡来的，写的是公开，顶栏导入会照文件把可见性也换掉。--public 照原样。
import collections
import copy
import datetime
import hashlib
import io
import json
import math
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_thin  # noqa: E402

ERAS = ['月银纪', '纷争纪', '山铜纪', '迷宫纪']
CN = '一二三四五六七八九十'
MB = 1000 * 1000

# 平台保存时的校验（前端 55765 那一块的 KU、Xc，2026-11-15 读的）。字数照 JS 的 length。
LIM = dict(prompt=98304, suggest=65536, content=100000, word=1024, words=256, black=256, prio=8192, depth=30,
           regex_n=500, regex=4096, repl=100000, styles=5242880, intro=5242880, title=100, desc=2048, changelog=2048,
           options=50, opt_label=128, opt_value=1024, tags=15, tag=32, wb_file=20 * 1024 * 1024)
TRIG = {'system', 'user', 'assistant', 'working-memory', 'model-name'}
IMPACT = {'system', 'headPrompt', 'rearPrompt'}


def jlen(s):
    """JS 的字符串长度（UTF-16 的码元数）。"""
    return len(s.encode('utf-16-le')) // 2


def dumps(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':'))


def nbytes(o):
    return len(dumps(o).encode('utf-8'))


def check_entry(e):
    bad = []
    tw = e.get('triggerWords')
    if not isinstance(tw, list) or not 1 <= len(tw) <= LIM['words']:
        bad.append('触发词 %s 个' % (len(tw) if isinstance(tw, list) else '?'))
    elif any(not isinstance(w, str) or jlen(w) > LIM['word'] for w in tw):
        bad.append('触发词过 1024 字')
    bw = e.get('blackListWords')
    if bw is not None and (not isinstance(bw, list) or len(bw) > LIM['black'] or any(not isinstance(w, str) or jlen(w) > LIM['word'] for w in bw)):
        bad.append('黑名单超了')
    if e.get('triggerWordsType') not in ('AND', 'OR') or e.get('blackListWordsType') not in ('AND', 'OR'):
        bad.append('AND/OR 没写')
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    if not num(e.get('priority')) or not 0 <= e['priority'] <= LIM['prio']:
        bad.append('优先级 %r' % e.get('priority'))
    if not num(e.get('probability')) or not 1 <= e['probability'] <= 100:
        bad.append('概率 %r' % e.get('probability'))
    if not num(e.get('scanDepth')) or not 0 <= e['scanDepth'] <= LIM['depth']:
        bad.append('深度 %r' % e.get('scanDepth'))
    if not isinstance(e.get('triggerRange'), list) or not set(e['triggerRange']) <= TRIG:
        bad.append('触发范围 %r' % e.get('triggerRange'))
    if not isinstance(e.get('impactRange'), list) or not set(e['impactRange']) <= IMPACT:
        bad.append('影响范围 %r' % e.get('impactRange'))
    cm = e.get('contentMethod', 'single')
    if cm == 'single':
        c = e.get('content', '')
        if not isinstance(c, str) or not c.strip() or jlen(c) > LIM['content']:
            bad.append('内容空着或过十万字')
    elif cm == 'weighted':
        cs = e.get('contents')
        if not isinstance(cs, list) or not 1 <= len(cs) <= 30:
            bad.append('加权内容的条数')
        else:
            if any(not isinstance(x.get('content'), str) or jlen(x['content']) > LIM['content'] or not num(x.get('probability')) or not 0 < x['probability'] <= 100 for x in cs):
                bad.append('加权内容的某一条')
            elif abs(sum(x['probability'] for x in cs) - 100) > .01:
                bad.append('加权概率之和不是 100')
        if 'content' in e and (not isinstance(e['content'], str) or jlen(e['content']) > LIM['content']):
            bad.append('content 不是字')
    else:
        bad.append('内容方式 %r' % cm)
    extra = set(e) - {'enabled', 'triggerWords', 'triggerWordsType', 'blackListWords', 'blackListWordsType', 'folder', 'priority',
                      'probability', 'scanDepth', 'triggerRange', 'impactRange', 'contentMethod', 'content', 'contents'}
    if extra:
        bad.append('多出来的键 %s' % sorted(extra))
    return bad


def check_card(card):
    bad = []
    p = card.get('prompt') or {}
    for k in ('systemPrompt', 'headPrompt', 'rearPrompt'):
        if jlen(p.get(k) or '') > LIM['prompt']:
            bad.append('%s 过 98304 字' % k)
    if jlen(p.get('suggestionsPrompt') or '') > LIM['suggest']:
        bad.append('后续建议过 65536 字')
    rr = card.get('assistantRegexReplace') or []
    if len(rr) > LIM['regex_n']:
        bad.append('正则 %d 条，过 500' % len(rr))
    for i, r in enumerate(rr):
        if jlen(r.get('regex') or '') > LIM['regex'] or jlen(r.get('replaceString') or '') > LIM['repl']:
            bad.append('正则第 %d 条太长' % i)
        if r.get('enabled', True) and not (r.get('regex') or '').strip():
            bad.append('正则第 %d 条匹配内容空着' % i)
    if jlen(card.get('injectStyles') or '') > LIM['styles']:
        bad.append('样式过 5242880 字')
    if jlen(card.get('introPage') or '') > LIM['intro']:
        bad.append('介绍页过 5242880 字')
    if not 1 <= jlen(card.get('title') or '') <= LIM['title']:
        bad.append('标题')
    if jlen(card.get('description') or '') > LIM['desc']:
        bad.append('简介过 2048 字')
    if jlen(card.get('changelog') or '') > LIM['changelog']:
        bad.append('更新说明过 2048 字')
    items = (card.get('options') or {}).get('items') or []
    if len(items) > LIM['options'] or any(not 1 <= jlen(o.get('label') or '') <= LIM['opt_label'] or not 1 <= jlen(o.get('value') or '') <= LIM['opt_value'] or o.get('type') != 'SET-INPUT' for o in items):
        bad.append('快捷键')
    tags = [t['tag']['name'] for t in card.get('cardsTags') or []]
    if len(tags) > LIM['tags'] or any(jlen(t) > LIM['tag'] for t in tags):
        bad.append('标签')
    if card.get('language') not in ('en', 'zh', 'ja', 'ko'):
        bad.append('语言')
    return bad


def norm(e):
    """世界书导入认重复用的那一套（前端 2850 那一块的 U）：补默认值、文件夹去空白、键排好序再比整条。"""
    d = dict(e)
    d['enabled'] = True if e.get('enabled') is None else e['enabled']
    d['blackListWords'] = e.get('blackListWords') if e.get('blackListWords') is not None else []
    f = (e.get('folder') or '').strip()
    if f:
        d['folder'] = f
    else:
        d.pop('folder', None)
    d['contentMethod'] = e.get('contentMethod') or 'single'
    d['content'] = e.get('content') if e.get('content') is not None else ''
    if e.get('contentMethod') == 'weighted':
        d['contents'] = e.get('contents')
    else:
        d.pop('contents', None)
    return json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def folder_no(e):
    m = re.match(r'\s*(\d+)', e.get('folder') or '')
    return int(m.group(1)) if m else -1


def group_of(e):
    """四十号以后、文件夹名里带纪名的归那一纪；别的（底卡 00 到 39、90 以后的功能、没文件夹的）归第 1 份。"""
    f = e.get('folder') or ''
    if folder_no(e) >= 40:
        m = re.search('|'.join(ERAS), f)
        if m:
            return m.group(0)
    return '底卡'


def cut(entries, max_bytes):
    """一纪的条目照文件夹号切成几份，每份不过 max_bytes，份数最少、各份尽量一般大。文件夹不拆开，条目的先后照原卡。"""
    total = sum(b for _, _, b in entries)
    if total <= max_bytes:
        return [entries]
    by = collections.OrderedDict()
    for it in sorted(entries, key=lambda x: (folder_no(x[1]), x[0])):
        by.setdefault(folder_no(it[1]), []).append(it)
    nos = list(by)
    size = [sum(b for _, _, b in by[n]) for n in nos]
    assert max(size) <= max_bytes, '有一个文件夹自己就超了：%s' % [(n, s) for n, s in zip(nos, size) if s > max_bytes]
    pre = [0]
    for s in size:
        pre.append(pre[-1] + s)
    n = len(nos)
    for k in range(math.ceil(total / max_bytes), n + 1):
        # best[j][i]：前 i 个文件夹切成 j 份，最大那一份最小是多少
        INF = float('inf')
        best = [[INF] * (n + 1) for _ in range(k + 1)]
        back = [[0] * (n + 1) for _ in range(k + 1)]
        best[0][0] = 0
        for j in range(1, k + 1):
            for i in range(j, n + 1):
                for h in range(j - 1, i):
                    v = max(best[j - 1][h], pre[i] - pre[h])
                    if v < best[j][i]:
                        best[j][i], back[j][i] = v, h
        if best[k][n] <= max_bytes:
            cuts, i = [], n
            for j in range(k, 0, -1):
                cuts.append((back[j][i], i))
                i = back[j][i]
            parts = []
            for a, b in reversed(cuts):
                part = [it for no in nos[a:b] for it in by[no]]
                parts.append(sorted(part, key=lambda x: x[0]))
            return parts
    raise AssertionError('切不开')


def pack_cards(sk, groups, out, spec, src_bytes, src_entries):
    """--cards：照写的几纪各出一张完整的卡。底卡那一部分每张都带，各纪的条目照原卡的先后插回去。"""
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if re.match(r'卡[一二三四五六七八九十]_.*\.json$', f):
            os.remove(os.path.join(out, f))
    used = collections.Counter()
    rows = []
    for k, part in enumerate(spec.split(',')):
        eras = [x for x in part.split('+') if x]
        assert eras and all(x in ERAS for x in eras), '纪名写错了：%s' % part
        used.update(eras)
        pick = sorted(groups['底卡'] + [it for g in eras for it in groups[g]], key=lambda x: x[0])
        c = copy.deepcopy(sk)
        c['prompt']['lorebook'] = [e for _, e, _ in pick]
        assert not check_card(c) and all(not check_entry(e) for e in c['prompt']['lorebook'])
        assert max(collections.Counter(norm(e) for e in c['prompt']['lorebook']).values()) == 1
        fn = '卡%s_%s.json' % (CN[k], '_'.join(eras))
        txt = dumps(c).encode('utf-8')
        with open(os.path.join(out, fn), 'wb') as f:
            f.write(txt)
        back = json.loads(txt.decode('utf-8'))
        assert len(back['prompt']['lorebook']) == len(pick) and back['publicAccess'] is c['publicAccess']
        rows.append((fn, eras, len(pick), len(txt)))
    miss = [g for g in ERAS if not used[g]]
    print('原卡 %.1f MB，%d 条世界书 → %d 张卡，写在 %s' % (src_bytes / MB, src_entries, len(rows), out))
    for fn, eras, n, b in rows:
        print('  %-24s 底卡加 %s：%5d 条，%5.1f MB' % (fn, '、'.join(eras), n, b / MB))
    print('每张都过了平台的校验，没有一字不差的重复条目。' + ('没进任何一张的纪：' + '、'.join(miss) if miss else '四纪都有着落。'))
    twice = [g for g in ERAS if used[g] > 1]
    if twice:
        print('两张里都有的纪：' + '、'.join(twice))


def folders_of(part):
    seen = collections.OrderedDict()
    for _, e, _ in sorted(part, key=lambda x: (folder_no(x[1]), x[0])):
        name = re.sub(r'^\s*\d+·', '', e.get('folder') or '')
        name = re.split('[｜|]', name, maxsplit=1)[-1]
        seen[name] = seen.get(name, 0) + 1
    return seen


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    src, out = args[0], args[1]
    opt = lambda k, d: float(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
    max_b, tail_b = int(opt('--max-mb', 9.5) * MB), int(opt('--tail-mb', 4) * MB)
    keep_intro, public = '--keep-intro' in sys.argv, '--public' in sys.argv
    raw = open(src, 'rb').read()
    card = json.loads(raw.decode('utf-8'))
    lb = card['prompt']['lorebook']

    # 一、原卡先照平台的规矩过一遍
    bad = check_card(card)
    for i, e in enumerate(lb):
        for b in check_entry(e):
            bad.append('世界书第 %d 条（%s）：%s' % (i, (e.get('content') or '')[:24].replace('\n', ' '), b))
    if bad:
        print('原卡过不了平台的校验，先改这些：')
        for b in bad[:60]:
            print('   ', b)
        sys.exit(1)
    seen = collections.Counter(norm(e) for e in lb)
    dup = sum(c - 1 for c in seen.values() if c > 1)
    assert dup == 0, '原卡里有 %d 条一字不差的重复条目，世界书导入会弹框' % dup

    # 二、分组
    items = [(i, e, nbytes(e) + 1) for i, e in enumerate(lb)]
    groups = collections.OrderedDict((g, []) for g in ['底卡'] + ERAS)
    for it in items:
        groups[group_of(it[1])].append(it)

    # 三、第 1 份：整张卡，世界书只留底卡和功能
    sk = copy.deepcopy(card)
    sk['prompt']['lorebook'] = [e for _, e, _ in groups['底卡']]
    intro_full = card.get('introPage') or ''
    # 11-17 起薄壳里存的退路是一页简式建档（三万字节上下），第 1 份照原样带着；只有存着那一整页旧介绍页（into_card.py --old）的才换成不带退路的
    has_old = '__OLD1001' in intro_full and len(intro_full) > 200000
    if not keep_intro and has_old:
        thin = make_thin.thin_html(old=None)
        assert 'FRONT_CFG' in thin and len(thin) < 20000
        sk['introPage'] = thin
        cl = sk.get('changelog') or ''
        sk['changelog'] = cl.replace('门面的图和页面放在图床上，载不下来的时候可以点一下退回原来的介绍页。', '门面的图和页面放在图床上。')
    if not public:
        sk['publicAccess'] = False
    assert not check_card(sk)

    if '--cards' in sys.argv:
        pack_cards(sk, groups, out, sys.argv[sys.argv.index('--cards') + 1], len(raw), len(lb))
        return

    # 四、各纪的份
    parts = []   # (名字, 类, 条目)
    for g in ERAS:
        cuts = cut(groups[g], tail_b if g == ERAS[-1] else max_b)
        if len(cuts) == 1:
            parts.append((g, cuts[0]))
        else:
            tag = '上下' if len(cuts) == 2 else ('上中下' if len(cuts) == 3 else CN)
            for k, c in enumerate(cuts):
                parts.append((g + tag[k], c))

    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if re.match(r'第\d+份_.*\.json$', f) or f in ('清单.json', '导入说明.md', '介绍页_带退路.html'):
            os.remove(os.path.join(out, f))
    files = []
    name1 = '第1份_骨架和底卡.json'
    with open(os.path.join(out, name1), 'w', encoding='utf-8', newline='') as f:
        f.write(dumps(sk))
    files.append(dict(file=name1, how='card', label='骨架和底卡', entries=len(sk['prompt']['lorebook'])))
    for k, (name, part) in enumerate(parts):
        fn = '第%d份_%s.json' % (k + 2, name)
        with open(os.path.join(out, fn), 'w', encoding='utf-8', newline='') as f:
            f.write(dumps({'prompt': {'lorebook': [e for _, e, _ in part]}}))
        files.append(dict(file=fn, how='lorebook', label=name, entries=len(part), folders=folders_of(part)))
    if not keep_intro and has_old:
        with open(os.path.join(out, '介绍页_带退路.html'), 'w', encoding='utf-8', newline='') as f:
            f.write(intro_full)

    # 五、核：读回来，合起来跟原卡一条不多一条不少；各份过平台的校验；大小；合起来再过一遍整张卡的校验
    back, total_entries, acc = collections.Counter(), 0, None
    base_bytes = None
    for d in files:
        p = os.path.join(out, d['file'])
        txt = open(p, 'rb').read()
        d['bytes'] = len(txt)
        d['sha256'] = hashlib.sha256(txt).hexdigest()
        o = json.loads(txt.decode('utf-8'))
        if d['how'] == 'card':
            assert not check_card(o) and o['publicAccess'] is (card['publicAccess'] if public else False)
            ents = o['prompt']['lorebook']
            acc = copy.deepcopy(o)
            base_bytes = len(txt) - nbytes(ents)
        else:
            assert list(o) == ['prompt'] and list(o['prompt']) == ['lorebook'], '世界书那一份只能有 prompt.lorebook 这一个口子，多了平台不认'
            assert d['bytes'] <= LIM['wb_file'], '%s 过了 20MB' % d['file']
            ents = o['prompt']['lorebook']
            acc['prompt']['lorebook'] = acc['prompt']['lorebook'] + ents
        assert len(ents) == d['entries'] and all(not check_entry(e) for e in ents)
        back.update(norm(e) for e in ents)
        total_entries += len(ents)
        d['total_entries'] = total_entries
        d['card_bytes'] = nbytes(acc)          # 存这一步时传上去的整张卡大概多大
    assert back == seen and total_entries == len(lb), '拆出来的合起来跟原卡对不上'
    assert not check_card(acc)
    rest = {k: v for k, v in acc.items() if k not in ('prompt', 'introPage', 'changelog', 'publicAccess')}
    assert rest == {k: v for k, v in card.items() if k not in ('prompt', 'introPage', 'changelog', 'publicAccess')}
    assert {k: v for k, v in acc['prompt'].items() if k != 'lorebook'} == {k: v for k, v in card['prompt'].items() if k != 'lorebook'}

    # 优先级相同的条目，拆完以后先后变没变（变了的只该是不同纪之间、或者底卡新条目跟各纪之间）
    pos = {norm(e): i for i, e in enumerate(lb)}
    order = [pos[norm(e)] for e in acc['prompt']['lorebook']]
    byp = collections.defaultdict(list)
    for i in order:
        byp[lb[i]['priority']].append(i)
    flips = collections.Counter()
    for idx in byp.values():
        for a, b in zip(idx, idx[1:]):
            if a > b:
                ga, gb = group_of(lb[a]), group_of(lb[b])
                assert ga != gb, '同一组里优先级相同的两条先后倒了'
                flips[ga + '／' + gb] += 1

    manifest = dict(made=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), source=os.path.basename(src), source_bytes=len(raw),
                    source_sha256=hashlib.sha256(raw).hexdigest(), entries=len(lb), keep_intro=keep_intro, public=public,
                    final_card_bytes=files[-1]['card_bytes'], same_priority_reordered=dict(flips), files=files)
    with open(os.path.join(out, '清单.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, '导入说明.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(readme(manifest, has_old and not keep_intro))

    print('原卡 %.1f MB，%d 条世界书 → %d 份，写在 %s' % (len(raw) / MB, len(lb), len(files), out))
    for d in files:
        print('  %-22s %-5s %5d 条 %6.2f MB ｜导完一共 %5d 条，存的时候整张卡约 %5.1f MB' % (
            d['file'], '顶栏' if d['how'] == 'card' else '世界书', d['entries'], d['bytes'] / MB, d['total_entries'], d['card_bytes'] / MB))
    print('合起来跟原卡一条不多一条不少；各份都过了平台的校验；没有一字不差的重复条目。')
    print('优先级相同、先后跟原卡不一样的相邻对：', dict(flips) or '没有')


def readme(m, intro_swapped):
    fs = m['files']
    mb = lambda b: '%.1f' % (b / MB)
    L = []
    L.append('# 四纪大框分批导入')
    L.append('')
    L.append('%s 拆的。整张卡 %s MB、%d 条世界书，拆成 %d 份。合起来跟整张的那一份一条不多一条不少，只是世界书里条目排的先后按纪归了堆，优先级一条没动。' % (
        m['made'][:10], mb(m['source_bytes']), m['entries'], len(fs)))
    L.append('')
    L.append('## 先知道五件事')
    L.append('')
    L.append('1. 编辑器里有两个“导入”，别弄反。最顶上那一排的“导入”点开选“Rili”，是把整张卡换掉。往下翻到“世界书”那一栏，“添加”那一排的右边有五个小图标钮，最左边那个（鼠标停上去写着“从文件导入世界书条目。”）是往后追加。第 1 份走顶上那个，第 2 份起都走世界书里那个。')
    L.append('2. 顶上那个导入换掉的是整张卡：主提示词、前置词后置词、世界书、显示正则、样式、介绍页、快捷键、标签、简介、是不是 NSFW，都照文件来。平台上手改过、文件里没有的东西会没掉，要留的先自己另存一份。')
    L.append('3. 每点一次“保存”，平台传的都是整张卡，不是只传新添的那一份。所以越往后存得越慢，最后一回要传 %s MB，平台只等 90 秒。用电脑，用快一点的网，别用手机流量。' % mb(m['final_card_bytes']))
    L.append('4. 卡过了二十兆（导完第 3 份起），编辑器这一页不能直接开网址、不能按 F5 刷新、不能从浏览器的历史或书签进，一进就是“500 · 服务器错误，Rili 断线了”。这不是卡坏了，存上的东西都在。要进编辑器，先到“工作室”的卡片列表，从列表里点这张卡。聊天页（玩家看到的那一页）不受影响，照常能直接开。')
    L.append('5. 卡过了三十兆，保存会时灵时不灵地报 503，隔几秒再点、多点几回能过（11-15 导到第 6 份、39.3MB 都是这样存上的）。最后要到 %s MB、%d 条，那一步没人试完过。所以最后一纪切得细，一步一步加，哪一步实在存不上，前面存上的都还在。' % (mb(m['final_card_bytes']), m['entries']))
    L.append('')
    L.append('## 步骤')
    L.append('')
    L.append('世界书那一栏的搜索框底下有一行小字“全部文件夹中共有 N 个项目”。每导完一份，这个数跟下表对得上再点保存。')
    L.append('')
    L.append('| 先后 | 文件 | 走哪个导入 | 导完一共几条 | 这一步存的时候整张卡多大 |')
    L.append('|---|---|---|---|---|')
    for i, d in enumerate(fs):
        L.append('| %d | %s（%s MB） | %s | %d | %s MB |' % (i + 1, d['file'], mb(d['bytes']), '顶栏“导入”→“Rili”' if d['how'] == 'card' else '世界书那一栏的导入钮', d['total_entries'], mb(d['card_bytes'])))
    L.append('')
    L.append('1. 从“工作室”的卡片列表点进这张卡的编辑器。平台上现在这一张想留个底的话，顶栏“导入”点开，最底下一项是“导出”，先存到电脑里。')
    L.append('2. 顶栏“导入”→“Rili”，选 %s。右边预览换成新门面的牌桌，世界书变成 %d 条。顶栏“保存”左边那一格会是“私密”（文件里写的就是私密；要盖的是已经公开的那一张，在这里改回公开再存）。点“保存”，等它跳出存好了的提示。' % (fs[0]['file'], fs[0]['total_entries']))
    L.append('3. 回“工作室”列表，再点进这张卡一回，确认存上了（世界书 %d 条）。这一步存完，卡已经能玩迷宫纪 1001 年，前面四纪还没有。' % fs[0]['total_entries'])
    L.append('4. 往下翻到“世界书”，点“添加”那一排右边最左的那个导入钮，选 %s。右上角跳一句导入了 %d 条，那行小字的数变成 %d。回到顶上点“保存”，等它跳出存好了的提示。' % (fs[1]['file'], fs[1]['entries'], fs[1]['total_entries']))
    L.append('5. 剩下几份照第 4 步，一份一份来：导一份，对一下数，存一次。从第 4 份起卡就过三十兆了，每存完一份，回“工作室”列表再点进来一回，确认编辑器还打得开、数目对，再导下一份。')
    L.append('')
    L.append('各份里是什么：')
    L.append('')
    L.append('- %s：提示词、显示正则、样式、介绍页、快捷键，加世界书里底卡那一部分（迷宫纪 1001 年、通用规则、命运骰和开关）。' % fs[0]['file'])
    for d in fs[1:]:
        L.append('- %s：%s。' % (d['file'], '、'.join(d['folders'])))
    L.append('')
    L.append('## 出了岔子')
    L.append('')
    L.append('- 导入时弹一个框说有重复的条目：是同一份导了两回。点“跳过重复”那个钮，别点全部导入。')
    L.append('- 保存报 503（Request failed with status code 503）或者超时：别关页面，隔几秒再点保存，多点几回。卡过了三十兆就是这样，11-15 那一回第 4 份点了两回、第 5 和第 6 份都是多点了几回才存上的。连点十来回都不行，再把页面关掉（不保存），平台上留着的是上一步存好的样子，前面几纪照常能玩。告诉我停在第几份、报的什么字。')
    L.append('- 存上了，可回头从列表点不进编辑器：也告诉我停在第几份。')
    L.append('- 想从头再来：重新走第 2 步，顶栏导入第 1 份会把世界书整个换回 %d 条。' % fs[0]['total_entries'])
    L.append('')
    if intro_swapped:
        L.append('## 介绍页的退路（可选，全存稳了再说）')
        L.append('')
        L.append('第 1 份里的介绍页是只有几千字的薄壳，新门面的页面和图都从图床取。图床连不上的时候，玩家只会看到一句话和“再试一次”。带退路的那一版（图床连不上能退回原来那一整页介绍页）存成了 介绍页_带退路.html：用记事本打开，全选复制，贴进编辑器“介绍页面”那一格（先把里面原来的全选删掉），再保存。整张卡会再大 3 MB 上下，存不上就不贴。')
        L.append('')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    main()
