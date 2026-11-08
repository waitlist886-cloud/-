#!/usr/bin/env python3
# 各时段的风尚进提示词（11-07）。查图查出来两万年的衣裳糊成一件立领一排扣的呢子长外套，根子之一是出图脚本从来没用风尚文档，
# 四纪老纪共用一句“照欧洲中世纪和文艺复兴剪裁、一排圆扣”。这里按页认时段，给三样：
#   doc(set, en)    风尚文档那一段末尾的英文 prompt（底稿/立绘/各时代风尚_*.md，运行时读，改文档就跟着变）
#   cut(set, en)    这一段的剪裁和扣法，顶替 GUARD 里中世纪那一句
#   magic(set, en)  这一段的奇幻那一层（用户 11-07：注意奇幻魔幻 JRPG 这些元素，尽量别纯中世纪）
#   python era_fashion.py          逐页打印认到的时段，查有没有落空
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, '..', '..', '立绘')
LEAD = ('This is high-fantasy Japanese RPG character design, not a historical costume study: clear readable shapes, one or two striking designed details, '
        'and the magic of this world visible on the clothes and gear. ')
USE = "Period fashion, use only the pieces that fit this character's role, station and side: "

# 页 → 时段（风尚文档的小标题打头的字），每段一句剪裁、一句奇幻
PERIODS = {
    '祭火': dict(head='祭火', cut='Everything is sewn with bone needles and rawhide: wrapped, tied and laced hide, fur and felt, fastened with thongs and bone pins; there are NO buttons and NO tailored collars anywhere.',
               magic='Mythic ice-age fantasy: a small clay fire-pot with a live ember worn at the neck like a sacred jewel, shards of pale silver sewn on as wards, charms of beast tooth, burnt-in runes on the hide that glow like embers.'),
    '万兽前': dict(head='万兽·前', cut='Straight-cut tunics, felt robes and whole pelts, belted with wide leather and fastened with antler toggles, bone pins and big bronze or gold brooches; NO rows of small buttons and NO tailored coats.',
               magic="Beast-slayer fantasy: the pelt of a slain monster still crackles with that beast's element (frost, thunder, flame), a glowing beast-core set in the crown, clasp or weapon, bone charms cut with runes."),
    '万兽中': dict(head='万兽·中', cut='Straight-cut wool tunics and indigo over-robes, wide belts, black iron mountain-shaped clasps, twisted arm rings, gold-thread woven panels; fastened with clasps and lacing, NO rows of small buttons and NO tailored coats.',
               magic='Hall-age fantasy: arm rings and clasps with a faint core-light in them, gold thread woven as wards that catches light by itself, beast-core charms, weapons with a thin line of elemental glow.'),
    '万兽后': dict(head='万兽·后', cut='National colours on straight-cut wool: split riding tunics, short riding skirts, indigo cloaks with white antlers, sharkskin and boiled leather armour; fastened with cast clasps, pins and lacing. NO steel plate armour, NO rows of small buttons, NO tailored coats.',
               magic='Small-kingdom fantasy: pearls that glow at night sewn on sharkskin, a burnt-in running-horse sigil that flickers, rune-glazed ceramic helms, indigo that shimmers like deep water, beast-core jewels.'),
    '晨祷': dict(head='晨祷', cut='Belted tunics and long robes of undyed coarse cloth, thick wool cloaks, cast bronze breast crests; fastened with brooches, lacing and a few big toggles; NO rows of small buttons and NO tailored coats.',
               magic='Early age of gods: crowns and brooches set with the glowing core of a slain beast, altar-blessed white cords that shine softly, candle-flame miracle light on priests.'),
    '午祷上': dict(head='午祷（上）', cut='Belted tunics, hooded travelling cloaks, hardened-leather jerkins and purple or madder-dyed robes; fastened with brooches, buckles and lacing; NO rows of small buttons and NO tailored coats.',
               magic='Early jewel age: bought gems ringed around a thunder-purple beast-core that still sparks, copper rings that hum, charms blessed at an altar.'),
    '午祷下': dict(head='午祷（下）', cut='Deep ruby-red and pale blue dyed wool, belted long tunics and surcoats, branded city crests on leather; fastened with brooches, buckles and lacing; NO rows of small buttons and NO tailored coats.',
               magic='Jewelled age: crowns crowded with rubies and pale star-stones that hold a soft inner light (pawned ones leave empty settings), gem-set brooches, faint glow in city crests.'),
    '晚祷上': dict(head='晚祷（上）', cut="Surcoats over mail and engraved plate, crests branded or embroidered large on the chest, white and gold of the sun kingdom; fastened with buckles and straps; NO rows of small buttons.",
               magic='War of the seven kings: engraved plate with sun-rays that catch a holy light, crowns engraved with one city gate, blessed banners, a miracle-glow on the sworn knights.'),
    '晚祷下': dict(head='晚祷（下）', cut='Deep lake-blue robes with a ring of embroidered water at the cuffs, silk ribbons, tower shields painted with a lake and stars; fastened with sashes, clasps and lacing; NO rows of small buttons.',
               magic='Treaty age: embroidered water at the cuffs that seems to ripple with light, oath-marks that glow when sworn on, pale star motifs on shields.'),
    '夜祷': dict(head='夜祷', cut='Heavy gilded breastplates, black velvet robes, chains of coin-weight silver, patched labourers\' leather; fastened with buckles, chains and clasps; NO rows of small buttons.',
               magic='Silver-gilt twilight: crowns and armour plated in cold pale silver with a faint chill shine, throne-hall gold, beast bones carved as charms, a thin sickly glow on the riches.'),
    '崛起上': dict(head='崛起（上）', cut='Bronze-coloured wolf-hide armour and plain grey wool robes, belted tunics; fastened with clasps, buckles and lacing; collars soft and folded; NO rows of small buttons.',
                magic='Dawn of a magic kingdom: a bone-silver inscribed ring on the hand of every trained mage, scale armour dusted with pale silver that flashes cold, a seven-ring wall sigil burnt into leather, cold white spell-light (never smoke, never electric).'),
    '崛起下': dict(head='崛起（下）', cut='Undyed wool, leather aprons, polished brass fittings, white and gold plate of the new legions; fastened with brass buckles and clasps; collars soft and folded; only a few big buttons.',
                magic='Rising tower age: bone-silver rings and rune-cut bracers, sun-wheel shields that shine with spell-light, the ring-of-fire and crossed-keys emblem appearing, cold white spell-light (never smoke, never electric).'),
    '帝国': dict(head='帝国', cut='White plate engraved with the ring of fire and two crossed keys, white satin and ivory robes, long deep-coloured wool with key-shaped clasps and ring-shaped collars at court; NO rows of small plain buttons.',
               magic='Golden high-magic empire: bone-silver thread that glows faint cold white, halberds tipped in cold pale silver, small floating rings of rune-light around mages, everything luminous and white.'),
    '魔族之世': dict(head='魔族之世', cut='Fine dyed wool and linen, almost colourless white satin at court with ring-shaped collars and key-shaped clasps, wooden registry tags on a cord for the horned; fastened with clasps and sashes; NO rows of small plain buttons.',
                 magic='Brightest age of the empire: bone-silver thread that glows faint cold white inside the towers, spell-lit lamps, registry tags with a burnt-in rune; cold white spell-light (never smoke, never electric).'),
    '末年上': dict(head='末年（上）', cut='Faded grey legion cloaks and worn crests, estate colours on over-robes, white satin court robes with ring-shaped collars and key-shaped clasps; fastened with clasps and sashes; NO rows of small plain buttons.',
                magic='Late empire: bone-silver embroidery with a cold white glow, house colours woven with faint rune lines, spell-lit key clasps, worn crests whose light has gone dull.'),
    '末年下': dict(head='末年（下）', cut='Floor-length white satin and ivory wool, near-black wine-red linings and overgowns, stiff ring-shaped collars, key-shaped clasps, heavy cold-silver embroidery; grey robes below; NO rows of small plain buttons.',
                magic='Final banquet of a luminous empire: heavy bone-silver embroidery that glows cold white, glass ornaments, rings of rune-light; cold white spell-light (never smoke, never electric).'),
    '灰': dict(head='灰的年月', cut="The fallen empire's leftovers: long robes and fine cloaks cut short at the hem for walking, frayed and gone grey with ash, oversized hand-me-down coats, oiled sheepskin, half-armour with its crest scraped off; collars soft and folded down, fastened with lacing, belts and a few mismatched buttons.",
             magic='Ruined high magic: bone-silver thread gone dull but still faintly alive in places, a cracked core lamp, drafting pens and old tower sigils, ash that never quite settles.'),
    '白石': dict(head='白石的年月', cut='Full plate polished bright with crests chiselled fresh, worn leather with the dawn crest stitched on the chest, rune-chiselled aprons, scale-pattern leather; fastened with straps and buckles; collars low; NO rows of small buttons.',
               magic='Age of crests: dwarven runes on shovels and aprons that glow when they strike, shields with a sunrise that catches real light, dark plate dusted with silver that flashes cold in the charge.'),
    '灯': dict(head='灯的年月', cut="Sturdy handed-down garrison gear: resized family leather armour with re-stitched shoulders, quarrymen's smocks, surcoats in the three kingdoms' colours (white, deep blue, wheat yellow), a wall coat brushed clean with an iron tag; collars folded down, fastened with straps and buckles.",
             magic='First millennium on the wall: wards stitched in thread on cloth, lanterns and candles with a steady miracle light, palms that shine for healers, rune-cut iron tags, the first enchanted plates.'),
    '炮': dict(head='炮的年月', cut='The prestige look is work gear: heavy leather forge aprons pocked with spark holes over coarse wool, smoked mica goggles, grey issue coats, canvas and chest-plates with rivets; fastened with straps, buckles and big rivets; collars low.',
              magic='Magitech age of workshops: enchanted iron with engraved rune lines that glow along the seams, fist-sized magic crystals and furnace cores that shine through cracks and grilles, crystal-core cannons with rune-cut barrels (never gunpowder), brass tools humming.'),
    '浮塔': dict(head='浮塔的年月', cut='Plain grey wool issue coats from common guard to emperor, elbows thinned and cuffs scorched, tower crews with thread stripes on the sleeve and soft-soled shoes, deep fleet blue; fastened with straps, belts and plain buttons; collars low or folded.',
               magic='Sky-tower age: chips of floating stone sewn into gear that drift a little, magic-crystal matrices on bracers and belts, rune lines on steam-armour plates, glowing crystal cases at the hip; demon clans each with their own blood-red, copper or bone sorcery.'),
    '铁狼': dict(head='铁狼的年月', cut='Function coded by sewn marks: plain grey-blue tunics with circles or stripes at the cuff, scouts with bound trouser legs, corps uniforms where the full dress is the same thing with every button done up and the helm under the arm; fastened with straps and buckles.',
               magic='Death-frontier magitech: spell-corps uniforms with engraved circuit lines that glow at the cuff, clockwork keys and small wind-up mechanisms on the belt, mica-shielded lamps, bracers set with crystal, bone charms of the wolf-makers on the demon side.'),
    '号角': dict(head='号角的年月', cut='Worn, patched, inherited gear: dark leather brigandines with one polished shoulder guard, riveted mail, oilcloth, wide belts, travelling clothes above uniforms; fastened with buckles, laces and mismatched fittings; collars open or folded.',
               magic='Last centuries of the war: old enchanted plates whose rune lines have dimmed but still flicker, salvaged crystals set in repaired gear, family charms, a horn or a medal with a faint spell on it.'),
    '犁': dict(head='犁的年月', cut='Demobilised wall-issue wool coats worn down the wall, unbleached linen, oilcloth, newly sewn company flags; collars open or folded down, fastened with mismatched buttons, buckles and laces; the plain-folk colours are undyed and muted.',
             magic='First peace after the war: dimmed rune plates reused as tools, a rune lantern, a wind-up machine part turned into a charm, the wall-oath burnt into a leather tag; from year 40 the upper city carries rune-engraved spell-gun wands at the hip.'),
    '长夜': dict(head='长夜的年月', cut='Long aristocratic peace: tall-house nobles in white gloves and long fitted coats of old military cut with the collar folded back, grey-dress maids with white caps, northern wolf pelts and red wool; common folk open-collared.',
               magic='Stagnant golden peace: rune-engraved spell-gun wands at noble hips, gem-set glove clasps with soft light, northern frost charms, a sword-oath mark, ruin-salvaged trinkets that glow.'),
    '白鸦': dict(head='白鸦的年月', cut='Golden age of mercenary companies: company badges sewn on the left chest, wall-family crests on the back and shields, red and gloved night-houses in the west; collars open or folded in the east, buttoned to the throat only in the west.',
               magic='Companies and ruins: charms and blades salvaged from sunken towers that still glow, rune-lit company badges, spell-gun wands on rich hips, blood-red rune thread on the night-houses.'),
    '黎明': dict(head='黎明的年月', cut="A commoner empress's new dynasty: military austerity in white-gold and old copper with no gilding, service coats with torn-off collar tabs, guild short coats; the west in deep grey and black gloves buttoned to the throat.",
               magic='New dynasty: plain old-copper fittings that hold a warm glow, the law-mark and oath-seals in faint light, ember-marked gloves and blood-script in the west, salvaged crystal lamps.'),
    '七城': dict(head='七城的年月', cut="Seven new cities in the demon west, each its own look and colour (forged dark iron and ember for the horn city, thorn-red for the red garden, bone white for the bell tomb, mirror violet, black wings, storm blue, deep-tide blue), black court robes in the east.",
               magic="Each city's sorcery worn openly: seams that glow like cooling lava, thorns with living red light, bone-silver bells, mirrored shards, wing-crests, stormlight in the metal, tide-glow; in the east law-seals with a faint light.",),
    '麦': dict(head='麦的年月', cut='An armed peace: the west in black and dark red long coats buttoned to the throat, contract-court red cords, wooden contract tags, single-shot firearms; the east in grey-brown wool garrison coats with open collars.',
             magic='Contract sorcery: red cords and seals that glow with a binding light, black iron with ember-lit lines, boundary-stone charms of white and black, furnace-lit fittings; the east keeps rune-engraved spell-guns.'),
    '探井': dict(head='探井的年月', cut='Veterans still in wall-issued grey wool with insignia unpicked, a white-stone seal on a cord, rope wound at the waist and wrist; collars folded down or open, fastened with mismatched buttons, buckles and laces.',
               magic='First descent into an endless dungeon: a white-stone seal with a faint inner light, strange glowing fungus-dye and dungeon-beast scraps on the gear, a knotted rope with luminous thread, a lantern with a captured wisp.'),
    '共约': dict(head='共约的年月', cut='Frontier boom around a dungeon city: patched leather coats and canvas, bronze plates, patches worn with pride, a mountain-copper round seal; collars open or folded; fastened with buckles, laces and big buttons.',
               magic='Dungeon loot in everyday gear: monster-hide patches with a sheen, dungeon-crystal lamps, rune-knotted rope, a copper seal with the guild scale that warms to the touch, charms from lower floors.'),
    '繁荣': dict(head='繁荣的年月', cut='Golden age of dungeon wealth: bronze rank emblems pinned on the chest, academy coats, windproof hoods, ribbons and silk cords, coloured fabrics at last; collars folded or open except in the west.',
               magic='Rank emblems (star, campfire, wing) that shine by themselves, academy coats with rune embroidery, dungeon-crystal jewellery, spell-lit ribbons; in the west the first electric lamps and workwear with copper coils.'),
    '深井': dict(head='深井的年月', cut='Prosperous magic-industrial age, everyone in a uniform: each guild and trade its own deep teal, navy or violet long coat or robe, stand collars now normal, rented dress wear; fastened with buttons and clasps.',
               magic='Glowing deep-seals, power cells worn on the back with crystal indicator lights, electro-mechanical limbs where the page names them, rune-printed badges, fog-gate charms.'),
    '黑潮': dict(head='黑潮的年月', cut='A long war against monster tides: mismatched pieced armour, blue cloth strips tied on the arm, issue coats, shared anti-ether cloaks, repairs on repairs; fastened with straps, buckles and wire.',
               magic='War-seals that burn with a blue light, anti-ether cloaks with a faint shimmer, runes scratched by hand into pieced plate, salvaged crystal cores, signal horns and smoke flasks with sorcery in them.'),
    '垂暮': dict(head='垂暮的年月', cut='Post-war recovery: war surplus retired and mended, boiled-leather jerkins, oilcloth short coats, grey-blue rescue jackets; in the cities the first fitted dark tailored coats with waistcoats and stand collars.',
               magic='Dimming war-seals, bronze guild emblems with a soft light on cords, mended rune plate, brass goggles and tools with small crystal cores, old war charms kept as mementoes.'),
}


