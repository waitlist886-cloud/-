#!/usr/bin/env python3
# 传奇的【能力】一节，收稿检查（11-09）。写稿的子任务交稿以前跑，主会话收稿也跑。只读，不改任何文件。
# 用法（在仓库根目录下）：python -I -X utf8 底稿/传奇能力/查稿.py 底稿/传奇能力/份N.md [--card 打好的卡.json] [--no-names]
# --card 默认是 11-09 第四回打的那一张 v12 试打卡（洗稿层是双王那一版），用来查旧名字还在别处用着没有、新名字撞不撞。
# 份N.md 的格式见 底稿/传奇能力/派活说明.md 第五节。
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.getcwd()
W = os.path.join(ROOT, '底卡洗稿')
CARD = r'C:/Users/waitl/AppData/Local/Temp/claude/85a810c2c0993c77/e22307d9-b63e-4d31-ad24-f0ffb0fc6126/scratchpad/v12_1109d/奥尔德兰_日里版_四纪全卷_测试v12.json'
# 立绘资料里写着的身高（底稿/状态栏/comfy/cast/cast_*.json 的 who），体态数据的身高照它，没有的自己定并标★
CAST_H = {880: 215, 883: 176, 884: 166, 886: 172, 887: 188, 888: 178, 889: 140, 890: 175, 891: 170, 892: 182,
          893: 178, 894: 195, 895: 152, 896: 188, 897: 125, 898: 172, 899: 185, 900: 170, 901: 140, 902: 140,
          903: 168, 904: 184, 905: 163, 906: 166, 907: 205, 908: 175, 909: 172, 910: 176, 911: 170, 912: 118,
          913: 168, 914: 195, 915: 105, 916: 172, 917: 178, 921: 190, 922: 160}
BAN_PUNCT = ['——', '—', '；', '…', '！', '...']
# 能力里不该出现的办事手续（计划第二节第5条），出现了不一定错，逐处看
SOFT = ['条款', '账', '粮', '登记', '流程', '审批', '程序', '手续', '盘问', '讯问', '诘问', '伟业簿', '报表', '名册', '签字', '盖章', '公文']
NEED = ['命路：', '职业：', 'Special：', 'Passive：', 'Art：', '职业能力｜', '专长【', '独有机制【', '被动【', '被动【', '主动【', '主动【', '早先三层：']


def entry(fn, n):
    s = open(os.path.join(W, fn), encoding='utf-8').read().replace('\r\n', '\n')
    m = re.search(r'(?m)^## #%d .*$' % n, s)
    if not m:
        return None
    f1 = s.index('\n````\n', m.end()) + 5
    f2 = s.index('\n````', f1)
    return s[f1:f2]


def ability(text):
    m = re.search(r'【能力｜([^】]*)】\n((?:- [^\n]*(?:\n|$))*)', text)
    if not m:
        return None, None, []
    return m.group(0).rstrip('\n'), m.group(1), m.group(2).rstrip('\n').split('\n')


