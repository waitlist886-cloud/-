#!/usr/bin/env python3
# 状态栏背包、装备格用的道具图标和面板正中那个人（11-04）。一张画十二样，切开拼成一张雪碧图，样式按道具名里的字认图标（make_icons.py）。
#   python gpt_icons.py [名字…]   写 out/四方_11-03/icons/，已有的不重出
import os
import sys
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_gen

OUT = os.path.join(HERE, 'out', '四方_11-03', 'icons')
STYLE = ('A sheet of fantasy RPG inventory icons, the kind of item art in a high-end Japanese fantasy action RPG: soft painterly cel shading, crisp clean silhouettes, warm highlights, restrained gold trim, '
         'three-quarter view, every object instantly readable at a very small size, consistent light from the upper left. ')
GRID = ('Landscape picture, aspect ratio 3:2. Exactly twelve separate objects in a perfectly regular grid of 4 columns and 3 rows, in the listed order, left to right, top to bottom. '
        'Each object is centered in its own cell, fills about two thirds of the cell, has empty space all around it and never touches a neighbour. Transparent background. '
        'No text, no labels, no numbers, no frames, no cell borders, no glow halo, no ground shadow, no background colour. ')
SHEETS = {
    'a': ['a one-handed steel sword with a leather-wrapped grip', 'a short dagger', 'a long spear with a leaf blade', 'a single-bladed battle axe',
          'a heavy war hammer', 'a recurve bow', 'a magic staff topped with a blue crystal', 'a round wooden shield with an iron rim',
          'a great two-handed sword', 'a crossbow', 'a long ornate rifle of dark wood and brass engraved with glowing rune circuits', 'a spell book with a gold clasp and a star on the cover'],
    'b': ['a steel plate cuirass', 'a brown leather armour vest', 'a blue cloth robe with gold trim', 'a steel helmet',
          'a pair of leather gloves', 'a pair of worn leather boots', 'a dark hooded cloak', 'a leather belt with a brass buckle',
          'a gold ring with a small red gem', 'a silver necklace with an amulet pendant', 'a round bronze badge with a star emblem', 'a simple linen tunic and trousers, folded'],
    'c': ['a loaf of dark rye bread', 'a strip of dried meat', 'a leather waterskin', 'a small round glass potion bottle with a cork, full of glowing red liquid',
          'a small round glass potion bottle with a cork, full of glowing blue liquid', 'a small round glass potion bottle with a cork, full of glowing green liquid', 'a bundle of dried green herbs tied with string', 'a roll of white linen bandage',
          'an unlit wooden torch wrapped in resin-soaked cloth', 'a small brass oil lantern, softly lit', 'a green glass wine bottle', 'a red apple'],
    'd': ['a rough chunk of iron ore', 'a steel ingot', 'a cluster of glowing cyan magic crystals', 'a small bundle of cut wood',
          'a folded animal pelt', 'a spool of coarse hemp thread', 'an empty small glass vial with a cork', 'a curved monster fang',
          'a large iridescent dragon scale', 'a long white feather', 'a brown forest mushroom', 'a rough grey whetstone'],
    'e': ['a rolled parchment scroll with a red wax seal', 'a folded letter with a small wax seal', 'a thick leather-bound book', 'an old folded map',
          'an ornate brass key', 'a leather coin pouch spilling a few gold coins', 'a small folding pocket knife', 'a ring of thin lockpicks',
          'a plain iron identity tag on a short chain', 'a small ornate treasure casket', 'a plain leather satchel', 'a fragment of an ancient stone tablet with glowing gold runes'],
    # 记忆和见闻各类的小标（11-04）：核心、未结因果、短期、长期、已完成、修正、全部；在办、已知情报、流言风闻、可接、线索
    'f': ['a glowing amber crystal with a tiny golden star sealed inside', 'a tangled knot of crimson thread around a small gold ring', 'a small brass hourglass with softly glowing sand', 'a thick closed leather tome with a red ribbon bookmark hanging out',
          'a round red wax seal stamped with a check mark', 'a white feather quill pen with a single ink drop', 'an open travel journal with handwritten pages', 'an open brass navigator compass',
          'a dark leather dossier folder tied with string', 'a small black raven perched, side view', 'a small wooden hanging notice tag with a red string', 'a magnifying glass with a brass frame'],
}
DOLL = ('A full-body figure of a nameless adventurer standing straight and facing the viewer, gender-neutral, a long hooded travelling cloak falling to the feet, the face fully hidden in the shadow of the hood, hands hidden under the cloak. '
        'Drawn as an elegant emblem from a high-end Japanese fantasy RPG character screen: the whole figure is a deep indigo silhouette with soft inner gradients, thin pale-gold contour lines describing the folds, and a faint constellation of tiny four-pointed stars inside the cloak. '
        'Tall portrait picture, aspect ratio 2:3, the figure fills the height of the picture and is perfectly centered. Transparent background. No text, no frame, no ground, no glow halo, no weapons.')


def job(name):
    os.makedirs(OUT, exist_ok=True)
    if name == 'doll':
        return gpt_gen.gen(os.path.join(OUT, 'doll'), DOLL)
    items = ' '.join('%d. %s.' % (i + 1, t) for i, t in enumerate(SHEETS[name]))
    return gpt_gen.gen(os.path.join(OUT, 'sheet_' + name), STYLE + GRID + 'The twelve objects: ' + items)


if __name__ == '__main__':
    names = sys.argv[1:] or list(SHEETS) + ['doll']
    with ThreadPoolExecutor(3) as ex:
        for n, r in zip(names, ex.map(job, names)):
            print(n, r, flush=True)
