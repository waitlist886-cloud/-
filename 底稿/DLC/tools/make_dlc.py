#!/usr/bin/env python3
# 四纪大框切 DLC（11-24，用户回切包方向稿第五节“照倾向”）：照 packs.json 的「_发布」那几包，把条目从打好的卡里拿出来，
# 一包出一份日里原生的模组 JSON（只带世界书），本体去掉这些条目另存。全本另留一份（风月版、1001 年切片、对账都从全本出）。
#
#   打卡那一串里（into_card.py 以后、split_card.py 以前），原地切：
#     python -I -X utf8 底稿/DLC/tools/make_dlc.py out/发布卡_四纪大框/奥尔德兰_四纪大框.json \
#            --also out/发布卡_四纪大框/奥尔德兰_四纪大框_原介绍页.json --ver 11-24
#     · 输入那两张先原样拷成 <名>_全本.json，再把本体写回原来的名字（split_card、zip_cards 照旧读这个名字）；
#     · 四包写在卡旁边的 DLC/ 下：奥尔德兰DLC_<包名>_<版本>.json，加 清单.json、说明.md。
#     · 输入里已经没有 DLC 的条目（切过一回了）就停，免得拿本体当全本。
#   不动原卡、另出一份（拿现行卡试切）：
#     python -I -X utf8 底稿/DLC/tools/make_dlc.py <卡.json> --also <原介绍页卡.json> --ver 11-24 --out out/DLC_11-24
#     · 本体写成 <out>/<名>_本体.json，四包和清单、说明也写在 <out>/ 下。
# 别的开关：
#   --base 11-24     描述头一行“需要本体 X 以后的版本”里的 X，不写就跟 --ver 一样
#   --packs 羁绊篇,神谱   只切这几包（默认 _发布 里全部）
#   --accept         引用扫描多出来的落空引用认下来，写进 底稿/DLC/落空白名单.json（不加就停）
#   --no-sim         不跑醒没醒得了的模拟（快十几秒）
#   --record         这一回的指纹记进 底稿/DLC/发布记录.json（真发出去以后再跑一回加这个）
#
# 核：各包两两不相交；本体加各包跟全本一条不多一条不少（split_card.norm）；本体过 split_card.check_card，DLC 每条过 check_entry、
# 每份不过 20MB；--also 那一张切下来的跟主卡切下来的是同一批；refscan 合切一回，硬引用跟 落空白名单.json 比，多出来的停；
# 拿 slim_card.cases 的凭证和回复底座，接上条目自己触发词里的字，模拟每条 DLC 条目至少在一种凭证下醒得了（醒不了的停）。
# 模组的后置词这一回不带（方向稿第五节第 3 件：模组的后置词是并进还是盖掉本体的没验过）。条目原样搬，优先级、深度、文件夹一个不改。
import collections
import copy
import datetime
import hashlib
import json
import os
import re
import shutil
import sys

sys.dont_write_bytecode = True
_KEEP = []     # refscan、split_card 导入时各自把 sys.stdout 换一回，换下来的留着引用，不然叫回收时会把底下的输出关掉
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
DLC_DIR = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, '底稿', '门面', '共用'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', '大框'))
_KEEP.append(sys.stdout)
import refscan as RS          # noqa: E402
_KEEP.append(sys.stdout)
import split_card as SC       # noqa: E402  check_card、check_entry、norm、jlen
_KEEP.append(sys.stdout)
import slim_card as SL        # noqa: E402  cases、_hit

MB = 1000 * 1000
WHITE = os.path.join(DLC_DIR, '落空白名单.json')
RECORD = os.path.join(DLC_DIR, '发布记录.json')
ERAS = ['月银纪', '纷争纪', '山铜纪', '迷宫纪']
OLD_CARD_N = '八千五百多'      # 切包以前那一张全本卡的条数，写进描述里提醒别混用


def dumps(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':'))


def opt(argv, k, d=None):
    if k in argv:
        i = argv.index(k)
        v = argv[i + 1]
        del argv[i:i + 2]
        return v
    return d


def finger(entries):
    return hashlib.sha256('\n'.join(sorted(SC.norm(e) for e in entries)).encode('utf-8')).hexdigest()


def era_of(e):
    m = re.search('|'.join(ERAS), e.get('folder') or '')
    return m.group(0) if m and SC.folder_no(e) >= 40 else None


