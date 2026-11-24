#!/usr/bin/env python3
# 大图书馆书里的插图（11-24）：书稿里独占一行的〔图一：……〕〔木刻一：……〕〔钱：……〕〔纸环一：……〕这些，一张一张出成图。
# 画法分五种（A 兵书图谱、B 铜版图版、C 抄本彩绘、D 通俗木版、E 手记与拓印），哪本书归哪一种、每本自己的纸和笔照它“装帧”那一行，
# 细目写在 ../插图/画法.md。编号照 共用/build_lib.py 打出来的数据：一本书里的图版照出现的先后从 1 编起（971 三册连着编），
# 跟页面上认的是同一套，图名 <书键>_<n>。
# 走本机 Codex（跟 gen_lib.py 同一套），用 ComfyUI 自带的 python 跑：
#   <py> -X utf8 gen_plates.py list                 读 共用/data/lib/ 写 ../插图/清单.json、清单.md（先跑 build_lib.py）
#   <py> -X utf8 gen_plates.py gen [id…|书键…|sample|all]   出图（已有的不重出），先用 ~/.codex_b，撞了额度换 ~/.codex，两个都撞了就停
#   <py> -X utf8 gen_plates.py cut [id…|sample|all]  转 webp（装进 1000×1200，质量 72），写 共用/assets/lib/plates/<id>.webp
#   <py> -X utf8 gen_plates.py sheet [id…|sample]    拼总览图 ../插图/截图/样张总览.jpg
#   <py> -X utf8 gen_plates.py show <id>             打印这一张的提示词和参考图
# 原图在 底稿/状态栏/comfy/out/大图书馆插图/（不进库）。要整张重画：把那一张的 png 挪进 旧/ 再 gen（用户定的：有错整张重出，不拿原图改一处）。
# 改了书稿：重跑 build_lib.py，再跑 list。编号是照先后编的，书里中间插了一张，后面的号都会挪，挪之前先把 plates/ 里那本书的图对一遍。
import json
import os
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
sys.path.insert(0, COMFY)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
DATA = os.path.join(ROOT, '底稿', '门面', '共用', 'data', 'lib')
PLATES = os.path.join(ROOT, '底稿', '门面', '共用', 'assets', 'lib', 'plates')
OUT = os.path.join(COMFY, 'out', '大图书馆插图')
DOC = os.path.normpath(os.path.join(HERE, '..', '插图'))
SHOT = os.path.join(DOC, '截图')
HOMES = ['C:/Users/waitl/.codex_b', 'C:/Users/waitl/.codex']

# ---------- 五种画法 ----------
STYLES = {
    'A': dict(
        name='兵书图谱',
        look='Royal Armouries Ms. I.33, Hans Talhoffer\'s fight books, Joachim Meyer\'s 1570 fencing book (woodcuts by Tobias Stimmer), Fabian von Auerswald\'s wrestling book, Girard Thibault\'s Academy of the Sword',
        text=('A plate from an old manual of fighting, fencing or wrestling. Drawn like the plates of {look}: clear outline drawing, '
              'figures shown full length in readable stances with correct, sturdy human anatomy and weight on the feet, the weapons and hands placed exactly, '
              'a plain ground line or simple floor, little or no background, generous blank margin around the picture, a thin ruled border line. '
              'Faces are simple and plain, drawn the way old manuals draw them, not anime faces.'),
        ar='3:4 portrait'),
    'B': dict(
        name='铜版图版',
        look='the plates of Diderot\'s Encyclopédie, the woodcuts of Agricola\'s De re metallica, Conrad Gesner\'s Historia animalium, Robert Hooke\'s Micrographia, Vesalius\'s Fabrica, early engraved Euclid diagrams and old nautical charts',
        text=('A plate from an old scholarly, natural-history or engineering book. Drawn like {look}: precise engraved line work with fine hatching and cross-hatching, '
              'black ink on pale paper, objects shown clearly and soberly, cutaways and sections where the caption asks for them, '
              'a measured, diagrammatic composition with generous blank margin and a thin ruled border. '
              'Where the caption mentions labels, numbers, scale bars or notes, draw them only as tiny leader lines ending in small blank tags or dots: no legible letters or digits. '
              'Any people are small, plain and anatomically correct.'),
        ar='4:3 landscape'),
    'C': dict(
        name='抄本彩绘',
        look='the Très Riches Heures du duc de Berry by the Limbourg brothers and the Aberdeen Bestiary',
        text=('A painted miniature from a medieval-style illuminated manuscript. Painted like {look}: flat tempera colours, deep ultramarine, vermilion and leaf green, '
              'burnished gold leaf for skies, haloes of fire and borders, fine dark outlines, gracefully stylised figures in a stacked, tilted landscape, '
              'small careful details, a framed miniature on a pale parchment page with a narrow painted border of thin vines. '
              'Figures have natural proportions and plain small faces in the manuscript manner, not anime faces.'),
        ar='3:4 portrait'),
    'D': dict(
        name='通俗木版',
        look='Comenius\'s Orbis Pictus, the colour toy books of Walter Crane and Randolph Caldecott printed by Edmund Evans, and English chapbook woodcuts',
        text=('A picture from a cheap, much-loved popular picture book. Printed like {look}: bold simple black woodblock lines, chunky readable shapes, '
              'a few flat block colours laid on slightly off register, warm and plain, easy for a child to read at a glance, '
              'the picture filling a simple ruled frame on thick paper. Figures are simple and sweet with dot eyes, never scary unless the caption says so, '
              'every body with exactly two arms and two legs unless the caption says otherwise.'),
        ar='4:3 landscape'),
    'E': dict(
        name='手记与拓印',
        look='the sketchbook of Villard de Honnecourt, the notebooks of Leonardo da Vinci and Delacroix\'s travel sketchbooks; rubbings and scratched drawings where the book says so',
        text=('A drawing made by hand directly on a page of a working notebook, diary, register or letter. Drawn like {look}: '
              'quick, loose but observant lines, unfinished edges, smudges, pressure marks and corrections left in, the drawing sitting on the page with plain paper around it. '
              'It looks made by one person with the tools named below, not printed. Where the caption mentions writing or notes beside the drawing, '
              'show only a few faint grey strokes that do not form any letters. Figures have correct anatomy; faces are a few strokes, not anime faces.'),
        ar='4:3 landscape'),
}

