# 再轻一档：0.30，把容易丢的几样加权写进去，看能不能保住设定又把画面变干净
import os
import sys
import time
sys.path.insert(0, r'E:\aldran_art\底稿\状态栏\comfy')
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import kit
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'noob2')
NEG = 'sparkle, glitter, light particles, lens flare, bloom, shiny skin, oily skin, 3d, realistic, western cartoon, text, human ears, '
ST = 'official art, game cg, genshin impact, '
J = {
    'queens': ((1024, 912), '2girls, multiple girls, ' + ST + 'upper body, from side, looking to the side, night sky, cloud, holding sword, longsword, (small gold crown:1.2), brown hair, gradient hair, braided bun, long sidelocks, scar across eye, amber eyes, white cape, white scarf, epaulettes, gold breastplate, grey hair, very long hair, blunt bangs, side braid, large black hair bow, (pointy ears:1.4), yellow eyes, (red forehead mark:1.4), high collar, crimson coat, black coat, gold trim, chain, earrings, red crystal'),
    'gods': ((1120, 704), '1boy, 3girls, multiple girls, ' + ST + 'from side, looking to the side, night sky, cloud, red hair, spiked hair, crimson coat, holding staff, golden staff, fire wings, blonde hair, long wavy hair, white dress, gold belt, small black cat on shoulder, short hair, (small antlers:1.4), green robe, holding wheat, green hair, long hair, (head wings:1.3), pink robe, hooded robe, white robe'),
}
for name, (size, prompt) in J.items():
    t = time.time()
    kit.gen(os.path.join(OUT, '%s_d30.png' % name), prompt, size[0], size[1], seed=4, model='noob', negative=NEG, init=os.path.join(OUT, 'src_%s.png' % name), denoise=0.30)
    print(name, '%.0f 秒' % (time.time() - t), flush=True)
kit.sheet([os.path.join(OUT, 'src_queens.png'), os.path.join(OUT, 'queens_d30.png'), os.path.join(OUT, 'queens_d40.png')], os.path.join(OUT, '_sheet_q3.jpg'), h=620)
kit.sheet([os.path.join(OUT, 'src_gods.png'), os.path.join(OUT, 'gods_d30.png'), os.path.join(OUT, 'gods_d40.png')], os.path.join(OUT, '_sheet_g3.jpg'), h=460)
print('done')
