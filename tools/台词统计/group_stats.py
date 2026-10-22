#!/usr/bin/env python3
"""按身份、性格、场合三条轴汇总台词形状。用法：python3 -I -X utf8 group_stats.py OUT_DIR"""
import glob, json, os, re, statistics, sys
from collections import defaultdict
OUT = sys.argv[1]
STATUS = {
    '神与古老者': '温迪 钟离 雷电将军 影 纳西妲 那维莱特 玛薇卡 魈 闲云 八重神子 甘雨 茜特菈莉',
    '执政与首领': '琴 凝光 刻晴 珊瑚宫心海 神里绫人 艾尔海森 芙宁娜 阿蕾奇诺 娜维娅 北斗 莱欧斯利',
    '军人与执法者': '九条裟罗 赛诺 克洛琳德 夏沃蕾 五郎 优菈 米卡 安柏 鹿野院平藏 夜兰 法尔伽',
    '贵族与名门': '神里绫华 迪卢克 行秋 林尼 千织 凯亚',
    '学者医者匠人': '丽莎 阿贝多 莫娜 提纳里 白术 卡维 珐露珊 莱依拉 烟绯 砂糖 艾梅莉埃 希诺宁',
    '江湖、营生与冒险': '班尼特 菲谢尔 迪希雅 坎蒂丝 嘉明 枫原万叶 辛焱 云堇 妮露 宵宫 香菱 多莉 绮良良 托马 诺艾尔',
    '孩子与少年': '可莉 七七 早柚 瑶瑶 迪奥娜 雷泽 重云 卡齐娜',
    '敌对与暗处': '达达利亚 「公子」 流浪者 散兵 「散兵」',
}
TEMPER = {
    '元气热络': '安柏 班尼特 香菱 宵宫 辛焱 玛拉妮 嘉明 迪希雅 荒泷一斗 可莉 卡齐娜',
    '冷淡寡言': '魈 申鹤 迪卢克 克洛琳德 雷泽 赛诺 艾尔海森 夜兰',
    '温和体贴': '芭芭拉 诺艾尔 琴 珊瑚宫心海 神里绫华 纳西妲 托马 久岐忍 白术',
    '狡黠爱逗': '八重神子 凯亚 胡桃 林尼 神里绫人 达达利亚 温迪',
    '别扭嘴硬': '迪奥娜 刻晴 流浪者 莫娜 闲云 九条裟罗',
    '戏剧与中二': '菲谢尔 芙宁娜 荒泷一斗 云堇',
    '老成古雅': '钟离 闲云 魈 萍姥姥 茜特菈莉',
    '怕生拘谨': '柯莱 七七 早柚 绮良良 莱依拉',
}
PART = ['呢', '吧', '啊', '呀', '哦', '嘛', '啦', '哟', '喔', '咯', '哇', '罢了', '而已', '么']
INTJ = re.compile(r'^(嗯|啊|哦|唔|欸|诶|哈|呼|嘿|咳|哼|呵|哎|唉|嗨|呃|咦|哇)')
CLASS = '之乎者也矣焉哉亦其乃汝尔甚岂莫勿毋皆此彼故遂且犹'
def plen(x): return len(re.sub(r'[\s「」『』，。！？…、：；“”‘’（）—\-·]', '', x))
def prof(lines):
    n = len(lines) or 1
    L = [plen(x) for x in lines]
    clauses = [s.strip('，、 「」') for x in lines for s in re.split(r'[。！？…]+', x) if s.strip('，、 「」')]
    part = sum(1 for s in clauses if any(s.endswith(p) for p in PART) and not re.search(r'(什|怎|这|那|多|要|干)么$', s)) / (len(clauses) or 1)  # 什么、怎么这一类的么不算
    chars = sum(L) or 1
    return dict(n=len(lines), med=statistics.median(L) if L else 0, p90=sorted(L)[int(len(L) * .9)] if L else 0,
                part=part, intj=sum(1 for x in lines if INTJ.match(x)) / n,
                q=sum(1 for x in lines if '？' in x) / n, exc=sum(1 for x in lines if '！' in x) / n,
                ell=sum(1 for x in lines if '…' in x) / n, you=sum(1 for x in lines if '你' in x or '您' in x) / n,
                nin=sum(1 for x in lines if '您' in x) / n, cls=sum(sum(x.count(c) for c in CLASS) for x in lines) / chars * 100)
