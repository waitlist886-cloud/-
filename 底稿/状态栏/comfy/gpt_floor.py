#!/usr/bin/env python3
# 此刻那一本（迷宫纪 1001 年）图鉴：楼层主十七位各阶、十王与凯斯珀的原画（11-26）。图出在 out/门面_楼层主/<键>.png（不进库），2:3。
# 提示词在 epic/prompts/floor_now.json（每一遍重读，改了字重画就照新的）。画法照史诗战那一套（gpt_epic.py 的 MJ 画法、HEAVY_MJ、NEXT2、CAMERA、WEST、FACE_JRPG），
# 收尾添这一本的护栏（不画十字、月牙、字、现代的东西）。同一位第二阶起拿上一阶当参考，上一阶在 review.json 里写了 ok 才开（审过的才当底子）。
#   python -I -X utf8 gpt_floor.py --loop            队列：两路并着出，撞了额度换另一个号（~/.codex、~/.codex_b），都撞了等恢复；放 out/门面_楼层主/STOP 收工
#   python -I -X utf8 gpt_floor.py --dry 键…         只打提示词和参考图
#   python -I -X utf8 gpt_floor.py --left            还缺哪几张、哪几张在等上一阶审过
#   python -I -X utf8 gpt_floor.py --ok 键…          审过（写 review.json）
#   python -I -X utf8 gpt_floor.py --redo 键…        整张重画：旧图挪进 备选/<键>_r<版次>.png，版次加一，review 里那一条拿掉（队列开着自己补上）
#   python -I -X utf8 gpt_floor.py --hold 键…        三回不对，留空
import json
import os
import re
import shutil
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_gen  # noqa: E402
import gpt_epic as E  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
PROMPTS = os.path.join(HERE, 'epic', 'prompts', 'floor_now.json')
OUT = os.path.join(HERE, 'out', '门面_楼层主')
BAK = os.path.join(OUT, '备选')
REVIEW = os.path.join(OUT, 'review.json')
REV = os.path.join(OUT, 'rev.json')
HOMES = [h for h in (os.path.join(os.path.expanduser('~'), '.codex'), os.path.join(os.path.expanduser('~'), '.codex_b')) if os.path.exists(os.path.join(h, 'auth.json'))]
WORKERS = int(os.environ.get('FB_WORKERS', '2'))          # 风月封面那一边也在用 Codex，这里至多两路

# 人那么大的对手：画大、在中景，冒险者小、在边上，脸照描述（写了藏着的照藏）
COMP_PERSON = ('Composition: the enemy here is of human size or only a little larger, not a colossus: draw them large and imposing in the middle ground, seen from a slightly low angle, filling much of the height of the picture, '
               'with the place around them grand and clearly readable; any adventurers are small, at the lower edge or to one side, seen from behind, and never cover the enemy. '
               'Unless the description says the face is hidden, masked or lost in light, the face is clearly visible. ')
# 醒过来、收着手的那几阶（奥里恩二阶、兹密伊三阶、拉奇埃尔二阶……）：分量还在，不再是吓人的那一种
CALM = ('This picture is the key art of a boss of a Western fantasy RPG at the solemn turning point of its battle: the being is still majestic and overwhelming in presence, '
        'but the mood is grave, sorrowful and luminous rather than menacing, like the last act of a great tragedy. ')
SAME_PLACE = ('The LAST attached picture shows the previous phase of this same battle in this same place: keep the same plaza, the same architecture, the same light and the same rendering. '
              'The figure is now a different monarch, as described here: do NOT copy that picture\'s composition, pose or figure; use a new camera angle and a new moment. ')
GUARD = (' There is no cross-shaped emblem, pendant, ornament, window, spire or grave marker anywhere in the picture: holy emblems are suns with straight rays, stars, flames, wings, chalices or keys. '
         'Nothing from the real modern world: no cars, guns, screens, plastic or modern uniforms. Dragons are heavy Western wyrms with four limbs and bat-like wings, no antlers, no whiskers. '
         'Abyss matter, where it appears, is black, thick and glossless and reflects no light. Runes, inscriptions and data are abstract glowing patterns, never readable letters or numbers. '
         'No moon, no crescent, no text, no letters, no numbers, no logo, no watermark, no frame, no border.')


