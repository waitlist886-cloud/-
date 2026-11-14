#!/usr/bin/env python3
# 查 scenes/mNN.json 合不合规矩（派活说明第三到六节）。用法：python -I -X utf8 check_scenes.py m05 m06 …（不写就查全部）
# 报“错”的要改；报“看”的自己看一眼，有来由就留着。
import glob
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)
ROOT = os.path.normpath(os.path.join(BOOK, '..', '..', '..'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
STYLES = {'anaxa', 'fire', 'wheat', 'aglaea_card', 'himeko_card', 'sparkle', 'jingyuan'}
CELLS = {'casual', 'private', 'battle', 'formal'}
SETS = ['立绘_纷争纪', '立绘_v3', '立绘_山铜纪', '立绘_前传', '立绘_月银纪史诗', '立绘_诸国期', '立绘_萨尔维斯']
BAN_EN = re.compile(r'\b(moon\w*|crescent\w*|kimono|katana|pagoda|hanfu|chinese|japanese|samurai|ninja|rifle|pistol|musket|firearm|revolver)\b', re.I)
BAN_ZH = re.compile(r'——|—|；|…|！|\.\.\.')
BIG = re.compile(r'之战|对决|决战|觉醒|羁绊|命运|绝望|希望|月亮|月光|新月|满月|残月|月牙|弦月')
HAN = re.compile(r'^[一-鿿]{2,4}$')


def beast_path(name):
    """beast 那一栏：god_ 打头的是神明显像，别的是史诗战的图（纷争纪三份）。"""
    if name.startswith('god_'):
        return os.path.join(COMFY, 'out', '神明显像', name + '.png')
    return os.path.join(COMFY, 'out', '史诗战', name.rsplit('_', 2)[0], name + '.png')


def por(key):
    for s in SETS:
        p = os.path.join(COMFY, 'out', s, key)
        if os.path.isdir(p):
            return p
    return None


def keys_of(era):
    out = {}
    for k, l in enumerate(era['lines']):
        pre = 'n' if len(era['lines']) == 1 else 'abcdefgh'[k]
        acts = [a.split('｜')[0] for a in l['acts'] if not a.startswith('幕间')]
        for i, a in enumerate(acts):
            out['%s_%s%d' % (era['id'], pre, i + 1)] = (l['name'], a)
    return out


def check(eid, moon):
    errs, looks = [], []
    path = os.path.join(HERE, eid + '.json')
    try:
        raw = open(path, 'rb').read()
        if raw[:3] == b'\xef\xbb\xbf':
            errs.append('文件带 BOM')
        d = json.loads(raw.decode('utf-8-sig'))
    except Exception as e:
        return ['读不了 %s：%s' % (path, e)], []
    era = [e for e in moon['eras'] if e['id'] == eid][0]
    want = keys_of(era)
    ages = {c['name']: c.get('age') for c in era.get('cast', []) + era.get('meet', [])}
    cast_names = {c['name'] for c in era.get('cast', [])}
    key2name = {c['key']: c['name'] for c in era.get('cast', []) + era.get('meet', []) + era.get('legends', []) + era.get('gods', []) if c.get('key')}
    if d.get('era') != eid:
        errs.append('era 不是 ' + eid)
    seen, names = set(), []

    def scene(s, death=False):
        k = s.get('key', '？')
        for f in ('key', 'name', 'style', 'light', 'camera', 'text'):
            if not s.get(f):
                errs.append('%s 缺 %s' % (k, f))
        if k in seen:
            errs.append('%s 键重了' % k)
        seen.add(k)
        nm = s.get('name', '')
        if nm and not HAN.match(nm):
            errs.append('%s name「%s」不是两到四个汉字' % (k, nm))
        if BIG.search(nm):
            errs.append('%s name「%s」用了大词或月相字' % (k, nm))
        names.append(nm)
        st = s.get('style') or []
        if len(st) != 2 or any(x not in STYLES for x in st):
            errs.append('%s style %s 不对（要两个，从表里挑）' % (k, st))
        if s.get('who') and s.get('row'):
            errs.append('%s who 和 row 只能写一个' % k)
        ppl = s.get('who') or s.get('row') or []
        for p in ppl:
            if not (isinstance(p, list) and len(p) == 3):
                errs.append('%s 人那一项要写成 [键, 衣服, 叫法]：%s' % (k, p))
                continue
            d_ = por(p[0])
            if not d_:
                errs.append('%s 立绘键 %s 找不到' % (k, p[0]))
            elif p[1] not in CELLS or not os.path.exists(os.path.join(d_, 'cell_%s.png' % p[1])):
                errs.append('%s %s 没有 %s 那一套' % (k, p[0], p[1]))
        n_ref = 2 + (1 if s.get('row') else len(s.get('who') or [])) + (1 if s.get('beast') else 0)
        if n_ref > 5:
            errs.append('%s 参考图 %d 张，超了五张（画风 2，人 %d，兽 %d）' % (k, n_ref, n_ref - 2 - (1 if s.get('beast') else 0), 1 if s.get('beast') else 0))
        if s.get('row') and len(s['row']) > 8:
            errs.append('%s row 超过八个人' % k)
        if s.get('beast') and not os.path.exists(beast_path(s['beast'])):
            errs.append('%s beast %s 没有这张图' % (k, s['beast']))
        t = s.get('text') or ''
        if t and not t.startswith('Scene:'):
            errs.append('%s text 要从 Scene: 起头' % k)
        n = len(t.split())
        if t and not 150 <= n <= 460:
            looks.append('%s text %d 个词（示例是两百到三百八）' % (k, n))
        for f in ('text', 'light', 'camera'):
            m = BAN_EN.search(s.get(f) or '')
            if m:
                errs.append('%s %s 里有不该有的词：%s' % (k, f, m.group(0)))
        if re.search(r'[一-鿿]', t + (s.get('light') or '') + (s.get('camera') or '')):
            errs.append('%s text、light、camera 里有汉字' % k)
        minors = [key2name.get(p[0], p[0]) for p in ppl if isinstance(p, list) and (ages.get(key2name.get(p[0])) or 99) < 18]
        if s.get('raw') and minors and not death:
            looks.append('%s raw 是 true，画里有未满十八岁的 %s，确认受伤的不是他' % (k, '、'.join(minors)))
        return k

    got = {}
    for s in d.get('nodes', []):
        k = scene(s)
        got[k] = (s.get('line'), s.get('act'))
    for k, v in want.items():
        if k not in got:
            errs.append('缺 %s（%s %s）' % (k, v[0], v[1]))
        elif got[k] != v:
            errs.append('%s 的 line、act 写的是 %s，任务单是 %s' % (k, got[k], v))
    for k in got:
        if k not in want and got[k] not in want.values():
            errs.append('%s 的 line、act %s 不是这个时代的哪一幕' % (k, got[k]))
    extra = {s.get('key') for s in d.get('nodes', []) if s.get('extra')}      # 主会话另添的（一幕配两幅）
    for k in got:
        if k not in want and k not in extra:
            errs.append('%s 不在任务单的键里' % k)
    for s in d.get('deaths', []):
        if s.get('same'):      # 档案里挂的就是某一幅节点原画，不另出图
            if s['same'] not in got:
                errs.append('%s same 指的 %s 不在节点里' % (s.get('key'), s['same']))
            if s.get('death') not in (d.get('fates') or {}):
                errs.append('%s fates 里没有「%s」' % (s.get('key'), s.get('death')))
            continue
        k = scene(s, death=True)
        if not re.match(r'^%s_d_[a-z0-9_]+$' % eid, k):
            errs.append('%s 死的那一刻的键要写成 %s_d_xxx' % (k, eid))
        if s.get('death') not in cast_names:
            errs.append('%s death「%s」不在这一段的旅伴里' % (k, s.get('death')))
        if not isinstance(s.get('age'), (int, float)):
            errs.append('%s 缺 age（死的时候几岁）' % k)
        elif s['age'] < 18:
            if not s.get('minor'):
                errs.append('%s 死的时候 %s 岁，要写 minor: true' % (k, s['age']))
            if s.get('raw'):
                errs.append('%s 未满十八岁，不能 raw' % k)
            if s['age'] < 15:
                errs.append('%s 十四岁以下不出图，拿掉这一幅，在 notes 里写一句' % k)
        if s.get('death') not in (d.get('fates') or {}):
            errs.append('%s 有死的那一刻，fates 里没有「%s」' % (k, s.get('death')))
    dup = sorted({n for n in names if n and names.count(n) > 1})
    if dup:
        errs.append('name 重了：' + '、'.join(dup))
    for n, f in (d.get('fates') or {}).items():
        if n not in ages:
            errs.append('fates「%s」不在这一段的旅伴和相遇里' % n)
        for x in ('when', 'where', 'how'):
            if not f.get(x):
                errs.append('fates「%s」缺 %s' % (n, x))
        txt = ''.join(str(f.get(x, '')) for x in ('when', 'where', 'how', 'label'))
        if BAN_ZH.search(txt):
            errs.append('fates「%s」里有禁用的标点' % n)
        if re.search(r'玩家|AI|裁定|条目|正史|旅伴|主线', txt):
            errs.append('fates「%s」里有给模型看的字眼' % n)
        if len(f.get('how', '')) > 130:
            looks.append('fates「%s」how %d 个字，偏长' % (n, len(f['how'])))
    print('%s：节点 %d／%d，死期 %d，死的那一刻 %d' % (eid, len(got), len(want), len(d.get('fates') or {}), len(d.get('deaths') or [])))
    return errs, looks


if __name__ == '__main__':
    moon = json.load(open(os.path.join(BOOK, 'data', 'strife.json'), encoding='utf-8'))
    ids = sys.argv[1:] or sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(HERE, 's??.json')))
    bad = 0
    for eid in ids:
        errs, looks = check(eid, moon)
        for e in errs:
            print('  错｜' + e)
        for e in looks:
            print('  看｜' + e)
        bad += len(errs)
    print('错合计', bad)
    sys.exit(1 if bad else 0)