def _page(en):
    m = re.match(r'[a-z]+\d*[a-z]?', en.split('_')[0])
    return en.split('_')[0]


def period_of(setn, en):
    p = _page(en)
    m = re.match(r'([a-z]+)(\d+)', p)
    if not m:
        return None
    pre, n = m.group(1), int(m.group(2))
    if setn == '月银纪史诗':
        return '祭火' if n == 1 else '万兽前' if n <= 6 else '万兽中' if n <= 9 else '万兽后'
    if setn == '诸国期':
        return ['晨祷', '午祷上', '午祷下', '晚祷上', '晚祷下', '夜祷'][n - 1]
    if setn == '萨尔维斯':
        return ['崛起上', '崛起下', '帝国', '魔族之世', '末年上', '末年下'][n - 1]
    if setn == '纷争纪':
        return {1: '灰', 2: '白石', 3: '灯', 4: '炮', 5: '浮塔', 6: '铁狼', 7: '号角'}[n]
    if setn == '山铜纪':
        return {1: '犁', 2: '长夜', 3: '白鸦', 4: '黎明', 5: '七城', 6: '麦'}[n]
    if setn == '前传':
        return {1: '探井', 2: '共约', 3: '繁荣', 4: '深井', 5: '黑潮', 6: '垂暮'}[n]
    return None


