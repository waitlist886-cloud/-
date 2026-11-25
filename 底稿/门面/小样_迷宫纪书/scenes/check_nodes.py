#!/usr/bin/env python3
# 查 scenes/nN.json（主线各幕的节点原画场面，11-25）合不合规矩。照山铜纪那一本的 check_scenes.py 改的。
#   python -I -X utf8 check_nodes.py [n1 n4 …]（不写就查全部）
# 报“错”的要改；报“看”的自己看一眼，有来由就留着。末尾打一行各页写了几幅、头一轮几幅。
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
SETS = ['立绘_前传', '立绘_v3', '立绘_山铜纪', '立绘_纷争纪', '立绘_月银纪史诗', '立绘_诸国期', '立绘_萨尔维斯']
ACTS = ['一幕', '二幕', '三幕', '收束']
BAN_EN = re.compile(r'\b(moon\w*|crescent\w*|kimono|katana|pagoda|hanfu|chinese|japanese|samurai|ninja|rifle|pistol|musket|firearm|revolver|crucifix|cross-shaped)\b', re.I)
BIG = re.compile(r'之战|对决|决战|觉醒|羁绊|命运|绝望|希望|月亮|月光|新月|满月|残月|月牙|弦月')
HAN = re.compile(r'^[一-鿿]{2,4}$')
TWIST = re.compile(r'three-quarter (?:view )?from behind|over (?:his|her|their) shoulder at us|looks? back at us|glanc\w+ back', re.I)


def por(key):
    for s in SETS:
        p = os.path.join(COMFY, 'out', s, key)
        if os.path.isdir(p):
            return p
    return None


def beast_path(name):
    if name.startswith('god_'):
        return os.path.join(COMFY, 'out', '神明显像', name + '.png')
    if name.startswith('dragon_'):
        return os.path.join(COMFY, 'out', '真龙原形', name + '.png')
    return os.path.join(COMFY, 'out', '史诗战', 'maze', name + '.png')