def pick(lb, packs, rel):
    """返回 {发布包名: [下标…]}（照卡里的先后）。"""
    out = collections.OrderedDict()
    for name in rel:
        idx = set()
        for p in packs['_发布'][name]['parts']:
            idx |= RS.select(lb, packs[p])
        out[name] = sorted(idx)
    return out


def description(name, spec, n, ver, base):
    s = '版本 %s｜需要本体 %s 以后的版本｜世界书 %d 条，追加进本体\n%s\n更新：模组出了新版本不会自动换，到模组那一栏选新版本再保存。别跟切包以前那一张整卡（世界书%s条的那一张）一起用，会重两份。' % (
        ver, base, n, spec['blurb'], OLD_CARD_N)
    assert SC.jlen(s) <= SC.LIM['desc'], name
    return s


# ---------------- 醒得了醒不了 ----------------
def literals(e):
    """条目触发词里能直接写进一句话的字（正则拆到元字符为止），去掉认纪元、开局、年份的。"""
    out = []
    for w in e.get('triggerWords') or []:
        p = SL.parse(w)
        if not p:
            runs = [w]
        else:
            body = re.sub(r'\\.', '\x01', p[0])
            runs = re.split(r'[\\^$.|?*+()\[\]{}/\x01]', body)
        for r in runs:
            r = r.strip()
            if len(r) >= 2 and re.search(r'[\u4e00-\u9fff]', r) and not re.search('纪元|开局|年份|底座', r):
                out.append(r)
    seen, res = set(), []
    for r in sorted(out, key=len, reverse=True):
        if r not in seen:
            seen.add(r)
            res.append(r)
    return res[:24]


YEAR_MAX = {'月银纪': 10200, '纷争纪': 11100, '山铜纪': 1000, '迷宫纪': 1100}
BOOK_OF = {era: b for b, (_, era) in SL.BOOKS.items()}


def _woke(e, s):
    return SL._hit(e.get('triggerWords'), e.get('triggerWordsType'), s) and not SL._hit(e.get('blackListWords'), e.get('blackListWordsType'), s)


def simulate(lb, idx_by_pack):
    """先拿 slim_card.cases 原样的凭证（user）和回复底座（assistant）各接一句条目自己触发词里的字试；
    主线开局的年份盖不住的（好多羁绊之章只在那个人活着的几十年里醒），再拿同一种凭证、底座把年份换成那一纪每一年扫一遍。
    凭证和底座的写法全从 cases 来，本体改了 纪元：X纪N年 的写法，这里跟着变，旧 DLC 醒不了就报出来。"""
    cases = SL.cases(ROOT)
    msgs = collections.defaultdict(list)          # 纪 → [(消息, 范围)]
    tmpl = {}                                     # 纪 → [(带 {Y} 的消息, 范围)]
    for era, name, old, new, reply in cases:
        if era not in ERAS:
            continue
        msgs[era].append((new or old, 'user'))
        if reply:
            msgs[era].append((reply, 'assistant'))
        if era not in tmpl and new and reply:
            yre = re.compile('纪元：%s(?:\\d+|元)年' % era)
            if yre.search(new) and yre.search(reply):
                tmpl[era] = [(yre.sub('纪元：%s{Y}' % era, new, count=1), 'user'), (yre.sub('纪元：%s{Y}' % era, reply, count=1), 'assistant')]
    assert set(tmpl) == set(ERAS), '有一纪的凭证或回复底座里认不出“纪元：X纪N年”：%s' % (set(ERAS) - set(tmpl))
    res = {}
    for pk, idx in idx_by_pack.items():
        sleep, nolit, swept = [], [], 0
        for i in idx:
            e = lb[i]
            cands = literals(e)
            if not cands:
                nolit.append(i)
                continue
            era = era_of(e)
            eras = [era] if era else ERAS
            rngs = e.get('triggerRange') or []
            ok = any(_woke(e, m + '\n' + c) for x in eras for m, rng in msgs[x] if rng in rngs for c in cands)
            if not ok:
                swept += 1
                for x in eras:
                    for y in range(1, YEAR_MAX[x] + 1):
                        yt = SL.year_text(BOOK_OF[x], y)
                        for m, rng in tmpl[x]:
                            if rng in rngs:
                                m2 = m.replace('{Y}', yt)
                                if any(_woke(e, m2 + '\n' + c) for c in cands):
                                    ok = True
                                    break
                        if ok:
                            break
                    if ok:
                        break
            if not ok:
                sleep.append(i)
        res[pk] = dict(n=len(idx), sleep=sleep, nolit=nolit, swept=swept)
    return res, len(cases)


