# 艺术照五官不正、跟立绘不像的，出几张候选挑（11-05 用户点了叶森）。提示词和参考图就是 gpt_sheet.art_job：最后一张放大的头、五官端正那一句，11-05 起正式流程也是这一套。
# 每位出两张候选写 out/立绘_<纪>/<en>/候选/art_a.png、art_b.png，挑好的再拷成 art.png。
#   CAST_SET=前传 python 立绘试验/art_face_fix.py q4b_yesen [更多键]      CANDS=a 只出一张
import os
import sys
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gpt_cast as G
import gpt_gen
import gpt_sheet as S

def run(job):
    k, v = job
    p, refs = S.art_job(k)
    out = gpt_gen.gen(os.path.join(S.d(k), '候选', 'art_' + v), p, refs=refs, timeout=1200)
    print('好了', k, v, flush=True)
    return out


jobs = [(k, v) for k in sys.argv[1:] for v in os.environ.get('CANDS', 'ab')]
with ThreadPoolExecutor(2) as ex:
    for f in [ex.submit(run, j) for j in jobs]:
        try:
            f.result()
        except Exception as e:
            print('失败', str(e)[:200], flush=True)
