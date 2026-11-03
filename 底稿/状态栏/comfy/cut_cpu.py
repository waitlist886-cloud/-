#!/usr/bin/env python3
# BiRefNet 抠透明底，走 CPU。这张 RX 6700 XT 的 ROCm 上 BiRefNet 的批归一化报 miopenStatusUnknownError，ComfyUI 那个节点跑不了。
# 用 ComfyUI 自带的 python：python cut_cpu.py <图目录> <输出目录> [名字前缀…]，已有的不重抠。
import glob
import os
import sys
import time
COMFY = r'C:\Users\waitl\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI (1)\ComfyUI'
MODEL = r'C:\Users\waitl\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\background_removal\birefnet.safetensors'
sys.path.insert(0, COMFY)
sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
src_dir, out_dir, *prefix = sys.argv[1:]
argv0 = sys.argv
sys.argv = sys.argv[:1]
from comfy.cli_args import args
GPU = os.environ.get('CUT_GPU') == '1'   # 设了就走显卡，关掉 MIOpen 那一路卷积和批归一化
args.cpu = not GPU
import numpy as np
import torch
if GPU:
    torch.backends.cudnn.enabled = False
from PIL import Image
from comfy.bg_removal_model import load

os.makedirs(out_dir, exist_ok=True)
files = sorted(glob.glob(os.path.join(src_dir, '*.png')))
if prefix:
    files = [f for f in files if any(os.path.basename(f).startswith(p) for p in prefix)]
files = [f for f in files if not os.path.exists(os.path.join(out_dir, os.path.basename(f)))]
if not files:
    print('没有要抠的')
    sys.exit(0)
m = load(MODEL)
for f in files:
    t0 = time.time()
    im = Image.open(f).convert('RGB')
    x = torch.from_numpy(np.asarray(im).astype(np.float32) / 255.0)[None]
    with torch.no_grad():
        mask = m.encode_image(x)[0].float().cpu().numpy()
    im.putalpha(Image.fromarray(np.uint8(np.clip(mask, 0, 1) * 255)))
    im.save(os.path.join(out_dir, os.path.basename(f)))
    print('抠', os.path.basename(f), '%.0f 秒' % (time.time() - t0), flush=True)
print('done')
