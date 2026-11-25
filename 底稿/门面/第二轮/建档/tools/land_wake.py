#!/usr/bin/env python3
# 身穿降临者的凭证改了那几句以后，头一轮多叫醒、少叫醒了卡里哪些条目（11-25）。
#   python -I -X utf8 底稿/门面/第二轮/建档/tools/land_wake.py <credcmp_isk_1125.mjs 存下的 乙组_全部.json> [卡，默认 out/发布卡_四纪大框/奥尔德兰_四纪大框_全本.json] [--all]
# 拿 底稿/状态栏/大框/slim_card.py 的 wake（跟打卡时查开局口令的是同一支）：改前、改后的凭证各当成玩家头一条消息扫一遍世界书，比两边醒的条目。
# 少醒的要是 0（改的句子没碰坏哪一条的触发）；多醒的一条一条列出来看该不该醒。--all 一份凭证一行，不加只列有出入的。
import io
import json
import os
import sys

sys.dont_write_bytecode = True
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', '大框'))
import slim_card as SL  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith('--')]
keep = json.load(open(args[0], encoding='utf-8'))
card = args[1] if len(args) > 1 else os.path.join(ROOT, 'out', '发布卡_四纪大框', '奥尔德兰_四纪大框_全本.json')
lb = json.load(open(card, encoding='utf-8'))['prompt']['lorebook']
title = lambda i: '%s｜%s' % (lb[i].get('folder') or '', (lb[i].get('content') or '').split('\n', 1)[0][:36])
size = lambda i: len(lb[i].get('content') or '')

gain_all, lost_all, tot_old, tot_new = {}, {}, 0, 0
for k in keep:
    a, b = SL.wake(lb, k['old'], 'user'), SL.wake(lb, k['new'], 'user')
    g, l = sorted(b - a), sorted(a - b)
    tot_old += sum(size(i) for i in a)
    tot_new += sum(size(i) for i in b)
    for i in g:
        gain_all.setdefault(i, []).append(k['what'])
    for i in l:
        lost_all.setdefault(i, []).append(k['what'])
    if g or l or '--all' in sys.argv:
        print('%s　%s　改前醒 %d 条 %d 字，改后 %d 条 %d 字' % (k['id'], k['what'], len(a), sum(size(i) for i in a), len(b), sum(size(i) for i in b)))
        for i in g:
            print('    多醒　%s　%d 字' % (title(i), size(i)))
        for i in l:
            print('    少醒　%s　%d 字' % (title(i), size(i)))
print()
print('%d 份凭证，卡 %s（世界书 %d 条）' % (len(keep), os.path.basename(card), len(lb)))
print('少醒的条目 %d 条' % len(lost_all))
for i, ws in sorted(lost_all.items(), key=lambda x: -len(x[1])):
    print('  %s　%d 字　%d 份里少醒　触发 %s' % (title(i), size(i), len(ws), json.dumps(lb[i].get('triggerWords'), ensure_ascii=False)[:200]))
print('多醒的条目 %d 条' % len(gain_all))
for i, ws in sorted(gain_all.items(), key=lambda x: -len(x[1])):
    print('  %s　%d 字　%d 份里多醒（%s）　触发 %s' % (title(i), size(i), len(ws), '、'.join(w.split('｜')[1] if '｜' in w else w for w in ws[:4]), json.dumps(lb[i].get('triggerWords'), ensure_ascii=False)[:240]))
n = max(1, len(keep))
print('头一轮叫醒的字数，平均一份 改前 %d 改后 %d（差 %+d）' % (tot_old / n, tot_new / n, (tot_new - tot_old) / n))
sys.exit(1 if lost_all else 0)
