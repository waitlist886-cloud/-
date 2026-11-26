# 女神体态数据（11-26，备注在 底稿/神域/备注_女神体态_11-26.md）：算罩杯、写进两纪神谱和底卡七神洗稿层。不加 --apply 只报。
import re, sys, glob, math, json, os
ROOT = r'E:/aldran_art'
APPLY = '--apply' in sys.argv

CUPS = 'ABCDEFGHIJK'
def cup(b, w):
    """下胸围按腰围加 7.5 估，差照 JIS：A 是 10，每 2.5 一档，上下各让 1.25"""
    diff = b - (w + 7.5)
    i = math.floor((diff - 8.75) / 2.5)
    edge = abs(((diff - 8.75) / 2.5) - round((diff - 8.75) / 2.5)) < 1e-9
    return ('AA' if i < 0 else CUPS[i]), diff, edge

# 名字：(身高, 胸, 腰, 臀 或 None 照未成年写法, 身形句, 人间形态那一小句或 None)
D = {
 '风之璐璐薇': (176, 88, 58, 88, '腿长腰细，站在风口上羽衣整片往后翻，脚下一步不挪', None),
 '破晓之风莉尤': (163, None, None, None, '身量轻，腿长，跑起来脚踝上的贝壳串一路响，停下来也站不久', None),
 '群翼的牧童塔兰迦': (158, None, None, None, '身量细，肩窄，背上那对白翅膀收拢了，翅尖垂到脚跟', None),
 '满帆之手欧希拉': (178, 97, 72, 98, '肩宽臂粗，两条胳膊赤着，一整匹湿帆布单手拎起来往桅杆上搭', None),
 '未落之箭卡瑟蕾': (174, 84, 62, 88, '精瘦，背阔，左肩比右肩略高一点，是常年拉弓拉出来的', None),
 '隘口的呼啸瓦尔缇': (185, 93, 68, 96, '高，骨架大，腿长，顶着山口的风站一夜，辫梢往山口那边飘，人不晃', None),
 '卷云弥尔瓦': (180, 101, 74, 100, '肩宽背厚，浑身湿透，甲板翻得再凶，两只脚也像钉在船板上', None),
 '第一口气与最后一口气塞维娅': (168, 83, 58, 86, '身段平常，坐在病床边半天不动，胸口一起一伏跟屋里的灯焰同一个拍子', None),
 '空笼与断缰之主阿科洛': (165, 80, 57, 84, '细，手脚伶俐，赤脚踩着河里的石头一跳一跳，站在一处总待不久', None),
 '河心的坐石莫兰特': (170, 87, 62, 90, '匀称，腰背稳，赤脚在湿滑的河石上来回走，一回也没滑过', None),
 '朝潮夕汐之主乌姆拉': (180, 98, 70, 100, '高，身架舒展，动得极慢，往滩上一站，身后的海退一步',
                    '人间形态（★）祂难得扮成人，扮了是一个高个子的渔妇，深水颜色的长发湿着贴在背上，站在潮退得太远的滩上'),
 '灯芯与灰烬的女主人莉薇兰': (177, 80, 60, 84, '瘦高，肩骨把衣裳撑起来，俯身看灯芯的时候整个人弯成一道弧', None),
 '霜息卡因霖': (182, 90, 62, 92, '高挑，肩平背直，裹着白狐皮在雪地里走，脚印浅得像没踩下去', None),
 '千结之绳奥兹米尔': (152, 78, 56, 82, '小个子，手指又细又灵，坐下来手里那根绳一刻也不停', None),
 '收获之库米罗妮': (168, 81, 58, 86, '身量单薄，走在一队人最后头，脚步轻得听不见，拄着的白蜡木长杖点地也没有声音', None),
 '垂首的金穗格蕾诺': (178, 103, 78, 104, '宽厚，胳膊有劲，头总低着，弯着腰割完一垄麦也不直起身歇一口', None),
 '群兽的乳母弥诺亚': (170, 102, 74, 102, '身量宽厚，前臂粗壮，一头躁着的牛偎过来靠在祂身上，祂晃都不晃', None),
 '灰烬里的新绿科尔妮': (176, 80, 60, 86, '瘦长，窄肩，筋骨像一根刚抽条的新枝，背着一大捆柴走过烧过的地', None),
 '花信的报春人梅莉茜': (158, 82, 57, 85, '小巧，身子轻，弯腰从花丛里穿过去，一枝花也碰不落', None),
 '不腐之盐萨尔缇': (168, 84, 61, 88, '细，肩背是扛盐扛出来的，一袋盐压在肩上站着，跟没压一样', None),
 '活水涅琉': (170, 81, 58, 86, '瘦，筋骨匀，挑两桶满水走过井台，一滴不洒', None),
 '幸运之艾赫卡托尔': (165, 86, 57, 86, '身轻腰细，在河边一蹲就是一天，钓线不晃，脚边那只猫也睡着了', None),
 '纺命之指阿兹瓦': (160, 80, 60, 84, '瘦小，腰板直，十根手指上缠满了线，掷钱的时候一根也不绞在一起', None),
 '两色之瞳提莉安': (155, None, None, None, '身量小，手脚轻，坐在门槛上两只脚一里一外晃个不停', None),
 '歧路的重逢薇尔蜜': (162, None, None, None, '身架细，肩窄，一手提灯一手端着汤锅也走得稳', None),
 '命中之签尤诺': (163, 84, 62, 88, '身段寻常，不高不矮，站进一排人里就找不着了', None),
 '先手之牌莉斯卡': (168, 88, 58, 88, '手长腿长，坐在牌桌边背不靠椅，两指夹着那张牌一晚上不放下', None),
 '治愈之朱亚': (151, 80, 55, 82, '个子小，手稳，换药的手从来不抖，扶起一个比祂高一头的伤兵也扶得动', None),
 '疫棚里的凉风塞雷娜': (178, 83, 60, 88, '高，细，背直，袖子挽到肘上，在疫棚里从天黑站到天亮', None),
 '初啼玛特罗娜': (164, 101, 76, 102, '丰满，圆润，一只手托得住刚落地的孩子，另一只手在他背上拍那一下', None),
 '合创贝尔娜': (156, 82, 62, 86, '矮，结实，手劲大，按住伤口的那一下整个人都压上去', None),
 '黑暗里的暖手卢缇亚': (166, 84, 59, 87, '纤细，闭着眼走在一队人最前头，伸出来的那只手一直不收回去', None),
 '青唇的药师菲洛缇': (167, 80, 58, 84, '瘦，指尖凉，弯腰凑近药碗闻的时候鼻尖几乎碰着碗沿', None),
 '鸦羽的女王艾尔缪': (170, 90, 58, 90, '高挑，腰细，坐在临终的人床边，赤红斗篷垂到地上，从头到尾一动不动', None),
 '代痛之身多萝缇': (160, 80, 57, 83, '瘦小，赤着脚，替人疼的时候身子不缩，青的只是手背', None),
 '息祭者薇瑟兰': (175, 87, 64, 91, '高，身板直，骨架匀，在两军之间的盐滩上站一整天，两手空着垂在身侧', None),
}
# 底卡七神（洗稿层 #86 到 #92 里的女神），显相
DK = {
 '风之璐璐薇（Lulwy of Wind）': ('风之璐璐薇', None),
 '收获之库米罗妮（Kumiromi of Harvest）': ('收获之库米罗妮', (142, None, None, None, '身量小，肩窄，进了谁家都要踮起脚才看得见锅里煮着什么', None)),
 '幸运之艾赫卡托尔（Ehekatl of Luck）': ('幸运之艾赫卡托尔', None),
 '治愈之朱亚（Jure of Healing）': ('治愈之朱亚', None),
}

