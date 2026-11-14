# 11-13 人体那一轮的第二回：重画出来以后逐张查，两幅再动。跑过一回就不再跑（anat 记成 2）。
#   缇里安：新图人体对了，可举着扶弓的是右臂。他的右臂抬不起来（灯的年月第105、172行，立绘资料 build 那一行），教人只用左手。
#           图左右翻了过来（原样留作 s08_f_tirian_a1.png），这里把场面稿改成翻过来以后的样子，往后照稿子重画也是对的。
#   狄昂：重画的一稿后脚尖还是朝右。不动场面稿，走 gpt_cg2.py 的 FIX（拿 _a1 当底只改两条腿），这里只在 note 里记一笔。
#   python -I -X utf8 review_anat2.py [--apply]
import glob
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

SUB = {
    's08_f_tirian': dict(
        camera="level from his right side at the height of his waist, he in full profile at centre left, the wall face rising out of frame behind him, slightly tilted",
        light="low golden late-afternoon sun from the right and the south, a cool grey-blue shadow side on the white stone and on his cloak",
        sub=[
            ("Low golden sunlight comes from the left, from the south, over the top of the wall.", "Low golden sunlight comes from the right, from the south, over the parapet."),
            ("In the near foreground, centre right,", "In the near foreground, centre left,"),
            ("in clean profile, facing LEFT toward the south and seen from his left side, tall and slender, both feet side by side and pointing left,",
             "in clean profile, facing RIGHT toward the south and seen from his right side, tall and slender, both feet side by side and pointing right,"),
            ("and his nearer hand, the left, rests on it at the height of his chest, the arm bent at the elbow; the deep hand-shaped grip mark in the wood is clearly visible. "
             "His farther arm hangs straight down at his side, relaxed; only its hand shows, below the edge of his cloak. His arms are of ordinary length.",
             "and his farther hand, the left, reaches forward and rests on it at the height of his chest; the deep hand-shaped grip mark in the wood is clearly visible. "
             "His nearer arm, the right, hangs straight down at his side from shoulder to hand, relaxed, and is never lifted: it is the left hand alone that holds the bow. His arms are of ordinary length."),
            ("Along his line of sight, far away to the left,", "Along his line of sight, far away to the right,"),
        ],
        note='（第二回：新图扶弓的是右臂，跟他抬不起来的右臂对不上，图左右翻了，稿子照翻过来的样子改。）'),
    's12_f_dion': dict(sub=[], note='（第二回：重画的一稿后脚尖还朝右，走 gpt_cg2.py 的 FIX，拿 _a1 当底只改两条腿。）'),
}


def main():
    apply = '--apply' in sys.argv
    files, where = {}, {}
    for p in sorted(glob.glob(os.path.join(HERE, 'g?.json'))):
        d = json.load(open(p, encoding='utf-8'))
        files[p] = d
        for s in d.get('falls', []):
            where[s['key']] = (p, s)
    for k, r in SUB.items():
        p, s = where[k]
        if s.get('anat') == 2:
            print('跑过了', k)
            continue
        assert s.get('anat') == 1, k
        for a, b in r['sub']:
            assert s['text'].count(a) == 1, (k, a[:50], s['text'].count(a))
            s['text'] = s['text'].replace(a, b)
        for f in ('camera', 'light'):
            if f in r:
                s[f] = r[f]
        s['note'] = s.get('note', '') + r['note']
        s['anat'] = 2
        print('改了', k, os.path.basename(p))
    if not apply:
        print('只报，没写盘。')
        return
    for p, d in files.items():
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(d, ensure_ascii=False, indent=1) + '\n')
    print('写了', len(files), '个文件')


if __name__ == '__main__':
    main()
