#!/usr/bin/env python3
# GPT 出的两扇放回四方：整张是一幅画，靠窗那一条只留抠出来的东西（箭、火翼、麦穗、剑、巨手、紫烟、崖石），其余透明，平边停在框线上。
#   python maze1001_frame_gpt.py [mid|gpt]    mid 是中间那一档，gpt 是头一版。图写 out/四方_11-03/art_<版本>/。pv_* 那几版走 maze1001_frame_pv.py，这里只存它们左扇的来源和抠图框。
# 先跑 gpt_prepare.py 把要抠的裁进 <来源>/crop/，cut_cpu.py 抠进 <来源>/cut/。楣和座在 maze1001_frame.py，mid 换 GPT 重画的飘带和徽记（<来源>/parts/，抠进 parts/cut/）。
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import numpy as np
from PIL import Image, ImageFilter
import frame_comp as F
from maze1001_frame import bottom_band, top_band

ROOT = os.path.join(HERE, 'out', '四方_11-03')
W, H, LINE = F.W, F.H, F.LINE
VERS = {
    'gpt': dict(src='gpt', left='left_b.png', down=90, art='art_gpt', tag='_gpt', boxes=(('l_hand', (560, 120, 1024, 480)), ('l_swirl', (740, 510, 1024, 930)))),
    'mid': dict(src='gpt_mid', left='left.png', down=130, art='art_mid', tag='_mid', parts='gpt_mid', boxes=(('l_hand', (600, 90, 1024, 440)), ('l_swirl', (770, 540, 1024, 910)), ('l_rock', (760, 1090, 1024, 1340)))),
    'pv_a': dict(src='pv', right='right_a.png', rcut='r_a', left='left_a.png', down=0, art='art_pv_a', tag='_pv_a', parts='gpt_mid', boxes=(('la_hand', (780, 400, 1024, 640)), ('la_rock', (640, 1060, 1024, 1536)))),
    'pv_b': dict(src='pv', right='right_a.png', rcut='r_a', left='left_b.png', down=0, art='art_pv_b', tag='_pv_b', parts='gpt_mid', boxes=(('lb_ring', (820, 180, 1024, 560)), ('lb_low', (820, 780, 1024, 1090)))),
    'pv_c': dict(src='pv', right='right_a.png', rcut='r_a', left='left_c2.png', down=0, art='art_pv_c', tag='_pv_c', parts='gpt_mid', boxes=(('lc2_hand', (780, 430, 1024, 700)),)),
    'pv_ab': dict(src='pv', right='right_f7.png', rcut='r_f7', left='left_ab.png', down=0, art='art_fu_ab', tag='_fu_ab', parts='gpt_mid', boxes=(('lab_hand', (760, 400, 1024, 860)), ('lab_rock', (640, 1200, 1024, 1536)))),
    'pv_d': dict(src='pv', right='right_pv.png', rcut='r_pv', left='left_d.png', down=0, art='art_pv_d', tag='_pv_d', parts='gpt_mid', boxes=(('ld_hand', (780, 430, 1024, 700)),)),
}


def soft(mask, grow=0, blur=0.8):
    if grow:
        mask = mask.filter(ImageFilter.MaxFilter(grow))
    return mask.filter(ImageFilter.GaussianBlur(blur))


def dim_outer(a, side, amount=0.55, start=760):
    x = np.arange(W, dtype=np.float32)
    d = x if side == 'right' else (W - 1 - x)
    k = 1 - np.clip((d - start) / (W - start), 0, 1)[None, :, None] * amount
    a[..., :3] *= k
    return a


def star_plate():
    """右扇外侧接的星空：照这张画天上的颜色，只有细星，没有圆球和云。"""
    t = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    top, bot = np.array((11, 16, 42), np.float32), np.array((17, 22, 56), np.float32)
    a = (top * (1 - t) + bot * t) * np.ones((H, W, 3), np.float32)
    rng = np.random.default_rng(5)
    n = 5200
    ys, xs = rng.integers(0, H, n), rng.integers(0, W, n)
    a[ys, xs] += (rng.random(n) ** 3 * 215 + 40)[:, None]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGB').filter(ImageFilter.GaussianBlur(0.6))


