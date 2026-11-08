#!/usr/bin/env python3
# 主提示词添一段：档案写出生日期，岁数照底座日期现算（11-08 生日代替年龄）。发布卡直接插，v12 走 进卡补丁_rili_v12.py 的 SYS_REPS。
#   python 算岁数.py pub <发布卡.json> <输出.json>
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
AGE_RULE = ('档案里写的是出生日期（生于〔纪〕〔年〕·〔月名〕·〔旬〕〔日〕），不是岁数：岁数照底座的日期现算，今年减生年，今年的生日还没到再减一'
            '（月份顺序萌芽、花信、清露、长曦、炎潮、蝉鸣、金穗、坠叶、霜降、初雪、寒星、归寂，一月三旬、一旬十日）。'
            '跨纪的换成总年数再减：月银纪前N年＝1-N，月银纪Y年＝Y，纷争纪Y年＝10080+Y，山铜纪Y年＝21113+Y，迷宫纪Y年＝22059+Y。'
            '档案写了外表的，年龄那一栏写 岁数（外表…）；生年不详的照档案写。上一轮写过的岁数照抄，过了生日那一天才加一。'
            '主角首轮照凭证的岁数和开局日期定一个出生日期，写在年龄那一栏，如 `18岁（生于迷宫纪982年·寒星月·下旬四日）`，往后照它算。')
PUB_ANCHOR = '`§角色｜全名｜种族 / 年龄 / 性别｜立绘:短名`'
V12_ANCHOR = '预设旅伴与传奇的种族、年龄、职业、命路、誓心、能力以档案为准'

if __name__ == '__main__' and sys.argv[1] == 'pub':
    card = json.load(open(sys.argv[2], encoding='utf-8'))
    sp = card['prompt']['systemPrompt']
    assert sp.count(PUB_ANCHOR) == 1 and AGE_RULE not in sp
    card['prompt']['systemPrompt'] = sp.replace(PUB_ANCHOR, PUB_ANCHOR + '\n' + AGE_RULE)
    with open(sys.argv[3], 'w', encoding='utf-8', newline='\n') as f:
        json.dump(card, f, ensure_ascii=False)
    print('主提示词添好了')
