#!/usr/bin/env python3
# 纷争纪剧情审稿走 API 批处理（11-21）。照 review_batch.py（迷宫纪前传那一回）改的：七页主线分九份，派活说明当 system，
# 方向稿几节、写作口径几节、三份记忆、页头和时段总纲、主线和裁定锁、旅伴身份一行当 user。
#   python -I -X utf8 tools/api/strife_review.py build|submit|wait
# 交稿写 底稿/审稿/纷争纪/审_<份名>.md。只用标准库；密钥照 claude_api.key() 取，不打印。
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import review_batch as rb  # noqa: E402

ROOT = rb.ROOT
D = os.path.join(ROOT, '底稿', '审稿', '纷争纪')
MEM = os.path.join(os.path.expanduser('~'), '.claude', 'projects', 'E--aldran-art', 'memory')
PAGES = {1: '一_灰', 2: '二_白石', 3: '三_灯', 4: '四_炮', 5: '五_浮塔', 6: '六_铁狼', 7: '七_号角'}
JOBS = [('灰', 1, None), ('白石', 2, None), ('灯', 3, None),
        ('炮上', 4, ['箭与冠的秤', '最后一垄', '白鸢的天', '无继之光']), ('炮下', 4, ['空鞍的白马', '第七座营垒', '不熄火', '锈花']),
        ('浮塔上', 5, ['北归道', '盐门', '离地', '塔与剑']), ('浮塔下', 5, ['松开的锁链', '射主', '南七段', '三枚日轮', '落尽']),
        ('铁狼', 6, None), ('号角', 7, None)]


def rd(p):
    return open(p, encoding='utf-8').read().replace('\r\n', '\n')


def page_text(n):
    f = [x for x in os.listdir(os.path.join(ROOT, '纷争纪')) if x.startswith('纷争纪时段_' + PAGES[n])][0]
    return rd(os.path.join(ROOT, '纷争纪', f))


def blocks(t):
    """按 ## 切块，回 [(标题, 全文)]。"""
    parts = re.split(r'(?=^## )', t, flags=re.M)
    return [(p.split('\n', 1)[0], p) for p in parts if p.startswith('## ')]


def head_of(t):
    """页头（第一个 ## 以前）和时段总纲（## 纷争纪·时段｜ 连同后头的裁定锁）。"""
    out = [t[:t.index('\n## ')]]
    bs = blocks(t)
    for i, (h, b) in enumerate(bs):
        if h.startswith('## 纷争纪·时段｜'):
            out.append(b)
            if i + 1 < len(bs) and bs[i + 1][0].startswith('## 裁定锁'):
                out.append(bs[i + 1][1])
    return '\n'.join(out)


def mains_of(t, names):
    bs = blocks(t)
    out = []
    for i, (h, b) in enumerate(bs):
        if not h.startswith('## 纷争纪·主线｜'):
            continue
        name = h.split('·', 2)[-1].strip()
        if names and name not in names:
            continue
        sec = [b]
        j = i + 1
        while j < len(bs) and bs[j][0].startswith('## 裁定锁'):
            sec.append(bs[j][1])
            j += 1
        who = []           # 这一条的旅伴：身份一行
        while j < len(bs) and not bs[j][0].startswith('## 纷争纪·主线｜'):
            hh, bb = bs[j]
            if hh.startswith('## 旅途同行：'):
                m = re.search(r'^身份：(.*)$', bb, re.M)
                who.append('- %s｜%s' % (hh[8:], (m.group(1)[:200] if m else '')))
            j += 1
        out.append(''.join(sec) + ('\n### 这一条的旅伴（只有身份一行）\n\n' + '\n'.join(who) + '\n' if who else ''))
    if names:
        assert len(out) == len(names), (names, len(out))
    return '\n'.join(out), len(out)


