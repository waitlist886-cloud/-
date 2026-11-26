#!/usr/bin/env python3
# 风月版打包：外壳（提示词、常驻、显示正则、样式、简介页，fy_shell.py 出的）加转好的世界书（fy_lore.py 出的），出能导的东西。
# 用法（仓库根上）：
#   python -I -X utf8 底稿/风月版/build_fy_era.py <纪…> [--all] [--src 全本.json] [--base core|std|all] [--step N]
#     纪：pre｜now｜moon｜strife｜bronze，也认 前传｜此刻｜迷宫纪前传｜迷宫纪此刻｜月银纪｜纷争纪｜山铜纪；不写就是五张（11-25 夜迷宫纪拆成前传、此刻两张）
#     --all   一条龙：先 fy_lore.py 转世界书，再 fy_sim.py 对账（带锚的消息上有不一样的就停），再打包。不加就只打包（读现成的 世界书_转换.json）
#     --step  传给 fy_sim.py（逐年扫每 N 年取一年，调试用）
# 出在 out/发布卡_风月_四纪/<纪名>/导入/：
#   <纪名>_小底卡.json            外壳，world_bk 里只有常驻那几条。先导这一张
#   <纪名>_世界书_第N份.json      {"world_book":[…]}，世界书的导入模板，一份不过 4.6MB（探针第四轮的写法和大小），照号一份一份导
#   <纪名>_整卡.json              外壳加全部世界书。整张不过 11MB 才出（风月整卡导入 11.3MB 导得进、12.6MB 超时）
#   清单.json、导入说明.md
# 外壳没出来的时候（out/发布卡_风月_四纪/<纪名>/外壳_<纪名>.json 不在），拿 11-04 那一张风月卡当外壳把流水线跑通（只留它的常驻条目），说明里会写明这是垫的。
# 核：风月世界书一张卡最多 5000 条（常驻加世界书）；一条正文不过四万字；钥匙过 RE2 的检查；整份文件扫屏蔽词；外壳里已经有的常驻不并第二份。
import collections
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fy_gate as G     # noqa: E402
import fy_lore as L     # noqa: E402

ROOT = G.ROOT
PART = int(4.6 * 1048576)
WHOLE = 11 * 1048576
FALLBACK = os.path.join(ROOT, 'out', '发布卡_风月_迷宫纪大框', '奥尔德兰_风月底卡_迷宫纪大框.json')
NAMES = {c: v['dir'] for c, v in G.CARDS.items()}      # 目录名，也是导入包里文件名的头（迷宫纪两张的纪名一样，目录名不一样）
FIELDS = ['group', 'match_type', 'key', 'key_region', 'value_type', 'value', 'value_configs', 'value_region', 'sort', 'depth', 'probability', 'enable']


def dumps(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':'))


def title(v):
    return (v or '').lstrip().split('\n', 1)[0][:60]


def load_shell(card):
    era = NAMES[card]
    d = os.path.join(L.OUT, era)
    p = os.path.join(d, '外壳_%s.json' % era)
    if os.path.exists(p):
        raw = open(p, 'rb').read()
        shell = json.loads(raw.decode('utf-8'))
        ip = os.path.join(d, '外壳_%s.接口.json' % era)
        iface = json.load(open(ip, encoding='utf-8')) if os.path.exists(ip) else {}
        iface['_sha256'] = hashlib.sha256(raw).hexdigest()
        iface['_mtime'] = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d %H:%M')
        return shell, iface, os.path.relpath(p, ROOT).replace(os.sep, '/'), False
    shell = json.load(open(FALLBACK, encoding='utf-8'))
    shell['world_bk'] = [e for e in shell['world_bk'] if e['key'].startswith('[\\s\\S]')]
    return shell, {}, os.path.relpath(FALLBACK, ROOT).replace(os.sep, '/') + '（垫的）', True


