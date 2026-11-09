# 次要地点铺开的收稿检查：地点、城邦条目的栏目、活事件、条目设置、年份黑名单，加上份表里的坐标
# 用法：python -I -X utf8 tools/place_check.py 稿子.md [稿子.md …] [--tsv 份表.tsv]
#   稿子里只查 ## X纪·地点｜ 和 ## X纪·城邦｜ 起头的条目（别的条目不管）
#   --tsv：这一份的地点表（栏目照 底稿/地图/铺开/派活说明.md 第五节），有它才查年份窗口、黑名单对不对得上、坐标落没落水
# 报出来的分两样：错（要改）和提醒（看一眼，多半是坐标落在河上、或者用的是别的年代的底图）
import csv
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import yearbl  # noqa: E402

ERA_OF_TITLE = {'月银纪': '月银纪', '纷争纪': '纷争纪', '山铜纪': '山铜纪', '迷宫纪': '前传'}
GATE = {'月银纪': '〔月银纪·正则〕', '纷争纪': '〔纷争纪·正则〕', '山铜纪': '〔山铜纪·正则〕', '前传': '〔迷宫纪前传·正则〕'}
FIELDS = ['哪里', '风貌', '人', '各时段', '活事件', '写法']
# 活事件一件一块：头一行  - **《题》，年份，等着玩家。** 起势；底下四格缩进的  - 人｜、调子｜、一拍｜、二拍｜、玩家在场｜、没人插手｜、往后｜（系列｜可以有）
EV_RE = re.compile(r'^  - \*\*《(.+?)》，(.+?)。\*\* ')
TSV_COLS = ['名字', '时段与年份', '类', '主要还是次要', '1001年叫什么', '别纪的叫法', '位置', '地图x', '地图y', '出处',
            '要说明的', '在的年份', '条目']
IMG = os.path.join(ROOT, '底稿', '地图', '样张')
SALT = os.path.join(ROOT, '底稿', '地图', 'azgaar', '盐海_纷争纪.path.txt')

errs, warns = [], []


def err(t, s):
    errs.append('%s｜%s' % (t, s))


def warn(t, s):
    warns.append('%s｜%s' % (t, s))


def entries(path):
    cur, buf = None, []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        m = re.match(r'^## (\S.*)$', line)
        if m:
            if cur:
                yield cur, buf
            t = m.group(1).strip()
            cur = t if re.match(r'^(月银纪|纷争纪|山铜纪|迷宫纪)·(地点|城邦)｜', t) else None
            buf = []
            continue
        if cur:
            buf.append(line)
    if cur:
        yield cur, buf


def years_in(s):
    return [int(v) for v in re.findall(r'(?<!\d)(\d{1,5})(?=年|到|起|，|）|\)|、|$)', s)]


