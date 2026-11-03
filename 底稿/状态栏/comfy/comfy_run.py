#!/usr/bin/env python3
# 奥尔德兰的旅印 · 状态栏美术出图脚本（接本机 ComfyUI，11-03）
#
# 放在用户电脑上 Remote Control 共享出来的那个文件夹里跑，ComfyUI 自带的 python 就行（要 Pillow，ComfyUI 自带）。
#   python comfy_run.py probe                       查 ComfyUI：系统、显卡显存、装了哪些模型和节点，写 probe.json
#   python comfy_run.py sketch maze1001             画构图底稿（彩色的给图生图打底，线稿给 ControlNet），写 sketches/maze1001/
#   python comfy_run.py run plan_maze1001.json [--only left,right] [--seeds 11,22] [--draft] [--dry]
#                                                   照计划出图，图和工作流写 out/<套>/<件>/，每件拼一张小样
#                                                   --draft 只出第一遍，不做高清修复，写 out/<套>_draft/<件>/，挑好了再跑正式的
#   python comfy_run.py comp plan_maze1001.json [--seeds 11,22] [--refine 0.2]
#                                                   一个人物一张再合成（计划里带 comp 的那一件），零件写 out/<套>_draft/<件>/parts/，已有的零件不重出
#   python comfy_run.py sheet out/maze1001/left     重拼一张小样
# 只用标准库（画图和收图用 Pillow）。ComfyUI 地址默认 http://127.0.0.1:8188，要改设环境变量 COMFY_URL。
# 节点的入参照 /object_info 补默认值，ComfyUI 版本不同、节点多了必填项也跑得起来。
import argparse
import io
import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASE = os.environ.get('COMFY_URL', 'http://127.0.0.1:8188').rstrip('/')
HERE = os.path.dirname(os.path.abspath(__file__))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


# ---------------------------------------------------------------- 接口
def _open(req, timeout=120):
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace')
        raise RuntimeError('ComfyUI 回了 %s：%s' % (e.code, body[:4000]))


def get_json(path, timeout=120):
    return json.loads(_open(BASE + path, timeout).decode('utf-8'))


def post_json(path, obj, timeout=120):
    req = urllib.request.Request(BASE + path, data=json.dumps(obj).encode('utf-8'), headers={'Content-Type': 'application/json'})
    return json.loads(_open(req, timeout).decode('utf-8'))


def upload(path, name):
    """传一张图进 ComfyUI 的 input/aldran/，回 LoadImage 认的名字。"""
    boundary = '----aldran' + uuid.uuid4().hex
    data = open(path, 'rb').read()
    parts = [
        ('--%s\r\nContent-Disposition: form-data; name="image"; filename="%s"\r\nContent-Type: image/png\r\n\r\n' % (boundary, name)).encode('utf-8'), data, b'\r\n',
        ('--%s\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n' % boundary).encode('utf-8'),
        ('--%s\r\nContent-Disposition: form-data; name="subfolder"\r\n\r\naldran\r\n' % boundary).encode('utf-8'),
        ('--%s--\r\n' % boundary).encode('utf-8'),
    ]
    req = urllib.request.Request(BASE + '/upload/image', data=b''.join(parts), headers={'Content-Type': 'multipart/form-data; boundary=%s' % boundary})
    r = json.loads(_open(req).decode('utf-8'))
    return (r['subfolder'] + '/' + r['name']) if r.get('subfolder') else r['name']


def combo(info, node, field):
    """节点某个下拉框的选项（新旧两种写法都认）。"""
    try:
        spec = info[node]['input']
    except KeyError:
        return []
    for grp in ('required', 'optional'):
        f = spec.get(grp, {}).get(field)
        if not f:
            continue
        v = f[0]
        if isinstance(v, list):
            return v
        if v == 'COMBO' and len(f) > 1 and isinstance(f[1], dict):
            return f[1].get('options', [])
    return []


# ---------------------------------------------------------------- probe
NODES_OF_INTEREST = [
    'CheckpointLoaderSimple', 'UNETLoader', 'CLIPLoader', 'DualCLIPLoader', 'VAELoader', 'LoraLoader', 'KSampler', 'KSamplerAdvanced',
    'ControlNetLoader', 'ControlNetApplyAdvanced', 'SetUnionControlNetType', 'Canny',
    'ConditioningSetArea', 'ConditioningSetMask', 'ConditioningCombine', 'ConditioningZeroOut', 'FluxGuidance',
    'EmptySD3LatentImage', 'VAEEncodeTiled', 'VAEDecodeTiled', 'ImageScale', 'ImageScaleBy', 'UpscaleModelLoader', 'ImageUpscaleWithModel',
    'IPAdapterUnifiedLoader', 'IPAdapterAdvanced', 'IPAdapterStyleComposition', 'IPAdapterModelLoader', 'CLIPVisionLoader',
    'AIO_Preprocessor', 'LineArtPreprocessor', 'AnimeLineArtPreprocessor', 'DepthAnythingV2Preprocessor',
    'Image Remove Background (rembg)', 'BRIA_RMBG_Zho', 'InspyrenetRembg', 'LayerMask: RemBgUltra', 'easy imageRemBg',
]


def family_of(name):
    n = name.lower()
    if 'anima' in n:
        return 'anima'
    if 'flux' in n:
        return 'flux'
    if 'pony' in n:
        return 'sdxl-pony'
    if 'illustrious' in n or 'noob' in n or 'ilxl' in n or 'wai' in n:
        return 'sdxl-illustrious'
    if 'sd3' in n:
        return 'sd3'
    if 'xl' in n or 'sdxl' in n or 'animagine' in n:
        return 'sdxl'
    if '1.5' in n or 'sd15' in n or 'v1-5' in n:
        return 'sd15'
    return '?'