def line(name, rec, ai_only, label):
    h, b, w, hp, s, star = rec
    pre = '' if ai_only else '只给 AI，'
    lab = star if star else label
    parts = ['- 体态数据｜%s%s' % (pre, lab), '身高 %dcm' % h]
    if b is not None:
        c, diff, edge = cup(b, w)
        if edge:
            raise SystemExit('%s 差 %.2f 落在档的边上，换个数' % (name, diff))
        parts += ['三维 %d / %d / %d' % (b, w, hp), '%s-cup' % c]
    parts.append(s + '。')
    return '｜'.join(parts)

table = []
for n, r in D.items():
    if r[1] is not None:
        c, diff, _ = cup(r[1], r[2])
        table.append((n, r[0], '%d/%d/%d' % r[1:4], diff, c))
    else:
        table.append((n, r[0], '-', None, '照未成年写法'))
for t in table:
    print(t)

files = sorted(glob.glob(ROOT + '/月银纪补卷/神谱_0*.md')) + sorted(glob.glob(ROOT + '/纷争纪/补卷/补卷_6[0-7]_*.md'))
done = []
for f in files:
    s = open(f, encoding='utf-8').read()
    lines = s.split('\n')
    out = []
    i = 0
    cur = None; ai = False
    for l in lines:
        m = re.match(r'^## (月银纪|纷争纪)·神谱｜(.+)$', l)
        if m:
            cur = m.group(2).strip(); ai = False
        elif l.startswith('## '):
            cur = None
        if cur and l.startswith('【调用】只给 AI'):
            ai = True
        if cur in D and l.startswith('- 体态数据｜') and out and out[-1].startswith('- 体态数据｜'):
            continue                     # 重跑：上一回插的那一行拿掉，下面重插
        out.append(l)
        if cur in D and l.startswith('- 样子：'):
            out.append(line(cur, D[cur], ai, '人间形态'))
            done.append((os.path.basename(f), cur))
    ns = '\n'.join(out)
    # 体态数据要在神力前头（build_shenyu 重跑拿掉的是神力到锁那一块）
    for m in re.finditer(r'^## (?:月银纪|纷争纪)·神谱｜(.+)\n(.*?)(?=^## |\Z)', ns, re.M | re.S):
        b = m.group(2)
        if '- 体态数据｜' in b:
            assert b.index('- 体态数据｜') < b.index('- 神力：'), m.group(1)
    if APPLY and ns != s:
        open(f, 'w', encoding='utf-8', newline='\n').write(ns)
print('神谱添了', len(done), '条')

wf = ROOT + '/底卡洗稿/批次_03隐藏真相_04神祇_三.md'
s = open(wf, encoding='utf-8').read()
out = []; cur = None; dk = []
for l in s.split('\n'):
    m = re.match(r'^## (.+)$', l)
    if m and not m.group(1).startswith('#'):
        cur = m.group(1).strip()
    if cur in DK and l.startswith('- 体态数据｜') and out and out[-1].startswith('- 体态数据｜'):
        continue
    out.append(l)
    if cur in DK and l.startswith('- 显相：'):
        nm, own = DK[cur]
        out.append(line(nm, own or D[nm], False, '显相'))
        dk.append(nm)
ns = '\n'.join(out)
if APPLY and ns != s:
    open(wf, 'w', encoding='utf-8', newline='\n').write(ns)
print('底卡七神添了', dk)
