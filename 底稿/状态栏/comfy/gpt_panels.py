#!/usr/bin/env python3
# 用 GPT 出两扇和楣、座的零件（11-03）。python gpt_panels.py [mid|parts|clean] [名字…]，写 out/四方_11-03/gpt_mid/、gpt_mid/parts/、gpt_clean/。
# 用户说第一版太腻，clean 是往回收的一头（平得像海报，作废），mid 是中间那一档（现行）。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_gen
OUT = os.path.join(HERE, 'out', '四方_11-03', 'gpt_clean')
EXT = os.path.join(HERE, 'out', '四方_11-03', '外部试图')
CLEAN = ('Art direction: a clean official Japanese anime game illustration, drawn with restraint. Thin confident line art of even weight in dark colored ink, not black. '
         'Crisp cel shading: two or three flat tones per surface with clean shadow shapes. A soft gradient only in the hair and the sky. Matte surfaces. Gold is drawn as flat ochre with one simple highlight, never as shiny metal. '
         'Leave large calm areas of plain cloth so the eye can rest; fewer small details, clear readable silhouettes. '
         'Absolutely no sparkles, no glitter, no gold dust, no glowing particles, no lens flare, no bloom, no rim glow, no painterly rendering, no 3D look. No text, no logo, no frame.')
JOBS = {
    'right': ([os.path.join(EXT, '参考_右扇构图.png'), os.path.join(EXT, '参考_巴尔缇娜.png'), os.path.join(EXT, '参考_索恩薇娅.png')],
              'Repaint the first attached image as a tall portrait picture with aspect ratio 1:2. Keep the exact composition: every figure stays in the same place, the same pose and the same direction, all turned to the left. '
              'The second attached image is the exact face, hair and costume reference for the silver-haired queen, with her closed high collar. The third attached image is the exact face, hair and costume reference for the crowned auburn-haired queen with the scar over one eye. '
              'The small goddess holding wheat has small fawn antlers on her head. The goddess with the bow has large white feathered wings. The man in the white hood wears a plain undyed robe with no ornaments. '
              'Sky: a calm plain deep navy night with very few small stars and two or three thin gold arcs. Clouds are simple flat shapes in muted indigo. ' + CLEAN),
    'left': ([os.path.join(EXT, '参考_左扇构图.png')],
             'Repaint the attached image as a tall portrait picture with aspect ratio 2:3. Keep the composition: the black sun with a thin pale gold corona at the top, the vast faceless shadow of violet smoke with its huge clawed hand reaching right, the colossal labyrinth of pale stone in concentric rings going down into a dark abyss, the gold spiral stair, the cloaked traveler seen from behind on the floating rock raising a staff to the right. '
             'Draw the labyrinth as big simple graphic rings with clean line work and deep dark shadow inside the well, so it feels ancient and ominous. No flowers, no trees, no waterfalls, no statues, no banners, no mist everywhere. Limited palette of deep violet, indigo and warm cream with one gold accent. ' + CLEAN),
}
# 中间那一档：干净版平得像矢量海报，上一版又腻，这一版要细线、柔和渐变、看得清的细节，不要闪光
MID = ('Art direction: a polished official illustration from a modern Japanese fantasy anime RPG, the quality of a major game\'s key visual. '
       'Fine, clean, confident line art that varies gently in weight, in dark colored ink rather than black. Refined anime cel shading: clear shadow shapes softened by smooth gradient transitions on skin, hair and cloth. '
       'Beautiful detailed anime faces and eyes. Costumes keep their real design details such as embroidery trim and jewelry, drawn crisply and kept readable, with calm plain areas of cloth between them. '
       'Gold and armor are drawn in crisp anime style with two or three clear tones and one small highlight. A single gentle warm light from the left, with subtle color in the shadows. '
       'Not flat vector art and not simplified TV anime, but also not oily or glossy: no sparkles, no glitter, no gold dust, no floating particles, no lens flare, no bloom, no glowing outlines, no heavy painterly texture, no 3D look. No text, no logo, no frame.')
MID_JOBS = {
    'right': (JOBS['right'][0], JOBS['right'][1].replace(CLEAN, MID).replace('Clouds are simple flat shapes in muted indigo.', 'Clouds are soft anime clouds in muted indigo and cream.')),
    'left': (JOBS['left'][0],
             'Repaint the attached image as a tall portrait picture with aspect ratio 2:3. Keep the composition: the black sun with a thin pale gold corona at the top, the vast faceless shadow of violet smoke with its huge clawed hand reaching right, the colossal labyrinth of pale stone in concentric rings going down into a dark abyss, the gold spiral stair, the cloaked traveler seen from behind on the floating rock raising a staff to the right. '
             'Draw the labyrinth with real architectural detail: weathered pale stone blocks, arcades, stairways and small towers, fading into cool violet haze with distance and falling into real darkness inside the well, so it feels monumental, ancient and ominous. No flowers, no trees, no waterfalls, no statues, no banners. Limited palette of deep violet, indigo and warm cream with one gold accent. ' + MID),
}
# 楣和座的零件照同一档重画，形状照旧，白底好抠
PARTS_DIR = os.path.join(os.path.dirname(OUT), 'parts')
ORN = ('Keep the exact silhouette and layout of every curl, and keep the plain pure white background with nothing else on it. '
       'Same art direction as a polished official Japanese fantasy anime RPG interface ornament: thin clean gold edge lines, smooth soft gradient shading, muted and matte. '
       'No glow, no sparkles, no particles, no thick black outlines, no glossy plastic look, no 3D look, no text, no logo.')
MID_PARTS = {
    'ribbon_top': ([os.path.join(PARTS_DIR, 'navyribbon_62.png')], 'Repaint the attached ornament of sweeping cloud ribbons curling into spirals as a landscape picture with aspect ratio 3:2, in muted deep navy and indigo. ' + ORN),
    'ribbon_bot': ([os.path.join(PARTS_DIR, 'navyribbon_63.png')], 'Repaint the attached ornament of sweeping cloud ribbons curling into spirals as a landscape picture with aspect ratio 3:2, in muted deep navy and indigo. ' + ORN),
    'cloud': ([os.path.join(PARTS_DIR, 'cumulus_53.png')], 'Repaint the attached bank of clouds as a landscape picture with aspect ratio 3:2: soft anime clouds in muted indigo with pale cream light on their tops. Keep the same overall silhouette. Same art direction as a polished official Japanese fantasy anime RPG background: clean soft shapes, smooth gradients, matte. Keep the plain pure white background with nothing else on it. No glow, no sparkles, no particles, no thick outlines, no 3D look, no text, no logo.'),
    'crest': ([os.path.join(PARTS_DIR, 'crest_31.png')], 'Repaint the attached symmetrical golden crest as a landscape picture with aspect ratio 3:2: a large eight pointed star in the center with scrollwork curling out to both sides. Draw the gold in crisp anime style with two or three clear tones and one small highlight, with a few very thin straight lines radiating from the star. ' + ORN),
}
if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'mid'
    table, sub = {'mid': (MID_JOBS, 'gpt_mid'), 'parts': (MID_PARTS, 'gpt_mid/parts'), 'clean': (JOBS, 'gpt_clean')}[which]
    for name in (sys.argv[2:] or table):
        refs, prompt = table[name]
        print(name, gpt_gen.gen(os.path.join(os.path.dirname(OUT), sub, name), prompt, refs=refs), flush=True)
    print('done')
