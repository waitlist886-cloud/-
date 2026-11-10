# 超凡演出（11-10，用户：“即便是近战命路本质上也是一种施法，是一种以自身引动以太的仪式……为每一种超凡表现都做出专属的演出，同时也做出纪元风格上的区分”）
# 第二稿照卡里的设定排（底卡 #559 到 #562 开通道的五种法子、各条命路的认法、四纪各自的法门和叫法，盘点在会话里，结论写进 超凡演出_说明.md）。
# 两样记录：§起手｜施放者｜名｜路·元素｜一句｜一句｜一句（引动以太的那一下）
#           §技｜施放者｜名｜路·元素｜一句结果（放出去的那一下）
# 「路」写命路（摧锋、真理……）；月银纪、纷争纪1104年以前没有命路，写那一纪的法门（饮血、呼吸、冥想、祷告、调曜、守火、结环、术、同念、誓……），或者兵器加风格（大剑·蓄斩）。
# 一种路子定四样：纹样、起手的叫法、颜色、横幅的底纹字，再归进一种演法（咏唱、祷告、演算、动作、誓约、煮药、影）。
# 纪元：回复里的 sz-era 认这一局是哪一纪，起手框和横幅换那一纪的材质和底纹（ERA）。认不出纪元的照迷宫纪。
import sys
import os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rite_svg as RS

R = '.rili-markdown-renderer:has(.sz-hud)'
ERA_SEL = {'moon': '.rili-markdown-renderer:has(.era-moon)', 'strife': '.rili-markdown-renderer:has(.era-strife)',
           'bronze': '.rili-markdown-renderer:has(.era-bronze)', 'pre': '.rili-markdown-renderer:has(.era-pre)', 'maze': '.rili-markdown-renderer:has(.era-maze)'}

# ---- 演法：一种开通道的法子一种演法。变量一样样写全，后认出来的路子整套盖掉先认出来的 ----
DEFAULT = {
    '--rl-d': 'block',                                  # 一句一行，还是几拍横着排
    '--rl-s': 'italic',
    '--rl-w': '400',
    '--rl-a': 'sz-rt-in .55s ease-out both',            # 一句怎么出来
    '--rl-st': '.3s',                                   # 一句一句隔多久
    '--rl-pre': 'none',                                 # 句前：演算的编号、誓的前引号
    '--rl-post': 'none',                                # 句后：誓的后引号
    '--rl-sep': None,                                   # 拍与拍之间（不写就跟句前一样）
    '--rl-sm': '0',                                     # 箭头后头的空
    '--rl-gap': '0',                                    # 两拍之间的空
    '--rn-a': 'sz-rt-flare .9s ease-out .8s both',      # 名字怎么出来
    '--rn-x': 'none',                                   # 名字后头落一枚印（誓约）
    '--fx-b': 'none',                                   # 叠在框上的一层：光、热气、方格、一道扫过去的光
    '--fx-a': 'none',
}
FAM = {
    # 咏唱：一句一句浮出来，斜体，名字最后亮
    'verse': {},
    # 祷告：咏唱的样子，框上从纹样那里落下一道光，慢慢地明暗
    'pray': {'--fx-b': 'radial-gradient(ellipse 120px 150% at 60px 0, color-mix(in srgb, var(--rc) 34%, transparent), transparent 72%)',
             '--fx-a': 'sz-rt-breathe 3.4s ease-in-out infinite'},
    # 演算：魔法使写他算。一二三编号，一句一句像划开，底下一层方格亮一下再淡下去
    'calc': {'--rl-s': 'normal', '--rl-w': '500', '--rl-a': 'sz-rt-wipe .5s steps(12) both', '--rl-st': '.32s',
             '--rl-pre': 'counter(rt, simp-chinese-informal) "　"', '--rn-a': 'sz-rt-flare .6s ease-out 1s both',
             '--fx-b': 'repeating-linear-gradient(0deg, color-mix(in srgb, var(--rc) 13%, transparent) 0 1px, transparent 1px 16px), repeating-linear-gradient(90deg, color-mix(in srgb, var(--rc) 13%, transparent) 0 1px, transparent 1px 16px)',
             '--fx-a': 'sz-rt-scan 1.6s ease-out .1s both'},
    # 动作：靠手艺的人不念咒，那一下的架势、呼吸、步子就是仪式。几拍横着排，名字砸下来，一道光扫过去
    'body': {'--rl-d': 'inline-block', '--rl-s': 'normal', '--rl-w': '600', '--rl-a': 'sz-rt-beat .32s ease-out both', '--rl-st': '.16s',
             '--rl-sep': '"▸"', '--rl-sm': '.45em', '--rl-gap': '.5em', '--rn-a': 'sz-rt-slam .46s cubic-bezier(.2,1.5,.4,1) .62s both',
             '--fx-b': 'linear-gradient(105deg, transparent 42%, color-mix(in srgb, var(--rc) 44%, transparent) 50%, transparent 58%) 0 0/320% 100% no-repeat',
             '--fx-a': 'sz-rt-sweep .7s ease-out .8s both'},
    # 誓约：誓写一句话、写当着谁说的。句子加引号，名字后头落一枚封蜡
    'oath': {'--rl-s': 'normal', '--rl-w': '700', '--rl-pre': '"“"', '--rl-post': '"”"', '--rn-x': '""'},
    # 煮药：有什么就煮什么。底下冒热气
    'feast': {'--rl-s': 'normal', '--rl-w': '500',
              '--fx-b': 'radial-gradient(circle at 22% 100%, rgb(255 255 255 / .18) 0 6px, transparent 18px), radial-gradient(circle at 50% 100%, rgb(255 255 255 / .13) 0 8px, transparent 22px), radial-gradient(circle at 78% 100%, rgb(255 255 255 / .16) 0 5px, transparent 16px)',
              '--fx-a': 'sz-rt-steam 3.6s ease-in infinite'},
    # 影：名字带两道残影，慢慢合成一个
    'shadow': {'--rn-a': 'sz-rt-ghost 1.1s ease-out .7s both'},
}

