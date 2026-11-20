#!/usr/bin/env python3
# 迷宫纪前传剧情大纲第一版的两条样稿走 API 额度（11-19）：断门长桌重写、光复加力。打成一个 Message Batch。
# 材料直接喂进请求（写手看不到仓库）：写作口径整节、四份写作 skill、大纲、那一条的审稿、页头总纲、原稿、几条人物。
#   python -I -X utf8 tools/api/sample_batch.py submit | wait | status | build
# 结果写 底稿/迷宫纪前传/剧情大纲/样稿_<名>.md，批号记在同目录 batch.json。密钥照 claude_api.key() 取，不打印。
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from claude_api import key  # noqa: E402,F401
import review_batch as rb  # noqa: E402

ROOT = rb.ROOT
OUT = os.path.join(ROOT, '底稿', '迷宫纪前传', '剧情大纲')
MAT = os.path.join(ROOT, '底稿', '审稿', '迷宫纪前传', '材料')
R = 2 if '--r2' in sys.argv else 1
ROUND2 = '''# 这一回是第二稿

用户看了你上一稿，原话：

> 我觉得方向ok，但是有几点需要注意一下：照着这个写进卡里会不会有点太详细了，作为给airp主持的ai看的剧情大纲而言。以及在如此详细地描写下，高阶超凡者的表现力没能写出来，无论是正反方，感觉写出来与中世纪凡人决斗一样。传奇能做到什么程度的表现力：如索恩薇娅斩冠的那一夜，一剑下去整个天穹如同被劈开成两半，一半被剑光映照得如同白昼，仿佛晨昏都被分割，世界被斩开。英雄已经是一个国家的顶梁柱，传奇在底卡的裁定更是以世界为基准。撼世 - 足以覆灭国家，撼动世界；天灾 - 如同行走的天灾，倾覆大陆

照大纲第五节末尾「用户 11-19 看了两条样稿以后补的两条」改「%s」这一条：
1. 收成给主持看的骨架。每幕五到八拍，一拍一两句，写这一幕要做成什么、对头这一回出哪一手、高潮的样子和靠什么赢；对白只留一幕一两句要紧的，斗嘴、吃饭、细小的动作点一句交给主持。开局到收束的正文控制在大纲给的字数上下。默认收束一段话说完，别复述三幕。玩家能改一条一两句。
2. 高阶的仗照那张位阶的表写：先写天地和远处的人看见什么，再写招。正反两方一样。凡人、低阶伙伴做的是撑住、拽人、报方位、修东西，不拿他们的打法当高阶的打法。每个出手的人照他在页头、人物条里的位阶写，拿不准的在设计备注里写明你按哪一档写的。
3. 上一稿里立住的东西（对头三回出手、伙伴戏的种子、旅伴、该留的原稿几拍、主会话收稿时改的）留着，只是收短、放大。
4. 设计备注照旧，头一节写这一稿比上一稿砍了什么、放大了什么。
'''
SK = os.environ.get('SKX') or os.path.join(os.environ.get('TEMP', ''), 'skx')


def rd(*p):
    return rb.rd(*p)


def sec(text, start, stop):
    return rb.section(text, start, stop)


def main_of(page, name):
    t = open(os.path.join(MAT, 'p%d_主线.md' % page), encoding='utf-8').read()
    s, n = rb.mains_of(page, [name])
    return s


def page_entry(fname, title_pat):
    t = rd('迷宫纪前传', fname)
    return sec(t, title_pat, r'^## (?!裁定锁)')


