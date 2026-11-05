# 用户点名四位的艺术照跟立绘不是一张脸（脸拉长、显老、发色走样、多了胡子）。每位两张，参考把放大的头放在最后，写明照它。挑好的另存 art.png。
import os
import sys
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.insert(0, 'E:/aldran_art/底稿/状态栏/comfy')
import gpt_cast as G
import gpt_gen
import gpt_sheet as S

FIX = {
    'aethelia': 'Copy the sprite\'s face: a soft, smooth, delicate oval face with a small chin, gentle large eyes and a calm kind look, NOT a long face, NOT harsh, NOT older than the sprite. Her hair is pale cream-gold as in the sprite, with no green in it; the leaf-green light only touches the background. No patterned shadow on the skin. Keep the laurel circlet exactly as in the sprite.',
    'eunice': 'Copy the sprite\'s face: a soft, rounded, kind young woman\'s face with a small chin and a warm gentle smile, eyes gently curved, NOT a long face, NOT sultry, NOT masculine. Keep the same loosely pinned-up light chestnut hair with the green ribbon and leaf sprig at the back of the head, as in the sprite, not loose all over the face. The hand does not touch the face: she holds a small glass vial near her shoulder.',
    'celica': 'Copy the sprite\'s face: a serene, soft oval face with a small chin and a calm closed-mouth smile, NOT a long face. Keep the hair tidy and sleek exactly as in the sprite: smooth pale platinum hair parted neatly and falling straight, with the small silver hair ornament; no wild strands across the face. A very faint sacred mark on the brow, barely glowing. The hand stays away from the face, the hands resting together at the chest.',
    'baro': 'Copy the sprite\'s face: clean-shaven with NO beard and NO stubble, a sly, boyish-looking grown halfling with narrow smiling eyes, a small straight nose and a smooth narrow chin, NOT a long or hooked nose, NOT older than the sprite. Keep the same tousled brown curls and feathered hat.',
}
JOBS = []
for k in FIX:
    for v in 'ab':
        JOBS.append((k, v))


def run(job):
    k, v = job
    c = G.CAST[k]
    d = S.d(k)
    cell = os.path.join(d, 'cell_casual.png')
    head = os.path.join(d, 'head.png')
    refs = G.refs_of(c, 'art')[:2] + [cell, head]
    lead = 'The LAST attached picture is a close-up of this exact character\'s head and the one before it the full sprite. Above all the face must be the same drawing as that close-up: the same face shape, the same proportions of eyes, nose and mouth, the same age. '
    eyes = '' if k in S.NOT_LEGEND else S.OLD_EYES
    # 这几位头发和脸盖过资料里写的 art 动作
    p = (S.ART % c['palette']).replace('The LAST attached picture is this exact character: the same face, eye shape, eye colour, hair colour, hairstyle and outfit, instantly recognisable as that sprite. ', lead) + eyes + c['who'] + ' ' + c['art'] + ' ' + FIX[k] + S.ART_END
    out = gpt_gen.gen(os.path.join(d, '候选', 'art_' + v), p, refs=refs, timeout=1200)
    print('好了', k, v, flush=True)
    return out


with ThreadPoolExecutor(3) as ex:
    for f in [ex.submit(run, j) for j in JOBS]:
        try:
            f.result()
        except Exception as e:
            print('失败', str(e)[:200], flush=True)