# ---- 路子：(认哪些字, 纹样, 起手的叫法, 颜色, 横幅底纹字, 纹样的动画, 演法)。后写的盖先写的，所以泛的在前、细的在后 ----
KINDS = [
    # 兵器（月银纪写兵器加风格；别的纪没写路的也认）
    (['剑', '刀'], 'slash', '起势', '#e9e2cf', '斩', 'tense', 'body'),
    (['枪', '矛', '戟'], 'arrow', '起势', '#e9e2cf', '突', 'tense', 'body'),
    (['斧', '锤', '拳'], 'shock', '起势', '#e9e2cf', '打', 'pulse', 'body'),
    (['弓', '弩'], 'reticle', '引弦', '#e9e2cf', '射', 'tense', 'body'),
    (['盾'], 'shield', '立盾', '#e9e2cf', '守', 'glow', 'body'),
    # 开通道的几种法子和各纪的法门（#559 魔法使、元素使，#560 祷告与奇迹，#561 血肉即法则；月银纪四门、纷争纪的术和誓、山铜纪的铳、前传和今天的圣歌）
    (['术', '咏'], 'circle', '咏唱', '#9fc0ff', '咏', 'spin', 'verse'),
    (['七课', '第八课', '大术'], 'circle', '起术', '#9fc0ff', '术', 'spin', 'verse'),
    (['同念', '落火', '兵团'], 'formation', '同念', '#efeadc', '念', 'glow', 'body'),
    (['呼吸', '调息', '岩息', '长气'], 'breath', '调息', '#9fe0d8', '息', 'pulse', 'body'),
    (['饮血'], 'blood', '饮血', '#e0344a', '血', 'beat', 'body'),
    (['冥想'], 'meditate', '冥想', '#b8c8ff', '思', 'glow', 'verse'),
    (['祷告', '祈祷', '祷'], 'halo', '祷告', '#ffe9a8', '祷', 'glow', 'pray'),
    (['奇迹', '神迹', '回话'], 'halo', '奇迹', '#fff0b0', '迹', 'glow', 'pray'),
    (['神言'], 'halo', '神言', '#fff0c0', '言', 'glow', 'pray'),
    (['圣歌', '歌'], 'song', '圣歌', '#ffe6a0', '歌', 'spin', 'pray'),
    (['调曜', '曜'], 'star', '调曜', '#e8e0ff', '曜', 'spin', 'verse'),
    (['祭火', '守火', '交火'], 'fire', '守火', '#ffb36b', '火', 'flicker', 'pray'),
    (['结环', '铭环', '环印'], 'ring', '结环', '#e6ecff', '环', 'spin', 'calc'),
    (['誓', '立誓'], 'seal', '立誓', '#f2d08a', '誓', 'glow', 'oath'),
    (['血誓'], 'blood', '血誓', '#d8344a', '誓', 'beat', 'oath'),
    (['高座之火', '魔神之火', '借火'], 'fire', '借火', '#ff6a3d', '火', 'beat', 'oath'),
    (['古龙祷告', '龙语'], 'drake', '龙祷', '#ffc86b', '龙', 'glow', 'pray'),
    (['龙息', '吐息', '真龙', '龙裔', '龙血'], 'drake', '吐息', '#ff9a4a', '龙', 'pulse', 'body'),
    (['铳'], 'gun', '点铳', '#ffd28a', '铳', 'tense', 'calc'),
    (['晶匣'], 'lattice', '换匣', '#9fe0ff', '匣', 'spin', 'calc'),
    (['灰帷'], 'mirror', '落帷', '#c8c4d0', '帷', 'flicker', 'shadow'),
    (['缄火', '圣钉'], 'seal', '落钉', '#fff0d0', '钉', 'glow', 'oath'),
    (['残火'], 'fire', '引火', '#ff7a45', '火', 'flicker', 'oath'),
    # 二十三条命路（纷争纪1104年以后、山铜纪、迷宫纪）。叫法照各条的认法：摧锋重心压在前脚蓄一两息，真理先分类再动手，天平押上钱再宣布规矩，铁律念契约条款
    (['摧锋'], 'shock', '蓄势', '#ff8a3d', '破', 'pulse', 'body'),
    (['沸血'], 'blood', '烧血', '#e0344a', '血', 'beat', 'body'),
    (['熔心'], 'forgeheart', '点炉', '#ff6a2a', '熔', 'spin', 'body'),
    (['洪流'], 'circle', '咏唱', '#7fb8ff', '流', 'spin', 'verse'),
    (['真理'], 'lattice', '演算', '#7fd0ff', '理', 'spin', 'calc'),
    (['极光'], 'burst', '聚辉', '#ffe08a', '辉', 'pulse', 'body'),
    (['悲悯', '慈悯'], 'halo', '祷告', '#ffe9a8', '悯', 'glow', 'pray'),
    (['断罪'], 'verdict', '宣判', '#fff0c0', '罪', 'glow', 'oath'),
    (['无形'], 'eye', '布局', '#9a8cff', '隐', 'flicker', 'shadow'),
    (['绝影'], 'slash', '屏息', '#b08cff', '影', 'flicker', 'shadow'),
    (['诡刃'], 'mirror', '织幻', '#d48cff', '幻', 'flicker', 'shadow'),
    (['惊弦'], 'reticle', '引弦', '#9fe0ff', '弦', 'tense', 'body'),
    (['行猎'], 'track', '循迹', '#8fd07a', '猎', 'tense', 'body'),
    (['魔梭'], 'arrow', '附矢', '#c08cff', '梭', 'tense', 'calc'),
    (['渊垒'], 'shield', '立盾', '#9fb8d8', '垒', 'glow', 'body'),
    (['死舞'], 'dance', '踏拍', '#ff7aa0', '舞', 'spin', 'body'),
    (['阵剑'], 'runeblade', '点纹', '#7fd8ff', '阵', 'glow', 'calc'),
    (['天平'], 'scales', '押注', '#ffd36e', '衡', 'swing', 'oath'),
    (['鼎镬'], 'cauldron', '下锅', '#ffb070', '鼎', 'beat', 'feast'),
    (['千锤'], 'anvil', '落锤', '#ff9a4a', '锤', 'swing', 'body'),
    (['枯荣'], 'flask', '调药', '#9fe08a', '荣', 'beat', 'feast'),
    (['铁律'], 'chain', '援引', '#d0d8e8', '律', 'glow', 'oath'),
    (['解构'], 'compass', '测绘', '#8fe0d0', '解', 'spin', 'calc'),
]

