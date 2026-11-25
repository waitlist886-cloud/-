# 11-25 兜底那一轮的截图和改前改后比对（复刻台 tools/rili_bench/static_bench.mjs，本机无头 Chrome）。在仓库根上跑：
#   python -I -X utf8 底稿/状态栏/大框/第三轮/兜底_截图.py <临时目录> <步骤> [步骤…]
# 临时目录里先备好四样（都不进库）：
#   rules_frame_改前.json、frame_改前.css   改动以前的两份（git show <改前的提交>:底稿/状态栏/大框/rules_frame.json 这样存出来）
#   art/            复刻台的图目录：comfy/out/frame_art、out/第三轮_检定演出/art、out/第三轮_家业页/art、out/第三轮_背包格子/上传、
#                   comfy/out/立绘_v3/art 的 face_*、comfy/out/立绘_主角/art 拷在一处
#   pc_local.css    主角预设立绘那几组变量（pc_portrait.css_lines()），图床地址换成 __ART__/文件名
# 步骤：
#   旧样本   现成的样本改前改后各截一遍，逐像素比（电脑 1536×1024、手机 390×844，最新一条的开头和末尾，另点几页）。只印结果，不留图。
#            并着跑对不上的会单独重跑两回，再对不上的同一版自己跑两遍比（自己跟自己都不一样的是截图不稳）。「旧样本复查」只跑 RECHECK 那几组
#   歪法     样本_兜底_11-25.txt：手札页整条拼成长图（改前、改后并排），十二张检定面板一张一张裁出来拼一张，家业页、同行页各一张改前改后
#   主角     第三轮/样本_主角头像_*.txt：检定面板头上那一截裁出来放大，一种一行；带主角的旧样本改前改后差在哪
#   剪影     各族各性别的剪影放大排一张（样本是一段现成的 HTML，样式只带检定演出那一份）
#   旧样本带主角   带 §判 的两个旧样本单独再比一遍（主角那一边从名字头一个字换成剪影，只许差在头像那一小块）
# 规则照卡里的次序拼（rules_convert.json 的“稳”组 + rules_frame.json + 认不出纪元算迷宫纪 + mod_page 五条），跟 兜底_体检.py 一样。
# 无头里动画的钟不走：截以前把按时间走的动画都跑完，跑不完的（一直转的）停在同一刻，改前改后才比得了。
import io
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(UP, '..', '..', '..'))
sys.path.insert(0, UP)
sys.dont_write_bytecode = True
TMP = os.path.abspath(sys.argv[1])
STEPS = sys.argv[2:]
OUT = os.path.join(UP, '截图', '兜底_11-25')
SHOT = os.path.join(TMP, 'shot')
os.makedirs(OUT, exist_ok=True)
os.makedirs(SHOT, exist_ok=True)
BENCH = os.path.join(ROOT, 'tools', 'rili_bench', 'static_bench.mjs')
PC = (1536, 1024, (150, 860))      # 宽、高、框里没有东西压着的那一截（拼长图取这一截）
MB = (390, 844, (120, 715))      # 手机上框顶两道花边压到一百出头，底下七百三往下有一道往输入栏暗下去的影子，都躲开


def card_rules(frame_path, out_path):
    import importlib
    convert = json.load(io.open(os.path.join(UP, 'rules_convert.json'), encoding='utf-8'))
    frame = json.load(io.open(frame_path, encoding='utf-8'))
    rules = [dict(r) for r in convert if not (r.get('name') or '').startswith('转')] + [dict(r) for r in frame]
    k = max(i for i, r in enumerate(rules) if '<i class="sz-era era-' in r['replaceString']) + 1
    maze = next(r for r in rules if '<i class="sz-era era-maze"' in r['replaceString'])
    rules.insert(k, dict(maze, name='纪元·认不出算迷宫纪', regex='/(<summary class="sz-head">)(?!<i class="sz-era)/', replaceString=re.sub(r' data-y="[^"]*"', ' data-y=""', maze['replaceString'])))
    importlib.import_module('mod_page').apply_rules(rules)
    json.dump(rules, io.open(out_path, 'w', encoding='utf-8'), ensure_ascii=False)
    return out_path


VER = {
    '改前': (os.path.join(TMP, 'frame_改前.css'), card_rules(os.path.join(TMP, 'rules_frame_改前.json'), os.path.join(TMP, 'card_改前.json'))),
    '改后': (os.path.join(UP, 'frame.css'), card_rules(os.path.join(UP, 'rules_frame.json'), os.path.join(TMP, 'card_改后.json'))),
}
ART = os.path.join(TMP, 'art')
PCCSS = os.path.join(TMP, 'pc_local.css')

