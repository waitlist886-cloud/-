#!/usr/bin/env python3
# 别的几纪的战装分档（11-22）：照 war_batch.py（山铜纪 11-21）那一套，用户 11-22 说“山铜纪已经改过的不用画，其他的都画”。
# 月银纪史诗、诸国期、萨尔维斯、纷争纪、前传已经画过的人，一人判位阶、家境、偏好，照各纪新写的「战装补层（11-22）」改写 battle 那一句（旧句留进 battle_old）。
# 这一回不走 API（额度用完了），材料切成份，交子任务写，交稿放回来再收。
#   python -I -X utf8 底稿/立绘/tools/war_batch2.py mat            出 底稿/立绘/战装_11-22/分档/说明_<纪>.md 和 材料/<纪>_<cast文件>_<n>.md
#   python -I -X utf8 底稿/立绘/tools/war_batch2.py take [--apply]  收 交稿/*.md，--apply 写回 cast，出重画任务 重画/<纪>.json
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import war_batch as WB  # noqa: E402  entry()、section() 照用

W = os.path.join(ROOT, '底稿', '立绘', '战装_11-22', '分档')
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
SETS = ['月银纪史诗', '诸国期', '萨尔维斯', '纷争纪', '前传']
WARF = {'纷争纪': 'war_纷争纪.json', '萨尔维斯': 'war_萨尔维斯.json', '诸国期': 'war_月银纪.json', '月银纪史诗': 'war_月银纪.json', '前传': 'war_前传.json'}
CHUNK = 20
rd = WB.rd


def people(setn):
    out = []
    for p in sorted(glob.glob(os.path.join(COMFY, 'cast', setn, '*.json'))):
        try:
            arr = json.load(open(p, encoding='utf-8'))
        except Exception:
            continue
        if not isinstance(arr, list):
            continue
        for x in arr:
            if not isinstance(x, dict) or not x.get('en') or not x.get('battle'):
                continue
            if not os.path.exists(os.path.join(COMFY, 'out', '立绘_' + setn, x['en'], 'cell_battle.png')):
                continue      # 没出图的不改（这一轮新写资料的人照说明直接写）
            out.append((os.path.basename(p)[:-5], x))
    return out


def fashion(setn):
    old = rd(os.path.join(ROOT, '底稿', '立绘', '各时代风尚_旧三纪.md'))
    new = rd(os.path.join(ROOT, '底稿', '立绘', '各时代风尚_新三纪.md'))
    if setn == '纷争纪':
        return WB.section(old, r'^## 纷争纪', r'^## 萨尔维斯')
    if setn == '萨尔维斯':
        return WB.section(old, r'^## 萨尔维斯', r'^## 诸国期')
    if setn == '诸国期':
        return WB.section(old, r'^## 诸国期', r'^## 祭火与万兽')
    if setn == '月银纪史诗':
        return WB.section(old, r'^## 祭火与万兽', r'^## 活过几段')
    return WB.section(new, r'^## 二、迷宫纪前传', r'^## 三、')


def tiers():
    new = rd(os.path.join(ROOT, '底稿', '立绘', '各时代风尚_新三纪.md'))
    i = new.index('**战装分档（11-21')
    return new[i:new.index('\n\n', i)]


def samples():
    out = []
    for p in sorted(glob.glob(os.path.join(COMFY, 'cast', '山铜纪', 's?n.json'))):
        for x in json.load(open(p, encoding='utf-8')):
            if x['en'] in WB.SAMPLES and x.get('battle_old'):
                out.append('- %s %s（%s）\n  改前：%s\n  改后：%s' % (x['en'], x['name'], x.get('gear', ''), x['battle_old'], x['battle']))
    return '\n'.join(out)


