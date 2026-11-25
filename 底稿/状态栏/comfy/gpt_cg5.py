#!/usr/bin/env python3
# 门面第四本书（迷宫纪）主线各幕的节点原画（11-25），都出在 out/门面_原画_迷宫纪_节点/（不进库）。
# 那一本原来只有一条主线一幅的壁画（gpt_cg4.py），这一回照山铜纪那一本给每条主线的一幕、二幕、三幕、收束各配一幅节点原画。
# 场面在 底稿/门面/小样_迷宫纪书/scenes/n1.json 到 n6.json（nodes 一幕一幅；lead 写 true 的是这一条主线头一轮先出的那一幅）。
# 画法照 gpt_cg.py 那一套（崩铁光锥，人体护栏 BODY、POSE 在 G.job 里），后头添的几条护栏照 gpt_cg3.py（不引它，只从它的源码里把那几个常数读出来）。
#   python gpt_cg5.py lead            头一轮：每条主线先出一幅（出过的跳过）
#   python gpt_cg5.py rest            别的幕
#   python gpt_cg5.py all             全部
#   python gpt_cg5.py q3 q1_a3        第三页那几幅，加指定的一幅；lead q1 q2 是这两页里头一轮的那几幅
#   python gpt_cg5.py --left [lead]   还缺哪几幅
#   python gpt_cg5.py --queue         队列：一直跑到全部出完。先头一轮（四十四条都有了才出别的幕），撞了额度等到恢复再接着出；
#                                     每一圈重读场面稿（新写的、--redo 挪开的都会补上）。平常就用它，bash run_1125_maze.sh 起。
#   python gpt_cg5.py --spawn         起一个脱开的 --queue 进程就回（run_1125_maze.sh 用的就是它）；--alive 看队列在不在跑。
#                                     要它停：在 out/门面_原画_迷宫纪_节点/ 里放一个空文件 _停（正在画的那一两张画完就退，歇着的时候十五秒内退）。
# 11-25 接手时改的：出图换成这份脚本自己的 gen5（加 --ephemeral，缘故写在 gen5 的说明里）；Codex 秒退、日志空的认得出，歇够了再试，不空转。
#   python gpt_cg5.py --redo q1_a3 …  重画：把现在这一张和它的日志挪成 <键>_v1.png（再重画是 _v2…），下一回出图就会重出。先改场面稿再跑。
#   CG_DRY=1 只打提示词和参考图，不出图；CG_WORKERS=3 并着出；CODEX_HOME 指到用哪个 Codex 号。
# 要带 PIL 的 Python（ComfyUI 那一个）。撞了出图额度就不再开新的，等额度回来原样再跑一遍，只补缺的。结果一行一行追加在 out/门面_原画_迷宫纪_节点/_队列.log。
import ast
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gpt_cg as G  # noqa: E402
import gpt_gen as GG  # noqa: E402  只用它找 Codex 的那一行、两句提示词和取图的 pick；出图用这份脚本自己的 gen5

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BOOK = os.path.join(ROOT, '底稿', '门面', '小样_迷宫纪书')
SCENES = os.path.join(BOOK, 'scenes')
OUT = os.path.join(HERE, 'out', '门面_原画_迷宫纪_节点')
QLOG = os.path.join(OUT, '_队列.log')
G.OUT = OUT                                           # 对照条（_ident）放在这一边，照现在的立绘新拼，不用别的书里旧的
G.POR_ALL = ['立绘_前传', '立绘_v3', '立绘_山铜纪', '立绘_纷争纪', '立绘_月银纪史诗', '立绘_诸国期', '立绘_萨尔维斯']


