#!/usr/bin/env python3
# 山铜纪战装分档（11-21）：用户看了战装补层的样张说照位阶和家境分开、照各人偏好区分（风尚文档 山铜纪 战装分档、各段 战装补层）。
# 山铜纪全部立绘资料交 Opus 批处理，一人判位阶、家境、偏好，改写 battle 那一句（旧句留进 battle_old）。
#   python -I -X utf8 底稿/立绘/tools/war_batch.py mat|build|submit|wait|take [--apply]
# 材料和交稿在 底稿/立绘/战装_11-21/。密钥照 claude_api 取，不打印。
import glob
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'api'))
import review_batch as rb  # noqa: E402

W = os.path.join(ROOT, '底稿', '立绘', '战装_11-21')
W = os.path.join(W, os.environ['WAR_SUB']) if os.environ.get('WAR_SUB') else W   # 补跑几个人另放一个子目录
ONLY = set(filter(None, os.environ.get('WAR_ONLY', '').split(',')))   # 只跑这几个键（整张重出排着的，cell 不在也算）
CAST = os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'cast', '山铜纪')
OUTD = os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'out', '立绘_山铜纪')
MODEL = 'claude-opus-5-5'
CHUNK = 16
PERIOD = {'一': '犁的年月（2到300年）', '二': '长夜的年月（301到579年）', '三': '白鸦的年月（580到660年）', '四': '黎明的年月（661到741年）',
          '五': '七城的年月（742到861年）', '六': '麦的年月（862到947年）'}
KEYS = r'(身份|底座|位阶|能力|装束|出身|家|兼修|类别|是谁|样子|做派|本事)'
SAMPLES = ['s1n_sirin', 's2n_lennart', 's3n_linhart', 's4n_cordula', 's5n_corvin', 's6n_hogel']


def rd(p):
    return open(p, encoding='utf-8').read().replace('\r\n', '\n')


def section(t, a, b):
    i = re.search(a, t, re.M).start()
    m = re.search(b, t[i + 1:], re.M)
    return t[i:i + 1 + m.start()] if m else t[i:]


_pages = {}


def page(f):
    if f not in _pages:
        _pages[f] = rd(os.path.join(ROOT, f)).split('\n')
    return _pages[f]


def entry(x):
    """原页里这个人自己那一条（## 标题带他名字的那一块），抽身份、底座、能力、装束那几行。找不到就取出处那一行前后。"""
    f, _, ln = x['src'].partition(':')
    L = page(f)
    names = [n for n in {x['name'], x['name'].split('·')[0], x.get('same_as') or '', x.get('alias') or ''} if len(n) >= 2]
    def block(i):
        j = i + 1
        while j < len(L) and not L[j].startswith('## '):
            j += 1
        keep = [s for s in L[i + 1:j] if re.match(r'^[-\s]*' + KEYS, s) or s.startswith('【能力')]
        if not keep:    # 成段写的人物条：取开头
            keep = [s for s in L[i + 1:j] if s.strip() and not s.startswith('【调用】') and not s.startswith('> 条目设置')]
        return L[i] + '\n' + '\n'.join(s[:260] for s in keep)[:1400]

    heads = [i for i, l in enumerate(L) if l.startswith('## ') and '主线' not in l and any(n in l for n in names)]
    if heads:
        return block(heads[0])
    full = [n for n in names if '·' in n] or names     # 凡世至强条的标题写的是传奇之名，本名在开头几行里
    for i, l in enumerate(L):
        if l.startswith('## ') and '主线' not in l and '命星' not in l and '裁定锁' not in l and any(n in s for s in L[i + 1:i + 8] for n in full):
            return block(i)
    n = int(ln) - 1 if ln.isdigit() else -1
    while n > 0 and not L[n].startswith('## '):     # 出处那一行所在的那一条
        n -= 1
    if n > 0:
        return block(n)
    return '（没找到他自己那一条）'


