# 风月：拿用户在平台上导出的那一张当底子，把我们这一版对世界书的改动搬过去，用户在平台上改过的条目一条不碰。
# 11-08 用户：“以这个为基底进行接下来的ui调整，你不用去经手我做出的任何已有世界书内容与提示词改动”。
# 做法：拿我们上一版（用户导进去的那一张）和这一版的风月卡逐条比，改了的条目（触发、深度、正文），
#   在用户那一张里找跟上一版那一条一字不差的（正文和触发都一样），换成这一版的；
#   用户那一张里这一条跟上一版不一样（用户在平台上改过），不换，列出来给用户看。
# 世界书以外的字段一个不动（样式、规则要换走 patch_fy_user_css.py）。
# 用法：python -I -X utf8 patch_fy_user_sync.py <用户导出.json> <上一版风月卡.json> <这一版风月卡.json> <输出.json>
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
BAN_RE = re.compile(r'rili|扣扣|日历|风月|fengyue', re.I)
FIELDS = ('key', 'value', 'depth')


def wb_of(card, what):
    ks = [k for k, v in card.items() if isinstance(v, list) and v and isinstance(v[0], dict) and {'key', 'value'} <= set(v[0])]
    if len(ks) != 1:
        sys.exit('%s认不出世界书那一栏：%s' % (what, ks))
    wb = card[ks[0]]
    if not all(set(FIELDS) <= set(e) for e in wb):
        sys.exit('%s的世界书条目里没有 %s 这几栏（风月改了字段名？），没改' % (what, '、'.join(FIELDS)))
    return ks[0], wb


user = json.load(open(sys.argv[1], encoding='utf-8'))
old = json.load(open(sys.argv[2], encoding='utf-8'))
new = json.load(open(sys.argv[3], encoding='utf-8'))
uk, uw = wb_of(user, '用户那一张')
_, ow = wb_of(old, '上一版')
_, nw = wb_of(new, '这一版')
assert len(ow) == len(nw), '上一版和这一版条数不一样，这个脚本只管逐条改了的'
changed = [i for i in range(len(ow)) if any(ow[i][f] != nw[i][f] for f in FIELDS)]
by_old = {}
for i in changed:
    by_old.setdefault((ow[i]['key'], ow[i]['value']), []).append(i)
done, hit = [], set()
for k, e in enumerate(uw):
    idx = by_old.get((e['key'], e['value']))
    if not idx:
        continue
    i = idx[0]
    if e['depth'] != ow[i]['depth']:
        continue
    for f in FIELDS:
        e[f] = nw[i][f]
    done.append((k, i))
    hit.add(i)
miss = [i for i in changed if i not in hit]
print('这一版改了的条目 %d 条；用户那一张里换了 %d 条（世界书 %s，%d 条）' % (len(changed), len(done), uk, len(uw)))
if miss:
    print('用户那一张里跟上一版对不上的 %d 条，没换（用户在平台上改过，或者删了），要用户自己看：' % len(miss))
    for i in miss:
        print('  上一版第 %d 条：%s' % (i, ow[i]['value'].split('\n', 1)[0][:50]))
text = json.dumps(user, ensure_ascii=False, indent=2)
hits = sorted(set(m.group(0) for m in BAN_RE.finditer(text)))
if hits:
    sys.exit('屏蔽词：%s' % hits)
open(sys.argv[4], 'w', encoding='utf-8').write(text)
print('ok', sys.argv[4], '；屏蔽词 0')