# ---------- 每本书：画法、这本书自己的纸和笔（照“装帧”那一行） ----------
BOOKS = {
    # 命路厅
    'ming-zddyslbcxqstgm': ('A', 'black woodcut printed on thick white academy paper; scenes are set in a knights\' training yard'),
    'ming-mldll': ('E', 'neat small ink drawing by a records clerk on calculation scrap paper, a faint printed grid showing through from the back'),
    'ming-bwzsj': ('E', 'charcoal on rough grey war-report paper; plates that are rubbings of carved stone are white carved marks on a black ink-rubbed ground'),
    'ming-qjsst': ('A', 'black line woodcut printed in a big academy textbook'),
    'ming-jsyxs': ('A', 'pen-and-ink outlines on calfskin vellum, only the clothes and the small round shields washed with a thin ochre, exactly the manner of Ms. I.33'),
    'ming-jdtp': ('A', 'pen drawing washed with watercolour on parchment, as in Talhoffer, the shields painted with their emblems in colour'),
    'ming-bhbf': ('A', 'very precise ink line drawing on thick paper, circles drawn with compasses and lines with a ruler, as in Thibault'),
    'ming-clbz': ('B', 'ink on official ruled paper, bluish black ink; a clumsy little doodle where the caption says so'),
    'ming-wlth': ('A', 'mineral pigments (ochre, azure, vermilion, a touch of silver) painted on thick ledger paper, like the Codex Wallerstein'),
    'ming-jd': ('A', 'lines sketched in charcoal and then burned into thick ash-grey paper with a red-hot iron stylus: dark brown scorched lines, no colour'),
    # 神与魔神厅
    'shen-spxyyj': ('C', 'painted on a long narrow deerskin scroll in pale glowing silver ink with a little ochre and soot black'),
    'shen-gzdh': ('E', 'a child\'s clumsy, careful ink drawing on coarse grey-yellow ash paper, lines a little crooked'),
    # 月银纪廊
    'moon-qxsp': ('C', 'a bestiary miniature painted on tanned sheepskin ONLY in pale glowing silver-white ink, a little ochre and soot black: no ultramarine, no red, no gold leaf, no painted vine border; the beasts are wild animals, never in harness or saddle-cloths unless the caption says so'),
    'moon-wzk': ('E', 'charcoal drawing on white chronicle paper, with a few tiny size marks in red ink'),
    'moon-dszxqg': ('E', 'heavy charcoal lines on parchment by someone who has only just learned to draw'),
    'moon-dszxwc': ('E', 'ink on parchment, the ink gone greyish from freezing'),
    'moon-dszxgh': ('C', 'pale glowing silver ink on parchment, a sea horizon line along the foot of the page'),
    'moon-dszxfy': ('C', 'silver ink on parchment, copied from figures once scratched into clay tablets, the lines stiff and simple'),
    'moon-dszxxy': ('C', 'ink and a little gold on white sun-temple sheepskin'),
    'moon-zgz': ('B', 'pen drawing on reed paper; coins are drawn true to size, front and back side by side, like a numismatic plate'),
    'moon-bqdrl': ('E', 'ink on rough straw paper'),
    'moon-htysy': ('B', 'precise diagram in ink on thick white tower-journal paper'),
    'moon-xslzl': ('E', 'ink on coarse linen paper'),
    'moon-qtgq': ('C', 'pale glowing silver ink on tanned deerskin'),
    # 纷争纪廊
    'strife-wjzg': ('E', 'charcoal stick on reed paper, a few edges of the paper scorched'),
    'strife-yysj': ('E', 'charcoal and ochre on odd scraps (birch bark, bandage cloth, old ledger backs)'),
    'strife-fb': ('E', 'charcoal on the back of a reward poster, some strokes burned through the paper'),
    'strife-ds': ('E', 'soot-and-lamp-black ink on the rough side of a strip of old tent hide'),
    'strife-dbdy': ('E', 'charcoal on a narrow hide prayer scroll'),
    'strife-xqsqr': ('E', 'heavy charcoal pressed deep into the back of war-report paper'),
    'strife-bxdt': ('E', 'charcoal and ink on reed paper'),
    'strife-qsdg': ('E', 'charcoal on reed paper'),
    'strife-md': ('E', 'rubbings taken from a carved stone gatepost (white carved strokes on black) and plain, square, chisel-like ink drawing'),
    # 山铜纪廊
    'bronze-ycqc': ('E', 'grey ink on grey court paper; rubbings are white on black'),
    'bronze-jh': ('E', 'lines chiselled into a thin black steel plate and filled with pale volcanic ash, so the picture is pale grey lines on black metal'),
    'bronze-hyqyy': ('E', 'fine drawing in faded brown rose-ink on delicate rose-petal paper'),
    'bronze-wd': ('B', 'cold blue-black ink on thick archive paper, ruled lines pressed with a bone tally'),
    'bronze-ht': ('B', 'a chart drawn with a feather quill in deep teal ink on old sailcloth canvas, lines only'),
    'bronze-jbhl': ('E', 'pencil and ink in a farm grain ledger, big plain strokes'),
    'bronze-hq': ('E', 'ink sketches in a guild register'),
    'bronze-ny': ('E', 'a child\'s careful, never-joined ink drawing in a small purple cloth notebook'),
    'bronze-bzfszf': ('E', 'simple instructive ink drawings copied by a nurse into a small notebook, a little flour and candle wax on the page'),
    # 迷宫纪廊
    'maze-jxcdz': ('B', 'a surveyor\'s drawing traced in fine bright crystal-pen lines on oiled paper'),
    'maze-cxjdl': ('E', 'an appraiser\'s neat little pen sketches on cut tag paper'),
    'maze-dsqcsl': ('E', 'charcoal on the back of guild commission slips'),
    'maze-fbsdl': ('E', 'big charcoal lines leaning to the upper right, as if drawn in the wind, on the back of freight slips'),
    'maze-xsyyy': ('E', 'pencil sketch in a little snack-cart account book'),
    'maze-wxsl': ('E', 'pen sketch in black, blue and red ink on a merchant\'s ruled account paper'),
    'maze-cwdxx': ('B', 'an exploded diagram in ink, the kind folded small and opening wider than a desk'),
    'maze-yf': ('E', 'ink sketch in a navy logbook printed with a faint compass rose'),
    'maze-cyyd': ('E', 'charcoal and pencil, crooked, drawn on the back of a guild slip in a sickroom'),
    'maze-nbysm': ('E', 'ink on the back of a white-edged commission slip'),
    # 奥法与工程厅
    'arcane-lpyjb': ('B', 'clean ink line technical drawing on thick drafting paper, oil fingerprints at the corner'),
    'arcane-xhk': ('B', 'ink on fine-gridded table paper'),
    'arcane-afxhyx': ('B', 'ink line drawing in a range logbook; some figures are soot prints'),
    'arcane-gl': ('B', 'hard, clean steel engraving'),
    'arcane-dqtpbw': ('E', 'quick pen scribble on a note slipped under a door, beside typewritten lines'),
    'arcane-bhzts': ('B', 'diagram in moon-silver ink on mountain-goat parchment; paper wheels (volvelles) are drawn as round cut-paper discs with a bone pin through the middle'),
    'arcane-lfs': ('B', 'small dense pen drawing on parchment, stones drawn in the margins'),
    'arcane-jgxdl': ('B', 'anatomical dissection plate, ink on damp grey-blue paper, like Vesalius'),
    'arcane-wd': ('E', 'pen drawing on the back of a gilt-edged party invitation, hands doodled in the margin'),
    'arcane-tsdgl': ('B', 'a workshop blueprint in ink, smoke-browned, with oily fingerprints at the edges'),
    'arcane-lcxzl': ('E', 'pen drawing on narrow ruled table paper'),
    'arcane-hs': ('B', 'ink section drawing on thick hide paper'),
    'arcane-sf': ('B', 'black woodcut cut by old miners, exactly in the manner of De re metallica'),
    'arcane-cxj': ('B', 'charcoal and fine stylus drawing in a parts ledger, oil-stained'),
    'arcane-xt': ('B', 'copperplate engraving, very fine and exact, like Micrographia'),
    'arcane-cfjyjq': ('B', 'ink drawing on thick banking ledger paper, like the plates of Babbage\'s engine'),
    'arcane-yzxdtdll': ('B', 'printed line illustration on grey-blue paper'),
    'arcane-ytdl': ('B', 'ink section drawings in a printed academy treatise'),
    'arcane-mjx': ('B', 'ink drawing on thick paper, crystal facets drawn precisely, no colour'),
    'arcane-wytj': ('B', 'copperplate plate exactly like the Encyclopédie plates'),
    # 星冠圣堂厅
    'crown-xgsds': ('C', 'tiny calendar miniature on calfskin: white-stone ground, ultramarine, gold leaf burnished'),
    'crown-xgwd': ('D', 'small black catechism woodcut on coarse paper, no colour'),
    'crown-dzyzb': ('E', 'ink and silver smudges on deerskin, crowded margins'),
    'crown-lhztj': ('B', 'a cross-section drawing in ink in a bell-tower register'),
    'crown-qdxw': ('B', 'a specimen drawn true to size, as in a collector\'s plate'),
    'crown-wdxsx': ('D', 'a small cheap letterpress page with a faint printed candle image'),
    'crown-gldg': ('E', 'charcoal on scrap war-report paper in a soldier\'s pocket book'),
    # 行当的歌（只有一张图，余下是谱）
    'craft-lbdd': ('E', 'pencil in an oilcloth smithy account book, little burn holes from sparks'),
    # 孩子的一架
    'child-ktsww': ('D', 'NOT a colour print: a plain black woodcut on coarse hemp paper exactly in the manner of Orbis Pictus, which a child has later coloured in places with grey charcoal and red earth, going over the lines'),
    'child-fbsz': ('D', 'a little hornbook: a paper glued to a small wooden paddle under a thin clear sheet of horn held by brass strips'),
    'child-jkty': ('D', 'small simple pen pictures on ruled ledger paper, a few red pen dots'),
    'child-yqlyc': ('D', 'a small black woodcut at the head of a typewritten story'),
    'child-bygrxj': ('D', 'a big bold black woodcut on thick paper, a little frightening as the caption wants'),
    'child-xzdtyn': ('D', 'a small woodcut by a handy student printed on grey paper'),
    'child-yzmybcj': ('D', 'colour woodblock toy book in the manner of Walter Crane, one big picture per page'),
    'child-swdgs': ('D', 'woodblock print on yellowish paper (or crisp steel-plate print on white for the western half)'),
    'child-jtyczjgz': ('D', 'colour-printed board book: the floor lord is moss green, the princess orange-red, the hero only a tiny blue dot hidden somewhere'),
    # 戏台与说书
    'stage-wssy': ('B', 'a stage-design drawing like those of the Galli-Bibiena family, the stage set drawn in gold powder over a dark ground'),
    'stage-jdyh': ('E', 'ink on the back of a used commission slip'),
    'stage-mcahq': ('E', 'cold ink on archive paper'),
    'stage-bxqsc': ('D', 'a cheap chapbook woodcut, smudgy ink, comic and lively'),
}

