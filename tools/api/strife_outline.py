#!/usr/bin/env python3
# 纷争纪主线改稿大纲（11-21，用户选了“重”）：九份交 Opus 批处理，一份一页（第四、五页各两份），照 底稿/审稿/纷争纪/派活说明_大纲.md。
# 材料：页头和时段总纲、这一页的史诗、方向稿第六节逐张、要改的主线、这一份的审稿、写作口径几节、三份记忆。
#   python -I -X utf8 tools/api/strife_outline.py build|submit|wait
# 交稿写 底稿/审稿/纷争纪/大纲_<份名>.md。
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import review_batch as rb  # noqa: E402
import strife_review as SR  # noqa: E402

D = SR.D
BP = os.path.join(D, 'batch_outline.json')


def songs(t):
    return '\n'.join(b for h, b in SR.blocks(t) if '（史诗·纷争纪）' in h)


def build():
    guide = SR.rd(os.path.join(D, '派活说明_大纲.md'))
    fx = SR.rd(os.path.join(rb.ROOT, '纷争纪', '纷争纪_方向与写法_第二版.md'))
    cards = rb.section(fx, r'^## 六、逐张', r'^## 七、')
    cl = SR.rd(os.path.join(rb.ROOT, 'CLAUDE.md'))
    rules = '\n\n'.join(rb.section(cl, p, r'^### ') for p in [r'^### 尺度、高魔和命路', r'^### 玩家在场', r'^### 什么杀得死传奇', r'^### 怎么踏进传奇', r'^### 润色口径'])
    mem = '\n\n'.join(re.sub(r'^---.*?---\n', '', SR.rd(os.path.join(SR.MEM, f)), flags=re.S) for f in
                      ['plots-need-onstage-antagonist.md', 'gm-outline-brief-and-superhuman-scale.md', 'create-grand-restrain-only-gm-rules.md', 'legend-death-only-four-ways.md'])
    system = '你给一张日式西幻 JRPG 跑团卡《奥尔德兰的旅印》的纷争纪写主线改稿大纲，全程用中文。下面是这一回的派活说明，照它做。\n\n' + guide
    reqs = []
    for name, n, names in SR.JOBS:
        t = SR.page_text(n)
        mains, k = SR.mains_of(t, names)
        review = SR.rd(os.path.join(D, '审_%s.md' % name))
        task = '你这一份的份名是「%s」，给纷争纪第%s页的 %d 条主线（%s）出改稿大纲。' % (
            name, '一二三四五六七'[n - 1], k, '全部' if not names else '、'.join(names))
        user = '\n\n'.join([
            '# 你的活\n\n' + task,
            '# 写作口径里的几节\n\n' + rules,
            '# 用户另外定过的几条（记忆原文）\n\n' + mem,
            '# 方向稿第六节 逐张（二十二张的牌，正史，不动）\n\n' + cards,
            '# 这一页的页头和时段总纲\n\n' + SR.head_of(t),
            '# 这一页的史诗（歌，正史，不动）\n\n' + songs(t),
            '# 这一份的审稿\n\n' + review,
            '# 你要改的主线（原文，带裁定锁和旅伴名单）\n\n' + mains,
        ])
        reqs.append({'custom_id': 'outline_%d' % len(reqs), 'params': {
            'model': rb.MODEL, 'max_tokens': 96000, 'thinking': {'type': 'adaptive'}, 'output_config': {'effort': 'high'},
            'system': system, 'messages': [{'role': 'user', 'content': user}]}})
    return reqs


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    cmd = sys.argv[1]
    if cmd == 'build':
        for r, j in zip(build(), SR.JOBS):
            print(j[0], len(r['params']['system']) + len(r['params']['messages'][0]['content']))
    elif cmd == 'submit':
        reqs = build()
        d = json.loads(rb.call(rb.API, {'requests': reqs}))
        json.dump({'id': d['id'], 'jobs': [j[0] for j in SR.JOBS]}, open(BP, 'w', encoding='utf-8'), ensure_ascii=False)
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
            tin += msg['usage']['input_tokens']
            tout += msg['usage']['output_tokens']
            text = ''.join(c.get('text', '') for c in msg['content'] if c.get('type') == 'text')
            open(os.path.join(D, '大纲_%s.md' % name), 'w', encoding='utf-8', newline='\n').write(text.strip() + '\n')
            print('%s：%d 字，停在 %s' % (name, len(text), msg.get('stop_reason')))
        print('进 %d、出 %d token，约 $%.2f' % (tin, tout, (tin * rb.PRICE[0] + tout * rb.PRICE[1]) / 1e6 / 2))