def brief(setn):
    war = json.load(open(os.path.join(ROOT, '底稿', '立绘', '战装_11-22', WARF[setn]), encoding='utf-8'))
    rank = WB.section(rd(os.path.join(ROOT, 'CLAUDE.md')), r'^### 命星', r'^### 时段页的格式')
    rank = '\n'.join(l for l in rank.split('\n') if l.startswith('- 位阶'))
    return ('# 战装分档改写｜%s（11-22）\n\n' % setn +
            '你给一张日式西幻 JRPG 跑团卡《奥尔德兰的旅印》改写角色立绘第三格（战斗那一身）的英文描述。用户看了山铜纪新人的战斗格说“比起时代的军事和科技太落后”，'
            '于是山铜纪先写了各段的「战装补层」、定了「战装分档」，逐人改写了战斗句、重画了战斗格（下面有六张用户认过的改前改后）。11-22 用户说先照山铜纪那样针对战装查一下，'
            '战斗装得符合纪元、年代和角色本身的设定，山铜纪以外已经画过的人都重画。这一份是%s。\n\n' % setn +
            '# 战装分档（用户 11-21 定的，各纪通用）\n\n' + tiers() + '\n\n'
            '# 这一纪的风尚（各段末尾的「战装补层（11-22）」是这一轮写的，照它）\n\n' + fashion(setn) + '\n\n'
            '# 出图脚本里各段的战装层（英文，给你参考用词；出图时会自动拼在你写的句子后头，你那一句里不用重复这一段的大背景）\n\n```json\n' +
            json.dumps(war, ensure_ascii=False, indent=1) + '\n```\n\n# 位阶\n\n' + rank +
            '\n\n# 山铜纪用户认过的六张（改前、改后，学详略和写法，别搬山铜纪的东西）\n\n' + samples() + '\n\n'
            '# 怎么改\n\n'
            '- 先从原页那一条和长相里判三样：位阶（原页底座或位阶那一行；没写的照身份和本事估，写明是估的），家境（贫、中、富、世家或上城，看出身和身份），偏好（照常、朴素、不靠装备、法袍、不打仗……，有来由才判不照常）。'
            '再定装备档 1 到 5：1 干活的衣服外头一两件这一段有的附魔件或兽材，2 一套改合身的旧甲带一两样会亮的东西，3 成套的这一段的战装加一件招牌，4 量身打造、设计过的，5 这一纪顶上的那一身。'
            '位阶定底子，家境低位阶时加减一到两档，极境以上至多一档，英雄往上不看家境；偏好朴素的照档用好料子，样子去装饰，偏好不靠装备的就别硬穿甲。魔族照它那一系在这一段的样子。\n'
            '- 年代要对：照这个人在资料出处那一页那一年。那一年还没有的东西不写（纷争纪 1020 年以前没有成批的附魔铠甲，前传 400 年以前西边没有电，各纪有没有火药照上面的补层），也别写得比那一年落后。'
            '有位阶走势的，照立绘画的那一刻。\n'
            '- 改写那一句：英文，跟样张一样的详略（七八十到一百二十个词），开头保留原句的场面短语（Holding the crossing: 这一类），兵器、手里拿的东西、姿势、法术光效、跟故事有关的物件一样不丢、不换，'
            '只把衣甲升到那一档，写清每一件是什么、哪里发光、什么颜色的符文或光。资料的配色照旧。不写脸、头发、眼睛、身材，不写场景、家具和地面（设定图要抠透明底），'
            '火和光贴在身上或兵器上，别往地上铺。不写东方式样（交领、宽袖、盘扣）。不写 crescent、moon。\n'
            '- 出图那边有安全审核，11-22 有两位因为“暴力和自残”被挡：不写血淋淋的、割开的、献祭、自残、伤口淌血这些字，血誓、血魔这一路写成暗红的光、红色的纹、誓带、刻印。\n'
            '- 原句本来就不是打仗的（修士、孩子、文书、不出手的人），或者资料写了 battle_pose（第三格整句换掉的姿势句），照这个人的路子：可以只是一件附魔披风、一枚护符、法袍上的符文，'
            '或者不改，写明为什么，battle 照原句交回。未成年（minor）的照旧穿得严实，档往低里判。\n'
            '- 同一个人在别处也有立绘的（同一个 same_as、同名），战装跟着他那时的位阶和年代走，偏好前后一样。传奇（legend）和凡世至强写出这一纪顶上那一档的气势。\n\n'
            '# 交什么\n\n一个 ```json 代码块，里面是一个数组，一人一条：{"en": "…", "rank": "灵格（估）", "wealth": "贫", "pref": "照常", "level": 2, "why": "一句中文，为什么是这一档、这个偏好", "battle": "改写后的英文"}。'
            'en 照材料里【】里的键原样抄。材料里每个人都要有一条，次序照材料。前后不加别的话。\n')