def check_entry(title, lines):
    era = ERA_OF_TITLE[title.split('·')[0]]
    kind = title.split('·')[1].split('｜')[0]
    text = '\n'.join(lines)
    if not any(l.startswith('【调用】') for l in lines):
        err(title, '没有【调用】')
    got = {}
    for l in lines:
        m = re.match(r'^- (\S{1,4})：', l)
        if m:
            got[m.group(1)] = l
    for f in FIELDS:
        if f not in got:
            err(title, '缺「%s」那一栏' % f)
    if '风貌' in got:
        n = len(got['风貌']) - len('- 风貌：')
        if n < 80 or n > 360:
            warn(title, '风貌 %d 字（定的是一百五到二百五上下）' % n)
    # 活事件：活事件那一栏底下，一件一个块，头一行两格缩进，底下的拍子四格缩进
    ev = []
    on = False
    for l in lines:
        if l.startswith('- 活事件'):
            on = True
            continue
        if on:
            if l.startswith('  - '):
                ev.append([l])
            elif l.startswith('    - ') and ev:
                ev[-1].append(l)
            elif l.startswith('- ') or l.startswith('#'):
                on = False
    if not 1 <= len(ev) <= 3:
        err(title, '活事件 %d 件（要一到三件）' % len(ev))
    for blk in ev:
        e = blk[0]
        m = EV_RE.match(e)
        if not m:
            err(title, '活事件那一行开头要写成「  - **《题》，年份，等着玩家。** 」（或者自己往前走）：%s' % e[:40])
            continue
        lab = m.group(2)
        if not re.search(r'\d', lab) and '全纪' not in lab:
            err(title, '活事件《%s》头一行没写年份' % m.group(1))
        if not re.search(r'(等着玩家|自己往前走)$', lab):
            err(title, '活事件《%s》头一行最后要写等着玩家或者自己往前走' % m.group(1))
        subs = {}
        for s in blk[1:]:
            mm = re.match(r'^    - (\S{1,4})｜', s)
            if not mm:
                err(title, '活事件《%s》底下这一行要写成「    - 名目｜」：%s' % (m.group(1), s[:30]))
                continue
            subs[mm.group(1)] = s
        for k in ('人', '一拍', '玩家在场', '没人插手'):
            if k not in subs:
                err(title, '活事件《%s》缺「%s｜」那一行' % (m.group(1), k))
        for k in ('调子', '往后'):
            if k not in subs:
                warn(title, '活事件《%s》没写「%s｜」' % (m.group(1), k))
        if '系列' in subs and not re.match(r'^    - 系列｜[^，]+，第[一二三四五六七八九十]+段', subs['系列']):
            err(title, '活事件《%s》系列那一行写成「系列｜系列名，第几段，……」' % m.group(1))
        n = sum(len(x) for x in blk)
        if n > 900:
            warn(title, '活事件《%s》%d 字，偏长（定的是四五百字）' % (m.group(1), n))
    if '### 裁定锁' not in text:
        err(title, '没有裁定锁')
    elif '玩家在场' not in text.split('### 裁定锁', 1)[1]:
        warn(title, '裁定锁里没有玩家在场那一句')
    st = [l for l in lines if l.startswith('> 条目设置：')]
    if len(st) != 1:
        err(title, '条目设置 %d 行' % len(st))
        return era, None, ev
    s = st[0]
    fold = '45' if kind == '地点' else '44'
    era_name = {'前传': '迷宫纪'}.get(era, era)
    if not s.startswith('> 条目设置：文件夹 %s·%s｜%s，' % (fold, era_name, kind)):
        err(title, '文件夹要写 %s·%s｜%s' % (fold, era_name, kind))
    if GATE[era] not in s:
        err(title, '触发里没有 %s' % GATE[era])
    trig = re.search(r'〕、`(/.+?/)`', s)
    if not trig:
        err(title, '触发的正则读不出')
    else:
        rx = trig.group(1)[1:-1]
        try:
            re.compile(rx)
        except re.error as x:
            err(title, '触发正则编不过：%s' % x)
        name = title.split('｜', 1)[1]
        short = re.sub(r'[（(].*?[）)]', '', name).split('与')[0]
        if short and not re.search(rx, short) and not re.search(rx, name):
            warn(title, '触发正则认不出条目名「%s」' % name)
    bl = re.search(r'黑名单 (无|`/.+?/`)，', s)
    if not bl:
        err(title, '黑名单读不出（写 无，或者 `/…/`）')
        blrx = None
    else:
        blrx = None if bl.group(1) == '无' else bl.group(1)[2:-2]
    if '范围 用户与助手' not in s or not s.rstrip().endswith('深度 2。'):
        err(title, '范围写用户与助手，深度 2')
    return era, blrx, ev


def salt_poly():
    if not os.path.exists(SALT):
        return None
    nums = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', open(SALT, encoding='utf-8').read())]
    return list(zip(nums[0::2], nums[1::2]))


def inside(poly, x, y):
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
            c = not c
        j = i
    return c


_img = {}


def water(name, x, y):
    try:
        from PIL import Image
    except ImportError:
        return None
    if name not in _img:
        _img[name] = Image.open(os.path.join(IMG, name)).convert('RGB')
    im = _img[name]
    n = 0
    for dx in (-5, 0, 5):
        for dy in (-5, 0, 5):
            px, py = int(x * 1.6) + dx, int(y * 1.6) + dy
            if not (0 <= px < im.size[0] and 0 <= py < im.size[1]):
                n += 1
                continue
            r, g, b = im.getpixel((px, py))
            if b - r >= 35 and r <= 180:
                n += 1
    return n >= 6


