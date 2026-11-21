#!/usr/bin/env python3
# 纷争纪改稿定数（11-21）：九份大纲末尾要定的事交 Opus 逐件查原页定下来，照 底稿/审稿/纷争纪/派活说明_定数.md。
# 材料：这一份的大纲、这一页除命星那一节以外的全文、方向稿第六节、写作口径几节。
#   python -I -X utf8 tools/api/strife_settle.py build|submit|wait      交稿写 底稿/审稿/纷争纪/定数_<份名>.md
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import review_batch as rb  # noqa: E402
import strife_review as SR  # noqa: E402

D = SR.D
BP = os.path.join(D, 'batch_settle.json')


def build():
    guide = SR.rd(os.path.join(D, '派活说明_定数.md'))
    fx = SR.rd(os.path.join(rb.ROOT, '纷争纪', '纷争纪_方向与写法_第二版.md'))
    cards = rb.section(fx, r'^## 六、逐张', r'^## 七、')
    cl = SR.rd(os.path.join(rb.ROOT, 'CLAUDE.md'))
    rules = '\n\n'.join(rb.section(cl, p, r'^### ') for p in [r'^### 玩家在场', r'^### 什么杀得死传奇', r'^### 怎么踏进传奇', r'^### 起名'])
    system = '你替一张日式西幻 JRPG 跑团卡《奥尔德兰的旅印》的主会话给纷争纪改稿定数，全程用中文。下面是这一回的派活说明，照它做。\n\n' + guide
    reqs = []
    for name, n, names in SR.JOBS:
        t = SR.page_text(n)
        page = '\n'.join(b for h, b in SR.blocks(t) if not h.startswith('## 这一代的命星'))
        outline = SR.rd(os.path.join(D, '大纲_%s.md' % name))
        user = '\n\n'.join([
            '# 你的活\n\n你这一份的份名是「%s」，纷争纪第%s页。' % (name, '一二三四五六七'[n - 1]),
            '# 写作口径几节\n\n' + rules,
            '# 方向稿第六节 逐张\n\n' + cards,
            '# 这一份的改稿大纲\n\n' + outline,
            '# 这一页原文（命星那一节以外）\n\n' + page,
        ])
        reqs.append({'custom_id': 'settle_%d' % len(reqs), 'params': {
            'model': rb.MODEL, 'max_tokens': 64000, 'thinking': {'type': 'adaptive'}, 'output_config': {'effort': 'high'},
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
                print('！没成', name, json.dumps(r['result'], ensure_ascii=False)[:300])
                continue
            msg = r['result']['message']
            tin += msg['usage']['input_tokens']
            tout += msg['usage']['output_tokens']
            text = ''.join(c.get('text', '') for c in msg['content'] if c.get('type') == 'text')
            open(os.path.join(D, '定数_%s.md' % name), 'w', encoding='utf-8', newline='\n').write(text.strip() + '\n')
            print('%s：%d 字，停在 %s' % (name, len(text), msg.get('stop_reason')))
        print('进 %d、出 %d token，约 $%.2f' % (tin, tout, (tin * rb.PRICE[0] + tout * rb.PRICE[1]) / 1e6 / 2))
