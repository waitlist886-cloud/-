# 原神画法试验：浮雕当骨架图生图，和直接文生图对照。style_test.py <输出目录> <right|left>
import io
import json
import os
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, r'E:\aldran_art\底稿\状态栏\comfy')
import comfy_run as C
import numpy as np
from PIL import Image

OUT, which = sys.argv[1], sys.argv[2]
SP = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)
info = json.load(open(os.path.join(C.HERE, 'object_info.json'), encoding='utf-8'))
cfg = json.load(open(os.path.join(C.HERE, 'plan_maze1001.json'), encoding='utf-8'))['config']


def skeleton(path, side):
    """把石板从白底或黑底里裁出来，靠窗那一边对齐，外侧用石板的平均色补满 512×1024。"""
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(float)
    corner = a[:8, :8].reshape(-1, 3).mean(axis=0)
    diff = np.abs(a - corner).max(axis=2) > 40
    cols = np.where(diff.mean(axis=0) > 0.5)[0]
    rows = np.where(diff.mean(axis=1) > 0.3)[0]
    box = (int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1)
    crop = im.crop(box)
    s = 1024 / crop.height
    crop = crop.resize((min(512, int(crop.width * s)), 1024), Image.LANCZOS)
    out = Image.new('RGB', (512, 1024))
    gap = 512 - crop.width
    if side == 'right':
        out.paste(crop, (0, 0))
        out.paste(crop.crop((crop.width - gap, 0, crop.width, 1024)).transpose(Image.FLIP_LEFT_RIGHT), (crop.width, 0))
    else:
        out.paste(crop, (gap, 0))
        out.paste(crop.crop((0, 0, gap, 1024)).transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
    print('石板', box, '放大后宽', crop.width)
    return out


PRE = "score_9, score_8, newest, year 2025, safe, anime, masterpiece, best quality, highres, official art, "
NEG = ("lowres, worst quality, low quality, blurry, watermark, signature, text, logo, picture frame, border, score_1, score_2, score_3, score_4, photorealistic, photo, 3d render, realistic shading, "
       "stone texture, statue, sculpture, relief, heavy rendering, nsfw, explicit, nude, extra limbs, bad anatomy, deformed, moon phases, crescent moon, white background, bright background, cream background")
STYLE = ("A stylized 2D storybook game event illustration with bold flat color shapes and big sweeping curves, in a limited palette of deep navy and indigo blue, soft violet and pale cream gold, on a dark night-blue ground. "
         "Visible grainy print texture and dry brush strokes on every color area, thin luminous colored rim lines along the edges of forms, soft glowing light, translucent overlapping layers. "
         "Figures are drawn with simple clean shapes and minimal facial features, eyes half closed. Round ornamental halos, thin gold arcs, four-pointed sparkle stars, floating orbs and small glowing white flowers. ")
SCENE = {
    'right': ("A tall vertical crowd of overlapping figures, each in a different action, all in side profile facing left, toward a bright light beyond the left edge of the picture. "
              "At the top a winged goddess with wild golden hair flies forward and draws a bow aimed left. Below her a red-haired duke in a long robe thrusts a staff to the left, his wings made of flame and frost. "
              "Behind them a colossal god, half of his body grey rock, with wings of layered stone ridges, grips a great hammer. A smiling blonde goddess tosses a gold coin to the left, a black cat on her shoulder. "
              "A small girl with little fawn antlers and vines holds out a sheaf of wheat. A small green-haired healer with tiny wings on her head kneels with her hands at her chest. A calm man in a plain hooded robe rests one hand on his sword. "
              "In the foreground at the bottom, largest of all, two queens stride to the left: the nearer queen with auburn hair in a braided bun, a small gold crown, white and gold armor and a cape raises a long sword, "
              "the other queen with very long silver hair, a large black ribbon and a small red mark on her forehead, in a crimson and black long coat, stretches out a gold scepter."),
    'left': ("A tall vertical scene, every motion directed to the right, toward a bright light beyond the right edge of the picture. "
             "At the top a black sun with a pale gold corona, and a vast faceless shadow of violet smoke rising from below, long tendrils and one huge hand reaching to the right. "
             "In the middle a colossal labyrinth in concentric rings descending like a well, with gothic spires and arched bridges and a glowing gold spiral stairway winding down. "
             "Small cloaked adventurers climb the stairs, each in a different action, raising lanterns and shields. In the foreground at the lower right a lone cloaked traveler on a rocky ledge, seen from behind, cape flowing, raises a staff with a small light toward the right."),
}
SKEL = {'right': os.path.join(SP, 'relief2', 'right_44.png'), 'left': os.path.join(SP, 'relief2', 'left_33.png')}
sk = skeleton(SKEL[which], which)
skp = os.path.join(OUT, '_skeleton_%s.png' % which)
sk.save(skp)
up = {'init': C.upload(skp, 'style_skeleton_%s.png' % which)}
TRIES = [('i85', 0.85, up), ('t2i', 1.0, {})]
ims, names = [], []
for tag, d, u in TRIES:
    for seed in (2, 3, 4):
        job = dict(gen=[512, 1024], final=[512, 1024], prompt=STYLE + SCENE[which], negative=NEG, prompt_prefix=PRE, steps=28, denoise=d, hires=0)
        hist, secs = C.queue_and_wait(C.build(info, cfg, job, seed, u, 'aldran/style_%s' % which))
        im = Image.open(io.BytesIO(C.fetch_images(hist)[0])).convert('RGB')
        name = '%s_%s_%d.png' % (which, tag, seed)
        im.save(os.path.join(OUT, name))
        ims.append(im)
        names.append(name)
        print(name, '%.0f 秒' % secs, flush=True)
sheet = Image.new('RGB', (sum(i.width for i in ims) + 10 * (len(ims) - 1), ims[0].height), (20, 20, 24))
x = 0
for im in ims:
    sheet.paste(im, (x, 0))
    x += im.width + 10
sheet.save(os.path.join(OUT, '_sheet_%s.jpg' % which), quality=90)
print('顺序', names)