# 元素压过路子的颜色：写在「·」后头的那一段（路·元素）
ELEM = [('火|炎|焰|灼|熔', '#ff7a45'), ('水|潮|浪|海', '#3fa9f5'), ('冰|霜|雪|寒', '#8fd8ff'), ('雷|电|霆', '#c08cff'), ('土|岩|石|地|砂', '#d2a86e'),
        ('风|岚|气', '#6fe0b8'), ('草|木|叶|藤|生|花', '#7dcf6a'), ('光|圣|辉|晨|曦|日', '#ffe08a'), ('暗|影|夜|冥|蚀', '#a58cff'),
        ('治|愈|疗|医', '#7ef0c6'), ('神', '#ffd36e'), ('混沌|虚空|虚', '#ff5fa8'), ('血', '#e0344a')]
# 月银纪的七曜：赤火、橙冰、黄岩、绿草、青风、蓝水、紫雷（写在哪里都认）
SEVEN = [('赤火|·赤', '#ff5a3d'), ('橙冰|·橙', '#ffa14a'), ('黄岩|·黄', '#ffd257'), ('绿草|·绿', '#7dd36a'), ('青风|·青', '#4fd1c5'), ('蓝水|·蓝', '#4f8cff'), ('紫雷|·紫', '#b07cff')]

