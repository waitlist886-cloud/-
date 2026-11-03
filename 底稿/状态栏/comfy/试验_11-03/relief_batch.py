# 浮雕构图批量试：relief_batch.py <输出目录> <right|left> <种子,种子>
import io
import json
import os
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, r'E:\aldran_art\底稿\状态栏\comfy')
import comfy_run as C
from PIL import Image

OUT, which, seeds = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')]
os.makedirs(OUT, exist_ok=True)
info = json.load(open(os.path.join(C.HERE, 'object_info.json'), encoding='utf-8'))
cfg = json.load(open(os.path.join(C.HERE, 'plan_maze1001.json'), encoding='utf-8'))['config']
PRE = "score_9, score_8, newest, year 2025, safe, masterpiece, best quality, highres, absurdres, intricate details, "
NEG = ("lowres, worst quality, low quality, blurry, watermark, signature, text, logo, picture frame, score_1, score_2, score_3, score_4, flat color, vector art, cel shading, line art, colorful, "
       "nsfw, explicit, nude, bare chest, extra limbs, bad anatomy, deformed, sky, clouds, white background, isolated on white, crescent moon, moon phases, perspective, building, tower, pillar, column, side wall, doorway arch, outdoor, ground, floor, plinth")
STONE = ("Straight-on frontal view, flat orthographic close-up of a high relief carved from blue-grey pietra serena stone with gilded gold leaf details, in the manner of Francois Rude and Donatello. "
         "The carving covers the whole image from edge to edge, cropped by the image borders, the figures and carved stone ground continue past every edge. Soft raking light comes from the left. Grey stone and gold only. ")
PROMPTS = {
    'right': STONE + ("A tall vertical crowded group of overlapping figures climbing the wall, each in a different action, every face, gesture and weapon directed to the left, toward a shared center outside the picture. "
                      "At the very top a winged goddess with wild windblown hair flies forward and draws a gilded bow aimed to the left, her huge feathered wings spread behind her. "
                      "Below her a stern duke with a long robe thrusts a gilded staff to the left, his wings carved with flames, frost and lightning. "
                      "Behind them a colossal god, half of his body still raw rock merging into the wall, with wings of layered stone ridges, braces his shoulder against the wall and grips a great hammer. "
                      "A smiling goddess tosses a gilded coin to the left with a small cat on her shoulder. A small girl with little fawn antlers and vines in long robes holds out a sheaf of wheat to the left. "
                      "A small gentle goddess with tiny wings on her head kneels in profile with her hands at her chest, facing left, feathers falling. A calm man in a plain hooded robe stands with one hand on his sword hilt, looking left. "
                      "In the foreground at the bottom, largest of all, two queens in profile stride to the left: the nearer queen in plate armor and a cape with her hair in a braided bun and a small gilded crown raises a long sword forward, "
                      "the other queen with very long hair and a large ribbon, in a high collared long coat, stretches out a gilded scepter. Flowing carved drapery, deep undercut shadows."),
    'left': STONE + ("A tall vertical carved scene, every figure and motion directed to the right, toward a shared center outside the picture. "
                     "At the top a black obsidian sun disc ringed with gold, and a vast faceless giant of carved smoke and tendrils rising from below, its tendrils and one huge hand reaching out to the right. "
                     "In the middle a colossal labyrinth carved in concentric rings descending like a well, with gothic spires and arched bridges and a gilded spiral stairway winding down. "
                     "Small adventurers in cloaks climb and fight on the stairs and bridges, each in a different action, some hauling ropes, some raising lanterns and shields. "
                     "In the foreground at the lower right a lone cloaked traveler on a rocky ledge, seen from behind, cape flowing, raises a gilded staff toward the right. Deep undercut shadows."),
}
ims = []
for seed in seeds:
    job = dict(gen=[512, 1024], final=[512, 1024], prompt=PROMPTS[which], negative=NEG, prompt_prefix=PRE, steps=28, denoise=1.0, hires=0)
    hist, secs = C.queue_and_wait(C.build(info, cfg, job, seed, {}, 'aldran/relief_%s' % which))
    im = Image.open(io.BytesIO(C.fetch_images(hist)[0])).convert('RGB')
    p = os.path.join(OUT, '%s_%d.png' % (which, seed))
    im.save(p)
    ims.append(im)
    print(which, seed, '%.0f 秒' % secs, flush=True)
sheet = Image.new('RGB', (sum(i.width for i in ims) + 10 * (len(ims) - 1), ims[0].height), (20, 20, 24))
x = 0
for im in ims:
    sheet.paste(im, (x, 0))
    x += im.width + 10
sheet.save(os.path.join(OUT, '_sheet_%s.jpg' % which), quality=90)
