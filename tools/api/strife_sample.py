#!/usr/bin/env python3
# 纷争纪改稿样稿（11-21）：照 纷争纪剧情大纲_第一版 合并稿写两条卡面稿给用户看口气和分量，Fable 写。
#   python -I -X utf8 tools/api/strife_sample.py build|submit|wait
# 交稿写 底稿/审稿/纷争纪/样稿_<主线>.md。写手看不到仓库，材料直接喂进请求；写作技能读 %TEMP%/skx（pukai_batch 那一套）。
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import review_batch as rb  # noqa: E402
import strife_review as SR  # noqa: E402
import pukai_batch as PB  # noqa: E402

D = SR.D
BP = os.path.join(D, 'batch_sample.json')
MODEL = 'claude-fable-5-2'
JOBS = [('雨城的星', 7, '号角'), ('无名之柱', 6, '铁狼')]

HEAD = '''你是这张卡的写手，全程用中文。这一回是纷争纪主线改稿的样稿，一条主线一份，写成卡面稿，给用户看口气和分量。你看不到仓库，要读的东西都附在用户消息里了。

要守的，按要紧的次序：
1. 改稿大纲合并稿里你这一条（附在后面）：新骨架、对手和他的三手、三幕、收束、传奇和凝名、玩家能干的、照留的原拍。大纲里〔待用户定〕的地方照它写的倾向写。
2. 歌、二十二张、碑是正史，一个字不动，你写的要跟它们对得上。原主线里大纲说照留的拍子照留，能用原句的用原句。
3. 主线是给主持的骨架，不是小说：一幕三到五拍，一拍一两句，台词只留最要紧的一两句。英雄、传奇出手先写天地和远处的人看见什么。对手有名有脸，玩家当面碰得上。
4. 写作口径整节（附在下面），卡面的标点、禁词、月相字、东方语感的字、玩家在场、什么杀得死传奇、怎么踏进传奇、起名，一条一条照守。
5. 四份写作 skill（附在下面），写之前读完。

卡面的规矩：
- 不用——、—、；、…、！、...，冒号只在标签行（八个字以内）。对白用“”。
- 神用祂。那一位恶神不点名。四执政不入场。
- 新起的设定在卡面句末标（★）。
- 格式照原主线：## 标题、【调用】、题和篇、引语、开局、世道、一幕二幕三幕（每幕一拍一条，末一条幕终）、收束、默认收束、玩家能改、碰得上的人、## 裁定锁、条目设置。条目设置那一行照原稿抄，只改触发里要跟着改的名字。

交什么：直接输出 Markdown，前后不加别的话。
1. 改好的整条主线，连同裁定锁和条目设置。
2. 新起的对手写一条人物条，格式照原页人物条（## 纷争纪·人物｜……（人物）那一种）。
3. 末尾一节「## 设计备注（不进卡）」：改了什么，新起的名字，旅伴条、人物条、凡世至强里哪几处要跟着改（一句一处）。

'''


def system():
    cl = PB.rd('CLAUDE.md')
    rules = PB.sec(cl, r'^## 写作口径', r'^## 换账号接手')
    skills = ['# skill：%s\n\n%s' % (n, open(os.path.join(PB.SK, n, 'SKILL.md'), encoding='utf-8').read())
              for n in ['western-fantasy-prose', 'chinese-prose-register', 'jrpg-lore-writing', 'genshin-dialogue-voice']]
    return HEAD + '# 写作口径（CLAUDE.md 整节）\n\n' + rules + '\n\n' + '\n\n'.join(skills)


def outline_of(name):
    t = SR.rd(os.path.join(D, '大纲_合并_第一版.md'))
    m = re.search(r'^(#{2,4}) [^\n]*' + re.escape(name) + r'[^\n]*$', t, re.M)
    lv = len(m.group(1))
    n = re.search(r'^#{2,%d} ' % lv, t[m.end():], re.M)
    return t[m.start():m.end() + (n.start() if n else len(t))]


def build():
    s = system()
    fx = SR.rd(os.path.join(rb.ROOT, '纷争纪', '纷争纪_方向与写法_第二版.md'))
    cards = rb.section(fx, r'^## 六、逐张', r'^## 七、')
    reqs = []
    for name, n, part in JOBS:
        t = SR.page_text(n)
        main, _ = SR.mains_of(t, [name])
        # 这一条碰得上的旅伴、人物条，和这一页的凡世至强（全页那几节）
        people = '\n'.join(b for h, b in SR.blocks(t) if ('（人物）' in h or h.startswith('## 纷争纪·凡世至强')))
        user = '\n\n'.join([
            '# 你的活\n\n写纷争纪第%s页的主线「%s」的样稿。' % ('一二三四五六七'[n - 1], name),
            '# 改稿大纲合并稿里你这一条\n\n' + outline_of(name),
            '# 方向稿第六节 逐张（二十二张，正史）\n\n' + cards,
            '# 这一页的页头和时段总纲\n\n' + SR.head_of(t),
            '# 这一页的史诗（歌，正史）\n\n' + '\n'.join(b for h, b in SR.blocks(t) if '（史诗·纷争纪）' in h),
            '# 这一条的审稿\n\n' + SR.rd(os.path.join(D, '审_%s.md' % part)),
            '# 原主线（带裁定锁和旅伴名单）\n\n' + main,
            '# 这一页的人物条和凡世至强（对账用）\n\n' + people,
        ])
        reqs.append({'custom_id': 'sample_%d' % len(reqs), 'params': {
            'model': MODEL, 'max_tokens': 64000, 'thinking': {'type': 'adaptive'}, 'output_config': {'effort': 'high'},
            'system': s, 'messages': [{'role': 'user', 'content': user}]}})
    return reqs


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    cmd = sys.argv[1]
    if cmd == 'build':
        for r, j in zip(build(), JOBS):
            print(j[0], len(r['params']['system']), len(r['params']['messages'][0]['content']))
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
        for line in rb.call(d['results_url']).splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            name = b['jobs'][int(r['custom_id'].rsplit('_', 1)[1])]
            if r['result']['type'] != 'succeeded':
                print('！没成', name, json.dumps(r['result'], ensure_ascii=False)[:300])
                continue
            msg = r['result']['message']
            text = ''.join(c.get('text', '') for c in msg['content'] if c.get('type') == 'text')
            open(os.path.join(D, '样稿_%s.md' % name), 'w', encoding='utf-8', newline='\n').write(text.strip() + '\n')
            print('%s：%d 字，停在 %s，进 %d 出 %d' % (name, len(text), msg.get('stop_reason'), msg['usage']['input_tokens'], msg['usage']['output_tokens']))