EV = r'''(async () => {
  const freeze = () => document.getAnimations().forEach((a) => { if (a.timeline !== document.timeline) return; try { a.finish(); } catch (e) { try { a.pause(); a.currentTime = 4000; } catch (e2) {} } });
  const tab = @TAB@, first = @FIRST@, sels = @SELS@;
  if (tab) { const t = [...document.querySelectorAll('.sz-tab.t-' + tab + ' input')].pop(); if (!t) return JSON.stringify({ err: 'no tab ' + tab }); t.click(); await new Promise((r) => setTimeout(r, @WAIT@)); }
  freeze(); await new Promise((r) => setTimeout(r, 200)); freeze();
  window.lay && window.lay();
  const c = document.getElementById('conversation');
  if (!tab && first === null) window.place && window.place();
  if (first !== null) c.scrollTop = first;
  await new Promise((r) => setTimeout(r, 250));
  freeze();
  await new Promise((r) => setTimeout(r, 100));
  const cr = c.getBoundingClientRect();
  const rect = (e) => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top - cr.top + c.scrollTop), Math.round(r.width), Math.round(r.height)]; };
  const msg = [...document.querySelectorAll('.rili-markdown-renderer')].pop();
  const out = { top: Math.round(cr.top), max: c.scrollHeight - c.clientHeight, msg: rect(msg) };
  for (const [k, sel] of Object.entries(sels)) out[k] = [...msg.querySelectorAll(sel)].filter((e) => e.getBoundingClientRect().height > 0).map(rect);
  return JSON.stringify(out);
})()'''


