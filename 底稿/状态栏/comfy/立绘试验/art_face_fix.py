# 艺术照五官不正、跟立绘不像的，照 test14 的办法重出（11-05 用户点了叶森）：参考最后一张换成放大的头，写明五官端正、两眼齐平、镜头只微微斜。
# 每位出两张候选写 out/立绘_<纪>/<en>/候选/art_a.png、art_b.png，挑好的再拷成 art.png。
#   CAST_SET=前传 python 立绘试验/art_face_fix.py q4b_yesen [更多键]
import os
import sys
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gpt_cast as G
import gpt_gen
import gpt_sheet as S

LEAD = ("The LAST attached picture is a close-up of this exact character's head and the one before it the full sprite. "
        "Above all the face must be the same drawing as that close-up: the same face shape, the same proportions of eyes, nose and mouth, the same age. ")
STRAIGHT = (" The face is drawn straight and well proportioned: both eyes level with each other and the same size and shape, the nose centred between them, "
            "the mouth centred under the nose, the jaw symmetrical; the head is turned only slightly and tilted only a little, never skewed or distorted.")
OLD = 'The LAST attached picture is this exact character: the same face, eye shape, eye colour, hair colour, hairstyle and outfit, instantly recognisable as that sprite. '


def run(job):
    k, v = job
    c = G.CAST[k]
    d = S.d(k)
    refs = G.refs_of(c, 'art')[:2] + [os.path.join(d, 'cell_casual.png'), os.path.join(d, 'head.png')]
    eyes = S.OLD_EYES if (c.get('legend') if S.SET else k not in S.NOT_LEGEND) else ''
    p = (S.ART % c['palette']).replace(OLD, LEAD) + eyes + c.get('face', '') + c['who'] + ' ' + c['art'] + ' ' + c.get('art_extra', '') + STRAIGHT + S.ART_END
    if c.get('art_close') or S.young(c):
        p += ' Only the head and shoulders are in the picture.'
    if S.young(c):
        p += ' The collar and clothes fully cover the shoulders and chest.' + S.YOUNG
    out = gpt_gen.gen(os.path.join(d, '候选', 'art_' + v), p, refs=refs, timeout=1200)
    print('好了', k, v, flush=True)
    return out


jobs = [(k, v) for k in sys.argv[1:] for v in 'ab']
with ThreadPoolExecutor(2) as ex:
    for f in [ex.submit(run, j) for j in jobs]:
        try:
            f.result()
        except Exception as e:
            print('失败', str(e)[:200], flush=True)
