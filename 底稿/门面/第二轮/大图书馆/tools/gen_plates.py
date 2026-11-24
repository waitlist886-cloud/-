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
              'Faces are simple and plain, drawn the way old manuals draw them, not anime faces. '
              'When two figures grapple or cross blades, every arm, hand, leg and foot must be traceable to its owner: two people have exactly four arms and four legs in total, '
              'and every sword is one unbroken piece from hilt to point.'),
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
    'ming-jsyxs': ('A', 'pen-and-ink outlines on calfskin vellum, only the clothes and the small round shields washed with a thin ochre, exactly the manner of Ms. I.33. '
                       'Every figure holds ONE arming sword in the right hand and ONE small round buckler in the left, as in I.33. The guard names in the captions are I.33-style guards: '
                       '臂下 under-arm (sword tucked under the left arm, point back), 右肩 / 左肩 right / left shoulder (sword raised beside that shoulder, point up), 顶上 overhead (sword held above the head), '
                       '胸前 breast (hilt at the chest, point at the opponent), 长尾 long tail (sword trailing low behind, point near the ground), 弓弦 bowstring (sword held flat across the chest, the buckler hand supporting the blade like a drawn bow; NO real bows). '
                       '缚 binding means pinning the opponent\'s sword and sword hand with your own sword and buckler, NEVER rope or cords'),
    'ming-jdtp': ('A', 'pen drawing washed with watercolour on parchment, as in Talhoffer, the shields painted with their emblems in colour'),
    'ming-bhbf': ('A', 'very precise ink line drawing on thick paper, circles drawn with compasses and lines with a ruler, as in Thibault. '
                      'The Hundred Ring (百环) of this book is ONE single large circle on the floor with one hundred small evenly spaced points (tiny ring-marks, 铭环) on its line; '
                      'its seven chords (弦) are straight lines across it. Never draw concentric circles, targets or spider webs; never repeat the same man many times around the ring'),
    'ming-clbz': ('B', 'ink on official ruled paper, bluish black ink; a clumsy little doodle where the caption says so'),
    'ming-wlth': ('A', 'mineral pigments (ochre, azure, vermilion, a touch of silver) painted on thick ledger paper, like the Codex Wallerstein. '
                      'Ironcheek (铁颊), who appears in many plates, is one HUMAN man (not a dwarf): broad-shouldered, short hair, short beard, an iron plate guarding one cheek'),
    'ming-jd': ('A', 'lines sketched in charcoal and then burned into thick ash-grey paper with a red-hot iron stylus: dark brown scorched lines, no colour. '
                     'This whole book is the wrestling of the flamehorn demon-kin of the Azure-Flame Horn City, so the wrestlers are flamehorn demon-kin with two thick horns'),
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
    'arcane-aedldldl': ('B', 'a survey-and-travel geography plate in cartographer\'s ink line work on thick waxed guild paper; the margins are crowded with later readers\' notes, drawn only as faint unreadable strokes'),
    'arcane-ryzq': ('B', 'ink technical drawing on thick drafting paper from an early furnace-and-steam treatise, sometimes with a pasted correction slip on the page'),
    'arcane-gdysl': ('B', 'copperplate engraving on very faintly gridded star-chart paper, like the plates of early natural philosophy (Boyle, Hooke)'),
    'arcane-txl': ('B', 'fine engraved astronomical drawing on thin star-chart paper with silvered page edges; stars, sundial stones and star maps only, never a moon or crescent'),
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
          'anything the caption calls writing, a title, a label, a quoted word or a number is drawn only as faint wavy grey scribble lines or blank tags: never Latin letters, never cursive handwriting, never Chinese or Japanese characters, never kana, never digits. '
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
    if v == 'coin' and '没有钱' not in it['原文']:
        return 'Draw the coin or coins true to size on blank paper, front and back side by side, like a numismatic plate; no lettering on the coins. '
    return ''