# BOOKS 里没写的书（书稿往后新添的）：照厅给一种画法，纸和笔拿这本书“装帧”那一行原文
HALL_STYLE = {'yuan': 'B', 'ming': 'A', 'shen': 'C', 'moon': 'E', 'strife': 'E', 'bronze': 'E', 'maze': 'E', 'arcane': 'B', 'crown': 'C',
              'craft': 'E', 'child': 'D', 'stage': 'E'}


def book_style(it):
    if it['书'] in BOOKS:
        return BOOKS[it['书']]
    return (HALL_STYLE.get(it['厅'], 'E'), 'the paper, ink and binding described in the book (in Chinese): ' + it.get('装帧', ''))


# 不出图的：谱（是唱法和拍子，不是画），“往下六页”（一句话带过六页）
def skip_reason(it):
    if it['v'] == 'score':
        return '谱，是唱法的说明，不是画'
    if it['label'].startswith('往下'):
        return '一句话带过几页，不是一张图'
    return ''


# 世界里的东西（图里点到了才带）
GLOSS = [
    ('炎角', 'Flamehorn demon-kin are human-shaped people with two thick horns (curving forward, sometimes glowing at the tips) and skin from charcoal to deep red; not monsters.'),
    ('影魔', 'Shadow demon-kin are lean human-shaped people with pale grey skin; their shadow moves half a step late.'),
    ('夜魔', 'Night demon-kin are human-shaped people with slender horns that curve backward.'),
    ('蛇魔', 'Serpent demon-kin are human-shaped from the waist up with four arms.'),
    ('魔族', 'Demon-kin in this world look like humans with horns and tinted skin.'),
    ('白骸', 'A white-bone soldier: a figure whose white bones show through the skin.'),
    ('亚龙', 'A drake: a lesser dragon used as a mount, four legs and two wings.'),
    ('狮鹫', 'A griffin: eagle head and wings, lion body.'),
    ('半身人', 'Halflings are small cheerful folk about a metre tall.'),
    ('矮人', 'Dwarves are short, broad and bearded.'),
    ('精灵', 'Elves have long pointed ears.'),
    ('机兵', 'Clockwork war-golems: tall figures of riveted bronze and iron plates.'),
    ('铜人', 'The bronze men are clockwork war-golems of riveted bronze plates.'),
    ('霜象', 'A frost elephant: a huge wild shaggy mammoth-like beast with long frost-white hair and long curved tusks.'),
    ('铳', 'Guns here are magitech crystal-fed muskets, not modern rifles.'),
    ('熔铁炉心', 'The Ironmelt Heart is a dwarven forge-city carved into a volcano: stone halls, round arches, steep gabled stone houses with slate roofs, iron and brass.'),
    ('炉城', 'The forge-city is dwarven: stone halls, round arches, steep gabled stone houses with slate roofs.'),
]

