#!/usr/bin/env python3
# 11-20 夜：山铜纪这一轮八条新主线的节点原画场面，一条主线一份交 Opus 批处理起稿（派活说明.md 那一套）。
#   python -I -X utf8 batch_scenes.py build|submit|wait|take [--apply]
# 交稿写 scenes/交稿_1120/<页>_<主线>.md；take 抠出 JSON 并进 scenes/pN.json（nodes、deaths 追加，fates 合并，notes 追加），
# 并完跑 merge_scenes.py，再 build_data.py；图照旧 comfy/gpt_cg3.py scenes 出（要等新人的立绘出了）。
import glob
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'api'))
import review_batch as rb  # noqa: E402

OUT = os.path.join(HERE, '交稿_1120')
BP = os.path.join(OUT, 'batch.json')
NEW = ['犁的年月·擎天之心', '犁的年月·河心三日', '长夜的年月·侠影', '长夜的年月·蛾名', '白鸦的年月·白石之夜', '白鸦的年月·旱年', '白鸦的年月·宴火', '麦的年月·归火']
PAGE = {'犁的年月': ('p1', '山铜纪时段_一_犁的年月'), '长夜的年月': ('p2', '山铜纪时段_二_长夜的年月'), '白鸦的年月': ('p3', '山铜纪时段_三_白鸦的年月'), '麦的年月': ('p6', '山铜纪时段_六_麦的年月')}


def rd(p):
    return open(p, encoding='utf-8').read().replace('\r\n', '\n')


def sec(t, a, b):
    m = re.search(a, t, re.M)
    if not m:
        return ''
    n = re.search(b, t[m.end():], re.M)
    return t[m.start():m.end() + (n.start() if n else len(t))]


def jobs():
    out = []
    for name in NEW:
        pn, fn = PAGE[name.split('·')[0]]
        task = rd(os.path.join(HERE, '任务单', pn + '.md'))
        page = rd(os.path.join(ROOT, '山铜纪', fn + '.md'))
        line = sec(task, r'^### ' + re.escape(name) + r'（', r'^### |^## ')
        people = sec(task, r'^## 这一段的人', r'^## 魔神')
        gods = sec(task, r'^## 魔神', r'^## 源稿')
        main = sec(page, r'^## 山铜纪·主线｜' + re.escape(name) + r'$', r'^## (?!裁定锁)')
        body = ('# 你这一份：%s（%s）\n\n只写这一条主线：nodes 一幕一幅（键照下面任务单给的），这一条里死的旅伴写 fates 和 deaths，notes 写拿不准的。'
                '交一个 ```json 代码块，样子照派活说明第三节（era 写 %s），前后不加别的话。\n\n## 任务单里这一条\n\n%s\n\n%s\n\n%s\n\n## 主线原文\n\n%s'
                % (name, pn, pn, line, people, gods, main))
        out.append((pn + '_' + name.split('·')[1], body))
    return out


def system():
    return ('你给一张日式西幻 JRPG 跑团卡《奥尔德兰的旅印》的门面写节点原画的场面（JSON），照下面的派活说明和示例。\n\n# 派活说明\n\n' + rd(os.path.join(HERE, '派活说明.md')) +
            '\n\n# 示例（纷争纪那一本 m07）\n\n```json\n' + rd(os.path.join(ROOT, '底稿', '门面', '小样_纷争纪书', 'scenes', '示例_m07.json')) + '\n```')


def build():
    s = system()
    reqs, names = [], []
    for n, body in jobs():
        reqs.append({'custom_id': 'sc_%d' % len(reqs), 'params': {'model': 'claude-opus-5-5', 'max_tokens': 48000, 'output_config': {'effort': 'medium'},
                     'thinking': {'type': 'adaptive'}, 'system': s, 'messages': [{'role': 'user', 'content': body}]}})
        names.append(n)
    return reqs, names


def take(apply):
    add = {}
    for f in sorted(glob.glob(os.path.join(OUT, '*.md'))):
        pn = os.path.basename(f).split('_')[0]
        m = re.search(r'```json\s*\n(.*?)\n```', rd(f), re.S)
        d = json.loads(m.group(1))
        a = add.setdefault(pn, {'nodes': [], 'deaths': [], 'fates': {}, 'notes': []})
        a['nodes'] += d.get('nodes', [])
        a['deaths'] += d.get('deaths', [])
        a['fates'].update(d.get('fates', {}))
        a['notes'] += d.get('notes', [])
        print(os.path.basename(f), '节点', len(d.get('nodes', [])), '死的那一刻', len(d.get('deaths', [])), '死期', len(d.get('fates', {})))
    for pn, a in add.items():
        p = os.path.join(HERE, pn + '.json')
        d = json.load(open(p, encoding='utf-8'))
        have = {x['key'] for x in d['nodes'] + d.get('deaths', [])}
        for x in a['nodes']:            # 任务单的字母插了新主线以后顺移了，老键底下的图已经画好，新主线的键前头加 n（p1_d1 → p1_nd1）
            if x['key'] in have:
                x['key'] = x['key'].replace(pn + '_', pn + '_n', 1)
        dup = [x['key'] for x in a['nodes'] + a['deaths'] if x['key'] in have]
        if dup:
            print('！', pn, '键已经有了：', dup)
            continue
        d['nodes'] += a['nodes']
        d.setdefault('deaths', []).extend(a['deaths'])
        d.setdefault('fates', {}).update(a['fates'])
        d.setdefault('notes', []).extend('11-20 新主线：' + x for x in a['notes'])
        if apply:
            json.dump(d, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('写了' if apply else '没写（加 --apply）')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    cmd = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    if cmd == 'build':
        reqs, names = build()
        for r, n in zip(reqs, names):
            print(n, len(r['params']['messages'][0]['content']))
        print('系统提示', len(reqs[0]['params']['system']))
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
            open(os.path.join(OUT, n + '.md'), 'w', encoding='utf-8', newline='\n').write(''.join(c.get('text', '') for c in msg['content'] if c.get('type') == 'text'))
        print('进 %d、出 %d token，约 $%.2f' % (tin, tout, (tin * 4 + tout * 20) / 1e6 / 2))
    elif cmd == 'take':
        take('--apply' in sys.argv)
