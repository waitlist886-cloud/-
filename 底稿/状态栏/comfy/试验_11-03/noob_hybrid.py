# 组合试验：GPT 中间版定构图，NoobAI 低重绘把人物画干净，看能不能又贴设定又接近原神立绘
import os
import sys
import time
sys.path.insert(0, r'E:\aldran_art\底稿\状态栏\comfy')
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import kit
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'noob2')
os.makedirs(OUT, exist_ok=True)
SRC = r'E:\aldran_art\底稿\状态栏\comfy\out\四方_11-03\gpt_mid\right.png'
NEG = 'sparkle, glitter, light particles, lens flare, bloom, shiny skin, oily skin, 3d, realistic, western cartoon, text, '
ST = 'official art, game cg, genshin impact, '
im = Image.open(SRC).convert('RGB')
CROPS = {
    'queens': ((0, 980, 887, 1774), (1024, 912),
               '2girls, multiple girls, ' + ST + 'upper body, from side, looking to the side, night sky, cloud, holding sword, longsword, small gold crown, brown hair, gradient hair, braided bun, long sidelocks, scar across eye, amber eyes, white cape, white scarf, epaulettes, gold breastplate, grey hair, very long hair, blunt bangs, side braid, large black hair bow, pointy ears, yellow eyes, forehead mark, high collar, crimson coat, black coat, gold trim, chain, earrings'),
    'gods': ((0, 560, 887, 1120), (1120, 704),
             '1boy, 3girls, multiple girls, ' + ST + 'from side, looking to the side, night sky, cloud, red hair, spiked hair, crimson coat, holding staff, golden staff, fire wings, blonde hair, long wavy hair, white dress, gold belt, black cat, short hair, small antlers, green robe, holding wheat, green hair, long hair, head wings, pink robe, hooded robe, white robe'),
}
paths = []
for name, (box, size, prompt) in CROPS.items():
    src = os.path.join(OUT, 'src_%s.png' % name)
    im.crop(box).resize(size, Image.LANCZOS).save(src)
    paths.append(src)
    for d in (0.40, 0.55):
        t = time.time()
        p = os.path.join(OUT, '%s_d%d.png' % (name, int(d * 100)))
        kit.gen(p, prompt, size[0], size[1], seed=4, model='noob', negative=NEG, init=src, denoise=d)
        paths.append(p)
        print(name, d, '%.0f 秒' % (time.time() - t), flush=True)
kit.sheet(paths[:3], os.path.join(OUT, '_sheet_queens.jpg'), h=620)
kit.sheet(paths[3:], os.path.join(OUT, '_sheet_gods.jpg'), h=460)
print('done')