def bench(sample, png, size, ver, tab=None, first=None, sels=None, scroll='latest', scrolls=None, wait=1500):
    """跑一遍复刻台，回 eval 量出来的东西。sample 相对 大框/；png 写到临时目录"""
    css, rules = VER[ver]
    ev = png[:-4] + '.ev.js'
    io.open(ev, 'w', encoding='utf-8').write(EV.replace('@WAIT@', str(wait)).replace('@TAB@', json.dumps(tab)).replace('@FIRST@', json.dumps(first)).replace('@SELS@', json.dumps(sels or {})))
    a = ['node', BENCH, os.path.join(UP, sample), png, 'w=%d' % size[0], 'h=%d' % size[1], 'sidebar=0', 'extracss=%s,%s' % (css, PCCSS), 'extrarules=' + rules,
         'art=' + ART, 'scroll=' + str(scroll), 'eval=' + ev, 'wait=%d' % (wait + 1000)]
    if scrolls:
        a.append('scrolls=' + ','.join(str(s) for s in scrolls))
    for k in range(4):      # 机器忙的时候无头浏览器二十秒起不来，复刻台会空手回来，多试几回
        r = subprocess.run(a, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        m = re.search(r'^\{.*\}$', r.stdout, re.M)
        if m:
            break
    if not m:
        raise RuntimeError('复刻台没回话 %s %s\n%s\n%s' % (sample, ver, r.stdout[-400:], r.stderr[-400:]))
    return json.loads(m.group(0))


def strip(sample, name, size, ver, tab=None, sel='.sz-prose', idx=0, extra=None, xr=None):
    """一块东西从头到尾拼成一张长图。回 (图, 量出来的各样东西的框，已经换成相对这张图的)"""
    w, h, (a, b) = size
    sels = dict(extra or {}, _t=sel)
    m = bench(sample, os.path.join(SHOT, name + '_量.png'), size, ver, tab=tab, sels=sels)
    if 'err' in m or not m['_t']:
        return None, m
    x, yc, wd, ht = m['_t'][idx]
    if xr:
        x, wd = xr[0], xr[1] - xr[0]
    step = b - a
    n = max(1, -(-ht // step))
    pos = [max(0, min(m['max'], yc - (a - m['top']) + i * step)) for i in range(n)]
    png = os.path.join(SHOT, name + '.png')
    bench(sample, png, size, ver, tab=tab, first=pos[0], sels=sels, scrolls=pos[1:])
    out = Image.new('RGB', (wd, ht), (0, 0, 0))
    for i, s in enumerate(pos):
        im = Image.open(png if i == 0 else png[:-4] + '_%d.png' % s).convert('RGB')
        c0, c1 = yc + i * step, min(yc + ht, yc + (i + 1) * step)
        v0 = c0 + m['top'] - s
        if v0 + (c1 - c0) > h:
            print('  ！这一截落到视口外头了', name, i, v0, c1 - c0)
        out.paste(im.crop((x, v0, x + wd, v0 + (c1 - c0))), (0, c0 - yc))
    rel = {k: [[r[0] - x, r[1] - yc, r[2], r[3]] for r in v] for k, v in m.items() if isinstance(v, list) and v and isinstance(v[0], list)}
    return out, rel


def font(px):
    for f in ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simhei.ttf', 'C:/Windows/Fonts/simsun.ttc']:
        if os.path.exists(f):
            return ImageFont.truetype(f, px)
    return ImageFont.load_default()


def label(im, text, px=22, pad=10, bg=(14, 13, 20), fg=(232, 214, 160)):
    """图上头添一行字"""
    f = font(px)
    out = Image.new('RGB', (im.width, im.height + px + pad * 2), bg)
    ImageDraw.Draw(out).text((pad, pad - 2), text, font=f, fill=fg)
    out.paste(im, (0, px + pad * 2))
    return out


def side(ims, gap=16, bg=(14, 13, 20)):
    ims = [i for i in ims if i]
    out = Image.new('RGB', (sum(i.width for i in ims) + gap * (len(ims) + 1), max(i.height for i in ims) + gap * 2), bg)
    x = gap
    for i in ims:
        out.paste(i, (x, gap))
        x += i.width + gap
    return out


def stack(ims, gap=12, bg=(14, 13, 20)):
    ims = [i for i in ims if i]
    out = Image.new('RGB', (max(i.width for i in ims) + gap * 2, sum(i.height for i in ims) + gap * (len(ims) + 1)), bg)
    y = gap
    for i in ims:
        out.paste(i, (gap, y))
        y += i.height + gap
    return out


def grid(ims, cols, gap=14, bg=(14, 13, 20)):
    rows = [ims[i:i + cols] for i in range(0, len(ims), cols)]
    return stack([side(r, gap, bg) for r in rows], 0, bg)


def save(im, name, q=84):
    p = os.path.join(OUT, name)
    im.save(p, quality=q, optimize=True)
    print('写了', os.path.relpath(p, UP), im.size, os.path.getsize(p) // 1024, 'KB')


def same(p1, p2):
    a, b = Image.open(p1).convert('RGB'), Image.open(p2).convert('RGB')
    if a.size != b.size:
        return 'size %s %s' % (a.size, b.size)
    return ImageChops.difference(a, b).getbbox()


# ---------------- 旧样本：改前改后逐像素比 ----------------
OLD = ['样本_新手.txt', '样本_中期_交战.txt', '样本_对话_坡口.txt', '样本_月银纪_焚原.txt', '样本_纷争纪_墙前.txt', '样本_山铜纪_长阶.txt', '样本_队友浮栏_战斗.txt',
       '样本_史诗战.txt', '样本_装备两层.txt', '第三轮/样本_家业页_迷宫纪_后期.txt', '第三轮/样本_家业页_写歪.txt', '第三轮/样本_命星页.txt', '第三轮/样本_背包格子.txt']
OLD_TABS = [('样本_中期_交战.txt', 'panel'), ('样本_中期_交战.txt', 'party'), ('样本_月银纪_焚原.txt', 'bag'), ('第三轮/样本_家业页_迷宫纪_后期.txt', 'estate'), ('第三轮/样本_家业页_迷宫纪_后期.txt', 'party'),
            ('第三轮/样本_命星页.txt', 'deed')]
# 带 §判 的旧样本：主角那一边从名字头一个字换成剪影，是这一轮有意改的，只许差在头像那一小块
OLD_PC = ['第三轮/样本_检定演出.txt', '第三轮/样本_四样同屏.txt']


# 头一遍（四路并着跑）对不上的六组，「旧样本复查」只跑这六组，一个一个来
RECHECK = [('样本_队友浮栏_战斗.txt', None, 'mb'), ('第三轮/样本_家业页_迷宫纪_后期.txt', None, 'mb'), ('第三轮/样本_家业页_写歪.txt', None, 'pc'), ('第三轮/样本_家业页_写歪.txt', None, 'mb'),
           ('样本_中期_交战.txt', 'panel', 'pc'), ('样本_中期_交战.txt', 'party', 'mb')]


def step_old(only=None):
    jobs = []
    for s in OLD + OLD_PC:
        for tag, size in (('pc', PC), ('mb', MB)):
            jobs.append((s, None, tag, size))
    for s, t in OLD_TABS:
        for tag, size in (('pc', PC), ('mb', MB)):
            jobs.append((s, t, tag, size))
    if only:
        jobs = [j for j in jobs if j[:3] in only]

    def run(j):
        s, t, tag, size = j
        base = re.sub(r'[\\/]', '_', s[:-4]) + '_' + tag + ('_' + t if t else '')
        res = []
        ps = {}
        for ver in VER:
            p = os.path.join(SHOT, '旧_%s_%s.png' % (base, ver))
            bench(s, p, size, ver, tab=t, scrolls=None if t else ['end'])
            ps[ver] = p
        res.append(same(ps['改前'], ps['改后']))
        if not t:
            res.append(same(ps['改前'][:-4] + '_end.png', ps['改后'][:-4] + '_end.png'))
        return j, res

    with ThreadPoolExecutor(1 if only else 2) as ex:
        out = list(ex.map(run, jobs))
    n_same = n_retry = n_flaky = n_diff = n_exp = 0
    for j, res in out:
        s, t, tag, _ = j
        ok = all(r is None for r in res)
        exp = s in OLD_PC
        note = ''
        if not ok and not exp:
            # 并着跑的时候机器忙，图没载完、动画没停稳就截了的也会对不上：一个一个重跑两回
            for k in range(2):
                res2 = run(j)[1]
                if all(r is None for r in res2):
                    ok, note = True, '（并着跑那一遍对不上 %s，单独重跑一样）' % res
                    n_retry += 1
                    break
            else:
                # 还对不上：两版各跑两遍，四张放一起比。改前改后有一对一样的就算一样；同一版自己跟自己都不一样的是复刻台截图不稳，不是规则和样式的事
                base = os.path.join(SHOT, '稳_%s_%s%s' % (re.sub(r'[\\/]', '_', s[:-4]), tag, '_' + t if t else ''))
                ends = [''] if t else ['', '_end']
                for ver in VER:
                    for k in (1, 2):
                        bench(s, '%s_%s_%d.png' % (base, ver, k), size_of(tag), ver, tab=t, scrolls=None if t else ['end'])
                eq = lambda a, b: all(same('%s_%s%s.png' % (base, a, e), '%s_%s%s.png' % (base, b, e)) is None for e in ends)
                cross = [eq('改前_%d' % a, '改后_%d' % b) for a in (1, 2) for b in (1, 2)]
                selfs = [eq('%s_1' % v, '%s_2' % v) for v in VER]
                if any(cross):
                    ok, note = True, '（头三回对不上 %s，再各跑两遍，四对里 %d 对一样%s）' % (res, sum(cross), '' if all(selfs) else '，同一版自己两遍也有不一样的')
                    n_retry += 1
                elif not all(selfs):
                    note = '（同一版自己跑两遍也不一样，截图不稳）'
                    n_flaky += 1
                    ok = None
        if ok:
            n_same += 1
        elif exp:
            n_exp += 1
        elif ok is False:
            n_diff += 1
        print('  %s %-34s %s %-7s %s%s' % ('一样' if ok else ('只差头像' if exp else ('不稳' if ok is None else '××不一样')), s, tag, t or '手札', '' if ok else res, note))
    print('旧样本 %d 组（一组是一个样本一种宽度，开头末尾各一张，或者点一页）：逐像素一样 %d（里头单独重跑才一样的 %d），带主角的检定面板只差头像 %d，截图自己不稳的 %d，真不一样 %d'
          % (len(out), n_same, n_retry, n_exp, n_flaky, n_diff))


def size_of(tag):
    return PC if tag == 'pc' else MB


# ---------------- 歪法样本 ----------------
BAD = '样本_兜底_11-25.txt'


def step_bad(tags=('电脑', '手机')):
    for tag, size, xr in (('电脑', PC, (452, 1084)), ('手机', MB, (16, 374))):
        if tag not in tags:
            continue
        got = {}
        for ver in VER:
            im, rel = strip(BAD, '歪_%s_手札_%s' % (tag, ver), size, ver, sel='.sz-prose', extra={'judge': '.sz-judge', 'row': '.sz-row[data-k="判"]'}, xr=xr)
            got[ver] = (im, rel)
            print(' ', tag, ver, '手札', im.size, '整张', len(rel.get('judge', [])), '落成一行的', len(rel.get('row', [])))
        save(side([label(got[v][0], '%s · 手札页 · %s' % (tag, v)) for v in VER]), '歪法_%s_手札_改前改后.jpg' % tag, 80)
        im, rel = got['改后']
        cells = [im.crop((max(0, r[0] - 6), max(0, r[1] - 6), r[0] + r[2] + 6, r[1] + r[3] + 6)) for r in sorted(rel.get('judge', []) + rel.get('row', []), key=lambda r: r[1])]
        save(grid(cells, 4 if tag == '电脑' else 6), '歪法_%s_检定十二张_改后.jpg' % tag)
    for tab, sel, nm in (('estate', '.p-estate', '家业页'), ('party', '.p-party', '同行页')):
        for tag, size in (('电脑', PC), ('手机', MB)):
            if tag not in tags:
                continue
            ims = []
            for ver in VER:
                im, rel = strip(BAD, '歪_%s_%s_%s' % (tag, nm, ver), size, ver, tab=tab, sel=sel, idx=-1, extra={'es': '.sz-es', 'pet': '.sz-pet'})
                if im is None:
                    print('  ', tag, ver, nm, '没有这一页：', rel.get('err') or '页是空的')
                    im = Image.new('RGB', (size[0] // 2, 120), (30, 28, 40))
                    ImageDraw.Draw(im).text((16, 44), '这一页没出来（记录没认出来，页签不显）', font=font(18), fill=(220, 200, 150))
                else:
                    print('  ', tag, ver, nm, im.size, '家业卡', len(rel.get('es', [])), '宠卡', len(rel.get('pet', [])))
                ims.append(label(im, '%s · %s · %s' % (tag, nm, ver)))
            save(side(ims), '歪法_%s_%s_改前改后.jpg' % (tag, nm), 80)
    if '电脑' not in tags:
        return
    # 浮栏里的宠：手札页头上那一截
    ims = []
    for ver in VER:
        p = os.path.join(SHOT, '歪_浮栏_%s.png' % ver)
        m = bench(BAD, p, PC, ver, sels={'pf': '.sz-pf'})
        ims.append(label(Image.open(p).convert('RGB').crop((440, 100, 1096, 520)), '电脑 · 手札页头上（浮栏里的魔宠坐骑）· %s' % ver))
    save(side(ims), '歪法_电脑_浮栏_改前改后.jpg')


# ---------------- 主角那一边的头像 ----------------
PCS = [('剪影_人类男', '没写立绘那一行：人类、男'), ('剪影_精灵女_没画的预设', '立绘写了预设，图床上还没有这一张：高等精灵、女'), ('剪影_魔族夜翼', '预设没画：魔族夜翼系、女'),
       ('剪影_矮人男_立绘写无', '立绘写「无」：矮人、男'), ('预设_晨曦人男健壮', '预设立绘有图：晨曦人·男·健壮'), ('自己的图', '玩家贴了自己的立绘和头像'),
       ('写成你_和_主角在右边', '出手方写成「你」（兽耳族、女）；第二张主角在应对那一边')]


def step_pc():
    # 「自己的图」那一份的地址要是 http 开头的（规则只认 http），样本里写的是本机 8791。那个口可能叫别人占着，
    # 这里另挑一个空着的口，起一个只在这一步里活着的静态服务（只听本机，根是图目录），样本抄一份到临时目录把口换掉
    import socket
    import time
    import urllib.request
    sk = socket.socket()
    sk.bind(('127.0.0.1', 0))
    port = sk.getsockname()[1]
    sk.close()
    srv = subprocess.Popen([sys.executable, '-I', '-m', 'http.server', str(port), '--bind', '127.0.0.1', '--directory', ART], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        try:
            assert urllib.request.urlopen('http://127.0.0.1:%d/face_one.webp' % port, timeout=2).status == 200
            break
        except Exception:
            time.sleep(0.5)
    else:
        srv.terminate()
        raise RuntimeError('本机的静态服务没起来，或者图目录里没有 face_one.webp（主角九格表情的头一格裁一张）')
    try:
        def run(j):
            nm, cap = j
            s = '第三轮/样本_主角头像_%s.txt' % nm
            if nm == '自己的图':
                txt = io.open(os.path.join(UP, s), encoding='utf-8').read()
                assert txt.count('http://127.0.0.1:8791/') == 2, txt.count('http://127.0.0.1:8791/')
                s = os.path.join(SHOT, '样本_主角头像_自己的图_换口.txt')
                io.open(s, 'w', encoding='utf-8', newline='\n').write(txt.replace('http://127.0.0.1:8791/', 'http://127.0.0.1:%d/' % port))
            n = 2 if nm.startswith('写成你') else 1
            ims = []
            for ver in (['改前', '改后'] if nm in ('剪影_人类男', '预设_晨曦人男健壮') else ['改后']):
                p = os.path.join(SHOT, '主角_%s_%s.png' % (nm, ver))
                m = bench(s, p, PC, ver, sels={'j': '.sz-judge'})
                for k, r in enumerate(m['j'][:n]):
                    q = p[:-4] + '_%d.png' % k
                    sc = max(0, min(m['max'], r[1] + m['top'] - 170))
                    bench(s, q, PC, ver, first=sc, sels={'j': '.sz-judge'})
                    y = r[1] + m['top'] - sc
                    c = Image.open(q).convert('RGB').crop((r[0], y, r[0] + r[2], y + 150))
                    ims.append(label(c.resize((c.width * 2, c.height * 2), Image.LANCZOS), '%s%s' % (ver, ' · 第 %d 张' % (k + 1) if n > 1 else ''), 18, 6))
            return label(side(ims, 10), cap, 22)

        with ThreadPoolExecutor(2) as ex:
            rows = list(ex.map(run, PCS))
        save(stack(rows), '主角头像_七种.jpg', 86)
    finally:
        srv.terminate()


# ---------------- 剪影一览 ----------------
def step_sil():
    """各族各性别的剪影放大排一张。也走复刻台：样本是一段现成的 HTML（不过规则），样式只带检定演出那一份"""
    import judge_fx as J
    cases = [('人类', '男'), ('人类', '女'), ('人类', ''), ('矮人', '男'), ('矮人', '女'), ('半身人', '男'), ('半身人', '女'), ('高等精灵', '女'), ('暗精灵', '男'), ('兽耳族', '女'), ('兽耳族', '男'),
             ('半兽人', '男'), ('半兽人', '女'), ('提夫林', '女'), ('魔族', '男'), ('魔族·炎角系', '男'), ('魔族·轰狱系', '男'), ('魔族·夜翼系', '女'), ('魔族·深潮系', '女'), ('魔族·白骸系', '男'),
             ('龙裔', '男'), ('龙裔·远裔', '女'), ('真龙幼体', '女'), ('（没认出来的族）', '女')]
    cells = ''.join('<div class="sil-c"><span class="jg-w l jg-pc" data-portrait="x" data-r="%s" data-g="%s" data-e=""><i class="jg-av" data-n="洛"></i></span><em>%s%s</em></div>'
                    % (r, g, r, '·' + g if g else '·没写性别') for r, g in cases)
    smp = os.path.join(SHOT, '剪影.txt')
    io.open(smp, 'w', encoding='utf-8').write('<i class="sz-hud" style="display:none"></i><div class="sil-w">%s</div>' % cells)
    css = os.path.join(SHOT, '剪影.css')
    io.open(css, 'w', encoding='utf-8').write(
        J.css(art=False) + '.sil-w{display:grid;grid-template-columns:repeat(6,1fr);gap:20px 4px;padding:18px 6px;background:#12112a;color:#e8dcc0;'
        '--fm-head:#f3e2b4;--fm-ink:#e8dcc0;--jl:#e6c66e;--jr:#9db8e8;--jg-sc:var(--jl);--fm-por1:#2a2a64;--fm-por2:#17163e}'
        '.sil-c{display:flex;flex-direction:column;align-items:center;gap:8px;min-width:0}.sil-c em{order:2;font-style:normal;font-size:11.5px;line-height:1.4;white-space:nowrap}'
        '.sil-c .jg-w{display:block;width:44px;height:44px;zoom:2;animation:none!important;opacity:1!important;transform:none!important}'
        '.sil-c:nth-child(even) .jg-w{--jg-sc:var(--jr)}')
    empty = os.path.join(SHOT, '空规则.json')
    io.open(empty, 'w', encoding='utf-8').write('[]')
    VER['剪影'] = (css, empty)
    im, _ = strip(smp, '剪影', PC, '剪影', sel='.sil-w')
    save(im, '主角剪影_各族一览.jpg', 90)


for st in STEPS:
    print('====', st)
    {'旧样本': step_old, '旧样本复查': lambda: step_old(RECHECK), '旧样本带主角': lambda: step_old([(s, None, g) for s in OLD_PC for g in ('pc', 'mb')]), '歪法': step_bad, '歪法手机': lambda: step_bad(('手机',)), '歪法电脑': lambda: step_bad(('电脑',)), '主角': step_pc, '剪影': step_sil}[st]()
