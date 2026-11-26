#!/usr/bin/env python3
# 风月五张外壳的简介页（薄壳）挨个放进沙箱框里跑一遍（fy_descr_check.mjs），11-25。
#   python -I -X utf8 底稿/风月版/bench/fy_descr_all.py <输出目录> [只跑哪几张，逗号隔开] [--dev=电脑|手机] [--no-off]
# 一张卡三回：电脑宽 1920×945、手机宽 390×844 各走一遍通的（取外壳、直接翻开、拦别纪、回牌桌、建档到确认页、真点复制），
# 再走一遍图床连不上的（镜像地址换成连不上的，看退路那一页简式建档）。--no-off 不跑连不上的那一回。
# 薄壳从 fy_shell_descr.build 现出（跟外壳里写的是同一份），不读 out/ 下的卡。要连外网（图床、字体）。结果写 <输出目录>/结果.json，截图在同目录。
# 机器忙的时候无头浏览器起得慢、图床六十秒取不到，会整回不过；单独重跑那一张就行。
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import fy_shell_descr as FD      # noqa: E402

# 卡：（键，建档从哪一条主线进。照 底稿/门面/第二轮/建档/tools/walk.mjs 的那几条）
CARDS = {
    # 11-25 夜迷宫纪拆成前传、此刻两张（拆以前那一张是 '迷宫纪': ('maze', 下面此刻那一条的建档)）
    '迷宫纪前传': ('pre', {"book": "maze", "era": "迷宫纪", "at": "q5", "title": "黑潮的年月", "line": "黑潮的年月·头一回斩首", "year": "852"}),
    '迷宫纪此刻': ('now', {"book": "maze", "era": "迷宫纪", "at": "1001", "site": "阿卡迪亚·外环棚区", "ti": "井口边的不眠之城", "line": "迷宫纪1001年·阿卡迪亚·外环棚区", "year": "1001"}),
    '月银纪': ('moon', {"book": "moon", "era": "月银纪", "at": "m07", "title": "焚原断刃", "line": "万兽·焚原", "year": "1690"}),
    '纷争纪': ('strife', {"book": "strife", "era": "纷争纪", "at": "free", "title": "第二十二张", "line": "", "year": ""}),
    '山铜纪': ('bronze', {"book": "bronze", "era": "山铜纪", "at": "p1", "title": "犁的年月", "line": "犁的年月·雨城清查", "year": "2"}),
}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    out_dir = os.path.abspath(args[0])
    only = args[1].split(',') if len(args) > 1 else None
    only_dev = next((a.split('=', 1)[1] for a in sys.argv if a.startswith('--dev=')), None)
    os.makedirs(out_dir, exist_ok=True)
    res_p = os.path.join(out_dir, '结果.json')
    out = json.load(open(res_p, encoding='utf-8')) if os.path.exists(res_p) else {}
    bad = 0
    for card, (key, build) in CARDS.items():
        if only and card not in only:
            continue
        html, acct = FD.build(key)
        thin = os.path.join(out_dir, '_薄壳_%s.html' % card)
        open(thin, 'w', encoding='utf-8', newline='\n').write(html)
        B = FD.BOOKS['all' if FD.SAME else key]
        runs = [(dev, w, h, '通') for dev, w, h in (('电脑', 1920, 945), ('手机', 390, 844)) if not only_dev or dev == only_dev]
        if '--no-off' not in sys.argv and (not only_dev or only_dev == '电脑'):
            runs.append(('电脑', 1920, 945, '断'))
        for dev, w, h, mode in runs:
            pfx = os.path.join(out_dir, '%s_%s%s' % (card, dev, '' if mode == '通' else '_断网'))
            cmd = ['node', os.path.join(HERE, 'fy_descr_check.mjs'), thin, pfx, B['start'] or 'table', ','.join(B['only']), 'w=%d' % w, 'h=%d' % h]
            cmd.append('build=' + json.dumps(build, ensure_ascii=False) if mode == '通' else 'mirrors=bad')
            r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            try:
                j = json.loads(r.stdout)
            except Exception:
                j = {'bad': ['脚本没跑完'], 'checks': [], 'raw': (r.stdout + r.stderr)[-600:]}
            out['%s｜%s｜%s' % (card, dev, mode)] = j
            bad += len(j.get('bad') or [])
            print('%s %s %s：%d 项，没过 %s' % (card, dev, '通' if mode == '通' else '图床连不上', len(j.get('checks', [])), '、'.join(j.get('bad') or []) or '无'), flush=True)
            for c in j.get('checks', []):
                if not c[1]:
                    print('   ✗', c[0], str(c[2])[:300], flush=True)
            if j.get('errs'):
                print('   页里报错', j['errs'][:3], flush=True)
            json.dump(out, open(res_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('完，没过的', bad, '项')
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
