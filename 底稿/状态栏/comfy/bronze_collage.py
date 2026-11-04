#!/usr/bin/env python3
# 山铜纪右扇：用户说现在的索恩薇娅看着怪（right4 比头一稿小了将近四成，两条腿笔直露着）。
# 只靠文字说“照头一稿的姿势”GPT 守不住大小，所以把头一稿的她原样挪过来贴在 right4 上当底（手对到剑柄上），再叫 GPT 照这个大小和姿势换回立绘上的头发和衣服。
# 写 ref/collage_thornevia.png（底）、ref/p_thornevia.png（立绘）。要 PIL，用 ComfyUI 那个 venv 的 python。
import os
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, 'out', '山铜纪_11-04')
REF = os.path.join(ROOT, 'ref')
DX, DY = -13, -28       # 头一稿的手在 (258,278)，right4 的手在 (245,250)
# 头一稿里她的轮廓（图的像素）：胳膊、头、身子、长外套，右边那一大片披风用 right4 自己的
POLY = [(250, 262), (305, 305), (360, 340), (420, 380), (445, 300), (480, 268), (540, 268), (585, 330), (596, 420),
        (640, 520), (652, 640), (668, 790), (440, 790), (392, 700), (322, 590), (372, 430), (330, 400), (280, 345), (246, 300)]

v1 = Image.open(os.path.join(ROOT, 'right.png')).convert('RGB')
base = Image.open(os.path.join(ROOT, 'right4.png')).convert('RGB')
m = Image.new('L', base.size, 0)
ImageDraw.Draw(m).polygon([(x + DX, y + DY) for x, y in POLY], fill=255)
m = m.filter(ImageFilter.GaussianBlur(2))
layer = base.copy()
layer.paste(v1, (DX, DY))
Image.composite(layer, base, m).save(os.path.join(REF, 'collage_thornevia.png'))
sheet = Image.open(os.path.join(REF, 'sheet_east.png')).convert('RGB')
sheet.crop((0, 56, 512, 640)).save(os.path.join(REF, 'p_thornevia.png'))
print('ok')
