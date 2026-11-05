import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.insert(0, r'E:\aldran_art\底稿\状态栏\comfy')
import gpt_gen
OUT = os.path.dirname(os.path.abspath(__file__))
L = r'E:\aldran_art\语料\人物参考_11-04\hsr_lc'
def lc(*n): return [os.path.join(L, x + '.png') for x in n]
ART = os.path.join(OUT, 'b_art.png')

LC = ("Draw an official full-body character illustration from the Japanese anime game Honkai: Star Rail, in the same hand as its Light Cone card art and official character art. The attached pictures show that hand; they are style references only: do not copy their characters, costumes, props or composition. ")
KEEP = "The LAST attached picture is this exact character, drawn in the style we want for her face: keep her face, her eye shape, hair colour and eye colour. "
BODY = ("BODY: she is a grown woman, not a girl: about 7 heads tall, 172 cm, the head a little larger than life but clearly an adult's, a slender neck, real shoulders, a defined waist, long legs with natural thickness at the thigh and calf, lean from training; NOT a stick-thin fashion figure and NOT a small girl. A clear line of action: the weight on one leg, hips and shoulders tilted in opposite directions; long fingers drawn with care. ")
HAIR = ("HAIR: NO thin wavy strands and NO glossy plastic stripes. About 8 to 12 thick, smooth, ribbon-like locks, each one a clean bold shape with a crisp edge, swelling in the middle and tapering to a sharp hook at the end. A smooth rounded mass over the skull, the volume close around the head and shoulders. Soft low-contrast shading: a broad, pale, feathered band of highlight across the crown, not shiny; a soft hue shift from root to tip; a few crisp shadow shapes under the locks; fine lines only near the tips. ")
FACE = ("FACE, as in the references: medium-large, sharp, gently slanted almond eyes, NOT big round doll eyes; a thin tapering dark-brown upper lash line and a fine eyelid crease, no thick black lashes; the iris a soft luminous gradient with a small highlight; thin eyebrows partly hidden by the fringe; a short distance from the eyes to the mouth; a tiny nose, only a faint shadow; a small thin mouth; a soft cheek tapering to a neat pointed chin, grown-up rather than childish. Pale clean skin with very little shading and only the faintest blush; skin shadows are a soft warm pink-orange, hard-edged under the fringe and under the chin. ")
REST = ("LINE: a fine thin warm-brown line, never black, tapering away inside the shapes. "
 "COLOUR: a sophisticated, slightly muted palette with soft transitions, the way the references handle plum, teal and silver; tinted whites; the darkest tones are plum or deep slate, not black; one small saturated accent. "
 "LIGHT: a gentle key light from the upper left; shadows tinted with a soft cool hue such as violet or slate blue; soft ambient occlusion where layers meet; a thin pale rim along one edge. "
 "CLOTHES: drawn lightly, not heavy and dark: every large piece of cloth carries a visible soft gradient of hue, the folds are a few crisp elegant shadow shapes radiating from tension points, hems flip over to show a contrasting lining. Materials differ: leather with long soft highlights and stitched edges, metal fittings with small crisp reflections, fine embroidery kept small and quiet along an edge. Detail gathers at the chest, waist and hands; the legs and hems stay calm. "
 "Avoid: the look of a Western animated film, the look of an old moe anime, big round eyes, black outlines, saturated yellow hair, glossy hair stripes, thin wavy strands, clip-art embroidery, stick-thin legs, flat fills, a stiff stance, beige cast, grain, glitter. ")
WHO = ("A 22-year-old woman, a kingdom knight, dignified, a beautiful mature face with a gentle air. Thick loose wavy locks of soft warm gold hair shifting to pale champagne at the tips, sea-blue eyes. ")
OUTFIT = ("Her travelling uniform: a fitted slate-navy knight's coat with a high collar buttoned to the throat, slim silver piping and small silver buttons, a small knight's badge on the left chest, a brown leather belt with a stitched strap, a split coat skirt to the mid-thigh lined in pale blue, slim dark breeches and knee-high riding boots; a short slate-navy cape over one shoulder lined with pale blue silk. Fully clothed, modest, not sexualized. ")
POSE = ("She stands in a relaxed three-quarter view, the weight on one leg, one hand resting on the belt, a light wind sweeping her hair and cape to one side, looking at the viewer with a calm, kind, slightly stern expression. The plain, regular version of the character: even light, no dramatic shadow across the face, no blur, no particles. The whole figure from the top of the head to the soles of the boots, filling the height of the picture. Transparent background: nothing behind the figure, no floor, no cast shadow. No text, no logo, no frame. Portrait picture, aspect ratio 2:3. ")
FULL = BODY + HAIR + FACE + REST + WHO + OUTFIT + POSE
JOBS = {
 'n1': (LC + KEEP + FULL, lc('firefly_full', 'guinaifen', 'lance_full', 'jingyuan') + [ART]),
 'n2': (LC + KEEP + FULL, lc('guinaifen', 'jingyuan', 'anaxa', 'wheat') + [ART]),
 'n3': (LC + FULL, lc('firefly_full', 'guinaifen', 'lance_full', 'jingyuan')),
}
def job(k):
    p, refs = JOBS[k]
    print('开始', k, flush=True)
    o = gpt_gen.gen(os.path.join(OUT, k), p, refs=refs, timeout=1200)
    print('好了', k, o, flush=True)
if __name__ == '__main__':
    names = sys.argv[1:] or list(JOBS)
    with ThreadPoolExecutor(3) as ex:
        for f in [ex.submit(job, k) for k in names]:
            try: f.result()
            except Exception as e: print('失败', e, flush=True)
