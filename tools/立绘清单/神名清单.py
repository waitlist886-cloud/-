# -*- coding: utf-8 -*-
"""神名清单（给立绘会话）：神名表.tsv + 月银纪、纷争纪神谱的是谁、样子、高座、倒下 + 七支柱底卡显相（洗稿层）。
魔神的样子另从 --gods-look（史诗战那一份收稿后抽出的 本体 json）补。
用法：python3 -I -X utf8 god_list.py 仓库根 输出.md [--gods-look look.json]"""
import sys, re, os, json, glob
root, out = sys.argv[1], sys.argv[2]
look = {}
if '--gods-look' in sys.argv:
    look = json.load(open(sys.argv[sys.argv.index('--gods-look') + 1], encoding='utf-8'))
look.setdefault('薇瑟兰', '人前是一个高个子女人，三十来岁的样子，看不出哪一族，褐里夹灰的短发，洗白了的旧军大氅，没有纹章，补过的靴子，手里什么也不拿（山铜纪/山铜纪时段_一_犁的年月.md 设计备注第10条，各页人物条「不说名字的女人」）。不上墙，不是谁的史诗战对手。')
bronze_hdrs = []
if '--bronze' in sys.argv:
    for line in open(sys.argv[sys.argv.index('--bronze') + 1], encoding='utf-8'):
        if line.startswith('### '): bronze_hdrs.append(line[4:].strip())
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(root, '底稿/神名/神名表.tsv'), encoding='utf-8')][1:]
def clean(s):
    s = re.sub(r'（★[^）]*）', '', s); s = s.replace('★', '')
    return s.strip()
def parse(globpat, head):
    d = {}
    for f in sorted(glob.glob(os.path.join(root, globpat))):
        t = open(f, encoding='utf-8').read()
        for m in re.finditer(r'^## ' + head + r'｜([^\n]+)\n(.*?)(?=^## |\Z)', t, re.S | re.M):
            title, body = m.group(1).strip(), m.group(2)
            fields = {}
            for fm in re.finditer(r'^- ([^：\n]{1,8})：(.*)$', body, re.M):
                fields.setdefault(fm.group(1), clean(fm.group(2)))
            d[title] = (fields, os.path.relpath(f, root))
    return d
moon = parse('月银纪补卷/神谱_*.md', '月银纪·神谱')
strife = parse('纷争纪/补卷/补卷_6[0-7]_神谱_*.md', '纷争纪·神谱')
def find(d, name):
    for k, v in d.items():
        if k.endswith(name): return k, v
    return None, ({}, '')
# 七支柱底卡显相（洗稿层）
pillar = {}
t = open(os.path.join(root, '底卡洗稿/批次_03隐藏真相_04神祇_三.md'), encoding='utf-8').read()
for m in re.finditer(r'^## #(8[6-9]|9[0-2]) ([^\n（]+)[^\n]*\n(.*?)(?=^## #|\Z)', t, re.S | re.M):
    body = m.group(3); f = {}
    for k in ('显相', '神器', '神仆', '神性'):
        mm = re.search(r'^- ' + k + r'：(.*)$', body, re.M)
        if mm: f[k] = clean(mm.group(1))
    pillar[m.group(2).strip()] = f
def first(s):
    if not s: return ''
    i = s.find('。')
    return s[:i + 1] if i >= 0 else s
L = []
w = L.append
w('# 神名清单（给立绘会话用）')
w('')
w('2026-11-07 从仓库里抽的，正文不改。用户说这一份跟史诗战的阶段名号一起搬到跑立绘的那个会话里。')
w('')
w('- 神号是平常叫的那一段，叫祂的时候写神号加本名（百锤之父卡尔德隆、死水威沛）。尊号是两段的全称。旧名号是 11-07 以前的叫法，卡里的旧条目和触发还认它。')
w('- 样子分两纪。月银纪是本相，和祂下到人间扮成的样子（月银纪补卷/神谱_*）；纷争纪是墙上的人见到祂的样子（纷争纪/补卷/补卷_60 到 _67）。七支柱另附底卡 1001 年那一局的显相、神器、神仆（底卡 #86 到 #92 洗稿层）。')
w('- 魔神的神谱没有样子那一栏，写的是高座和奉祂的人。魔神每一阶的样子在 底稿/立绘/史诗战名号/ 纷争纪那两份里，这里的“样子”一行是那两份写的本体。活到山铜纪的九尊坐上高座以后另有一套样子，在山铜纪那一份。')
w('- 原文里新起设定标的★这里去掉了。神不画月相，神用祂。那一位恶神不在这张表里，也不画。')
w('')
groups = []
for r in rows:
    pil, kind, name, ref, old, hao, zun = (r + [''] * 7)[:7]
    groups.append((pil, kind, name, ref, old, hao, zun))
