# 两样再细量：时段钥匙（又长又在几百条里重复的那种正则）一共占多少、改短能省多少；底卡里只有 1001 年那一局用得上的有多少。
import collections
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
card = json.load(open('E:/aldran_art/out/发布卡_四纪大框/奥尔德兰_四纪大框.json', encoding='utf-8'))
lb = card['prompt']['lorebook']
u8 = lambda s: len(s.encode('utf-8'))
B = lambda o: len(json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
MB = 1e6

tw = collections.Counter(w for e in lb for w in (e.get('triggerWords') or []) + (e.get('blackListWords') or []))
keys = {w: n for w, n in tw.items() if w.startswith('/') and '开局时段' in w and n >= 5}
tot = sum(u8(w) * n for w, n in keys.items())
print('带“开局时段”、在五条以上重复的正则：%d 种，一共出现 %d 回，占 %.2f MB；平均一条 %d 字节' % (len(keys), sum(keys.values()), tot / MB, tot / max(1, sum(keys.values()))))
print('   要是每回都换成 100 字节上下的短钥匙，省 %.2f MB' % ((tot - 100 * sum(keys.values())) / MB))
long_all = {w: n for w, n in tw.items() if w.startswith('/') and u8(w) >= 300}
print('三百字节以上的正则：%d 种，出现 %d 回，占 %.2f MB' % (len(long_all), sum(long_all.values()), sum(u8(w) * n for w, n in long_all.items()) / MB))


def fno(e):
    m = re.match(r'\s*(\d+)', e.get('folder') or '')
    return int(m.group(1)) if m else -1


# 底卡里哪些只有 1001 年那一局用得上：拿四纪的底座去撞它的黑名单，四纪都被挡掉的就算
ERA_LINES = {
    '月银纪': '§底座｜纪元：月银纪1690年·坠叶月·上旬三日 · 08:10 · 双虹城 · 万兽·焚原·一幕 · 防抢话：开 · 档位：长',
    '纷争纪': '§底座｜纪元：纷争纪3600年·萌芽月·上旬三日 · 08:10 · 长垒中段 · 炮的年月·不熄火·一幕 · 防抢话：开 · 档位：长',
    '山铜纪': '§底座｜纪元：山铜纪745年·坠叶月·上旬三日 · 08:10 · 苍焰角城 · 七城的年月·苍焰角城·一幕 · 防抢话：开 · 档位：长',
    '迷宫纪前传': '§底座｜纪元：迷宫纪620年·坠叶月·上旬三日 · 08:10 · 阿卡迪亚 · 深井的年月·第五十一层·一幕 · 防抢话：开 · 档位：长',
}


def hit(words, typ, msg):
    if not words:
        return False
    res = []
    for w in words:
        m = re.match(r'^/(.*)/([a-z]*)$', w, re.S)
        if m:
            try:
                fl = re.I if 'i' in m.group(2) else 0
                res.append(bool(re.search(m.group(1), msg, fl | (re.S if 's' in m.group(2) else 0))))
            except re.error:
                res.append(False)
        else:
            res.append(w in msg)
    return all(res) if typ == 'AND' else any(res)


base = [e for e in lb if fno(e) < 40]
blocked = collections.Counter()
bytes_blocked = collections.Counter()
only1001 = []
for e in base:
    k = sum(1 for msg in ERA_LINES.values() if hit(e.get('blackListWords'), e.get('blackListWordsType', 'OR'), msg))
    blocked[k] += 1
    bytes_blocked[k] += B(e)
    if k == 4:
        only1001.append(e)
print('底卡 %d 条 %.2f MB。四纪的底座各撞一遍它的黑名单：' % (len(base), sum(B(e) for e in base) / MB))
for k in sorted(blocked):
    print('   被 %d 纪挡掉的 %4d 条 %.2f MB' % (k, blocked[k], bytes_blocked[k] / MB))
by = collections.Counter()
for e in only1001:
    by[e.get('folder')] += B(e)
print('   四纪都挡的（只有 1001 年那一局用）按文件夹：' + '，'.join('%s %.2f' % (f, b / MB) for f, b in by.most_common(12)))