def cmd_probe(args):
    s = get_json('/system_stats')
    info = get_json('/object_info', timeout=300)
    sysi = s.get('system', {})
    out = {
        'url': BASE,
        'system': {k: sysi.get(k) for k in ('os', 'python_version', 'comfyui_version', 'pytorch_version', 'embedded_python', 'ram_total', 'ram_free')},
        'devices': [{'name': d.get('name'), 'type': d.get('type'), 'vram_total_gb': round((d.get('vram_total') or 0) / 2 ** 30, 1),
                     'vram_free_gb': round((d.get('vram_free') or 0) / 2 ** 30, 1)} for d in s.get('devices', [])],
        'checkpoints': combo(info, 'CheckpointLoaderSimple', 'ckpt_name'),
        'unets': combo(info, 'UNETLoader', 'unet_name'),
        'clips': combo(info, 'DualCLIPLoader', 'clip_name1'),
        'vaes': combo(info, 'VAELoader', 'vae_name'),
        'loras': combo(info, 'LoraLoader', 'lora_name'),
        'controlnets': combo(info, 'ControlNetLoader', 'control_net_name'),
        'upscale_models': combo(info, 'UpscaleModelLoader', 'model_name'),
        'clip_vision': combo(info, 'CLIPVisionLoader', 'clip_name'),
        'ipadapter_files': combo(info, 'IPAdapterModelLoader', 'ipadapter_file'),
        'ipadapter_presets': combo(info, 'IPAdapterUnifiedLoader', 'preset'),
        'samplers': combo(info, 'KSampler', 'sampler_name'),
        'schedulers': combo(info, 'KSampler', 'scheduler'),
        'nodes': {n: (n in info) for n in NODES_OF_INTEREST},
        'node_count': len(info),
    }
    out['checkpoint_families'] = {c: family_of(c) for c in out['checkpoints']}
    out['unet_families'] = {c: family_of(c) for c in out['unets']}
    json.dump(out, open(os.path.join(HERE, 'probe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(info, open(os.path.join(HERE, 'object_info.json'), 'w', encoding='utf-8'))
    print('ComfyUI', out['system'].get('comfyui_version'), '| Python', out['system'].get('python_version'), '| torch', out['system'].get('pytorch_version'), '|', out['system'].get('os'))
    for d in out['devices']:
        print('显卡', d['name'], '显存', d['vram_total_gb'], 'GB（空着', d['vram_free_gb'], 'GB）')
    for k in ('checkpoints', 'unets', 'clips', 'vaes', 'controlnets', 'loras', 'upscale_models', 'clip_vision', 'ipadapter_files'):
        v = out[k]
        print('%s（%d）：%s' % (k, len(v), '、'.join(v[:40]) + ('……' if len(v) > 40 else '')))
    print('节点：', '、'.join(n for n, ok in out['nodes'].items() if ok))
    print('没有的节点：', '、'.join(n for n, ok in out['nodes'].items() if not ok))
    print('写了 probe.json 和 object_info.json，节点一共', out['node_count'], '个')


# ---------------------------------------------------------------- 构图底稿
def _imgs():
    from PIL import Image, ImageDraw, ImageFilter
    return Image, ImageDraw, ImageFilter


def vgrad(W, H, stops):
    Image, ImageDraw, _ = _imgs()
    im = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1)
        for i in range(len(stops) - 1):
            (t0, c0), (t1, c1) = stops[i], stops[i + 1]
            if t0 <= t <= t1:
                u = (t - t0) / max(t1 - t0, 1e-6)
                c = tuple(int(c0[k] + (c1[k] - c0[k]) * u) for k in range(3))
                d.line([(0, y), (W, y)], fill=c)
                break
    return im


class Canvas:
    """彩色底稿和线稿一起画：fill 上色进彩色那一张，同一个形状描边进线稿。"""

    def __init__(self, W, H, bg_stops):
        Image, ImageDraw, ImageFilter = _imgs()
        self.Image, self.ImageDraw, self.ImageFilter = Image, ImageDraw, ImageFilter
        self.W, self.H = W, H
        self.color = vgrad(W, H, bg_stops).convert('RGBA')
        self.line = Image.new('L', (W, H), 0)
        self.ld = ImageDraw.Draw(self.line)

    def layer(self):
        return self.Image.new('RGBA', (self.W, self.H), (0, 0, 0, 0))

    def put(self, lay, blur=0):
        if blur:
            lay = lay.filter(self.ImageFilter.GaussianBlur(blur))
        self.color.alpha_composite(lay)

    def ellipse(self, box, fill, blur=0, line=0, alpha=255):
        lay = self.layer()
        self.ImageDraw.Draw(lay).ellipse(box, fill=fill[:3] + (alpha,))
        self.put(lay, blur)
        if line:
            self.ld.ellipse(box, outline=255, width=line)

    def ring(self, box, fill, width, blur=0, line=0, alpha=255):
        lay = self.layer()
        self.ImageDraw.Draw(lay).ellipse(box, outline=fill[:3] + (alpha,), width=width)
        self.put(lay, blur)
        if line:
            self.ld.ellipse(box, outline=255, width=line)

    def poly(self, pts, fill, blur=0, line=0, alpha=255):
        lay = self.layer()
        self.ImageDraw.Draw(lay).polygon(pts, fill=fill[:3] + (alpha,))
        self.put(lay, blur)
        if line:
            self.ld.line(pts + [pts[0]], fill=255, width=line, joint='curve')

    def path(self, pts, fill, width, blur=0, line=0, alpha=255):
        lay = self.layer()
        self.ImageDraw.Draw(lay).line(pts, fill=fill[:3] + (alpha,), width=width, joint='curve')
        self.put(lay, blur)
        if line:
            self.ld.line(pts, fill=255, width=line, joint='curve')

    def halo(self, cx, cy, r, line=4):
        """一圈金色圆光：外圈亮、里面暖白，线稿里两道圈。"""
        for k in range(14, 0, -1):
            t = k / 14
            c = (int(255 - 40 * t), int(238 - 70 * t), int(200 - 120 * t))
            self.ellipse([cx - r * t, cy - r * t, cx + r * t, cy + r * t], c, alpha=255)
        self.ellipse([cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10], (230, 190, 100), blur=14, alpha=120)
        self.ld.ellipse([cx - r, cy - r, cx + r, cy + r], outline=255, width=line)
        self.ld.ellipse([cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14], outline=180, width=2)

    def figure(self, cx, top, h, robe, skin=(244, 226, 210), hair=None, wings=None, prop=None, line=4, wide=1.0):
        """一个人的剪影：头、肩、长袍，可带翼和手里的东西。h 是从头顶到袍底的高。"""
        hr = h * 0.075
        hx, hy = cx, top + hr
        sw = h * 0.20 * wide
        if wings:
            for side in (-1, 1):
                pts = [(cx + side * sw * 0.3, top + h * 0.22), (cx + side * sw * 2.2, top + h * 0.02), (cx + side * sw * 2.6, top + h * 0.30),
                       (cx + side * sw * 2.0, top + h * 0.52), (cx + side * sw * 0.5, top + h * 0.45)]
                self.poly(pts, wings, blur=2, line=line - 1)
        robe_pts = [(cx - sw * 0.55, top + h * 0.17), (cx + sw * 0.55, top + h * 0.17), (cx + sw * 1.1, top + h), (cx - sw * 1.1, top + h)]
        self.poly(robe_pts, robe, blur=1, line=line)
        if hair:
            self.ellipse([hx - hr * 1.35, hy - hr * 1.25, hx + hr * 1.35, hy + hr * 1.9], hair, blur=1)
        self.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], skin, line=line)
        if prop:
            kind, col = prop
            if kind == 'staff':
                self.path([(cx + sw * 0.9, top + h * 0.05), (cx + sw * 0.9, top + h * 0.95)], col, 10, line=line)
                self.ellipse([cx + sw * 0.9 - 18, top + h * 0.02 - 18, cx + sw * 0.9 + 18, top + h * 0.02 + 18], (255, 240, 200), blur=6)
            elif kind == 'spear':
                self.path([(cx - sw * 0.9, top - h * 0.05), (cx - sw * 0.9, top + h * 0.95)], col, 8, line=line)
                self.poly([(cx - sw * 0.9, top - h * 0.12), (cx - sw * 0.9 - 14, top - h * 0.02), (cx - sw * 0.9 + 14, top - h * 0.02)], (240, 240, 250), line=line - 1)
            elif kind == 'sword':
                self.path([(cx + sw * 0.6, top + h * 0.35), (cx + sw * 1.4, top + h * 0.95)], col, 12, line=line)
            elif kind == 'hammer':
                self.path([(cx + sw * 0.9, top + h * 0.2), (cx + sw * 0.9, top + h * 0.9)], (120, 100, 80), 12, line=line)
                self.poly([(cx + sw * 0.55, top + h * 0.12), (cx + sw * 1.25, top + h * 0.12), (cx + sw * 1.25, top + h * 0.28), (cx + sw * 0.55, top + h * 0.28)], col, line=line)
            elif kind == 'bow':
                self.path([(cx - sw * 1.2, top + h * 0.1), (cx - sw * 1.6, top + h * 0.35), (cx - sw * 1.2, top + h * 0.6)], col, 8, line=line)
            elif kind == 'sickle':
                self.path([(cx + sw * 0.8, top + h * 0.25), (cx + sw * 0.8, top + h * 0.85)], (120, 90, 60), 8, line=line)
                self.path([(cx + sw * 0.8, top + h * 0.25), (cx + sw * 1.4, top + h * 0.18), (cx + sw * 1.6, top + h * 0.32)], col, 8, line=line)
            elif kind == 'cat':
                self.ellipse([cx - sw * 1.5, top + h * 0.12, cx - sw * 0.7, top + h * 0.34], col, line=line - 1)
                self.poly([(cx - sw * 1.45, top + h * 0.16), (cx - sw * 1.35, top + h * 0.07), (cx - sw * 1.25, top + h * 0.15)], col)
                self.poly([(cx - sw * 0.95, top + h * 0.15), (cx - sw * 0.85, top + h * 0.06), (cx - sw * 0.75, top + h * 0.14)], col)
            elif kind == 'scepter':
                self.path([(cx - sw * 0.9, top + h * 0.15), (cx - sw * 0.9, top + h * 0.95)], col, 9, line=line)
                self.ellipse([cx - sw * 0.9 - 22, top + h * 0.09 - 22, cx - sw * 0.9 + 22, top + h * 0.09 + 22], (190, 30, 50), blur=4)

    def save(self, folder, name):
        os.makedirs(folder, exist_ok=True)
        c = self.color.convert('RGB')
        c.save(os.path.join(folder, name + '_color.png'))
        ln = self.line.filter(self.ImageFilter.GaussianBlur(0.8)).point(lambda v: 255 if v > 60 else 0)
        ln.convert('RGB').save(os.path.join(folder, name + '_line.png'))
        return c