ANIM = {
    'spin': 'sz-rt-spin 16s linear infinite',
    'pulse': 'sz-rt-pulse 1.8s ease-in-out infinite',
    'beat': 'sz-rt-beat2 1.1s ease-in-out infinite',
    'glow': 'sz-rt-glow 2.6s ease-in-out infinite',
    'flicker': 'sz-rt-flick 3.2s steps(1) infinite',
    'tense': 'sz-rt-tense 1.6s ease-in-out infinite',
    'swing': 'sz-rt-swing 2.2s ease-in-out infinite',
}
KEYFRAMES = '''@keyframes sz-rt-spin{to{transform:rotate(360deg)}}
@keyframes sz-rt-pulse{0%,100%{transform:scale(.92);opacity:.85}50%{transform:scale(1.06);opacity:1}}
@keyframes sz-rt-beat2{0%,100%{transform:scale(.95)}20%{transform:scale(1.08)}40%{transform:scale(.98)}}
@keyframes sz-rt-glow{0%,100%{filter:drop-shadow(0 0 4px var(--rc))}50%{filter:drop-shadow(0 0 14px var(--rc))}}
@keyframes sz-rt-flick{0%,100%{opacity:1}40%{opacity:.35}43%{opacity:1}70%{opacity:.6}73%{opacity:1}}
@keyframes sz-rt-tense{0%,100%{transform:scaleX(1)}50%{transform:scaleX(.9)}}
@keyframes sz-rt-swing{0%,100%{transform:rotate(-6deg)}50%{transform:rotate(6deg)}}
@keyframes sz-rt-in{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
@keyframes sz-rt-wipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes sz-rt-beat{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}
@keyframes sz-rt-flare{0%{opacity:0;text-shadow:0 0 0 transparent}55%{opacity:1;text-shadow:0 0 22px var(--rc), 0 0 6px var(--rc)}100%{opacity:1}}
@keyframes sz-rt-slam{0%{opacity:0;transform:scale(1.45);filter:blur(3px)}60%{opacity:1;transform:scale(.97);filter:none}100%{opacity:1;transform:none}}
@keyframes sz-rt-ghost{0%{opacity:0;text-shadow:-16px 0 color-mix(in srgb, var(--rc) 50%, transparent), 16px 0 color-mix(in srgb, var(--rc) 50%, transparent)}40%{opacity:1}100%{opacity:1;text-shadow:-2px 0 color-mix(in srgb, var(--rc) 22%, transparent), 2px 0 color-mix(in srgb, var(--rc) 22%, transparent)}}
@keyframes sz-rt-stamp{0%{opacity:0;transform:scale(2.3) rotate(-28deg)}70%{opacity:1;transform:scale(.92) rotate(-6deg)}100%{opacity:1;transform:rotate(-8deg)}}
@keyframes sz-rt-sweep{from{background-position:100% 0;opacity:1}to{background-position:0 0;opacity:0}}
@keyframes sz-rt-scan{0%{opacity:0}30%{opacity:1}100%{opacity:.32}}
@keyframes sz-rt-breathe{0%,100%{opacity:.5}50%{opacity:1}}
@keyframes sz-rt-steam{0%{transform:translateY(8px);opacity:0}30%{opacity:1}100%{transform:translateY(-34px);opacity:0}}'''