def load():
    data = json.load(open(PROMPTS, encoding='utf-8'))
    jobs, order = {}, []
    for b in data['beings']:
        n_ph = len(b['phases'])
        for p in b['phases']:
            key = '%s_%d' % (b['id'], p['no']) if n_ph > 1 or not b['id'].startswith('k') else b['id']
            prev = '%s_%d' % (b['id'], p['no'] - 1) if p['no'] > 1 else None
            pref = p.get('person_ref') if 'person_ref' in p else b.get('person_ref')
            pr = E.person_refs(pref) if pref else []
            lead = (E.PERSON if pr else '')
            if prev:
                lead += SAME_PLACE if p.get('same_place') else (E.NEXT2 + E.CAMERA.get(p['no'], ''))
            comp = COMP_PERSON if b['kind'] == 'person' else E.MJ_COMP
            dead = E.DEAD if re.search(r'\bdead\b|echo|corpse|drowned|fallen', p['prompt']) else ''
            text = (E.MJ_TEXT + (CALM if p.get('calm') else E.HEAVY_MJ) + comp + lead + b['design'] + ' ' + p['prompt'] + E.END + dead + E.WEST + E.FACE_JRPG + GUARD
                    + ((' ' + p['fix']) if p.get('fix') else ''))
            jobs[key] = dict(text=text, refs=list(E.MJ_REFS) + pr, prev=prev, no=p['no'])
            order.append(key)
    # 头一阶先出（审完才放后几阶），再按次序
    pos = {k: i for i, k in enumerate(order)}
    order.sort(key=lambda k: (jobs[k]['no'] > 1, pos[k]))
    return jobs, order


def rj(p):
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def wj(p, d):
    json.dump(d, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, sort_keys=True)


def img(k):
    return os.path.join(OUT, k + '.png')


def have(k):
    return os.path.exists(img(k))


def stamp():
    return time.strftime('%m-%d %H:%M:%S')


def ready(k, jobs, rv):
    pv = jobs[k]['prev']
    return pv is None or (rv.get(pv) == 'ok' and have(pv))


def log_text(k):
    try:
        return open(os.path.join(OUT, k + '.log'), encoding='utf-8', errors='replace').read()
    except OSError:
        return ''


def limited(k):
    t = log_text(k).lower()
    return 'usage_limit' in t or 'usage limit' in t or ('rate limit' in t and 'try again' in t) or ' 429' in t


def reset_wait(k):
    t = log_text(k)
    m = re.search(r'resets?_at\D{0,6}(\d{9,11})', t)
    if m:
        return max(0, int(m.group(1)) - time.time())
    m = re.search(r'resets?_in_seconds\D{0,6}(\d+)', t)
    if m:
        return int(m.group(1))
    m = re.search(r'try again in (?:about )?(\d+)\s*(hour|minute|min)', t, re.I)
    if m:
        return int(m.group(1)) * (3600 if m.group(2).startswith('h') else 60)
    return None


SPENT = {}          # home: 到什么时候再试（纪元秒）
FAILS = {}
LOCK = threading.Lock()


def pick_home():
    now = time.time()
    for h in HOMES:
        if SPENT.get(h, 0) <= now:
            return h
    return None


def one(k, job, home):
    t0 = time.time()
    try:
        out = gpt_gen.gen(os.path.join(OUT, k), job['text'], job['refs'] + ([img(job['prev'])] if job['prev'] else []), 'gpt-6-luna', 'low', 1500, home)
        print(stamp(), '好了', k, os.path.basename(home), '%d 秒' % (time.time() - t0), [os.path.basename(o) for o in out], flush=True)
        return 'ok'
    except Exception as e:   # noqa: BLE001
        if limited(k):
            w = reset_wait(k)
            with LOCK:
                SPENT[home] = time.time() + ((w + 300) if w is not None else 1800)
            print(stamp(), '== 额度', os.path.basename(home), k, '等到', time.strftime('%m-%d %H:%M', time.localtime(SPENT[home])), flush=True)
            q = os.path.join(OUT, k + '.log')
            if os.path.exists(q):
                os.replace(q, os.path.join(OUT, k + '.quota.log'))
            return 'quota'
        FAILS[k] = FAILS.get(k, 0) + 1
        print(stamp(), '失败（第 %d 回）' % FAILS[k], k, str(e)[:300], flush=True)
        return 'fail'