def main():
    data = json.load(open(os.path.join(BOOK, 'data', 'maze.json'), encoding='utf-8'))
    eras = {e['id']: e for e in data['eras']}
    pages = [a for a in sys.argv[1:]] or sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(HERE, 'n?.json')))
    allnames, total, leads, nerr = {}, 0, 0, 0
    used = set(l.get('task', '') for e in data['eras'] for l in e['lines']) | set(l['name'].split('·')[-1] for e in data['eras'] for l in e['lines'])
    for pg in pages:
        errs, looks = [], []
        path = os.path.join(HERE, pg + '.json')
        try:
            raw = open(path, 'rb').read()
            if raw[:3] == b'\xef\xbb\xbf':
                errs.append('文件带 BOM')
            d = json.loads(raw.decode('utf-8-sig'))
        except Exception as e:
            print(pg, '读不了：', e)
            nerr += 1
            continue
        eid = d.get('era')
        if eid not in eras or eid[1:] != pg[1:]:
            errs.append('era 不对：%s' % eid)
            continue
        era = eras[eid]
        want = {}
        for l in era['lines']:
            acts = [a.split('｜')[0] for a in l['acts'] if not a.startswith('幕间')]
            for i, a in enumerate(acts):
                want['%s%d' % (l['mural'], i + 1)] = (l['name'], a)
        ages = {c.get('key'): c.get('age') for c in era.get('cast', []) + era.get('meet', []) if c.get('key')}
        got, lead_of = {}, {}
        for s in d.get('nodes', []):
            k = s.get('key', '？')
            for f in ('key', 'line', 'act', 'name', 'style', 'light', 'camera', 'text'):
                if not s.get(f):
                    errs.append('%s 缺 %s' % (k, f))
            if k in got:
                errs.append('%s 键重了' % k)
            got[k] = (s.get('line'), s.get('act'))
            nm = s.get('name', '')
            if nm and not HAN.match(nm):
                errs.append('%s name「%s」不是两到四个汉字' % (k, nm))
            if BIG.search(nm):
                errs.append('%s name「%s」用了大词或月相字' % (k, nm))
            if nm in allnames:
                errs.append('%s name「%s」跟 %s 重了' % (k, nm, allnames[nm]))
            if nm in used:
                looks.append('%s name「%s」跟主线名或任务名一样' % (k, nm))
            allnames[nm] = k
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
                elif p[1] not in CELLS or not os.path.exists(os.path.join(d_, 'cell_%s.png' % p[1])) or not os.path.exists(os.path.join(d_, 'art.png')):
                    errs.append('%s %s 没有 %s 那一套或者没有艺术照' % (k, p[0], p[1]))
                if p[2].lower() not in (s.get('text') or '').lower():
                    looks.append('%s 叫法「%s」在 text 里没出现' % (k, p[2]))
            n_ref = 2 + (1 if s.get('row') else len(s.get('who') or [])) + (1 if s.get('beast') else 0)
            if n_ref > 5:
                errs.append('%s 参考图 %d 张，超了五张' % (k, n_ref))
            if s.get('row') and len(s['row']) > 8:
                errs.append('%s row 超过八个人' % k)
            if s.get('beast') and not os.path.exists(beast_path(s['beast'])):
                errs.append('%s beast %s 没有这张图' % (k, s['beast']))
            if s.get('like'):
                lk = s['like']
                if not (isinstance(lk, list) and len(lk) == 2):
                    errs.append('%s like 要写成 [键, 画里是谁]' % k)
                elif n_ref >= 5 or s.get('beast'):
                    looks.append('%s 有 like 可参考图已经满了或者有 beast，like 用不上' % k)
            t = s.get('text') or ''
            if t and not t.startswith('Scene:'):
                errs.append('%s text 要从 Scene: 起头' % k)
            n = len(t.split())
            if t and not 140 <= n <= 460:
                looks.append('%s text %d 个词' % (k, n))
            for f in ('text', 'light', 'camera'):
                m = BAN_EN.search(s.get(f) or '')
                if m:
                    errs.append('%s %s 里有不该有的词：%s' % (k, f, m.group(0)))
            m = TWIST.search(t)
            if m:
                looks.append('%s 朝向可能写成了背加侧脸：%s' % (k, m.group(0)))
            if re.search(r'[一-鿿]', t + (s.get('light') or '') + (s.get('camera') or '')):
                errs.append('%s text、light、camera 里有汉字' % k)
            minors = [p[0] for p in ppl if isinstance(p, list) and (ages.get(p[0]) or 99) < 18]
            if s.get('raw') and minors:
                looks.append('%s raw 是 true，画里有未满十八岁的 %s，确认受伤的不是他' % (k, '、'.join(minors)))
            if s.get('lead'):
                if s.get('line') in lead_of:
                    errs.append('%s 这一条主线有两幅 lead（另一幅 %s）' % (k, lead_of[s['line']]))
                lead_of[s.get('line')] = k
        for k, v in got.items():
            if k not in want:
                errs.append('%s 不是这一页的键' % k)
            elif want[k] != v:
                errs.append('%s 的 line、act 写的是 %s，该是 %s' % (k, v, want[k]))
        miss = [k for k in want if k not in got]
        nolead = [l['name'] for l in era['lines'] if l['name'] not in lead_of and any(v[0] == l['name'] for v in got.values())]
        if nolead:
            errs.append('没标 lead 的主线：' + '、'.join(nolead))
        total += len(got)
        leads += len(lead_of)
        nerr += len(errs)
        print('%s（%s）：写了 %d／%d 幅，头一轮 %d／%d 条；错 %d，看 %d%s' % (pg, era['title'], len(got), len(want), len(lead_of), len(era['lines']), len(errs), len(looks),
                                                            ('；还没写的 ' + ' '.join(miss[:30]) + (' …' if len(miss) > 30 else '')) if miss else ''))
        for e in errs:
            print('  错', e)
        for e in looks:
            print('  看', e)
    print('合计：场面', total, '幅，头一轮', leads, '幅，错', nerr)
    return 1 if nerr else 0


if __name__ == '__main__':
    sys.exit(main())