JOBS = [
    {'name': '断门长桌', 'page': 1, 'review': ('审_探井.md', r'^## 三、断门长桌', r'^## 四'), 'outline': ['## 八、样稿一'],
     'extra': [('迷宫纪前传/补卷/补卷_77_冒险团_探井与共约.md', r'^## 迷宫纪·冒险团｜雾海之王', r'^## 迷宫纪·冒险团｜山铜之冠')],
     'note': '这一条要重写骨架，照大纲第八节。签约是背景，戏在桌子底下的旧地道里。对头（那个炎角老将，或者照第十节第 3 件的另两条路里你觉得最好的一条）你起名，名字标★写进设计备注。'},
    {'name': '光复', 'page': 5, 'review': ('审_黑潮下.md', r'^## 四、光复', r'^## 这一份共有的'), 'outline': ['## 七、黑潮的决战'],
     'extra': [('迷宫纪前传/迷宫纪前传时段_五_黑潮的年月.md', r'^## 七魔神将，黑潮的年月里的七个人', r'^## 魔王，黑潮的年月里的巴尔缇娜'),
               ('迷宫纪前传/迷宫纪前传时段_五_黑潮的年月.md', r'^## 魔王，黑潮的年月里的巴尔缇娜', r'^## (?!裁定锁|#)')],
     'note': '这一条是加力，骨架不动，照大纲第七节。这是整场黑潮和整个前传的高潮，要写出悲壮和宏大，赢下来的光要亮。现有的好拍子（法丽达打桩、芒戈的脸、刻期家的老人、塔隆守门、蕾雅撕门）留着；报名桌、结算、读名、钱压成两三拍。'},
]


SYSTEM_HEAD = '''你是这张卡的写手，全程用中文。这一回写一条主线的样稿，给用户看口气，用户看了才定全铺不铺。你看不到仓库，要读的东西都附在用户消息里了。

要守的，按要紧的次序：
1. 用户这一回要的（大纲第一节、审稿报告里用户的原话）：迷宫纪是亮的、往前走的王道 JRPG，有上台下棋的对头，高潮是做出来的事，伙伴有日常和斗嘴，赢下来。黑潮要悲壮和宏大。
2. 大纲里这一条的那一节，和这一条的审稿意见（改法方向、该留的几拍、毛病）。
3. 写作口径整节（附在下面），卡面的标点、禁词、月相字、东方语感的字、玩家在场、什么杀得死传奇、台词、容貌、起名，一条一条照守。
4. 四份写作 skill（附在下面），写之前读完，写完照它们自查一遍。

格式：
- 输出两块，前后不加别的话。头一块是这一条主线的全文，从「## 迷宫纪·主线｜」那一行写到「> 条目设置：」那一行为止，照原稿的栏目和次序：【调用】、题、章、引语、开局、世道、一幕二幕三幕（每幕「一幕｜标题。月份，时长。」下面一拍一条，末一条「- 幕终：……」）、收束、默认收束、玩家能改、碰得上的人、「## 裁定锁」、条目设置。
- 「## 迷宫纪·主线｜」标题、「题：」「章：」两行、「## 裁定锁」标题、条目设置那一行，一个字不动，照原稿抄。
- 第二块从「## 设计备注」起，不进卡，写：改了什么（对着审稿逐条）、新起的设定和名字（标★，借了什么写明）、对头的三回出手各在哪一拍、留下了原稿哪几拍、要用户定的。
- 新起的设定在卡面句末标（★），跟原稿一样。
- 标点：不用——、—、；、…、！、...，冒号只在标签行。对白用“”。
- 那一位恶神不点名，卡面和备注都不点，只写那一位。表层不说井在吃什么。
- 原稿里写“（#46）”这类底卡出处的括号照留原样。
- 长短：跟原稿差不多或者短一些，别注水。一拍写一件事，写结果和动作，不写说辞。

'''


