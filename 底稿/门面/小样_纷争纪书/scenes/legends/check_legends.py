#!/usr/bin/env python3
# 查 scenes/legends/gX.json 合不合规矩（派活说明_传奇.md 第三到五节）。用法：python -I -X utf8 check_legends.py gA gB …（不写就查全部）
# 报“错”的要改；报“看”的自己看一眼，有来由就留着。
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = os.path.dirname(HERE)
sys.path.insert(0, SCENES)
import check_scenes as CS  # noqa: E402    它一进来就把 stdout 包成 utf-8 了

BOOK = CS.BOOK
TIER = re.compile(r'撼世|天灾|圣座|凡极|LVL|位阶|极境|英雄位阶')
META = re.compile(r'玩家|AI|裁定|条目|正史|旅伴|主线|底卡|★|#\d|深层|真容')
MOON = re.compile(r'月亮|月光|新月|满月|残月|月牙|弦月')
ZH_BAN = re.compile(r'——|—|；|…|！|\.\.\.')
COLLOQ = re.compile(r'爹|娘亲|掌柜|师父|徒弟|丫头|客栈')
BIG = re.compile(r'之战|对决|决战|觉醒|羁绊|命运|绝望|希望|陨落|月亮|月光|新月|满月|残月|月牙|弦月')
HAN = re.compile(r'^[一-鿿]{2,4}$')


def zh(errs, where, t, lo, hi, looks):
    for rx, what in ((ZH_BAN, '禁用的标点'), (TIER, '档位的字'), (META, '给模型看的字眼'), (MOON, '月相字'), (COLLOQ, '中式口语')):
        m = rx.search(t)
        if m:
            errs.append('%s 里有%s：%s' % (where, what, m.group(0)))
    if not lo <= len(t) <= hi:
        looks.append('%s %d 个字（要 %d 到 %d）' % (where, len(t), lo, hi))


