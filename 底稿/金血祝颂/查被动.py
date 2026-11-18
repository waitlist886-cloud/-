#!/usr/bin/env python3
# 金血祝颂改纯被动那一轮的收稿检查（11-17 夜）：照 被动样稿.md「新的写法」查 稿/ 对 稿_被动前/。
#   python -I -X utf8 底稿/金血祝颂/查被动.py [份N …]        不写份名就查八份
# 查的是：名字、【调用】、祝颂、箴言一字没动（份8 的只给 AI、前传的局可以改，列出来给人看）；
# 被动末尾的两项六维跟原来一样；被动里没有有次数的那一手、保命的、整类豁免这一类字眼；字数；卡面规矩。
import csv
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NEW = os.path.join(HERE, '稿')
OLD = os.path.join(HERE, '稿_被动前')
ONLY = [a for a in sys.argv[1:] if a.startswith('份')]

ROWS = list(csv.DictReader(open(os.path.join(HERE, '名单.tsv'), encoding='utf-8'), delimiter='\t'))
GODS = sorted({r['神'] for r in ROWS} | {r['倒影的魔神'] for r in ROWS if r['倒影的魔神']}, key=len, reverse=True)
SEVEN = ('欧巴德斯', '伊兹帕鲁特', '库米罗妮', '艾赫卡托尔', '朱亚', '耶万', '璐璐薇')
ERA_ONLY = ['魔神', '长垒', '段城', '联军', '军册', '萨尔维斯', '辉塔', '星冠圣城', '白烛', '客星城', '浮空塔', '机兵',
            '炮', '列车', '命路', '面板', '旅印', '公会']
SEVEN_BAN = ['公会', '旅印', '委托', '黑耀', '灰之魔女']
BAD_PUNCT = ['——', '—', '；', '…', '！', '...', '「', '」']
MOON = ['新月', '满月', '残月', '月牙', '弦月', '月亮', '月光']
STAT = re.compile(r'(STR|DEX|MANA|MIND|VGR|FTH)／(STR|DEX|MANA|MIND|VGR|FTH) \+30%。?$')
# 被动里出现就是错：有次数、要发动的那一手，保命的，整类豁免
BAN = ['每天', '每日', '每场', '每夜', '每回', '每次', '一天一回', '一回', '两回', '三回', '几回', '一次', '续命', '续上',
       '免死', '不死', '拖命', '撑到', '致死']
# 出现了要人看一眼：落在别人身上、动外头世界的、近乎豁免的
LOOK = ['替', '身边', '周围', '方圆', '十步内', '队友', '同伴', '旁人', '所有人', '全队', '身后的人', '退开', '拱起', '散开',
        '叫来', '召', '不受伤', '伤不了', '无效', '不能伤', '倍']


def parse(p):
    s = open(p, encoding='utf-8').read().replace('\r', '')
    head, _, tail = s.partition('\n## 备注')
    out = []
    heads = list(re.finditer(r'(?m)^### (.+?) \(Passive \| Legend\)\s*$', head))
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(head)
        body = head[m.end():end]
        f, lines = {}, []
        for ln in body.split('\n'):
            t = ln.strip()
            if not t or t.startswith('> 条目设置'):
                continue
            mm = re.match(r'^(?:- |> )?(祝颂|箴言|被动|限制|只给 AI|前传的局)[：，](.*)$', t)
            if mm:
                f[mm.group(1)] = mm.group(2).strip()
            elif t.startswith('【调用】'):
                f['调用'] = t[len('【调用】'):].strip()
            else:
                lines.append(t)
        out.append((m.group(1).strip(), f, lines))
    return out, tail


def han(t):
    return len(re.findall(r'[一-鿿]', t))


