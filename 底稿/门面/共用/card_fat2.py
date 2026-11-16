# 能机械地瘦掉的几样各有多少：旧 HTML 状态栏的锚、主线按幕拆多出来的、同名条目、样式里的图地址、给旧存档用的正则。
import collections
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = 'E:/aldran_art/'
card = json.load(open(ROOT + 'out/发布卡_四纪大框/奥尔德兰_四纪大框.json', encoding='utf-8'))
lb = card['prompt']['lorebook']
u8 = lambda s: len(s.encode('utf-8'))
B = lambda o: len(json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
MB = 1e6

# 一、旧 HTML 状态栏的锚（<br>、hud-meta">、</b>）在触发词和黑名单里占多少
LEG = re.compile(r'<br>|hud-meta|</b>|<\\/b>|<b>')
tw_all = [w for e in lb for w in e.get('triggerWords') or []]
bw_all = [w for e in lb for w in e.get('blackListWords') or []]
bw_leg = [w for w in bw_all if LEG.search(w) and not w.startswith('/')]
print('黑名单里整个就是旧锚的纯词：%d 个，%.2f MB（黑名单一共 %d 个，%.2f MB）' % (len(bw_leg), sum(u8(w) + 3 for w in bw_leg) / MB, len(bw_all), sum(u8(w) + 3 for w in bw_all) / MB))
tw_leg_plain = [w for w in tw_all if LEG.search(w) and not w.startswith('/')]
print('触发词里整个就是旧锚的纯词：%d 个，%.2f MB' % (len(tw_leg_plain), sum(u8(w) + 3 for w in tw_leg_plain) / MB))


def strip_legacy(rx):
    """正则里去掉只有旧 HTML 回复才对得上的那几支（估个数，不是真改法）。"""
    s = rx
    s = s.replace('(?:<br>|hud-meta">|纪元：)', '纪元：')
    s = re.sub(r'(?:^/|\|)[^|/()]*<\\/b><br>[^|()]*(?=\||/[a-z]*$)', lambda m: '/' if m.group(0).startswith('/') else '', s)
    return s


save = 0
n = 0
for w in tw_all + bw_all:
    if w.startswith('/') and LEG.search(w):
        s2 = strip_legacy(w)
        save += u8(w) - u8(s2)
        n += 1
print('带旧锚的正则 %d 个，去掉旧锚那几支大约省 %.2f MB' % (n, save / MB))

# 二、主线按幕拆以后，主线那一夹比没拆的时候多了多少
v12p = None
for cand in ['v12_1115/奥尔德兰_日里版_四纪全卷_测试v12.json']:
    p = os.path.join(os.environ.get('TEMP', ''), 'claude/85a810c2c0993c77/a9c888bd-63aa-40a5-83e1-c4b9ceefb820/scratchpad', cand)
    if os.path.exists(p):
        v12p = p
if not v12p:
    base = os.path.join(os.environ.get('TEMP', ''), 'claude/85a810c2c0993c77/a9c888bd-63aa-40a5-83e1-c4b9ceefb820/scratchpad')
    for root, dirs, files in os.walk(base):
        for f in files:
            if f.endswith('.json') and 'v12' in f and '测试' in f:
                v12p = os.path.join(root, f)
if v12p:
    v12 = json.load(open(v12p, encoding='utf-8'))
    f41 = lambda book: sum(B(e) for e in book if re.match(r'41·', e.get('folder') or ''))
    n41 = lambda book: sum(1 for e in book if re.match(r'41·', e.get('folder') or ''))
    a, b = f41(v12['prompt']['lorebook']), f41(lb)
    print('时段主线那一夹：没拆 %d 条 %.2f MB，拆了以后 %d 条 %.2f MB，多 %.2f MB' % (n41(v12['prompt']['lorebook']), a / MB, n41(lb), b / MB, (b - a) / MB))
else:
    print('没找到 v12 那一张，主线按幕拆多出来多少没量')

# 三、题一样的条目
title = collections.defaultdict(list)
for i, e in enumerate(lb):
    c = (e.get('content') or '').strip()
    if c:
        title[c.split('\n', 1)[0].strip()].append(i)
dup = {t: ix for t, ix in title.items() if len(ix) > 1 and len(t) > 6}
print('头一行一样的条目：%d 组，多出来的 %d 条，合计 %.2f MB' % (len(dup), sum(len(ix) - 1 for ix in dup.values()), sum(sum(B(lb[i]) for i in ix[1:]) for ix in dup.values()) / MB))
for t, ix in sorted(dup.items(), key=lambda x: -sum(B(lb[i]) for i in x[1][1:]))[:12]:
    print('   ×%d %6.1f KB %s' % (len(ix), sum(B(lb[i]) for i in ix[1:]) / 1000, t[:60]))

# 四、样式里的图地址
css = card['injectStyles']
urls = re.findall(r'url\(([^)]+)\)', css)
http = [u for u in urls if 'http' in u]
data = [u for u in urls if u.strip('"\'').startswith('data:')]
print('样式 %.2f MB：图地址 %d 个 %.2f MB（其中走网络的 %d 个 %.2f MB，写在样式里的 data: %d 个 %.2f MB）' % (
    u8(css) / MB, len(urls), sum(u8(u) for u in urls) / MB, len(http), sum(u8(u) for u in http) / MB, len(data), sum(u8(u) for u in data) / MB))
pre = collections.Counter(re.match(r'["\']?(https://[^/]+/gh/[^/]+/[^/@]+@[0-9a-f]+/)', u).group(1) for u in http if re.match(r'["\']?(https://[^/]+/gh/[^/]+/[^/@]+@[0-9a-f]+/)', u))
print('   图床地址的前缀 %d 种，前缀合计 %.2f MB' % (len(pre), sum(u8(k) * v for k, v in pre.items()) / MB))

# 五、显示正则里给旧存档用的
rr = card['assistantRegexReplace']
print('显示正则 %d 条 %.2f MB' % (len(rr), B(rr) / MB))
