#!/usr/bin/env python3
# 风月五张打 zip（11-28 起写成脚本，原来手打）：一纪一个 风月_<短名>_<版本>.zip，装 导入/ 底下的东西；前传另打一个 本卡加mod（拆mod/ 底下的东西）。
#   python -I -X utf8 底稿/风月版/zip_fy.py <版本>
import os
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'out', '发布卡_风月_四纪')
ERAS = [('月银纪', '月银纪'), ('纷争纪', '纷争纪'), ('山铜纪', '山铜纪'), ('迷宫纪前传', '前传'), ('迷宫纪此刻', '此刻')]


def pack(src, dst):
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(src)):
            p = os.path.join(src, f)
            if os.path.isfile(p):
                z.write(p, f)
    print(os.path.basename(dst), os.path.getsize(dst) // 1024, 'KB')


def main():
    ver = sys.argv[1]
    for d, short in ERAS:
        pack(os.path.join(OUT, d, '导入'), os.path.join(OUT, '风月_%s_%s.zip' % (short, ver)))
    mod = os.path.join(OUT, '迷宫纪前传', '拆mod')
    if os.path.isdir(mod):
        pack(mod, os.path.join(OUT, '风月_前传_本卡加mod_%s.zip' % ver))


if __name__ == '__main__':
    main()
