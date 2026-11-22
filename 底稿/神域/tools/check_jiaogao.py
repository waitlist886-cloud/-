# 交稿检查：python -I -X utf8 底稿/神域/tools/check_jiaogao.py <份名>
# 读 底稿/神域/交稿/<份名>.md，把「## 域｜X」「## 纷争纪｜X」「## 月银纪｜X」换成卡面标题拼一份临时检查稿，
# 跑 cardscan、check_people_v7、ngram，再核标题对不对得上源稿、每块几栏、多少字。
import os, re, subprocess, sys, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SHARES = {
    '离弦': ('补卷_60_神谱_离弦.md', '神谱_01_离弦.md'), '负山': ('补卷_61_神谱_负山.md', '神谱_02_负山.md'),
    '翻页甲': ('补卷_62_神谱_翻页甲.md', '神谱_03_翻页甲.md'), '翻页乙': ('补卷_63_神谱_翻页乙.md', '神谱_04_翻页乙.md'),
    '返青': ('补卷_64_神谱_返青.md', '神谱_05_返青.md'), '立边': ('补卷_65_神谱_立边.md', '神谱_06_立边.md'),
    '静光': ('补卷_66_神谱_静光.md', '神谱_07_静光.md'), '不退': ('补卷_67_神谱_不退.md', '神谱_08_不退.md'),
}
# cardscan 靠「> 条目设置」那一行认一条的正文到哪里，临时稿每节末尾要带一行，不然一条也不扫（不退那一份查出来的）
SET = '\n> 条目设置：文件夹 58·纷争纪｜神谱，触发（同时满足）〔纷争纪·正则〕、`/检查稿/`，黑名单 无，范围 用户与助手，深度 2。\n'
FEATS = '神火不落 万相 神威 擎天巨相 应名千里 职司之眼 先见 神罚 瞬临 无中造物 一言成律 封神铸器 灭却 神选 万灵应召 分相 赐名 降神 启门 立律 地上神国 封柄 镇封 夺柄'.split()


def heads(path, era):
    out = []
    for ln in open(path, encoding='utf-8'):
        m = re.match(r'^## %s·神谱｜(.+?)\s*$' % era, ln)
        if m:
            out.append(m.group(1))
    return out


def blocks(text):
    out, cur = [], None
    for ln in text.split('\n'):
        m = re.match(r'^## (域|纷争纪|月银纪|备注)(?:｜(.+?))?\s*$', ln)
        if m:
            cur = [m.group(1), m.group(2) or '', []]
            out.append(cur)
        elif cur is not None:
            cur[2].append(ln)
    return [(k, n, '\n'.join(b).strip()) for k, n, b in out]


def main(share):
    src = os.path.join(ROOT, '底稿', '神域', '交稿', share + '.md')
    bl = blocks(open(src, encoding='utf-8').read())
    f_strife, f_moon = SHARES[share]
    want_s = heads(os.path.join(ROOT, '纷争纪', '补卷', f_strife), '纷争纪')
    want_m = heads(os.path.join(ROOT, '月银纪补卷', f_moon), '月银纪')
    got_s = [n for k, n, _ in bl if k == '纷争纪']
    got_m = [n for k, n, _ in bl if k == '月银纪']
    got_d = [n for k, n, _ in bl if k == '域']
    bad = 0
    for label, want, got in (('纷争纪', want_s, got_s), ('月银纪', want_m, got_m)):
        miss = [w for w in want if w not in got]
        extra = [g for g in got if g not in want]
        print('%s 神域栏 %d／%d' % (label, len(got) - len(extra), len(want)), ('缺 ' + '、'.join(miss)) if miss else '', ('对不上源稿标题 ' + '、'.join(extra)) if extra else '')
        bad += len(miss) + len(extra)
    print('域条目 %d' % len(got_d), '、'.join(got_d))
    tmp = []
    for k, n, body in bl:
        if k == '备注':
            continue
        han = len(re.findall(r'[一-鿿]', body))
        if k == '域':
            tmp.append('## 纷争纪·神域｜%s\n\n%s\n' % (n, '\n'.join(l for l in body.split('\n') if not l.startswith('触发词'))) + SET)
            lim = (220, 400)
        else:
            tmp.append('## %s·神谱｜%s（神域栏）\n\n%s\n' % (k, n, body) + SET)
            lim = (240, 440) if k == '纷争纪' else (120, 240)
        if not lim[0] <= han <= lim[1]:
            print('  字数 %s｜%s %d（要 %d 到 %d）' % (k, n, han, lim[0], lim[1]))
        for ln in body.split('\n'):
            if ln.strip() and not ln.startswith('- ') and not ln.startswith('触发词'):
                print('  不是条目行 %s｜%s：%s' % (k, n, ln[:30]))
                bad += 1
        m = re.search(r'^- 神域专长：(.+)$', body, re.M)
        if k != '域':
            if not m:
                print('  没有神域专长行 %s｜%s' % (k, n)); bad += 1
            else:
                first = m.group(1).split('。')[0]
                for f in re.split(r'[，、]', first):
                    if f.strip() and f.strip() not in FEATS:
                        print('  目录里没有的专长 %s｜%s：%s' % (k, n, f.strip())); bad += 1
            if '- 神力：' not in body or '- 神性：' not in body:
                print('  缺神力或神性行 %s｜%s' % (k, n)); bad += 1
    d = tempfile.mkdtemp(prefix='shenyu_')
    p = os.path.join(d, share + '_检查稿.md')
    open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(tmp))
    py = [sys.executable, '-I', '-X', 'utf8']
    for cmd in (['tools/cardscan.py', p], ['tools/check_people_v7.py', p, '.'], ['tools/ngram.py', p, '语料']):
        r = subprocess.run(py + cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        lines = [x for x in (r.stdout + r.stderr).strip().split('\n') if x.strip()]
        show = [x for x in lines if '硬问题' in x or '合计' in x or 'hits' in x or '禁' in x or '冒号' in x or '标点' in x or '「' in x]
        print('==', cmd[0]); print('\n'.join(show[-14:]))
    print('结构问题', bad)


if __name__ == '__main__':
    main(sys.argv[1])
