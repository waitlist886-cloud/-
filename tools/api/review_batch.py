#!/usr/bin/env python3
# 迷宫纪前传剧情审稿走 API 额度的批处理（11-19）。八份审稿打成一个 Message Batch（五折、异步，不怕长请求超时）。
# 材料直接喂进请求里（审稿人看不到仓库）：派活说明当 system，方向稿那几节、写作口径里“玩家在场”那一节、那一页的页头总纲和要审的主线当 user。
#   python -I -X utf8 tools/api/review_batch.py submit     交批处理，批号记在 底稿/审稿/迷宫纪前传/材料/batch.json
#   python -I -X utf8 tools/api/review_batch.py wait       每分钟问一次，结束就取结果写 审_<份名>.md，印用量和花费
#   python -I -X utf8 tools/api/review_batch.py status     只问一次
# 只用标准库；密钥照 claude_api.key() 取，不打印。
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from claude_api import key  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
D = os.path.join(ROOT, '底稿', '审稿', '迷宫纪前传')
M = os.path.join(D, '材料')
API = 'https://api.anthropic.com/v1/messages/batches'
MODEL = 'claude-opus-5-5'
PRICE = (4.0, 20.0)   # Opus 5.5 每百万 token 进／出，批处理再打五折

JOBS = [
    ('探井', 1, None),
    ('共约', 2, None),
    ('繁荣', 3, None),
    ('深井上', 4, ['七重龙门', '第五十一层', '一段残响', '第五十六层的路标', '断崖', '七百个梦', '曜石审判']),
    ('深井下', 4, ['两边的名单', '七日的锅', '没有门框的门', '第七次楼层主讨伐', '海墙', '一枚金币']),
    ('黑潮上', 5, ['头一张撤离单', '头一回斩首', '白碑东门', '白碑第七夜', '背靠背']),
    ('黑潮下', 5, ['花雨', '九十九条', '坠龙航线', '光复']),
    ('垂暮', 6, None),
]
NOTE = {
    '黑潮上': '这一页是用户说的“黑潮战争的悲壮与宏大”，规模、牺牲、齐心、赢下来的光要特别看。',
    '黑潮下': '这一页是用户说的“黑潮战争的悲壮与宏大”，规模、牺牲、齐心、赢下来的光要特别看；光复是黑潮的收尾，看它收不收得住整场战争。',
    '垂暮': '第六页是前传的收尾，看它把一千年收到 1001 年的开局收住没有。另附 1001 年那一头的一条支线「兆八·归火开炉」，它是支线不是主线，照同一把尺子审，看它跟前传接不接得上，单独写一节。',
}


def rd(*p):
    return open(os.path.join(ROOT, *p), encoding='utf-8').read().replace('\r\n', '\n')


def lines(text, a, b):
    return '\n'.join(text.split('\n')[a - 1:b])


def section(text, start_pat, stop_pat):
    i = re.search(start_pat, text, re.M).start()
    m = re.search(stop_pat, text[i + 1:], re.M)
    return text[i:i + 1 + m.start()] if m else text[i:]


def mains_of(page, names):
    t = open(os.path.join(M, 'p%d_主线.md' % page), encoding='utf-8').read()
    secs = re.split(r'(?=^## 迷宫纪·主线｜)', t, flags=re.M)
    secs = [s for s in secs if s.startswith('## 迷宫纪·主线｜')]
    if names:
        secs = [s for s in secs if s.split('\n', 1)[0].split('·', 2)[-1].strip() in names]
        assert len(secs) == len(names), (page, names, len(secs))
    return ''.join(secs), len(secs)