voice, story = defaultdict(list), defaultdict(list)
occ = defaultdict(list)
for f in glob.glob(os.path.join(OUT, 'lines*.jsonl')):
    for l in open(f, encoding='utf-8'):
        e = json.loads(l)
        if e['src'] == 'voice' and e['speaker'] != '旅行者':
            voice[e['speaker']].append(e['text'])
            ti = re.sub(r'…+$', '', e['qtitle']); ti = re.sub(r'·.*', '', ti)
            if ti.startswith('关于') and ti not in ('关于我们', '关于「神之眼」') and not ti.startswith(f'关于{e["speaker"]}'):
                ti = '关于别人'
            elif ti.startswith(f'关于{e["speaker"]}'):
                ti = '关于自己'
            occ[ti].append(e['text'])
        elif e['src'] in ('quest', 'idle') and not e.get('player'):
            story[e['speaker']].append(e['text'])
def table(groups, src, title):
    rows = [f'### {title}\n', '| 组 | 人数 | 句数 | 句长中位 | 九成句长 | 句尾语气词 | 叹词起头 | 带问号 | 带感叹号 | 带省略号 | 对人说你您 | 用您 | 文言虚字/百字 |', '|' + '---|' * 13]
    for g, names in groups.items():
        ns = [n for n in names.split() if src.get(n)]
        lines = [x for n in ns for x in src[n]]
        if not lines: continue
        p = prof(lines)
        rows.append(f'| {g} | {len(ns)} | {p["n"]} | {p["med"]:.0f} | {p["p90"]} | {p["part"]:.2f} | {p["intj"]:.2f} | {p["q"]:.2f} | {p["exc"]:.2f} | {p["ell"]:.2f} | {p["you"]:.2f} | {p["nin"]:.2f} | {p["cls"]:.1f} |')
    return '\n'.join(rows) + '\n'
md = ['# 台词形状统计（原神简中，本地语料）\n', '句长按汉字算，标点不计。句尾语气词按分句算，其余按整句算。\n']
md.append(table(STATUS, voice, '按身份，角色语音'))
md.append(table(STATUS, story, '按身份，剧情对话'))
md.append(table(TEMPER, voice, '按性格，角色语音'))
md.append(table(TEMPER, story, '按性格，剧情对话'))
OCC = ['初次见面', '闲聊', '下雨的时候', '下雪的时候', '打雷的时候', '阳光很好', '早上好', '中午好', '晚上好', '晚安', '关于自己', '关于我们', '关于「神之眼」', '有什么想要分享', '感兴趣的见闻', '关于别人', '想要了解', '喜欢的食物', '讨厌的食物', '收到赠礼', '生日', '突破的感受', '元素战技', '元素爆发', '打开宝箱', '加入队伍', '生命值低', '同伴生命值低', '倒下', '重受击']
rows = ['### 按场合，角色语音\n', '| 场合 | 句数 | 句长中位 | 九成句长 | 句尾语气词 | 叹词起头 | 带问号 | 带感叹号 | 带省略号 | 对人说你您 |', '|' + '---|' * 10]
for o in OCC:
    ls = occ.get(o, [])
    if not ls: continue
    p = prof(ls)
    rows.append(f'| {o} | {p["n"]} | {p["med"]:.0f} | {p["p90"]} | {p["part"]:.2f} | {p["intj"]:.2f} | {p["q"]:.2f} | {p["exc"]:.2f} | {p["ell"]:.2f} | {p["you"]:.2f} |')
md.append('\n'.join(rows) + '\n')
open(os.path.join(OUT, 'stats_groups.md'), 'w', encoding='utf-8').write('\n'.join(md))
print('\n'.join(md))