def sketch_maze1001_left(folder):
    """左扇：大迷宫（一圈一圈往下的井和城），井底的影子（不画脸），黑日，崖边一个旅人。左边是外侧，右边贴窗。"""
    W, H = 1000, 2000
    cv = Canvas(W, H, [(0, (14, 8, 34)), (0.35, (44, 24, 92)), (0.62, (34, 30, 86)), (1, (22, 26, 62))])
    rnd = random.Random(7)
    # 井底升上来的影子：一大团紫烟和触须，占住上半截，没有脸
    for i in range(9):
        x0 = rnd.randint(60, 900)
        pts = [(x0, 1050)]
        for k in range(1, 9):
            pts.append((x0 + math.sin(k * 0.9 + i) * 160 + rnd.randint(-40, 40), 1050 - k * 120))
        cv.path(pts, (120, 72, 190), rnd.randint(40, 80), blur=22, alpha=170)
    cv.ellipse([150, 120, 950, 760], (90, 52, 160), blur=60, alpha=150)
    # 黑日和一圈淡紫的光
    cv.ellipse([470, 330, 830, 690], (200, 170, 255), blur=40, alpha=200)
    cv.ellipse([520, 380, 780, 640], (8, 6, 18), line=5)
    cv.ring([512, 372, 788, 648], (236, 226, 255), 10, blur=3, alpha=200)
    cv.path([(650, 640), (640, 900), (560, 1150)], (190, 160, 255), 36, blur=20, alpha=150)
    # 塔林：一排一排的尖塔，越往下越暗，窗里一点金光
    for row, (y0, col) in enumerate([(820, (58, 44, 110)), (960, (46, 38, 96)), (1100, (36, 30, 80))]):
        x = 20 + row * 30
        while x < 980:
            w = rnd.randint(40, 90)
            h = rnd.randint(120, 300) - row * 30
            cv.poly([(x, y0 + 200), (x, y0 + 200 - h), (x + w / 2, y0 + 200 - h - rnd.randint(40, 120)), (x + w, y0 + 200 - h), (x + w, y0 + 200)], col, line=2 if row == 0 else 0)
            for _ in range(3):
                wx, wy = x + rnd.randint(8, max(9, w - 8)), y0 + 200 - rnd.randint(20, max(21, h - 20))
                cv.ellipse([wx - 3, wy - 5, wx + 3, wy + 5], (240, 205, 140), alpha=220)
            x += w + rnd.randint(10, 40)
    # 井：一圈一圈往下，正中有光往下沉
    cx, cy = 470, 1240
    for k, rx in enumerate(range(420, 40, -38)):
        ry = rx * 0.34
        col = (64, 54, 124) if k % 2 == 0 else (32, 28, 70)
        cv.ellipse([cx - rx, cy - ry + k * 14, cx + rx, cy + ry + k * 14], col, line=3 if k % 2 == 0 else 0)
    cv.ellipse([cx - 90, cy + 110, cx + 90, cy + 190], (250, 220, 150), blur=30, alpha=230)
    # 一道金白的螺旋路，从左下绕进井口
    pts = []
    for k in range(60):
        t = k / 59
        ang = math.pi * 0.9 + t * math.pi * 3.2
        rr = 430 * (1 - t * 0.85)
        pts.append((cx + math.cos(ang) * rr * 1.0, cy + 520 * (1 - t) + math.sin(ang) * rr * 0.34))
    cv.path(pts, (250, 228, 170), 26, blur=3, line=4)
    cv.path(pts, (255, 245, 210), 60, blur=26, alpha=90)
    # 崖：从右下伸出来的一块，旅人站在上面，背对着看井（离窗边留七十像素）
    cv.poly([(560, 1520), (760, 1480), (930, 1490), (1000, 1500), (1000, 1720), (820, 1690), (600, 1640)], (24, 20, 48), line=4)
    cv.figure(720, 1330, 170, robe=(18, 16, 32), skin=(30, 26, 50), prop=('staff', (60, 50, 90)), line=4)
    cv.path([(690, 1365), (640, 1420), (610, 1500)], (40, 34, 70), 28, blur=2, line=3)   # 斗篷往后飘
    cv.ellipse([700, 1300, 760, 1360], (255, 230, 180), blur=18, alpha=150)
    # 底下的云和金浪（接底下那一条）
    for k in range(10):
        x = rnd.randint(-80, 950)
        y = rnd.randint(1700, 1960)
        r = rnd.randint(90, 180)
        cv.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], (236, 224, 250) if k % 3 else (240, 208, 140), blur=10, alpha=235, line=2 if k % 2 else 0)
    return cv.save(folder, 'left')


