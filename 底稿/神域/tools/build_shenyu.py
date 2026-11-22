# 神域补档收稿（11-22）。在仓库根上跑：
#   python -I -X utf8 底稿/神域/tools/build_shenyu.py            只报，不写
#   python -I -X utf8 底稿/神域/tools/build_shenyu.py --apply    写盘
# 做三件事：
# 1. 交稿里「## 纷争纪｜X」「## 月银纪｜X」的神域栏，插进两纪神谱源稿各条「- 锁：」那一行前头
#    （重跑会先拿掉上一回插的：从「- 神力：」到「- 锁：」前头）。
# 2. 交稿里「## 域｜X」拼成 通用条目/神域_七十二域.md（次序照全表）。
# 3. 规则层_第一版.md 生成 通用条目/神域_规则.md（标题换成 奥尔德兰·，条目设置换成通用条目的写法）。
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_jiaogao as CJ

ROOT = CJ.ROOT
APPLY = '--apply' in sys.argv
JG = os.path.join(ROOT, '底稿', '神域', '交稿')
FOLDER_GOD = '04·神祇、魔王与龙权'
FOLDER_RULE = '05·数值、位阶与成长'


def read(p):
    return open(p, encoding='utf-8').read().replace('\r', '')


def write(p, s):
    if APPLY:
        open(p, 'w', encoding='utf-8', newline='\n').write(s)


def splice(path, era, got):
    """got: {名: 神域栏正文}。返回 (插了几条, 缺的)"""
    parts = re.split(r'(?m)^(?=## )', read(path))
    n, miss = 0, []
    for i, p in enumerate(parts):
        m = re.match(r'## %s·神谱｜(.+?)\s*\n' % era, p)
        if not m:
            continue
        name = m.group(1)
        if name not in got:
            miss.append(name)
            continue
        lines = p.split('\n')
        k = [j for j, l in enumerate(lines) if l.startswith('- 锁：')]
        assert len(k) == 1, (path, name, '锁行', len(k))
        k = k[0]
        a = [j for j, l in enumerate(lines[:k]) if l.startswith('- 神力：')]
        start = a[0] if a else k
        body = [l for l in got[name].split('\n') if l.strip()]
        assert all(l.startswith('- ') for l in body), (name, [l for l in body if not l.startswith('- ')][:1])
        lines[start:k] = body
        parts[i] = '\n'.join(lines)
        n += 1
    write(path, ''.join(parts))
    return n, miss


def domain_order():
    t = read(os.path.join(ROOT, '底稿', '神域', '七十二域全表_第一版.md'))
    return re.findall(r'(?m)^\*\*(.+?之域)\*\*', t)


def main():
    doms = {}
    for share, (f_s, f_m) in CJ.SHARES.items():
        src = os.path.join(JG, share + '.md')
        if not os.path.exists(src):
            print('没交', share)
            continue
        bl = CJ.blocks(read(src))
        got_s = {n: b for k, n, b in bl if k == '纷争纪'}
        got_m = {n: b for k, n, b in bl if k == '月银纪'}
        for k, n, b in bl:
            if k == '域':
                assert n not in doms, ('域重了', n)
                doms[n] = b
        r1 = splice(os.path.join(ROOT, '纷争纪', '补卷', f_s), '纷争纪', got_s)
        r2 = splice(os.path.join(ROOT, '月银纪补卷', f_m), '月银纪', got_m)
        print('%s 纷争纪 %d 缺 %s｜月银纪 %d 缺 %s' % (share, r1[0], r1[1] or '无', r2[0], r2[1] or '无'))

    order = domain_order()
    out = ['# 通用条目｜七柱七十二域（11-22 神域玩法）', '',
           '> 这一节是说明，不进卡。一域一条，四纪和迷宫纪1001年都用，不挡纪元。由 `底稿/神域/tools/build_shenyu.py` 从 `底稿/神域/交稿/` 各份的「## 域｜」拼成，要改改交稿再重跑。规则在 神域_规则.md「七柱七十二域」那一条，全表在 `底稿/神域/七十二域全表_第一版.md`。', '']
    lack = [d for d in order if d not in doms]
    extra = [d for d in doms if d not in order]
    for d in order:
        if d not in doms:
            continue
        body, trig = [], []
        for l in doms[d].split('\n'):
            if l.startswith('触发词'):
                trig = [w.strip() for w in re.split(r'[、，]', l.split('：', 1)[1]) if w.strip()]
            elif l.strip():
                body.append(l)
        if d not in trig:
            trig.insert(0, d)
        assert all('`' not in w and '/' not in w for w in trig), (d, trig)
        out += ['## 奥尔德兰·神域｜%s' % d, '', '【调用】说到%s归谁、这一域的祭司求得来什么、朝这一域起的誓作不作数的时候用。' % d.replace('之域', '这一域'), '']
        out += body
        out += ['', '> 条目设置：文件夹 %s，触发 %s，黑名单 无，范围 用户与AI，深度 2。' % (FOLDER_GOD, '、'.join(trig)), '']
    write(os.path.join(ROOT, '通用条目', '神域_七十二域.md'), '\n'.join(out))
    print('域 %d／%d' % (len(order) - len(lack), len(order)), ('缺 ' + '、'.join(lack)) if lack else '', ('全表里没有 ' + '、'.join(extra)) if extra else '')

    t = read(os.path.join(ROOT, '底稿', '神域', '规则层_第一版.md'))
    t = t.split('## 设计备注（不进卡）')[0]
    parts = re.split(r'(?m)^(?=## )', t)[1:]
    out = ['# 通用条目｜神域玩法规则层（11-22）', '',
           '> 这一节是说明，不进卡。凡极以后神力等级那一层的规则，四纪和迷宫纪1001年都用，不挡纪元，接在底卡神之领域、凡极之上、神域之路那几条后头。由 `底稿/神域/tools/build_shenyu.py` 从 `底稿/神域/规则层_第一版.md` 生成，要改改那一份再重跑。方向稿在根目录 神域玩法_方向稿.md。', '']
    n = 0
    for p in parts:
        m = re.match(r'## 纷争纪·规则｜(.+?)\s*\n', p)
        assert m, p[:30]
        body = p[m.end():]
        s = re.search(r'(?m)^> 条目设置：.*?(`/.+/`).*$', body)
        assert s, m.group(1)
        body = body[:s.start()].strip('\n')
        out += ['## 奥尔德兰·规则｜%s' % m.group(1), '', body, '',
                '> 条目设置：文件夹 %s，触发 %s，黑名单 无，范围 用户与AI，深度 2。' % (FOLDER_RULE, s.group(1)), '']
        n += 1
    write(os.path.join(ROOT, '通用条目', '神域_规则.md'), '\n'.join(out))
    print('规则 %d 条' % n, '（写盘了）' if APPLY else '（没写盘，加 --apply）')


if __name__ == '__main__':
    main()