# ---- 五纪的材质：(底, 框线, 字, 名字, 小字, 横幅的底, 另加的几条)。认不出纪元的照迷宫纪 ----
ERA = {
    'maze': ('linear-gradient(160deg, color-mix(in srgb, var(--rc) 16%, #121232), #0b0b1e 70%)', '#d6b26a', '#efe6d0', '#fff7e6', '#cfc3a6', None, ''),
    'pre': ('repeating-linear-gradient(115deg, rgb(60 40 20 / .07) 0 1px, transparent 1px 5px), linear-gradient(180deg, #f1e6c9, #e2d2ab)', '#5b3a1e', '#2e2012', '#1e1408', '#6b4a2a',
            'repeating-linear-gradient(115deg, rgb(60 40 20 / .07) 0 1px, transparent 1px 5px), linear-gradient(100deg, #f3e8cc, #e0cfa6)',
            '.sz-rite .rt-c{background:#3b2614!important;filter:none!important}.sz-rite .rt-n{text-shadow:none!important}.sz-rite .rt-bd{animation:none}'
            '.sz-waza .wz-n{color:#1e1408!important;text-shadow:none}.sz-waza .wz-who{color:#6b4a2a}.sz-waza .wz-d{color:#3b2a18}.sz-waza .wz-k{color:#7a3b1e}.sz-waza::before{color:#8e2a1a;text-shadow:none;opacity:.3}'),
    'bronze': ('linear-gradient(90deg, #e9e4d8 0 84px, #c9c2b2 84px 86px, #141218 86px), linear-gradient(180deg, #1a171f, #0e0c12)', '#d8b45a', '#ece4d2', '#fff6e0', '#b8ac8e',
               'linear-gradient(90deg, #e9e4d8 0 62px, #c9c2b2 62px 64px, transparent 64px), linear-gradient(100deg, color-mix(in srgb, var(--wc) 24%, #161319) 0, #0e0c12 70%)',
               '.sz-rite .rt-bd{animation:none}.sz-rite .rt-c{background:#2a241c!important;filter:drop-shadow(0 1px 0 rgb(255 255 255 / .5))!important}'
               '.sz-rite .rt-n{text-shadow:0 1px 0 rgb(255 255 255 / .14), 0 -1px 0 rgb(0 0 0 / .7), 0 0 12px color-mix(in srgb, var(--rc) 45%, transparent)!important}'
               '.sz-waza::before{color:#3a3328;text-shadow:none;opacity:.75}'),
    'strife': ('radial-gradient(circle at 10px 10px, rgb(255 255 255 / .18) 0 2px, transparent 2.5px) 0 0/calc(100% - 4px) calc(100% - 4px), linear-gradient(90deg, #6e1414 0 8px, transparent 8px), linear-gradient(160deg, #2a2a30, #141418 70%)',
               '#9aa0aa', '#e6e2da', '#ffffff', '#b8b2a8',
               'radial-gradient(circle at 8px 8px, rgb(255 255 255 / .16) 0 1.6px, transparent 2px) 0 0/calc(100% - 4px) 100%, linear-gradient(90deg, #6e1414 0 6px, transparent 6px), linear-gradient(100deg, color-mix(in srgb, var(--wc) 26%, #26262c) 0, #18181c 65%)',
               '.sz-rite .rt-n{width:fit-content;padding-bottom:3px;box-shadow:inset 0 -2px 0 #8e1b1b}'),
    'moon': ('radial-gradient(1px 1px at 20% 30%, rgb(255 255 255 / .7), transparent), radial-gradient(1px 1px at 70% 60%, rgb(255 255 255 / .5), transparent), radial-gradient(1px 1px at 45% 85%, rgb(255 255 255 / .6), transparent), linear-gradient(160deg, #3a4456, #1c2230 75%)',
             '#c8d2e0', '#e8ecf2', '#ffffff', '#aab6c8',
             'radial-gradient(1px 1px at 30% 40%, rgb(255 255 255 / .6), transparent), radial-gradient(1px 1px at 76% 70%, rgb(255 255 255 / .5), transparent), linear-gradient(100deg, color-mix(in srgb, var(--wc) 30%, #2b3446) 0, #1f2533 60%, #161b26)',
             '.sz-rite .rt-c{background:color-mix(in srgb, var(--rc) 52%, #eef4ff)!important}.sz-rite .rt-n{letter-spacing:.24em}'),
}
MAZE_BG = ERA['maze'][0]
XI = [('一', 1), ('两', 2), ('二', 2), ('三', 3), ('四', 4), ('五', 5), ('六', 6), ('七', 7), ('八', 8), ('九', 9)]


def bundle(fam):
    d = dict(DEFAULT)
    d.update(FAM[fam])
    if d['--rl-sep'] is None:
        d['--rl-sep'] = d['--rl-pre']
    return ';'.join('%s:%s' % kv for kv in d.items())