def _consts(path, names):
    """从一份脚本的源码里读出几个顶层的字符串常数、字典常数，不执行它。"""
    out = {}
    for node in ast.parse(open(path, encoding='utf-8').read()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except Exception:
                pass
    return out


_C = _consts(os.path.join(HERE, 'gpt_cg3.py'), {'CUT_BOW', 'CUT_FEEL', 'CUT_COUNT', 'CUT_HEADBAND', 'CUT_WOUND', 'FOLK'})
CUT_BOW, CUT_FEEL, CUT_COUNT, CUT_HEADBAND, CUT_WOUND, FOLK = (_C[k] for k in ('CUT_BOW', 'CUT_FEEL', 'CUT_COUNT', 'CUT_HEADBAND', 'CUT_WOUND', 'FOLK'))
BOW_RX = re.compile(r'\bbows?\b|bowstring|\barchers?\b|\barrows?\b')
# 这一本添的：井里的大东西、那一位的投影不画成一张具体的脸；同一条主线先出的那一幅当后几幅的参考（没有立绘的人靠它认）
NO_FACE = ("The great unnatural thing in this scene has no face of its own: draw it only as the scene describes it, as a shape, a darkness, a hand, a tide, "
           "never with a human or monstrous face, eyes or a mouth unless the scene itself names them. ")
LIKE = ("The last attached picture is an earlier approved plate from this same story, in this same rendering: %s appear in it. Keep their faces, hair, colouring, "
        "build and clothes the same as in that plate so that they are recognisably the same people; take nothing else from it, not its composition, its camera, its poses or its setting. ")
SMALL = ("Small marks and seals are never drawn as readable writing: a stamped seal is a small round mark, a notice or a contract is a sheet with fine illegible lines. ")
# 11-25 审图：莫莉背包上的白烛记号叫画成了一枚金十字。这一本不画十字架和十字纹（照壁画那一轮的规矩）
NO_CROSS = ("There is no cross-shaped emblem, pendant, ornament or grave marker anywhere in the picture: nothing on a bag, a robe, a shield or a banner is drawn as a cross; "
            "a healer's emblem is a small candle flame. A sickle or other curved blade is dark dull iron, short, and never a pale shining curve against the sky. ")
# 11-25 第三手审图：q1_b4、q1_d1 把“大井”画成了一口村里的小石井圈。场面里说到那一口大井（迷宫的井口）就添这一句
GREAT_WELL = ("The great well in this scene is the mouth of the Great Labyrinth: one vast round pit in the open ground, several hundred paces across, "
              "so wide that its far rim and anything standing on it look small with distance, its inner walls stepping down ring below ring into darkness. "
              "It is never a small village wellhead, never a little ring of masonry a few steps wide; where the scene names a stone rail, that is a low parapet "
              "running along the vast curving lip, and its curve is gentle because the pit is so large. ")
GREAT_WELL_RX = re.compile(r'great (round )?well|well mouth|mouth of the (great )?well|lip of the well|round mouth of the well')
ACTS = ['一幕', '二幕', '三幕', '收束']

S = {}


def beast_path(name):
    if name.startswith('god_'):
        return os.path.join(HERE, 'out', '神明显像', name + '.png')
    if name.startswith('dragon_'):                  # 真龙的龙形（out/真龙原形/）
        return os.path.join(HERE, 'out', '真龙原形', name + '.png')
    return os.path.join(HERE, 'out', '史诗战', 'maze', name + '.png')


def load():
    age = {}
    dp = os.path.join(BOOK, 'data', 'maze.json')
    if os.path.exists(dp):
        for e in json.load(open(dp, encoding='utf-8'))['eras']:
            for c in e.get('cast', []) + e.get('meet', []):
                if c.get('key') and c.get('age') is not None:
                    age[(e['id'], c['key'])] = c['age']
    flag = set()
    for f in glob.glob(os.path.join(HERE, 'cast', '**', '*.json'), recursive=True):
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        for x in (d if isinstance(d, list) else []):
            if isinstance(x, dict) and x.get('en') and (x.get('minor') or x.get('teen') or x.get('child')):
                flag.add(x['en'])
    for p in sorted(glob.glob(os.path.join(SCENES, 'n?.json'))):
        d = json.load(open(p, encoding='utf-8-sig'))
        for s in d.get('nodes', []):
            e = dict(kind='cut', style=tuple(s['style']), light=s['light'], camera=s['camera'], text=s['text'], raw=bool(s.get('raw')), scene=True,
                     page=d['era'], line=s['line'], act=s['act'], lead=bool(s.get('lead')), differs=True)
            ppl = [tuple(x) for x in (s.get('row') or s.get('who') or [])]
            if s.get('row'):
                e['row'] = ppl
            elif ppl:
                e['who'] = ppl
            if s.get('beast'):
                e['extra'] = [beast_path(s['beast'])]
                e['beast'] = True
            if s.get('minor') or s.get('young') or any(age.get((d['era'], k), 99) < 18 or k in flag for k, _, _ in ppl):
                e['young'] = True
                e['raw'] = False if s.get('minor') else e['raw']
            for f in ('like', 'noface'):
                if s.get(f):
                    e[f] = s[f]
            S[s['key']] = e


load()


def job(key):
    s = S[key]
    G.S[key] = s                 # 提示词照 gpt_cg.py 那一套拼，后头再添山铜纪试画查出来的几条和这一本的几条
    p, refs = G.job(key)
    p += ' ' + CUT_FEEL + CUT_COUNT + CUT_HEADBAND + SMALL + NO_CROSS
    if BOW_RX.search(s['text']):
        p += CUT_BOW
    if s.get('raw'):
        p += CUT_WOUND
    if s.get('noface'):
        p += NO_FACE
    if GREAT_WELL_RX.search(s['text']):
        p += GREAT_WELL
    p += ''.join(v for k, v in FOLK.items() if k in s['text'])
    if s.get('like') and not s.get('beast') and len(refs) < 5:
        lk = os.path.join(OUT, s['like'][0] + '.png')
        if os.path.exists(lk):
            refs = refs + [lk]
            p += LIKE % s['like'][1]
    return p, refs


STOP = []
TRANS = []         # 请求发出去没有回音的（日志里连模型的头一句都没有）：不算这一张的毛病，不计进三回
HOLD = []          # 连着两张没有回音：这一圈剩下的先不开，歇一阵回来只试一张
QUICK = []         # Codex 一起就退、日志里连会话号都没有的：不算这一张的毛病，这一圈剩下的不再开，歇够了回来只试一张
NL = chr(10)       # 这份脚本里不写反斜杠转义：11-25 有一回补丁走了 bash heredoc，引号里的换行转义叫剥成了真换行，整份脚本语法错了
QUICK_SECS = 40    # 不到这么多秒就退、日志里又没有会话号的，算“秒退”
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


class Quick(RuntimeError):
    """Codex 一起就退了：几秒钟，日志是空的或者没有会话号。不是这一张的毛病，是起 Codex 的环境坏了。"""


def gen5(stem, prompt, refs=(), model='gpt-6-luna', effort='low', timeout=900):
    """照 gpt_gen.gen 出一张（那一份是现成的脚本，没动它），11-25 接手时改了四处：
    一，加 --ephemeral。Codex 0.167 把每一回 exec 的会话连参考图一起写进 CODEX_HOME 的 thread_history_1.sqlite，
        .codex_b 那一份涨到了 12GB，又在 C 盘那块机械盘上（另一个号的出图队列同时在刷它自己 31GB 的那一份），
        一回合卡在往这个库里追加那一步，模型的请求根本发不出去，干等到超时。--ephemeral 不落会话，这一步就没有了；
        图照旧存在 CODEX_HOME/generated_images/<会话号>/。
    二，退出码和用时写在日志末尾；几秒钟就退、日志里没有会话号的抛 Quick，队列认得出，不拿它当这一张的失败。
    三，起 Codex 用 CREATE_NO_WINDOW：它自己带一个看不见的控制台，不靠父进程的（父进程的控制台没了，子进程会一起就退）。
    四，超时了连它起的子进程一起结束（taskkill /T）。"""
    if os.path.exists(stem + '.png'):
        return [stem + '.png']
    if not GG.CODEX:
        raise RuntimeError('没找到 Codex')
    if len(refs) > 5:
        raise ValueError('参考图最多五张')
    lost = [r for r in refs if not os.path.exists(r)]
    if lost:
        raise FileNotFoundError('参考图不在：' + '，'.join(lost))
    os.makedirs(os.path.dirname(os.path.abspath(stem)), exist_ok=True)
    log = stem + '.log'
    d = tempfile.mkdtemp(prefix='aldran_codex_')
    cmd = [GG.CODEX[0], 'exec', '--skip-git-repo-check', '--sandbox', 'read-only', '-C', d, '-m', model, '-c', 'model_reasoning_effort="%s"' % effort]
    if not os.environ.get('CG_PERSIST'):
        cmd.insert(2, '--ephemeral')
    for r in refs:
        cmd += ['-i', os.path.abspath(r)]
    cmd += ['--', '$imagegen Use the built-in image generation tool. ' + prompt + (GG.ALL % (len(refs), len(refs)) if refs else '') + GG.ONCE]
    t0, rc = time.time(), None
    try:
        with open(log, 'w', encoding='utf-8') as f:
            p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, creationflags=NO_WINDOW)
            try:
                rc = p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                subprocess.call(['taskkill', '/PID', str(p.pid), '/T', '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=NO_WINDOW)
                try:
                    p.wait(30)
                except subprocess.TimeoutExpired:
                    p.kill()
                rc = '超时'
                raise
    finally:
        shutil.rmtree(d, ignore_errors=True)
        try:
            with open(log, 'a', encoding='utf-8') as f:
                f.write(NL + '[gpt_cg5] 退出码 %s，用时 %d 秒' % (rc, time.time() - t0) + NL)
        except OSError:
            pass
    secs = time.time() - t0
    txt = open(log, encoding='utf-8', errors='replace').read()
    if 'session id:' not in txt:
        head = ' '.join(txt.split('[gpt_cg5]')[0].split())[:160]
        if secs < QUICK_SECS:
            raise Quick('Codex %d 秒就退了，退出码 %s，日志里%s' % (secs, rc, ('是：' + head) if head else '什么都没有'))
        raise RuntimeError('Codex 跑了 %d 秒，退出码 %s，日志里没有会话号：%s' % (secs, rc, head))
    out = GG.pick(log, stem)
    if not out:
        raise RuntimeError('Codex 退出码 %s，没有出图，看 %s' % (rc, log))
    return out


def note(*a):
    line = time.strftime('%m-%d %H:%M:%S ') + ' '.join(str(x) for x in a)
    print(line, flush=True)
    try:
        os.makedirs(OUT, exist_ok=True)
        with open(QLOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except OSError:
        pass


PIDF = os.path.join(OUT, '_队列.pid')


def queue_pid():
    """队列进程在不在：读 _队列.pid，再问系统这个进程号是不是还活着的 python。在就回进程号，不在回 0。"""
    try:
        pid = int(open(PIDF, encoding='utf-8').read().strip())
    except (OSError, ValueError):
        return 0
    if pid == os.getpid():
        return 0
    try:
        t = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid, '/FO', 'CSV', '/NH'], capture_output=True, text=True, errors='replace', creationflags=NO_WINDOW, timeout=60).stdout
    except Exception:
        return 0
    return pid if 'python' in t.lower() else 0


class StopAsked(Exception):
    pass


def stop_asked():
    return os.path.exists(os.path.join(OUT, '_停'))


def nap(secs):
    """歇 secs 秒；中间有人放了 _停 就不等了。"""
    end = time.time() + secs
    while time.time() < end:
        if stop_asked():
            raise StopAsked()
        time.sleep(min(15, max(0.1, end - time.time())))


def limited(key):
    try:
        t = open(os.path.join(OUT, key + '.log'), encoding='utf-8', errors='replace').read().lower()
    except OSError:
        return False
    return 'usage_limit' in t or 'usage limit' in t


def answered(key):
    """这一张的请求模型回过话没有（Codex 的日志里模型开口那一行是单独一行 codex）。"""
    try:
        return (NL + 'codex' + NL) in open(os.path.join(OUT, key + '.log'), encoding='utf-8', errors='replace').read().replace(chr(13) + NL, NL)
    except OSError:
        return False


def one(key):
    if STOP:
        note('没开（撞了出图额度）', key)
        return
    if HOLD or QUICK or stop_asked():
        return
    if os.path.exists(os.path.join(OUT, key + '.png')):
        return
    try:
        os.makedirs(OUT, exist_ok=True)
        p, refs = job(key)
        t0 = time.time()
        out = gen5(os.path.join(OUT, key), p, refs=refs, timeout=int(os.environ.get('CG_TIMEOUT', '1800')))      # 画一张两到五分钟；Codex 起来那一下要先查一遍它那个 12GB 的库，C 盘忙的时候光这一步就七八分钟（11-25 头一张 617 秒）
        note('好了', key, '%d 秒' % (time.time() - t0), [os.path.basename(x) for x in out])
        del TRANS[:]
    except Quick as e:
        QUICK.append(key)
        note('秒退', key, str(e)[:200])
    except Exception as e:
        if not STOP and limited(key):
            STOP.append(key)
            note('== 撞了出图额度，不再开新的')
        if not STOP and not answered(key):
            TRANS.append(key)
            if len(TRANS) >= 2 and not HOLD:
                HOLD.append(key)
            note('没有回音', key, '（请求发出去模型没回话，%s）' % type(e).__name__)
        else:
            note('失败', key, str(e)[:200])


def reset_wait(key):
    """撞了额度：从那一张的日志里找恢复的时刻（try again at Nov 23rd, 2026 11:58 AM. 或 try again in 3 hours 20 minutes），回还要等多少秒；找不到回 None。"""
    from datetime import datetime, timedelta
    try:
        t = open(os.path.join(OUT, key + '.log'), encoding='utf-8', errors='replace').read()
    except OSError:
        return None
    m = re.search(r'try again in\s+((?:\d+\s*(?:days?|hours?|hrs?|minutes?|mins?|seconds?|secs?)[,\s]*(?:and\s*)?)+)', t, re.I)
    if m:
        unit = {'day': 86400, 'hour': 3600, 'hr': 3600, 'minute': 60, 'min': 60, 'second': 1, 'sec': 1}
        return sum(int(n) * unit[u.lower()] for n, u in re.findall(r'(\d+)\s*(day|hour|hr|minute|min|second|sec)', m.group(1), re.I))
    m = re.search(r'try again at\s+([^\n]+?)\s*(?:\.\s|\.$|\n|$)', t, re.I | re.M)
    if m:
        s = re.sub(r'(\d)(st|nd|rd|th)\b', r'\1', m.group(1).strip().rstrip('.'))
        now = datetime.now()
        for fmt in ('%b %d, %Y %I:%M %p', '%B %d, %Y %I:%M %p', '%b %d %Y %I:%M %p', '%I:%M %p', '%H:%M'):
            try:
                dt = datetime.strptime(s, fmt)
            except ValueError:
                continue
            if dt.year == 1900:
                dt = dt.replace(year=now.year, month=now.month, day=now.day)
                if dt < now:
                    dt += timedelta(days=1)
            return max(0, (dt - now).total_seconds())
    return None


def queue(workers, lines_total, acts_total):
    """一直跑到全部出完（11-25 用户：撞了额度就等重置了继续）。每一圈重读场面稿：先出头一轮的（每条主线一幅），
    头一轮的场面没写齐、图没出齐以前不出别的幕；撞了额度，日志里有恢复时刻就等到那时候，没有就隔二十分钟，回来先只试一张，试通了再并着出。
    同一张不是因为额度连着三回没出来就先放下（末尾列出来）。OUT 里放一个名叫 _停 的文件，这一圈跑完就退。"""
    fails, probe, rounds, quick_n, idle = {}, False, 0, 0, 0
    have = lambda k: os.path.exists(os.path.join(OUT, k + '.png'))
    while True:
        if stop_asked():
            note('== 看见 _停，队列退了')
            return
        S.clear()
        try:
            load()
        except Exception as e:                       # 场面稿正写到一半、JSON 还不全
            note('场面稿读不了，过五分钟再读：', str(e)[:120])
            nap(300)
            continue
        leads = [k for k in order(S) if S[k]['lead']]
        batch = [k for k in leads if not have(k) and fails.get(k, 0) < 3]
        phase = '头一轮'
        if not batch and [k for k in leads if not have(k)] and rounds < 6:          # 头一轮里有连着三回没出来的：歇二十分钟再给三回，不拿它们挡着别的幕太久
            rounds += 1
            stuck = [k for k in leads if not have(k)]
            note('== 头一轮有 %d 幅连着三回没出来，歇二十分钟再试（第 %d 轮）：' % (len(stuck), rounds), ' '.join(stuck))
            nap(1200)
            for k in stuck:
                fails.pop(k, None)
            continue
        if not batch:
            if len(leads) < lines_total:
                note('头一轮的场面还没写齐（%d／%d 条），十分钟以后再看' % (len(leads), lines_total))
                nap(600)
                continue
            phase = '别的幕'
            batch = [k for k in order(S) if not S[k]['lead'] and not have(k) and fails.get(k, 0) < 3]
            stuck = [k for k in S if not have(k) and fails.get(k, 0) >= 3]
            if not batch and stuck and rounds < 6:          # 三回没出来的（多半是网断了、出图服务那一头超时）：歇二十分钟，从头再给三回，至多再给六轮
                rounds += 1
                note('== 有 %d 幅连着三回没出来，歇二十分钟再试（第 %d 轮）：' % (len(stuck), rounds), ' '.join(stuck[:20]))
                nap(1200)
                for k in stuck:
                    fails.pop(k, None)
                continue
            if not batch:
                if len(S) < acts_total:
                    if idle % 6 == 0:                      # 一个钟头记一行，别把日志刷满
                        note('别的幕的场面还没写齐（%d／%d 幅），写了的都出过了，十分钟看一回有没有新的' % (len(S), acts_total))
                    idle += 1
                    nap(600)
                    continue
                break
        idle = 0
        if probe:
            batch = batch[:1]
        del STOP[:]
        del TRANS[:]
        del HOLD[:]
        del QUICK[:]
        note('== %s，这一圈出 %d 幅%s：%s' % (phase, len(batch), '（试一张）' if probe else '', ' '.join(batch[:12]) + (' …' if len(batch) > 12 else '')))
        t_batch = time.time()
        with ThreadPoolExecutor(1 if probe else workers) as ex:
            list(ex.map(one, batch))
        got = sum(1 for k in batch if have(k))
        if got:
            quick_n = 0
        if stop_asked():
            continue
        if STOP:
            w = reset_wait(STOP[0])
            note('== 撞了额度，%s' % ('日志里写了恢复的时刻，等 %d 分钟' % (w // 60 + 2) if w is not None else '日志里没写什么时候恢复，等二十分钟'), '再试一张')
            nap((w + 120) if w is not None else 1200)
            probe = True
        elif QUICK:
            # Codex 一起就退、日志空：不是哪一张的毛病（11-25 那一夜这样空转了九百多行，一秒三张）。这一圈剩下的已经没再开，
            # 歇十分钟回来只试一张，连着还是这样就二十、四十、六十分钟地歇；不记进各张的三回里。
            quick_n += 1
            w = min(600 * 2 ** (quick_n - 1), 3600)
            note('== Codex 一起就退（连着第 %d 回），不是哪一张的毛病，歇 %d 分钟，回来先试一张。日志看 %s.log' % (quick_n, w // 60, QUICK[0]))
            nap(w)
            probe = True
        elif HOLD or (TRANS and not got):
            note('== 出图那一头没有回音（%s），歇十分钟，回来先试一张' % ' '.join(TRANS[:4]))
            nap(600)
            probe = True
        else:
            probe = False
            for k in batch:
                if not have(k) and k not in TRANS:
                    fails[k] = fails.get(k, 0) + 1
            if not got and time.time() - t_batch < 120:      # 兜底：一圈不到两分钟、一张没出，不管报的是什么都先歇着，不空转
                note('== 这一圈不到两分钟、一张没出，歇十分钟，回来先试一张')
                nap(600)
                probe = True
    gone = sorted(k for k, n in fails.items() if n >= 3 and not have(k))
    note('== 队列全出完了，场面', len(S), '幅，有图', sum(1 for k in S if have(k)), '幅' + ('；三回没出来放下的：' + ' '.join(gone) if gone else ''))


def redo(keys):
    for k in keys:
        src = os.path.join(OUT, k + '.png')
        if not os.path.exists(src):
            print('没有这一张', k)
            continue
        n = 1
        while os.path.exists(os.path.join(OUT, '%s_v%d.png' % (k, n))):
            n += 1
        os.replace(src, os.path.join(OUT, '%s_v%d.png' % (k, n)))
        lg = os.path.join(OUT, k + '.log')
        if os.path.exists(lg):
            os.replace(lg, os.path.join(OUT, '%s_v%d.log' % (k, n)))
        for extra in glob.glob(os.path.join(OUT, k + '_[0-9].png')):     # Codex 多画的那一张也挪开
            os.replace(extra, extra[:-4] + '_v%d.png' % n)
        print('挪开了', k, '→ _v%d' % n)


def order(keys):
    """先后：头一轮的在前，再照页、主线、幕的次序。"""
    return sorted(keys, key=lambda k: (0 if S[k]['lead'] else 1, k[:-1], ACTS.index(S[k]['act'])))


def pick(args):
    pages = [a for a in args if re.fullmatch(r'q\d', a)]
    keys = set(a for a in args if a in S)
    mode = [a for a in args if a in ('lead', 'rest', 'all')]
    for k, s in S.items():
        if pages and s['page'] not in pages:
            continue
        if 'all' in mode or ('lead' in mode and s['lead']) or ('rest' in mode and not s['lead']) or (pages and not mode):
            keys.add(k)
    return order(keys)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[:1] == ['--left']:
        keys = pick(args[1:] or ['all'])
        left = [k for k in keys if not os.path.exists(os.path.join(OUT, k + '.png'))]
        print(' '.join(left))
        print('缺', len(left), '／', len(keys), '；场面一共', len(S), '，其中头一轮', sum(1 for s in S.values() if s['lead']))
        sys.exit(0)
    if args[:1] == ['--redo']:
        redo(args[1:])
        sys.exit(0)
    if args[:1] == ['--spawn']:
        # 起一个跟这个终端脱开的队列进程（自己带一个看不见的控制台、自己一个进程组），起完就回。派它的会话没了它照旧跑。
        os.makedirs(OUT, exist_ok=True)
        os.makedirs(os.path.join(HERE, 'out', '日志'), exist_ok=True)
        pid = queue_pid()
        if pid:
            print('队列已经在跑，进程号', pid, '；要停：在', OUT, '里放一个空文件 _停，或者 taskkill /PID %d /T /F' % pid)
            sys.exit(0)
        if stop_asked():
            os.remove(os.path.join(OUT, '_停'))
        lf = open(os.path.join(HERE, 'out', '日志', '1125_maze_nodes.log'), 'a', encoding='utf-8')
        cmd = [sys.executable, '-X', 'utf8', os.path.abspath(__file__), '--queue']
        flags = NO_WINDOW | getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0)
        kw = dict(stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=HERE, close_fds=True)
        try:
            p = subprocess.Popen(cmd, creationflags=flags | getattr(subprocess, 'CREATE_BREAKAWAY_FROM_JOB', 0), **kw)
        except OSError:                              # 这个会话的作业对象不让脱开，就留在里头
            p = subprocess.Popen(cmd, creationflags=flags, **kw)
        print('队列起来了（启动器进程号 %d），号 %s，并 %s 张；日志 %s' % (p.pid, os.environ.get('CODEX_HOME', '~/.codex'), os.environ.get('CG_WORKERS', '2'), QLOG))
        sys.exit(0)
    if args[:1] == ['--alive']:
        pid = queue_pid()
        print(('队列在跑，进程号 %d' % pid) if pid else '队列没在跑')
        sys.exit(0 if pid else 1)
    if args[:1] == ['--queue']:
        book = json.load(open(os.path.join(BOOK, 'data', 'maze.json'), encoding='utf-8'))
        nl = sum(len(e['lines']) for e in book['eras'])
        na = sum(len([a for a in l['acts'] if not a.startswith('幕间')]) for e in book['eras'] for l in e['lines'])
        os.makedirs(OUT, exist_ok=True)
        if queue_pid():
            note('== 已经有一个队列在跑（进程号 %d），这一个不起了' % queue_pid())
            sys.exit(0)
        with open(PIDF, 'w', encoding='utf-8') as f:
            f.write(str(os.getpid()))
        note('== 队列开跑，进程号', os.getpid(), '，主线', nl, '条，幕', na, '；号', os.environ.get('CODEX_HOME', '~/.codex'), '，并', os.environ.get('CG_WORKERS', '2'), '张')
        try:
            queue(int(os.environ.get('CG_WORKERS', '2')), nl, na)
        except StopAsked:
            note('== 看见 _停，队列退了')
        finally:
            try:
                os.remove(PIDF)
            except OSError:
                pass
        sys.exit(0)
    keys = pick(args)
    if not keys:
        print('键：', ' '.join(sorted(S)))
        sys.exit(0)
    if os.environ.get('CG_DRY'):
        for k in keys:
            p, refs = job(k)
            print('==', k, len(p), '字', [os.path.basename(r) for r in refs])
            print(p)
        sys.exit(0)
    todo = [k for k in keys if not os.path.exists(os.path.join(OUT, k + '.png'))]
    note('== 开跑', ' '.join(args), '要出', len(todo), '幅（已经有的', len(keys) - len(todo), '）', '号', os.environ.get('CODEX_HOME', '~/.codex'))
    with ThreadPoolExecutor(int(os.environ.get('CG_WORKERS', '3'))) as ex:
        list(ex.map(one, todo))
    left = [k for k in keys if not os.path.exists(os.path.join(OUT, k + '.png'))]
    note('== 这一趟完了，还缺', len(left), ('（撞了额度）' if STOP else ''), ' '.join(left[:40]))
