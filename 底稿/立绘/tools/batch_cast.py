#!/usr/bin/env python3
# 立绘铺开（11-20 夜）：缺立绘的人交 Opus 批处理起稿出图资料（cast JSON）。
#   python -I -X utf8 底稿/立绘/tools/batch_cast.py build|submit|wait
# 材料 底稿/立绘/铺开_11-20/材料/<页>.md（cast_material.py 出），交稿写 底稿/立绘/铺开_11-20/交稿/<份>.md，
# 收稿 take_cast.py 抠出 JSON 写进 底稿/状态栏/comfy/cast/山铜纪/<页>n.json。密钥照 claude_api 取，不打印。
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

W = os.path.join(ROOT, '底稿', '立绘', '铺开_11-20')
MODEL = 'claude-opus-5-5'
CHUNK = 12


def rd(p):
    return open(p, encoding='utf-8').read().replace('\r\n', '\n')


def section(t, a, b):
    i = re.search(a, t, re.M).start()
    m = re.search(b, t[i + 1:], re.M)
    return t[i:i + 1 + m.start()] if m else t[i:]


def system():
    spec = rd(os.path.join(ROOT, '底稿', '立绘', '写资料说明.md'))
    fashion = section(rd(os.path.join(ROOT, '底稿', '立绘', '各时代风尚_新三纪.md')), r'^## 三、山铜纪', r'^## 四、')
    claude = rd(os.path.join(ROOT, 'CLAUDE.md'))
    looks = section(claude, r'^### 容貌', r'^### 旅伴、相遇')
    sample = json.dumps(json.load(open(os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'cast', 'cast_E.json'), encoding='utf-8'))[:2], ensure_ascii=False, indent=1)
    art = rd(os.path.join(ROOT, '底稿', '立绘', '艺术照提示词_11-19.md'))
    return ('你给一张日式西幻 JRPG 跑团卡《奥尔德兰的旅印》写角色立绘的出图资料（交给出图脚本用的 JSON），全程照下面的说明。'
            '材料一页一份，每个【要画】一个人：先照说明判画不画（整群、神、魔物、只有名字没有长相的不画），画的照说明写一条。\n\n'
            '# 写资料说明\n\n' + spec + '\n\n# 这一纪的风尚\n\n' + fashion + '\n\n# 容貌口径（必须守）\n\n' + looks +
            '\n\n# 现成的样子（cast_E.json 头两条，照它的详略和写法）\n\n```json\n' + sample + '\n```\n\n'
            '# 门洞那一院（斐里安、伊诺克、内森、玛蓓、佩林、玛丽贝尔）\n\n'
            '这几位照原典的长相写（斐里安照雷内，伊诺克照雅各布，内森照阿兰，玛蓓照玛丽安，玛丽贝尔照桑多涅，佩林照卡特），出图时主会话会把原典的图当 identity 参考挂上去。'
            '下面是用户认过的艺术照提示词，长相、衣裳、配色照它；有原典的人，脸照原典的年纪和五官写，别写岁数和“不屑”这类神情，写跟参考图一样年轻。\n\n' + art +
            '\n\n# 交什么\n\n先交一个 ```json 代码块，里面是一个 JSON 数组，一个人一条（en 用这一页的前缀，比如 p3 那一页写 s3n_ 开头，加一个短的罗马字，整一纪不许重）。'
            '再交一个 ```md 代码块，是备注：画了谁、没画谁和缘故、哪几条是自己起的（★）。前后不加别的话。')


def jobs():
    out = []
    for f in sorted(glob.glob(os.path.join(W, '材料', '*.md'))):
        pg = os.path.basename(f)[:-3]
        t = rd(f)
        head, *items = t.split('=' * 20 + '\n')
        for i in range(0, len(items), CHUNK):
            part = items[i:i + CHUNK]
            out.append(('%s_%d' % (pg, i // CHUNK + 1), head.replace('：', '（这一份 %d 人）：' % len(part), 1) + '\n'.join('=' * 20 + '\n' + x for x in part)))
    return out


def build():
    s = system()
    reqs, names = [], []
    for name, body in jobs():
        reqs.append({'custom_id': 'cast_%d' % len(reqs), 'params': {
            'model': MODEL, 'max_tokens': 64000, 'output_config': {'effort': 'medium'}, 'thinking': {'type': 'adaptive'},
            'system': s, 'messages': [{'role': 'user', 'content': body}]}})
        names.append(name)
    return reqs, names


BP = os.path.join(W, 'batch.json')

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    cmd = sys.argv[1]
    if cmd == 'build':
        reqs, names = build()
        for r, n in zip(reqs, names):
            print(n, len(r['params']['messages'][0]['content']))
        print('份数', len(reqs), '系统提示', len(reqs[0]['params']['system']), '字')
    elif cmd == 'submit':
        reqs, names = build()
        d = json.loads(rb.call(rb.API, {'requests': reqs}))
        json.dump({'id': d['id'], 'jobs': names}, open(BP, 'w', encoding='utf-8'), ensure_ascii=False)
        print('交上去了：', d['id'], len(reqs), '份')
    elif cmd == 'wait':
        b = json.load(open(BP, encoding='utf-8'))
        while True:
            d = json.loads(rb.call(rb.API + '/' + b['id']))
            print(d.get('processing_status'), d.get('request_counts'))
            if d.get('processing_status') == 'ended':
                break
            time.sleep(60)
        os.makedirs(os.path.join(W, '交稿'), exist_ok=True)
        tin = tout = 0
        for line in rb.call(d['results_url']).splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            name = b['jobs'][int(r['custom_id'].rsplit('_', 1)[1])]
            res = r['result']
            if res['type'] != 'succeeded':
                print('！没成', name, json.dumps(res, ensure_ascii=False)[:300])
                continue
            msg = res['message']
            u = msg.get('usage', {})
            tin += u.get('input_tokens', 0)
            tout += u.get('output_tokens', 0)
            open(os.path.join(W, '交稿', name + '.md'), 'w', encoding='utf-8', newline='\n').write(''.join(c.get('text', '') for c in msg['content'] if c.get('type') == 'text'))
            if msg.get('stop_reason') != 'end_turn':
                print('！停在', msg.get('stop_reason'), name)
        print('进 %d、出 %d token，约 $%.2f' % (tin, tout, (tin * 4 + tout * 20) / 1e6 / 2))
