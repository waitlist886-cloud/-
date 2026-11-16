#!/usr/bin/env python3
# 搭山铜纪、迷宫纪前传各页的洗稿活（洗的是分段稿，洗完照 tools/assemble_shantong_pN.py、tools/assemble_maze.py 重拼）。
#   python -I -X utf8 底稿/洗稿/全卡精炼/搭活_分段.py list 铜|前            只列各份有哪些文件、多少汉字
#   python -I -X utf8 底稿/洗稿/全卡精炼/搭活_分段.py make 铜|前 [份名…]     搭活的文件夹（不写份名就全搭）
#   python -I -X utf8 底稿/洗稿/全卡精炼/搭活_分段.py groups 铜|前 <份名>    把这一份的文件分给几位审稿人（一位两万六千字以内）
# 分法是算出来的：一页里 a、b、c… 各段照文件名排，一份装到可洗的五万字上下；p1_overview 并进头一份，
# p5、p6、p7 并进末一份。不洗的不进活：p0_head（碑、委托是头一层，不动）、p8_legends、p9_notes、z_notes。
import io
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
FROZEN = re.compile(r'史诗|传唱|设计备注|传奇表|凡世至强')
# 纷争纪头三页收稿时添的三条，各纪都带上
COMMON = ('另外三条各纪都一样：“这一段旅伴之间”里原稿有几对就留几对，一对一行，不并不丢。'
          '星条里的机制用语照原稿，“判定获得优势”不写成“判定有优势”，档、百分数、冷却、几回、多远一个不变。'
          '条目里写着到某个时候把一个名字、一句话告诉玩家的（龙名、真名），那个名字留在这一条里，不挪进背景条。'
          '原稿世道只写“世道照某某的时段总纲”的，照原稿留这一句，不从时段总纲里抄句子过来。')
CAP = 52000
NUM = '甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳'

ERA = {
    '铜': dict(dir='山铜纪', pages=6, note=(
        '这几份是山铜纪的分段稿，止戈以后九百四十七年。'
        '一，这一纪的冒险照剑与魔法的传统西幻写，佣兵团、遗迹、王国之间的张力，权谋的筹码是有魔力的东西，这一层收短可以，不能洗成账和手续。'
        '二，碑不在这几份里。正文里引到碑名、碑上的字，照原稿一个字不动。'
        '三，巴尔缇娜、索恩薇娅两个人的事和年份照原稿，她们的名号、称呼哪一年才有，洗后不能提早。巴尔缇娜的口癖“我记一下”只给她。'
        '四，七神照旧行于人间、不替凡人拿主意，止戈的那一位和雨城那个不说名字的女人是不是同一个人，原稿没说破的地方洗后不说破。那一位恶神不点名。'
        '五，文件末尾“这一份的设计备注”整节不动。“## 星”那一节里一颗一颗的星照命星洗，Special 的头一段不动。'
        '六，标题带凡世至强的节整节不动。')),
    '前': dict(dir='迷宫纪前传', pages=6, note=(
        '这几份是迷宫纪前传的分段稿，迷宫纪2年到1000年，戏在井下。'
        '一，这一纪照日式迷宫冒险写，下井、层、楼层主、公会、委托，这一层收短可以，不能洗成柜台上的手续。'
        '二，委托单不在这几份里。正文里引到委托的题、单子上的字，照原稿一个字不动。'
        '三，层数、第几次大迷宫潮、哪一年、几个人按印、回来几个，这些数一个不变。深度板上写的是哪一层照原稿。'
        '四，井为什么开、潮照着谁捏的、楼层主的底，原稿只给 AI 的洗后还得是只给 AI 的，不往开局和世道里挪。那一位恶神不点名，四执政不入场。'
        '五，文件末尾“这一份的设计备注”整节不动。“## 星”那一节里一颗一颗的星照命星洗，Special 的头一段不动。'
        '六，标题带凡世至强的节整节不动。')),
}


def han(s):
    return len(re.findall(r'[一-鿿]', s))


def washable(text):
    idx = [m.start() for m in re.finditer(r'^## ', text, re.M)]
    if not idx:
        return han(text)
    n = han(text[:idx[0]])
    idx.append(len(text))
    for a, b in zip(idx, idx[1:]):
        if not FROZEN.search(text[a:text.index('\n', a)]):
            n += han(text[a:b])
    return n