def people():
    out = []
    for p in sorted(glob.glob(os.path.join(CAST, '*.json'))):
        for x in json.load(open(p, encoding='utf-8')):
            if ONLY:
                if x['en'] in ONLY:
                    out.append((os.path.basename(p)[:-5], x))
                continue
            if not os.path.exists(os.path.join(OUTD, x['en'], 'cell_battle.png')):
                continue          # 没出图的（未成年那一档等）不改
            out.append((os.path.basename(p)[:-5], x))
    return out


def mat():
    os.makedirs(os.path.join(W, '材料'), exist_ok=True)
    by = {}
    for fn, x in people():
        f = x['src'].split(':')[0]
        pn = re.search(r'时段_(.)_', f).group(1)
        by.setdefault(pn, []).append(x)
    for pn, arr in by.items():
        blocks = []
        for x in arr:
            b = ['【%s】%s（%s，%s）' % (x['en'], x['name'], x['sex'], x['tier'])]
            if x.get('same_as'):
                b.append('同一个人在别处也有立绘：%s（跨页的战装跟着位阶走，偏好不变）' % x['same_as'])
            if x.get('legend'):
                b.append('传奇')
            b.append('长相（英文资料）：' + x['who'][:600])
            b.append('常服：' + x['casual'][:400])
            b.append('现在的战装（要改写的这一句）：' + x.get('battle_old', x['battle']))
            if x.get('battle_pose'):
                b.append('第三格另有姿势句（不改，照它对得上）：' + x['battle_pose'][:300])
            b.append('原页里他那一条：\n' + entry(x))
            blocks.append('\n'.join(b))
        head = '# 山铜纪第%s页 %s：' % (pn, PERIOD[pn]) + '%d 人\n\n' % len(arr)
        open(os.path.join(W, '材料', 'p%s.md' % '一二三四五六'.index(pn).__add__(1)), 'w', encoding='utf-8', newline='\n').write(
            head + '\n'.join('=' * 20 + '\n' + b + '\n' for b in blocks))
        print('第%s页' % pn, len(arr), '人')


def samples():
    out = []
    for p in sorted(glob.glob(os.path.join(CAST, 's?n.json'))):
        for x in json.load(open(p, encoding='utf-8')):
            if x['en'] in SAMPLES:
                out.append('- %s %s\n  改前：%s\n  改后：%s' % (x['en'], x['name'], x['battle_old'], x['battle']))
    return '\n'.join(out)


