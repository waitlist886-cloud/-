#!/usr/bin/env python3
# 立绘铺开（11-20 夜）收稿：底稿/立绘/铺开_11-20/交稿/<页>_<份>.md 里的 ```json 数组并成一页一份，
# 写 底稿/状态栏/comfy/cast/山铜纪/<页号>n.json（s1n、s2n…），备注并成同名 .md。门洞那一院挂上原典的 identity。
#   python -I -X utf8 底稿/立绘/tools/take_cast.py          只报
#   python -I -X utf8 底稿/立绘/tools/take_cast.py --apply  写盘，写完跑 cast_lint.py
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
W = os.path.join(ROOT, '底稿', '立绘', '铺开_11-20')
CAST = os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'cast', '山铜纪')
# identity 路径相对 底稿/状态栏/comfy/out/
REF = '../../../立绘/原典参考_11-19/'
IDENT = {'斐里安': REF + '切_雷内_斐里安.png', '伊诺克': REF + '切_雅各布_伊诺克.png', '内森': REF + '切_阿兰_内森.png',
         '玛蓓': REF + '切_玛丽安_玛蓓.png', '玛丽贝尔': REF + '桑多涅_立绘卡.jpg'}


def blocks(t, lang):
    return re.findall(r'```' + lang + r'\s*\n(.*?)\n```', t, re.S)


def main(apply):
    pages, notes, bad = {}, {}, []
    for f in sorted(glob.glob(os.path.join(W, '交稿', '*.md'))):
        pg = os.path.basename(f).split('_')[0]
        t = open(f, encoding='utf-8').read()
        js = blocks(t, 'json')
        if not js:
            bad.append('%s 没有 json 块' % os.path.basename(f))
            continue
        try:
            arr = json.loads(js[0])
        except Exception as e:
            bad.append('%s json 读不出：%s' % (os.path.basename(f), e))
            continue
        pages.setdefault(pg, []).extend(arr)
        notes.setdefault(pg, []).extend(blocks(t, 'md'))
    have = set()           # 已经有出图资料的人（门面的 have.json 没跟上，por_cover 会误报）
    for fp in glob.glob(os.path.join(CAST, '*.json')):
        if fp.endswith('n.json'):
            continue
        for x in json.load(open(fp, encoding='utf-8')):
            have.add(x.get('name', '').split('·')[0])
    drop = []
    for pg in pages:
        keep, names = [], set()
        for x in pages[pg]:
            s = re.sub(r'（.*', '', x.get('name', '')).split('·')[0]
            if s in have or s in names:
                drop.append('%s %s' % (pg, x.get('name')))
                continue
            names.add(s)
            keep.append(x)
        pages[pg] = keep
    print('去掉（已有资料或重了）', len(drop), '：', '、'.join(drop))
    for arr in pages.values():         # 名字带括号的（伊斯坎·暮雨（唱歌的）），书里认的是括号里那个叫法，起的名字挪进备注栏
        for x in arr:
            m = re.match(r'^(.+?)（(.+)）$', x.get('name', ''))
            if m:
                x['name'], x['alias'] = m.group(2), m.group(1)
    seen = {}
    for pg, arr in pages.items():
        for x in arr:
            if x.get('en') in seen:
                bad.append('en 重了：%s（%s、%s）' % (x.get('en'), seen[x['en']], pg))
            seen[x.get('en')] = pg
            if x.get('name') in IDENT:
                x['identity'] = IDENT[x['name']]
    for pg, arr in pages.items():
        print(pg, len(arr), '人：', '、'.join(x.get('name', '?') for x in arr))
    for b in bad:
        print('！', b)
    if apply and not bad:
        for pg, arr in pages.items():
            n = pg.replace('p', 's') + 'n'
            json.dump(arr, open(os.path.join(CAST, n + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
            open(os.path.join(CAST, n + '.md'), 'w', encoding='utf-8', newline='\n').write(
                '# %s（11-20 夜 Opus 起稿，主会话收）\n\n' % n + '\n\n'.join(notes[pg]) + '\n')
        print('写了', len(pages), '份')


if __name__ == '__main__':
    main('--apply' in sys.argv)
