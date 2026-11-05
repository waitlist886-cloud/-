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
KEEP = "The LAST attached picture shows this exact character: keep her hair colour, her eye colour and her costume idea, but draw her face and body the way the other references draw them. "
SPEC = ("FACE, Japanese not Western: large, tall, glossy eyes set low, at about the middle of the head, taking up much of the face; a thick curved dark-brown upper lash line with a small wing and a thin lower lash; the iris a multi-colour gradient, dark at the top and bright at the bottom, with one big soft highlight and one tiny sharp one; thin short eyebrows partly hidden by the fringe; a very short distance from the eyes to the mouth; a tiny nose, only a dot of shadow and a tiny highlight; a small mouth; soft rounded cheeks tapering to a small pointed chin; a short forehead mostly hidden by the fringe. Peach skin with a pink airbrushed blush under the eyes and on the ears; skin shadows are a warm saturated orange-pink, hard-edged under the fringe and under the chin. "
 "BODY: a small head, about 1 to 8 heads tall, very long slender legs, narrow shoulders, slim limbs, a clear line of action: the weight on one leg, hips and shoulders tilted in opposite directions; long slender fingers drawn with care. "
 "HAIR: a big expressive silhouette, flowing in large ribbon-like clumps that curl at the ends; the base colour shifts smoothly in hue from root to tip; a soft feathered zigzag band of highlight across the crown; crisp shadow shapes under each clump; fine strand lines only near the ends. "
 "CLOTHES: a designed, multi-layered flagship costume with every material treated differently: leather with long soft highlights and stitched edges, metal fittings with hard bright and dark reflections, silk with a soft sheen, embroidered trim whose pattern follows the folds. Folds radiate from the tension points as crisp angular shadow shapes with a soft gradient beside them; hems flip over and show a contrasting lining; every large piece of cloth carries a gradient of hue; small hanging details, straps, a tassel, a ribbon, one small jewel. Detail is dense at the chest, waist and hands, calmer on the legs and hems. "
 "LIGHT AND COLOUR: a clear key light from the upper left; shadows tinted with a saturated cool hue such as violet or blue, never grey; deep soft ambient occlusion where layers meet; a thin bright back-rim along one edge; tinted whites and no pure black, the darkest tones are plum or deep navy; one dominant hue family and one small accent. "
 "LINE: a fine dark-brown or dark-hued line of varying weight, stronger on the contour and under overlaps, tapering away inside the shapes. "
 "Avoid: the look of a Western animated film, a long nose, a wide jaw, small eyes, a long mid-face, thick even outlines, flat fills, a stiff mannequin stance, beige cast, grain, glitter. ")
WHO = ("A 22-year-old woman, a kingdom knight: tall and slender, dignified, a beautiful grown-up face with a gentle air. Big loose waves of warm gold hair shifting to pale champagne at the tips, sea-blue eyes. ")
OUTFIT = ("Her travelling uniform: a fitted dark navy knight's coat with a high collar buttoned to the throat, slim silver piping and small silver buttons, a small knight's badge on the left chest, a brown leather belt with a stitched strap, a split coat skirt to the knee lined in pale blue, dark breeches and knee-high riding boots; a short navy cape over one shoulder lined with pale blue silk. Fully clothed, modest, not sexualized. ")
POSE = ("She stands in a relaxed three-quarter view, the weight on one leg, one hand resting on the belt, a light wind sweeping her hair and cape to one side, looking at the viewer with a calm, kind, slightly stern expression. The plain, regular version of the character: even light, no dramatic shadow across the face, no blur, no particles. The whole figure from the top of the head to the soles of the boots, filling the height of the picture. Transparent background: nothing behind the figure, no floor, no cast shadow. No text, no logo, no frame. Portrait picture, aspect ratio 2:3. ")
JOBS = {
 'l1': (LC + KEEP + SPEC + WHO + OUTFIT + POSE, lc('firefly_full', 'lance_full', 'guinaifen', 'jingyuan') + [ART]),
 'l2': (LC + KEEP + SPEC + WHO + OUTFIT + POSE, lc('firefly_full', 'guinaifen', 'huohuo', 'wheat') + [ART]),
 'l3': (LC + SPEC + WHO + OUTFIT + POSE, lc('firefly_full', 'lance_full', 'guinaifen', 'jingyuan')),
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