def sketch_maze1001_right(folder):
    """右扇：七支柱各一圈圆光，底下双王，再往下阿卡迪亚和空艇。左边贴窗，右边是外侧。"""
    W, H = 1000, 2000
    cv = Canvas(W, H, [(0, (242, 234, 210)), (0.45, (226, 206, 158)), (0.75, (170, 186, 172)), (1, (110, 150, 170))])
    rnd = random.Random(11)
    # 青绿和金的卷纹铺底
    for i in range(10):
        x0 = rnd.randint(0, 1000)
        y0 = rnd.randint(0, 1500)
        pts = [(x0 + math.cos(t / 6) * (80 + t * 6), y0 + math.sin(t / 6) * (80 + t * 6)) for t in range(0, 36)]
        cv.path(pts, (70, 150, 140) if i % 2 else (196, 170, 96), 18, blur=6, alpha=120)
    gods = [
        # (中心 x, 中心 y, 半径, 袍色, 发色, 翼, 手里的)   七支柱照底卡显相
        (560, 330, 132, (250, 248, 240), (238, 200, 90), (255, 255, 250), ('bow', (200, 170, 90))),          # 璐璐薇：白羽、疾风、金色乱发、风之弓
        (300, 470, 132, (180, 60, 40), (200, 50, 30), (240, 120, 60), ('staff', (90, 70, 60))),               # 伊兹帕鲁特：赤发，翼里火焰冰雾雷光
        (600, 620, 145, (150, 150, 146), (220, 220, 215), (120, 110, 100), ('hammer', (170, 160, 150))),      # 欧巴德斯：半身石躯，山脉鳞层的翼，大地之锤
        (300, 770, 124, (120, 170, 90), (150, 110, 70), None, ('sickle', (200, 210, 220))),                    # 库米罗妮：幼小，鹿角，藤叶，种子光环，镰刀
        (600, 910, 128, (40, 34, 44), (30, 28, 32), None, ('cat', (20, 20, 24))),                               # 艾赫卡托尔：黑猫，金铃，硬币
        (300, 1050, 128, (244, 244, 250), (190, 220, 210), (250, 250, 255), ('spear', (230, 220, 200))),      # 朱亚：翠玉眼，头顶细小羽翼，圣枪
        (600, 1180, 128, (150, 130, 110), (80, 70, 70), None, ('sword', (200, 200, 210))),                     # 耶万：朴素长袍，征战之刃
    ]
    for cx, cy, r, robe, hair, wings, prop in gods:
        cv.halo(cx, cy, r)
        small = 0.8 if prop[0] == 'sickle' else 1.0
        cv.figure(cx, cy - r * 0.78, r * 1.55 * small, robe=robe, hair=hair, wings=wings, prop=prop, line=4)
    # 库米罗妮头上一对小鹿角、种子光环
    cv.path([(286, 683), (272, 652), (260, 660)], (150, 110, 70), 7, line=3)
    cv.path([(314, 683), (328, 652), (340, 660)], (150, 110, 70), 7, line=3)
    # 双王：左（贴窗）索恩薇娅，戴冠，深金棕的发、白金甲；右巴尔缇娜，灰银长发、黑红袍、额角一粒红
    cv.figure(300, 1350, 450, robe=(240, 236, 222), hair=(150, 104, 58), prop=('sword', (230, 225, 210)), line=5, wide=1.1)
    cv.poly([(272, 1344), (284, 1318), (300, 1338), (316, 1318), (328, 1344)], (232, 196, 90), line=3)   # 冠
    cv.figure(640, 1335, 470, robe=(70, 18, 26), hair=(212, 214, 222), prop=('scepter', (40, 30, 34)), line=5, wide=1.1)
    cv.path([(565, 1520), (530, 1700), (510, 1800)], (160, 28, 40), 40, blur=3, line=3)   # 红的披风
    # 底下：阿卡迪亚的白城、空艇、云
    for k in range(14):
        x = rnd.randint(0, 960)
        h = rnd.randint(80, 220)
        cv.poly([(x, 1960), (x, 1960 - h), (x + 18, 1960 - h - 40), (x + 36, 1960 - h), (x + 36, 1960)], (236, 240, 240), line=2)
    for x, y in ((180, 1760), (760, 1700)):
        cv.ellipse([x - 70, y - 22, x + 70, y + 22], (90, 110, 130), line=3)
        cv.poly([(x - 30, y + 18), (x + 30, y + 18), (x + 20, y + 40), (x - 20, y + 40)], (120, 90, 60), line=2)
    for k in range(9):
        x = rnd.randint(-60, 1000)
        y = rnd.randint(1820, 1990)
        r = rnd.randint(90, 170)
        cv.ellipse([x - r, y - r * 0.55, x + r, y + r * 0.55], (240, 244, 246), blur=10, alpha=235, line=2 if k % 2 else 0)
    return cv.save(folder, 'right')


