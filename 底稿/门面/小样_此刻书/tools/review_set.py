#!/usr/bin/env python3
# 审图记到 scenes/review.json（prep_assets.py cg 只收写了 ok 的）。
#   python -I -X utf8 tools/review_set.py ok n1165_1 n1166_2 …        审过了
#   python -I -X utf8 tools/review_set.py redo n1170_3 "缘故一句"       不过，整张重画（旧图挪进备选、版次加一，队列开着会自己补上）；缘故记进 scenes/审图记录.tsv
#   python -I -X utf8 tools/review_set.py note n1179_3 "带注通过的话"   只记一句话，不改状态
#   python -I -X utf8 tools/review_set.py hold n1170_3 "缘故"           重画三回还不对，留空
#   python -I -X utf8 tools/review_set.py                               看眼下各种状态各有几幅
import io
import json
import os
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RJ = os.path.join(HERE, 'scenes', 'review.json')
VJ = os.path.join(HERE, 'scenes', 'rev.json')
LOG = os.path.join(HERE, 'scenes', '审图记录.tsv')
GEN = os.path.normpath(os.path.join(HERE, '..', '..', '状态栏', 'comfy', 'gpt_cg_now.py'))


def main():
    rv = json.load(open(RJ, encoding='utf-8')) if os.path.exists(RJ) else {}
    a = sys.argv[1:]
    if not a:
        from collections import Counter
        print(dict(Counter(rv.values())))
        print('redo/hold：', ' '.join(k for k, v in sorted(rv.items()) if v in ('redo', 'hold')))
        return
    what, rest = a[0], a[1:]
    rows = []
    if what == 'ok':
        for k in rest:
            rv[k] = 'ok'
            rows.append((k, 'ok', ''))
    elif what in ('redo', 'hold', 'note'):
        k, why = rest[0], (rest[1] if len(rest) > 1 else '')
        rev = (json.load(open(VJ, encoding='utf-8')) if os.path.exists(VJ) else {}).get(k, 0)
        if what == 'redo':
            rv[k] = 'redo'
            subprocess.check_call([sys.executable, '-I', '-X', 'utf8', GEN, '--redo', k])
        elif what == 'hold':
            rv[k] = 'hold'
        rows.append((k, what + ('（第 %d 版）' % rev if what != 'note' else ''), why))
    else:
        raise SystemExit('不认得 ' + what)
    json.dump(rv, open(RJ, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, sort_keys=True)
    with open(LOG, 'a', encoding='utf-8', newline='\n') as f:
        for k, s, why in rows:
            f.write('%s\t%s\t%s\t%s\n' % (time.strftime('%m-%d %H:%M'), k, s, why))
    print('记了', len(rows), '条')


if __name__ == '__main__':
    main()
