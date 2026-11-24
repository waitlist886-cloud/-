#!/usr/bin/env python3
# 11-23 原画核对（底稿/立绘/原画核对_11-23/山铜纪书.md）以后重画前改的场面字。重跑无害（改过的跳过）。
#   python -I -X utf8 review_1123.py
# p6_j2、p6_j3：斐里安、玛丽贝尔原来没挂立绘键，照现行立绘（s1n_ferian、s6n_maribel_dean）挂上，样子的字照立绘改，别的字不动。
# p4_b3：11-14 那一回 FIX 把血泥改成寻常湿土，重画要写进场面里，不然又画成血泥。
# p5_a2：瓦尔德拉克立绘是断角，场面里写明这时两只角都在（11-14 FIX 改过一回）。p5_a4：11-14 FIX 拿掉过花枝。
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

EDITS = {
    'p6_j2': {
        'style': ['fire'],      # 挂上两位以后参考图六张，出图最多五张，风格参考留一张
        'who_add': [['s1n_ferian', 'casual', 'the slender youth with ash-violet hair and a gold monocle'],
                    ['s6n_maribel_dean', 'casual', 'the porcelain-pale clockwork woman']],
        'text': [
            ("Across from her on the right sits a slender young man with grey-violet hair tied back with a strip of old cloth, a single round lens before his right eye, a plain dark travelling coat;",
             "Across from her on the right sits the slender youth with ash-violet hair, who looks fifteen or sixteen: messy ash-violet hair tied loosely at the nape with a faded strip of old cloth, "
             "amber-gold eyes, long slender pointed ears like an elf's showing through his hair, a single round gold-rimmed monocle on a thin gold chain over his right eye only, the eye toward us, "
             "his other eye bare and no spectacles, a plain dark travelling coat;"),
            ("a porcelain-pale woman with grey-brown curls and a white ruffled headdress sits upright against the wall, facing us,",
             "the porcelain-pale clockwork woman sits upright against the wall, facing us: soft ash-grey-brown hair in loose curls cut to the chin, short straight blunt bangs and two long soft locks at the front, "
             "clear crystal-blue eyes, a white ruffled headdress with long red cords hanging from it,"),
        ],
    },
    'p6_j3': {
        'who_add': [['s6n_maribel_dean', 'casual', 'the porcelain-pale clockwork woman'],
                    ['s1n_ferian', 'casual', 'the slender youth with ash-violet hair and a gold monocle']],
        'text': [
            ("stands a porcelain-pale woman who has just jumped down from a floating machine: grey-brown curls, a white ruffled headdress, a long grey-and-white dress from neck to ankle, the bow of a large clockwork key showing above her shoulder.",
             "stands the porcelain-pale clockwork woman, who has just jumped down from a floating machine: soft ash-grey-brown hair in loose curls cut to the chin, short straight blunt bangs and two long soft locks at the front, "
             "clear crystal-blue eyes, a white ruffled headdress with long red cords hanging from it, a long grey-and-white dress from neck to ankle; a large wind-up key is fixed in her lower back and juts straight out behind her waist, "
             "its gilded filigree bow inlaid with pale cyan crystal."),
            ("a slender young man with grey-violet hair tied with an old cloth strip and a single lens before his right eye stands still, watching her;",
             "the slender youth with ash-violet hair stands still, facing us and watching her: messy ash-violet hair tied with a faded old cloth strip, long slender pointed ears, "
             "a single round gold-rimmed monocle over his right eye only, on the viewer's left, and no spectacles;"),
        ],
    },
    'p4_b3': {
        'text': [
            ("all open and empty, and the earth beside them is stained dark.",
             "all open and empty; the ground around them is ordinary dark brown wet earth, stained darker in patches, with grey-brown puddles of rain water, and there is no red on the ground anywhere."),
        ],
    },
    'p5_a2': {
        'text': [
            ("and both of his great black horns still whole and glossy.",
             "and both of his great black horns still whole, smooth and glossy, the mirror of each other: neither horn is broken, cracked or glowing, although his reference sheet shows him later with one horn broken."),
        ],
    },
    'p5_a4': {
        'text': [
            ("Fine ash and specks of blue-green light drift out of focus across the near corners.",
             "Fine grey ash and specks of blue-green light drift out of focus across the near corners; there are no flowers, blossoms or petals anywhere in the picture."),
        ],
    },
}


def main():
    for f in ('p4', 'p5', 'p6'):
        p = os.path.join(HERE, f + '.json')
        raw = open(p, encoding='utf-8').read()
        d = json.loads(raw)
        n = 0
        for s in d.get('nodes', []) + d.get('deaths', []):
            e = EDITS.get(s['key'])
            if not e:
                continue
            if e.get('style'):
                s['style'] = e['style']
            for w in e.get('who_add', []):
                have = [x[0] for x in s.get('who', [])]
                if w[0] not in have:
                    s.setdefault('who', []).append(w)
                    n += 1
            for old, new in e.get('text', []):
                if old == new or new in s['text']:
                    continue
                assert s['text'].count(old) == 1, (s['key'], old[:60])
                s['text'] = s['text'].replace(old, new)
                n += 1
        out = json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else '')
        open(p, 'w', encoding='utf-8', newline='\n').write(out)
        print(f, '改了', n, '处')


main()
