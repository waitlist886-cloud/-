#!/usr/bin/env python3
# 把第四到七页二十颗要接半句的 Special 的头一段印出来，核对接的那句老话里说话的人在原句里有没有出处。
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
STARS = {
    '纷争纪/parts4/t6_stars.md': ['压焰呼吸', '血墨守誓'],
    '纷争纪/parts4/t6b_stars_2400.md': ['坠风心跳'],
    '纷争纪/parts4/t6d_stars_1790.md': ['醒面指尖', '拔根臂膀'],
    '纷争纪/parts4/t6e_stars_3600.md': ['长哨喉咙', '风信发梢'],
    '纷争纪/parts4/t6f_stars_4200.md': ['隔岭耳廓'],
    '纷争纪/parts5/u6_stars.md': ['镜天眼眸', '拨火指尖'],
    '纷争纪/parts5/u6d_stars_7166.md': ['归羽直觉', '穿风哨音'],
    '纷争纪/parts5/u6e_stars_7672.md': ['余温角尖'],
    '纷争纪/parts5/u6f_stars_5300.md': ['车铃脉搏'],
    '纷争纪/parts5/u6g_stars_8780.md': ['回声指腹'],
    '纷争纪/parts6/v6_stars.md': ['甜锈嗅觉'],
    '纷争纪/parts6/v6c_stars_9520.md': ['林冠瞳孔'],
    '纷争纪/parts6/v6e_stars_10200.md': ['地声脚掌'],
    '纷争纪/parts7/w6_stars.md': ['风传哨', '门闩警戒'],
}
for f, names in STARS.items():
    t = open(f, encoding='utf-8').read().replace('\r\n', '\n')
    for n in names:
        m = re.search(r'^### ' + re.escape(n) + r'[^\n]*\n(.*?)(?=^### |\Z)', t, re.M | re.S)
        if not m:
            print('!! 没找到', f, n)
            continue
        body = m.group(1)
        # 头一段：【调用】那一行以后、第一个 "- " 栏以前
        lines = [x for x in body.split('\n') if x.strip()]
        lead = [x for x in lines if not x.startswith('【调用】') and not x.startswith('- ') and not x.startswith('>')]
        print('== %s｜%s' % (f.split('/')[-1], n))
        for x in lead[:2]:
            print('   ' + x)