def build():
    guide = open(os.path.join(D, '派活说明.md'), encoding='utf-8').read()
    fx = rd('迷宫纪前传_方向稿_第四版.md')
    direction = '\n\n'.join([lines(fx, 7, 14), lines(fx, 223, 309), lines(fx, 364, 403), lines(fx, 446, 459)])
    team = section(rd('迷宫纪整理与前传补完_方向稿.md'), r'^## 五、冒险团', r'^## 六')
    cl = rd('CLAUDE.md')
    present = section(cl, r'^### 玩家在场', r'^### ')
    rival = ('主线要有上台下棋的对手（用户 11-18 定的）：每条一个有名有脸、出三回手的对手，一回比一回狠，高潮是做出来的事；'
             '名字、碑、账、一碗汤不当高潮；锁别把这一纪的对手锁出棋盘；英雄的本事别写成取消冲突的开关。')
    system = ('你是审稿人，全程用中文。下面是这一回的派活说明，照它做。\n\n这一回有一处跟派活说明不一样：你看不到仓库，'
              '派活说明第三节要你读的东西都已经附在用户消息里了（方向稿那几节、写作口径里玩家在场那一节、页头和时段总纲、你要审的主线）；'
              '第三节第 5 条说的去页面文件查旅伴和人物这一步做不了，只凭主线和总纲判断，拿不准就写拿不准。'
              '第五节说的“写一个文件”，就是把那份审稿文件的全文直接输出成 Markdown，从一级标题写起，前后不加别的话；'
              '第六节最后那段三百字的回话不用写。\n\n' + guide)
    reqs = []
    for name, page, names in JOBS:
        mains, n = mains_of(page, names)
        head = open(os.path.join(M, 'p%d_页头与总纲.md' % page), encoding='utf-8').read()
        extra = ''
        if name == '垂暮':
            extra = '\n\n# 附：1001 年那一头的支线「兆八·归火开炉」\n\n' + open(os.path.join(M, '1001_兆八归火开炉.md'), encoding='utf-8').read()
        task = ('你这一份的份名是「%s」，审迷宫纪前传第%s页的 %d 条主线（%s）。%s末尾「这一份共有的」只就你这几条说。'
                % (name, '一二三四五六'[page - 1], n, '全部' if not names else '、'.join(names), NOTE.get(name, '')))
        user = '\n\n'.join([
            '# 你的活\n\n' + task,
            '# 方向稿第四版（迷宫纪前传_方向稿_第四版.md）里要读的几节\n\n' + direction,
            '# 迷宫纪整理与前传补完_方向稿.md 第五节\n\n' + team,
            '# 写作口径里的两条\n\n' + present + '\n\n' + rival,
            '# 这一页的页头和时段总纲\n\n' + head,
            '# 你要审的主线（一条一个「## 迷宫纪·主线｜」，后头跟着它的裁定锁）\n\n' + mains + extra,
        ])
        reqs.append({'custom_id': 'review_%d' % len(reqs), 'params': {
            'model': MODEL, 'max_tokens': 96000,
            'thinking': {'type': 'adaptive'}, 'output_config': {'effort': 'high'},
            'system': system, 'messages': [{'role': 'user', 'content': user}]}})
    return reqs


def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8') if body is not None else None,
                                 method='POST' if body is not None else 'GET',
                                 headers={'x-api-key': key(), 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        raise SystemExit('API 回错 %s：%s' % (e.code, e.read().decode('utf-8', 'replace')[:800]))


def submit():
    reqs = build()
    for r, (name, _, _) in zip(reqs, JOBS):
        n = len(r['params']['system']) + len(r['params']['messages'][0]['content'])
        print('%s：请求约 %d 字' % (name, n))
    d = json.loads(call(API, {'requests': reqs}))
    json.dump({'id': d['id'], 'jobs': [j[0] for j in JOBS]}, open(os.path.join(M, 'batch.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('交上去了：', d['id'], d.get('processing_status'))


def status():
    b = json.load(open(os.path.join(M, 'batch.json'), encoding='utf-8'))
    d = json.loads(call(API + '/' + b['id']))
    print(d.get('processing_status'), d.get('request_counts'))
    return b, d


def fetch(b, d):
    out = call(d['results_url'])
    tin = tout = 0
    for line in out.splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        i = int(r['custom_id'].split('_')[1])
        name = b['jobs'][i]
        res = r['result']
        if res['type'] != 'succeeded':
            print('！%s 没成：%s' % (name, json.dumps(res, ensure_ascii=False)[:300]))
            continue
        msg = res['message']
        text = ''.join(c.get('text', '') for c in msg['content'] if c.get('type') == 'text')
        u = msg.get('usage', {})
        tin += u.get('input_tokens', 0)
        tout += u.get('output_tokens', 0)
        p = os.path.join(D, '审_%s.md' % name)
        open(p, 'w', encoding='utf-8').write(text.strip() + '\n')
        print('%s：%d 字，停在 %s，进 %d 出 %d' % (name, len(text), msg.get('stop_reason'), u.get('input_tokens', 0), u.get('output_tokens', 0)))
    cost = (tin * PRICE[0] + tout * PRICE[1]) / 1e6 / 2
    print('合计进 %d、出 %d token，批处理五折约 $%.2f' % (tin, tout, cost))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'submit':
        submit()
    elif cmd == 'status':
        status()
    elif cmd == 'wait':
        for _ in range(240):
            b, d = status()
            if d.get('processing_status') == 'ended':
                fetch(b, d)
                break
            time.sleep(60)
    elif cmd == 'build':
        for r in build():
            print(r['custom_id'], len(r['params']['messages'][0]['content']))
