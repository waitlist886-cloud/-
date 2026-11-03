# 精修版重绘试验：双王那一块，从 Turbo 拼的和 GPT 的各走一遍，看能不能又干净又不腻
import io
import os
import sys
import time
sys.path.insert(0, r'E:\aldran_art\底稿\状态栏\comfy')
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import kit
import comfy_run as C
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clean1')
os.makedirs(OUT, exist_ok=True)
ROOT = r'E:\aldran_art\底稿\状态栏\comfy\out\四方_11-03'
EXT = os.path.join(ROOT, '外部试图')
W, H = 768, 832
# 右扇下半，双王
tb = Image.open(os.path.join(EXT, '参考_右扇构图.png')).convert('RGB')
tb = tb.crop((0, 640, tb.width, 1400)).resize((W, H), Image.LANCZOS)
tb_p = os.path.join(OUT, 'src_turbo.png')
tb.save(tb_p)
gp = Image.open(os.path.join(ROOT, 'gpt', 'right.png')).convert('RGB')
y0 = int(gp.height * 640 / 1400)
gp = gp.crop((0, y0, gp.width, gp.height)).resize((W, H), Image.LANCZOS)
gp_p = os.path.join(OUT, 'src_gpt.png')
gp.save(gp_p)


def lines(src, dst):
    """官方 any-test 模板那一路：Canny 再反相，白底黑线。"""
    if os.path.exists(dst):
        return dst
    g = C.Graph(kit.info())
    li = g.add('LoadImage', image=C.upload(src, 'kit_line_%s' % os.path.basename(src)))
    ca = g.add('Canny', image=[li, 0], low_threshold=0.1, high_threshold=0.3)
    iv = g.add('ImageInvert', image=[ca, 0])
    g.add('SaveImage', images=[iv, 0], filename_prefix='aldran/line')
    imgs, _ = kit._run(g.nodes)
    Image.open(io.BytesIO(imgs[0])).convert('RGB').save(dst)
    return dst


CLEAN = ('official art, game cg, anime coloring, cel shading, flat color, clean thin lineart, detailed face, beautiful detailed eyes, 2girls, two queens seen from the side facing left. '
         'A stern queen in front with dark brown hair with auburn tips in a large braided bun, small spiked gold crown, amber eyes, a scar over one eye, white high collar cape with gold trim, gold epaulettes, gold breastplate, raising a long sword. '
         'Behind her a cold queen with very long straight silver hair, blunt bangs, a side braid, a large black hair bow, pointed ears, gold eyes, a small red mark on her forehead, crimson and black high collar long coat. Deep navy night sky with few stars. Simple, calm, matte, clean shapes.')
NEG = 'sparkle, glitter, light particles, lens flare, bloom, glow, shiny skin, oily skin, metallic texture, realistic, 3d, painterly, western cartoon, text, '
JOBS = [
    ('turbo_d55', tb_p, 0.55, None),
    ('gpt_d55', gp_p, 0.55, None),
    ('gpt_d75_line', gp_p, 0.75, 'gpt'),
    ('turbo_d75_line', tb_p, 0.75, 'turbo'),
]
for name, src, d, ctl in JOBS:
    t = time.time()
    control = None
    if ctl:
        control = (lines(src, os.path.join(OUT, 'line_%s.png' % ctl)), 'any-test', 0.8)
    kit.gen(os.path.join(OUT, name + '.png'), CLEAN, W, H, seed=3, model='aesthetic', negative=NEG, init=src, denoise=d, steps=24, control=control)
    print(name, '%.0f 秒' % (time.time() - t), flush=True)
kit.sheet([tb_p, os.path.join(OUT, 'turbo_d55.png'), os.path.join(OUT, 'turbo_d75_line.png'), gp_p, os.path.join(OUT, 'gpt_d55.png'), os.path.join(OUT, 'gpt_d75_line.png')], os.path.join(OUT, '_sheet.jpg'), h=620)
print('done')