COMMON = ('Hard rules. Everything is Western: European medieval to early-modern architecture, clothing and objects (gabled roofs, round or pointed arches, timber framing, stone keeps); '
          'nothing East Asian at all (no curved tiled roofs, no pagodas, no Chinese or Japanese clothing or script), even though the caption is written in Chinese. '
          'One picture only, filling the image as a page of the book seen straight on and flat (no table, no hands holding it, no book edges, no perspective). '
          'There is no moon and no crescent anywhere. No readable writing anywhere: no letters, no digits, no runes that look like writing, no signature, no watermark; '
          'anything the caption calls writing, a title, a label or a number is drawn only as faint strokes or blank tags. '
          'Every person has exactly two arms, two legs and five fingers on each hand unless the caption says otherwise, and hands hold things believably. '
          'Where the caption says a face is not drawn or not carved, leave that face blank. '
          'Draw everything the caption mentions, in the places it says, and add nothing that contradicts it.')

# 图版的名目自己带的话（上半幅、下半幅、纸环、钱）
def label_hint(it):
    l, v = it['label'], it['v']
    if l.startswith('上半幅'):
        return ('This picture is only the upper half of an Encyclopédie-style plate: the scene alone. '
                'Do NOT draw the row of tools or any lower band; the lower half is a separate picture. ')
    if l.startswith('下半幅'):
        return ('This picture is only the lower half of an Encyclopédie-style plate: the objects listed in the caption, each drawn alone, '
                'laid out in neat rows on blank paper in the order listed, each with a small blank tag instead of its number; no scene, no people unless listed. ')
    m = re.search(r'标着([一二三四五六七八九十两0-9]+)个数', it['原文'])
    if m:
        return ('The caption says the picture is marked with %s numbers: draw exactly that many small blank tags, each on a thin leader line pointing to one thing in the scene '
                '(as in Orbis Pictus); leave the tags empty. ' % m.group(1))
    if v == 'ring':
        return 'The plate is a paper volvelle: one or two round paper discs drawn flat, pinned at the centre with a bone pin, with the marks the caption describes. '
    if v == 'coin':
        return 'Draw the coin or coins true to size on blank paper, front and back side by side, like a numismatic plate; no lettering on the coins. '
    return ''


