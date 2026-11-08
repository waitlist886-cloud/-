# 真龙原形（11-08）：用户“为包括阿蕾缇娅在内的有档案的真龙角色补上真龙形态的立绘”。一头一张，竖的 2:3，放进同行页的立绘位，
# 角色的衣着写 龙形 时换这一张（four_era_art.py 的 DRAGONS）。画法照史诗战和神明显像定下的那一路（gpt_epic.py 的 MJ：干净的电影感概念画、
# 压迫感、人脸照 JRPG），只是这一回画的是一头真龙本身：独自一头，占满画面，不打仗。真龙的样子照底卡 #84 和 天脊真龙_方向稿.md：
# 苍白岩石龙鳞，血里赤红阳雷，四足两翼的西方龙；一支一相（阿蕾缇娅是正午一脉，七相都有）。
# 用法：python -I -X utf8 gpt_dragon.py [键…]   不给键就全出；已经出过的跳过。资料读 cast 里写了 dragon_form 的那几条，阿蕾缇娅写在这里。
import glob, json, os, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import gpt_gen     # noqa: E402
import gpt_epic    # noqa: E402  画法（MJ_TEXT、MJ_REFS）、WEST、END

OUT = os.path.join(HERE, 'out', '真龙原形')

TRUE_DRAGON = ('This picture is the true-form portrait of a TRUE DRAGON for the codex of a Western fantasy RPG: one ancient dragon alone, majestic and overwhelming, '
               'filling most of the frame, seen from a slightly low angle against a vast sky, perched on a crag or a mountain ridge or half-risen in flight; not fighting anyone. '
               'It is a Western dragon: four powerful legs and a separate pair of great wings, a long neck and a long tail, horns; never a serpentine Chinese dragon, no whiskers, no pearl. '
               'Every true dragon shares two marks: its scales are pale and stone-like, like weathered white rock or pale granite plates, never glossy reptile skin; '
               'and crimson sun-lightning runs in its blood, glowing as red light in the seams between the stone scales and crackling along its body. '
               'Its eyes are intelligent and old. Clean and readable: one huge silhouette, a lot of sky, haze far below. ')

ALETIA = ('This dragon is Aletia, "the Dragon Sovereign of Seven Radiances", of the noon line, the scattered blood of the dragon lord of the sun: she carries all seven elements at once and none of them purely, '
          'like white light that holds all seven colours. Her stone scales are pale ivory, and along her horns, the ridge of her back and the edges of her scales a slow seven-coloured iridescent glow flows, '
          'red, orange, yellow, green, cyan, blue and violet. Her wings are elemental wing-membranes of seven aspects, each section of the membrane a different element: flame, frost crystal, stone, green leafy light, wind, water and violet lightning, '
          'spread wide enough to darken half the sky. Her eyes are layered like crystal with a rainbow sheen deep inside. She is slender, long-necked and graceful, elegant and dangerous at once, '
          'with sweeping swept-back horns crowned by a faint halo of prismatic light; crimson sun-lightning threads through her chest. Feminine grace in a dragon\'s form, never a monster, the most beautiful thing in the sky.')


def jobs():
    out = {'aletia': ALETIA}
    for f in glob.glob(os.path.join(HERE, 'cast', '**', '*.json'), recursive=True):
        try:
            data = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        rows = data if isinstance(data, list) else data.get('cast', []) if isinstance(data, dict) else []
        for e in rows:
            if isinstance(e, dict) and e.get('dragon_form'):
                key = e.get('en') or e.get('key')
                out[key.split('_', 1)[1] if '_' in key else key] = e['dragon_form']
    return out


def run(keys=None, workers=3):
    J = jobs()
    keys = keys or sorted(J)
    os.makedirs(OUT, exist_ok=True)

    def one(k):
        prompt = gpt_epic.MJ_TEXT + TRUE_DRAGON + J[k] + gpt_epic.END + gpt_epic.WEST
        try:
            return k, gpt_gen.gen(os.path.join(OUT, 'dragon_' + k), prompt, refs=list(gpt_epic.MJ_REFS), timeout=1500)
        except Exception as ex:   # noqa: BLE001
            return k, '失败：%s' % ex
    with ThreadPoolExecutor(workers) as ex:
        for k, r in ex.map(one, keys):
            print(k, r)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    if '--list' in sys.argv:
        for k, v in jobs().items():
            print(k, v[:80])
    else:
        run(args or None)