_docs = None


def _load():
    global _docs
    if _docs is not None:
        return _docs
    docs = {}
    for fn in ('各时代风尚_旧三纪.md', '各时代风尚_新三纪.md'):
        head = None
        lines = open(os.path.join(DOC, fn), encoding='utf-8').read().split('\n')
        for i, l in enumerate(lines):
            if l.startswith('#'):
                head = l.lstrip('# ').strip()
            if l.startswith('prompt:'):
                t = l[len('prompt:'):].strip()
                j = i + 1
                while not t and j < len(lines):
                    t = lines[j].strip()
                    j += 1
                docs[head] = t
    _docs = docs   # 读完才放出去，多线程不会读到半张表
    return _docs


def doc(setn, en):
    p = period_of(setn, en)
    if not p:
        return ''
    h = PERIODS[p]['head']
    for k, v in _load().items():
        if k.startswith(h):
            return v
    raise KeyError('风尚文档里找不到 ' + h)


def cut(setn, en):
    p = period_of(setn, en)
    return PERIODS[p]['cut'] if p else ''


def magic(setn, en):
    p = period_of(setn, en)
    return PERIODS[p]['magic'] if p else ''


def block(setn, en):
    """整段接进提示词的话。1001 那一套不走这里。"""
    p = period_of(setn, en)
    if not p:
        return ''
    return LEAD + USE + doc(setn, en) + ' Fantasy layer of this period: ' + magic(setn, en) + ' Cut and fastenings of this period: ' + cut(setn, en) + ' '


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for setn, pages in [('月银纪史诗', ['ge%d' % i for i in range(1, 16)]), ('诸国期', ['zg%d' % i for i in range(1, 7)]), ('萨尔维斯', ['sa%d' % i for i in range(1, 7)]),
                        ('纷争纪', ['z1', 'z2', 'z3', 'z4a', 'z4b', 'z4c', 'z5a', 'z5b', 'z5c', 'z6a', 'z6b', 'z7']),
                        ('山铜纪', ['s1', 's2a', 's2b', 's3a', 's3b', 's4a', 's4b', 's4c', 's5a', 's5b', 's6a', 's6b']),
                        ('前传', ['q1', 'q2', 'q3', 'q4a', 'q4b', 'q5a', 'q5b', 'q6'])]:
        for p in pages:
            en = p + '_x'
            d = doc(setn, en)
            print(setn, p, period_of(setn, en), len(block(setn, en)), d[:48])
