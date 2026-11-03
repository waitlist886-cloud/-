# NoobAI 试验：同样的双王和大迷宫，看 SDXL 这条路够不够干净、这张卡跑不跑得动
import os
import sys
import time
sys.path.insert(0, r'E:\aldran_art\底稿\状态栏\comfy')
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import kit
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'noob1')
NEG = 'sparkle, glitter, light particles, lens flare, bloom, shiny skin, oily skin, 3d, realistic, western cartoon, text, '
STYLE = 'official art, game cg, genshin impact, '
JOBS = {
    'balt': ('1girl, solo, ' + STYLE + 'cowboy shot, from side, looking to the side, very long hair, straight hair, grey hair, blunt bangs, side braid, large black hair bow, pointy ears, yellow eyes, forehead mark, red gem, expressionless, high collar, crimson coat, black coat, long coat, gold trim, chain, black dress, earrings, holding scepter, white background, simple background', 832, 1216),
    'sorn': ('1girl, solo, ' + STYLE + 'cowboy shot, from side, looking to the side, arm up, holding sword, longsword, brown hair, gradient hair, red hair tips, braided bun, long sidelocks, small gold crown, amber eyes, scar across eye, serious, white cape, high collar, white scarf, epaulettes, gold trim, gold breastplate, white background, simple background', 832, 1216),
    'maze': ('no humans, scenery, fantasy, ' + STYLE + 'ruins, giant labyrinth, concentric circles, stone architecture, arch, arcade, spiral staircase, golden stairs, abyss, dark, gothic architecture, spire, purple sky, eclipse, black sun, giant shadow, tendrils, wide shot, from above', 832, 1216),
}
for name, (p, w, h) in JOBS.items():
    for seed in (1, 2):
        t = time.time()
        kit.gen(os.path.join(OUT, '%s_%d.png' % (name, seed)), p, w, h, seed=seed, model='noob', negative=NEG)
        print(name, seed, '%.0f 秒' % (time.time() - t), flush=True)
kit.sheet([os.path.join(OUT, '%s_%d.png' % (n, s)) for n in JOBS for s in (1, 2)], os.path.join(OUT, '_sheet.jpg'), h=640)
print('done')
