#!/usr/bin/env python3
# 世界之书自查（11-15）：python -I -X utf8 底稿/门面/卡片/check_wb.py <文件.json> …   （仓库根上跑）
# 文件可以是整本（{"volumes": [...]}，就是 世界之书.json），也可以是一卷（{"id": "strife", "title": …, "pages": [...]}）。
# 查：各栏在不在、一页多少字、一段多长、标点、月相字、冒号、禁词；再拼成卡面检查稿跑 cardscan 和 authormark。
# 字数照月银纪卷量的：一页正文三百到五百字（月银纪卷 330 到 428），一段一百四十字以内，编年一条四十五字以内。
import io
import json
import os
import re
import subprocess
import sys
import tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
han = lambda s: len(re.findall(r'[一-鿿]', s or ''))
BAD = re.compile(r'[—；…！]|\.\.\.|[:：]')
MOON = re.compile(r'月亮|月光|新月|满月|残月|月牙|弦月|月相')
BANNED = ['一丝', '一抹', '不禁', '威压', '修为', '登记', '晋升', '只给 AI', '只给AI', '玩家能改', '裁定', '★', '底卡', '条目']
VOLS = {'general': '通用', 'moon': '月银纪', 'strife': '纷争纪', 'bronze': '山铜纪', 'maze': '迷宫纪'}
SCAN = {'general': '迷宫纪', 'moon': '月银纪', 'strife': '纷争纪', 'bronze': '山铜纪', 'maze': '迷宫纪'}      # 检查稿的标题要纪名起头，cardscan 才扫（11-15 W1 查出来的，原来写“世界之书·”一条也不扫）
NEED = {'strife': ['age', 'map', 'chron'], 'bronze': ['age', 'map', 'chron'], 'maze': ['age', 'map', 'chron'], 'moon': ['age', 'map', 'chron']}


def check(vols):
    probs, md = [], []
    for v in vols:
        vid = v.get('id')
        if vid not in VOLS:
            probs.append('卷 id %r 不认得（只认 %s）' % (vid, '、'.join(VOLS)))
            continue
        for k in ('title', 'sub', 'pages'):
            if not v.get(k):
                probs.append('%s 卷缺 %s' % (vid, k))
        ids = [p.get('id') for p in v.get('pages', [])]
        if len(ids) != len(set(ids)):
            probs.append('%s 卷页 id 有重的' % vid)
        for want in NEED.get(vid, []):
            if want not in ids:
                probs.append('%s 卷没有 id 为 %s 的那一页' % (vid, want))
        texts = [(vid + ' 卷题', v.get('title', '')), (vid + ' 卷副题', v.get('sub', ''))]
        for p in v.get('pages', []):
            pid = '%s/%s' % (vid, p.get('id'))
            for k in ('id', 'title', 'sub'):
                if not p.get(k):
                    probs.append('%s 缺 %s' % (pid, k))
            if han(p.get('title')) > 10:
                probs.append('%s 题 %d 字' % (pid, han(p.get('title'))))
            if han(p.get('sub')) > 18:
                probs.append('%s 副题 %d 字（至多 18）' % (pid, han(p.get('sub'))))
            texts += [(pid + ' 题', p.get('title', '')), (pid + ' 副题', p.get('sub', ''))]
            if p.get('kind') == 'chron':
                items = p.get('items') or []
                if not 12 <= len(items) <= 40:
                    probs.append('%s 编年 %d 条（12 到 40）' % (pid, len(items)))
                for it in items:
                    if not isinstance(it.get('spoil'), bool):
                        probs.append('%s 编年 %s 的 spoil 不是 true/false' % (pid, it.get('y')))
                    if han(it.get('t')) > 45 or not it.get('t'):
                        probs.append('%s 编年 %s 写了 %d 字（至多 45）' % (pid, it.get('y'), han(it.get('t'))))
                    if len(it.get('y', '')) > 14:
                        probs.append('%s 编年年份太长 %s' % (pid, it.get('y')))
                    texts.append((pid + ' ' + it.get('y', ''), it.get('t', '')))
                md.append('## %s·世界之书编年｜%s\n%s\n> 条目设置：检查稿，不进卡。\n' % (SCAN[vid], pid,'\n'.join('%s　%s' % (it.get('y', ''), it.get('t', '')) for it in items)))
                continue
            secs = p.get('sections') or []
            if not 3 <= len(secs) <= 9:
                probs.append('%s %d 段（3 到 9）' % (pid, len(secs)))
            tot = sum(han(s.get('t')) for s in secs)
            if not 280 <= tot <= 520:
                probs.append('%s 正文 %d 字（280 到 520）' % (pid, tot))
            for s in secs:
                if not s.get('h') or not s.get('t'):
                    probs.append('%s 有一段缺 h 或 t' % pid)
                if han(s.get('h')) > 16:
                    probs.append('%s 小题 %s %d 字' % (pid, s.get('h'), han(s.get('h'))))
                if han(s.get('t')) > 140:
                    probs.append('%s 「%s」 %d 字（至多 140）' % (pid, s.get('h'), han(s.get('t'))))
                texts += [(pid + ' ' + (s.get('h') or ''), s.get('h', '')), (pid + ' ' + (s.get('h') or ''), s.get('t', ''))]
            md.append('## %s·世界之书｜%s\n%s\n> 条目设置：检查稿，不进卡。\n' % (SCAN[vid], p.get('title', ''),'\n'.join('%s。%s' % (s.get('h', ''), s.get('t', '')) for s in secs)))
        for who, t in texts:
            for m in BAD.finditer(t or ''):
                probs.append('%s 有 %s' % (who, m.group(0)))
            for m in MOON.finditer(t or ''):
                probs.append('%s 有月相字 %s' % (who, m.group(0)))
            for w in BANNED:
                if w in (t or ''):
                    probs.append('%s 有 %s' % (who, w))
    return probs, md


def main():
    probs, md = [], []
    for f in sys.argv[1:]:
        D = json.load(open(f, encoding='utf-8'))
        vols = D['volumes'] if 'volumes' in D else [D]
        p, m = check(vols)
        probs += p
        md += m
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