def build(card):
    era = NAMES[card]
    d = os.path.join(L.OUT, era)
    conv = json.load(open(os.path.join(d, '世界书_转换.json'), encoding='utf-8'))
    rep = json.load(open(os.path.join(d, '转换报告.json'), encoding='utf-8'))
    sim_p = os.path.join(d, '对账报告.json')
    sim = json.load(open(sim_p, encoding='utf-8')) if os.path.exists(sim_p) else None
    shell, iface, shell_from, fallback = load_shell(card)
    res = list(shell.get('world_bk') or [])
    assert all(list(e) == FIELDS for e in res), '外壳里世界书条目的字段跟风月的对不上'
    skip_titles = set(iface.get('别再并进来') or [])
    have_val = {e['value'] for e in res}
    have_title = {title(e['value']) for e in res}
    lore, dup = [], []
    for x in conv['entries']:
        if x['_title'] in skip_titles or x['value'] in have_val or (fallback and x['_title'] in have_title):
            dup.append(x['_title'])
            continue
        e = collections.OrderedDict((k, x[k]) for k in FIELDS)
        lore.append(e)
    probs = []
    total = len(res) + len(lore)
    if total > L.LIMIT_N:
        probs.append('世界书一共 %d 条，过了风月 5000 条的上限' % total)
    for e in lore:
        bad = G.re2_problems(e['key'])
        if bad:
            probs.append('RE2 不认：%s %s' % (title(e['value']), bad))
        if len(e['value']) > L.LIMIT_VALUE:
            probs.append('正文过四万字：%s' % title(e['value']))
    # 切份
    parts, cur, size = [], [], 16
    for e in lore:
        n = len(dumps(e).encode('utf-8')) + 1
        if cur and size + n > PART:
            parts.append(cur)
            cur, size = [], 16
        cur.append(e)
        size += n
    if cur:
        parts.append(cur)
    out = os.path.join(d, '导入')
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if re.match(r'.*_(?:小底卡|整卡|世界书_第\d+份)\.json$', f) or f in ('清单.json', '导入说明.md'):
            os.remove(os.path.join(out, f))
    files = []

    def put(name, obj, what, n):
        txt = dumps(obj).encode('utf-8')
        m = L.BAN_RE.search(txt.decode('utf-8'))
        if m:
            t = txt.decode('utf-8')
            probs.append('屏蔽词：%s 里有“%s”' % (name, t[max(0, m.start() - 12):m.end() + 12]))
        with open(os.path.join(out, name), 'wb') as f:
            f.write(txt)
        files.append(dict(file=name, what=what, entries=n, bytes=len(txt), sha256=hashlib.sha256(txt).hexdigest()))
        return len(txt)
    base_name = '%s_小底卡.json' % era
    put(base_name, shell, '小底卡（外壳，常驻 %d 条）' % len(res), len(res))
    acc = len(res)
    for k, p in enumerate(parts, 1):
        folders = list(dict.fromkeys(e['group'] for e in p))
        acc += len(p)
        b = put('%s_世界书_第%d份.json' % (era, k), {'world_book': p}, '世界书第 %d 份（%s 到 %s）' % (k, folders[0], folders[-1]), len(p))
        files[-1]['acc'] = acc
        assert b <= PART + 4096, (k, b)
    whole = dict(shell)
    whole['world_bk'] = res + lore
    wb = len(dumps(whole).encode('utf-8'))
    whole_name = None
    if wb <= WHOLE and not probs:
        whole_name = '%s_整卡.json' % era
        put(whole_name, whole, '整卡（外壳加全部世界书）', total)
    kc = [len(e['key']) for e in lore]
    man = dict(card=card, era=era, made=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), shell=shell_from, shell_fallback=fallback,
               shell_sha256=iface.get('_sha256'), shell_mtime=iface.get('_mtime'), src=rep['src'], src_sha256=rep['src_sha256'],
               base=rep['base'], resident=len(res), lore=len(lore), total=total, dup_skipped=dup, parts=len(parts), whole=whole_name, whole_bytes=wb,
               regex_rp=len(shell.get('regex_rp') or []), css_chars=len(shell.get('built_in_css') or ''), descr_chars=len(shell.get('descr') or ''),
               key_max=max(kc or [0]), key_over1200=sum(k > 1200 for k in kc), skipped=len(rep['skipped']), weighted=rep['weighted'], split=rep['split'],
               sim=None if not sim else dict(tests=sim['tests'], anchored_diff=len(sim['anchored_diff']), bare_diff=len(sim['bare_diff']), re2_bad=len(sim['re2_bad']),
                                             bare_expected_entries=sim['bare_expected_entries'], step=sim['step'], made=sim['made']),
               files=files, problems=probs)
    with open(os.path.join(out, '清单.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, '导入说明.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(readme(man))
    mb = lambda b: b / 1048576
    print('【%s】外壳 %s；常驻 %d ＋ 世界书 %d ＝ %d 条；小底卡 %.2f MB，世界书 %d 份（%s MB）；整卡 %.2f MB%s' % (
        era, shell_from, len(res), len(lore), total, mb(files[0]['bytes']), len(parts), '、'.join('%.2f' % mb(x['bytes']) for x in files[1:1 + len(parts)]),
        mb(wb), '，出了' if whole_name else '，过 11MB 没出'))
    if dup:
        print('   外壳已经带了、没并第二份的：', '、'.join(dict.fromkeys(dup)))
    for p in probs[:20]:
        print('   ✗', p)
    return man


def legacy_note(m):
    """此刻那一张（legacy）：怎么覆盖线上那张已经发布的 1001 年底卡、老玩家的存档怎么办"""
    if not G.CARDS[m['card']].get('legacy'):
        return []
    whole = m['whole']
    n_old = len(json.load(open(FALLBACK, encoding='utf-8'))['world_bk'])      # 线上那张（11-04 发的）世界书的条数
    W = ['## 覆盖线上那张已经发布的卡', '',
         '这一张是迷宫纪1001年那一局的重制版，拿去覆盖线上已经发布的那张 1001 年的卡（卡名换成“（重制版）【日式西幻·JRPG】奥尔德兰年代记·迷宫纪·此刻｜迎长风推开门扉”；封面、背景图、标签照线上那张；简介前头那几行和“这张卡里有什么”那一串照线上那张，开头那一大段重写了，添了一段说是重制版）。', '',
         '1. **先把线上那张导出一份留底**，存好。下面哪一步不对，拿它导回去就是原样。',
         '2. 照上面在一张私有的新卡上走一遍，导得进、开得了局、简介页翻得开，再动线上那张。',
         ('3. 到线上那张卡的编辑页，导入 `%s` 覆盖。' % whole + '导完看一眼世界书，应当正好是 **%d 条**。条数对不上（原来那 %d 条还在、重了份），清掉世界书，照分份的路子重导。' % (m['total'], n_old)) if whole else
         '3. 到线上那张卡的编辑页，导入 `%s` 覆盖，再看世界书：要是原来那 %d 条还在，先清掉，只剩常驻 %d 条，再照上面第 2 步一份一份导。' % (m['files'][0]['file'], n_old, m['resident']),
         '4. 保存、发布。卡的地址和收藏照旧（覆盖的是同一张卡）。', '',
         '**线上那张卡上你自己改过的地方这一包没有并进来**：提示词里拿掉的身份那一句和成年那两节、九位旅伴体态那一行（11-08 起是 merge_user_fy.py 照条目下标并的）。'
         '新卡的提示词和世界书换了一套，那支脚本套不上，没有硬并。要的话覆盖以后在新卡上再改一回：提示词在前置提示和世界书「00·核心运行」那几条常驻里，旅伴在「15·人物与旅途同行」那一组。'
         '改之前看一眼留底的那一份，照着改。', '',
         '## 老玩家的存档', '',
         '- 存档跟着卡走，覆盖以后老玩家的对话都还在，接着聊就行。',
         '- 库里的旧回复是带标签的老样子（HTML 状态栏），这一张的显示正则会把它们换成新的大框显示；发给模型的历史里还是原样，后置词里写了不要照抄。',
         '- 头一轮让模型照新样子重写状态：点快捷指令里的「旧档转换」（跟「格式刷新」是同一条规矩）。数值、物品、人物、任务、关系、记忆照单承接，只重建版面。',
         '- 老建档页交的凭证（头一行没有“纪元：”、认“命途已确认”）这一张照旧认，算 1001 年的局。',
         '- 存档要是在迷宫纪前传那一段（底座上的纪元是迷宫纪 2 到 1000 年），这一张里没有前传的内容了，换到迷宫纪前传那一张卡里读档。', '']
    return W


def pre_note(m):
    """前传那一张：跟此刻那一张怎么分"""
    if m['card'] != 'pre':
        return []
    return ['## 跟迷宫纪1001年那一张怎么分', '',
            '- 这一张只有迷宫纪前传（2 到 1000 年）。底卡里迷宫纪1001年那个世界的历史、神祇、城市、凡世至强、公会这些只在迷宫纪1001年那一张里，这一张只带规则核（建档、数值位阶、命路、命星、种族、职业、货币装备、怪物、旅行、队伍、委托和几样功能）。',
            '- 前传写到 1000 年为止。局玩过了 1000 年，换到迷宫纪1001年那一张卡里读档接着走。山铜纪那一张的局玩过了迷宫纪元年，转过年来的迷宫纪 2 年到这一张来。', '']


def readme(m):
    mb = lambda b: '%.1f' % (b / 1048576)
    era = m['era']
    W = ['# %s 风月版 导入说明' % era, '',
         '%s 打的，build_fy_era.py 自己写的。世界书一共 %d 条（常驻 %d、内容 %d），风月上限 5000。' % (m['made'], m['total'], m['resident'], m['lore']),
         '外壳用的是 %s（%s 出的那一份）；外壳后来重出过的话，这一包要重打（见 底稿/风月版/说明.md「怎么重打」）。' % (m['shell'], m.get('shell_mtime') or '时间不详'), '']
    if m['shell_fallback']:
        W += ['**这一份的外壳是垫的**（11-04 那一张风月卡，只留了它的常驻），提示词、状态栏、简介页都不是这一纪的，只能拿来看导不导得进。外壳出来以后重打。', '']
    if m['problems']:
        W += ['**有没过的检查，先别导：**'] + ['- ' + p for p in m['problems'][:20]] + ['']
    W += ['## 照这个导（手机上也一样）', '',
          '先在一张**私有的新卡**上走一遍，没问题再动线上的。', '',
          '1. 新建卡，导入 `%s`（%s MB），保存。这时候世界书里应当只有常驻 %d 条；要是导在一张旧卡上、旧的条目还在，先清掉再往下，免得重份。' % (
              m['files'][0]['file'], mb(m['files'][0]['bytes']), m['resident']),
          '2. 进这张卡的世界书，用“导入模板”那个入口，照号一份一份导。**导一份，对一下条数，存一回**，再导下一份：', '',
          '| 导哪一份 | 这一份 | 大小 | 导完世界书一共 |', '|---|---|---|---|']
    for x in m['files'][1:1 + m['parts']]:
        W.append('| `%s` | %d 条 | %s MB | %d 条 |' % (x['file'], x['entries'], mb(x['bytes']), x['acc']))
    W += ['', '3. 全导完，关掉编辑器重新打开这张卡，世界书应当是 **%d 条**。少了就是哪一份没存住，从条数对不上的那一份接着导。' % m['total'],
          '4. 开一局走两三轮：从简介页建档，看头一轮底座那一行写没写“纪元：%s某年”，状态栏出不出来。' % G.CARDS[m['card']]['name'], '']
    if m['whole']:
        W += ['整张不过 11MB，也出了一张 `%s`（%s MB），嫌一份份导麻烦可以直接导它；导不进（超时）就照上面分份的来。' % (m['whole'], mb(m['whole_bytes'])), '']
    else:
        W += ['整张 %s MB，过了风月整卡导入的线（11.3MB 导得进、12.6MB 超时），所以只有分份这一条路。' % mb(m['whole_bytes']), '']
    W += legacy_note(m) + pre_note(m)
    W += ['## 要知道的', '',
          '- **分份导累计到这么大存不存得住，还没有在风月上确认过。** 探针第四轮一份份导到第五份才碰上 5000 条的线，前四份（3870 条、连底卡 22MB 上下）每一份存没存住当时没有回话。这一张导完是 %d 条、连小底卡 %s MB。哪一步存不上，记下是第几份、报什么。' % (
              m['total'], mb(sum(x['bytes'] for x in m['files'][:1 + m['parts']]))),
          '- 钥匙最长 %d 字，过 1200 字的 %d 条。探针里导进去过的最长是 1225 字；更长的平台收不收、跑不跑得动没试过。' % (m['key_max'], m['key_over1200']),
          '- 没进卡的 %d 条里 %d 条是加权条目（命运骰、起名性格身形三条种子、路上天气差事的骰表），风月的世界书没有“几样里抽一样”的写法。' % (m['skipped'], m['weighted']),
          '- 风月的钥匙是照“日里什么时候醒、这里就什么时候醒”转的。' + (
              '对账（%s）：比了 %d 回，带锚的消息上不一样 %d 条，裸打的一句上不一样 %d 条（另有 %d 条是认这一纪的钥匙拿掉以后玩家一提就醒，日里要慢一轮）。' % (
                  m['sim']['made'], m['sim']['tests'], m['sim']['anchored_diff'], m['sim']['bare_diff'], m['sim']['bare_expected_entries']) if m['sim'] else '对账还没跑。'),
          '- 真页面、真模型没上过。细目见 底稿/风月版/说明.md，逐条的清单在上一层的 转换清单.md、对账.md。', '']
    return '\n'.join(W) + '\n'


def main():
    argv = sys.argv[1:]

    def opt(k, dflt=None):
        if k in argv:
            i = argv.index(k)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return dflt
    src, base, step = opt('--src'), opt('--base'), opt('--step')
    full = '--all' in argv
    cards = [G.card_of(a) for a in argv if not a.startswith('--')] or list(G.CARDS)
    if full:
        py = [sys.executable, '-I', '-X', 'utf8']
        extra = (['--src', src] if src else [])
        r = subprocess.run(py + [os.path.join(HERE, 'fy_lore.py')] + cards + extra + (['--base', base] if base else []))
        if r.returncode:
            sys.exit('fy_lore.py 没过，停')
        r = subprocess.run(py + [os.path.join(HERE, 'fy_sim.py')] + cards + extra + (['--step', step] if step else []))
        if r.returncode:
            sys.exit('fy_sim.py：带锚的消息上有不一样的（或者钥匙 RE2 不认），停。看各纪的 对账.md')
    bad = 0
    for card in cards:
        bad += len(build(card)['problems'])
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
