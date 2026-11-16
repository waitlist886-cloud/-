# 四纪大框的分量都在哪：按文件夹、按成分（正文、触发词、黑名单、结构）量，再找重复的行和重复的触发词。
import collections
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
card = json.load(open('E:/aldran_art/out/发布卡_四纪大框/奥尔德兰_四纪大框.json', encoding='utf-8'))
lb = card['prompt']['lorebook']
B = lambda o: len(json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
u8 = lambda s: len(s.encode('utf-8'))
MB = 1e6
ERAS = ['月银纪', '纷争纪', '山铜纪', '迷宫纪']


def fno(e):
    m = re.match(r'\s*(\d+)', e.get('folder') or '')
    return int(m.group(1)) if m else -1


def grp(e):
    f = e.get('folder') or ''
    if fno(e) >= 40:
        m = re.search('|'.join(ERAS), f)
        if m:
            return m.group(0)
    return '底卡'


def text(e):
    if e.get('contentMethod') == 'weighted':
        return '\n'.join(x['content'] for x in e.get('contents') or [])
    return e.get('content') or ''


tot = B(lb)
c_bytes = sum(u8(text(e)) for e in lb)
t_bytes = sum(u8(w) for e in lb for w in e.get('triggerWords') or [])
k_bytes = sum(u8(w) for e in lb for w in e.get('blackListWords') or [])
print('世界书 %.1f MB：正文 %.1f，触发词 %.2f，黑名单 %.2f，其余（键名、引号、转义、设置）%.2f' % (
    tot / MB, c_bytes / MB, t_bytes / MB, k_bytes / MB, (tot - c_bytes - t_bytes - k_bytes) / MB))
print('别的字段：样式 %.2f MB，显示正则 %.2f MB，主提示词 %.2f MB' % (u8(card['injectStyles']) / MB, B(card['assistantRegexReplace']) / MB, u8(card['prompt']['systemPrompt']) / MB))

print('\n== 底卡各文件夹（00 到 39，加 90 以后）')
by = collections.OrderedDict()
for e in lb:
    if grp(e) == '底卡':
        d = by.setdefault(e.get('folder') or '(没有)', [0, 0])
        d[0] += 1
        d[1] += B(e)
for f, (n, b) in sorted(by.items(), key=lambda x: (fno({'folder': x[0]}), x[0])):
    print('   %-34s %4d 条 %5.2f MB' % (f[:34], n, b / MB))

print('\n== 四纪各类文件夹合计（按文件夹名里｜后头那一截）')
kind = collections.defaultdict(lambda: [0, 0, collections.Counter()])
for e in lb:
    g = grp(e)
    if g == '底卡':
        continue
    name = re.split('[｜|]', e.get('folder') or '', maxsplit=1)[-1]
    kind[name][0] += 1
    kind[name][1] += B(e)
    kind[name][2][g] += B(e)
for name, (n, b, per) in sorted(kind.items(), key=lambda x: -x[1][1]):
    print('   %-10s %5d 条 %5.2f MB ｜%s' % (name, n, b / MB, ' '.join('%s %.2f' % (g[0], per[g] / MB) for g in ERAS if per[g])))

print('\n== 重复的行（十五个字以上、在不止一条里出现的），算多出来的那些遍数')
cnt = collections.Counter()
for e in lb:
    seen = set()
    for ln in text(e).split('\n'):
        s = ln.strip()
        if len(s) >= 15:
            cnt[s] += 1
red = sum((n - 1) * u8(s) for s, n in cnt.items() if n > 1)
print('   多出来的字节合计 %.2f MB（占正文 %.1f%%）' % (red / MB, 100 * red / c_bytes))
top = sorted(((n - 1) * u8(s), n, s) for s, n in cnt.items() if n > 1)[-28:]
for b, n, s in reversed(top):
    print('   %6.1f KB ×%-5d %s' % (b / 1000, n, s[:74]))

print('\n== 重复的句子（按。切，二十个字以上）')
cs = collections.Counter()
for e in lb:
    for s in re.split(r'(?<=[。！？])', text(e).replace('\n', '')):
        s = s.strip()
        if len(s) >= 20:
            cs[s] += 1
red2 = sum((n - 1) * u8(s) for s, n in cs.items() if n > 1)
print('   多出来的字节合计 %.2f MB' % (red2 / MB))
for b, n, s in reversed(sorted(((n - 1) * u8(s), n, s) for s, n in cs.items() if n > 1)[-14:]):
    print('   %6.1f KB ×%-5d %s' % (b / 1000, n, s[:74]))

print('\n== 触发词')
tw = collections.Counter(w for e in lb for w in e.get('triggerWords') or [])
print('   共 %d 个，%.2f MB；不同的 %d 个，各算一遍 %.2f MB' % (sum(tw.values()), t_bytes / MB, len(tw), sum(u8(w) for w in tw) / MB))
for b, n, w in reversed(sorted((n * u8(w), n, w) for w, n in tw.items())[-14:]):
    print('   %6.1f KB ×%-5d 长 %4d  %s' % (b / 1000, n, u8(w), w[:60]))
print('== 黑名单')
bw = collections.Counter(w for e in lb for w in e.get('blackListWords') or [])
print('   共 %d 个，%.2f MB；不同的 %d 个，各算一遍 %.2f MB' % (sum(bw.values()), k_bytes / MB, len(bw), sum(u8(w) for w in bw) / MB))
for b, n, w in reversed(sorted((n * u8(w), n, w) for w, n in bw.items())[-10:]):
    print('   %6.1f KB ×%-5d 长 %4d  %s' % (b / 1000, n, u8(w), w[:60]))

print('\n== 条目大小')
sizes = sorted(u8(text(e)) for e in lb)
for lim in (300, 600, 1500, 4000, 10000, 100000):
    n = sum(1 for s in sizes if s <= lim)
    print('   正文不过 %6d 字节的 %5d 条，合计 %.2f MB' % (lim, n, sum(s for s in sizes if s <= lim) / MB))