def css():
    out = ['/* ==== 11-10 超凡演出（rite_css.py）：起手框和横幅，路子换纹样、叫法和演法，纪元换材质 ==== */', KEYFRAMES]
    w = out.append
    # 框
    w(R + r''' .sz-rite{--rc:#e9cf8a;--rm:''' + RS.MOTIF['circle'] + ';--rca:' + ANIM['spin'] + ';--rlab:" · 起手";' + bundle('verse') + r''';--qc:var(--rl, #d6b26a);position:relative;isolation:isolate;display:block;max-width:560px;margin:16px auto;padding:16px 22px 14px 108px;border-radius:12px;overflow:hidden;counter-reset:rt;background:var(--rb, ''' + MAZE_BG + r''');box-shadow:inset 0 0 0 1px var(--qline, color-mix(in srgb, var(--rl, #d6b26a) 70%, transparent)), inset 0 0 0 4px rgb(0 0 0 / .12), var(--qdbl, 0 0 0 transparent), 0 10px 26px rgb(0 0 0 / .35), var(--qglow, 0 0 0 transparent);color:var(--rt, #efe6d0);animation:sz-rt-enter .55s cubic-bezier(.2,.9,.3,1) both}
''' + R + r''' .rt-bd{position:absolute;left:12px;top:50%;z-index:0;width:84px;height:84px;margin-top:-42px;background:var(--rbd, ''' + RS.BACK['maze'] + r''') center/contain no-repeat;pointer-events:none;animation:sz-rt-spin 90s linear infinite}
''' + R + r''' .rt-c{position:absolute;left:16px;top:50%;z-index:1;width:76px;height:76px;margin-top:-38px;background:color-mix(in srgb, var(--rc) 85%, #fff);-webkit-mask:var(--rm) center/contain no-repeat;mask:var(--rm) center/contain no-repeat;filter:drop-shadow(0 0 8px var(--rc));animation:sz-rt-spinin 1s cubic-bezier(.2,.8,.2,1) both, var(--rca) 1s}
''' + R + r''' .rt-fx{position:absolute;inset:0;z-index:0;pointer-events:none;background:var(--fx-b);animation:var(--fx-a)}
''' + R + r''' :is(.rt-who,.rt-l,.rt-n){position:relative;z-index:1}
''' + R + r''' .rt-who{display:block;font-size:11px;letter-spacing:.18em;color:color-mix(in srgb, var(--rc) 55%, var(--rs, #cfc3a6))}
''' + R + r''' .rt-who::after{content:var(--rlab)}
''' + R + r''' .rt-l{display:var(--rl-d);margin-top:4px;font-family:var(--fm-serif);font-size:14px;font-style:var(--rl-s);font-weight:var(--rl-w);line-height:1.7;color:var(--rt, #efe6d0);animation:var(--rl-a)}
''' + R + r''' .rt-l:empty{display:none}
''' + R + r''' .rt-l:not(:empty){counter-increment:rt}
''' + R + r''' .rt-l:not(:empty)::before{content:var(--rl-pre)}
''' + R + r''' .rt-l:not(:empty)::after{content:var(--rl-post)}
''' + R + r''' .rt-l:not(:empty)+.rt-l:not(:empty)::before{content:var(--rl-sep);margin-right:var(--rl-sm)}
''' + R + r''' .rt-l:not(:empty)+.rt-l:not(:empty){margin-left:var(--rl-gap)}
''' + R + r''' .sz-rite .rt-l:nth-of-type(2){animation-delay:.3s}
''' + R + r''' .sz-rite .rt-l:nth-of-type(3){animation-delay:calc(.3s + var(--rl-st))}
''' + R + r''' .sz-rite .rt-l:nth-of-type(4){animation-delay:calc(.3s + var(--rl-st) * 2)}
''' + R + r''' .sz-rite .rt-l:nth-of-type(5){animation-delay:calc(.3s + var(--rl-st) * 3)}
''' + R + r''' .rt-n{display:block;margin-top:8px;font-family:var(--fm-serif);font-size:19px!important;font-weight:800!important;letter-spacing:.16em;transform-origin:left center;color:var(--rh, #fff7e6)!important;text-shadow:0 0 12px color-mix(in srgb, var(--rc) 70%, transparent);animation:var(--rn-a)}
''' + R + r''' .rt-n::after{content:var(--rn-x);display:inline-block;width:30px;height:30px;margin-left:12px;vertical-align:-6px;background:#b3261e;-webkit-mask:''' + RS.MOTIF['oathseal'] + r''' center/contain no-repeat;mask:''' + RS.MOTIF['oathseal'] + r''' center/contain no-repeat;animation:sz-rt-stamp .4s cubic-bezier(.2,1.6,.4,1) 1.15s both}
''' + R + r''' .sz-rite[data-xi] .rt-n::after{content:"";width:calc(var(--xi, 2) * 13px);height:10px;margin-left:14px;vertical-align:2px;background:radial-gradient(circle, var(--rc) 0 3.4px, transparent 4px) 0 50%/13px 10px repeat-x;-webkit-mask:none;mask:none;animation:sz-rt-wipe calc(var(--xi, 2) * .22s) steps(var(--xi, 2)) .5s both}''')
    w(R + ' .sz-rite:not([data-xi]) .rt-n::after{transform:rotate(-8deg)}')
    for word, n in XI:
        w('%s .sz-rite[data-xi="%s"]{--xi:%d}' % (R, word, n))
    # 路子
    for keys, motif, label, col, kj, anim, fam in KINDS:
        sel = ','.join('[data-k*="%s"]' % k for k in keys)
        w('%s .sz-rite:is(%s){--rc:%s;--rm:%s;--rca:%s;--rlab:" · %s";%s}' % (R, sel, col, RS.MOTIF[motif], ANIM[anim], label, bundle(fam)))
        w('%s .sz-waza:is(%s){--wc:%s;--kj:"%s"}' % (R, sel, col, kj))
    for keys, col in ELEM:   # 旧写法 §咏唱 那一栏只写元素（data-k 就是一个字），也认
        sel = ','.join('[data-k*="·%s"],[data-k="%s"]' % (k, k) for k in keys.split('|'))
        w('%s :is(.sz-rite,.sz-waza):is(%s){--rc:%s;--wc:%s}' % (R, sel, col, col))
    for keys, col in SEVEN:
        sel = ','.join('[data-k*="%s"]' % k for k in keys.split('|'))
        w('%s :is(.sz-rite,.sz-waza):is(%s){--rc:%s;--wc:%s}' % (R, sel, col, col))
    # 手机、减少动画
    w('@media (max-width:639px){' + R + ' .sz-rite{padding:14px 16px 12px 86px}' + R + ' :is(.rt-c,.rt-bd){left:10px;width:62px;height:62px;margin-top:-31px}}')
    w('@media (prefers-reduced-motion:reduce){' + R + ' :is(.rt-c,.rt-bd,.rt-fx,.rt-l,.rt-n){animation:none!important}' + R + ' .rt-n::after{animation:none!important}}')
    # 纪元
    for era, (bg, line, txt, head, small, wbg, extra) in ERA.items():
        sel = ERA_SEL[era]
        w('%s{--rb:%s;--rl:%s;--rt:%s;--rh:%s;--rs:%s;--rbd:%s}' % (sel, bg, line, txt, head, small, RS.BACK[era]))
        if wbg:
            w('%s .sz-waza{background:%s}' % (sel, wbg))
        if extra:
            w(''.join('%s %s}' % (sel, x) for x in extra.split('}') if x.strip()))
    # 手机上山铜纪那一道白石窄一点，不压字（排在纪元那几条后头才盖得住）
    w('@media (max-width:639px){'
      + ERA_SEL['bronze'] + '{--rb:linear-gradient(90deg, #e9e4d8 0 74px, #c9c2b2 74px 76px, #141218 76px), linear-gradient(180deg, #1a171f, #0e0c12)}'
      + ERA_SEL['bronze'] + ' .sz-waza{padding-left:66px;background:linear-gradient(90deg, #e9e4d8 0 52px, #c9c2b2 52px 54px, transparent 54px), linear-gradient(100deg, color-mix(in srgb, var(--wc) 24%, #161319) 0, #0e0c12 70%)}'
      + ERA_SEL['bronze'] + ' .sz-waza::before{left:6px}}')
    # 类和稀有度（rite_tier.py）：Skill、Art 收着演，Active、Special 放开演；Epic、Legend、Unique 一档比一档华丽
    import rite_tier as RT
    w(RT.css())
    return '\n'.join(out)


if __name__ == '__main__':
    print(len(css()))
