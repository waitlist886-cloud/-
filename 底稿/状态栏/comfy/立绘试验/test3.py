import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.insert(0, r'E:\aldran_art\底稿\状态栏\comfy')
import gpt_gen
OUT = os.path.dirname(os.path.abspath(__file__))
H = r'E:\aldran_art\语料\人物参考_11-04\hsr\crop'
def r(*n): return [os.path.join(H, x + '.png') for x in n]
ART = os.path.join(OUT, 'b_art.png')

FINISH = ("Match the premium finish of official Honkai: Star Rail character illustrations. The attached reference pictures show that finish; they are for style only, do not copy their characters, costumes or composition. The LAST attached picture is this exact character: keep her face, eyes and hair colour. "
 "This finish is a layered digital illustration, NOT flat cel art: ultra-thin delicate coloured line art that fades out in the light areas; crisp hard-edged cel shadows with smooth airbrushed gradients layered over them, so every shape has a soft multi-hue transition: hair melting from a deep saturated amber in the shadows through warm gold to almost white at the tips, with translucent light passing through the thin locks; skin with rosy gradients at the cheeks, ears and knuckles; cloth with a gentle gradient from a lit hue to a shadow hue and coloured bounce light inside the folds; a soft bloom around the brightest highlights; metal and gems rendered like fine jewellery, with sharp mirror-like reflections, thin elegant edges rather than thick stripes; large luminous eyes with an intricate iris. "
 "The costume is designed like a flagship character of that game: an elegant layered silhouette, refined tailoring with thin metallic piping, a delicate embroidered motif along the hems, one or two jewel accents, a few asymmetrical details; rich but tidy. Extremely clean edges, high resolution. "
 "Avoid: flat vector fills, thick stripes, plastic-looking hair, lemon yellow, mobile clip-art feel, dark outlines, beige or sepia cast, muddy shading, grain, glitter. ")
WHO = ("A 22-year-old woman, a kingdom knight who earned her badge on the battlefield: tall, straight-backed, lean and trained, grown-up and dignified, beautiful with a mature gentle face. Big loose curling waves of rich warm gold hair, sea-blue gem eyes. ")
OUTFIT = ("She wears her off-duty travelling uniform: a fitted dark navy knight's coat with a high collar buttoned to the throat, slim silver piping and small silver buttons, a small knight's badge on the left chest, a brown leather belt, a split coat skirt to the knee, dark breeches and knee-high riding boots; a short navy travelling cape over one shoulder lined with pale blue silk. Fully clothed, modest, not sexualized. A calm, kind expression, the brows relaxed, looking at the viewer. ")
FULL = ("Full-body standing character sprite for the character screen of a Japanese fantasy RPG: the whole figure from the top of the head to the soles of the boots, centred, an elegant relaxed stance, natural proportions, hands drawn carefully. Soft key light from the upper left and a thin bright rim of light along one side. No dramatic shadow across the face, no blur, no floating particles. Transparent background: nothing behind the figure, no floor, no cast shadow. No text, no logo, no frame. Portrait picture, aspect ratio 2:3. ")
KNEE = ("Three-quarter character sprite for the dialogue and character screens of a Japanese fantasy RPG: the figure from the top of the head down to just above the knees, cut off cleanly by the bottom edge of the picture, centred and large in the frame, an elegant relaxed stance, hands drawn carefully. Soft key light from the upper left and a thin bright rim of light along one side. No dramatic shadow across the face, no blur, no floating particles. Transparent background: nothing behind the figure, no floor, no cast shadow. No text, no logo, no frame. Portrait picture, aspect ratio 2:3. ")
STYLE = r('kelvdela', 'fengjin', 'changyeyue', 'aglaea') + [ART]
JOBS = {
 'g_full': (FINISH + WHO + OUTFIT + FULL, STYLE),
 'h_knee': (FINISH + WHO + OUTFIT + KNEE, STYLE),
 'i_full2k': (FINISH + WHO + OUTFIT + FULL + 'Render at the largest size the tool allows, ideally 2048 by 3072 pixels. ', STYLE),
}
def job(k):
    p, refs = JOBS[k]
    print('开始', k, flush=True)
    o = gpt_gen.gen(os.path.join(OUT, k), p, refs=refs, timeout=1200)
    print('好了', k, o, flush=True)
with ThreadPoolExecutor(3) as ex:
    for f in [ex.submit(job, k) for k in sys.argv[1:] or JOBS]:
        try: f.result()
        except Exception as e: print('失败', e, flush=True)