# ---------------- 说明 ----------------
def readme(m):
    L = []
    mb = lambda b: '%.2f' % (b / MB)
    L.append('# 奥尔德兰的旅印 DLC（%s）' % m['ver'])
    L.append('')
    L.append('%s 从 %s 切的（世界书 %d 条、%s MB）。四包追加进本体，本体去掉了这些条目。make_dlc.py 自己写的，改了重跑会盖掉。' % (
        m['made'][:10], m['full']['file'], m['full']['entries'], mb(m['full']['bytes'])))
    L.append('')
    L.append('| 文件 | 模组标题 | 条目 | 大小 |')
    L.append('|---|---|---|---|')
    for d in m['packs']:
        L.append('| %s | %s | %d | %s MB |' % (d['file'], d['title'], d['entries'], mb(d['bytes'])))
    for b in m['bodies']:
        L.append('| %s | 本体（%s） | %d | %s MB |' % (b['file'], b['which'], b['entries'], mb(b['bytes'])))
    L.append('')
    L.append('本体加四包跟全本一条不多一条不少；本体照旧 %d 条显示正则，提示词、样式、介绍页、快捷键一个字没动。' % m['regex'])
    if len(m['bodies']) > 1:
        L.append('')
        L.append('本体两张只差介绍页：%s 是平时导的那一张（薄壳介绍页，门面从图床取）；%s 带原来那一整页介绍页，备着用。' % (
            m['bodies'][0]['file'], m['bodies'][1]['file']))
    L.append('')
    L.append('## 先私密试导一包（量一量模组能装多大）')
    L.append('')
    L.append('模组建了以后适用范围、公开、收费改不了，一天至多新建五个，私密的也改不成公开。所以先拿最大的羁绊篇（%s）建一个私密的试，试完删掉，正式的另建。' % next(
        ('%d 条、%s MB' % (d['entries'], mb(d['bytes'])) for d in m['packs'] if d['name'] == '羁绊篇'), '最大那一包'))
    L.append('')
    L.append('1. 工作室里新建模组：类型选卡片专用，绑测试链接那一张卡（试的时候别绑公开那一张），可见性私密，免费。')
    L.append('2. 模组编辑器的世界书那一栏，点“添加”那一排右边最左的导入钮（鼠标停上去写着“从文件导入世界书条目。”），选 奥尔德兰DLC_羁绊篇_%s.json。右上角跳一句导入了几条，对一下是不是上面表里的数。' % m['ver'])
    L.append('3. 点保存。看存不存得上、回列表再点进来条数还对不对。存不上记下报的什么字、等了多久。')
    L.append('4. 只量能装多大的话，到第 3 步就够了。要看醒得对不对：测试链接那一张卡先换成本体（它要还是整卡，羁绊之章本来就在里头，醒了也说明不了什么，还会重两份），再装上这个模组，开两局各问一句：月银纪的局里问希尔妲的个人线；纷争纪二十二张那一路问一位旅伴的章名。那一章开得出来就是醒对了。再开一局不装模组的问同一句，应当不开章，只说她有一段还没讲的旧事（主提示词里管这个的那一句 11-24 改进了源稿，跟下一回打卡一起进卡，这一回切的本体里还没有）。')
    L.append('5. 试完把私密的那一个删了。')
    L.append('')
    L.append('## 正式发')
    L.append('')
    L.append('四包四个模组，一天建得完。发公开模组要有充值记录或积分过十五万，先看一眼账号够不够。')
    L.append('')
    L.append('- 类型：卡片专用，绑公开的那一张（别绑测试链接那一张）。')
    L.append('- 收费：免费。可见性：公开。')
    L.append('- 标题、描述：照下面原样贴，描述头一行是版本号，模组的版本说明里也写同一个号。')
    L.append('- 世界书：照第 2 步导，存完核条数。前置词、后置词、正则、样式都不填（后置词是并进本体还是盖掉本体的还没验过）。')
    L.append('')
    for d in m['packs']:
        L.append('### %s' % d['title'])
        L.append('')
        L.append('文件 %s，%d 条，%s MB。描述：' % (d['file'], d['entries'], mb(d['bytes'])))
        L.append('')
        for l in d['description'].split('\n'):
            L.append('> ' + l)
        L.append('')
    L.append('## 本体')
    L.append('')
    if m['mode'] == '原地':
        L.append('本体写回了原来的名字（切以前的拷成了 _全本.json），后头照旧 split_card.py 拆分批导入、zip_cards.py 打包，最后一步存的是 %s MB。' % mb(m['bodies'][0]['bytes']))
    else:
        L.append('这一回只出文件，没拆分批导入。要导本体时：`python -I -X utf8 底稿/门面/共用/split_card.py %s <输出目录>`，照它出的导入说明一份一份导，最后一步存的是 %s MB（原来 %s MB）。原来的整卡、分批导入都没动。' % (
            m['bodies'][0]['path'], mb(m['bodies'][0]['bytes']), mb(m['full']['bytes'])))
    L.append('')
    L.append('玩家那一头：装了切包以前的整卡又装 DLC 的会重两份，描述里写了一句。')
    L.append('')
    L.append('## 往后')
    L.append('')
    L.append('- 模组更新不会自动推给玩家，所以四包先冻住。每回打卡切完看 清单.json 里的指纹跟 底稿/DLC/发布记录.json 比，一样就不出新版本；变了 make_dlc 会列出增、删、改各几条，攒够了再发新版，发完加 --record 记一回。')
    L.append('- DLC 靠本体的几样接口醒：凭证和底座里的“纪元：X纪N年”、二十二张那一路的“开局时段：第二十二张｜年份：N”、人名地名章名书名。本体改了这几样，旧版 DLC 会醒不了，make_dlc 的模拟会停下来报。')
    L.append('- 落空的引用 %d 处（都是“照某某那一条”的指路话，指不到只少一层细节），清单在 底稿/DLC/落空白名单.json。' % m['hard'])
    L.append('')
    return '\n'.join(L) + '\n'


