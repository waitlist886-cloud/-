#!/usr/bin/env python3
# 搭纷争纪七页的洗稿活（洗的是分段稿，洗完照 tools/assemble_strife.sh 重拼）。
#   python -I -X utf8 底稿/洗稿/全卡精炼/搭活_纷争纪.py list            只列各份有哪些文件、多少汉字
#   python -I -X utf8 底稿/洗稿/全卡精炼/搭活_纷争纪.py make [份名…]    搭活的文件夹（不写份名就全搭）
#   python -I -X utf8 底稿/洗稿/全卡精炼/搭活_纷争纪.py groups <份名>   把这一份的文件分给几位审稿人（一位两万四千字以内）
# 不洗的分段不进活：史诗（*_head）、设计备注（*_notes）、整份都是凡世至强的（*新传奇*、*持影*、v7a_cenwa）。
import io
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
FROZEN = re.compile(r'史诗|传唱|设计备注|传奇表|凡世至强')

NOTE = ('这几份是纷争纪的分段稿，一万一千年的长垒血战。'
        '一，这一纪尺度大、是高魔，原稿主线的世道那一栏里写着的整条墙、整场仗，收短可以，不能洗没。'
        '原稿世道只写“世道照某某的时段总纲”的，就照原稿留这一句，不从时段总纲里抄尺度的句子过来（总纲自己常驻）。'
        '二，诺伦·晨曦在原稿里哪里写他、哪里写她，照原稿一个字不换，表层一律是他。'
        '三，传奇之名、神名、魔神名、名号照原稿，不替谁起名，只给 AI 的底不往开局和世道里挪。'
        '四，那一位恶神不点名，两军之间那个女人不说名字，四执政不入场，原稿没写的不添。'
        '五，伤亡册第几卷第几页、几根石柱、几根鹿角、几座营垒，这些数一个不变。'
        '六，有的文件只有 `### ` 的星条、没有 `## ` 标题，那是这一页命星一节的后半截，照样一颗一颗洗，Special 的头一段不动。'
        '七，标题带凡世至强的节整节不动。'
        '八，魔族那一边不泛用“营”字，原稿写部、支、帐子、篝火的照原稿，别换成营。'
        '九，“这一段旅伴之间”里原稿有几对就留几对，一对一行，不并不丢。'
        '十，星条里的机制用语照原稿：“判定获得优势”不写成“判定有优势”，档、百分数、冷却、几回、多远一个不变。'
        '十一，条目里写着到某个时候把一个名字、一句话告诉玩家的（龙名、真名），那个名字留在这一条里，不挪进背景条。')

P = {1: 'parts', 2: 'parts2', 3: 'parts3', 4: 'parts4', 5: 'parts5', 6: 'parts6', 7: 'parts7'}
JOBS = [
    ('纷1', 1, ['p2_overview', 'p3_line1', 'p4_line2', 'p5_line3', 'p6_stars', 'p7_people']),
    ('纷2甲', 2, ['q2_overview', 'q3_line4', 'q4_line5', 'q4b_comp5', 'q5_line6']),
    ('纷2乙', 2, ['q6_line7', 'q7_stars', 'q8_people']),
    ('纷3甲', 3, ['r2_overview', 'r3_line8', 'r3b_gap_700', 'r4_line9']),
    ('纷3乙', 3, ['r5_line10', 'r6_stars', 'r6b_stars_700', 'r7_people']),
    ('纷4甲', 4, ['t2_overview', 't3_line11', 't3a_gap_1790', 't3b_gap_2400']),
    ('纷4乙', 4, ['t4_line12', 't5_line13', 't5b_gap_3400', 't7_people', 't7c_people_3400', 't7d_people_1790']),
    ('纷4丙', 4, ['t5c_gap_3600', 't5d_gap_4200', 't6_stars', 't6b_stars_2400', 't6c_stars_3400', 't6d_stars_1790', 't6e_stars_3600', 't6f_stars_4200']),
    ('纷5甲', 5, ['u2_overview', 'u2b_gap_4601', 'u2c_gap_5200', 'u2d_gap_5300']),
    ('纷5乙', 5, ['u3_line14', 'u4_line15', 'u4b_gap_7166']),
    ('纷5丙', 5, ['u4c_gap_7672', 'u5_line16', 'u5b_gap_8780']),
    ('纷5丁', 5, ['u6_stars', 'u6b_stars_4601', 'u6c_stars_5200', 'u6d_stars_7166', 'u6e_stars_7672', 'u6f_stars_5300', 'u6g_stars_8780',
                'u7c_people_5200', 'u7d_people_7166', 'u7g_people_8780', 'u7_people']),
    ('纷6甲', 6, ['v2_overview', 'v3_line17', 'v3b_gap_9520']),
    ('纷6乙', 6, ['v3c_gap_9800', 'v3d_gap_10200']),
    ('纷6丙', 6, ['v3e_gap_10500', 'v4_line18']),
    ('纷6丁', 6, ['v6_stars', 'v6a_stars17', 'v6b_stars18', 'v6c_stars_9520', 'v6d_stars_9800', 'v6e_stars_10200', 'v6f_stars_10500', 'v7d_people_10200', 'v7_people']),
    ('纷7甲', 7, ['w2_overview', 'w3_line19']),
    ('纷7乙', 7, ['w4_line20', 'w5_line21']),
    ('纷7丙', 7, ['w6_stars', 'w6a_stars19', 'w6b_stars20', 'w6c_stars21', 'w7_people']),
]


