#!/usr/bin/env python3
# 门面第五本书“此刻”（迷宫纪 1001 年）主线的节点原画（11-25）。图出在 out/门面_原画_此刻/（不进库）。
# 场面写在 底稿/门面/小样_此刻书/scenes/now_*.json（nodes 一幕一幅，几份并着读），画法照 gpt_cg.py 节点原画那一套（崩铁光锥，人体护栏 BODY、POSE），
# 后头添山铜纪试画查出来的那几条（照 gpt_cg3.py 抄的，没改那两支脚本）。1001 年是魔导和蒸汽的年代，收尾那一段世界的话另写（TAIL_NOW）。
#   python -I -X utf8 gpt_cg_now.py round1          出头一轮（每条主线一幅，场面稿里 round=1 的），出过的跳过
#   python -I -X utf8 gpt_cg_now.py all             出全部（先头一轮，再别的）
#   python -I -X utf8 gpt_cg_now.py n1165_1 n1176_3 出这几幅
#   python -I -X utf8 gpt_cg_now.py L1176           出这一条主线的各幕
#   python -I -X utf8 gpt_cg_now.py --left [round1] 还缺哪几幅
#   python -I -X utf8 gpt_cg_now.py --redo n1165_1  整张重画：旧图挪进 备选/，scenes/rev.json 里这一幅的版次加一（只挪不出，队列开着会自己补上）
#   python -I -X utf8 gpt_cg_now.py --loop all      队列：一直跑到出完，撞了额度等恢复再接着出，每一遍重读场面稿（放后台跑，日志追加到 run_1125.log）
#                                                   要它停：在 out/门面_原画_此刻/ 放一个叫 STOP 的空文件
#   CG_DRY=1 只打提示词和参考图；CG_WORKERS=3 并着出（默认 3）
# scenes/looks.json：没有立绘的任务人物，同一条主线里前头审过的那一幅当参考（那一幅在 scenes/review.json 里写了 ok 才开这一幅）。
# 出图走本机官方 Codex 的订阅额度，这一本用默认的 ~/.codex 那个号（HOME_NOW），单跑时撞了额度就不再开新的，过后原样重跑会接着出；--loop 会等额度恢复。
import json
import os
import re
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_cg as G  # noqa: E402
from gpt_gen import gen  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BOOK = os.path.join(ROOT, '底稿', '门面', '小样_此刻书')
SCENES = os.path.join(BOOK, 'scenes')                                # now_*.json，几份并着读
REV = os.path.join(BOOK, 'scenes', 'rev.json')
LOOKS = os.path.join(BOOK, 'scenes', 'looks.json')          # {键: [前头哪一幅的键, 那一幅里要照着画的是谁（英文）]}
REVIEW = os.path.join(BOOK, 'scenes', 'review.json')
OUT = os.path.join(HERE, 'out', '门面_原画_此刻')
BAK = os.path.join(OUT, '备选')
HOME_NOW = os.path.join(os.path.expanduser('~'), '.codex')      # 这一本只用默认这个号，~/.codex_b 留给迷宫纪那一本
G.OUT = OUT                                                      # 对照条（_ident）放这一边
if '立绘_v3' not in G.POR_ALL:
    G.POR_ALL.append('立绘_v3')

# 1001 年：剑与魔法照旧，添了魔导和蒸汽。列车、空艇、煤气灯、魔导灯是这个年代的东西，别的现代物件照旧不画。
TAIL_NOW = ("Everyone is fully and modestly clothed; nothing is sexualized. %s"
            "The world is Western high fantasy of swords and magic, in a late age of brass, steam and arcane engines: gas lamps and glowing crystal lamps, armoured steam trains on rails, "
            "wooden and brass airships with sails, clockwork and riveted iron belong to it. Clothes, armour and buildings are European fantasy: no East Asian garments, roofs or motifs. "
            "Nothing from the real modern world: no cars, no phones, no screens, no neon, no plastic, no modern firearms, no modern uniforms. "
            "Dragons are heavy Western wyrms with bat-like wings, no antlers, no whiskers. "
            "There is no moon and no crescent anywhere in the picture. No text, no letters, no numbers, no logo, no watermark, no frame, no border, no caption, no user interface. "
            "Landscape picture, wider than tall, aspect ratio 3:2, the painting filling the whole frame edge to edge.")