# 个别几张原文容易读岔的地方（主会话查图时添）
NOTES = {
    'child-ktsww_1': '苇棚 is a whole cluster of many (at least six) reed shacks crowded along the river bank, smoke rising from several roofs. The reed shacks are poor river-bank shacks of reeds, broken planks and old sailcloth on the edge of a Western fantasy city; the barefoot girl wears a plain, patched European peasant smock.',
    'arcane-wytj_1': '墙上挂着几样炸过的东西 means a few real objects on the wall that once burst or blew apart in the forge (cracked, split, blackened metal pieces), NOT exploded-view diagrams.',
}

# 样张：每种画法两张（id 照清单）
SAMPLES = []          # list 时照 SAMPLE_PICK 定下来
SAMPLE_PICK = {
    'A': [('ming-jd', 1), ('ming-qjsst', 1)],
    'B': [('arcane-wytj', 1), ('arcane-sf', 1)],
    'C': [('crown-xgsds', 1), ('moon-qxsp', 3)],
    'D': [('child-yzmybcj', 4), ('child-ktsww', 1)],
    'E': [('strife-yysj', 1), ('strife-xqsqr', 1)],
}


# ---------- 点了名的人 ----------
ERA_SETS = {'月银纪': ['月银纪史诗', '诸国期', '萨尔维斯', '神明'], '纷争纪': ['纷争纪', '神明'], '山铜纪': ['山铜纪', '神明'], '迷宫纪': ['前传', 'v3', '主角', '执政', '神明']}
STOP_NAMES = {'学生', '祭司', '首席', '勇者', '公主', '层主', '老人', '孩子', '骑士', '书记', '兔子', '老头', '女人', '殿主', '拿剑的', '琥珀'}
# 认出来了但不是画里的人（名字是别的词里的一截、只是写字的人、只是提到）：(id, 名)
NOT_DRAWN = {('arcane-gl_5', '希奥'), ('arcane-dqtpbw_8', '佐拉'), ('child-xzdtyn_5', '葛嘉')}


