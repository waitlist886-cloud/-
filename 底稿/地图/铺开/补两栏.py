# 乙·给已有的地点、城邦条目补「风貌」「活事件」两栏：各份把要补的写进自己的稿子，这个脚本照稿子插回原条目
# 用法：python -I -X utf8 底稿/地图/铺开/补两栏.py 稿子.md [稿子.md …] [--apply]
#   不加 --apply 只查不写：每一块找不找得到原条目、原条目是不是已经有这两栏、活事件的格式对不对。
#
# 稿子的写法（一条原条目一块）：
#   ## 月银纪·补两栏｜名字
#   > 补到｜文件路径｜原条目的标题行（照原文件那一行抄，三批旧稿写 === 名字，补卷写 ## 月银纪·地点｜名字）
#   【调用】……（可以没有：原条目的【调用】要放宽才写，写整句，替换原来那一行）
#   - 风貌：……
#   - 活事件：
#     - **《题》，年份，等着玩家。** ……
#       - 人｜……
#       …
#   别的话（备注）写在稿子末尾「## 设计备注」以后。
#
# 插在哪：风貌接在原条目「什么地方」（或「什么样」）那一栏后头，没有就接在「哪里」后头；
#         活事件接在「各时段」那一栏后头，没有就接在「写法」前头。原条目别的一个字不动。
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import place_check as pc  # noqa: E402

args = sys.argv[1:]
apply = '--apply' in args
files = [a for a in args if a != '--apply']
errs = []


def blocks(path):
    text = open(path, encoding='utf-8').read()
    text = text.split('\n## 设计备注', 1)[0]
    parts = re.split(r'\n(?=## 月银纪·补两栏｜)', '\n' + text)
    for p in parts:
        p = p.strip('\n')
        if not p.startswith('## 月银纪·补两栏｜'):
            continue
        yield p.split('\n')


def field_span(lines, i):
    # 从第 i 行（- X：）往下，属于这一栏的行到哪里为止（不含）
    j = i + 1
    while j < len(lines):
        l = lines[j]
        if not l.strip():
            break
        if l.startswith('- ') or l.startswith('#') or l.startswith('>') or l.startswith('【') or l.startswith('==='):
            break
        j += 1
    return j


def entry_span(lines, title):
    idx = [k for k, l in enumerate(lines) if l.rstrip() == title.rstrip()]
    if len(idx) != 1:
        return None
    a = idx[0]
    old = title.startswith('=== ')
    b = a + 1
    while b < len(lines):
        l = lines[b]
        if old and l.startswith('=== '):
            break
        if not old and (l.startswith('## ') and not l.startswith('### ')):
            break
        b += 1
    return a, b


def check_block(name, blk):
    head = blk[0]
    meta = [l for l in blk if l.startswith('> 补到｜')]
    if len(meta) != 1:
        errs.append('%s｜要有一行「> 补到｜文件｜原标题」' % head)
        return None
    _, f, title = meta[0].split('｜', 2)
    call = [l for l in blk if l.startswith('【调用】')]
    fm = [k for k, l in enumerate(blk) if l.startswith('- 风貌：')]
    ev = [k for k, l in enumerate(blk) if l.startswith('- 活事件')]
    if len(fm) != 1 or len(ev) != 1:
        errs.append('%s｜风貌、活事件各要一栏' % head)
        return None
    fm_lines = blk[fm[0]:field_span(blk, fm[0])]
    ev_end = ev[0] + 1
    while ev_end < len(blk) and (blk[ev_end].startswith('  ') or not blk[ev_end].strip()):
        ev_end += 1
    ev_lines = blk[ev[0]:ev_end]
    while ev_lines and not ev_lines[-1].strip():
        ev_lines.pop()
    # 活事件的格式借 place_check 那一套
    pc.errs.clear()
    pc.warns.clear()
    fake = ['【调用】x', '- 哪里：x', fm_lines[0], '- 人：x', '- 各时段：x'] + ev_lines + ['- 写法：x', '', '### 裁定锁', '- 玩家在场插手了，往后照玩家做的事走。']
    pc.check_entry('月银纪·地点｜' + name, fake)
    for s in pc.errs:
        if '条目设置' in s:
            continue
        errs.append(s)
    for s in pc.warns:
        print('提醒｜' + s)
    return f.strip(), title.strip(), (call[0] if call else None), fm_lines, ev_lines


def main():
    plan = {}
    for p in files:
        for blk in blocks(p):
            name = blk[0].split('｜', 1)[1].strip()
            r = check_block(name, blk)
            if r:
                plan.setdefault(r[0], []).append((name,) + r[1:])
    done = 0
    for f, items in plan.items():
        path = os.path.join(ROOT, f)
        if not os.path.exists(path):
            errs.append('%s｜文件不在' % f)
            continue
        lines = open(path, encoding='utf-8').read().split('\n')
        for name, title, call, fm_lines, ev_lines in items:
            sp = entry_span(lines, title)
            if not sp:
                errs.append('%s｜在 %s 里找不到（或者不止一处）标题行：%s' % (name, f, title))
                continue
            a, b = sp
            body = lines[a:b]
            if any(l.startswith('- 风貌：') or l.startswith('- 活事件') for l in body):
                errs.append('%s｜原条目已经有风貌或活事件了，别补两回' % name)
                continue
            fields = {}
            for k, l in enumerate(body):
                m = re.match(r'^- ([^：\s]{1,8})：', l)
                if m and m.group(1) not in fields:
                    fields[m.group(1)] = k
            # 风貌接在讲这一处什么样的那一栏后头；三批旧稿的城邦写的是所在、城里什么样，城区写的是这座城的形状
            anchor = next((fields[k] for k in ('什么地方', '什么样', '什么样子', '城里什么样', '这座城的形状', '哪里', '所在') if k in fields), None)
            if anchor is None:
                errs.append('%s｜原条目找不到哪里、所在、什么地方、什么样、城里什么样那一栏，风貌没处接' % name)
                continue
            fm_at = field_span(body, anchor)
            if '各时段' in fields:
                ev_at = field_span(body, fields['各时段'])
            elif '写法' in fields:
                ev_at = fields['写法']
            else:
                errs.append('%s｜原条目找不到各时段、写法那一栏，活事件没处接' % name)
                continue
            if ev_at < fm_at:
                errs.append('%s｜原条目里各时段在什么地方前头，先停下来看一眼' % name)
                continue
            new = body[:fm_at] + fm_lines + body[fm_at:ev_at] + ev_lines + body[ev_at:]
            if call:
                ks = [k for k, l in enumerate(new) if l.startswith('【调用】')]
                if len(ks) != 1:
                    errs.append('%s｜原条目的【调用】不止一行或者没有' % name)
                    continue
                new[ks[0]] = call
            lines[a:b] = new
            done += 1
        if apply and not errs:
            open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    for s in errs:
        print('错｜' + s)
    print('能补 %d 条，错 %d%s' % (done, len(errs), '' if apply else '（没写盘，加 --apply 写）'))
    if apply and errs:
        print('有错，一个文件也没写')
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
