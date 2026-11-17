#!/usr/bin/env python3
# 七十九颗金血祝颂写成卡里的条目（11-17）：一纪一份，进 49 命星。
#   python -I -X utf8 底稿/金血祝颂/gen_entries.py      照 稿/ 八份写四个文件（旧的整个盖掉）
# 份1 到份7 那七十二颗进月银纪、纷争纪两份，份8 七神那一版进山铜纪、迷宫纪前传两份。
# 一颗一条，标题 X纪·金血祝颂｜名字，触发是这一纪的门加名字（凭证里写 金血祝颂【名字】，往后状态栏里也有这个名字），
# 条目里不点神亲是谁（叙述不点破）；稿子里的引用块和设计记号★拿掉。
import csv
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
# 11-17 晚改短那一轮换了名字，旧名字照 改名表.tsv 留在触发里当别名（拿旧建档页出的凭证照样叫得醒）
ALIAS = {}
_RT = os.path.join(HERE, '改名表.tsv')
if os.path.exists(_RT):
    for _r in csv.DictReader(open(_RT, encoding='utf-8'), delimiter='\t'):
        if _r['旧名'] and _r['旧名'] != _r['新名']:
            ALIAS.setdefault((_r['份'] == '份8', _r['新名']), []).append(_r['旧名'])
R = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = {
    '月银纪': (os.path.join(R, '月银纪补卷', '金血祝颂.md'), '月银纪', False),
    '纷争纪': (os.path.join(R, '纷争纪', '补卷', '补卷_100_金血祝颂.md'), '纷争纪', False),
    '山铜纪': (os.path.join(R, '山铜纪', '补卷', '补卷_61_金血祝颂.md'), '山铜纪', True),
    '迷宫纪前传': (os.path.join(R, '迷宫纪前传', '补卷', '补卷_82_金血祝颂.md'), '迷宫纪', True),
}
GATE = {'月银纪': '〔月银纪·正则〕', '纷争纪': '〔纷争纪·正则〕', '山铜纪': '〔山铜纪·正则〕', '迷宫纪前传': '〔迷宫纪前传·正则〕'}


def strip(t):
    return re.sub(r'（★）|★', '', t).rstrip()


def parse(p):
    s = open(p, encoding='utf-8').read().replace('\r', '').split('\n## 备注')[0]
    out = []
    heads = list(re.finditer(r'(?m)^### (.+?) \(Passive \| Legend\)\s*$', s))
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(s)
        body = s[m.end():end].split('\n> 条目设置')[0]
        lines = []
        for ln in body.split('\n'):
            ln = strip(ln)
            if not ln.strip():
                continue
            if ln.startswith('> 祝颂：'):
                ln = '- 祝颂：' + ln[len('> 祝颂：'):]
            elif ln.startswith('>'):
                ln = ln.lstrip('> ')
            lines.append(ln)
        out.append((m.group(1).strip(), lines))
    return out


seventy_two, seven = [], []
for p in sorted(glob.glob(os.path.join(HERE, '稿', '份*.md'))):
    (seven if os.path.basename(p).startswith('份8') else seventy_two).extend(parse(p))
assert len(seventy_two) == 72 and len(seven) == 7, (len(seventy_two), len(seven))

for key, (path, folder_era, is_seven) in OUT.items():
    stars = seven if is_seven else seventy_two
    era_word = key if key != '迷宫纪前传' else '迷宫纪'
    w = ['## %s·金血祝颂说明（不进卡）' % era_word, '',
         '这一份是 `底稿/金血祝颂/gen_entries.py` 照 `底稿/金血祝颂/稿/` 出的，别手改，改稿子再跑脚本。'
         '一颗一条，玩家建档时挑了神亲才拿得到，凭证里写 金血祝颂【名字】。条目里不点神亲是谁。'
         '11-17 晚改短那一轮换了名字，旧名字照 `底稿/金血祝颂/改名表.tsv` 留在触发里当别名。', '']
    for name, lines in stars:
        w.append('## %s·金血祝颂｜%s' % (era_word, name))
        w.append('')
        w.append('金血祝颂，Legend 的 Passive，生在这一纪的黄金裔才有。')
        w.extend(lines)
        w.append('')
        rx = '|'.join(re.escape(a).replace('\\，', '，') for a in [name] + ALIAS.get((is_seven, name), []))
        w.append('> 条目设置：文件夹 49·%s｜命星，触发（同时满足）%s、`/%s/`，黑名单 无，范围 用户与助手，深度 2。' % (folder_era, GATE[key], rx))
        w.append('')
    text = '\n'.join(w).replace('## %s·金血祝颂说明（不进卡）' % era_word, '## 设计备注', 1)
    # 设计备注放在页尾才不进卡：挪到最后
    head, rest = text.split('\n', 1)
    note_end = rest.index('\n## ')
    note = head + rest[:note_end]
    text = rest[note_end + 1:] + '\n' + note + '\n'
    open(path, 'w', encoding='utf-8', newline='\r\n').write(text)
    print(key, len(stars), '颗 →', os.path.relpath(path, R))