order = ['离弦', '负山', '翻页', '返青', '立边', '静光', '不退']
w('## 一、七支柱')
w('')
for pil, kind, name, ref, old, hao, zun in groups:
    if kind != '柱': continue
    full = hao + name
    mk, (mf, mfile) = find(moon, name); sk, (sf, sfile) = find(strife, name)
    p = next((v for k, v in pillar.items() if k.endswith(name)), {})
    w(f'### {pil}·{full}')
    w(f'- 尊号：{zun}')
    w(f'- 是谁：{sf.get("是谁") or mf.get("是谁", "")}')
    if mf.get('样子'): w(f'- 月银纪的样子：{mf["样子"]}')
    if sf.get('样子'): w(f'- 纷争纪的样子：{sf["样子"]}')
    if p.get('显相'): w(f'- 1001年的显相（底卡）：{p["显相"]}')
    if p.get('神器') or p.get('神仆'): w(f'- 神器、神仆（底卡）：{p.get("神器", "")} {p.get("神仆", "")}'.rstrip())
    w('- 下落：活到纪末，迷宫纪起正名七支柱、通称七神，迷宫纪起本人不现身。')
    w('')
for sect, kd, label in (('二', '正', '正神'), ('三', '魔', '魔神')):
    n = sum(1 for g in groups if g[1] == kd)
    w(f'## {sect}、{label}（{n}）')
    w('')
    for pil in order:
        w(f'### {pil}')
        w('')
        for pil2, kind, name, ref, old, hao, zun in groups:
            if pil2 != pil or kind != kd: continue
            mk, (mf, mfile) = find(moon, name); sk, (sf, sfile) = find(strife, name)
            title = sk or mk or (hao + name)
            w(f'**{title}**')
            w(f'- 尊号：{zun}。旧名号：{old}。' + (f'祂是{ref}的倒影。' if ref and kd == '魔' else ''))
            who = sf.get('是谁') or mf.get('是谁', '')
            if who: w(f'- 是谁：{who}')
            if kd == '正':
                if mf.get('聚成'): w(f'- 聚成（月银纪）：{first(mf["聚成"])}')
                if mf.get('样子'): w(f'- 月银纪的样子：{mf["样子"]}')
                if sf.get('样子'): w(f'- 纷争纪的样子：{sf["样子"]}')
            else:
                if sf.get('高座'): w(f'- 高座：{sf["高座"]}')
                lk = look.get(name)
                w(f'- 样子：{lk}' if lk else '- 样子：见 史诗战名号/ 下纷争纪那两份里这一尊那一块。')
                hits = [h for h in bronze_hdrs if name in h]
                if hits: w('- 山铜纪坐上高座以后的样子：见 史诗战名号/山铜纪.md 的 ' + '、'.join(hits) + '。')
            down = sf.get('倒下') or ''
            if down: w(f'- 倒下：{first(down)}')
            elif kd == '魔': w('- 倒下：纷争纪里没有倒下，往后的事看山铜纪。')
            else: w('- 倒下：活到纪末。')
            w('')
w('## 四、已经画过的（往后画同一位，先拿这几张对）')
w('')
w('- 七支柱，迷宫纪1001年那一局：四方右扇 底稿/状态栏/comfy/out/四方_11-03/art_fu_ab/maze_right.webp，画法在 底稿/状态栏/comfy/README.md 第九、十回。朱亚、库米罗妮、艾赫卡托尔、欧巴德斯照底卡 #87、#89、#90、#91 修过一回（comfy/fix_gods.py），底卡没写的发色和衣服照 Elona 官方立绘。艾赫卡托尔的硬币上是一张笑着的猫脸，幸运之首画成腰间一把小匕首。')
w('- 纷争纪四方 底稿/状态栏/comfy/out/纷争纪_11-04/art/（strife_left、strife_right，提示词 comfy/gpt_strife.py）。左上五尊魔神：绝后者亚蒙，兜帽，胸口透白光，身后没路；自噬的狼群玛尔乔西亚斯，坐着的一个人，近看是一群兽；错位之骨弗劳洛斯，骨头全折反；拆墙者拜恩，9318年以后的样子，断左角，瞎右眼，胸口东门的火；不愈之镞勒莱耶，一身烂疮的弓手。右上五位正神：举盾者斯卡索；立誓者奥尔达，黑纱，无鬃黑马，石戒；擎山者多尔加恩，肩上积雪；未落之箭卡瑟蕾，红铜短发；断后者雷格纳。')
w('- 亚蒙两阶的 Boss 立绘 boss_yamon1、boss_yamon2（同上目录），葛摩恩两阶 boss_gemoen1、boss_gemoen2（底稿/状态栏/comfy/out/山铜纪_11-04/art/），提示词都在 底稿/状态栏/comfy/gpt_boss.py。亚蒙没有脸，一张兜帽底下的暗面；葛摩恩脸上是一整块没有五官的山铜板，伸出来的那只手五个指头是五把打铁的大钳。')
w('')
open(out, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('写了', out, len(L), '行；神谱月银纪', len(moon), '条，纷争纪', len(strife), '条，七支柱显相', len(pillar))
