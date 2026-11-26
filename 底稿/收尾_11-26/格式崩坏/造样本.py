# 造“模型写歪了”的样本：拿干跑 1001 第三轮（打仗那一轮）和第二轮（不打仗）当底，一种歪法一份
import os, re, sys, json
ROOT = 'E:/aldran_art'
# 用法：python -I -X utf8 造样本.py <输出目录>（不进库，跑一回就有）
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
R = ROOT + '/tools/dryrun/runs/迷宫纪1001/'
B3 = open(R + '轮3_回复.txt', encoding='utf-8').read().replace('\r', '')
B2 = open(R + '轮2_回复.txt', encoding='utf-8').read().replace('\r', '')
L3 = B3.split('\n')

def idx(lines, pre):
    return [i for i, l in enumerate(lines) if l.startswith(pre)]

def blk(lines, pres):
    return [l for l in lines if any(l.startswith(p) for p in pres)]

WAR = ('§战斗｜', '§敌情｜', '§战况｜')
war = blk(L3, WAR)
nowar = [l for l in L3 if not l.startswith(WAR)]
cases = {}
def put(name, text, note):
    cases[name] = (text, note)

put('00_正常_战斗轮', B3, '干跑原样')
put('00_正常_平常轮', B2, '干跑原样')
# ---- 战斗栏放错地方 ----
def insert_before(lines, pre, block):
    i = idx(lines, pre)[0]
    return lines[:i] + block + lines[i:]
def insert_after_last(lines, pre, block):
    i = idx(lines, pre)[-1] + 1
    return lines[:i] + block + lines[i:]
put('W01_战斗栏在分支前头', '\n'.join(insert_before(nowar, '§分支｜', war)), '战斗栏写在 §分支 前头（正文刚完就写敌情）')
put('W02_战斗栏夹在面板和装备中间', '\n'.join(insert_before(nowar, '§装备｜', war)), '战斗栏写在 §面板｜委托 和 §装备 中间')
put('W03_战斗栏夹在角色中间', '\n'.join(insert_before(nowar, '§角色｜艾珂娅', war)), '战斗栏写在两组角色之间')
put('W04_战斗栏在末尾', '\n'.join(insert_before(nowar, '§预载｜', war)), '战斗栏写在记忆后头、预载前头')
put('W05_战斗栏写两遍', '\n'.join(insert_before(L3, '§面板｜身份', war)), '战斗栏照写一遍，面板前又抄了一遍')
put('W06_战斗栏没有头一行', '\n'.join(l for l in L3 if not l.startswith('§战斗｜')), '§战斗 那一行漏了，只有 §敌情、§战况')
put('W07_战斗栏没头又写在面板中间', '\n'.join(insert_before(nowar, '§装备｜', [l for l in war if not l.startswith('§战斗｜')])), '没有 §战斗 那一行，敌情战况写在面板中间')
# 出战斗那一轮：残半截
lastwar = B2.split('\n')
put('W08_出战斗残半截', '\n'.join(insert_before(lastwar, '§面板｜身份', ['§战斗｜外围圈第三段·掘地鼠扑车｜已胜', '§敌情｜掘地鼠头鼠｜约 LVL 8｜已倒下'])), '仗打完那一轮：战斗头一行写已胜，敌情只剩半截两栏')
put('W09_出战斗写无', '\n'.join(insert_before(lastwar, '§面板｜身份', ['§战斗｜无', '§敌情｜无', '§战况｜弱点｜无', '§战况｜注意｜无'])), '不打仗的轮照写一套 无')
put('W10_出战斗只剩战况', '\n'.join(insert_before(lastwar, '§面板｜身份', ['§战况｜注意｜骡子受了惊，车在坡上'])), '不打仗了还留一行 §战况')
put('W11_战斗和背包挤一行', B3.replace('§战况｜注意｜骡子受了惊，车在坡上，笼头一松车就往下溜\n', '§战况｜注意｜骡子受了惊，车在坡上，笼头一松车就往下溜 §物品｜消耗｜火把×2｜Normal｜照明·1kg｜点着能烧半个钟头\n'), '§战况 那一行末尾接着写了一条 §物品')
put('W12_敌情栏数不对', B3.replace('§敌情｜掘地鼠头鼠｜约 LVL 8｜没见血｜破防，仰面翻在车辕下｜危险｜两息之内翻不过身', '§敌情｜掘地鼠头鼠｜约 LVL 8｜没见血｜危险｜两息之内翻不过身').replace('§敌情｜掘地鼠 ×5｜约 LVL 5｜一只后胯带伤｜没乱｜相当｜四只围在两步外，一只咬着骡子后腿', '§敌情｜掘地鼠 ×5｜LVL 5｜轻伤·80｜稳固·90｜相当｜围着｜一只咬着骡子后腿｜多一栏'), '敌情一行少两栏、一行多一栏、伤势不带条长')
put('W13_战斗栏写成小标题加列表', '\n'.join(insert_before(nowar, '§面板｜身份', ['【战斗栏】', '- 遭遇：外围圈第三段·掘地鼠扑车（交战中）', '- 敌情：掘地鼠头鼠 约 LVL 8，破防，危险', '- 敌情：掘地鼠 ×5 约 LVL 5，相当', '- 弱点：头鼠喉下的软毛', '- 注意：骡子受了惊'])), '战斗栏写成【战斗栏】小标题加一串列表（不是记录行）')
put('W14_战斗栏写成表格', '\n'.join(insert_before(nowar, '§面板｜身份', ['| 敌人 | 等级 | 伤势 | 架势 | 威胁 |', '|---|---|---|---|---|', '| 掘地鼠头鼠 | 约 8 | 没见血 | 破防 | 危险 |', '| 掘地鼠 ×5 | 约 5 | 轻伤 | 没乱 | 相当 |'])), '战斗栏写成 Markdown 表格')
put('W15_史诗和战斗一起', '\n'.join(insert_before(L3, '§面板｜身份', ['§首领｜深沟鼠王｜第三段坡下', '§史诗｜深沟鼠王｜阶段 I/III｜鼠潮｜LVL 14｜外围圈第三段', '§史诗势｜稳固·90｜稳固·80', '§史诗况｜已识别｜群鼠跟着它走'])), '普通战斗栏和史诗战卡同时写了')
# ---- 物品栏 ----
def rep_bag(lines, f):
    return '\n'.join(f(l) if l.startswith('§物品｜') else l for l in lines)
