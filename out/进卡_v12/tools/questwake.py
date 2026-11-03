# 主线那一格每轮都写进回复，看它会顺带叫醒哪些范围含助手的条目（单条消息，照日里一条一条算：触发词任一中、AND 全中、黑名单同条挡）
import json, re, sys, collections
card = json.load(open(sys.argv[1], encoding='utf-8'))
lb = card['prompt']['lorebook']
rep = open(sys.argv[2], encoding='utf-8').read()
def rx(w):
    if w.startswith('/') and w.rfind('/') > 0:
        body, fl = w[1:w.rfind('/')], w[w.rfind('/') + 1:]
        try:
            return re.compile(body, re.I if 'i' in fl else 0)
        except re.error:
            return None
    return None
def hit(w, t):
    r = rx(w)
    return bool(r.search(t)) if r else (w in t)
def fires(e, t):
    if 'assistant' not in e.get('triggerRange', []):
        return False
    tw = e['triggerWords']
    ok = all(hit(w, t) for w in tw) if e.get('triggerWordsType') == 'AND' else any(hit(w, t) for w in tw)
    if not ok:
        return False
    bl = e.get('blackListWords') or []
    if bl and any(hit(w, t) for w in bl):
        return False
    return True
title = lambda e: e['content'].strip().split('\n')[0].lstrip('# ').strip()
# 显示名从报告「主线进状态栏（v12）」那一节读
sec = rep[rep.find('主线进状态栏（v12）'):]
sec = sec[:sec.find('没落到时段总纲')]
names = []
for line in sec.split('\n')[1:]:
    m = re.match(r'^(.+?)：\d+ 条，(.*)$', line)
    if m:
        names += [(m.group(1), x) for x in m.group(2).split('、')]
DATES = {'月银纪': '月银纪3200年·春·萌芽月·上旬一日', '纷争纪': '纷争纪1500年·春·萌芽月·上旬一日', '山铜纪': '山铜纪400年·春·萌芽月·上旬一日', '迷宫纪': '迷宫纪400年·春·萌芽月·上旬一日'}
extra = collections.Counter(); per = []
for pt, show in names:
    era = pt.split('·')[0]
    base = '<span class="hud-meta">%s · 08:30 · 某地 · 防抢话 开</span>' % DATES[era]
    with_q = base + '<span class="hud-quest">%s·一幕</span>' % show
    a = set(i for i, e in enumerate(lb) if fires(e, base))
    b = set(i for i, e in enumerate(lb) if fires(e, with_q))
    new = sorted(b - a)
    per.append((len(new), show, [title(lb[i])[:24] for i in new]))
    for i in new: extra[title(lb[i])] += 1
per.sort(reverse=True)
print('显示名 %d 个，平均多醒 %.1f 条，最多 %d 条' % (len(per), sum(p[0] for p in per) / max(1, len(per)), per[0][0] if per else 0))
for n, s, t in per[:15]:
    print(n, s, '｜', '、'.join(t[:6]))
print('被叫醒最多的条目：')
for t, c in extra.most_common(12): print(' ', c, t)