def mat():
    os.makedirs(os.path.join(W, '材料'), exist_ok=True)
    for f in glob.glob(os.path.join(W, '材料', '*.md')):
        os.remove(f)
    tot = 0
    for setn in SETS:
        open(os.path.join(W, '说明_%s.md' % setn), 'w', encoding='utf-8', newline='\n').write(brief(setn))
        by = {}
        for fn, x in people(setn):
            by.setdefault(fn, []).append(x)
        n = 0
        for fn, arr in by.items():
            for i in range(0, len(arr), CHUNK):
                part = arr[i:i + CHUNK]
                blocks = []
                for x in part:
                    b = ['【%s】%s（%s，%s）' % (x['en'], x['name'], x.get('sex', ''), x.get('tier', ''))]
                    for k in ('same_as', 'minor', 'legend', 'imposing'):
                        if x.get(k):
                            b.append('%s：%s' % (k, x[k]))
                    b.append('资料出处：' + x.get('src', ''))
                    b.append('长相（英文资料）：' + x['who'][:600])
                    b.append('常服：' + x.get('casual', '')[:400])
                    b.append('现在的战装（要改写的这一句）：' + x.get('battle_old', x['battle']))
                    if x.get('battle_pose'):
                        b.append('第三格另有姿势句 battle_pose（出图时只顶掉第三格那一句通用姿势，衣甲照旧从 battle 来；不打仗的人照「怎么改」那一条，打仗的照常改 battle）：' + x['battle_pose'][:400])
                    try:
                        b.append('原页里他那一条：\n' + WB.entry(x))
                    except Exception as ex:
                        b.append('原页里他那一条：（取不到 %s）' % ex)
                    blocks.append('\n'.join(b))
                name = '%s_%s_%d' % (setn, fn, i // CHUNK + 1)
                head = '# %s｜%s 第 %d 份：%d 人（说明在 ../说明_%s.md）\n\n' % (setn, fn, i // CHUNK + 1, len(part), setn)
                open(os.path.join(W, '材料', name + '.md'), 'w', encoding='utf-8', newline='\n').write(
                    head + '\n'.join('=' * 20 + '\n' + b + '\n' for b in blocks))
                n += len(part)
        print(setn, n, '人')
        tot += n
    print('一共', tot, '人', len(glob.glob(os.path.join(W, '材料', '*.md'))), '份')


def take(apply):
    want = {}
    for setn in SETS:
        for fn, x in people(setn):
            want[(setn, x['en'])] = x
    got = {}
    for f in sorted(glob.glob(os.path.join(W, '交稿', '*.md'))):
        setn = os.path.basename(f).split('_')[0]
        m = re.search(r'```json\s*\n(.*?)\n```', rd(f), re.S)
        if not m:
            print('！没有 json', os.path.basename(f))
            continue
        for d in json.loads(m.group(1)):
            k = (setn, d.get('en'))
            if k not in want:
                print('！对不回', os.path.basename(f), d.get('en'))
                continue
            if k in got:
                print('！重了', k)
            got[k] = d
    miss = sorted(k for k in want if k not in got)
    print('交回', len(got), '要', len(want), '缺', len(miss), miss[:20])
    lv = {}
    for d in got.values():
        lv[str(d.get('level'))] = lv.get(str(d.get('level')), 0) + 1
    print('各档人数', dict(sorted(lv.items())))
    json.dump({'%s|%s' % k: v for k, v in got.items()}, open(os.path.join(W, '收稿.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    if not apply:
        return
    os.makedirs(os.path.join(W, '重画'), exist_ok=True)
    for setn in SETS:
        tasks = []
        for p in sorted(glob.glob(os.path.join(COMFY, 'cast', setn, '*.json'))):
            try:
                arr = json.load(open(p, encoding='utf-8'))
            except Exception:
                continue
            if not isinstance(arr, list):
                continue
            n = 0
            for x in arr:
                if not isinstance(x, dict):
                    continue
                d = got.get((setn, x.get('en')))
                if d and d.get('battle'):
                    changed = d['battle'].strip() != x.get('battle_old', x['battle']).strip()
                    x.setdefault('battle_old', x['battle'])
                    x['battle'] = d['battle']
                    x['gear'] = '%s｜%s｜%s｜%s档｜%s' % (d.get('rank'), d.get('wealth'), d.get('pref'), d.get('level'), d.get('why'))
                    if changed:     # 照原句交回的不重画（battle_pose 只换第三格那一句通用姿势，衣甲照 battle，改了照样重画）
                        tasks.append({'en': x['en'], 'cell': 'battle'})
                    n += 1
            if n:
                json.dump(arr, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
                print('写了', setn, os.path.basename(p), n)
        json.dump(tasks, open(os.path.join(W, '重画', setn + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        print('重画', setn, len(tasks))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    if sys.argv[1] == 'mat':
        mat()
    elif sys.argv[1] == 'take':
        take('--apply' in sys.argv)