put('B01_数量写法五花八门', B3.replace('黑面包×1｜', '黑面包 x1｜').replace('水囊×1｜', '水囊 ×1｜').replace('库房七号木牌×1｜', '库房七号木牌(1)｜').replace('见习旅印×1｜', '见习旅印*1｜').replace('父亲的旧肩垫×1｜', '父亲的旧肩垫×1件｜'), '名×数写成 x1、空格×1、(1)、*1、×1件')
put('B02_少一栏', rep_bag(L3, lambda l: re.sub(r'｜Normal｜', '｜', l, count=1)), '每样东西漏了品阶那一栏（四栏）')
put('B03_多一栏', rep_bag(L3, lambda l: l + '｜0.2kg｜可出售'), '每样东西末尾多两栏')
put('B04_一行超长', B3.replace('§物品｜消耗｜黑面包×1｜Normal｜口粮·0.2kg｜母亲早上塞的，一块顶半天', '§物品｜消耗｜黑面包×1｜Normal｜口粮·0.2kg｜' + '母亲早上塞的，一块顶半天，掰开来里头还夹着一片咸肉，咸肉是上个月在棚区口那家卖面包的店里换来的，用的是父亲替人背货挣的两个便士，' * 4), '一样东西的说明写到四百字')
put('B05_一行塞好几样', B3.replace('§物品｜消耗｜黑面包×1｜Normal｜口粮·0.2kg｜母亲早上塞的，一块顶半天\n§物品｜消耗｜水囊×1｜Normal｜饮水·1kg｜羊皮水囊，装满够喝一天', '§物品｜消耗｜黑面包×1、水囊×1、火把×3、绷带×2'), '一类东西挤成一行用顿号隔开')
put('B06_类别写错', B3.replace('§物品｜消耗｜黑面包', '§物品｜食物｜黑面包').replace('§物品｜贵重｜', '§物品｜杂物｜').replace('§物品｜不可丢弃｜见习旅印', '§物品｜任务物品｜见习旅印'), '类别写成 食物、杂物、任务物品')
put('B07_背包写成一段', '\n'.join([l for l in L3 if not l.startswith('§物品｜')][:idx([l for l in L3 if not l.startswith('§物品｜')], '§背包｜')[0]] + ['§背包｜随身｜黑面包一块、水囊一只、库房七号木牌、见习旅印、父亲的旧肩垫'] + [l for l in L3 if not l.startswith('§物品｜')][idx([l for l in L3 if not l.startswith('§物品｜')], '§背包｜')[0]:]), '没写 §物品，背包写成一行')
put('B08_物品写在角色后头', '\n'.join(insert_after_last([l for l in L3 if not l.startswith('§物品｜')], '§角色', blk(L3, ('§物品｜',)))), '§物品 几行挪到角色后头（次序颠倒）')
put('B09_装备栏数不齐', B3.replace('§装备｜副手｜旧木圆盾｜Normal｜圆盾·PV+2｜漆面剥了大半，盾心钉着一块补过的铁皮，上头两道凹痕｜分会库房租的，损坏照价从押金里扣', '§装备｜副手｜旧木圆盾（Normal，圆盾，PV+2）').replace('§装备｜上衣｜粗麻短外套｜Normal｜外套｜洗得发白的灰褐粗麻，两肩各缝着一块加厚的补丁｜无', '§装备｜上衣｜粗麻短外套｜Normal｜外套｜洗得发白的灰褐粗麻｜无｜耐久 80%｜多一栏'), '装备一行写成一句、一行多两栏')
put('B10_装备部位写别的叫法', B3.replace('§装备｜主手｜空置', '§装备｜武器｜空置').replace('§装备｜副手｜', '§装备｜盾牌｜').replace('§装备｜上衣｜', '§装备｜护甲｜'), '部位写成 武器、盾牌、护甲')
put('B11_物品带引号', B3.replace('§物品｜不可丢弃｜父亲的旧肩垫×1', '§物品｜不可丢弃｜"父亲的旧肩垫"×1'), '物品名带半角引号')
put('B12_物品写无', B2.replace('§背包｜队伍共用｜无', '§物品｜无\n§物品｜消耗｜无\n§背包｜队伍共用｜无'), '写了 §物品｜无、§物品｜消耗｜无')
# ---- 通用 ----
def drop(lines, pres):
    return '\n'.join(l for l in lines if not any(l.startswith(p) for p in pres))
