# 本地第二轮（不占 GPT 额度）：拿 GPT 常服定构图，比各路能不能出崩铁的样子。
#   ctl   Anima preview3 + LLLite any-test，不加风格模型，当对照
#   tag   Anima 精修 + LLLite any-test，提示词里写作品名，看不下载能走多远
#   ntag  NoobAI 图生图 0.55，提示词里写作品名
#   dora  Anima preview3 + HSR2D DoRA + LLLite any-test（要先有文件）
#   nlora NoobAI + Honkai Starrail Style LoRA，图生图 0.55（要先有文件）
#   nfree NoobAI + 同一个 LoRA，文生图，不看构图（要先有文件）
#   dfree HSR2D 开满，文生图，只看画风能到哪儿
#   dctl6 HSR2D 开满，any-test 0.6
#   di2i  HSR2D 开满，图生图 0.5
# 用法：local2.py 输出目录 人(alice|eleanor|...) 路子...
import os
import sys
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.insert(0, 'E:/aldran_art/底稿/状态栏/comfy')
import kit
from PIL import Image

SRC = 'E:/aldran_art/底稿/状态栏/comfy/out/立绘_v2/%s/casual.png'
DORA = ('HSR2D_AnimaV3_DoRA_V2-000065.safetensors', 0.85)
LORA = ('Honkai_Starrail_Style_Lora.safetensors', 1.0)
PEOPLE = {
    'alice': dict(
        nat='A grown woman with long brown hair in one thick side braid and a big pink ribbon, green eyes, gentle smile. She wears a short red cropped jacket over a long pink dress with a layered skirt, a sage green sash, a small leather pouch and brown lace-up ankle boots. She holds a tall wooden staff wrapped in pink ribbon in one hand and a pink flower in the other.',
        tag='1girl, solo, adult woman, mature female, long hair, light brown hair, thick side braid, large pink ribbon, green eyes, gentle smile, red cropped jacket, short sleeves, long pink dress, layered skirt, sage green sash, leather pouch, brown lace-up ankle boots, holding wooden staff, ribbon on staff, holding pink flower, bracelets'),
    'eleanor': dict(
        # any-test 只认线条，颜色全靠这里写；头一版没写颜色，出来一身米色，头一版的 tag 还写了盔甲和手甲，NoobAI 照着添了
        nat='A grown woman, a kingdom knight, tall and dignified, a beautiful mature face with a gentle air. Thick loose wavy locks of soft warm gold hair swept back from the forehead, shifting to pale champagne at the tips, sea-blue eyes. She wears a dark navy high-collared military coat with silver buttons and silver embroidery, a silver braided cord on the shoulder, a dark navy half-cape with a pale blue lining, a brown leather belt, slim dark navy trousers and tall dark brown riding boots. One hand on her hip.',
        tag='1girl, solo, adult woman, mature female, tall, gentle, long wavy hair, blonde hair, gradient hair, hair swept back, forehead, blue eyes, dark blue military uniform, high collar, silver buttons, silver trim, aiguillette, dark blue capelet, blue lining, brown belt, dark blue pants, tall brown boots, hand on hip'),
}
NAT_HEAD = 'A full-body standing illustration on a plain white background, clean modern Japanese anime game style, thin warm-brown lines, soft muted colours, long legs with the knee high. '
TAG_HEAD = 'full body, standing, white background, simple background, official art, game cg, '


def base_of(out, who):
    p = out + who + '_base.png'
    if not os.path.exists(p):
        im = Image.open(SRC % who).convert('RGBA')
        a = im.getchannel('A').point(lambda v: 0 if v < 72 else min(255, int((v - 72) * 255 / 138)))
        im.putalpha(a)
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        bg.convert('RGB').resize((768, 1152), Image.LANCZOS).save(p)
    return p


def b_hi(out, who):
    """GPT 常服垫白，缩到 832×1248。1024×1536 在这张 AMD 卡上解码时驱动报错、ComfyUI 整个退出（11-05 试的）。"""
    p = out + who + '_base_hi.png'
    im = Image.open(p) if os.path.exists(p) else None
    if im is None or im.size != HI:
        im = Image.open(SRC % who).convert('RGBA')
        a = im.getchannel('A').point(lambda v: 0 if v < 72 else min(255, int((v - 72) * 255 / 138)))
        im.putalpha(a)
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        bg.convert('RGB').resize(HI, Image.LANCZOS).save(p)
    return p


