#!/usr/bin/env python3
# 命星重审第二轮（11-19 夜）走 API 批处理（照 tools/api/pukai_batch.py 那一套，五折、异步）。
#   python -I -X utf8 底稿/命星重审第二轮/tools/batch.py build screen|rare     看各份多大
#   python -I -X utf8 底稿/命星重审第二轮/tools/batch.py submit screen|rare    交，批号记在 材料/batch_<名>.json
#   python -I -X utf8 底稿/命星重审第二轮/tools/batch.py wait screen|rare      等完了取结果，写 交稿/<名>_<份>.md
# 筛表交 Opus 5.5（判断），Rare 加魔法交 Fable 5.2（写）。材料先跑 tools/extract.py。密钥照 claude_api.key() 取，不打印。
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'api'))
import review_batch as rb  # noqa: E402

W = os.path.join(ROOT, '底稿', '命星重审第二轮')
MAT = os.path.join(W, '材料')
OUT = os.path.join(W, '交稿')
MODEL = {'screen': 'claude-opus-5-5', 'rare': 'claude-fable-5-2', 'pu': 'claude-opus-5-5'}
EFFORT = {'screen': 'medium', 'rare': 'medium', 'pu': 'medium'}
CHUNK = {'screen': 12, 'rare': 10, 'pu': 6}
PRE = {'screen': '筛_', 'rare': 'rare_', 'pu': '铺_'}
PRICE = {'claude-fable-5-2': (8.0, 40.0), 'claude-opus-5-5': (4.0, 20.0)}


def rd(p):
    return open(p, encoding='utf-8').read().replace('\r\n', '\n')


def section(t, a, b):
    i = re.search(a, t, re.M).start()
    m = re.search(b, t[i + 1:], re.M)
    return t[i:i + 1 + m.start()] if m else t[i:]


def system(kind):
    s2 = rd(os.path.join(W, '样稿_第二版.md'))
    if kind == 'pu':
        g = rd(os.path.join(W, '派活说明_铺开.md'))
        sh = rd(os.path.join(W, '筛表_第一版.md'))
        zs = rd(os.path.join(W, '技艺走势_口径.md'))
        return (g.replace('{口径}', section(s2, r'^## 二、口径草案', r'^## 三、'))
                 .replace('{决定}', section(sh, r'^## 〇之一', r'^## 〇、'))
                 .replace('{走势}', section(zs, r'^## 二、口径', r'\Z'))
                 .replace('{样稿}', section(s2, r'^## 三、样稿', r'^## 四、')))
    if kind == 'screen':
        g = rd(os.path.join(W, '派活说明_筛表.md'))
        return g.replace('{口径}', section(s2, r'^## 二、口径草案', r'^## 三、')).replace('{样稿}', section(s2, r'^## 三、样稿', r'^## 四、'))
    g = rd(os.path.join(W, '派活说明_Rare.md'))
    return g.replace('{样稿}', section(s2, r'^## 四、Rare', r'^## 五、'))


def jobs(kind):
    idx = json.load(open(os.path.join(MAT, '索引.json'), encoding='utf-8'))
    pre = PRE[kind]
    out = []
    for key in idx:
        f = os.path.join(MAT, pre + key + '.md')
        if not os.path.exists(f):
            continue
        t = rd(f)
        head, *items = t.split('=' * 20 + '\n')
        if kind == 'rare':
            items = ['=' * 20 + '\n' + x for x in items]
        else:
            items = ['=' * 20 + '\n' + x for x in items]
        n = CHUNK[kind]
        for i in range(0, len(items), n):
            part = items[i:i + n]
            name = '%s_%s_%d' % (kind, key, i // n + 1)
            only = [x for x in os.environ.get('ONLY', '').split(',') if x]
            if only:                      # 重跑撞了输出上限的那几份：切成三位一份，名字后头加 a、b
                if name in only:
                    for j in range(0, len(part), 3):
                        out.append((name + 'abcdef'[j // 3], head + '\n'.join(part[j:j + 3])))
                continue
            out.append((name, head + '\n'.join(part)))
    return out


def build(kind):
    sysm = system(kind)
    reqs, names = [], []
    for name, body in jobs(kind):
        model = MODEL[kind]
        params = {'model': model, 'max_tokens': 32000, 'output_config': {'effort': EFFORT[kind]},
                  'system': sysm, 'messages': [{'role': 'user', 'content': body}]}
        if not model.startswith('claude-fable'):
            params['thinking'] = {'type': 'adaptive'}
        reqs.append({'custom_id': '%s_%d' % (kind, len(reqs)), 'params': params})
        names.append(name)
    return reqs, names


def bpath(kind):
    return os.path.join(MAT, 'batch_%s.json' % kind)


def submit(kind):
    reqs, names = build(kind)
    d = json.loads(rb.call(rb.API, {'requests': reqs}))
    json.dump({'id': d['id'], 'jobs': names, 'model': MODEL[kind]}, open(bpath(kind), 'w', encoding='utf-8'), ensure_ascii=False)
    print('交上去了：', d['id'], d.get('processing_status'), len(reqs), '份')


def status(kind):
    b = json.load(open(bpath(kind), encoding='utf-8'))
    d = json.loads(rb.call(rb.API + '/' + b['id']))
    print(d.get('processing_status'), d.get('request_counts'))
    return b, d


def fetch(b, d):
    os.makedirs(OUT, exist_ok=True)
    out = rb.call(d['results_url'])
    tin = tout = 0
    bad = []
    for line in out.splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        name = b['jobs'][int(r['custom_id'].rsplit('_', 1)[1])]
        res = r['result']
        if res['type'] != 'succeeded':
            print('！%s 没成：%s' % (name, json.dumps(res, ensure_ascii=False)[:300]))
            bad.append(name)
            continue
        msg = res['message']
        text = ''.join(c.get('text', '') for c in msg['content'] if c.get('type') == 'text')
        u = msg.get('usage', {})
        tin += u.get('input_tokens', 0)
        tout += u.get('output_tokens', 0)
        open(os.path.join(OUT, '%s.md' % name), 'w', encoding='utf-8', newline='\n').write(text.strip() + '\n')
        if msg.get('stop_reason') != 'end_turn':
            print('！%s 停在 %s' % (name, msg.get('stop_reason')))
            bad.append(name)
    pr = PRICE[b['model']]
    print('收了 %d 份，进 %d、出 %d token，批处理五折约 $%.2f' % (len(b['jobs']) - len(bad), tin, tout, (tin * pr[0] + tout * pr[1]) / 1e6 / 2))
    if bad:
        print('要重跑的：', bad)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    cmd, kind = sys.argv[1], sys.argv[2]
    if cmd == 'build':
        reqs, names = build(kind)
        tot = 0
        for r, n in zip(reqs, names):
            c = len(r['params']['messages'][0]['content'])
            tot += c + len(r['params']['system'])
            print(n, c)
        print('份数', len(reqs), '系统提示', len(reqs[0]['params']['system']), '字，合计约', tot, '字')
    elif cmd == 'submit':
        submit(kind)
    elif cmd == 'status':
        status(kind)
    elif cmd == 'wait':
        for _ in range(600):
            b, d = status(kind)
            if d.get('processing_status') == 'ended':
                fetch(b, d)
                break
            time.sleep(60)
