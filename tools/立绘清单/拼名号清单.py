# -*- coding: utf-8 -*-
"""把六份（有 _v3 用 _v3，没有用草稿）拼成给立绘会话的交付：
底稿/立绘/史诗战名号/ 下 总表.md + 六份全文；魔神的本体另写 look.json 给 god_list.py。
用法：python3 -I -X utf8 assemble.py 仓库根 草稿目录"""
import sys, os, re, json, shutil
root, src = sys.argv[1], sys.argv[2]
PARTS = [('moon', '月银纪', '月银纪.md'), ('strife_god1', '纷争纪·魔神（离弦、负山、翻页）', '纷争纪_魔神_离弦负山翻页.md'),
         ('strife_god2', '纷争纪·魔神（返青、立边、静光、不退）', '纷争纪_魔神_返青立边静光不退.md'),
         ('strife_other', '纷争纪·魔神以外的对手', '纷争纪_其余对手.md'), ('bronze', '山铜纪', '山铜纪.md'), ('maze', '迷宫纪前传', '迷宫纪前传.md')]
out = os.path.join(root, '底稿/立绘/史诗战名号'); os.makedirs(out, exist_ok=True)
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(root, '底稿/神名/神名表.tsv'), encoding='utf-8')][1:]
demons = [r[2] for r in rows if r[1] == '魔']
PH = re.compile(r'^\s*-\s*(?:\*\*)?(?:隐藏·[^，,【]{1,12}[，,]\s*)?(?:隐藏)?([一二三四五六七八九十]+阶(?:（[^）]*）)?)(?:\*\*)?\s*【([^【】]+)】')
summary = []; look = {}; stats = []
for key, title, fname in PARTS:
    p = os.path.join(src, key + '_v3.md')
    used = p if os.path.exists(p) else os.path.join(src, key + '.md')
    text = open(used, encoding='utf-8').read()
    lines = text.split('\n')
    summary.append(f'## {title}（全文在 {fname}）\n')
    hdr = None; base = None; cur = []; tag = None; n_opp = n_ph = 0
    def flush():
        global n_opp
        if hdr and cur:
            label = re.sub(r'（[^）]{18,}）', lambda m: '（' + m.group(0)[1:17] + '…）', hdr)
            extra = f'（名号栏：{tag}）' if tag and tag not in hdr else ''
            summary.append(f'- {label}{extra}：' + ' → '.join(f'【{n}】' for _, n in cur))
    for line in lines:
        if line.startswith('## '):
            flush(); hdr = None; cur = []; tag = None
            continue
        if line.startswith('### '):
            flush(); hdr = line[4:].strip(); base = hdr; cur = []; tag = None
            continue
        if line.startswith('#### ') and hdr:
            flush(); hdr = re.sub(r'（.*$', '', base) + '·' + line[5:].strip(); cur = []; tag = None
            continue
        mh = re.match(r'^\s*-\s*(?:\*\*)?隐藏(?:\*\*)?[，,：:\s]*([^（。，,：:\s【一二三四五六七八九十]+)', line)
        ms = re.match(r'^\s{2,}-\s*([^\s。（，【]{1,14})(?:（[^）]*）)?。本体', line)
        mb = re.match(r'^\s*-\s*本体（隐藏）', line)
        if hdr and (mh or ms or mb):
            flush(); cur = []; tag = None
            hdr = re.sub(r'（.*$', '', base) + ('·隐藏 ' + mh.group(1) if mh else '·' + ms.group(1) if ms else '·隐藏')
        if hdr is None: continue
        m = re.match(r'^\s*-\s*名号栏[：:]\s*([^。（，\s]+)', line)
        if m: tag = m.group(1)
        m = re.match(r'^\s*-\s*本体[：:]\s*(.*)$', line)
        if m and key.startswith('strife_god'):
            for d in demons:
                if d in hdr and d not in look:
                    look[d] = re.sub(r'（[^）]*[:：][^）]*）', '', m.group(1)).strip()
        mi = re.match(r'^\s*-\s*([^\s。（，【]{1,16})(?:（[^）]*）)?。本体', line)
        if hdr and mi and not PH.match(line) and '【' in line and not line.lstrip().startswith(('- 本体', '- 依据')):
            found = re.findall(r'【([^【】]+)】', line.split('本体', 1)[1])
            if found:
                flush(); cur = []; tag = None
                hdr = re.sub(r'（.*$', '', base) + '·' + mi.group(1)
                for n in found:
                    cur.append(('一阶', n)); n_ph += 1
                n_opp += 1
                continue
        mhd = re.match(r'^\s*-\s*隐藏·([^，,【]{1,12})[，,]\s*[一二三四五六七八九十]+阶', line)
        if hdr and mhd:
            lab = re.sub(r'（.*$', '', base) + '·隐藏 ' + mhd.group(1)
            if hdr != lab:
                flush(); cur = []; tag = None; hdr = lab
        m = PH.match(line)
        if m:
            cur.append((m.group(1), m.group(2))); n_ph += 1
            if len(cur) == 1: n_opp += 1
            for m2 in re.finditer(r'([一二三四五六七八九十]+阶)【([^【】]+)】', line[m.end():]):
                cur.append((m2.group(1), m2.group(2))); n_ph += 1
    flush()
    summary.append('')
    with open(os.path.join(out, fname), 'w', encoding='utf-8') as f:
        f.write(f'<!-- 2026-11-07 阶段名号第二版，{title}。给跑立绘的会话用，不进卡。 -->\n\n' + text)
    stats.append((title, n_opp, n_ph, fname))
json.dump(look, open(os.path.join(src, 'look.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
head = ['# 史诗战对手与阶段名号（给立绘会话用）', '',
        '2026-11-07。四纪（月银纪、纷争纪、山铜纪、迷宫纪前传）里我们在底卡之后新添的史诗战，每一阶一整段名号。用户说这一份不进卡，连同 底稿/立绘/神名清单.md 一起搬到跑立绘的会话里。卡里各页、补卷、状态栏样本一个字没改。', '',
        '怎么读：', '',
        '- 一个对手一行，几阶用 → 连起来。全文那六份里每一阶先写这一阶的样子（身形、颜色、身上的东西、四周变成什么样，带出处 文件:行），再写它在干什么；原文没写、照名号和设定推出来的标了★。每个对手另有一行本体，几阶共用的长相写在那里。',
        '- 名号栏是状态栏和立绘认图用的短名（焚原、亚蒙、葛摩恩照旧），阶段名号是那一阶的整段名号。',
        '- 一个对手几场仗样子不一样的另起一套，编号写成 编号·场次。原来锁着不起名的都起了名字，锁在哪、原句、要是往后改卡怎么改，在各份的锁改写清单里。',
        '- 那一位恶神照旧不点名，它伸进这个世界的手和门有自己的名号。四执政不入场。', '',
        '| 份 | 对手 | 阶段名号 | 全文 |', '|---|---|---|---|'] + [f'| {t} | {a} | {b} | {u} |' for t, a, b, u in stats] + [f'| 合计 | {sum(x[1] for x in stats)} | {sum(x[2] for x in stats)} | |', '']
tail = open(os.path.join(src, 'work/todo_user.md'), encoding='utf-8').read() if os.path.exists(os.path.join(src, 'work/todo_user.md')) else ''
open(os.path.join(out, '总表.md'), 'w', encoding='utf-8').write('\n'.join(head + summary) + '\n' + tail)
print('\n'.join(f'{t}：{a} 个对手，{b} 个名号（{u}）' for t, a, b, u in stats)); print('魔神本体', len(look))