PLACE = ("The last attached picture shows the place of this scene as it has been painted before, in another, more painterly rendering and from another viewpoint. "
         "Use it only for the look of the place: its architecture, its landmarks and its colours. Redraw the place in the clean Light Cone rendering of the style references, "
         "from the viewpoint the scene below describes. Do not copy that picture's composition, and add nothing from it that the scene does not name. ")
# 没有立绘的任务人物（露希亚、菲雅、卡萝……）：同一条主线里前头审过的那一幅当参考，几幅里才是同一个人
LOOK = ("The last attached picture is an approved plate of this same story, painted earlier in the same series. It shows %s: draw the same individual here, "
        "with the same face, hair colour and hairstyle, eye colour, build and clothes, so that the two plates plainly show one and the same person or creature. "
        "Take nothing else from that picture: not its composition, its poses, its setting, its light or its other figures. ")


class NotReady(Exception):
    pass


# 下面几条照 gpt_cg3.py（11-14 山铜纪试画查出来的）
FOLK = {
    'night-wing': "A night-wing is a person of a winged demon-kin people: a man or woman of ordinary human size and shape with a pair of large dark wings growing from the back, most often membranous like a bat's, sometimes feathered; never a dragon, a bat or a bird. ",
    'fire-horn': "A fire-horn is a person of a horned demon-kin people, ordinary human size and shape with horns on the head that may glow or burn like torches; never a beast. ",
    'bone folk': "The bone folk are a tall, pale demon-kin people with bone-white skin; they are living people, not skeletons. ",
    'beast-eared': "A beast-eared person is an ordinary human in every way except for a pair of animal ears on top of the head, in place of human ears, and a tail; the face is fully human, with no muzzle and no fur on the skin. ",
    'dragonkin': "A dragonkin is a person of ordinary human shape with a few patches of fine scales on the skin (temples, neck, backs of the hands); a fully human face, no muzzle, no wings, no tail unless the scene says so. ",
    'sea-folk': "The sea-folk are people of ordinary human shape with faint gill lines on the sides of the neck and a few fine scales; two legs, no fish tail. ",
}
BOW_RX = re.compile(r'\bbows?\b|bowstring|\barchers?\b|\barrows?\b')
CUT_BOW = ("Archery is drawn correctly. A bow is gripped at its middle by the bow hand. The bowstring is one single string: on a drawn bow it runs straight from the upper tip of the bow "
           "to the fingers of the drawing hand, and from those same fingers straight to the lower tip, so the two halves of the string meet at one point inside the drawing hand, "
           "and the back end of the arrow sits on the string at that point. An undrawn bow has one straight string from tip to tip. ")
CUT_FEEL = ("Every face shows the feeling the scene gives that person: nobody grins or laughs unless the scene says so, and people running from danger look afraid, desperate or grimly set. ")
CUT_COUNT = "Where the scene gives a number of people, draw exactly that many. "
CUT_HEADBAND = "A band or strip of cloth tied round someone's head sits on the forehead above the eyes and never covers the eyes, unless the scene says the eyes are covered. "
CUT_WOUND = "Wounds are only where the scene puts them; there is no cut across the inside of any wrist or forearm. "
# 英雄、传奇、巨物出手：先画天地的反应（用户定的：超凡要写出世界级的表现力）
CUT_SCALE = ("Scale is shown boldly: where the scene names something vast (a giant, a dragon, a storm, a tower, a wave, a spell), it is truly vast, cut off by the edges of the frame, "
             "and the sky, the ground, the water and the light around it visibly react to it. ")

S, ORDER = {}, []