def system():
    fashion = section(rd(os.path.join(ROOT, '底稿', '立绘', '各时代风尚_新三纪.md')), r'^## 三、山铜纪', r'^## 四、')
    war = section(rd(os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'era_fashion.py')), r'^WAR_LEAD', r'^def war')
    rank = section(rd(os.path.join(ROOT, 'CLAUDE.md')), r'^### 命星', r'^### 时段页的格式')
    rank = '\n'.join(l for l in rank.split('\n') if l.startswith('- 位阶'))
    return ('你给一张日式西幻 JRPG 跑团卡《奥尔德兰的旅印》改写角色立绘第三格（战斗那一身）的英文描述。这一纪是山铜纪，纷争纪那场高魔大战刚过去，'
            '附魔铠甲修好了卖只要几枚金币，魔晶落价，机兵零件和遗迹里的东西满地都是。用户看了旧图说战装比起时代的军事和科技太落后，又看了六张样张回“基本可以”，'
            '要照位阶和家境分开、照各人偏好区分。全程照下面这一纪的风尚，尤其开头那一条「战装分档」和各段末尾的「战装补层」。\n\n'
            '# 这一纪的风尚\n\n' + fashion + '\n\n# 出图脚本里各段的战装层（英文，给你参考用词）\n\n```python\n' + war + '\n```\n\n# 位阶\n\n' + rank +
            '\n\n# 用户认过的六张样张（改前、改后）\n\n' + samples() + '\n\n'
            '# 怎么改\n\n'
            '- 先从原页那一条和长相里判三样：位阶（原页底座或位阶那一行；没写的照身份和本事估，写明是估的），家境（贫、中、富、世家或上城，看出身和身份），偏好（照常、朴素、不靠装备、法袍、不打仗……，有来由才判不照常）。'
            '再定装备档 1 到 5：1 干活的衣服外头一两件捡来的附魔件，2 一套改合身的旧附魔甲，3 成套的附魔战装加一件招牌，4 量身打造、设计过的，5 这一纪顶上的那一身。位阶定底子，家境低位阶时加减一到两档，极境以上至多一档，英雄往上不看家境；偏好朴素的照档用好料子，样子去装饰，偏好不靠装备的就别硬穿甲。\n'
            '- 改写那一句：英文，跟样张一样的详略（七八十到一百二十个词），开头保留原句的场面短语（Holding the crossing: 这一类），兵器、手里拿的东西、姿势、法术光效、跟故事有关的物件一样不丢、不换，'
            '只把衣甲升到那一档，写清每一件是什么、哪里发光、什么颜色的符文。资料的配色照旧。西边862年以前没有火药枪，东边从来不用火药（铳是施法的家什），山铜纪没有电。'
            '不写脸、头发、眼睛、身材，那些出图时另有。不写东方式样（交领、宽袖、盘扣）。\n'
            '- 原句本来就不是打仗的（修士、孩子、文书、不出手的人），照这个人的路子：可以只是一件附魔披风、一枚护符、法袍上的符文，或者不改，写明为什么。\n'
            '- 同一个人在别的页也有立绘的（同一个 same_as），战装跟着他那时的位阶走，偏好前后一样。\n'
            '- 六张样张那几位也在材料里，照分档再判一回，档对得上就照样张那一句交回，对不上就改。\n\n'
            '# 交什么\n\n一个 ```json 代码块，里面是一个数组，一人一条：{"en": "…", "rank": "灵格（估）", "wealth": "贫", "pref": "照常", "level": 2, "why": "一句中文，为什么是这一档、这个偏好", "battle": "改写后的英文"}。材料里每个人都要有一条，次序照材料。前后不加别的话。')


