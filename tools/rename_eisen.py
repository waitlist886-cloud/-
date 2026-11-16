#!/usr/bin/env python3
# 11-15 辛美尔小队的矮人改名：艾冯改艾泽（照原作的通行译名），传奇之名三响改砧音。
#   python -I -X utf8 tools/rename_eisen.py          只报
#   python -I -X utf8 tools/rename_eisen.py --apply  写盘
# 只改现行的源稿和工具要读的数据，方向稿、计划、备注、旧版这些记录照留旧名。拼好的页不直接改，改完分段稿重拼。
# 条目设置里的触发正则留着旧名当别名（艾[泽冯]、砧音|三响），旧存档照样叫得醒。
# “三响”在卡里别处是深井敲三下的规矩、钟敲了三响，不是名号，所以只换认得出是名号的那几种写法。
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
APPLY = '--apply' in sys.argv

FILES = '''
纷争纪/parts5/u8_notes.md
纷争纪/parts7/*.md
纷争纪/补卷/第一项_常驻与纪元钟.md
纷争纪/补卷/第一项_规则补丁.md
纷争纪/补卷/补卷_15_姓与家名.md
纷争纪/补卷/补卷_36_墙外的魔物.md
纷争纪/补卷/补卷_43_羁绊_二.md
纷争纪/补卷/补卷_44_规则_羁绊.md
纷争纪/补卷/补卷_58_羁绊_十六.md
纷争纪/补卷/补卷_67_神谱_不退.md
纷争纪/补卷/补卷_70_群陨之役_铁狼与号角的年月.md
纷争纪/补卷/补卷_73_墙下与南段诸地.md
纷争纪/纷争纪_旅伴与传奇总表.md
山铜纪/parts1/*.md
山铜纪/parts2/p9_notes.md
山铜纪/parts3/p9_notes.md
山铜纪/补卷/第一项_常驻与纪元钟.md
山铜纪/补卷/第一项_规则.md
山铜纪/补卷/补卷_04_诸族与圣堂.md
山铜纪/补卷/补卷_06_东边的巨城.md
山铜纪/补卷/补卷_25_羁绊_二.md
山铜纪/补卷/补卷_27_羁绊_三.md
tools/strife_legends.py
Art传承表_定稿.md
out/进卡_v12/tools/patch_strife.py
底稿/状态栏/comfy/cast/山铜纪/s1.json
底稿/状态栏/comfy/cast/山铜纪/s1.md
底稿/状态栏/comfy/cast/纷争纪/z7.json
底稿/状态栏/comfy/cast/纷争纪/z7.md
底稿/状态栏/comfy/strife_frame.py
底稿/状态栏/comfy/epic/in/strife_god2.json
底稿/状态栏/comfy/epic/阶段表.json
底稿/状态栏/大框/样本_纷争纪_亚蒙.txt
底稿/状态栏/大框/样本_纷争纪_墙前.txt
底稿/状态栏/大框/超凡演出_样本行.json
底稿/立绘/名册.json
底稿/立绘/名册.md
底稿/立绘/跨纪人物与穿衣脾气.md
底稿/立绘/各时代风尚_旧三纪.md
底稿/立绘/史诗战名号/纷争纪_魔神_返青立边静光不退.md
底稿/生日/登记_纷争纪.tsv
底稿/门面/卡片/纷争纪/s19.json
底稿/门面/小样_山铜纪书/build_data.py
底稿/门面/小样_山铜纪书/scenes/p1.json
底稿/门面/小样_纷争纪书/scenes/legends/gH.json
底稿/门面/小样_纷争纪书/scenes/legends/make_legend_tasks.py
底稿/门面/小样_纷争纪书/scenes/s19.json
'''.split()
NOTES = re.compile(r'(?:p9_notes|w8_notes|u8_notes)\.md$')   # 设计备注：名字照换，名号的来历是记录，不换三响

OLD, NEW = '艾冯', '艾泽'
T_OLD, T_NEW = '三响', '砧音'
# 认得出是名号的写法（都在换过名字以后的文字上认）
TITLE = [
    (r'三响(\s*[·]?\s*)艾泽', r'砧音\1艾泽'),
    (r'(叫|凝名|说到|记得|添|凡世至强|醉烛、|敲铁的|传奇之名：|角色签｜)三响', r'\1砧音'),
    (r'三响(和醉烛|、醉烛|那一条|，回了深井)', r'砧音\1'),
    (r"'艾泽', '艾泽', '三响'", "'艾泽', '艾泽', '砧音'"),
]


def settings_line(l):
    """条目设置：反引号里的正则留旧名当别名，反引号外头的话照换。"""
    parts = l.split('`')
    for i, p in enumerate(parts):
        if i % 2 == 1:
            p = p.replace(OLD, '艾[泽冯]')
            p = re.sub(r'(?<!砧音\|)三响', '砧音|三响', p) if '艾[泽冯]' in p or '白须斧' in p else p
        else:
            p = p.replace(OLD, NEW)
        parts[i] = p
    return '`'.join(parts)


def convert(path, s):
    notes = bool(NOTES.search(path))
    out = []
    for l in s.split('\n'):
        if l.startswith('> 条目设置'):
            out.append(settings_line(l))
            continue
        l2 = l.replace(OLD, NEW)
        if not notes and T_OLD in l2 and (NEW in l2 or '矮人' in l2 or '醉烛' in l2 or '白须斧' in l2 or '敲铁' in l2 or '角色签' in l2):
            for a, b in TITLE:
                l2 = re.sub(a, b, l2)
        out.append(l2)
    return '\n'.join(out)


def main():
    files = []
    for p in FILES:
        g = sorted(glob.glob(p))
        assert g, '没有这个文件：' + p
        files += g
    tot = 0
    left = []
    for f in files:
        raw = open(f, encoding='utf-8', newline='').read()
        crlf = '\r\n' in raw
        s = raw.replace('\r\n', '\n')
        t = convert(f.replace('\\', '/'), s)
        n = s.count(OLD)
        if t != s:
            tot += n
            print('%4d 处  %s' % (n, f.replace('\\', '/')))
            if APPLY:
                open(f, 'w', encoding='utf-8', newline='').write(t.replace('\n', '\r\n') if crlf else t)
        for i, l in enumerate(t.split('\n')):
            if T_OLD in l and not NOTES.search(f) and (NEW in l or '白须斧' in l or '醉烛' in l) and not l.startswith('> 条目设置'):
                left.append('%s:%d｜%s' % (f.replace('\\', '/'), i + 1, l[max(0, l.index(T_OLD) - 30):l.index(T_OLD) + 30]))
    print('合计 %d 个文件里的 %d 处%s' % (len(files), tot, '，写了盘' if APPLY else '（只报，没写）'))
    if left:
        print('还留着“三响”、又像在说他的行（逐条看）：')
        for x in left:
            print('  ' + x)


if __name__ == '__main__':
    main()
