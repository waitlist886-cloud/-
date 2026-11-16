#!/usr/bin/env python3
# 门面卡片自查：python -I -X utf8 底稿/门面/卡片/check_cards.py <纪> [时代 id …]   （仓库根上跑）
# 查：名字对得上书里的数据、该有的人和主线都有、各栏在不在、字数、禁用标点、月相字、冒号、禁词；再把卡片拼成卡面检查稿跑 cardscan 和 authormark。
# 检查稿每条末尾带一行「> 条目设置」，cardscan 和 authormark 只扫带这一行的条目（11-15 萨尔维斯那一份查出来的，原来这两项永远报 0）。
import io
import json
import os
import re
import subprocess
import sys
import tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
BOOK = {'月银纪': ('小样_月银纪书', 'moon.json'), '纷争纪': ('小样_纷争纪书', 'strife.json'),
        '山铜纪': ('小样_山铜纪书', 'bronze.json'), '迷宫纪': ('小样_迷宫纪书', 'maze.json')}
han = lambda s: len(re.findall(r'[一-鿿]', s or ''))
BAD = re.compile(r'[—；…！]|\.\.\.|[:：]')
MOON = re.compile(r'月亮|月光|新月|满月|残月|月牙|弦月|月相')
BANNED = ['一丝', '一抹', '不禁', '威压', '修为', '登记', '晋升', '只给 AI', '只给AI', '玩家能改', '裁定', '★']


def main():
    era = sys.argv[1]
    d, f = BOOK[era]
    D = json.load(open(os.path.join(ROOT, '底稿', '门面', d, 'data', f), encoding='utf-8'))
    eras = {e['id']: e for e in D['eras']}
    ids = sys.argv[2:] or sorted(eras)
    probs, md = [], []
    for i in ids:
        fp = os.path.join(ROOT, '底稿', '门面', '卡片', era, i + '.json')
        if not os.path.exists(fp):
            probs.append('%s 没有卡片文件' % i)
            continue
        C = json.load(open(fp, encoding='utf-8'))
        e = eras[i]
        lines = {l['name'] for l in e['lines']}
        cast = {c['name'] for c in e['cast']}
        meet = {m['name'] for m in (e.get('meet') or [])}
        for n in lines - set(C.get('lines', {})):
            probs.append('%s 主线 %s 没写' % (i, n))
        for n in (cast | meet) - set(C.get('people', {})):
            probs.append('%s 人 %s 没写' % (i, n))
        for n in set(C.get('lines', {})) - lines:
            probs.append('%s 主线 %s 书里没有这个名字' % (i, n))
        for n in set(C.get('people', {})) - cast - meet:
            probs.append('%s 人 %s 书里没有这个名字' % (i, n))
        texts = []
        for n, l in C.get('lines', {}).items():
            if han(l.get('open')) > 66 or not l.get('open'):
                probs.append('%s 主线 %s open %d 字' % (i, n, han(l.get('open'))))
            texts += [('主线 ' + n, l.get('hook', '')), ('主线 ' + n, l.get('open', ''))]
            md.append('## %s·主线｜%s\n%s\n%s\n> 条目设置：检查稿，不进卡。\n' % (era, n, l.get('hook', ''), l.get('open', '')))
        for n, p in C.get('people', {}).items():
            k = p.get('kind')
            want = 'cast' if n in cast else 'meet'
            if k != want:
                probs.append('%s %s kind 写成 %s，书里是 %s' % (i, n, k, want))
            need = ['head', 'tags', 'traits', 'bg', 'stars', 'meet', 'hook', 'line'] if want == 'cast' else ['head', 'bg']
            for x in need:
                if not p.get(x):
                    probs.append('%s %s 缺 %s' % (i, n, x))
            body = [p.get('bg', ''), p.get('meet', ''), p.get('hook', ''), p.get('line', '')] + [s.get('text', '') for s in p.get('stars', [])]
            tot = sum(han(x) for x in body) + sum(han(x) for x in p.get('head', []) + p.get('tags', []) + p.get('traits', []))
            lo, hi = (200, 460) if want == 'cast' else (20, 180)
            if not lo <= tot <= hi:
                probs.append('%s %s 合计 %d 字（%d 到 %d）' % (i, n, tot, lo, hi))
            caps = {'bg': 130 if want == 'cast' else 90, 'meet': 80, 'hook': 90}
            for x, c in caps.items():
                if han(p.get(x)) > c:
                    probs.append('%s %s %s %d 字（至多 %d）' % (i, n, x, han(p.get(x)), c))
            for s in p.get('stars', []):
                if han(s.get('text')) > 46:
                    probs.append('%s %s 星 %s %d 字' % (i, n, s.get('name'), han(s.get('text'))))
                if s.get('kind') not in ('Special', 'Passive', 'Art', 'Active'):
                    probs.append('%s %s 星 %s kind 是 %s' % (i, n, s.get('name'), s.get('kind')))
            for x in p.get('head', []) + p.get('tags', []):
                if han(x) > 10:
                    probs.append('%s %s 标签太长：%s' % (i, n, x))
            for x in p.get('traits', []):
                if han(x) > 7:
                    probs.append('%s %s 性格词太长：%s' % (i, n, x))
            texts += [(n, x) for x in body + p.get('head', []) + p.get('tags', []) + p.get('traits', [])]
            md.append('## %s·人物｜%s\n%s\n%s\n> 条目设置：检查稿，不进卡。\n' % (era, n, '\n'.join(x for x in body if x), '　'.join(p.get('head', []) + p.get('tags', []) + p.get('traits', []))))
        for who, t in texts:
            for m in BAD.finditer(t or ''):
                probs.append('%s %s 有 %s' % (i, who, m.group(0)))
            for m in MOON.finditer(t or ''):
                probs.append('%s %s 有月相字 %s' % (i, who, m.group(0)))
            for w in BANNED:
                if w in (t or ''):
                    probs.append('%s %s 有 %s' % (i, who, w))
    for p in probs:
        print(p)
    if md:
        with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as tf:
            tf.write('\n'.join(md))
        for tool in ('cardscan.py', 'authormark.py'):
            r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(ROOT, 'tools', tool), tf.name], capture_output=True, text=True, encoding='utf-8')
            out = r.stdout.strip().splitlines()
            print(tool, out[-1] if out else r.stderr[-300:])
            if out and not out[-1].endswith(' 0'):
                print('\n'.join(out[-30:]))
        os.unlink(tf.name)
    print('合计 %d 处' % len(probs))


if __name__ == '__main__':
    main()