put('G01_漏了见闻', drop(L3, ('§见闻｜',)), '整段见闻没写')
put('G02_漏了面板', drop(L3, ('§面板｜', '§装备｜', '§状态｜')), '整段面板和装备没写')
put('G03_背包在面板前头', '\n'.join(insert_before([l for l in L3 if not l.startswith(('§物品｜', '§背包｜'))], '§面板｜身份', blk(L3, ('§物品｜', '§背包｜')))), '背包写在面板前头（次序颠倒）')
put('G04_记忆在见闻前头', '\n'.join(insert_before([l for l in L3 if not l.startswith('§记忆｜')], '§见闻｜', blk(L3, ('§记忆｜',)))), '记忆写在见闻前头')
put('G05_面板写两遍', '\n'.join(insert_before(L3, '§见闻｜', blk(L3, ('§面板｜',)))), '面板十几行在见闻前头又抄了一遍')
put('G06_竖线少了', B3.replace('§面板｜资源｜HP 168/176 MP 85/85 SP 96/112 架势 58/74｜饱食 70%', '§面板｜资源｜HP 168/176 MP 85/85 SP 96/112 架势 58/74 饱食 70%').replace('§角色签｜见习冒险者｜无｜LVL 11', '§角色签｜见习冒险者 无｜LVL 11').replace('§物品｜消耗｜水囊×1｜Normal｜', '§物品｜消耗｜水囊×1 Normal｜'), '几行里少了一道竖线')
put('G07_竖线多了', B3.replace('§面板｜六维｜STR', '§面板｜六维｜｜STR').replace('§角色行｜羁绊｜好感 Lv.1 初次见面的关系 4/10 ｜', '§角色行｜羁绊｜｜好感 Lv.1 初次见面的关系 4/10 ｜'), '几行里多了一道竖线')
put('G08_半角竖线和冒号', B3.replace('§物品｜消耗｜黑面包×1｜Normal｜口粮·0.2kg｜', '§物品:消耗:黑面包×1|Normal|口粮·0.2kg|').replace('§装备｜鞋｜旧皮短靴｜Normal｜短靴｜', '§装备|鞋|旧皮短靴|Normal|短靴|').replace('§底座｜纪元：', '§底座:纪元:'), '半角竖线、半角冒号当分隔')
put('G09_HTML没关', B3.replace('§面板｜身份｜', '<div class="status"><b>状态栏\n§面板｜身份｜'), '面板前头混进一段没关的 HTML')
put('G10_旧版HTML状态栏', B3.split('§面板｜身份')[0] + '<details open><summary>📜 冒险者面板</summary>\n<div class="panel"><table><tr><td>HP</td><td>168/176</td></tr><tr><td>MP</td><td>85/85</td></tr>\n<p>背包：黑面包×1、水囊×1\n</details>\n§记忆｜已完成｜无', '面板以后整段写成老版 HTML（details、table），标签没关全')
put('G11_【】没关', B3.replace('§能力｜Art｜皇家宫廷剑术｜Rare｜一阶·×1.2｜', '§能力｜Art｜【皇家宫廷剑术｜Rare｜一阶·×1.2｜'), '能力一行里一个【没关')
put('G12_代码围栏包状态栏', B3.replace('§面板｜身份', '```\n§面板｜身份', 1).replace('§预载｜', '```\n§预载｜'), '面板到记忆包在一对代码围栏里')
put('G13_代码围栏没收', B3.replace('§面板｜身份', '```text\n§面板｜身份', 1), '面板前头开了代码围栏，没收')
put('G14_没写底座', '\n'.join(l for l in L3 if not l.startswith(('§底座｜',))), '底座那一行漏了')
put('G15_底座写歪', B3.replace('§底座｜纪元：迷宫纪1001年·春·萌芽月·上旬四日 · 08:32 上午 · ', '§底座｜迷宫纪1001年 春 萌芽月 上旬四日 08:32（上午）'), '底座日期和时间的分隔写歪')
put('G16_正文写在面板后头', '\n'.join(insert_after_last([l for l in L3 if not (l and not l.startswith('§')) and not l.startswith(('§正文｜', '§话｜', '§判｜', '§技｜', '§起手｜'))], '§记忆｜', [l for l in L3 if (l and not l.startswith('§')) or l.startswith(('§正文｜', '§话｜', '§判｜', '§技｜', '§起手｜'))])), '正文和对话写在记忆后头')
put('G17_记录前有空格和列表号', '\n'.join(('  ' + l if l.startswith('§面板') else ('- ' + l if l.startswith('§物品') else ('1. ' + l if l.startswith('§见闻') else l))) for l in L3), '面板行前有空格，物品行前有 - ，见闻行前有 1. ')
put('G18_记录之间空行', '\n\n'.join(L3), '每一行之间都空了一行')
put('G19_同一行写两条记录', B3.replace('§面板｜姿态｜', '§面板｜着装｜沾了土 §面板｜姿态｜').replace('§见闻｜流言风闻｜', '§见闻｜已知情报｜无。§见闻｜流言风闻｜'), '两条记录写在同一行')
put('G20_角色组写两遍', '\n'.join(insert_before(L3, '§见闻｜', [l for l in L3 if l.startswith(('§角色', ))][:12])), '头一个人的角色组在见闻前又抄了一遍')
put('G21_名目写错', B3.replace('§面板｜身份｜', '§状态栏｜身份｜').replace('§物品｜消耗｜黑面包', '§背包物品｜消耗｜黑面包').replace('§见闻｜日报｜', '§日报｜'), '名目写成 §状态栏、§背包物品、§日报')
put('G22_全角冒号当分隔', B3.replace('§物品｜消耗｜黑面包×1｜Normal｜', '§物品：消耗：黑面包×1：Normal：').replace('§面板｜位阶｜', '§面板：位阶：'), '全角冒号当竖线')
# 截断
for pct in (25, 45, 60, 75, 90):
    n = int(len(B3) * pct / 100)
    put('T%02d_截断在%d%%' % (pct, pct), B3[:n], '回复写到 %d%%（%d 字）断了，断在行中间' % (pct, n))
