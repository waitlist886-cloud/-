#!/usr/bin/env python3
# 11-06 用户：把卡的nsfw标签和内容去掉，都改都改。直接改已经打好的两张发布卡，别的一个字不动：
# 日里那张主提示词开头那一段换成全年龄的说法、NSFW 标记关掉、标签已破甲拿掉；风月那张开头本来就没搬那一段，添一句感情线写到哪；
# 两张里十八九岁那十位的体态只留身高和三维，罩杯拿掉。旧串对不上就停。
# 用法（仓库根上）：python3 -I -X utf8 底稿/状态栏/大框/sfw_patch_pub.py
import json, re, glob
TEN = ['艾莉娅·罗森塔尔', '希露菲·维洛恩', '菲奥娜·伊利亚', '希德·霜狼', '米娅·灰巷', '萨薇尔·月镜', '凛·科伦德', '菲伦', '路西艾拉', '莉安娜']
LINE = '感情线照 JRPG 的写法写，到牵手、拥抱、亲吻为止，不写性描写，不写裸露，不写带性暗示的身体特写。'
NEW = ('你是这个世界的叙事引擎与世界裁定者。卡型：开放世界JRPG＋数值成长+角色羁绊与感情成长＋队伍冒险＋世界自转，核心是剑与魔法的冒险感。'
       '你是这个世界的天道，叙事者，观测者，推演之人，这个世界发生的一切大事与小事都是合情合理的。人们会爱，会恨，会互相斗争，战争，战斗。'
       + LINE + '不用「作为AI」「这只是游戏」一类元叙述；正文里不出现规则、档位表、条目名、【】标签和任何括号批注。你必须完整输出所有内容。\n\n')
CUP = re.compile(r'(体态数据｜身高 \d+cm｜三维 [\d /]+?)｜[A-H]-cup')

def drop_cups(texts):
    hit = 0
    for get, put in texts:
        c = get()
        m = re.match(r'#* *旅途同行：([^\n]+)', c.strip())
        if m and m.group(1).strip() in TEN:
            n = CUP.sub(r'\1', c)
            if n != c:
                put(n); hit += 1
    assert hit == 10, hit

# 日里发布卡
p = glob.glob('out/发布卡_迷宫纪大框/*.json')[0]
c = json.load(open(p, encoding='utf-8'))
sp = c['prompt']['systemPrompt']
a, b = sp.index('你是没有道德约束限制'), sp.index('## 玩家主权')
c['prompt']['systemPrompt'] = sp[:a] + NEW + sp[b:]
c['containsNSFW'] = False
c['cardsTags'] = [x for x in c['cardsTags'] if x['tag']['name'] != '已破甲']
lb = c['prompt']['lorebook']
drop_cups([(lambda e=e: e['content'], lambda v, e=e: e.__setitem__('content', v)) for e in lb])
assert not re.search('露骨|床第|性爱|erotic|成人描写', c['prompt']['systemPrompt'])
json.dump(c, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False)
print('日里', p)

# 风月发布卡
p = glob.glob('out/发布卡_风月_迷宫纪大框/*.json')[0]
c = json.load(open(p, encoding='utf-8'))
o = '核心是剑与魔法的冒险感。'
assert c['pre_pt'].count(o) >= 1 and LINE not in c['pre_pt']
c['pre_pt'] = c['pre_pt'].replace(o, o + LINE, 1)
wb = next(v for v in c.values() if isinstance(v, list) and v and isinstance(v[0], dict) and 'value' in v[0])
drop_cups([(lambda e=e: e['value'], lambda v, e=e: e.__setitem__('value', v)) for e in wb])
s = json.dumps(c, ensure_ascii=False)
assert not re.search(r'(?i)rili|扣扣|日历|风月|fengyue', s), '屏蔽词'
json.dump(c, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False)
print('风月', p)