def size(rel):
    t = open(os.path.join(ROOT, rel), encoding='utf-8').read().replace('\r', '')
    return washable(t)


def jobs(era):
    cfg = ERA[era]
    out = []
    for p in range(1, cfg['pages'] + 1):
        d = '%s/parts%d' % (cfg['dir'], p)
        fs = sorted(f for f in os.listdir(os.path.join(ROOT, d)) if f.endswith('.md'))
        segs = [f for f in fs if not re.match(r'p\d|z_', f)]
        head = [f for f in fs if f.startswith('p1_')]
        tail = [f for f in fs if re.match(r'p[567]_', f)]
        skipped = [f for f in fs if f not in segs + head + tail]
        packs, cur, curw = [], [], 0
        for f in head + segs:
            w = size(d + '/' + f)
            if cur and curw + w > CAP:
                packs.append(cur)
                cur, curw = [], 0
            cur.append(f)
            curw += w
        tw = sum(size(d + '/' + f) for f in tail)
        if cur and curw + tw > CAP * 1.15:
            packs.append(cur)
            cur = []
        cur += tail
        if cur:
            packs.append(cur)
        for k, fl in enumerate(packs):
            name = '%s%d%s' % (era, p, NUM[k] if len(packs) > 1 else '')
            out.append((name, p, [d + '/' + f for f in fl], skipped))
    return out


cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
era = sys.argv[2] if len(sys.argv) > 2 else '铜'
if cmd == 'list':
    tot = 0
    for name, p, files, skipped in jobs(era):
        w = sum(size(f) for f in files)
        tot += w
        print('%s｜第 %d 页｜%d 个文件｜可洗 %.1f 万字｜%s' % (name, p, len(files), w / 10000, '、'.join(os.path.basename(f)[:-3] for f in files)))
    print('合计 %d 份，可洗 %.1f 万字｜不进活的：%s' % (len(jobs(era)), tot / 10000, '、'.join(sorted({re.sub(r'\.md$', '', s) for j in jobs(era) for s in j[3]}))))
elif cmd == 'make':
    want = sys.argv[3:]
    for name, p, files, _ in jobs(era):
        if want and name not in want:
            continue
        r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, 'prep_job.py'), 'make', name, 'codex'] + files +
                           ['--note', ERA[era]['note'] + COMMON], capture_output=True)
        print((r.stdout.decode('utf-8', 'replace').strip().split('\n') or [''])[-1], r.stderr.decode('utf-8', 'replace')[-300:])
elif cmd == 'pick':
    # 自己点文件起一份活：pick 铜 <份名> <相对仓库根的文件…>。
    # list 是照仓库里现在的字数现分的，一页洗了一半以后份名会挪（11-16 第五页就这样：新分法的 铜5丁、铜5戊 跟已经在用的文件夹撞名）。
    # 这种时候别拿 make 重搭撞名的份，剩下的文件拿这一条另起名字。
    name, files = sys.argv[3], sys.argv[4:]
    for f in files:
        if not os.path.isfile(os.path.join(ROOT, f)):
            raise SystemExit('没有这个文件：' + f)
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, 'prep_job.py'), 'make', name, 'codex'] + files +
                       ['--note', ERA[era]['note'] + COMMON], capture_output=True)
    print((r.stdout.decode('utf-8', 'replace').strip().split('\n') or [''])[-1], r.stderr.decode('utf-8', 'replace')[-300:])
elif cmd == 'groups':
    name = sys.argv[3]
    cap = 26000
    for n, p, files, _ in jobs(era):
        if n != name:
            continue
        groups, cur, curw = [], [], 0
        for f in files:
            w = size(f)
            if cur and curw + w > cap:
                groups.append((cur, curw))
                cur, curw = [], 0
            cur.append(os.path.basename(f))
            curw += w
        if cur:
            groups.append((cur, curw))
        for k, (g, w) in enumerate(groups, 1):
            print('第 %d 位｜可洗 %d 字｜%s' % (k, w, '、'.join(g)))
