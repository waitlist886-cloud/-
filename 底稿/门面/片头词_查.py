#!/usr/bin/env python3
# 片头的词交稿以后照卡面口径过一遍：拍数、长短版字数、禁用标点、月相字、禁词、不碰的名字、太长的拍。
# 认的写法：一拍一行，“编号. ●/○ 词”，或者“编号 ●/○ 词”“● 编号. 词”这几种小出入。
# 用法：python -I -X utf8 片头词_查.py 稿子.md [稿子2.md …]
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
BAN_P = r'[—…！；!;]|\.\.\.|--'
MOON = r'新月|满月|残月|月牙|弦月|月亮|月光|月相|月色|明月'
BAN_W = (r'学宫|客栈|朝廷|门客|时辰|掌柜|百官|丫头|宗门|长老|功法|镖局|一丝|一抹|不禁|威压|修为|登记|军令|条例|晋升|量子|熵|坐标|频率|能量|系统|'
         r'爹|娘亲|师父|徒弟|江湖|内力|仿佛|宿命|命运的齿轮|历史的车轮')
NAMES = r'厄洛伽|伊斯塔露|纳贝里士|阿斯莫代|凯尔萨斯|薇瑟兰|理想国|执政'
cn = lambda t: len(re.findall(r'[一-鿿]', t))
for path in sys.argv[1:]:
    s = open(path, encoding='utf-8').read().replace('\r\n', '\n')
    beats = []
    for ln in s.split('\n'):
        m = re.match(r'^\s*(?:[-*]\s*)?(?:\*\*)?(\d{1,2})(?:\*\*)?[\.、．]?\s*([●○])\s*(.+?)\s*$', ln) or re.match(r'^\s*(?:[-*]\s*)?([●○])\s*(\d{1,2})[\.、．]\s*(.+?)\s*$', ln)
        if not m:
            continue
        a, b, c = m.groups()
        num, mark = (int(a), b) if a.isdigit() else (int(b), a)
        beats.append((num, mark, re.sub(r'^\*\*|\*\*$', '', c)))
    print('==', path.replace('\\', '/').split('/')[-1])
    if not beats:
        print('   没认出一拍一行的词'); continue
    nums = [b[0] for b in beats]
    text = '\n'.join(b[2] for b in beats)
    print('   拍数 %d（编号 %d 到 %d%s），● %d，长版 %d 字，短版 %d 字' % (len(beats), nums[0], nums[-1], '' if nums == list(range(nums[0], nums[0] + len(nums))) else '，编号不连着',
          sum(1 for b in beats if b[1] == '●'), sum(cn(b[2]) for b in beats), sum(cn(b[2]) for b in beats if b[1] == '●')))
    long_ = [(b[0], cn(b[2])) for b in beats if cn(b[2]) > 25]
    print('   过二十五个字的拍', long_ if long_ else '无')
    for label, rx in (('禁用标点', BAN_P), ('月相字', MOON), ('禁词', BAN_W), ('不碰的名字', NAMES)):
        hit = [(b[0], m.group(0)) for b in beats for m in re.finditer(rx, b[2])]
        print('   %s %s' % (label, hit if hit else '无'))
    she = len(re.findall(r'[她他它]', text)), len(re.findall(r'祂', text)), len(re.findall(r'你', text))
    print('   她他它 %d 处，祂 %d 处，你 %d 处' % she)