SKETCHES = {'maze1001': [sketch_maze1001_left, sketch_maze1001_right]}


def cmd_sketch(args):
    folder = os.path.join(HERE, 'sketches', args.set)
    ims = [f(folder) for f in SKETCHES[args.set]]
    Image, ImageDraw, _ = _imgs()
    sheet = Image.new('RGB', (sum(i.width // 2 for i in ims) * 2 + 60, 1000 + 40), (12, 12, 16))
    x = 20
    for f, im in zip(SKETCHES[args.set], ims):
        name = f.__name__.split('_')[-1]
        sheet.paste(im.resize((im.width // 2, im.height // 2)), (x, 20))
        ln = Image.open(os.path.join(folder, name + '_line.png')).resize((im.width // 2, im.height // 2))
        sheet.paste(ln, (x + im.width // 2 + 10, 20))
        x += im.width + 30
    sheet.save(os.path.join(folder, '_sheet.png'))
    print('底稿写在', folder)


# ---------------------------------------------------------------- 工作流
class Graph:
    def __init__(self, info):
        self.nodes, self.i, self.info = {}, 0, info

    def add(self, cls, **inputs):
        if cls not in self.info:
            raise RuntimeError('ComfyUI 里没有节点 %s' % cls)
        self.i += 1
        k = str(self.i)
        spec = self.info[cls].get('input', {})
        for name, f in spec.get('required', {}).items():   # 版本不同多出来的必填项照默认值补上
            if name in inputs:
                continue
            if len(f) > 1 and isinstance(f[1], dict) and 'default' in f[1]:
                inputs[name] = f[1]['default']
            elif isinstance(f[0], list) and f[0]:
                inputs[name] = f[0][0]
            elif f[0] == 'COMBO' and len(f) > 1 and isinstance(f[1], dict) and f[1].get('options'):
                inputs[name] = f[1]['options'][0]
        self.nodes[k] = {'class_type': cls, 'inputs': inputs}
        return k


def r8(v):
    return int(round(v / 8.0)) * 8


def add_regions(g, clip, pos, regions, w, h):
    """区域提示词。ConditioningSetArea 按像素算，高清修复那一遍尺寸变了要照新尺寸另算一份。"""
    for rg in regions:
        t = g.add('CLIPTextEncode', text=rg['prompt'], clip=clip)
        x, y, rw, rh = rg['box']
        a = g.add('ConditioningSetArea', conditioning=[t, 0], width=r8(rw * w), height=r8(rh * h), x=r8(x * w), y=r8(y * h), strength=rg.get('strength', 1.0))
        pos = [g.add('ConditioningCombine', conditioning_1=pos, conditioning_2=[a, 0]), 0]
    return pos


def build(info, cfg, job, seed, up, prefix):
    g = Graph(info)
    fam = cfg['family']
    gw, gh = job['gen']
    fw, fh = job['final']
    if fam == 'flux':
        if cfg.get('ckpt'):
            ck = g.add('CheckpointLoaderSimple', ckpt_name=cfg['ckpt'])
            model, clip, vae = [ck, 0], [ck, 1], [ck, 2]
        else:
            un = g.add('UNETLoader', unet_name=cfg['unet'], weight_dtype=cfg.get('weight_dtype', 'default'))
            cl = g.add('DualCLIPLoader', clip_name1=cfg['clip1'], clip_name2=cfg['clip2'], type='flux')
            va = g.add('VAELoader', vae_name=cfg['vae'])
            model, clip, vae = [un, 0], [cl, 0], [va, 0]
    elif fam == 'anima':
        un = g.add('UNETLoader', unet_name=cfg['unet'], weight_dtype=cfg.get('weight_dtype', 'default'))
        cl = g.add('CLIPLoader', clip_name=cfg['clip'], type=cfg.get('clip_type', 'stable_diffusion'))
        va = g.add('VAELoader', vae_name=cfg['vae'])
        model, clip, vae = [un, 0], [cl, 0], [va, 0]
    else:
        ck = g.add('CheckpointLoaderSimple', ckpt_name=cfg['ckpt'])
        model, clip, vae = [ck, 0], [ck, 1], [ck, 2]
    for lr in cfg.get('loras', []):
        lo = g.add('LoraLoader', model=model, clip=clip, lora_name=lr['name'], strength_model=lr.get('w', 0.7), strength_clip=lr.get('w', 0.7))
        model, clip = [lo, 0], [lo, 1]
    text = job.get('prompt_flux') if (fam == 'flux' or cfg.get('natural_prompt')) and job.get('prompt_flux') else job['prompt']
    pos = [g.add('CLIPTextEncode', text=job.get('prompt_prefix', cfg.get('prompt_prefix', '')) + text, clip=clip), 0]
    regions = []
    if fam == 'flux':
        pos = [g.add('FluxGuidance', conditioning=pos, guidance=job.get('guidance', 3.5)), 0]
        neg = [g.add('ConditioningZeroOut', conditioning=pos), 0]
    else:
        neg = [g.add('CLIPTextEncode', text=job['negative'] + cfg.get('negative_suffix', ''), clip=clip), 0]
        regions = job.get('regions', []) if cfg.get('regions', True) else []
    pos0, neg0 = pos, neg
    cn, ls = None, None
    if cfg.get('controlnet') and up.get('line'):
        li = g.add('LoadImage', image=up['line'])
        ls = g.add('ImageScale', image=[li, 0], upscale_method='lanczos', width=gw, height=gh, crop='disabled')
        cn = [g.add('ControlNetLoader', control_net_name=cfg['controlnet']), 0]
        if cfg.get('union_type') and 'SetUnionControlNetType' in info:
            cn = [g.add('SetUnionControlNetType', control_net=cn, type=cfg['union_type']), 0]

    def conds(w, h):
        p = add_regions(g, clip, pos0, regions, w, h)
        if not cn:
            return p, neg0
        ap = g.add('ControlNetApplyAdvanced', positive=p, negative=neg0, control_net=cn, image=[ls, 0], strength=job.get('cn_strength', 0.55),
                   start_percent=0.0, end_percent=job.get('cn_end', 0.65))
        return [ap, 0], [ap, 1]

    pos, neg = conds(gw, gh)
    if cfg.get('ipadapter') and up.get('style') and fam != 'flux':
        si = g.add('LoadImage', image=up['style'])
        ul = g.add('IPAdapterUnifiedLoader', model=model, preset=cfg.get('ipa_preset', 'PLUS (high strength)'))
        ia = g.add('IPAdapterAdvanced', model=[ul, 0], ipadapter=[ul, 1], image=[si, 0], weight=job.get('ipa_weight', 0.55),
                   weight_type=cfg.get('ipa_weight_type', 'style transfer'), combine_embeds='concat', start_at=0.0, end_at=1.0, embeds_scaling='V only')
        model = [ia, 0]
    denoise = job.get('denoise', 1.0)
    if up.get('init') and denoise < 1.0:
        ii = g.add('LoadImage', image=up['init'])
        isc = g.add('ImageScale', image=[ii, 0], upscale_method='lanczos', width=gw, height=gh, crop='disabled')
        lat = [g.add('VAEEncode', pixels=[isc, 0], vae=vae), 0]
    else:
        lat = [g.add('EmptySD3LatentImage' if fam == 'flux' and 'EmptySD3LatentImage' in info else 'EmptyLatentImage', width=gw, height=gh, batch_size=1), 0]
    samp = dict(sampler_name=job.get('sampler', cfg.get('sampler', 'euler' if fam == 'flux' else 'dpmpp_2m')), scheduler=job.get('scheduler', cfg.get('scheduler', 'simple' if fam == 'flux' else 'karras')))
    scale = 1.0 if fam == 'flux' else cfg.get('cfg_scale', job.get('cfg', 6.0))
    ks = g.add('KSampler', model=model, seed=seed, steps=job.get('steps', 26 if fam == 'flux' else 30), cfg=scale,
               positive=pos, negative=neg, latent_image=lat, denoise=denoise, **samp)
    img = [g.add('VAEDecode', samples=[ks, 0], vae=vae), 0]
    hires = job.get('hires', 0)
    if hires:
        hw, hh = (r8(fw), r8(fh)) if fam not in ('flux', 'anima') else (int(math.ceil(fw / 16.0)) * 16, int(math.ceil(fh / 16.0)) * 16)
        pos2, neg2 = conds(hw, hh) if regions else (pos, neg)
        if cfg.get('upscale_model') and 'UpscaleModelLoader' in info:
            um = g.add('UpscaleModelLoader', model_name=cfg['upscale_model'])
            img = [g.add('ImageUpscaleWithModel', upscale_model=[um, 0], image=img), 0]
        img = [g.add('ImageScale', image=img, upscale_method='lanczos', width=hw, height=hh, crop='disabled'), 0]
        enc = 'VAEEncodeTiled' if cfg.get('tiled_vae') and 'VAEEncodeTiled' in info else 'VAEEncode'
        dec = 'VAEDecodeTiled' if cfg.get('tiled_vae') and 'VAEDecodeTiled' in info else 'VAEDecode'
        lat2 = [g.add(enc, pixels=img, vae=vae), 0]
        ks2 = g.add('KSampler', model=model, seed=seed + 1, steps=job.get('hires_steps', 20), cfg=scale,
                    positive=pos2, negative=neg2, latent_image=lat2, denoise=hires, **samp)
        img = [g.add(dec, samples=[ks2, 0], vae=vae), 0]
    img = [g.add('ImageScale', image=img, upscale_method='lanczos', width=fw, height=fh, crop='center'), 0]
    g.add('SaveImage', images=img, filename_prefix=prefix)
    return g.nodes


def queue_and_wait(graph, timeout=3600):
    r = post_json('/prompt', {'prompt': graph, 'client_id': uuid.uuid4().hex})
    if r.get('node_errors'):
        raise RuntimeError('工作流有错：' + json.dumps(r['node_errors'], ensure_ascii=False)[:3000])
    pid = r['prompt_id']
    t0 = time.time()
    while time.time() - t0 < timeout:
        h = get_json('/history/' + pid)
        if pid in h:
            st = h[pid].get('status', {})
            if st.get('status_str') == 'error':
                raise RuntimeError('出图出错：' + json.dumps(st, ensure_ascii=False)[:3000])
            if st.get('completed') or h[pid].get('outputs'):
                return h[pid], time.time() - t0
        time.sleep(2)
    raise RuntimeError('等了 %d 秒还没出来' % timeout)


def fetch_images(hist):
    out = []
    for node in hist.get('outputs', {}).values():
        for im in node.get('images', []):
            if im.get('type') != 'output':
                continue
            q = urllib.parse.urlencode({'filename': im['filename'], 'subfolder': im.get('subfolder', ''), 'type': 'output'})
            out.append(_open(BASE + '/view?' + q, 300))
    return out


def cmd_run(args):
    plan = json.load(open(args.plan, encoding='utf-8'))
    info = json.load(open(os.path.join(HERE, 'object_info.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, 'object_info.json')) else get_json('/object_info', 300)
    cfg = plan['config']
    only = set(args.only.split(',')) if args.only else None
    seeds = [int(s) for s in args.seeds.split(',')] if args.seeds else None
    Image = _imgs()[0]
    for job in plan['jobs']:
        if only and job['piece'] not in only:
            continue
        if args.draft:
            job = dict(job, hires=0, final=job['gen'])
        name = plan['set'] + ('_draft' if args.draft else '')
        folder = os.path.join(HERE, 'out', name, job['piece'])
        os.makedirs(folder, exist_ok=True)
        up = {}
        for key in ('init', 'line', 'style'):
            p = job.get(key)
            if p and not args.dry:
                up[key] = upload(os.path.join(HERE, p), '%s_%s_%s' % (plan['set'], job['piece'], os.path.basename(p)))
            elif p:
                up[key] = 'aldran/' + os.path.basename(p)
        for seed in (seeds or job.get('seeds', [1])):
            graph = build(info, cfg, job, seed, up, 'aldran/%s_%s_%d' % (name, job['piece'], seed))
            stem = os.path.join(folder, '%s_%d' % (job['piece'], seed))
            json.dump({'config': cfg, 'job': job, 'seed': seed, 'graph': graph}, open(stem + '.workflow.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            if args.dry:
                print('（只写工作流）', stem + '.workflow.json')
                continue
            print('出', plan['set'], job['piece'], '种子', seed, '……', flush=True)
            hist, secs = queue_and_wait(graph)
            for k, data in enumerate(fetch_images(hist)):
                im = Image.open(io.BytesIO(data)).convert('RGB')
                im.save(stem + ('' if k == 0 else '_%d' % k) + '.png')
                im.save(stem + ('' if k == 0 else '_%d' % k) + '.webp', quality=86, method=6)
            print('  好了，%.0f 秒，%s.png' % (secs, stem), flush=True)
        make_sheet(folder)


def make_sheet(folder):
    Image, ImageDraw, _ = _imgs()
    files = sorted(f for f in os.listdir(folder) if f.endswith('.png') and not f.startswith('_'))
    if not files:
        return
    ims = [Image.open(os.path.join(folder, f)).convert('RGB') for f in files]
    th = 900
    tw = [int(i.width * th / i.height) for i in ims]
    sheet = Image.new('RGB', (sum(tw) + 20 * (len(ims) + 1), th + 70), (12, 12, 16))
    d = ImageDraw.Draw(sheet)
    x = 20
    for f, im, w in zip(files, ims, tw):
        sheet.paste(im.resize((w, th)), (x, 50))
        d.text((x, 18), f, fill=(220, 210, 190))
        x += w + 20
    sheet.save(os.path.join(folder, '_sheet.jpg'), quality=86)
    print('小样', os.path.join(folder, '_sheet.jpg'))


# ---------------------------------------------------------------- 一个人物一张再合成
# 整幅一次出图，模型分不开九个人。七神一位一张裁成圆光，双王从用户给的参考图抠出来，铺在背景上，再低重绘统一画风。
def gen_part(info, cfg, job, seed, up, path, prefix):
    if os.path.exists(path):
        return
    hist, secs = queue_and_wait(build(info, cfg, job, seed, up, prefix))
    _imgs()[0].open(io.BytesIO(fetch_images(hist)[0])).convert('RGB').save(path)
    print('  %s，%.0f 秒' % (os.path.basename(path), secs), flush=True)


def paste_medallion(base, im, cx, cy, r):
    Image, ImageDraw, ImageFilter = _imgs()
    d, S = 2 * r, 4
    shadow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([cx - r - 6, cy - r - 2, cx + r + 6, cy + r + 10], fill=(70, 50, 20, 120))
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))
    mask = Image.new('L', (d * S, d * S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, d * S - 1, d * S - 1], fill=255)
    base.paste(im.convert('RGB').resize((d, d), Image.LANCZOS), (cx - r, cy - r), mask.resize((d, d), Image.LANCZOS))
    ring = Image.new('RGBA', (d * S, d * S), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    for inset, w, c in ((0, 40, (150, 104, 40, 255)), (6, 26, (232, 196, 110, 255)), (14, 8, (255, 240, 190, 255)), (52, 5, (232, 196, 110, 200))):
        rd.ellipse([inset, inset, d * S - 1 - inset, d * S - 1 - inset], outline=c, width=w)
    base.alpha_composite(ring.resize((d, d), Image.LANCZOS), (cx - r, cy - r))


def paste_cutout(base, c):
    """box 是合成图上的位置，poly 是参考图上的轮廓（照原图像素），fade 是往下渐隐进云里的那一段。"""
    Image, ImageDraw, ImageFilter = _imgs()
    src = Image.open(os.path.join(HERE, c['src'])).convert('RGB')
    mask = Image.new('L', src.size, 0)
    ImageDraw.Draw(mask).polygon([tuple(p) for p in c['poly']], fill=255)
    x, y, w, h = c['box']
    im = src.resize((w, h), Image.LANCZOS)
    mask = mask.filter(ImageFilter.GaussianBlur(4)).resize((w, h), Image.LANCZOS)
    a, b = c['fade']
    px = mask.load()
    for yy in range(max(0, a - y), h):
        k = max(0.0, 1.0 - (yy + y - a) / float(b - a))
        for xx in range(w):
            px[xx, yy] = int(px[xx, yy] * k)
    base.paste(im, (x, y), mask)


def refine_cutout(info, cfg, base, c, neg, seed, parts, stem, tag):
    """抠出来的人和这一幅差一口气：连着周围一起低重绘一遍，边缘也顺带补上。整幅重绘脸会跑，只动这一块。"""
    Image, ImageDraw, ImageFilter = _imgs()
    x, y, w, h = c['box']
    box = (max(x, 0), max(y, 0), min(x + w, base.width), min(y + h, base.height))
    crop = base.crop(box).convert('RGB')
    p = os.path.join(parts, '%s_in_%d.png' % (c['name'], seed))
    crop.save(p)
    up = {'init': upload(p, '%s_%s_in_%d.png' % (stem, c['name'], seed))}
    gen = [int(round(crop.width / 16.0)) * 16, int(round(crop.height / 16.0)) * 16]
    job = dict(gen=gen, final=gen, prompt=c['prompt'], negative=neg, steps=c.get('refine_steps', 14), denoise=c['refine'], hires=0)
    hist, secs = queue_and_wait(build(info, cfg, job, seed, up, tag))
    out = Image.open(io.BytesIO(fetch_images(hist)[0])).convert('RGB').resize(crop.size, Image.LANCZOS)
    mask = Image.new('L', crop.size, 0)
    ImageDraw.Draw(mask).rectangle([30, 30, crop.width - 31, crop.height - 31], fill=255)
    base.paste(out, box[:2], mask.filter(ImageFilter.GaussianBlur(14)))
    print('  %s 低重绘 %.2f，%.0f 秒' % (c['name'], c['refine'], secs), flush=True)


def cmd_comp(args):
    plan = json.load(open(args.plan, encoding='utf-8'))
    p_info = os.path.join(HERE, 'object_info.json')
    info = json.load(open(p_info, encoding='utf-8')) if os.path.exists(p_info) else get_json('/object_info', 300)
    cfg = plan['config']
    Image = _imgs()[0]
    for job in plan['jobs']:
        comp = job.get('comp')
        if not comp:
            continue
        piece = job['piece']
        name = plan['set'] + '_draft'
        folder = os.path.join(HERE, 'out', name, piece)
        parts = os.path.join(folder, 'parts')
        os.makedirs(parts, exist_ok=True)
        gen, final, neg = job['gen'], job['final'], job['negative']
        tag = 'aldran/%s_%s_part' % (name, piece)
        for seed in ([int(x) for x in args.seeds.split(',')] if args.seeds else job.get('seeds', [1])):
            print('合成', piece, '种子', seed, '……', flush=True)
            bg_seed = comp.get('bg_seed', seed)
            bg = os.path.join(parts, 'bg_%d.png' % bg_seed)
            bg_size = comp.get('bg_size', gen)
            gen_part(info, cfg, dict(gen=bg_size, final=bg_size, prompt=comp['bg_prompt'], negative=neg + comp.get('bg_negative', ''), steps=comp.get('bg_steps', 28), denoise=1.0, hires=0,
                                     prompt_prefix=comp.get('bg_prefix', cfg.get('prompt_prefix', ''))),
                     bg_seed, {}, bg, tag)
            base = Image.open(bg).convert('RGBA').resize(tuple(final), Image.LANCZOS)
            size = comp.get('fig_size', [640, 640])
            for m in comp['medallions']:
                p = os.path.join(parts, '%s_%d.png' % (m['name'], seed))
                gen_part(info, cfg, dict(gen=size, final=size, prompt=comp.get('fig_prefix', '') + m['prompt'], negative=neg, steps=comp.get('fig_steps', 24), denoise=1.0, hires=0),
                         seed, {}, p, tag)
                paste_medallion(base, Image.open(p), m['xy'][0], m['xy'][1], m['r'])
            for c in comp['cutouts']:
                paste_cutout(base, c)
                if c.get('refine') or args.refine:
                    refine_cutout(info, cfg, base, dict(c, refine=args.refine or c['refine']), neg, seed, parts, '%s_%s' % (name, piece), tag)
            stem = os.path.join(folder, '%s_%d' % (piece, seed))
            json.dump({'config': cfg, 'comp': comp, 'seed': seed}, open(stem + '.workflow.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            im = base.convert('RGB')
            im.save(stem + '.png')
            im.save(stem + '.webp', quality=86, method=6)
            print('  好了，%s.png' % stem, flush=True)
        make_sheet(folder)


def cmd_sheet(args):
    make_sheet(args.folder)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd')
    sp.add_parser('probe')
    s = sp.add_parser('sketch')
    s.add_argument('set')
    r = sp.add_parser('run')
    r.add_argument('plan')
    r.add_argument('--only')
    r.add_argument('--seeds')
    r.add_argument('--draft', action='store_true')
    r.add_argument('--dry', action='store_true')
    c = sp.add_parser('comp')
    c.add_argument('plan')
    c.add_argument('--seeds')
    c.add_argument('--refine', type=float)
    h = sp.add_parser('sheet')
    h.add_argument('folder')
    args = ap.parse_args()
    {'probe': cmd_probe, 'sketch': cmd_sketch, 'run': cmd_run, 'comp': cmd_comp, 'sheet': cmd_sheet}.get(args.cmd, lambda a: ap.print_help())(args)


if __name__ == '__main__':
    main()