def load():
    import glob
    nodes = []
    for f in sorted(glob.glob(os.path.join(SCENES, 'now_*.json'))):
        nodes += json.load(open(f, encoding='utf-8'))['nodes']
    looks = json.load(open(LOOKS, encoding='utf-8')) if os.path.exists(LOOKS) else {}
    for s in nodes:
        if s['key'] in S:
            raise ValueError('键重了：' + s['key'])
        e = dict(style=tuple(s['style']), light=s['light'], camera=s['camera'], text=s['text'], raw=bool(s.get('raw')), young=bool(s.get('young') or s.get('minor')),
                 line=s['line'], act=s['act'], round=s.get('round', 2), place=s.get('place'))
        ppl = [tuple(x) for x in (s.get('row') or s.get('who') or [])]
        if s.get('row'):
            e['row'] = ppl
        elif ppl:
            e['who'] = ppl
        if e['young']:
            e['raw'] = False
        if s['key'] in looks:
            e['look'] = tuple(looks[s['key']])
        S[s['key']] = e
    ORDER[:] = sorted(S, key=lambda k: (S[k]['round'], k))


def place_png(rel):
    """地方的参考图：小样_此刻书/assets/ 底下那张 webp 转成 png 放 _ident/（Codex 的 -i 不一定认 webp）。"""
    src = rel if os.path.isabs(rel) else os.path.join(BOOK, 'assets', rel)
    os.makedirs(os.path.join(OUT, '_ident'), exist_ok=True)
    dst = os.path.join(OUT, '_ident', 'place_' + re.sub(r'\W+', '_', os.path.splitext(os.path.basename(src))[0]) + '.png')
    if not os.path.exists(dst):
        im = Image.open(src).convert('RGB')
        if im.width > 1536:
            im = im.resize((1536, round(im.height * 1536 / im.width)), Image.LANCZOS)
        im.save(dst)
    return dst


def job(key):
    s = S[key]
    style = [os.path.join(G.LC, n + '.png') for n in s['style']]
    refs, who = list(style), ''
    if s.get('row'):
        refs.append(G.lineup(key + '_row', [(k, c) for k, c, _ in s['row']]))
        who = G.ROW % '; '.join(d for _, _, d in s['row'])
    elif s.get('who'):
        refs += [G.ident(k, c) for k, c, _ in s['who']]
        who = G.ONE if len(s['who']) == 1 else G.MANY % (len(s['who']), '; '.join(d for _, _, d in s['who']))
    look = ''
    if s.get('look'):
        lk, who_ = s['look']
        rv = json.load(open(REVIEW, encoding='utf-8')) if os.path.exists(REVIEW) else {}
        lp = os.path.join(OUT, lk + '.png')
        if rv.get(lk) == 'hold':          # 那一幅留空了：不等它，照字画
            pass
        elif not os.path.exists(lp) or rv.get(lk) != 'ok':
            raise NotReady(lk)          # 那一幅还没出、还没审过或者正在重画：这一幅先不开
        else:
            refs.append(lp)
            look = LOOK % who_
    if s.get('place') and not look:
        refs.append(place_png(s['place']))
    if len(refs) > 5:
        raise ValueError('参考图多于五张：' + key)
    p = ((G.LEAD_CUT % len(style)) + (G.LOOK % (s['light'], s['camera'])) + who + (G.POSE + G.DIFF if who else '') + (PLACE if s.get('place') and not look else '') + look
         + s['text'] + ' ' + CUT_SCALE + G.FACE + G.BODY + (G.YOUNG if s['young'] else '') + (TAIL_NOW % (G.RAW if s['raw'] else G.CALM)))
    p += ' ' + CUT_FEEL + CUT_COUNT + CUT_HEADBAND
    if BOW_RX.search(s['text']):
        p += CUT_BOW
    if s['raw']:
        p += CUT_WOUND
    p += ''.join(v for k, v in FOLK.items() if k in s['text'])
    return p, refs


STOP = []
FAILS = {}          # 键: 不是额度的失败回数（出图服务挡了、超时、没图），三回就先放下
GIVE_UP = 3


