#!/usr/bin/env python3
# 风月版按纪元拆四张（用户 11-25：“风月直接按纪元拆卡，到时候我先把现有的卡替换为迷宫纪，然后发一个月银纪……”），这里出每一张的“外壳”：
# 提示词的风月切法、显示正则（状态栏）、样式（上图床）、简介页（薄壳）、快捷指令。纪元内容的世界书不在这里，另一支打包脚本读这一张、把转好的世界书并进去。
#
#   python -I -X utf8 底稿/风月版/fy_shell.py <纪> [日里全本.json] [--no-push] [--no-check]
#     <纪>：迷宫纪｜月银纪｜纷争纪｜山铜纪｜全部
#     日里全本：默认 out/发布卡_四纪大框/奥尔德兰_四纪大框_原介绍页_全本.json（这一纪的常驻、前置词、快捷指令从它取；显示正则拿它核一遍跟源稿同不同步）
#     --no-push：样式不推图床（卡里的地址写 NOPUSH，只看字数用）；--no-check：不跑规则回归
#   出：out/发布卡_风月_四纪/<纪>/外壳_<纪>.json      一张风月格式的卡，world_bk 里只有提示词切出来的常驻那几条
#       out/发布卡_风月_四纪/<纪>/外壳_<纪>.接口.json   给并世界书的那一支脚本看的：哪几条是常驻、日里全本里哪几条别再并进来、样式地址、各项的数
#       out/发布卡_风月_四纪/<纪>/样式_<纪>.css         推上图床的那一份（加好前缀的），留一份对照
# 各部分在同目录：fy_shell_prompt.py（提示词）、fy_shell_rules.py（显示正则）、fy_shell_css.py（样式和推图床）、fy_shell_descr.py（简介页）、
# fy_shell_check.mjs（规则回归）。做法和验过什么见 外壳_说明.md。日里那一套脚本和源稿这里只读不改。
import copy
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import fy_shell_rules as FR       # noqa: E402
import fy_shell_prompt as FP      # noqa: E402
import fy_shell_css as FC         # noqa: E402
import fy_shell_descr as FD       # noqa: E402

BIG = os.path.join(ROOT, '底稿', '状态栏', '大框')
RILI = os.path.join(ROOT, 'out', '发布卡_四纪大框', '奥尔德兰_四纪大框_原介绍页_全本.json')
TEMPLATE = os.path.join(ROOT, 'out', '发布卡_风月_迷宫纪大框', '奥尔德兰_风月底卡_迷宫纪大框.json')    # 平台的各个字段照这一张（11-04 起导进风月的都是这一套字段名）
OUT = os.path.join(ROOT, 'out', '发布卡_风月_四纪')
# 风月保存时扫屏蔽词，命中就自动下架（11-04 客服回的）。整份文件一个字符一个字符查
BAN_RE = re.compile('rili|扣扣|日历|风月|fengyue', re.I)