errs, looks, notes = [], [], []
for p in sorted(glob.glob(os.path.join(NEW, '份*.md'))):
    fen = re.match(r'(份\d)', os.path.basename(p)).group(1)
    if ONLY and fen not in ONLY:
        continue
    seven = fen == '份8'
    gods = [r['神'] for r in ROWS if r['份'] == fen]
    new, tail = parse(p)
    old, _ = parse(os.path.join(OLD, os.path.basename(p)))
    if '11-17 夜' not in tail:
        looks.append(fen + ' 备注里没有 11-17 夜改纯被动那一节')
    if len(new) != len(old) or len(new) != len(gods):
        errs.append('%s 颗数对不上：现在 %d，原来 %d，名单 %d' % (fen, len(new), len(old), len(gods)))
        continue
    for god, (nm, f, extra), (onm, of, oextra) in zip(gods, new, old):
        tag = '%s %s【%s】' % (fen, god, nm)
        if nm != onm:
            errs.append(tag + ' 名字动了（原来 %s）' % onm)
        for k in ('祝颂', '箴言'):
            if f.get(k) != of.get(k):
                errs.append(tag + ' %s 动了' % k)
        if f.get('调用') != of.get('调用'):          # 主会话收稿时把还提着拿掉那一手的【调用】改了，列出来看
            notes.append('%s 调用改了：%s' % (tag, f.get('调用', '')))
        if extra != oextra:
            errs.append(tag + ' 多了或少了别的行：' + ' / '.join(set(extra) ^ set(oextra))[:120])
        for k in ('只给 AI', '前传的局'):
            if (f.get(k) or '') != (of.get(k) or ''):
                if seven:
                    notes.append('%s %s 改了：%s' % (tag, k, f.get(k, '（拿掉了）')))
                else:
                    errs.append(tag + ' %s 动了' % k)
        bd = f.get('被动', '')
        lm = f.get('限制', '')
        st, ost = STAT.search(bd), STAT.search(of.get('被动', ''))
        if not st:
            errs.append(tag + ' 被动末尾没有“XXX／YYY +30%”')
        elif ost and st.group(0).rstrip('。') != ost.group(0).rstrip('。'):
            errs.append(tag + ' 六维跟原来不一样：%s → %s' % (ost.group(0), st.group(0)))
        core = STAT.sub('', bd)
        for w in BAN:
            if w in core:
                errs.append(tag + ' 被动里有“%s”' % w)
        hit = [w for w in LOOK if w in core]
        if hit:
            looks.append(tag + ' 被动里有 ' + '、'.join(hit) + '：' + core)
        if not 36 <= han(bd) <= 100:
            looks.append('%s 被动 %d 字（36 到 100）' % (tag, han(bd)))
        if not 10 <= han(lm) <= 60:
            looks.append('%s 限制 %d 字（10 到 60）' % (tag, han(lm)))
        if bd == of.get('被动') and lm == of.get('限制'):
            looks.append(tag + ' 被动、限制都没动')
        text = '\n'.join(v for k, v in f.items() if k not in ('只给 AI', '前传的局'))
        for g in GODS:
            if g in bd + lm:
                errs.append(tag + ' 卡面点了神名 ' + g)
        if '只给 AI' in f:
            for g in GODS:
                if g in f['只给 AI'] and g not in SEVEN:
                    errs.append(tag + ' 只给 AI 点了倒下诸神的名字 ' + g)
        for w in (SEVEN_BAN if seven else ERA_ONLY):
            if w in bd + lm:
                errs.append(tag + ' 一纪才有的字 ' + w)
        for w in BAD_PUNCT + MOON:
            if w in '\n'.join(f.values()):
                errs.append(tag + ' 禁用 ' + w)
        for k in ('被动', '限制', '只给 AI', '前传的局'):
            if '：' in f.get(k, ''):
                errs.append(tag + ' %s 那一行里还有冒号' % k)

print('== 错 %d' % len(errs))
for e in errs:
    print('  ' + e)
print('\n== 看 %d' % len(looks))
for w in looks:
    print('  ' + w)
print('\n== 份8 改了的只给 AI、前传的局 %d' % len(notes))
for w in notes:
    print('  ' + w)