def log_text(key):
    try:
        return open(os.path.join(OUT, key + '.log'), encoding='utf-8', errors='replace').read()
    except OSError:
        return ''


def limited(key):
    t = log_text(key).lower()
    return 'usage_limit' in t or 'usage limit' in t or ('rate limit' in t and 'try again' in t)


def reset_wait(key):
    """撞额度那一幅的日志里要是写了恢复的时候（resets_at 一个纪元秒，或者 resets_in_seconds），回还要等几秒；没写回 None。"""
    t = log_text(key)
    m = re.search(r'resets?_at\D{0,6}(\d{9,11})', t)
    if m:
        return max(0, int(m.group(1)) - time.time())
    m = re.search(r'resets?_in_seconds\D{0,6}(\d+)', t)
    if m:
        return int(m.group(1))
    return None


def stamp():
    return time.strftime('%m-%d %H:%M:%S')


def have(key):
    return os.path.exists(os.path.join(OUT, key + '.png'))


def one(key):
    if STOP:
        return
    if have(key):
        return
    try:
        os.makedirs(OUT, exist_ok=True)
        try:
            p, refs = job(key)
        except NotReady:
            return
        t0 = time.time()
        out = gen(os.path.join(OUT, key), p, refs=refs, timeout=1500, home=HOME_NOW)
        print(stamp(), '好了', key, '%d 秒' % (time.time() - t0), [os.path.basename(o) for o in out], flush=True)
    except Exception as e:
        if limited(key):
            if not STOP:
                STOP.append(key)
                print(stamp(), '== 撞了出图额度，不再开新的', key, flush=True)
            return
        FAILS[key] = FAILS.get(key, 0) + 1
        print(stamp(), '失败（第 %d 回）' % FAILS[key], key, str(e)[:300], flush=True)


def redo(key):
    """整张重画：旧图和日志挪进 备选/<键>_r<旧版次>.png，版次加一。只挪，不出图（队列开着它自己会补上，没开就再跑一回）。"""
    rev = json.load(open(REV, encoding='utf-8')) if os.path.exists(REV) else {}
    n = rev.get(key, 0)
    os.makedirs(BAK, exist_ok=True)
    moved = False
    for ext in ('.png', '.log', '_2.png'):
        src = os.path.join(OUT, key + ext)
        if os.path.exists(src):
            shutil.move(src, os.path.join(BAK, '%s_r%d%s' % (key, n, ext)))
            moved = moved or ext == '.png'
    if moved:
        rev[key] = n + 1
        json.dump(rev, open(REV, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, sort_keys=True)
    print('重画', key, '旧图挪进 备选/，版次', rev.get(key, 0))


def pick(args):
    keys = []
    for a in args:
        if a == 'all':
            keys += ORDER
        elif a == 'round1':
            keys += [k for k in ORDER if S[k]['round'] == 1]
        elif a in S:
            keys.append(a)
        elif re.fullmatch(r'L\d+', a):
            keys += [k for k in ORDER if k.startswith('n' + a[1:] + '_')]
        else:
            print('不认得', a)
    seen = set()
    return [k for k in keys if not (k in seen or seen.add(k))]


def run_pass(keys, workers):
    todo = [k for k in keys if not have(k) and FAILS.get(k, 0) < GIVE_UP]
    ready = []
    for k in todo:
        try:
            job(k)
            ready.append(k)
        except NotReady:
            pass
        except Exception:
            ready.append(k)
    if not ready:
        return
    todo = ready
    print(stamp(), '开跑：', len(todo), '幅', flush=True)
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(one, todo))