def cast_names():
    out = {}          # 名字 → [(套, 键)]
    base = os.path.join(COMFY, 'cast')
    for dp, dn, fn in os.walk(base):
        for f in fn:
            if not f.endswith('.json') or f == '覆盖.json':
                continue
            st = os.path.basename(dp) if dp != base else 'v3'
            try:
                d = json.load(open(os.path.join(dp, f), encoding='utf-8'))
            except Exception:
                continue
            if not isinstance(d, list):
                continue
            for x in d:
                nm, en = x.get('name', ''), x.get('en', '')
                if not nm or not en:
                    continue
                # 神的全名带神号（风之璐璐薇、战祸之耶万），书里多半只写名字：取最后一个之、的、者后头那一截
                for n in {nm, nm.split('·')[0], re.sub(r'[（(].*$', '', nm), re.split(r'[之的者]', nm)[-1] if st == '神明' else nm}:
                    n = n.strip()
                    if len(n) >= 2 and n not in STOP_NAMES:
                        out.setdefault(n, [])
                        if (st, en) not in out[n]:
                            out[n].append((st, en))
    return out


def por_dir(st, en):
    return os.path.join(COMFY, 'out', '立绘_' + st, en)


def era_of(year):
    for e in ERA_SETS:
        if e in year:
            return e
    return ''


def find_people(text, year, names, it_id=''):
    hits, seen = [], set()
    for n in sorted(names, key=len, reverse=True):
        if n in text and not any(n in s for s in seen) and (it_id, n) not in NOT_DRAWN:
            seen.add(n)
            cands = names[n]
            pref = ERA_SETS.get(era_of(year), [])
            cands = sorted(cands, key=lambda c: (pref.index(c[0]) if c[0] in pref else 99))
            st, en = cands[0]
            has = os.path.exists(os.path.join(por_dir(st, en), 'art.png'))
            h = {'名': n, '键': '%s:%s' % (st, en), '有立绘': has, '别的同名': ['%s:%s' % c for c in cands[1:4]]}
            # 神名后头跟着殿、系、的、顿号逗号的，是殿名、记号、一串名字里的一个，不是画里站着的神
            if st == '神明' and all(text[m.end():m.end() + 1] in '殿系的、，。' for m in re.finditer(re.escape(n), text)):
                h['只是提到'] = 1
            hits.append(h)
    return hits


# ---------- 清单 ----------
def strip(h):
    return re.sub(r'<[^>]+>', '', h).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')


def build_list():
    idx = json.load(open(os.path.join(DATA, 'index.json'), encoding='utf-8'))
    names = cast_names()
    items = []
    for h in idx['halls']:
        for b in h.get('books', []):
            bk = json.load(open(os.path.join(DATA, b['k'] + '.json'), encoding='utf-8'))
            for s in bk['secs']:
                for bl in s['b']:
                    if bl['k'] != 'fig':
                        continue
                    text = strip(bl['h'])
                    it = {'id': '%s_%d' % (b['k'], bl['n']), '书': b['k'], '书名': bk['t'], '文件': bk['src'], 'n': bl['n'],
                          'label': strip(bl['l']), 'v': bl['v'], '原文': text, '厅': h['k'], '厅名': h['n'],
                          '作者': bk.get('a', ''), '成书': bk.get('y', ''), '装帧': bk.get('z', ''), '剧透': bl.get('s', 0)}
                    it['人物'] = find_people(text, bk.get('y', ''), names, it['id'])
                    it['画法'] = book_style(it)[0]
                    if b['k'] not in BOOKS:
                        it['画法来源'] = '厅默认'
                    r = skip_reason(it)
                    if r:
                        it['不出图'] = r
                    items.append(it)
    return idx, items


def load_items():
    p = os.path.join(DOC, '清单.json')
    return json.load(open(p, encoding='utf-8'))['图']