put('T99_截断在战斗栏中间', B3[:B3.index('§敌情｜掘地鼠 ×5') + 18], '回复断在第二行敌情中间')
put('B13_类型和品阶写长', B3.replace('§物品｜消耗｜水囊×1｜Normal｜饮水·1kg｜', '§物品｜消耗｜水囊×1｜Normal｜饮水·1kg·羊皮缝的·能装一天的水·挂在腰上｜').replace('§物品｜不可丢弃｜父亲的旧肩垫×1｜Normal｜', '§物品｜不可丢弃｜父亲的旧肩垫×1｜Normal（旧物）｜'), '类型一栏写到二十几个字，品阶写成 Normal（旧物）')
put('G23_写进一段style', B3.replace('§分支｜趁', '<style>.sz-page{display:none} details summary{opacity:.2} .sz-tabs{display:none}</style>\n§分支｜趁', 1), '正文末尾混进一段 <style>（学别的卡的 HTML 状态栏写法）')
put('G24_面板前开了details没关', B3.replace('§面板｜身份｜', '<div class="status-panel"><details open><summary>📜 状态</summary>\n§面板｜身份｜', 1), '面板前头开了 <div><details>，没关')
for k, (t, note) in cases.items():
    open(os.path.join(OUT, k + '.txt'), 'w', encoding='utf-8').write(t)
json.dump({k: v[1] for k, v in cases.items()}, open(os.path.join(OUT, '_notes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(cases))