def maps_for(era, wins):
    out = []
    for a, b in wins:
        if era == '月银纪' or (era == '纷争纪' and a <= 1087):
            out.append('月银纪_萨尔维斯末年_样张.jpg')
        if era == '纷争纪' and b >= 1088 and a <= 4500:
            out.append('纷争纪_炮的年月_样张.jpg')
        if era == '纷争纪' and b >= 4501:
            out.append('纷争纪_浮塔的年月_样张.jpg')
        if era == '山铜纪':
            out.append('山铜纪_麦的年月_样张.jpg')
        if era == '前传':
            out.append('海与水路_1001_试样.jpg')
    return sorted(set(out))


def parse_wins(s):
    s = s.strip()
    if s in ('全纪', ''):
        return None
    wins = []
    for part in re.split(r'[,，、 ]+', s):
        m = re.fullmatch(r'(\d+)(?:-(\d+))?', part)
        if not m:
            raise ValueError(part)
        wins.append((int(m.group(1)), int(m.group(2) or m.group(1))))
    return wins


def main():
    args = sys.argv[1:]
    tsv = None
    if '--tsv' in args:
        i = args.index('--tsv')
        tsv = args[i + 1]
        del args[i:i + 2]
    found = {}
    for p in args:
        for t, lines in entries(p):
            if t in found:
                err(t, '同一个标题写了两回')
            found[t] = check_entry(t, lines)
    if not found:
        print('一条地点、城邦条目也没找到')
    if tsv:
        rows = list(csv.DictReader(open(tsv, encoding='utf-8'), delimiter='\t'))
        if rows:
            miss = [c for c in TSV_COLS if c not in rows[0]]
            if miss:
                err(os.path.basename(tsv), '份表少了几栏：%s' % '、'.join(miss))
        titled = {}
        for r in rows:
            t = (r.get('条目') or '').strip()
            if t:
                titled.setdefault(t, []).append(r)
        salt = salt_poly()
        for t, (era, blrx, ev) in found.items():
            rs = titled.get(t)
            if not rs:
                err(t, '份表里没有一行的「条目」写它')
                continue
            for r in rs:
                try:
                    wins = parse_wins(r.get('在的年份', ''))
                except ValueError as x:
                    err(t, '「%s」那一行的在的年份看不懂：%s' % (r['名字'], x))
                    continue
                try:
                    x, y = float(r['地图x']), float(r['地图y'])
                except ValueError:
                    err(t, '「%s」那一行没有坐标' % r['名字'])
                    continue
                if not (0 <= x <= 2200 and 0 <= y <= 1400):
                    err(t, '「%s」坐标出了图：%s, %s' % (r['名字'], x, y))
                    continue
                for img in maps_for(era, wins or [(yearbl.ERAS[era]['lo'], yearbl.ERAS[era]['end'])]):
                    w = water(img, x, y)
                    if w:
                        warn(t, '「%s」(%s, %s) 在 %s 上落在水里' % (r['名字'], x, y, img))
                if salt and era in ('纷争纪', '山铜纪') and inside(salt, x, y):
                    lo = min(a for a, b in wins) if wins else 1
                    if era == '山铜纪' or (wins and max(b for a, b in wins) >= 1088):
                        warn(t, '「%s」(%s, %s) 在 1088 年以后的盐海里' % (r['名字'], x, y))
            # 黑名单和窗口：取这一条的第一行（主行）的窗口
            main_row = rs[0]
            try:
                wins = parse_wins(main_row.get('在的年份', ''))
            except ValueError:
                continue
            e = yearbl.ERAS[era]
            want = [] if wins is None else [yy for yy in range(e['lo'], e['end'] + 1)
                                            if not any(a <= yy <= b for a, b in wins)]
            got = [] if blrx is None else yearbl.blocked_years(era, blrx)
            if got != want:
                err(t, '黑名单挡的年份跟份表的在的年份对不上：挡了 %s，该挡 %s（拿 tools/yearbl.py 重出）' % (
                    yearbl.spans(got), yearbl.spans(want)))
            if wins:
                for blk in ev:
                    m = EV_RE.match(blk[0])
                    if not m:
                        continue
                    for yy in years_in(m.group(2)):
                        if not any(a - 30 <= yy <= b + 30 for a, b in wins):
                            err(t, '活事件「%s」的 %d 年不在这一处在的年份里' % (m.group(1), yy))
    for s in errs:
        print('错｜' + s)
    for s in warns:
        print('提醒｜' + s)
    print('条目 %d 条，错 %d，提醒 %d' % (len(found), len(errs), len(warns)))
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