def path(page, base):
    return '纷争纪/%s/%s.md' % (P[page], base)


def han(s):
    return len(re.findall(r'[一-鿿]', s))


def washable(text):
    """可洗的汉字数：去掉冻住的 ## 节；没有 ## 的文件整份算。"""
    idx = [m.start() for m in re.finditer(r'^## ', text, re.M)]
    if not idx:
        return han(text)
    n = han(text[:idx[0]])
    idx.append(len(text))
    for a, b in zip(idx, idx[1:]):
        if not FROZEN.search(text[a:text.index('\n', a)]):
            n += han(text[a:b])
    return n


def sizes(page, bases):
    out = []
    for b in bases:
        t = open(os.path.join(ROOT, path(page, b)), encoding='utf-8').read().replace('\r', '')
        out.append((b, han(t), washable(t)))
    return out


def all_parts_covered():
    used = {(p, b) for _, p, bs in JOBS for b in bs}
    for p, d in P.items():
        for f in sorted(os.listdir(os.path.join(ROOT, '纷争纪', d))):
            if not f.endswith('.md'):
                continue
            b = f[:-3]
            skip = re.search(r'_head$|_notes$|新传奇|持影|cenwa', b)
            if (p, b) not in used and not skip:
                print('！没排进活的分段：', path(p, b))
            if (p, b) in used and skip:
                print('！不该洗的分段排进了活：', path(p, b))


cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
if cmd == 'list':
    tot = 0
    for name, page, bases in JOBS:
        sz = sizes(page, bases)
        w = sum(x[2] for x in sz)
        tot += w
        print('%s｜第 %d 页｜%d 个文件｜可洗 %.1f 万字｜%s' % (name, page, len(bases), w / 10000, '、'.join(b for b, _, _ in sz)))
    print('合计 %d 份，可洗 %.1f 万字' % (len(JOBS), tot / 10000))
    all_parts_covered()
elif cmd == 'make':
    want = sys.argv[2:]
    for name, page, bases in JOBS:
        if want and name not in want:
            continue
        r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, 'prep_job.py'), 'make', name, 'codex'] +
                           [path(page, b) for b in bases] + ['--note', NOTE], capture_output=True)
        print((r.stdout.decode('utf-8', 'replace').strip().split('\n') or [''])[-1], r.stderr.decode('utf-8', 'replace')[-300:])
elif cmd == 'groups':
    name = sys.argv[2]
    cap = 24000
    for n, page, bases in JOBS:
        if n != name:
            continue
        groups, cur, curw = [], [], 0
        for b, _, w in sizes(page, bases):
            if cur and curw + w > cap:
                groups.append((cur, curw))
                cur, curw = [], 0
            cur.append(b)
            curw += w
        if cur:
            groups.append((cur, curw))
        for k, (g, w) in enumerate(groups, 1):
            print('第 %d 位｜可洗 %d 字｜%s' % (k, w, '、'.join(x + '.md' for x in g)))
