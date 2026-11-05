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
N2 = os.path.join(OUT, 'n2.png')

LC = ("Draw an official full-body character illustration from the Japanese anime game Honkai: Star Rail, in the same hand as its Light Cone card art and official character art. The attached pictures show that hand; they are style references only: do not copy their characters, costumes, props or composition. ")
KEEP = "The LAST attached picture is this exact character: keep her grown-up gentle face, her eye shape, hair colour and eye colour and her costume, but make her head bigger and the colours cleaner as described here. "
BODY = ("BODY: she is a grown woman with the adult proportions of the FIRST two references, not a girl: a head of natural size on a long elegant figure, real shoulders, a narrow waist, womanly hips, very long legs with natural thickness at the thigh and calf, not stick-thin; relaxed and well balanced. Long fingers drawn with care. ")
HAIR = ("HAIR: about 8 to 12 thick, smooth, ribbon-like locks, each one a clean bold shape with a crisp edge, swelling in the middle and tapering to a sharp hook at the end. A smooth rounded mass over the skull, the volume close around the head and shoulders. No fibrous texture, no thin wavy strands, no glossy plastic stripes. A broad, pale, feathered band of highlight across the crown; a clear hue shift from warm gold at the root to pale champagne at the tips; crisp shadow shapes in warm ochre under the locks; fine lines only near the tips. ")
FACE = ("FACE, exactly as in the references, this is what makes the picture Japanese: the iris is LARGE and fills almost the whole eye opening, almost no white visible at the sides; the upper eyelid is a heavy, nearly straight dark-brown line that slightly covers the top of the iris, giving a calm, half-lidded look; the outer corner tapers to a small point; the iris is one soft deep tone at the top melting to a luminous tone at the bottom, with one small highlight; a fine eyelid crease; no thick black lashes, no bright saturated eye colour. Thin pale eyebrows, partly hidden by the fringe. A short distance from the eyes to the mouth. The nose is only a tiny faint shadow, NO triangular highlight on the nose bridge. The mouth is a very short, thin, slightly curved line, a barely visible smile, no lips drawn, no grin. A simple clean face with a soft cheek and a neat pointed chin, grown-up. Pale clean skin almost without shading and only the faintest blush; skin shadows are a soft warm pink-orange, crisp and hard-edged under the fringe and under the chin. ")
REST = ("RENDERING: clean digital anime rendering with crisp hard-edged cel shadows and smooth gradients layered over them; luminous and fresh, never dull or grey, no painterly texture, no fibres, no grain. "
 "LINE: a fine thin warm-brown line, never black, tapering away inside the shapes. "
 "COLOUR: clear and refined: a slate blue with violet in its shadows and a real saturated blue where the light hits, pale sky-blue lining, warm honey gold, warm brown leather, silver with cool highlights; tinted whites; the darkest tones are plum or deep slate, not black; one small saturated accent. "
 "LIGHT: a clear key light from the upper left; shadows tinted with a clean cool hue such as violet or blue; soft ambient occlusion where layers meet; a thin pale rim along one edge. "
 "CLOTHES: every large piece of cloth carries a visible gradient of hue, the folds are a few crisp elegant shadow shapes radiating from tension points, hems flip over to show the contrasting lining. Materials differ: leather with long soft highlights and stitched edges, metal fittings with small crisp reflections, very little embroidery, small and quiet along one edge. Detail gathers at the chest, waist and hands; the legs and hems stay calm. "
 "Avoid: the look of a Western animated film, the look of an old moe anime, big round eyes, black outlines, saturated yellow hair, thin wavy strands, clip-art embroidery, stick-thin legs, a small head, a tall fashion-model figure, a dull grey cast, a stiff stance, beige cast, grain, glitter. ")
WHO = ("A 22-year-old woman, a kingdom knight, dignified, a beautiful grown-up face with a gentle air. Thick loose wavy locks of warm golden blonde hair, soft blue-grey eyes with a sea-blue glow. ")
OUTFIT = ("Her travelling uniform: a fitted slate-blue knight's coat with a high collar buttoned to the throat, slim silver piping and small silver buttons, a small knight's badge on the left chest, a brown leather belt with a stitched strap, a split coat skirt to the mid-thigh lined in pale sky blue, slim dark breeches and knee-high riding boots; a short slate-blue cape over one shoulder lined with pale blue silk. Fully clothed, modest, not sexualized. ")
POSE = ("She stands facing the viewer in the plain neutral stance of a character-select screen, like the first two references: nearly frontal, the body turned very slightly, feet slightly apart, the weight a little on one leg, both arms hanging relaxed with a small gap from the body, one hand holding nothing, the cape and hair falling naturally with only a slight lift of wind. A calm, kind expression. The plain, regular version of the character: even clean light, no dramatic shadow across the face, no blur, no particles. The whole figure from the top of the head to the soles of the boots, filling the height of the picture. Transparent background: nothing behind the figure, no floor, no cast shadow, ignore the starry backgrounds of the references. No text, no logo, no frame. Portrait picture, aspect ratio 2:3. ")
POSE2 = ("She stands in a three-quarter view, the weight on one leg, one hand resting on the belt, a light wind sweeping her hair and cape to one side, looking at the viewer with a calm, kind expression. The plain, regular version of the character: even clean light, no dramatic shadow across the face, no blur, no particles. The whole figure from the top of the head to the soles of the boots, filling the height of the picture. Transparent background: nothing behind the figure, no floor, no cast shadow, ignore the starry backgrounds of the references. No text, no logo, no frame. Portrait picture, aspect ratio 2:3. ")
FULL = BODY + HAIR + FACE + REST + WHO + OUTFIT + POSE
P1 = os.path.join(OUT, 'p1.png')
K = LC + KEEP.replace(', but make her head bigger and the colours cleaner as described here', ', but redraw her eyes, nose and mouth as described here')
JOBS = {
 'q1': (K + FULL, lc('himeko_stand', 'aglaea_stand', 'himeko_full', 'guinaifen') + [P1]),
 'q2': (K + FULL, lc('himeko_stand', 'guinaifen', 'jingyuan', 'wheat') + [P1]),
 'q3': (K + FULL, lc('himeko_stand', 'aglaea_stand', 'guinaifen', 'jingyuan') + [ART]),
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