# 快捷指令（风月上限十个）：日里那张卡输入框菜单里的，这一张用得上的
CMDS = {
    'maze': ['超程铭刻', '防抢话', '格式刷新', '旧档转换', '开局·迷宫纪前传', '难度', '节奏', '调子', '主角立绘'],
    'moon': ['超程铭刻', '防抢话', '格式刷新', '开局·月银纪', '难度', '节奏', '调子', '主角立绘'],
    'strife': ['超程铭刻', '防抢话', '格式刷新', '开局·纷争纪', '难度', '节奏', '调子', '主角立绘'],
    'bronze': ['超程铭刻', '防抢话', '格式刷新', '开局·山铜纪', '难度', '节奏', '调子', '主角立绘'],
}
# 卡名和简介：迷宫纪那一张顶替线上的卡，照线上的不动；另外三张是新卡，先放一份草稿（照那一纪常驻头一段的话缩的），上架前用户自己改
SERIES = '《奥尔德兰的旅印》按纪元拆成四张卡：月银纪、纷争纪、山铜纪、迷宫纪。换纪元就换卡，上一张的存档拿到下一张里读档接着走。'
HOWTO = '【怎么开始】简介页直接翻开这一纪的书，挑一段主线，建档，复制凭证，回到聊天的输入框里粘贴再发送。不看门面也行，点输入框上头的开局快捷指令。'
META = {
    'moon': ('JRPG日式西幻大世界：奥尔德兰的旅印·月银纪',
             '月银纪，一万零八十一年。\n\n前六千年是魔兽和刀兵的年代，王国一轮轮兴亡，英雄靠斩兽铸名。6007年萨尔维斯从西陆的环山起家，8081年把两块大陆收进一面旗下。10081年登神术那一夜，帝国自己塌了。\n\n'
             '祭火、万兽、诸国、崛起、帝国、魔族之世、末年，七个时段，各有主线、旅伴和一首史诗。\n\n' + SERIES + '这是第一张，往后接纷争纪。\n\n' + HOWTO),
    'strife': ('JRPG日式西幻大世界：奥尔德兰的旅印·纷争纪',
               '纷争纪，一万一千零三十四年。\n\n月银纪10081年归寂月那一夜，穹都城外的大地裂开，影子从裂缝里一个接一个站起来，比塔还高。一道白石长垒从冰原边上砌到南段的尽头，墙的两边打了一万年。\n\n'
               '灰、白石、灯、炮、浮塔、铁狼、号角，七段年月，二十二张牌，一张开一段主线的口子。\n\n' + SERIES + '这是第二张，前头是月银纪，往后接山铜纪。\n\n' + HOWTO),
    'bronze': ('JRPG日式西幻大世界：奥尔德兰的旅印·山铜纪',
               '山铜纪，九百四十七年。\n\n纷争纪10993年止戈，打了一万年的仗停了，正神剩七位，魔神剩九尊。11034年归寂月，灰雨城南门的门洞里多了一只篮子。这一纪世上最大的那些东西都睡了，发条机兵回炉打成了犁。\n\n'
               '犁、长夜、白鸦、黎明、七城、麦，六段年月，一件事立一块碑。\n\n' + SERIES + '这是第三张，前头是纷争纪，往后接迷宫纪。\n\n' + HOWTO),
}
NAME_CN = {'maze': '迷宫纪', 'moon': '月银纪', 'strife': '纷争纪', 'bronze': '山铜纪'}


PROMPT_REV = None


def export_prompts(rev):
    """--prompt-rev=<git 的版本>：主提示词那一套（主提示词/ 下的 .md）不读工作区，照 git 里那一版取。
    另有子任务正在改工作区里那几份、还没收的时候用（比如 --prompt-rev=HEAD），等它收了再不带这一格重跑。
    导到 out/发布卡_风月_四纪/_主提示词_<版本>/，叫 prompt_src 改读它。四纪各自的常驻不走这里，是从日里全本那张卡里取的。"""
    rel = '底稿/状态栏/大框/主提示词'
    r = subprocess.run(['git', 'ls-tree', '-z', '--name-only', rev, rel + '/'], cwd=ROOT, capture_output=True)
    if r.returncode:
        raise SystemExit('git 里取不到 %s 的主提示词：%s' % (rev, r.stderr.decode('utf-8', 'replace')[-200:]))
    names = [n for n in r.stdout.decode('utf-8').split('\0') if n.endswith('.md')]
    assert len(names) >= 8, names
    dst = os.path.join(OUT, '_主提示词_%s' % re.sub(r'\W', '_', rev))
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst)
    for n in names:
        data = subprocess.run(['git', 'show', '%s:%s' % (rev, n)], cwd=ROOT, capture_output=True, check=True).stdout
        with open(os.path.join(dst, os.path.basename(n)), 'wb') as f:
            f.write(data)
    return dst


def src_fp():
    """日里那头的源稿此刻的样子（内容的 sha1 前十二位）：规则和样式三份，主提示词那一套（主提示词/ 下的 .md）。
    另有子任务在改它们的时候，四张外壳要出自同一个样子：出每一张前后各量一回，半路变了就停、叫人重跑；
    量到的写进接口文件和总表，往后看得出这一张是照哪一份出的。（11-25 接手那天两样都撞上过：兜底那一份半路重出了规则，干跑修那一份半路改了主提示词）"""
    out = {}
    for fn in ('rules_convert.json', 'rules_frame.json', 'frame.css'):
        out[fn] = hashlib.sha1(open(os.path.join(BIG, fn), 'rb').read()).hexdigest()[:12]
    h = hashlib.sha1()
    pdir = FP.PSRC.SRC              # 平常是 大框/主提示词；带 --prompt-rev 的时候是从 git 里导出来的那一份
    out['主提示词取自'] = PROMPT_REV or '工作区'
    for fn in sorted(os.listdir(pdir)):
        if fn.endswith('.md') and fn != '说明.md':
            h.update(fn.encode('utf-8'))
            h.update(open(os.path.join(pdir, fn), 'rb').read())
    out['主提示词'] = h.hexdigest()[:12]      # 读它们的两支脚本是开头就载进来的，半路改了也不影响这一回，不量
    return out