def write_list():
    idx, items = build_list()
    os.makedirs(DOC, exist_ok=True)
    nb = len({i['书'] for i in items})
    draw = [i for i in items if '不出图' not in i]
    json.dump({'说明': '大图书馆书里的插图，一张一条。id 是 <书键>_<n>，n 照书里图版出现的先后（971 三册连着编），跟页面认的一样。'
                     '人物是照立绘资料里的名字机器认的，出图前人看一遍（同名的、只是提到名字的都会认进来）。画法见 画法.md。',
               '合计': len(items), '要出图': len(draw), '书': nb, '图': items},
              open(os.path.join(DOC, '清单.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    # 给人看的
    L = ['# 大图书馆插图清单', '', '`gen_plates.py list` 出的，别手改。改了书稿先跑 `build_lib.py` 再跑 list。', '']
    L.append('一共 %d 张图版，在 %d 本书里；要出图的 %d 张（谱 %d 张是唱法的说明、“往下几页” %d 张是一句话带过，不出图，页面照旧是字框）。' % (
        len(items), nb, len(draw), sum(1 for i in items if i['v'] == 'score'), sum(1 for i in items if i['label'].startswith('往下'))))
    pp = [i for i in draw if i['人物']]
    pr = [i for i in pp if any(p['有立绘'] and not p.get('只是提到') for p in i['人物'])]
    L.append('原文里认出人名的 %d 张，其中画里真站着、有立绘可挂的 %d 张（机器认的，见末一节；神名后头跟着殿、系、的、顿号的算只是提到）。' % (len(pp), len(pr)))
    L += ['', '## 按厅', '', '| 厅 | 书 | 图版 | 要出图 | A 兵书 | B 铜版 | C 抄本 | D 木版 | E 手记 |', '|---|---|---|---|---|---|---|---|---|']
    for h in idx['halls']:
        hi = [i for i in items if i['厅'] == h['k']]
        if not hi:
            continue
        hd = [i for i in hi if '不出图' not in i]
        L.append('| %s | %d | %d | %d | %s |' % (h['n'], len({i['书'] for i in hi}), len(hi), len(hd),
                                                ' | '.join(str(sum(1 for i in hd if i['画法'] == k) or '') for k in 'ABCDE')))
    L.append('| 合计 | %d | %d | %d | %s |' % (nb, len(items), len(draw), ' | '.join(str(sum(1 for i in draw if i['画法'] == k)) for k in 'ABCDE')))
    L += ['', '## 各书', '', '| 厅 | 书键 | 书名 | 图版 | 要出图 | 画法 | 成书 |', '|---|---|---|---|---|---|---|']
    seen = []
    for i in items:
        if i['书'] in seen:
            continue
        seen.append(i['书'])
        bi = [x for x in items if x['书'] == i['书']]
        L.append('| %s | %s | %s | %d | %d | %s | %s |' % (i['厅名'], i['书'], i['书名'], len(bi), sum(1 for x in bi if '不出图' not in x),
                                                       (i['画法'] + ' ' + STYLES[i['画法']]['name']) if i['画法'] else '', i['成书'][:24]))
    L += ['', '## 认出人名的图', '', '机器照立绘资料里的名字认的，同名的人、只提到名字没画出来的都在里头，出图前要人看一遍；有立绘的会挂立绘当长相参照。', '']
    for i in pp:
        L.append('- `%s` %s：%s' % (i['id'], '、'.join('%s（%s%s%s）' % (p['名'], p['键'], '' if p['有立绘'] else '，没有立绘', '，只是提到' if p.get('只是提到') else '') for p in i['人物']), i['原文'][:60]))
    open(os.path.join(DOC, '清单.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print('清单：%d 张，%d 本书，要出图 %d 张，认出人名 %d 张（画里站着、有立绘 %d）' % (len(items), nb, len(draw), len(pp), len(pr)))
    print(' '.join('%s=%d' % (k, sum(1 for i in draw if i['画法'] == k)) for k in 'ABCDE'))


# ---------- 提示词 ----------
CAST_OK = {}      # id → 只挂这几位（主会话看过）；没写的照清单里有立绘的全挂（至多三位）


def people_refs(it):
    want = CAST_OK.get(it['id'])
    ps = [p for p in it['人物'] if p['有立绘'] and not p.get('只是提到') and (want is None or p['名'] in want)]
    return ps[:3]


def ident(st, en):
    from PIL import Image
    d = por_dir(st, en)
    os.makedirs(os.path.join(OUT, '_ident'), exist_ok=True)
    dst = os.path.join(OUT, '_ident', '%s_%s.png' % (st, en))
    if not os.path.exists(dst):
        def flat(p, h):
            im = Image.open(p).convert('RGBA')
            bg = Image.new('RGBA', im.size, (200, 200, 204, 255))
            bg.alpha_composite(im)
            return bg.convert('RGB').resize((round(im.width * h / im.height), h), Image.LANCZOS)
        cells = [os.path.join(d, 'cell_casual.png'), os.path.join(d, 'art.png')]
        ims = [flat(p, 1024) for p in cells if os.path.exists(p)]
        out = Image.new('RGB', (sum(i.width for i in ims) + 36 * (len(ims) - 1), 1024), (200, 200, 204))
        x = 0
        for i in ims:
            out.paste(i, (x, 0))
            x += i.width + 36
        out.save(dst)
    return dst


def prompt(it):
    S = STYLES[it['画法']]
    st, medium = book_style(it)
    gl = ' '.join(g for k, g in GLOSS if k in it['原文'] + it['作者'])
    ps = people_refs(it)
    pr = ''
    if ps:
        pr = ('The attached reference picture%s show%s %s: use %s only for looks (hair, eyes, horns, build, clothes), and draw %s in this plate\'s own manner, not in the reference\'s painting style. ' % (
            's' if len(ps) > 1 else '', '' if len(ps) > 1 else 's', ', '.join('%s (left to right in order)' % p['名'] if len(ps) > 1 else p['名'] for p in ps),
            'them', 'them'))
    ar = S['ar']
    return ('Make one illustration in %s format. ' % ar +
            'It is a plate inside an old book in the library of a Western high-fantasy world of sword and magic (a Japanese fantasy RPG world). '
            'The book is called 《%s》, written by %s, %s. ' % (it['书名'], it['作者'][:60], it['成书'][:60]) +
            'In the book the plate is described by this caption (in Chinese); draw exactly this scene: 「%s」 ' % it['原文'] +
            label_hint(it) + (NOTES[it['id']] + ' ' if it['id'] in NOTES else '') +
            'Style: ' + S['text'].format(look=S['look']) + ' The medium of this particular book: ' + medium + '. ' +
            (gl + ' ' if gl else '') + pr + COMMON)


# ---------- 出图 ----------
STOP = []


def hit_limit(log):
    try:
        t = open(log, encoding='utf-8', errors='replace').read().lower()
    except OSError:
        return False
    return 'usage_limit' in t or 'usage limit' in t or ' 429' in t


def pick_ids(args, items):
    byid = {i['id']: i for i in items}
    if not args or args == ['sample']:
        return ['%s_%d' % x for k in 'ABCDE' for x in SAMPLE_PICK[k]]
    if args == ['all']:
        return [i['id'] for i in items if '不出图' not in i]
    out = []
    for a in args:
        if a in byid:
            out.append(a)
        else:
            out += [i['id'] for i in items if i['书'] == a and '不出图' not in i]
    return out


def gen(ids, items):
    import gpt_gen
    byid = {i['id']: i for i in items}
    os.makedirs(OUT, exist_ok=True)
    home = [0]

    def job(k):
        it = byid[k]
        stem = os.path.join(OUT, k)
        if os.path.exists(stem + '.png'):
            return 'had'
        refs = [ident(*p['键'].split(':', 1)) for p in people_refs(it)]
        while home[0] < len(HOMES):
            h = HOMES[home[0]]
            try:
                return gpt_gen.gen(stem, prompt(it), refs=refs, home=h)
            except Exception as x:
                if hit_limit(stem + '.log'):
                    if home[0] < len(HOMES) and HOMES[home[0]] == h:
                        print('== %s 撞了额度，换号' % h, flush=True)
                        home[0] += 1
                    continue
                return '没成：%s' % str(x)[:300]
        STOP.append(k)
        return '两个号都撞了额度，没开'

    with ThreadPoolExecutor(int(os.environ.get('PLATE_WORKERS', '3'))) as ex:
        for k, res in zip(ids, ex.map(job, ids)):
            print(k, res, flush=True)


def cut(ids):
    from PIL import Image
    os.makedirs(PLATES, exist_ok=True)
    for k in ids:
        src = os.path.join(OUT, k + '.png')
        if not os.path.exists(src):
            print(k, '没有原图')
            continue
        im = Image.open(src).convert('RGB')
        # 装进 1000×1200 的框（横幅宽 1000、竖幅高 1200，宽不过 1200），质量 72：页面上图至多四五百像素宽，手机两倍屏也够；
        # 一张平均二百 KB 上下，全部出完一百四五十 MB，推图床要另开分支并照 120MB 拆段
        sc = min(1000 / im.width, 1200 / im.height, 1)
        if sc < 1:
            im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
        p = os.path.join(PLATES, k + '.webp')
        im.save(p, 'WEBP', quality=72, method=6)
        print(k, im.size, os.path.getsize(p) // 1024, 'KB')


def sheet(ids, items, name='样张总览.jpg'):
    from PIL import Image, ImageDraw, ImageFont
    byid = {i['id']: i for i in items}
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
    cols, cw, ch, cap = 2, 1000, 760, 150
    have = [k for k in ids if os.path.exists(os.path.join(OUT, k + '.png'))]
    rows = (len(have) + cols - 1) // cols
    W, H = cols * cw + (cols + 1) * 16, rows * (ch + cap) + (rows + 1) * 16
    out = Image.new('RGB', (W, H), (28, 30, 42))
    d = ImageDraw.Draw(out)
    for n, k in enumerate(have):
        it = byid[k]
        x, y = 16 + (n % cols) * (cw + 16), 16 + (n // cols) * (ch + cap + 16)
        im = Image.open(os.path.join(OUT, k + '.png')).convert('RGB')
        s = min(cw / im.width, ch / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        out.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
        S = STYLES[it['画法']]
        d.text((x, y + ch + 8), '%s %s ｜ 《%s》%s ｜ %s' % (it['画法'], S['name'], it['书名'][:22], it['label'], k), font=font, fill=(230, 226, 210))
        t = it['原文']
        lines, cur = [], ''
        for c in t:
            cur += c
            if d.textlength(cur, font=small) > cw - 10:
                lines.append(cur); cur = ''
        if cur:
            lines.append(cur)
        for j, l in enumerate(lines[:5]):
            d.text((x, y + ch + 42 + j * 21), l + ('……' if j == 4 and len(lines) > 5 else ''), font=small, fill=(170, 176, 196))
    os.makedirs(SHOT, exist_ok=True)
    p = os.path.join(SHOT, name)
    out.save(p, 'JPEG', quality=82)
    print(p, out.size, os.path.getsize(p) // 1024, 'KB')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'list':
        write_list()
        sys.exit()
    items = load_items()
    if cmd == 'gen':
        gen(pick_ids(sys.argv[2:], items), items)
    elif cmd == 'cut':
        cut(pick_ids(sys.argv[2:], items))
    elif cmd == 'sheet':
        sheet(pick_ids(sys.argv[2:], items), items)
    elif cmd == 'show':
        it = {i['id']: i for i in items}[sys.argv[2]]
        print(prompt(it))
        print('参考图：', [p['键'] for p in people_refs(it)])
    else:
        print('用法见文件头')