def main():
    argv = sys.argv[1:]
    also = opt(argv, '--also')
    ver = opt(argv, '--ver', datetime.date.today().strftime('%m-%d'))
    base = opt(argv, '--base', ver)
    out = opt(argv, '--out')
    only = opt(argv, '--packs')
    accept, no_sim, record = '--accept' in argv, '--no-sim' in argv, '--record' in argv
    argv = [a for a in argv if not a.startswith('--')]
    src = argv[0]
    packs = json.load(open(os.path.join(HERE, 'packs.json'), encoding='utf-8'))
    rel_packs = [x for x in packs['_发布'] if not only or x in only.split(',')]
    assert rel_packs, '包名写错了'

    raw = open(src, 'rb').read()
    card = json.loads(raw.decode('utf-8'))
    lb = card['prompt']['lorebook']
    sel = pick(lb, packs, rel_packs)

    # 一、挑出来的两两不相交、每包都有东西
    allc = collections.Counter(i for v in sel.values() for i in v)
    over = [i for i, c in allc.items() if c > 1]
    assert not over, '有条目同时落在两包里：%s' % [RS.title_of(lb[i]) for i in over[:5]]
    empty = [k for k, v in sel.items() if not v]
    assert not empty, '这几包一条也没挑到（输入是不是已经切过了）：%s' % empty
    cut = set(allc)
    print('卡 %s：世界书 %d 条，%.2f MB' % (os.path.basename(src), len(lb), len(raw) / MB))
    for k, v in sel.items():
        print('  %-6s %4d 条' % (k, len(v)))

    # 二、引用扫描（合切一回），跟白名单比
    sc = RS.Scan(card)
    parts = {p: RS.select(lb, packs[p]) for k in rel_packs for p in packs['_发布'][k]['parts']}
    r = sc.run(cut, others=parts)
    hard = sorted({'%s ←→ %s' % (RS.fmt_src(sc, h[0]), h[2]) for h in r['hard']})
    if not os.path.exists(WHITE):
        json.dump(dict(_说明='make_dlc.py 头一回跑时写的：四包合切以后本体里会落空的引用（都是“照某某那一条”的指路话）。往后多出来的 make_dlc 会停，认了加 --accept 重跑。',
                       made=datetime.date.today().isoformat(), refs=hard), open(WHITE, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
        print('落空的引用 %d 处，头一回跑，写进 %s' % (len(hard), os.path.relpath(WHITE, ROOT)))
    else:
        W = json.load(open(WHITE, encoding='utf-8'))
        new = [h for h in hard if h not in set(W['refs'])]
        if new and not accept:
            print('落空的引用比白名单多了 %d 处（认了加 --accept 重跑）：' % len(new))
            for h in new[:40]:
                print('   ', h)
            sys.exit(1)
        if new:
            W['refs'] = sorted(set(W['refs']) | set(new))
            json.dump(W, open(WHITE, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
        gone = len(set(W['refs']) - set(hard))
        print('落空的引用 %d 处，白名单里都有（新认 %d 处；白名单里已经不落空的 %d 处）' % (len(hard), len(new), gone))
    assert not r['always'] and not r['preload'], 'DLC 里有常亮的或者靠 §预载 叫醒的条目，不能切'
    assert not r['cross'], '包和包之间有引用：%s' % r['cross'][:5]

    # 三、模拟醒不醒得了
    sim = None
    if not no_sim:
        sim, ncase = simulate(lb, sel)
        bad = []
        for k, d in sim.items():
            print('  模拟 %-6s %d 条，醒不了 %d 条，触发里拆不出字的 %d 条（主线开局的年份盖不住、逐年扫过的 %d 条）' % (
                k, d['n'], len(d['sleep']), len(d['nolit']), d['swept']))
            bad += [(k, RS.title_of(lb[i])) for i in d['sleep'] + d['nolit']]
        print('  （%d 种凭证和回复底座）' % ncase)
        if bad:
            for k, t in bad[:40]:
                print('    醒不了：〔%s〕%s' % (k, t))
            sys.exit(1)

    # 四、出文件
    made = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    if out:
        dlc_dir = out
    else:
        dlc_dir = os.path.join(os.path.dirname(os.path.abspath(src)), 'DLC')
    os.makedirs(dlc_dir, exist_ok=True)
    for f in os.listdir(dlc_dir):
        if re.match(r'奥尔德兰DLC_.*\.json$', f):
            os.remove(os.path.join(dlc_dir, f))
    full_norm = collections.Counter(SC.norm(e) for e in lb)
    rows = []
    back = collections.Counter()
    for k, idx in sel.items():
        spec = packs['_发布'][k]
        ents = [lb[i] for i in idx]
        bad = [(RS.title_of(e), b) for e in ents for b in SC.check_entry(e)]
        assert not bad, bad[:5]
        mod = collections.OrderedDict(title=spec['title'], description=description(k, spec, len(ents), ver, base), language='zh',
                                      prompt={'lorebook': ents})
        assert 1 <= SC.jlen(mod['title']) <= SC.LIM['title']
        fn = '奥尔德兰DLC_%s_%s.json' % (k, ver)
        txt = dumps(mod).encode('utf-8')
        assert len(txt) <= SC.LIM['wb_file'], '%s 过了 20MB' % fn
        with open(os.path.join(dlc_dir, fn), 'wb') as f:
            f.write(txt)
        o = json.loads(txt.decode('utf-8'))
        assert list(o) == ['title', 'description', 'language', 'prompt'] and list(o['prompt']) == ['lorebook']
        assert len(o['prompt']['lorebook']) == len(ents)
        back.update(SC.norm(e) for e in o['prompt']['lorebook'])
        eras = collections.Counter(era_of(e) or '通用' for e in ents)
        rows.append(dict(name=k, file=fn, title=spec['title'], description=mod['description'], entries=len(ents), bytes=len(txt),
                         sha256=hashlib.sha256(txt).hexdigest(), finger=finger(ents), eras=dict(eras),
                         parts={p: len(RS.select(lb, packs[p]) & set(idx)) for p in spec['parts']}))

    def body_of(c, cutset):
        b = copy.deepcopy(c)
        b['prompt']['lorebook'] = [e for i, e in enumerate(c['prompt']['lorebook']) if i not in cutset]
        return b

    def rel(p):
        try:
            return os.path.relpath(p, ROOT).replace(os.sep, '/')
        except ValueError:          # 不在同一个盘上
            return os.path.abspath(p).replace(os.sep, '/')

    def make_body(c, path_in, which):
        """切一张卡，核完返回要写的东西；两张都核过了才一起写，免得原地切到一半停下、一张切了一张没切。"""
        l2 = c['prompt']['lorebook']
        s2 = pick(l2, packs, rel_packs)
        c2 = set(i for v in s2.values() for i in v)
        assert collections.Counter(SC.norm(l2[i]) for i in c2) == collections.Counter(SC.norm(lb[i]) for i in cut),             '%s 里切下来的跟主卡切下来的不是同一批' % os.path.basename(path_in)
        b = body_of(c, c2)
        assert not SC.check_card(b), SC.check_card(b)
        bn = collections.Counter(SC.norm(e) for e in b['prompt']['lorebook'])
        assert bn + collections.Counter(SC.norm(l2[i]) for i in c2) == collections.Counter(SC.norm(e) for e in l2), '本体加 DLC 跟全本对不上'
        assert {k: v for k, v in b.items() if k != 'prompt'} == {k: v for k, v in c.items() if k != 'prompt'}
        assert {k: v for k, v in b['prompt'].items() if k != 'lorebook'} == {k: v for k, v in c['prompt'].items() if k != 'lorebook'}
        stem = os.path.splitext(os.path.basename(path_in))[0]
        full = None if out else os.path.join(os.path.dirname(os.path.abspath(path_in)), stem + '_全本.json')
        dst = os.path.join(out, stem + '_本体.json') if out else path_in
        raw_in = open(path_in, 'rb').read()
        compact = b', ' not in raw_in[:20000] and b'": ' not in raw_in[:20000]
        txt = (dumps(b) if compact else json.dumps(b, ensure_ascii=False)).encode('utf-8')
        assert len(json.loads(txt.decode('utf-8'))['prompt']['lorebook']) == len(b['prompt']['lorebook'])
        row = dict(which=which, file=os.path.basename(dst), path=rel(dst), entries=len(b['prompt']['lorebook']), bytes=len(txt),
                   sha256=hashlib.sha256(txt).hexdigest(), full_entries=len(l2), full_bytes=len(raw_in))
        return row, path_in, full, dst, txt

    assert back + collections.Counter(SC.norm(e) for i, e in enumerate(lb) if i not in cut) == full_norm
    todo = [make_body(card, src, '薄壳介绍页')]
    if also:
        todo.append(make_body(json.load(open(also, encoding='utf-8')), also, '原介绍页'))
    for row, path_in, full, dst, txt in todo:
        if full:
            shutil.copyfile(path_in, full)      # 原地切：先留全本
        with open(dst, 'wb') as f:
            f.write(txt)
    bodies = [t[0] for t in todo]

    # 五、跟上一回发出去的比
    diff = {}
    if os.path.exists(RECORD):
        R = json.load(open(RECORD, encoding='utf-8'))
        last = R['versions'][-1] if R.get('versions') else None
        if last:
            for d in rows:
                old = last['packs'].get(d['name'])
                if not old:
                    diff[d['name']] = '上一回没发这一包'
                elif old['finger'] == d['finger']:
                    diff[d['name']] = '跟 %s 发的一样，不用出新版本' % last['ver']
                else:
                    ot = set(old.get('titles') or [])
                    nt = {RS.title_of(lb[i]) for i in sel[d['name']]}
                    diff[d['name']] = '跟 %s 发的不一样：增 %d、删 %d、标题没变改了正文或设置的另算' % (last['ver'], len(nt - ot), len(ot - nt))
    else:
        diff = {d['name']: '还没有发布记录（发出去以后加 --record 记一回）' for d in rows}

    manifest = dict(made=made, mode='另出' if out else '原地', ver=ver, base=base, hard=len(hard), regex=len(card.get('assistantRegexReplace') or []),
                    full=dict(file=os.path.basename(src), entries=len(lb), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()),
                    bodies=bodies, packs=rows, diff=diff,
                    sim=None if sim is None else {k: dict(n=v['n'], sleep=len(v['sleep']), nolit=len(v['nolit'])) for k, v in sim.items()})
    with open(os.path.join(dlc_dir, '清单.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    with open(os.path.join(dlc_dir, '说明.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(readme(manifest))
    if record:
        R = json.load(open(RECORD, encoding='utf-8')) if os.path.exists(RECORD) else dict(_说明='发出去的 DLC 每一版的指纹，make_dlc.py --record 写的', versions=[])
        R['versions'].append(dict(ver=ver, base=base, made=made, packs={d['name']: dict(finger=d['finger'], entries=d['entries'], sha256=d['sha256'],
                                                                                         titles=sorted(RS.title_of(lb[i]) for i in sel[d['name']])) for d in rows}))
        json.dump(R, open(RECORD, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
        print('记进了', os.path.relpath(RECORD, ROOT))

    print('\nDLC 写在 %s' % dlc_dir)
    for d in rows:
        print('  %-30s %4d 条 %6.2f MB ｜%s' % (d['file'], d['entries'], d['bytes'] / MB, diff.get(d['name'], '')))
    for b in bodies:
        print('  本体（%s）%-32s %4d 条 %6.2f MB（全本 %d 条 %.2f MB）' % (b['which'], b['file'], b['entries'], b['bytes'] / MB, b['full_entries'], b['full_bytes'] / MB))
    print('本体加各包跟全本一条不多一条不少；本体过了平台的校验；DLC 每条过了条目校验。')


if __name__ == '__main__':
    main()