HI = (832, 1248)
FACE_BOX = {'alice': (260, 8, 520, 268), 'eleanor': (240, 24, 500, 284)}   # 头在 832×1248 上的位置，先手量
NEG_HI = 'border, hair over one eye, open mouth, teeth, child, loli, aged down, '


def hi_pass(out, who, dst, base, tag, nat2, denoise):
    """原尺寸图生图 + 脸单独放大重绘再贴回。全身图上脸只有两百来像素，SDXL 这个尺寸画不清。"""
    from PIL import ImageDraw, ImageFilter
    p1 = dst[:-4] + '_raw.png'
    kit.gen(p1, tag + ', closed mouth', HI[0], HI[1], seed=11, model='noob', init=base, denoise=denoise, lora=LORA, negative=NEG_HI)
    if os.path.exists(dst):
        return
    x0, y0, x1, y1 = FACE_BOX[who]
    im = Image.open(p1).convert('RGB')
    face = im.crop((x0, y0, x1, y1)).resize((1024, 1024), Image.LANCZOS)
    fp = dst[:-4] + '_face_in.png'
    face.save(fp)
    p2 = dst[:-4] + '_face_out.png'
    kit.gen(p2, 'portrait, face focus, detailed eyes, ' + tag + ', closed mouth', 1024, 1024, seed=12, model='noob', init=fp, denoise=0.38, lora=LORA, negative=NEG_HI)
    w, h = x1 - x0, y1 - y0
    fx = Image.open(p2).convert('RGB').resize((w, h), Image.LANCZOS)
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).ellipse((16, 16, w - 16, h - 16), fill=255)
    im.paste(fx, (x0, y0), m.filter(ImageFilter.GaussianBlur(12)))
    im.save(dst)


def main():
    out = sys.argv[1].rstrip('/') + '/'
    who = sys.argv[2]
    jobs = sys.argv[3:]
    os.makedirs(out, exist_ok=True)
    b = base_of(out, who)
    p = PEOPLE[who]
    seed = 11
    nat = NAT_HEAD + p['nat']
    nat2 = 'A full-body standing illustration on a plain white background. ' + p['nat']   # 不写线条和颜色的要求，留给风格模型
    tag = TAG_HEAD + p['tag']
    for j in jobs:
        f = out + who + '_' + j + '.png'
        if j == 'ctl':
            kit.gen(f, nat, 768, 1152, seed=seed, model='preview3', control=(b, 'any-test', 0.85))
        elif j == 'tag':
            kit.gen(f, 'honkai: star rail, official art, ' + nat, 768, 1152, seed=seed, model='aesthetic', control=(b, 'any-test', 0.85))
        elif j == 'ntag':
            kit.gen(f, 'honkai: star rail, ' + tag, 768, 1152, seed=seed, model='noob', init=b, denoise=0.55)
        elif j == 'dora':
            kit.gen(f, 'HSR2D Style, ' + nat, 768, 1152, seed=seed, model='preview3', control=(b, 'any-test', 0.85), lora=DORA)
        elif j == 'nlora':
            kit.gen(f, tag, 768, 1152, seed=seed, model='noob', init=b, denoise=0.55, lora=LORA, negative='border, ')
        elif j == 'nfree':
            kit.gen(f, tag, 832, 1216, seed=seed, model='noob', lora=LORA, negative='border, ')
        elif j == 'dfree':    # 不看构图，只看 HSR2D 到底把画风带到哪儿
            kit.gen(f, 'HSR2D Style, ' + nat2, 832, 1216, seed=seed, model='preview3', lora=(DORA[0], 1.0))
        elif j == 'dctl6':    # 风格模型开满，构图放松一点
            kit.gen(f, 'HSR2D Style, ' + nat2, 768, 1152, seed=seed, model='preview3', control=(b, 'any-test', 0.6), lora=(DORA[0], 1.0))
        elif j == 'di2i':     # 图生图，颜色从 GPT 原图来
            kit.gen(f, 'HSR2D Style, ' + nat2, 768, 1152, seed=seed, model='preview3', init=b, denoise=0.5, lora=(DORA[0], 1.0))
        elif j.startswith('hi'):   # 高清那一路：原尺寸图生图，再单独修一遍脸。hi45 = 重绘 0.45
            hi_pass(out, who, f, b_hi(out, who), tag, nat2, float(j[2:]) / 100)
        print(j, 'ok', flush=True)


main()