def right_panel(v):
    G = os.path.join(ROOT, v['src'])
    r = Image.open(os.path.join(G, v.get('right', 'right.png'))).convert('RGB').resize((1000, 2000), Image.LANCZOS)
    sky = star_plate()
    ramp = np.clip((1000 - np.arange(W, dtype=np.float32)) / 150, 0, 1) * 255
    fade = Image.fromarray(np.uint8(np.repeat(ramp[None, :], H, axis=0)))
    full = sky.copy()
    pad = Image.new('RGB', (W, H))
    pad.paste(r, (0, 0))
    full.paste(pad, (0, 0), fade)
    a = np.dstack([np.asarray(full).astype(np.float32), np.full((H, W), 255, np.float32)])
    a = dim_outer(a, 'right')
    # 靠窗那一条只留抠出来的
    cut = Image.open(os.path.join(G, 'cut', v.get('rcut', 'r_full') + '.png')).getchannel('A').resize((1000, 2000), Image.LANCZOS)
    cm = np.asarray(soft(cut.point(lambda t: 255 if t > 90 else 0))).astype(np.float32)
    a[:, :LINE, 3] = cm[:, :LINE]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def left_panel(v):
    G = os.path.join(ROOT, v['src'])
    down = v['down']
    src = Image.open(os.path.join(G, v['left'])).convert('RGB')
    k = H / src.height
    s = src.resize((int(src.width * k + 0.5), H), Image.LANCZOS)
    x0 = W - s.width
    full = Image.new('RGB', (W, H))
    full.paste(s.crop((0, 0, x0, H)).transpose(Image.FLIP_LEFT_RIGHT), (0, down))
    full.paste(s, (x0, down))
    # 黑日别叫顶栏压住，整张往下挪，上面空出来的一条藏在顶栏底下；只取黑日以上那几行来补，不然顶栏的模糊里透出一团黑日
    if down:
        full.paste(full.crop((0, down, W, down + 8)).transpose(Image.FLIP_TOP_BOTTOM).resize((W, down), Image.BICUBIC), (0, 0))
    a = np.dstack([np.asarray(full).astype(np.float32), np.full((H, W), 255, np.float32)])
    a = dim_outer(a, 'left')
    # 靠窗那一条：裁下来抠的几块拼回原图坐标
    mk = Image.new('L', src.size, 0)
    for name, box in v['boxes']:
        c = Image.open(os.path.join(G, 'cut', name + '.png')).getchannel('A').resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS)
        mk.paste(c.point(lambda t: 255 if t > 90 else 0), box[:2])
    mk = mk.resize(s.size, Image.LANCZOS)
    full_m = Image.new('L', (W, H), 0)
    full_m.paste(mk, (x0, down))
    cm = np.asarray(soft(full_m)).astype(np.float32)
    a[:, W - LINE:, 3] = cm[:, W - LINE:]
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)), 'RGBA')


def part(v, name):
    """GPT 重画的楣和座零件，缩成原来那几张零件的尺寸，排版不用改。"""
    im = Image.open(os.path.join(ROOT, v['parts'], 'parts', 'cut', name + '.png')).convert('RGBA')
    return F.clean_edges(F.trim_alpha(F.keep_thin(im))).resize((1120, 768), Image.LANCZOS)


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'mid'
    v = VERS[name]
    ART = os.path.join(ROOT, v['art'])
    os.makedirs(ART, exist_ok=True)
    r, l = right_panel(v), left_panel(v)
    r.save(os.path.join(ROOT, v['tag'] + '_right.png'))
    l.save(os.path.join(ROOT, v['tag'] + '_left.png'))
    F.save_webp(r, os.path.join(ART, 'maze_right.webp'))
    F.save_webp(l, os.path.join(ART, 'maze_left.webp'))
    # 底下那座蓝顶小城是 Turbo 画的，放在这几版上像贴上去的，不要
    if v.get('parts'):
        t = top_band(ribbon=part(v, 'ribbon_top'), crest=part(v, 'crest'), rk=0.44, rx=220)   # 楣是固定像素，人跟着窗口高度缩，飘带太大的话矮窗口上会盖住璐璐薇的头
        b = bottom_band(city=False, ribbon=part(v, 'ribbon_bot'))
    else:
        t, b = top_band(), bottom_band(city=False)
    t.save(os.path.join(ROOT, v['tag'] + '_top.png'))
    b.save(os.path.join(ROOT, v['tag'] + '_bottom.png'))
    F.save_webp(t, os.path.join(ART, 'maze_top.webp'))
    F.save_webp(b, os.path.join(ART, 'maze_bottom.webp'))
    print('ok', name, [os.path.getsize(os.path.join(ART, n)) // 1024 for n in sorted(os.listdir(ART))], 'KB')
