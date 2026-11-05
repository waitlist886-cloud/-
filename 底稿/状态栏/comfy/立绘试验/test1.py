import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.insert(0, r'E:\aldran_art\底稿\状态栏\comfy')
import gpt_gen
OUT = os.path.dirname(os.path.abspath(__file__))
H = r'E:\aldran_art\语料\人物参考_11-04\hsr\crop'
def r(*n): return [os.path.join(H, x + '.png') for x in n]

RENDER = ("Draw in the exact rendering style of the attached reference pictures, which are official key art from the game Honkai: Star Rail. They are style references only: do not copy their characters, costumes, flowers or composition. "
 "Copy how they are drawn: thin, crisp, even line art in a darker tint of each local colour, never black; flat, luminous cel colour with razor-sharp two-step and three-step shadow shapes, no airbrushing and no soft painterly blending; hair drawn as big clean flowing masses that end in long tapered points, with a colour gradient along the length, hard-edged highlight bands and a few single thin hairline strokes; large jewel-like eyes with a layered radial iris, a bright gradient, one small sharp catchlight and thin coloured eyeliner; a small sharp nose shown by a tiny triangular shadow, a small thin mouth, a slim V-shaped jaw; smooth flawless skin in a clean flat tone; saturated, clear, high-key colours and pure whites. "
 "Avoid the look of a generic AI anime picture: no beige or sepia cast, no muted dusty colours, no soft airbrushed shading, no watercolour or oil-paint feel, no canvas or paper grain, no fabric weave or wear textures, no scratches or grime, no noisy micro-detail, no thick dark outlines, no rounded generic face. ")
WHO = ("A 22-year-old woman, a kingdom knight who earned her badge on the battlefield: tall, straight-backed, lean and trained, grown-up and dignified. Bright gold hair in big loose curling waves, sea-blue gem eyes. ")
TACHIE = ("Full-body standing character sprite for a Japanese fantasy RPG, the kind shown on the character screen: the whole figure from the top of the head to the soles of the boots, centred, filling the height of the picture with a small margin, the body turned slightly to the viewer's left, a natural head-to-body ratio of about 1 to 7.5, hands drawn carefully. Even, neutral light with clean cel shadows, a calm expression, looking at the viewer. Fully clothed, modest, not sexualized. Costume design in the language of that game: sharp tailoring, clean layered shapes, neat metallic trim, one or two dominant colours and one small complementary accent, clean flat surfaces. Transparent background: nothing behind the figure, no floor, no cast shadow. No text, no logo, no frame. Portrait picture, aspect ratio 2:3. ")
OUTFIT = ("She wears her off-duty travelling uniform: a fitted dark navy knight's coat with a high collar buttoned to the throat, silver trim and plain silver buttons, a small knight's badge on the left chest, a brown leather belt, dark breeches and knee-high riding boots; a short travelling cape over one shoulder, its edge neatly mended. Her hair falls loose in big gold waves. She stands very straight, one hand resting on the belt.")
ART = ("A dramatic promotional art portrait of her, the same kind of picture as the references: a tight bust close-up cropped at the chest, the camera tilted, the head tilted and turned, looking back over the shoulder straight at the viewer with an intense, quiet, resolute expression, the figure filling the frame and cut off by its edges. A strong single-direction coloured light: a large hard-edged shadow falls across half of her face and dappled shadows fall over her hair; the skin takes on the hue of the light; the highlights bloom to pure white. The whole picture is built from one hue family, her gold, with deep navy shadows and one small sea-blue accent in the eyes. Soft out-of-focus shapes in the foreground for depth: drifting white feathers and scraps of banner cloth. One gauntleted hand rises near her collar, resting on the high crossguard of an enormous sword whose blade has a groove where a name was chiselled away. She wears a fitted dark navy knight's coat with a high collar and silver trim, a small knight's badge. Fully clothed, not sexualized. No text, no logo, no frame, no column. Portrait picture, aspect ratio 2:3. ")
JOBS = {
 'a_tachie': (RENDER + TACHIE + WHO + OUTFIT, r('nakexia', 'kelvdela', 'baie', 'fengjin')),
 'b_art': (RENDER + WHO + ART, r('nakexia', 'kelvdela', 'baie', 'fengjin')),
 'c_tachie2': (RENDER + TACHIE + WHO + OUTFIT, r('kelvdela', 'baie')),
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