def loop(args):
    """一直跑到出完：撞了额度就等（日志里有恢复的时候就等到那时候再加五分钟，没有就每二十分钟拿一幅探一回），探通了接着三路并着出。
    每一遍重读场面稿，后添的场面、挪进备选要重画的（--redo）都会接上。不是额度的失败一幅试三回，三回都不成先放下，收工时列出来。"""
    workers = int(os.environ.get('CG_WORKERS', '3'))
    idle = 0
    while True:
        S.clear()
        try:
            load()
        except Exception as e:          # 场面稿正写到一半（JSON 还不全）：等一会儿再读
            print(stamp(), '场面稿读不了，两分钟后再读：', str(e)[:200], flush=True)
            time.sleep(120)
            continue
        keys = pick(args)
        left = [k for k in keys if not have(k) and FAILS.get(k, 0) < GIVE_UP]
        if not left:
            idle += 1
            if idle == 1:
                gone = [k for k in keys if not have(k)]
                print(stamp(), '眼下的都出完了，共', len(keys), '幅；三回不成放下的：', ' '.join(gone) or '无', '。等新的场面稿和重画（--redo），十分钟看一回', flush=True)
            if os.path.exists(os.path.join(OUT, 'STOP')):
                print(stamp(), '见到 STOP 文件，收工', flush=True)
                return
            time.sleep(600)
            continue
        idle = 0
        STOP.clear()
        n0 = sum(1 for k in left if have(k))
        run_pass(left, workers)
        if not STOP and sum(1 for k in left if have(k)) == n0:          # 一幅没出：都在等前头那一幅审过，或者都失败了
            time.sleep(60)
        if STOP:
            w = reset_wait(STOP[0])
            if w is not None:
                w += 300
                print(stamp(), '== 额度：日志里写了恢复的时候，等 %d 分钟' % (w // 60), flush=True)
            else:
                w = 1200
                print(stamp(), '== 额度：没写恢复的时候，二十分钟后拿一幅探', flush=True)
            # 探：一回一幅，通了才放开并着出
            while True:
                time.sleep(max(60, w))
                S.clear()
                try:
                    load()
                except Exception:
                    w = 120
                    continue
                left = [k for k in pick(args) if not have(k) and FAILS.get(k, 0) < GIVE_UP]
                if not left:
                    break
                STOP.clear()
                k = left[0]
                for ext in ('.log',):          # 上一回撞额度的日志挪开，免得这一回没撞也读成撞了
                    p_ = os.path.join(OUT, k + ext)
                    if os.path.exists(p_):
                        os.replace(p_, os.path.join(OUT, k + '.quota.log'))
                print(stamp(), '探一幅', k, flush=True)
                one(k)
                if have(k):
                    print(stamp(), '== 探通了，接着出', flush=True)
                    break
                if not STOP:          # 不是额度的失败：换下一幅接着探
                    w = 60
                    continue
                w2 = reset_wait(k)
                w = (w2 + 300) if w2 is not None else 1200
                print(stamp(), '== 还没恢复，再等 %d 分钟' % (w // 60), flush=True)
        if os.path.exists(os.path.join(OUT, 'STOP')):
            print(stamp(), '见到 STOP 文件，收工', flush=True)
            return


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    load()
    args = sys.argv[1:]
    if args[:1] == ['--left']:
        keys = pick(args[1:] or ['all'])
        left = [k for k in keys if not have(k)]
        print(' '.join(left))
        print('共', len(keys), '缺', len(left))
        sys.exit(0)
    if args[:1] == ['--redo']:
        for k in pick(args[1:]):
            redo(k)
        sys.exit(0)
    if args[:1] == ['--loop']:
        loop(args[1:] or ['all'])
        sys.exit(0)
    keys = pick(args)
    if not keys:
        print('键：', ' '.join(ORDER))
        sys.exit(0)
    if os.environ.get('CG_DRY'):
        for k in keys:
            try:
                p, refs = job(k)
            except NotReady as e:
                print('==', k, '在等前头那一幅审过：', e)
                continue
            print('==', k, len(p), '字', [os.path.basename(r) for r in refs])
            print(p)
        sys.exit(0)
    run_pass(keys, int(os.environ.get('CG_WORKERS', '3')))
    left = [k for k in keys if not have(k)]
    print(stamp(), '收工：还缺', len(left), ' '.join(left), flush=True)