def build():
    cl = rd('CLAUDE.md')
    rules = sec(cl, r'^## 写作口径', r'^## 换账号接手')
    skills = []
    for n in ['western-fantasy-prose', 'chinese-prose-register', 'jrpg-lore-writing', 'genshin-dialogue-voice']:
        p = os.path.join(SK, n, 'SKILL.md')
        skills.append('# skill：%s\n\n%s' % (n, open(p, encoding='utf-8').read()))
    system = SYSTEM_HEAD + '# 写作口径（CLAUDE.md 整节）\n\n' + rules + '\n\n' + '\n\n'.join(skills)
    outline = rd('迷宫纪前传剧情大纲_第一版.md')
    report = rd('迷宫纪前传剧情审稿_11-19.md')
    reqs = []
    for j in JOBS:
        rv = sec(open(os.path.join(ROOT, '底稿', '审稿', '迷宫纪前传', j['review'][0]), encoding='utf-8').read(), j['review'][1], j['review'][2])
        head = open(os.path.join(MAT, 'p%d_页头与总纲.md' % j['page']), encoding='utf-8').read()
        orig = main_of(j['page'], j['name'])
        extras = []
        for f, a, b in j['extra']:
            extras.append(sec(rd(*f.split('/')), a, b))
        user = '\n\n'.join([
            '# 你的活\n\n写迷宫纪前传第%s页「%s」这一条主线的样稿。%s' % ('一二三四五六'[j['page'] - 1], j['name'], j['note']),
            '# 剧情大纲第一版（整份，这一条看第六节表里那一行和%s那一节）\n\n' % '、'.join(j['outline']) + outline,
            '# 审稿报告（整份，用户原话在第一节）\n\n' + report,
            '# 这一条的分审意见\n\n' + rv,
            '# 这一页的页头和时段总纲\n\n' + head,
            '# 用得上的几条人物、冒险团（照这几条的长相、年份、下场写，别改）\n\n' + '\n\n'.join(extras),
            '# 原稿\n\n' + orig,
        ] + ([ROUND2 % j['name'], '# 你上一稿（主会话收稿时改过几处，末尾有记录）\n\n'
              + open(os.path.join(OUT, '样稿_%s.md' % j['name']), encoding='utf-8').read()] if R == 2 else []))
        reqs.append({'custom_id': 'sample_%d' % len(reqs), 'params': {
            'model': rb.MODEL, 'max_tokens': 100000,
            'thinking': {'type': 'adaptive'}, 'output_config': {'effort': 'high'},
            'system': system, 'messages': [{'role': 'user', 'content': user}]}})
    return reqs


def submit():
    os.makedirs(OUT, exist_ok=True)
    reqs = build()
    for r, j in zip(reqs, JOBS):
        print('%s：请求约 %d 字' % (j['name'], len(r['params']['system']) + len(r['params']['messages'][0]['content'])))
    d = json.loads(rb.call(rb.API, {'requests': reqs}))
    json.dump({'id': d['id'], 'jobs': [j['name'] for j in JOBS]}, open(os.path.join(OUT, 'batch%s.json' % ('2' if R == 2 else '')), 'w', encoding='utf-8'), ensure_ascii=False)
    print('交上去了：', d['id'], d.get('processing_status'))


def status():
    b = json.load(open(os.path.join(OUT, 'batch%s.json' % ('2' if R == 2 else '')), encoding='utf-8'))
    d = json.loads(rb.call(rb.API + '/' + b['id']))
    print(d.get('processing_status'), d.get('request_counts'))
    return b, d


def fetch(b, d):
    out = rb.call(d['results_url'])
    tin = tout = 0
    for line in out.splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        name = b['jobs'][int(r['custom_id'].split('_')[1])]
        res = r['result']
        if res['type'] != 'succeeded':
            print('！%s 没成：%s' % (name, json.dumps(res, ensure_ascii=False)[:300]))
            continue
        msg = res['message']
        text = ''.join(c.get('text', '') for c in msg['content'] if c.get('type') == 'text')
        u = msg.get('usage', {})
        tin += u.get('input_tokens', 0)
        tout += u.get('output_tokens', 0)
        open(os.path.join(OUT, '样稿_%s%s.md' % (name, '_第二稿' if R == 2 else '')), 'w', encoding='utf-8').write(text.strip() + '\n')
        print('%s：%d 字，停在 %s，进 %d 出 %d' % (name, len(text), msg.get('stop_reason'), u.get('input_tokens', 0), u.get('output_tokens', 0)))
    print('合计进 %d、出 %d token，批处理五折约 $%.2f' % (tin, tout, (tin * rb.PRICE[0] + tout * rb.PRICE[1]) / 1e6 / 2))


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
        for r, j in zip(build(), JOBS):
            print(j['name'], len(r['params']['system']), len(r['params']['messages'][0]['content']))
