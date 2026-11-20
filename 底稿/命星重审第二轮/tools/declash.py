#!/usr/bin/env python3
# 命星重审第二轮·铺开（11-20）：给撞了名的星另起名字，换进 收稿/记录.json。
#   python -I -X utf8 底稿/命星重审第二轮/tools/declash.py ask      调一回 Opus 起名，写 收稿/去撞名.json
#   python -I -X utf8 底稿/命星重审第二轮/tools/declash.py apply    照它改 记录.json 里那几颗的标题、【】、能力行
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
W = os.path.join(ROOT, '底稿', '命星重审第二轮')
R = os.path.join(W, '收稿')
sys.path.insert(0, os.path.join(ROOT, 'tools', 'api'))


def taken():
    names = set()
    for r in json.load(open(os.path.join(R, '记录.json'), encoding='utf-8')):
        for s in r['stars']:
            names.add(s['new'])
    for p in ['月银纪史诗/*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md', '纷争纪/纷争纪时段_*.md', '山铜纪/山铜纪时段_*.md', '迷宫纪前传/迷宫纪前传时段_*.md']:
        for f in glob.glob(os.path.join(ROOT, p)):
            names |= set(re.findall(r'^### (\S+) \(', open(f, encoding='utf-8').read(), re.M))
    return names


def ask():
    from claude_api import ask as call
    cl = json.load(open(os.path.join(R, '撞名.json'), encoding='utf-8'))
    items = []
    for i, x in enumerate(cl):
        first = re.split(r'\n\n', x['block'], 3)
        items.append('%d｜%s｜%s｜现在拟的名字【%s】（%s）｜星条开头：%s' % (i, x['who'], re.match(r'### \S+ \((\w+) \| (\w+)\)', x['block']).group(0)[4:], x['new'], x['why'], ' '.join(first[2:3])[:220]))
    sysm = ('你给一张日式西幻 JRPG 跑团卡的命星起名，全程用中文。下面每一行是一颗星，它现在拟的名字跟别人撞了，要另起一个。'
            '起名照异世界轻小说和 JRPG 的路子：高档（Legend、Unique）华丽、带点中二，Epic 像技能列表里一眼认得出的名字，Rare、Normal 白、短，像状态栏上的一行（某某耐性、某某体质、某某之眼也可以，但要跟这个人自己的东西挂上，别泛）。'
            '名字要落在这个人自己的意象上（看星条开头写的出身和那件事），两到六个字，不带标点，不用这几个字：宗、长老、功法、修为、威压、一丝、一抹、量子、能量、系统、月光、月亮。'
            '不能跟下面“已经占用”里的任何一个名字一样，也不能跟这一回别的新名字一样。'
            '只输出 JSON 数组，一项一行：[{"i": 序号, "name": "新名字"}, ...]，前后不加别的话。')
    user = '要改的：\n' + '\n'.join(items) + '\n\n已经占用（不许用）：' + '、'.join(sorted(taken()))
    text, usage = call(user, system=sysm, model='claude-opus-5-5', max_tokens=8000, timeout=900)
    m = re.search(r'\[.*\]', text, re.S)
    out = json.loads(m.group(0))
    json.dump(out, open(os.path.join(R, '去撞名.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('起了', len(out), '个名字', usage)


def apply():
    cl = json.load(open(os.path.join(R, '撞名.json'), encoding='utf-8'))
    nm = {x['i']: x['name'] for x in json.load(open(os.path.join(R, '去撞名.json'), encoding='utf-8'))}
    recs = json.load(open(os.path.join(R, '记录.json'), encoding='utf-8'))
    used = taken()
    n = 0
    for i, x in enumerate(cl):
        new = nm.get(i)
        assert new and new not in used, (i, x['new'], new)
        used.add(new)
        for r in recs:
            if r['page'] == x['page'] and r['who'] == x['who']:
                for s in r['stars']:
                    if s['old'] == x['old'] and s['new'] == x['new']:
                        s['block'] = re.sub(r'^### ' + re.escape(x['new']) + r' \(', '### ' + new + ' (', s['block'], count=1, flags=re.M).replace('【%s】' % x['new'], '【%s】' % new)
                        s['new'] = new
                        r['ability'] = r['ability'].replace('【%s】' % x['new'], '【%s】' % new, 1)
                        n += 1
    json.dump(recs, open(os.path.join(R, '记录.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('改了', n, '颗')


if __name__ == '__main__':
    {'ask': ask, 'apply': apply}[sys.argv[1]]()
