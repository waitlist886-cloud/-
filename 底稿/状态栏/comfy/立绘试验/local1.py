# 本地实测（不占 GPT 额度）：同一位爱丽丝，四条路各一张，比能不能达到定下的画风。
#   a  NoobAI 文生图（人物最干净，但许可证禁止商用）
#   b  Anima 精修文生图（出的图可以商用）
#   c  拿 GPT 的常服当底，Anima 精修图生图 0.35，只看能不能保住画风
#   d  拿 GPT 的常服抽线稿（LLLite lineart），Anima 精修照线重上色，看换衣服、改比例这条路通不通
import os
import sys
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.insert(0, 'E:/aldran_art/底稿/状态栏/comfy')
import kit
from PIL import Image

OUT = 'C:/Users/waitl/AppData/Local/Temp/claude/85a810c2c0993c77/e22307d9-b63e-4d31-ad24-f0ffb0fc6126/scratchpad/hsr/local/'
os.makedirs(OUT, exist_ok=True)
SRC = 'E:/aldran_art/底稿/状态栏/comfy/out/立绘_v2/alice/casual.png'
# GPT 图透明底垫白，模型吃不了透明
base = OUT + 'alice_base.png'
if not os.path.exists(base):
    im = Image.open(SRC).convert('RGBA')
    a = im.getchannel('A').point(lambda v: 0 if v < 72 else min(255, int((v - 72) * 255 / 138)))
    im.putalpha(a)
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
    bg.convert('RGB').resize((768, 1152), Image.LANCZOS).save(base)

TAGS = ('1girl, solo, adult woman, full body, standing, white background, simple background, official art, game cg, anime coloring, soft cel shading, delicate thin lineart, '
        'long brown hair in a thick side braid, large pink ribbon in hair, green eyes, gentle smile, red cropped jacket with short sleeves, long pink dress, layered skirt, sage green sash, leather pouch, brown lace-up ankle boots, '
        'holding a tall wooden staff wrapped with pink ribbon, holding a pink flower, bracelets, long legs, ')
NAT = ('A full-body standing illustration of a grown woman on a plain white background, in a clean modern Japanese anime game style with thin warm-brown lines and soft muted colours. '
       'Long brown hair in one thick side braid with a big pink ribbon, green eyes, gentle smile. She wears a short red cropped jacket over a long pink dress with a layered skirt, a sage green sash, a small leather pouch and brown lace-up ankle boots. She holds a tall wooden staff wrapped in pink ribbon in one hand and a pink flower in the other. Long legs, knees high, fully clothed.')
SEED = 11
jobs = sys.argv[1:] or ['a', 'b', 'c', 'd']
if 'a' in jobs:
    print('a', kit.gen(OUT + 'a_noob.png', TAGS, 832, 1216, seed=SEED, model='noob'), flush=True)
if 'b' in jobs:
    print('b', kit.gen(OUT + 'b_anima.png', NAT, 768, 1120, seed=SEED, model='aesthetic'), flush=True)
if 'c' in jobs:
    print('c', kit.gen(OUT + 'c_i2i.png', NAT, 768, 1152, seed=SEED, model='aesthetic', init=base, denoise=0.35), flush=True)
if 'd' in jobs:
    print('d', kit.gen(OUT + 'd_line.png', NAT, 768, 1152, seed=SEED, model='aesthetic', control=(base, 'any-test', 0.85)), flush=True)