def build():
    guide = rd(os.path.join(D, '派活说明.md'))
    fx = rd(os.path.join(ROOT, '纷争纪', '纷争纪_方向与写法_第二版.md'))
    direction = rb.section(fx, r'^## 一句话', r'^## 四、')
    cl = rd(os.path.join(ROOT, 'CLAUDE.md'))
    rules = '\n\n'.join(rb.section(cl, p, r'^### ') for p in [r'^### 尺度、高魔和命路', r'^### 玩家在场', r'^### 什么杀得死传奇', r'^### 怎么踏进传奇', r'^### 润色口径'])
    mem = '\n\n'.join(re.sub(r'^---.*?---\n', '', rd(os.path.join(MEM, f)), flags=re.S) for f in
                      ['plots-need-onstage-antagonist.md', 'gm-outline-brief-and-superhuman-scale.md', 'create-grand-restrain-only-gm-rules.md'])
    system = '你是审稿人，全程用中文。下面是这一回的派活说明，照它做。\n\n' + guide
    reqs = []
    for name, n, names in JOBS:
        t = page_text(n)
        mains, k = mains_of(t, names)
        task = '你这一份的份名是「%s」，审纷争纪第%s页的 %d 条主线（%s）。末尾「这一份共有的」只就你这几条说。' % (
            name, '一二三四五六七'[n - 1], k, '全部' if not names else '、'.join(names))
        user = '\n\n'.join([
            '# 你的活\n\n' + task,
            '# 纷争纪方向与写法第二版（一句话到第三节）\n\n' + direction,
            '# 写作口径里的几节\n\n' + rules,
            '# 用户另外定过的三条（记忆原文）\n\n' + mem,
            '# 这一页的页头和时段总纲\n\n' + head_of(t),
            '# 你要审的主线（一条一个「## 纷争纪·主线｜」，后头跟着它的裁定锁和旅伴名单）\n\n' + mains,
        ])
        reqs.append({'custom_id': 'strife_%d' % len(reqs), 'params': {
            'model': rb.MODEL, 'max_tokens': 96000, 'thinking': {'type': 'adaptive'}, 'output_config': {'effort': 'high'},
            'system': system, 'messages': [{'role': 'user', 'content': user}]}})
    return reqs


BP = os.path.join(D, 'batch.json')

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    cmd = sys.argv[1]
    if cmd == 'build':
        for r, j in zip(build(), JOBS):
            print(j[0], len(r['params']['system']) + len(r['params']['messages'][0]['content']))
    elif cmd == 'submit':
        reqs = build()
        d = json.loads(rb.call(rb.API, {'requests': reqs}))
        json.dump({'id': d['id'], 'jobs': [j[0] for j in JOBS]}, open(BP, 'w', encoding='utf-8'), ensure_ascii=False)
        print('交上去了：', d['id'], len(reqs), '份')
    elif cmd == 'wait':
        b = json.load(open(BP, encoding='utf-8'))
        while True:
            d = json.loads(rb.call(rb.API + '/' + b['id']))
            if d.get('processing_status') == 'ended':
                break
            time.sleep(60)
        tin = tout = 0
        for line in rb.call(d['results_url']).splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            name = b['jobs'][int(r['custom_id'].rsplit('_', 1)[1])]
            if r['result']['type'] != 'succeeded':
                print('！没成', name)
                continue
            msg = r['result']['message']
            u = msg['usage']
            tin += u['input_tokens']
            tout += u['output_tokens']
            text = ''.join(c.get('text', '') for c in msg['content'] if c.get('type') == 'text')
            open(os.path.join(D, '审_%s.md' % name), 'w', encoding='utf-8', newline='\n').write(text.strip() + '\n')
            print('%s：%d 字，停在 %s' % (name, len(text), msg.get('stop_reason')))
        print('进 %d、出 %d token，约 $%.2f' % (tin, tout, (tin * rb.PRICE[0] + tout * rb.PRICE[1]) / 1e6 / 2))