def jobs():
    out = []
    for f in sorted(glob.glob(os.path.join(W, '材料', '*.md'))):
        pg = os.path.basename(f)[:-3]
        head, *items = rd(f).split('=' * 20 + '\n')
        for i in range(0, len(items), CHUNK):
            part = items[i:i + CHUNK]
            out.append(('%s_%d' % (pg, i // CHUNK + 1), head.replace('：', '（这一份 %d 人）：' % len(part), 1) + '\n'.join('=' * 20 + '\n' + x for x in part)))
    return out


def build():
    s = system()
    reqs, names = [], []
    for name, body in jobs():
        reqs.append({'custom_id': 'war_%d' % len(reqs), 'params': {
            'model': MODEL, 'max_tokens': 64000, 'output_config': {'effort': 'medium'}, 'thinking': {'type': 'adaptive'},
            'system': s, 'messages': [{'role': 'user', 'content': body}]}})
        names.append(name)
    return reqs, names


BP = os.path.join(W, 'batch.json')


def take(apply):
    got = {}
    want = {x['en'] for _, x in people()}
    # 有几份把 en 写成了英文名，或者键后头跟了英文名：照资料 who 开头的英文名对回键，同名的（跨页的巴尔缇娜）取这一份那一页的
    eng = {}
    for _, x in people():
        eng.setdefault(re.split(r'[,(]', x['who'])[0].strip().lower(), []).append(x['en'])
    HAND = {'the stranger who threw': 's2b_thrower', 'the emperor of the sword-holding': 's2b_emperor'}
    for f in sorted(glob.glob(os.path.join(W, '交稿', '*.md'))):
        m = re.search(r'```json\s*\n(.*?)\n```', rd(f), re.S)
        if not m:
            print('！没有 json', os.path.basename(f))
            continue
        pg = 's' + os.path.basename(f)[1]
        for d in json.loads(m.group(1)):
            k = d['en']
            if k not in want:
                k1, kl = k.split(' ')[0], k.lower()
                hit = [k1] if k1 in want else [HAND[kl]] if kl in HAND else [e for n, es in eng.items() for e in es if n and (n == kl or n.startswith(kl) or kl in n)]
                if len(hit) > 1:
                    hit = [e for e in hit if e.startswith(pg)]
                if len(hit) > 1:
                    hit = [e for n, es in eng.items() for e in es if n == kl and e in hit] or hit
                if len(hit) > 1:
                    hit = [e for e in hit if e not in got and not any(g.get('en') == e for g in [])]
                if len(hit) > 1:
                    hit = [e for e in hit if '_child' not in e and e not in got]
                if len(hit) != 1:
                    print('！对不回', os.path.basename(f), k, hit)
                    continue
                d = dict(d, en=hit[0])
            if d['en'] in got:
                print('！重了', d['en'])
            got[d['en']] = d
    print('交回', len(got), '要', len(want), '缺', sorted(want - set(got)), '多', sorted(set(got) - want))
    lv = {}
    for d in got.values():
        lv[d.get('level')] = lv.get(d.get('level'), 0) + 1
    print('各档人数', dict(sorted(lv.items(), key=lambda kv: str(kv[0]))))
    json.dump(got, open(os.path.join(W, '收稿.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    if not apply:
        return
    for p in sorted(glob.glob(os.path.join(CAST, '*.json'))):
        arr = json.load(open(p, encoding='utf-8'))
        n = 0
        for x in arr:
            d = got.get(x['en'])
            if d and d.get('battle'):
                x.setdefault('battle_old', x['battle'])
                x['battle'] = d['battle']
                x['gear'] = '%s｜%s｜%s｜%s档｜%s' % (d.get('rank'), d.get('wealth'), d.get('pref'), d.get('level'), d.get('why'))
                n += 1
        if n:
            json.dump(arr, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
            print('写了', os.path.basename(p), n)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    cmd = sys.argv[1]
    if cmd == 'mat':
        mat()
    elif cmd == 'build':
        reqs, names = build()
        for r, n in zip(reqs, names):
            print(n, len(r['params']['messages'][0]['content']))
        print('系统提示', len(reqs[0]['params']['system']), '共', len(reqs), '份')
    elif cmd == 'submit':
        reqs, names = build()
        d = json.loads(rb.call(rb.API, {'requests': reqs}))
        json.dump({'id': d['id'], 'jobs': names}, open(BP, 'w', encoding='utf-8'), ensure_ascii=False)
        print('交上去了：', d['id'], len(reqs), '份')
    elif cmd == 'wait':
        b = json.load(open(BP, encoding='utf-8'))
        while True:
            d = json.loads(rb.call(rb.API + '/' + b['id']))
            if d.get('processing_status') == 'ended':
                break
            time.sleep(60)
        os.makedirs(os.path.join(W, '交稿'), exist_ok=True)
        tin = tout = 0
        for line in rb.call(d['results_url']).splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            n = b['jobs'][int(r['custom_id'].rsplit('_', 1)[1])]
            if r['result']['type'] != 'succeeded':
                print('！没成', n)
                continue
            msg = r['result']['message']
            tin += msg['usage']['input_tokens']
            tout += msg['usage']['output_tokens']
            open(os.path.join(W, '交稿', n + '.md'), 'w', encoding='utf-8', newline='\n').write(''.join(c.get('text', '') for c in msg['content'] if c.get('type') == 'text'))
        print('进 %d、出 %d token，约 $%.2f' % (tin, tout, (tin * 4 + tout * 20) / 1e6 / 2))
    elif cmd == 'take':
        take('--apply' in sys.argv)