def check(gid, spec, used):
    errs, looks = [], []
    path = os.path.join(HERE, gid + '.json')
    try:
        raw = open(path, 'rb').read()
        if raw[:3] == b'\xef\xbb\xbf':
            errs.append('文件带 BOM')
        d = json.loads(raw.decode('utf-8-sig'))
    except Exception as e:
        return ['读不了 %s：%s' % (path, e)], []
    mine = {n: s for n, s in spec.items() if s['group'] == gid}
    leg = d.get('legends') or {}
    for n in mine:
        if n not in leg:
            errs.append('缺「%s」' % n)
    for n, x in leg.items():
        if n not in mine:
            errs.append('「%s」不在这一组的任务单里（键要跟任务单上的名字一字不差）' % n)
            continue
        if not x.get('who'):
            errs.append('「%s」缺 who' % n)
        else:
            zh(errs, '「%s」who' % n, x['who'], 30, 120, looks)
        a, b = mine[n]['cards']
        want, got = list(range(a, b + 1)), []
        for seg in x.get('at') or []:
            c = seg.get('cards')
            if not (isinstance(c, list) and len(c) == 2 and all(isinstance(v, int) for v in c) and c[0] <= c[1]):
                errs.append('「%s」at 的 cards 要写成 [头一张, 末一张]：%s' % (n, c))
                continue
            got += list(range(c[0], c[1] + 1))
            if not seg.get('text'):
                errs.append('「%s」at %s 缺 text' % (n, c))
            else:
                zh(errs, '「%s」at %s' % (n, c), seg['text'], 24, 130, looks)
        if got != want:
            errs.append('「%s」at 盖的是 %s，要正好是第 %d 到第 %d 张，照先后排，不重不漏' % (n, got, a, b))
        for q in x.get('quotes') or []:
            zh(errs, '「%s」quotes' % n, q, 2, 80, looks)
        if len(x.get('quotes') or []) > 2:
            errs.append('「%s」quotes 至多两句' % n)
    falls = d.get('falls') or []
    seen, names = set(), []
    need = {s['fall']: n for n, s in mine.items() if s['fall']}
    for f in falls:
        k = f.get('key', '？')
        if k in seen:
            errs.append('%s 键重了' % k)
        seen.add(k)
        if k not in need:
            errs.append('%s 不是任务单给的键' % k)
            continue
        if f.get('death') != need[k]:
            errs.append('%s death 写的是「%s」，任务单是「%s」' % (k, f.get('death'), need[k]))
        for x, lo, hi in (('when', 5, 30), ('where', 2, 24), ('how', 30, 170)):
            if not f.get(x):
                errs.append('%s 缺 %s' % (k, x))
            else:
                zh(errs, '%s %s' % (k, x), f[x], lo, hi, looks)
        if mine[need[k]]['end'] == '不知所终' and f.get('label') != '不知所终':
            errs.append('%s 要写 "label": "不知所终"' % k)
        if f.get('noart'):
            continue
        for x in ('name', 'style', 'light', 'camera', 'text'):
            if not f.get(x):
                errs.append('%s 缺 %s' % (k, x))
        nm = f.get('name', '')
        if nm and not HAN.match(nm):
            errs.append('%s name「%s」不是两到四个汉字' % (k, nm))
        if BIG.search(nm):
            errs.append('%s name「%s」用了大词或月相字' % (k, nm))
        if nm in used.get(k[:3], []):
            errs.append('%s name「%s」跟这张牌已有的图名重了' % (k, nm))
        names.append(nm)
        st = f.get('style') or []
        if len(st) != 2 or any(x not in CS.STYLES for x in st):
            errs.append('%s style %s 不对（要两个，从表里挑）' % (k, st))
        ppl = f.get('who') or []
        for p in ppl:
            if not (isinstance(p, list) and len(p) == 3):
                errs.append('%s 人那一项要写成 [键, 衣服, 叫法]：%s' % (k, p))
                continue
            dd = CS.por(p[0])
            if not dd:
                errs.append('%s 立绘键 %s 找不到' % (k, p[0]))
            elif p[1] not in CS.CELLS or not os.path.exists(os.path.join(dd, 'cell_%s.png' % p[1])):
                errs.append('%s %s 没有 %s 那一套' % (k, p[0], p[1]))
        if 2 + len(ppl) + (1 if f.get('beast') else 0) > 5:
            errs.append('%s 参考图超了五张（画风 2，人 %d，兽 %d）' % (k, len(ppl), 1 if f.get('beast') else 0))
        if f.get('beast') and not os.path.exists(CS.beast_path(f['beast'])):
            errs.append('%s beast %s 没有这张图' % (k, f['beast']))
        t = f.get('text') or ''
        if t and not t.startswith('Scene:'):
            errs.append('%s text 要从 Scene: 起头' % k)
        n = len(t.split())
        if t and not 150 <= n <= 460:
            looks.append('%s text %d 个词（要两百到三百五）' % (k, n))
        for x in ('text', 'light', 'camera'):
            m = CS.BAN_EN.search(f.get(x) or '')
            if m:
                errs.append('%s %s 里有不该有的词：%s' % (k, x, m.group(0)))
        if re.search(r'[一-鿿]', t + (f.get('light') or '') + (f.get('camera') or '')):
            errs.append('%s text、light、camera 里有汉字' % k)
        if f.get('young') and f.get('raw'):
            errs.append('%s young 和 raw 不能都写' % k)
        if need[k].startswith('诺伦') and re.search(r'\b(she|her|face|hair)\b', t, re.I):
            looks.append('%s 诺伦那一幅里出现了 she、her、face、hair 这类词，确认没有露底' % k)
    for k, n in need.items():
        if k not in seen:
            errs.append('缺 falls %s（%s）' % (k, n))
    dup = sorted({n for n in names if n and names.count(n) > 1})
    if dup:
        errs.append('name 重了：' + '、'.join(dup))
    print('%s：传奇 %d／%d，at %d 段，falls %d／%d' % (gid, len([n for n in leg if n in mine]), len(mine), sum(len(x.get('at') or []) for x in leg.values()), len(seen & set(need)), len(need)))
    return errs, looks


if __name__ == '__main__':
    spec = json.load(open(os.path.join(HERE, 'spec.json'), encoding='utf-8'))
    cg = json.load(open(os.path.join(BOOK, 'cg_table.json'), encoding='utf-8'))
    used = {}
    for stem, t in cg.items():
        if t.get('name') and not t.get('fall'):          # 并进表以后陨落那些行也在表里，不拿它们自己跟自己比
            used.setdefault(stem.split('_')[0], []).append(t['name'])
    ids = sys.argv[1:] or sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(HERE, 'g?.json')))
    bad = 0
    for gid in ids:
        errs, looks = check(gid, spec, used)
        for e in errs:
            print('  错｜' + e)
        for e in looks:
            print('  看｜' + e)
        bad += len(errs)
    print('错合计', bad)
    sys.exit(1 if bad else 0)