def loop():
    os.makedirs(OUT, exist_ok=True)
    print(stamp(), '开跑，登了', [os.path.basename(h) for h in HOMES], '并', WORKERS, '路', flush=True)
    running = {}
    idle_said = False
    with ThreadPoolExecutor(WORKERS) as ex:
        while True:
            if os.path.exists(os.path.join(OUT, 'STOP')):
                print(stamp(), '见到 STOP，等手上的出完收工', flush=True)
                wait(list(running))
                return
            try:
                jobs, order = load()
            except Exception as e:   # noqa: BLE001
                print(stamp(), '提示词读不了：', str(e)[:200], flush=True)
                time.sleep(60)
                continue
            rv = rj(REVIEW)
            busy = {v[0] for v in running.values()}
            todo = [k for k in order if not have(k) and rv.get(k) != 'hold' and FAILS.get(k, 0) < 3 and k not in busy and ready(k, jobs, rv)]
            while todo and len(running) < WORKERS:
                h = pick_home()
                if not h:
                    break
                k = todo.pop(0)
                running[ex.submit(one, k, jobs[k], h)] = (k, h)
            if not running:
                if not todo:
                    left = [k for k in order if not have(k) and rv.get(k) != 'hold']
                    if not idle_said:
                        print(stamp(), '眼下能出的都出了；还缺', len(left), '张（等上一阶审过或三回失败）：', ' '.join(left), flush=True)
                        idle_said = True
                    time.sleep(60)
                    continue
                t = min(SPENT.values()) - time.time()
                print(stamp(), '== 两个号都撞了额度，等 %d 分钟' % max(1, t // 60), flush=True)
                time.sleep(max(60, t))
                continue
            idle_said = False
            done, _ = wait(list(running), timeout=60, return_when=FIRST_COMPLETED)
            for f in done:
                running.pop(f)


def redo(k):
    rev = rj(REV)
    n = rev.get(k, 0)
    os.makedirs(BAK, exist_ok=True)
    moved = False
    for ext in ('.png', '.log', '_2.png'):
        s = os.path.join(OUT, k + ext)
        if os.path.exists(s):
            shutil.move(s, os.path.join(BAK, '%s_r%d%s' % (k, n, ext)))
            moved = moved or ext == '.png'
    if moved:
        rev[k] = n + 1
        wj(REV, rev)
    rv = rj(REVIEW)
    rv.pop(k, None)
    wj(REVIEW, rv)
    FAILS.pop(k, None)
    print('重画', k, '版次', rev.get(k, 0))


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--loop']:
        loop()
    elif a[:1] == ['--dry']:
        J, _ = load()
        for k in a[1:]:
            j = J[k]
            print('==', k, len(j['text']), '字', [os.path.basename(r) for r in j['refs']] + ([j['prev']] if j['prev'] else []))
            print(j['text'])
    elif a[:1] == ['--left']:
        J, O = load()
        rv = rj(REVIEW)
        print('共', len(O), '张；出了', sum(have(k) for k in O), '；审过', sum(rv.get(k) == 'ok' for k in O), '；留空', [k for k in O if rv.get(k) == 'hold'])
        print('缺：', ' '.join(k for k in O if not have(k)))
        print('出了没审：', ' '.join(k for k in O if have(k) and k not in rv))
    elif a[:1] in (['--ok'], ['--hold']):
        rv = rj(REVIEW)
        for k in a[1:]:
            rv[k] = a[0][2:]
        wj(REVIEW, rv)
        print(a[0], a[1:])
    elif a[:1] == ['--redo']:
        for k in a[1:]:
            redo(k)
    else:
        print(__doc__ or '看文件头')