# 个别几张原文容易读岔的地方（主会话查图时添）
NOTES = {
    'arcane-wytj_12': 'The two shot balls (item five) are drawn EXACTLY alike, plain, no glow or marks on either.',
    'child-jtyczjgz_3': "This page's blue dot is big: it is the hero himself, the ONLY blue dot on the page, turning into the dark path on the left.",
    'child-jtyczjgz_11': 'There is NO blue dot anywhere on this page (no blue figure in the crowd).',
    'stage-jdyh_3': 'Exactly TWENTY bundles of tally marks (count them), the last one cut thick and deep.',
    'child-ktsww_16': 'This is the same picture as plate eight of the other half of the book: a great crack split open in the middle of a wasteland, stakes driven at its edge with ropes tied on, a tent pitched beside it, several adults with backpacks queuing down into the crack, and far off a ring of children watching, the front child holding the end of a thin cord. Mark it with SIX small blank tags with leader lines, one of them on a little wooden board hanging at the tent door.',
    'child-jkty_2': 'Two children sit BACK TO BACK on a step, facing opposite ways; one reaches a hand behind her back, palm down, and the other slaps it with her palm.',
    'child-jkty_6': 'A row of chalk squares on the ground; the farthest square holds a big mushroom drawing. A child hopping on one foot has reached the SECOND-TO-LAST square, right next to the mushroom square, and is turning to hop back toward the start.',
    'child-yqlyc_5': 'Above the waterline: a row of roofless stone huts standing in water. Below the waterline: their mirror REFLECTION, drawn UPSIDE DOWN (flipped vertically, as reflections are), and in the upside-down reflection each hut has a roof with an upside-down heron on it; above the water the huts have no roofs and no herons.',
    'child-bygrxj_8': 'Two panels side by side in one frame. Left panel: a lamp post in a camp, a queue of people under the lamp, the small child Beibei last in line with bread stuffed in the mouth. Right panel: next morning, the camp completely EMPTY: no tents, no stakes, no lamp, no people, only bare ground with holes where stakes were; Beibei alone curled asleep behind a rock while darkness closes in.',
    'child-yzmybcj_5': 'The young man pulls the sword fully OUT of the stone with both hands on the hilt (both arms visible), the blade shining like morning, clear of the stone; the queue of people gape.',
    'child-swdgs_6': 'The camp officer standing at the gateway is a WOMAN (the same woman officer as the previous picture).',
    'child-ktsww_9': 'The stone monument is enormously tall, taller than TEN grown men stacked on top of each other: the people beside it are tiny, reaching only to the bottom of its base.',
    'strife-dbdy_2': "Draw the twelve priests FACING THE VIEWER (we look at their faces; the back of the shield wall stands behind them in the background), standing apart, each with a small round shield slung behind his shoulders. Each raises his LEFT hand, which, since they face us, is on the VIEWER'S RIGHT side of each figure; before every raised palm stands a flat pane of pale golden light.",
    'arcane-mjx_2': 'The mark carved on the scale weight is a single plain horizontal notch, not a letter or numeral.',
    'arcane-wytj_10': 'Item two is a trough carved from STONE (a stone basin), not wood.',
    'arcane-yzxdtdll_5': "A fold-out map: a row of black towers on southern wasteland; ONE line runs north across the lava plain to a horned city, where a SECOND line coming from north of that city joins it; the joined line runs to a cluster of main towers outside the capital, and from there hundreds of fine lines spread into the city's streets.",
    'arcane-jgxdl_3': "Two whole living wolf-like beasts side by side in plain outside view (NO dissection, NO skeleton, no cutaway): the left one untouched; the right one 'stained' with its eyes blackened, fine lines seeping outward from the edges of a wound, and the grass under its feet white.",
    'arcane-cxj_2': 'On a small table a test stand: a FLAT spiral clock-spring (a coiled flat steel band, like a watch mainspring, not a helical coil spring) wound tight, its winding crank facing outward; a brass clamp reaches out and bites the axle at the bottom of a fist-sized magic crystal heart set beside it. A faint grey scribble note beside it.',
    'arcane-lfs_5': 'The ring-mark contains one LONG gentle wave with widely spaced crests (only two or three crests across the whole ring), not short tight peaks.',
    'ming-jd_48': "The old man pushes Isam's LEFT shoulder with one hand and with his other hand pulls Isam's RIGHT elbow (the far arm), twisting him.",
    'ming-jd_59': "The old man lays his own ELBOW (forearm bent) across the inside of Isam's elbow joint and presses it down; not gripping with his hands.",
    'ming-jd_61': "The old man stands behind Isam, threads BOTH arms up under Isam's armpits from behind and laces his ten fingers together on the BACK of Isam's neck (a full nelson).",
    'ming-jd_29': "A thin crack line (the edge seam of the ring) runs across the ground right under Isam's rear foot; Isam's rear foot is planted on it.",
    'arcane-lpyjb_2': "The table's cells are left EMPTY (blank boxes), no marks inside them at all; a single smudge of red charcoal in the margin, no letters.",
    'arcane-dqtpbw_4': 'The brass ruler has tick marks only, no numerals.',
    'ming-jsyxs_17': "Two figures only, each with ONE sword and ONE buckler. The priest's buckler presses down on the student's sword hand, and the priest's own sword slips in UNDER his buckler, its point reaching into the student's armpit. The student holds a complete sword (blade and hilt).",
    'ming-jsyxs_25': 'Two figures, each holding exactly ONE sword and ONE small buckler, no extra blades anywhere. The woman stands in the under-arm guard: her sword tucked under her LEFT arm with its point to the rear, her buckler held over the hilt in front of her chest. The priest faces her.',
    'strife-yysj_2': 'All forty-odd people around the bonfire are horned demon-kin, and a small flame burns ON THE HORNS of every one of them (fire on their horns, not torches or cups). The woman speaking the oath also has horns.',
    'strife-dbdy_2': "Twelve priests seen FROM BEHIND (we see their backs), standing apart behind a shield wall, each with a small round shield slung on his back. Each raises his LEFT arm; since we see their backs, the raised arm is on the VIEWER'S LEFT side of each figure. Before every raised palm stands a flat pane of pale golden light.",
    'strife-dbdy_3': 'A shield standing on the southernmost end of the wall, TWICE as tall as a man (it towers over the old priest). Along its rim runs one band of carved scratches (no letters): the left half of the band cut fresh and sharp, the right half old and worn. A white-haired old priest stands before it raising his left palm, with no light in it.',
    'maze-yf_2': 'Both kinds of handwriting on the page are drawn only as faint grey scribble lines (small cramped scribble on the upper half, looser scribble below, one line in the middle traced twice), never letters.',
    'moon-qxsp_4': 'No cow anywhere: only a long tethering rope hangs down from the floating rock and is tied to a tree on the ground.',
    'moon-qxsp_7': 'Only the three sailors have wax in their ears; the helmsman lashed to the mast has none. The sea is drawn as plain medieval bestiary waves (simple scalloped lines), not curling Japanese-print waves.',
    'moon-zgz_7': 'There is NO coin on this plate at all; draw only what the caption lists (horsehair, oxtail hair, a scale and two people) as a simple pen drawing.',
    'ming-jd_83': "The old man's face is pushed under the water (only the back of his head and horns show above the surface); both men have horns; every arm clearly belongs to one of the two men.",
    'ming-jdtp_17': "The fallen knight lies on the ground; the opponent's sword point stops just before his visor; the fallen knight raises his LEFT hand (the arm on his left side), his right hand on the ground.",
    'ming-jdtp_24': "Inside the white chalk ring of the lists: one man stands in a pit that is only WAIST-DEEP (his upper body above the ground), holding a sword; a ring of white lime around the pit's edge. The other man stands outside the pit, inside the lists ring, with sword and shield.",
    'ming-bhbf_2': 'The point of the level-held sword reaches EXACTLY to the edge of the circle, not beyond it.',
    'ming-bhbf_8': 'A straight chord (not through the centre) runs from the 12th point to the 50th point of the ring (they are 38 points apart, so the chord is shorter than a diameter); three small footprints marked along it.',
    'ming-bhbf_9': 'Many men stand on the points of the ring, one per point, evenly spaced; at one spot of the ring a point is empty and its little ring-mark is dark. Just outside the ring, directly facing that empty spot, one man stands on a footprint mark holding his sword level.',
    'ming-wlth_5': 'In the middle of the arena ONE fencer unfolds his sword art: petals of sword-light fill the whole arena. Ironcheek stands among the petals, a little off-centre, his clothes slit in seventeen places, his skin unhurt.',
    'ming-wlth_6': 'THREE people: two people dressed all in white stand back to back in the middle; Ironcheek (not in white) comes from the left raising a hammer; the white figure on the right tilts his head to the left first, the left one follows, and the hammer misses.',
    'ming-wlth_16': 'TWO people: one fighter presses the fingertips of his LEFT hand on an old carved mark on his RIGHT wrist and has already shifted into a new stance; Ironcheek is still charging at where the old stance was.',
    'ming-bwzsj_3': 'The struck-out line under the stove is a row of faint grey wavy scribble with one straight line through it, no letters.',
    'ming-zddyslbcxqstgm_39': "Man A's sabre stops a finger's breadth before Man B's throat. Man B's sabre stops a finger's breadth above Man A's sword-hand WRIST (Man A's arm is extended forward, so B's blade rests just over A's wrist). Neither blade touches skin.",
    'ming-zddyslbcxqstgm_23': "The short-sword fighter HIMSELF holds a short sword in his hand; directly behind him stands an identical copy of him (also holding a short sword). The opponent's sword comes down on that copy behind, and the copy bursts into scattered light.",
    'ming-zddyslbcxqstgm_3': 'Composition seen from a high viewpoint: two TRIANGULAR (arrowhead) blocks of armoured men, each triangle pointing at the other, about ten men per triangle arranged 1-2-3-4 rows from the point back. The man at the point of each triangle is visibly taller; a glow runs from him back along the two slanted outer edges of his triangle. Not columns, not lines: two triangles.',
    'ming-zddyslbcxqstgm_59': 'Exactly TWENTY-THREE men in the row (count them), plus nothing else in line; below them small blank tags, one per man.',
    'ming-qjsst_34': 'Exactly SEVEN glowing swords (count them: seven), no more.',
    'ming-qjsst_13': 'Both hands hold the sword high above the head with the blade lying back over the head so that the POINT AIMS BEHIND HIM (Vom Tag / roof guard seen from the side), as if about to split the sky.',
    'ming-qjsst_16': "The crowned tutor holds his sword with both hands LOW, the hilt down by his left knee and the blade slanting up in front of him, point raised like a boar's tusk (Meyer's boar guard). He grips it; it is not lying on the ground. A straight longsword.",
    'ming-qjsst_22': "The 'grey man' is a pale grey, faceless ghost-figure (the same student drawn faint grey to show what he should NOT do), turning back to pick up the dropped sword, while the tutor raises his hand behind him; the real student, drawn normally, runs out of the frame.",
    'ming-qjsst_24': "The STUDENT holds a shield and his own sword: he pushes the tutor's blade aside with the face of the shield and, in the same motion, thrusts his own sword in from under the shield.",
    'ming-qjsst_28': "The tutor (crowned, red sash) is the one wearing armour. With one hand he grabs the student's hand where it holds the blade and presses it down, so that the student's sword point slides out of the gap in the tutor's armour without hurting him.",
    'ming-qjsst_29': 'Two students stand back to back, swords pointing outward, and BOTH step sideways the same way together (side-stepping in step); a few grey wolves circle around them.',
    'ming-zddyslbcxqstgm_3': "Two wedge formations (each a V / arrowhead shape of about ten men, point forward) charge at each other in a yard. The man at each wedge's point is half a head taller than the rest; the glow on him flows back along BOTH edges of his wedge; the men stand shoulder to shoulder, each man's left side covered by the next man's shield.",
    'ming-zddyslbcxqstgm_22': "The 'tide' is a dark, dense swarm of monsters (a black mass of countless bodies, claws and horns), NOT sea waves; no ocean waves at all. In it one man stands with a greatsword coming down on a monster taller than a city gate tower; in one corner three tiny figures retreat out of the swarm, one looking back.",
    'ming-zddyslbcxqstgm_23': "The opponent's sword slashes DOWN onto the duplicate standing behind the short-sword fighter, from above and beside, never passing through anyone's head or body; where it strikes, the duplicate bursts into scattered light.",
    'ming-zddyslbcxqstgm_32': 'Exactly FIVE beasts around the man, one at each side (count them: five). The black mass is OUTSIDE the well mouth, on the ground before it, pulling back toward the well; the people on the distant city wall cling to the battlements. Do not copy any beasts from the style reference.',
    'ming-zddyslbcxqstgm_33': "The mount is a big grey highland WOLF (plain wolf, no spots, no ear tufts), foam at its mouth; the rider's bow is fully drawn; below the slope a crowd of monsters look up; above them an eagle folds its wings and dives.",
    'ming-zddyslbcxqstgm_39': "Two men a step and a half apart, each with a sabre: one man's blade stops just in front of the other's throat; the other man's blade stops just above the first man's WRIST (sword hand); neither touches skin. A child squats at the side copying them with a stick.",
    'arcane-ryzq_1': 'Count carefully: twelve small cones stand in one row on a firebrick. Cones 1 to 6 (left) are bent over, more and more, and the tip of cone 6 just touches the brick; cone 7 leans only slightly; cones 8 to 12 (the right five) stand straight. Under the brick one line of faint grey scribble, no letters.',
    'crown-wdxsx_1': 'The page holds exactly TWELVE lines of print, each line drawn as a row of faint grey scribble (no letters); under the lines, printed very faintly like a pale watermark, the shadow of one white candle whose flame leans to one side; a tiny faint line of scribble at the foot. Nothing else: no door, no solid candle drawing.',
    'stage-mcahq_1': 'The page is the first page of a hand-copied musical score: several faint ruled staves with simple notation marks across the page (no clefs, no letters, no digits); in the top left corner a small drawing of a bone tally whose number is just a few carved notches, with an empty space below it.',
    'craft-lbdd_3': "This is a smith's homemade notation, NOT modern sheet music: no five-line staff, no clefs, no notes. On the left a column of short horizontal dashes, one dash per sung note; on the right lines of handwriting drawn as faint pencil scribble, the top line pressed hardest; a small brass tuning fork nailed to the page corner.",
    'strife-qsdg_1': 'The names carved all over the wall are shown only as dense rows of short scratched nicks and tally marks, never as letters.',
    'bronze-hyqyy_1': 'Exactly THIRTEEN chairs along the long table (count them), plus the one very low chair by the wall behind the first seat.',
    'maze-jxcdz_1': "The mapmaker's mark by the flame is just a tiny blank tag, not a character.",
    'bronze-ny_1': 'The two doors are DRAWN FLAT ON THE GROUND (chalk-like outlines of two door frames lying on the floor, seen from a little above), not standing doors; a ring of small lamps around each outline, more lamps around the outer one, fewer around the inner one; inside the frames the ground is empty.',
    'bronze-jh_1': 'The carving on the stone walls is rendered as fine horizontal bands of chisel texture, never letters or handwriting.',
    'maze-fbsdl_1': 'The drake is hunched with its neck pulled DOWN INTO its shoulders (like a creature huddling against cold), head drawn in close to the body, not stretched forward.',
    'arcane-lpyjb_1': 'Around the copper-bronze cage bars run several rings of carved runes (simple geometric glyphs, not letters), and each ring has a small blank tag with a leader line, as numbered callouts.',
    'arcane-dqtpbw_1': 'The vessel is a plain European laboratory jar of white glazed stoneware with no painted decoration at all (no blue-and-white flowers).',
    'arcane-jgxdl_1': "The wolf's skull is inside the wolf's head (the skeleton layer follows the body correctly: skull in head, ribs in chest); all labels are small blank tags.",
    'ming-bwzsj_1': 'This is an ink rubbing of a carved lintel: black ground, the carved lines come out white. The carved inscription is four lines arranged as columns from left to right, but render every carved line only as weathered, worn white strokes that cannot be read as any letters or characters; the top of the first (leftmost) column is weathered away at one corner.',
    'ming-bhbf_1': "Seen straight from directly above: a man lies flat on his back on the ground, arms stretched straight past his head, legs together; a large circle centred on his navel just touches his fingertips and heels; a cross inside the circle, its four ends marked with four small blank tags (for the four directions). Geometric diagram like Thibault's or Vitruvian figure, but lying, not standing.",
    'shen-gzdh_1': 'Exactly FIVE crooked horizontal lines across the horn from root to tip, each with one small blank tag beside it; drawn clumsily by a child, the lines uneven and wobbly.',
    'moon-qtgq_1': 'The gateway is almost shut, only a narrow slit left open; inside it a man sits holding a spear crosswise with a big wolf lying at his feet; outside the gate SEVERAL people turn sideways and squeeze into that narrow slit one after another.',
    'strife-yysj_1': 'Only the old woman lying in bed has horns. The tall thin girl sitting by the bed has NO horns at all.',
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


PREV_WORDS = ('同上', '上一页', '上一幅', '上一张', '前一页', '跟前面', '跟前头', '照前', '换了一边', '换到')


def prev_hint(it):
    """原文是“同上，换到左肩”“跟上一页一样，换了一边”这一类的，把本书上一张的原文带上"""
    if not any(w in it['原文'] for w in PREV_WORDS):
        return ''
    try:
        items = load_items()
    except Exception:
        return ''
    prev = [i for i in items if i['书'] == it['书'] and i['n'] < it['n'] and '不出图' not in i]
    if not prev:
        return ''
    chain, cur = [], prev[-1]
    chain.append(cur['原文'])
    while any(w in cur['原文'] for w in PREV_WORDS):          # 上一张也是“同上”的，接着往前找
        pp = [i for i in prev if i['n'] < cur['n']]
        if not pp:
            break
        cur = pp[-1]
        chain.append(cur['原文'])
    return ('This caption refers to the previous plate(s) of the book. Previous captions, nearest first: ' + ' / '.join('「%s」' % c for c in chain) +
            '. Draw the previous scene with the change this caption names (for example the same pose mirrored to the other side, the sword moved to the other shoulder). ')


def prompt(it, refs=()):
    S = STYLES[it['画法']]
    st, medium = book_style(it)
    gl = ' '.join(g for k, g in GLOSS if k in it['原文'])          # 只看原文：作者是夜魔不等于画里的人是（11-24 用户定的）
    ps = [] if refs else people_refs(it)          # 挂了参照的照 refs_text 说
    pr = refs_text(refs)
    if ps:
        pr = ('The attached reference picture%s show%s %s: use %s only for looks (hair, eyes, horns, build, clothes), and draw %s in this plate\'s own manner, not in the reference\'s painting style. ' % (
            's' if len(ps) > 1 else '', '' if len(ps) > 1 else 's', ', '.join('%s (left to right in order)' % p['名'] if len(ps) > 1 else p['名'] for p in ps),
            'them', 'them'))
    ar = S['ar']
    return ('Make one illustration in %s format. ' % ar +
            'It is a plate inside an old book in the library of a Western high-fantasy world of sword and magic (a Japanese fantasy RPG world). '
            'The book is called 《%s》, written by %s, %s. ' % (it['书名'], it['作者'][:60], it['成书'][:60]) +
            'In the book the plate is described by this caption (in Chinese); draw exactly this scene: 「%s」 ' % it['原文'] +
            label_hint(it) + prev_hint(it) + (NOTES[it['id']] + ' ' if it['id'] in NOTES else '') +
            'Style: ' + S['text'].format(look=S['look']) + ' The medium of this particular book: ' + medium + '. ' +
            (gl + ' ' if gl else '') + pr + COMMON)


# ---------- 参照：画法一张、本书头一张 ----------
# 每种画法挑样张里过得最干净的一张当风格参照（用户 11-24 看过样张总览）；月银纪那几本抄本是银墨写在兽皮上，另挂七曜兽谱那一张。
STYLE_REF = {'A': 'ming-qjsst_1', 'B': 'arcane-sf_1', 'C': 'crown-xgsds_1', 'D': 'child-ktsww_1', 'E': 'strife-xqsqr_1'}
STYLE_REF_MOON = 'moon-qxsp_3'
PROG = os.path.join(DOC, '进度.json')


def load_prog():
    return json.load(open(PROG, encoding='utf-8')) if os.path.exists(PROG) else {}


def save_prog(pg):
    json.dump(pg, open(PROG, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, sort_keys=True)


def drawable(items):
    return [i for i in items if '不出图' not in i]


def book_first(items):
    """书键 → 这本书头一张要出图的 id"""
    out = {}
    for i in drawable(items):
        if i['书'] not in out or i['n'] < int(out[i['书']].rsplit('_', 1)[1]):
            out[i['书']] = i['id']
    return out


def style_ref_of(it):
    if it['画法'] == 'C' and it['书'].startswith('moon-'):
        return STYLE_REF_MOON
    return STYLE_REF.get(it['画法'])


def refs_of(it, items, pg):
    """[(路径, 是什么)]：画法参照、本书头一张（审过的才挂）、点了名的人。"""
    out = []
    sr = style_ref_of(it)
    if sr and sr != it['id'] and os.path.exists(os.path.join(OUT, sr + '.png')):
        out.append((os.path.join(OUT, sr + '.png'), 'style'))
    bf = book_first(items).get(it['书'])
    if bf and bf != it['id'] and bf != sr and pg.get(bf, {}).get('状态') == 'ok' and os.path.exists(os.path.join(OUT, bf + '.png')):
        out.append((os.path.join(OUT, bf + '.png'), 'book'))
    for p in people_refs(it):
        out.append((ident(*p['键'].split(':', 1)), 'person'))
    return out[:5]


def refs_text(refs):
    if not refs:
        return ''
    n = {'style': 'a style reference plate from this same series of library books', 'book': 'an earlier plate from this very book',
         'person': 'a character reference (looks only)'}
    t = 'The attached pictures, in order: ' + '; '.join('%d) %s' % (j + 1, n[k]) for j, (_, k) in enumerate(refs)) + '. '
    if any(k == 'style' for _, k in refs):
        t += ('From the style reference take only the kind of drawing and its level of craft (how lines, hatching and figures are handled); never its subject, composition, figures, beasts or objects (do not copy any creature or object from it into this picture). '
              "Where this book's own medium below names a different paper, ink or colour, the book's medium wins. ")
    if any(k == 'book' for _, k in refs):
        t += ("The earlier plate from this book shows how this book's illustrator draws: match its hand, paper, palette and framing, "
              "so the two look drawn by the same person, but draw the new scene from the caption, not that plate's scene. ")
    if any(k == 'person' for _, k in refs):
        t += "Use a character reference only for that person's looks (hair, eyes, horns, build, clothes), drawn in this plate's own manner. "
    return t


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
    pg = load_prog()
    if args[:1] == ['first']:          # 各书头一张，还没审过的
        return [k for k in book_first(items).values() if pg.get(k, {}).get('状态') != 'ok' and not pg.get(k, {}).get('出不了')]
    if args[:1] == ['rest']:           # 头一张审过了的书，余下还没出的；rest N 只取头 N 张
        bf = book_first(items)
        out = [i['id'] for i in drawable(items) if i['id'] not in bf.values() and pg.get(bf[i['书']], {}).get('状态') == 'ok'
               and not os.path.exists(os.path.join(OUT, i['id'] + '.png')) and not pg.get(i['id'], {}).get('出不了')]
        return out[:int(args[1])] if len(args) > 1 else out
    if args[:1] == ['unreviewed']:     # 出了图、还没审的
        return [i['id'] for i in drawable(items) if os.path.exists(os.path.join(OUT, i['id'] + '.png')) and not pg.get(i['id'], {}).get('状态')]
    if args[:1] == ['ok']:             # 审过了的
        return [i['id'] for i in drawable(items) if pg.get(i['id'], {}).get('状态') == 'ok']
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
    pg = load_prog()

    def job(k):
        it = byid[k]
        stem = os.path.join(OUT, k)
        if os.path.exists(stem + '.png'):
            return 'had'
        rr = refs_of(it, items, pg)
        refs = [r for r, _ in rr]
        while home[0] < len(HOMES):
            h = HOMES[home[0]]
            try:
                return gpt_gen.gen(stem, prompt(it, rr), refs=refs, home=h)
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


# 照 build_lib.py 的 PLATE_SEG（照厅分段），不 import 它（它一载进来就换 stdout）
def seg_of(k):
    t = open(os.path.join(ROOT, '底稿', '门面', '共用', 'build_lib.py'), encoding='utf-8').read()
    m = re.search(r"PLATE_SEG = (\{.*?\})\n", t, re.S)
    seg = eval(m.group(1))
    return seg.get(k.split('-', 1)[0], 'p2')


def cut(ids):
    from PIL import Image
    os.makedirs(PLATES, exist_ok=True)
    for k in ids:
        src = os.path.join(OUT, k + '.png')
        if not os.path.exists(src):
            print(k, '没有原图')
            continue
        dst = os.path.join(PLATES, seg_of(k), k + '.webp')
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            continue          # 已经转过、原图没换
        im = Image.open(src).convert('RGB')
        # 装进 1000×1200 的框（横幅宽 1000、竖幅高 1200，宽不过 1200），质量 72：页面上图至多四五百像素宽，手机两倍屏也够；
        # 一张平均二百 KB 上下，全部出完一百四五十 MB，推图床要另开分支并照 120MB 拆段
        sc = min(1000 / im.width, 1200 / im.height, 1)
        if sc < 1:
            im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
        p = os.path.join(PLATES, seg_of(k), k + '.webp')
        os.makedirs(os.path.dirname(p), exist_ok=True)
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


# ---------- 审图、进度 ----------
def mark(ids, why, state):
    """state 'ok'：审过了（why 不空就记成拿不准的话）；'redo'：整张重画，原图挪进 旧/<id>_r<k>.png，缘故记下来；
    'skip'：这一张不出图了（出图服务回回拒、或重画三回还有看得出的错），原图挪进 旧/，页面上照旧是字框"""
    pg = load_prog()
    os.makedirs(os.path.join(OUT, '旧'), exist_ok=True)
    for k in ids:
        e = pg.setdefault(k, {})
        if state == 'ok':
            e['状态'] = 'ok'
            if why:
                e['拿不准'] = why
        elif state == 'skip':
            e['出不了'] = why
            e.pop('状态', None)
            src = os.path.join(OUT, k + '.png')
            if os.path.exists(src):
                v = e.get('重画', 0) + 1
                shutil.move(src, os.path.join(OUT, '旧', '%s_r%d.png' % (k, v)))
            w = os.path.join(PLATES, seg_of(k), k + '.webp')
            if os.path.exists(w):
                os.remove(w)
        else:
            src = os.path.join(OUT, k + '.png')
            if not os.path.exists(src):
                print(k, '没有原图，跳过')
                continue
            v = e.get('重画', 0) + 1
            while os.path.exists(os.path.join(OUT, '旧', '%s_r%d.png' % (k, v))):
                v += 1
            shutil.move(src, os.path.join(OUT, '旧', '%s_r%d.png' % (k, v)))
            if os.path.exists(os.path.join(OUT, k + '.log')):
                shutil.move(os.path.join(OUT, k + '.log'), os.path.join(OUT, '旧', '%s_r%d.log' % (k, v)))
            for x in ('_2', '_3'):
                if os.path.exists(os.path.join(OUT, k + x + '.png')):
                    os.remove(os.path.join(OUT, k + x + '.png'))
            e['重画'] = v
            e.pop('状态', None)
            e.setdefault('缘故', []).append(why)
        print(k, state, why)
    save_prog(pg)


def progress(items):
    pg = load_prog()
    dr = drawable(items)
    have = [i for i in dr if os.path.exists(os.path.join(OUT, i['id'] + '.png'))]
    ok = [i for i in dr if pg.get(i['id'], {}).get('状态') == 'ok']
    pend = [i for i in have if pg.get(i['id'], {}).get('状态') != 'ok']
    skip = {k: v['出不了'] for k, v in pg.items() if v.get('出不了')}
    left = [i for i in dr if not os.path.exists(os.path.join(OUT, i['id'] + '.png')) and i['id'] not in skip]
    redo = {k: v for k, v in pg.items() if v.get('重画')}
    doubt = {k: v['拿不准'] for k, v in pg.items() if v.get('拿不准')}
    webp = sum(1 for i in dr if os.path.exists(os.path.join(PLATES, seg_of(i['id']), i['id'] + '.webp')))
    L = ['# 大图书馆插图·出图进度', '', '`gen_plates.py progress` 出的，别手改；明细在 `进度.json`。', '',
         '- 要出图 %d 张；出了 %d 张，审过 %d 张，出了还没审 %d 张，还没出 %d 张；转成 webp 进了页面的 %d 张。' % (len(dr), len(have), len(ok), len(pend), len(left), webp),
         '- 整张重画过的 %d 张，合计重画 %d 回；不出图（页面照旧是字框）%d 张。' % (len(redo), sum(v['重画'] for v in redo.values()), len(skip)),
         '- 接着跑：先 `gen first`（各书头一张），审完 `mark ok`／`redo`，再 `gen rest 100` 一批一批出；每批审完 `cut ok`、重跑 build_lib.py 和 sync.py copy、`batchsheet <n> <id…>`。', '']
    if left:
        L += ['## 还没出的（按书）', '']
        by = {}
        for i in left:
            by.setdefault(i['书'], []).append(i['n'])
        for b, ns in by.items():
            L.append('- %s：%d 张（%s）' % (b, len(ns), '、'.join(str(n) for n in ns[:30]) + ('……' if len(ns) > 30 else '')))
        L.append('')
    if pend:
        L += ['## 出了还没审的', '', '、'.join(i['id'] for i in pend), '']
    if redo:
        L += ['## 重画过的', '']
        for k, v in sorted(redo.items()):
            L.append('- `%s` %d 回：%s' % (k, v['重画'], '；'.join(x for x in v.get('缘故', []) if x)))
        L.append('')
    if skip:
        L += ['## 不出图的（页面照旧是字框）', '']
        for k, v in sorted(skip.items()):
            L.append('- `%s`：%s' % (k, v))
        L.append('')
    if doubt:
        L += ['## 拿不准的（审过放行了，留给人看）', '']
        for k, v in sorted(doubt.items()):
            L.append('- `%s`：%s' % (k, v))
        L.append('')
    open(os.path.join(DOC, '进度.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
    print('进度：出了 %d／%d，审过 %d，没审 %d，没出 %d，重画过 %d 张' % (len(have), len(dr), len(ok), len(pend), len(left), len(redo)))


def batchsheet(n, ids, items):
    """一批的总览：缩略图排成格子，下头写 id，存 截图/批次_<n>.jpg"""
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 15)
    have = [k for k in ids if os.path.exists(os.path.join(OUT, k + '.png'))]
    cols, cw, ch, cap, g = 10, 300, 300, 24, 8
    rows = max(1, (len(have) + cols - 1) // cols)
    out = Image.new('RGB', (cols * cw + (cols + 1) * g, rows * (ch + cap) + (rows + 1) * g), (28, 30, 42))
    d = ImageDraw.Draw(out)
    for j, k in enumerate(have):
        x, y = g + (j % cols) * (cw + g), g + (j // cols) * (ch + cap + g)
        im = Image.open(os.path.join(OUT, k + '.png')).convert('RGB')
        im.thumbnail((cw, ch), Image.LANCZOS)
        out.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
        d.text((x + 2, y + ch + 3), k, font=font, fill=(220, 216, 200))
    os.makedirs(SHOT, exist_ok=True)
    pth = os.path.join(SHOT, '批次_%s.jpg' % n)
    out.save(pth, 'JPEG', quality=80)
    print(pth, out.size, os.path.getsize(pth) // 1024, 'KB')


def review_sheet(ids, items, path, w=900):
    """给审图看的：一张一张按原尺寸缩到 w 宽，旁边不写字（原文另给）。每张存一份 jpg，回路径。"""
    from PIL import Image
    os.makedirs(path, exist_ok=True)
    out = []
    for k in ids:
        src = os.path.join(OUT, k + '.png')
        if not os.path.exists(src):
            continue
        im = Image.open(src).convert('RGB')
        im.thumbnail((w, w), Image.LANCZOS)
        q = os.path.join(path, k + '.jpg')
        im.save(q, 'JPEG', quality=86)
        out.append(q)
    return out


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'list':
        write_list()
        sys.exit()
    items = load_items()
    if cmd == 'gen':
        gen(pick_ids(sys.argv[2:], items), items)
    elif cmd == 'mark':          # mark ok <id…> [--why 拿不准的话]   mark redo <id…> --why 缘故
        a = sys.argv[3:]
        why = a[a.index('--why') + 1] if '--why' in a else ''
        ids = [x for x in a[:a.index('--why')]] if '--why' in a else a
        mark(ids, why, sys.argv[2])
    elif cmd == 'progress':
        progress(items)
    elif cmd == 'batchsheet':
        batchsheet(sys.argv[2], pick_ids(sys.argv[3:], items), items)
    elif cmd == 'reviewjpg':     # reviewjpg <目录> <id…>：给审图的出 900 宽的 jpg
        print('\n'.join(review_sheet(pick_ids(sys.argv[3:], items), items, sys.argv[2])))
    elif cmd == 'captions':      # captions <id…>：审图用的单子（id、书、画法、原文）
        byid = {i['id']: i for i in items}
        for k in pick_ids(sys.argv[2:], items):
            i = byid[k]
            print('%s｜%s《%s》%s｜%s%s｜%s' % (k, i['厅名'], i['书名'], i['label'], i['画法'], STYLES[i['画法']]['name'], i['原文']))
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