def parse(path):
    lines = open(path, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
    blocks, cur = [], None
    for i, l in enumerate(lines):
        m = re.match(r'^## #(\d+)', l)
        if m:
            cur = {'n': int(m.group(1)), 'head': l, 'lines': []}
            blocks.append(cur)
            continue
        if cur is not None:
            cur['lines'].append(l)
    out = []
    for b in blocks:
        ls = b['lines']
        d = {'n': b['n'], 'to': None, 'pass': [], 'body': None, 'ab': None, 'stars': [], 'notes': []}
        i = 0
        while i < len(ls):
            l = ls[i]
            if l.startswith('> 补到｜'):
                p = l.split('｜')
                d['to'] = (p[1].strip(), p[2].strip()) if len(p) >= 3 else None
            elif l.startswith('> 放行｜'):
                d['pass'] = [x.strip() for x in re.split('[、，,]', l.split('｜', 1)[1]) if x.strip()]
            elif l.startswith('体态数据｜'):
                d['body'] = l
            elif l.startswith('【能力｜'):
                j = i + 1
                while j < len(ls) and ls[j].startswith('- '):
                    j += 1
                d['ab'] = '\n'.join(ls[i:j])
                i = j
                continue
            elif l.startswith('> 页上的星'):
                j = i + 1
                while j < len(ls) and ls[j].startswith('- '):
                    d['stars'].append(ls[j])
                    j += 1
                i = j
                continue
            elif l.startswith('> 备注'):
                d['notes'].append(l)
            i += 1
        out.append(d)
    return out


def names_in(ab):
    ns = set(re.findall(r'【([^】｜]{1,16})】', ab))
    m = re.search(r'- 职业：([^。\n]*)', ab)
    if m:
        for part in m.group(1).split('←'):
            nm = re.sub(r'\s*\(.*', '', part).replace('·Ⅳ', '').strip()
            if nm:
                ns.add(nm)
    return ns


def main():
    args = sys.argv[1:]
    card = CARD
    if '--card' in args:
        card = args[args.index('--card') + 1]
        args.remove('--card')
        args.remove(card)
    do_names = '--no-names' not in args
    args = [a for a in args if a != '--no-names']
    path = args[0]
    blocks = parse(path)
    print('份文件', path, '｜', len(blocks), '位')
    lb = None
    pages = []
    others = []
    if do_names:
        d = json.load(open(card, encoding='utf-8'))
        lb = [(i, e.get('content', ''), (e.get('content', '').split('\n', 1)[0])[:30]) for i, e in enumerate(d['prompt']['lorebook'])]
        lb.append((-1, d.get('introPage', '') or '', '介绍页'))
        # 命路、职业谱、流派那几条（#161 到 #259）里本来就有的名字，几位传奇共用是应当的，不算撞
        jobtext = '\n'.join(c for i, c, t in lb if 161 <= i <= 259)
        for f in glob.glob(os.path.join(ROOT, '**', '*.md'), recursive=True):
            if os.sep + '语料' + os.sep in f or os.sep + '.claude' + os.sep in f or 'node_modules' in f:
                continue
            if os.path.abspath(f) == os.path.abspath(path):
                continue
            if os.sep + '传奇能力' + os.sep in f and os.path.basename(f).startswith('份'):
                # 别的份只看【能力】块里起的名字，备注里提到的不算
                used = set()
                for ob in parse(f):
                    if ob['ab']:
                        used |= names_in(ob['ab'])
                others.append((f, '\n'.join(sorted(used))))
                continue
            if os.sep + '底卡洗稿' + os.sep in f:
                continue
            rel = os.path.relpath(f, ROOT)
            if rel == 'CLAUDE.md' or rel.startswith(('交接存档', os.path.join('底稿', '洗稿'), os.path.join('底稿', '传奇能力'))):
                continue
            pages.append((f, open(f, encoding='utf-8', errors='replace').read()))
    total_hard = 0
    tmp_parts = []
    for b in blocks:
        n = b['n']
        warn, hard = [], []
        if not b['to']:
            hard.append('没有「> 补到｜批次文件｜#号」那一行')
            print('\n#%d' % n, '｜'.join(hard))
            total_hard += len(hard)
            continue
        fn, tag = b['to']
        if tag != '#%d' % n:
            hard.append('补到那一行的号 %s 跟标题 #%d 对不上' % (tag, n))
        body = entry(fn, n)
        if body is None:
            hard.append('%s 里找不到 #%d' % (fn, n))
            print('\n#%d' % n, '｜'.join(hard))
            total_hard += len(hard)
            continue
        old_ab, who, old_lines = ability(body)
        anc = re.search(r'固定锚定：([^\n]*)', body).group(1)
        female = '性别=女' in anc
        race = re.search(r'种族锚定=([^｜。]*)', anc).group(1)
        look = re.search(r'外表([^｜。]*)', anc)
        look = look.group(1) if look else ''
        exempt = ('半身人' in race or '妖精' in race or re.match(r'十[一二三四五六七]|[一二三四五六七八九]岁', look) is not None)
        ab = b['ab']
        if not ab:
            hard.append('没有【能力｜…】那一块')
        else:
            if ab.split('\n')[0] != '【能力｜%s】' % who:
                hard.append('头一行要照原来写成【能力｜%s】' % who)
            body_lines = ab.split('\n')[1:]
            heads = [l[2:] for l in body_lines]
            k = 0
            for need in NEED:
                while k < len(heads) and not heads[k].startswith(need):
                    k += 1
                if k == len(heads):
                    hard.append('缺「- %s」，或者次序不对（命路、职业、Special、Passive、来路、Art、留下的旧行、职业能力、专长、独有机制、被动两条、主动两条、早先三层）' % need)
                    break
                k += 1
            for key in ('Special：', 'Passive：', 'Art：'):
                for h in heads:
                    if h.startswith(key) and '(Unique)' not in h:
                        hard.append('%s 那一行没写 (Unique)' % key[:-1])
            for l in body_lines:
                if '：' in l:
                    lab = l[2:].split('：', 1)[0]
                    if len(lab) > 8 or '，' in lab or '。' in lab:
                        hard.append('冒号前的标签超过八个字或带了标点，换成｜：%s' % l[:24])
                for p in BAN_PUNCT:
                    if p in l:
                        hard.append('禁用标点 %s：%s' % (p, l[:24]))
                for w in SOFT:
                    if w in l and not l.startswith('- 来路'):
                        warn.append('办事手续的字眼「%s」，看一眼是不是又往制度上写了：%s' % (w, l[:30]))
            kept = [l for l in old_lines if not re.match(r'- (天赋|被动|技艺)【', l)]
            for l in kept:
                if l not in body_lines:
                    hard.append('原来这一行要原样留在新块里：%s' % l[:30])
            size = len(re.sub(r'\s', '', ab))
            if size < 1300 or size > 2400:
                warn.append('长短 %d 字（不算空白），照双王是一千五到两千' % size)
            else:
                warn.append('长短 %d 字' % size)
        bl = b['body']
        if not bl:
            hard.append('没有体态数据那一行')
        else:
            if female and not exempt:
                if not re.match(r'^体态数据｜身高 \d{2,3}cm｜三维 \d{2,3} / \d{2,3} / \d{2,3}｜[A-H]-cup｜[^｜]+$', bl):
                    hard.append('成年女性写成 体态数据｜身高 Xcm｜三维 a / b / c｜X-cup｜身架一句')
            else:
                if not re.match(r'^体态数据｜身高 \d{2,3}cm｜[^｜]+$', bl) or '三维' in bl or 'cup' in bl:
                    hard.append('%s只写 体态数据｜身高 Xcm｜身架一句，不写三维和杯' % ('这一位' if exempt else '男性'))
            m = re.search(r'身高 (\d{2,3})cm', bl)
            if m and n in CAST_H and int(m.group(1)) != CAST_H[n]:
                warn.append('身高 %scm，立绘资料写的是 %dcm' % (m.group(1), CAST_H[n]))
        # 旧名字：天赋、被动、技艺三行的名字，新块和这一条别处都没有了的，要进放行；别处还在用的，倾向留作俗名
        if old_ab:
            olds = [re.match(r'- (?:天赋|被动|技艺)【([^】]*)】', l).group(1) for l in old_lines if re.match(r'- (?:天赋|被动|技艺)【', l)]
            rest = body.replace(old_ab, '')
            for o in olds:
                if ab and o in ab:
                    continue
                if o in rest:
                    continue
                if o not in b['pass']:
                    hard.append('旧名字【%s】新块里没有了，要写进「> 放行｜」' % o)
                if lb is not None:
                    where = [t for i, c, t in lb if i != n and o in c]
                    pg = [os.path.relpath(f, ROOT) for f, c in pages if o in c]
                    if where or pg:
                        warn.append('旧名字【%s】别处还在用：卡里 %d 条（%s）｜页和补卷 %d 个文件（%s）。倾向在新星里留一句它是俗名或露出来的头一点' % (
                            o, len(where), '、'.join(where[:3]), len(pg), '、'.join(pg[:3])))
        if do_names and ab:
            for nm in sorted(names_in(ab)):
                if len(nm) < 2 or nm in jobtext:
                    continue
                where = [t for i, c, t in lb if i != n and nm in c]
                pg = [os.path.relpath(f, ROOT) for f, c in pages if nm in c]
                ot = [os.path.basename(f) for f, c in others if nm in c]
                if ot:
                    hard.append('新名字【%s】撞了别的份：%s' % (nm, '、'.join(ot)))
                if where or pg:
                    warn.append('名字【%s】卡里 %d 条（%s）｜页和补卷 %d 个文件（%s）' % (
                        nm, len(where), '、'.join(where[:3]), len(pg), '、'.join(pg[:2])))
        for s_ in b['stars']:
            if not re.match(r'^- [^｜]+｜###? [^｜]+｜[A-Za-z]+｜.+$', s_):
                warn.append('页上的星那一行写成「- 文件｜### 星标题｜现阶｜对上哪一颗」：%s' % s_[:30])
        total_hard += len(hard)
        print('\n#%d %s｜%s%s｜硬 %d' % (n, who, race, '（只写身高）' if exempt else '', len(hard)))
        for h in hard:
            print('  [硬]', h)
        for w_ in warn:
            print('  [看]', w_)
        if ab:
            tmp_parts.append('## 迷宫纪·人物｜%s\n%s\n\n%s\n' % (who, bl or '', ab))
    # 卡面四样
    tf = tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8')
    tf.write('\n'.join(tmp_parts))
    tf.close()
    py = sys.executable
    print('\n== 卡面检查（check_people_v7、cardscan、authormark、原神撞句）')
    r = subprocess.run([py, '-I', '-X', 'utf8', 'tools/check_people_v7.py', tf.name, '.'], capture_output=True, text=True, encoding='utf-8')
    for l in r.stdout.split('\n'):
        if l.startswith('==') and l.count('|') >= 4 and l.split('|', 4)[4].strip():
            print(' ', l[:200])
        if '硬问题合计' in l:
            print(' ', l[:120])
    for tool in ('tools/cardscan.py', 'tools/authormark.py'):
        r = subprocess.run([py, '-I', '-X', 'utf8', tool, tf.name], capture_output=True, text=True, encoding='utf-8')
        out = [l for l in r.stdout.split('\n') if l.strip()]
        bad = [l for l in out[:-1]][:12]
        print(' ', tool, out[-1] if out else '（没有输出）')
        if out and out[-1].strip() != '合计 0':
            for l in bad:
                print('    ', l[:160])
    if os.path.isdir(os.path.join(ROOT, '语料')):
        r = subprocess.run([py, '-X', 'utf8', 'tools/ngram.py', tf.name, '语料'], capture_output=True, text=True, encoding='utf-8')
        out = [l for l in r.stdout.split('\n') if l.strip()]
        print('  原神撞句', out[-1] if out else '（没有输出）')
        if out and not out[-1].rstrip().endswith('hits 0'):
            for l in out[:-1][:10]:
                print('    ', l[:160])
    os.unlink(tf.name)
    print('\n硬问题合计', total_hard, '（要改到 0；[看] 的逐条看过，留下的在「> 备注｜」里说一句为什么）')


if __name__ == '__main__':
    main()