def samples(C):
    """规则回归的样本：这一纪的走甲乙两路，别纪的只走甲（前头带 @）；迷宫纪那一张添旧 HTML 回复"""
    def era_of(p):
        m = re.search(r'§底座｜(?:纪元：)?(月银纪|纷争纪|山铜纪|迷宫纪)', open(p, encoding='utf-8').read())
        return {'月银纪': 'moon', '纷争纪': 'strife', '山铜纪': 'bronze', '迷宫纪': 'maze'}.get(m.group(1)) if m else None
    new = sorted(glob.glob(os.path.join(BIG, '样本_*.txt')) + glob.glob(os.path.join(BIG, '第三轮', '样本_*.txt')))
    files = [(p if era_of(p) in C['eras'] else '@' + p) for p in new]
    if C['convert']:
        files += sorted(glob.glob(os.path.join(BIG, '发布', '试写', '*.html')) + glob.glob(os.path.join(BIG, '发布', '试写', '*.txt'))
                        + glob.glob(os.path.join(ROOT, 'moon', 'samples', '*.html')) + glob.glob(os.path.join(ROOT, '底稿', '状态栏', '样张', '样本_*.html')))
    return files


def make(card, rili_card, do_push=True, do_check=True, fp=None, sync='', outroot=None):
    C = FR.CARDS[card]
    key = C['key']
    outdir = os.path.join(outroot or OUT, card)
    os.makedirs(outdir, exist_ok=True)
    print('==== %s ====' % card)
    shell = copy.deepcopy(json.load(open(TEMPLATE, encoding='utf-8')))
    keys0 = list(shell.keys())

    # 一、提示词
    P = FP.build(key, C['eras'], rili_card)
    shell['pre_pt'], shell['ptx'], shell['posttxt'] = P['pre_pt'], P['ptx'], P['posttxt']
    shell['world_bk'] = P['wb']
    pa = P['acct']
    print('提示词：pre_pt %d 字，常驻 %d 条 %s 字，后置词 %d 字；每轮常驻合计 %s 字；改了 %s' % (
        pa['pre_pt'], len(P['wb']), pa['常驻'], pa['后置词'], pa['每轮常驻合计'], '、'.join(pa['改'])))
    for x in pa['提醒']:
        print('  提醒：' + x)

    # 二、显示正则
    fy, ref, names, ra = FR.build(card)
    assert len(fy) <= 800, len(fy)
    shell['regex_rp'] = fy
    print('显示正则：%d 条（转换那一组 %d 条放存、显两份，展开 %d 条），%d 字；别纪的拿掉 %d 条；行内变量换大写 %d 个' % (
        ra['风月'], ra['转换'], ra['展开'], ra['字数'], len(ra['拿掉']), len(names)))
    if do_check:
        dump = os.path.join(outdir, '_回归.json')
        json.dump({'card': card, 'fy': fy, 'ref': ref, 'orig': FR.rili_rules(C['convert']), 'names': names, 'lw': FR.LW_IX[C['lw']], 'eras': C['eras']},
                  open(dump, 'w', encoding='utf-8'), ensure_ascii=False)
        r = subprocess.run(['node', os.path.join(HERE, 'fy_shell_check.mjs'), dump] + samples(C), capture_output=True, text=True, encoding='utf-8')
        os.remove(dump)
        tail = (r.stdout + r.stderr).strip().split('\n')
        print('规则回归：' + tail[-1])
        if r.returncode:
            print('\n'.join('  ' + x[:400] for x in tail[:-1][:12]))
            raise SystemExit('规则回归没过，停')
        ra['回归'] = tail[-1]

    # 三、样式：上图床，卡里只留一行 @import
    css, ca = FC.build(key, C['eras'], names, ref['convert'] + ref['frame'])
    scoped = FC.scoped(css)
    open(os.path.join(outdir, '样式_%s.css' % card), 'w', encoding='utf-8', newline='\n').write(scoped)
    url, pub = FC.publish(key, scoped, do_push)
    shell['built_in_css'] = '@import url("%s");\n' % url
    print('样式：%d 字（加前缀以后 %d 字节），%s；别纪的拿掉 %d 条；%s %s' % (ca['字'], pub['字节'], ca['图'], ca['别纪拿掉'], pub['怎么来的'], url))

    # 四、简介页
    descr, da = FD.build(key)
    shell['descr'] = descr
    print('简介页：薄壳 %d 字，直接翻开 %s，认 %s，图床连不上的退路%s，门面指针第 %s 代' % (da['字'], da['翻开'], da['认'], '有' if da['退路'] else '没有', da['指针'][1:]))

    # 五、快捷指令
    opt = {o['label']: o['value'] for o in rili_card['options']['items']}
    miss = [x for x in CMDS[key] if x not in opt]
    assert not miss, ('日里全本的菜单里没有', miss)
    shell['short_cmds'] = [{'label': x, 'command_text': opt[x]} for x in CMDS[key]]
    assert len(shell['short_cmds']) <= 10

    # 六、卡名和简介
    if key in META:
        shell['name'], shell['abstract'] = META[key]

    # 核对
    assert list(shell.keys()) == keys0
    text = json.dumps(shell, ensure_ascii=False)
    hit = BAN_RE.search(text)
    assert not hit, ('外壳里有平台的屏蔽词', text[max(0, hit.start() - 30):hit.end() + 30])
    assert '日里' not in re.sub('[一-鿿]日里', '', text), '日里当平台的名字出现了'
    assert '<style' not in ''.join(r['replace_text'] for r in fy)
    path = os.path.join(outdir, '外壳_%s.json' % card)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(shell, f, ensure_ascii=False, separators=(',', ':'))
    side = {
        '卡': card, '外壳': os.path.basename(path),
        '日里源稿': dict(fp or src_fp(), 跟日里全本=sync),
        '说明': '外壳里 world_bk 只有提示词切出来的常驻条目（下面列的那几条，文件夹 00·核心运行）。并世界书的时候：这几条照留；日里全本里“别再并进来”的那几条（这一纪的常驻）外壳已经带了，别并第二份。',
        '常驻条目': [{'下标': i, '标题': h, '钥匙': e['key'], '深度': e['depth'], '次序': e['sort'], '字': len(e['value'])} for i, (h, e) in enumerate(zip(P['heads'], P['wb']))],
        '别再并进来': P['heads'][5:],
        '这一张里的纪': C['eras'],
        '认年份的钥匙': ({'前传': FP.KEY_PRE, '1001年': FP.KEY_1001} if key == 'maze' else {}),
        '样式': dict(pub, 地址=url, 字=ca['字']),
        '显示正则': {k: v for k, v in ra.items() if k not in ('拿掉', '改')},
        '显示正则拿掉的': sorted(set('%s（%s）' % (a, b) for a, b in ra['拿掉'])),
        '提示词': pa,
        '简介页': da,
        '快捷指令': CMDS[key],
        '外壳字节': os.path.getsize(path),
    }
    with open(os.path.join(outdir, '外壳_%s.接口.json' % card), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(side, f, ensure_ascii=False, indent=1)
    print('写好了', os.path.relpath(path, ROOT), '%d KB' % (os.path.getsize(path) // 1024))
    return side


def summary():
    """四张外壳眼下的数和地址，从各张的接口文件里读，写 out/发布卡_风月_四纪/外壳_总表.md（每回出完「全部」重写；单要这张表：fy_shell.py 总表）"""
    rows, fps = [], set()
    for card in FR.CARDS:
        p = os.path.join(OUT, card, '外壳_%s.接口.json' % card)
        if not os.path.exists(p):
            continue
        j = json.load(open(p, encoding='utf-8'))
        rx, st, pt = j['显示正则'], j['样式'], j['提示词']
        tot = pt['每轮常驻合计']
        tot = '前传 %d／1001 年 %d' % (tot['前传的局'], tot['1001年的局']) if isinstance(tot, dict) else str(tot)
        rows.append('| %s | %d（转换 %d 条存显各一份，展开 %d） | %s | %d | %s | %s | %d |' % (
            card, rx['风月'], rx['转换'], rx['展开'], tot, st['字节'], '`%s`' % st['地址'] if st['提交'] != 'NOPUSH' else '没推（--no-push 出的，卡里的地址取不到）',
            '取回核过' if st.get('取回核过') else '没核', j['外壳字节']))
        fp = j.get('日里源稿') or {}
        fps.add('，'.join('%s %s' % (k, fp[k]) for k in ('rules_convert.json', 'rules_frame.json', 'frame.css', '主提示词', '主提示词取自') if k in fp))
    text = ('# 风月四张外壳｜眼下的数和样式地址\n\nfy_shell.py 每回出完「全部」重写这一张，别手改。做法见 底稿/风月版/外壳_说明.md。\n\n'
            '| 卡 | 显示正则 | 每轮常驻的字 | 样式字节 | 样式地址（卡的样式格里 @import 的就是它） | 图床 | 外壳字节 |\n|---|---|---|---|---|---|---|\n' + '\n'.join(rows) + '\n\n'
            '照日里那头哪一份源稿出的（内容指纹）：' + '；'.join(sorted(fps)) + ('。\n' if len(fps) == 1 else '。**四张不是照同一份出的，整条命令重跑。**\n'))
    path = os.path.join(OUT, '外壳_总表.md')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    return path, text


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if args and args[0] == '总表':
        print(summary()[1])
        return
    if not args or (args[0] != '全部' and args[0] not in FR.CARDS):
        raise SystemExit('用法：python -I -X utf8 底稿/风月版/fy_shell.py <迷宫纪|月银纪|纷争纪|山铜纪|全部|总表> [日里全本.json] [--no-push] [--no-check] [--prompt-rev=HEAD]')
    rili_p = args[1] if len(args) > 1 else RILI
    rili_card = json.load(open(rili_p, encoding='utf-8'))
    ok, msg = FR.sync_check(rili_card)
    print(('同步：' if ok else '提醒：') + msg)
    n = FP.selftest()
    print('常驻的钥匙自验 %d 种，过了' % n)
    cards = list(FR.CARDS) if args[0] == '全部' else [args[0]]
    global PROMPT_REV
    PROMPT_REV = next((a.split('=', 1)[1] for a in sys.argv if a.startswith('--prompt-rev=')), None)
    if PROMPT_REV:
        FP.PSRC.SRC = export_prompts(PROMPT_REV)
        print('主提示词照 git 里 %s 那一版取（不读工作区）' % PROMPT_REV)
    fp = src_fp()
    print('日里源稿：' + '，'.join('%s %s' % kv for kv in fp.items()))
    # 先出在暂存目录里，这一回要出的几张都出完、源稿没变过，才一起挪进各张的目录：半路停了，原来那几张原样留着，不会一半新一半旧
    stage = os.path.join(OUT, '_暂存')
    shutil.rmtree(stage, ignore_errors=True)
    for c in cards:
        make(c, rili_card, do_push='--no-push' not in sys.argv, do_check='--no-check' not in sys.argv, fp=fp, sync=msg, outroot=stage)
        now = src_fp()
        if now != fp:
            shutil.rmtree(stage, ignore_errors=True)
            raise SystemExit('日里那头的源稿在出外壳的半路上变了（%s）。这一回出的都没有落盘，原来的外壳原样留着。等那一头改完了整条命令重跑。' % '、'.join(k for k in fp if now.get(k) != fp[k]))
    for c in cards:
        os.makedirs(os.path.join(OUT, c), exist_ok=True)
        for fn in os.listdir(os.path.join(stage, c)):
            os.replace(os.path.join(stage, c, fn), os.path.join(OUT, c, fn))
    shutil.rmtree(stage, ignore_errors=True)
    print('落盘：' + '、'.join(cards))
    print('总表：', os.path.relpath(summary()[0], ROOT))


if __name__ == '__main__':
    main()
