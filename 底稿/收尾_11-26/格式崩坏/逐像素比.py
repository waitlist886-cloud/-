# 两个截图目录里同名的 png 逐像素比
import sys, os
from PIL import Image, ImageChops
a, b = sys.argv[1], sys.argv[2]
for f in sorted(os.listdir(a)):
    if not f.endswith('.png') or not os.path.exists(os.path.join(b, f)): continue
    A = Image.open(os.path.join(a, f)).convert('RGB'); B = Image.open(os.path.join(b, f)).convert('RGB')
    if A.size != B.size: print(f, '尺寸不一样', A.size, B.size); continue
    d = ImageChops.difference(A, B); bb = d.getbbox()
    n = sum(1 for p in d.getdata() if p != (0, 0, 0)) if bb else 0
    print(f, '一样' if not bb else '不一样 %d 像素 框%s' % (n, bb))
