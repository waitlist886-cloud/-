#!/usr/bin/env python3
# 全卡精炼洗稿：收一份审过的稿子（主会话用）。在仓库根上跑：
#   python -I -X utf8 底稿/洗稿/全卡精炼/收稿.py <份名…> [--apply] [--engine codex|agy]
# 不加 --apply 只报，一样一样列出来：
#   1. 自查（稿/ 对 原/）：错几条、看几条
#   2. 审稿人动了多少（稿/ 对 稿_Codex原样/）：各节字数、补回是不是守住了上限
#   3. 一节一节留了多少（可洗的各节）
#   4. 命星一节里 Special、Passive 的头一句还有没有“生来、天赋、体质”一类的字
# 加 --apply：先照 prep_job.py take 拷回仓库，再对标签 详本_11-15 查受保护的行、跑 tools/recv_check.sh。
import io
import json
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
BASE = {'codex': 'C:/Users/waitl/codex_work/wash_1115', 'agy': 'C:/Users/waitl/agy_work/wash_1115'}
TAG = '详本_11-15'
FROZEN = re.compile(r'史诗|传唱|设计备注|传奇表')
BORN = re.compile(r'生来|天赋|体质|生下来|打小|胎里|与生俱来|天生|生就|落地|娘胎|血里|骨头里|一出生|出生时|生在')
han = lambda s: len(re.findall(r'[一-鿿]', s))


def rd(p):
    return open(p, encoding='utf-8', newline='').read().replace('\r\n', '\n')


def sections(text):
    out, cur, buf = [], '', []
    for l in text.split('\n'):
        if l.startswith('## '):
            out.append((cur, '\n'.join(buf)))
            cur, buf = l[3:].strip(), [l]
        else:
            buf.append(l)
    out.append((cur, '\n'.join(buf)))
    return out


def stars(text):
    """回 [(标题, 头一句)]：### 名字 (Special|Passive | 档) 底下头一行正文的头一句。"""
    out = []
    ls = text.split('\n')
    for i, l in enumerate(ls):
        m = re.match(r'^### (.+?) \((Special|Passive) \| ', l)
        if not m:
            continue
        body = ''
        for k in ls[i + 1:i + 8]:
            if k.strip() and not k.startswith(('#', '>', '【调用】', '- ')):          # 【调用】那一行不算头一句
                body = k.strip()
                break
        out.append((m.group(1), m.group(2), re.split(r'。', body)[0][:90]))
    return out


def one(name, engine, apply):
    d = os.path.join(BASE[engine], name)
    meta = json.load(open(os.path.join(d, 'job.json'), encoding='utf-8'))
    print('=' * 12, name)
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, '自查.py'), os.path.join(d, '稿'), os.path.join(d, '原')], capture_output=True)
    out = r.stdout.decode('utf-8', 'replace')
    bad = [l for l in out.split('\n') if l.strip().startswith(('错｜', '看｜'))]
    print('自查：', out.strip().split('\n')[-1], '' if not bad else '\n  ' + '\n  '.join(x.strip()[:110] for x in bad[:14]))
    ok = '错 0' in out.strip().split('\n')[-1]
    for base, f in meta['files'].items():
        old, new = rd(os.path.join(d, '原', base)), rd(os.path.join(d, '稿', base))
        cx = os.path.join(d, '稿_Codex原样', base)
        cod = rd(cx) if os.path.exists(cx) else None
        so, sn = sections(old), dict(sections(new))
        sc = dict(sections(cod)) if cod else {}
        wo = wn = wc = 0
        over, rows = [], []
        for t, b in so:
            if not t or FROZEN.search(t):
                if t and sn.get(t) != b:
                    print('  ！冻住的节变了：', t[:40])
                    ok = False
                continue
            a, n, c = han(b), han(sn.get(t, '')), han(sc.get(t, '')) if cod else 0
            wo += a
            wn += n
            wc += c
            if cod and n - c > a * 0.10 + 5:
                over.append('%s（原 %d，Codex %d，审后 %d）' % (t[:24], a, c, n))
            rows.append((n / max(1, a), a, n, t))
        print('%s｜全文 %d → %d（留 %d%%）｜可洗 %d → Codex %s → 审后 %d（留 %d%%）' % (base, han(old), han(new), 100 * han(new) / max(1, han(old)), wo, wc if cod else '?', wn, 100 * wn / max(1, wo)))
        if over:
            print('  ！补回过了上限的节：', '；'.join(over[:8]))
        rows.sort()
        print('  留得最少：', '；'.join('%s %d%%' % (t[:14], 100 * r) for r, a, n, t in rows[:3]), '｜留得最多：', '；'.join('%s %d%%' % (t[:14], 100 * r) for r, a, n, t in rows[-3:] if a > 400))
        so_st = {(n, k): h for n, k, h in stars(old)}
        lost = [(n, k, h) for n, k, h in stars(new) if not BORN.search(h) and BORN.search(so_st.get((n, k), ''))]
        if lost:
            print('  ！头一句丢了“生来”一类字的星 %d 颗：' % len(lost))
            for n, k, h in lost:
                print('     %s（%s）：%s ｜原：%s' % (n, k, h[:44], so_st[(n, k)][:44]))
        if apply:
            p = os.path.join(ROOT, f)
            raw = open(p, encoding='utf-8', newline='').read()
            cur = raw.replace('\r\n', '\n')
            if cur != old and cur != new:
                print('  ！仓库里的 %s 在派活以后又改过，先别拷，手工并' % f)
                ok = False
                continue
            if cur != new:
                open(p, 'w', encoding='utf-8', newline='').write(new.replace('\n', '\r\n') if '\r\n' in raw else new)
            tmp = os.path.join(os.environ.get('TEMP', '.'), '详本_' + base)
            src = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (TAG, f)], capture_output=True).stdout
            open(tmp, 'wb').write(src)
            r = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'tools', 'check_protected.py'), tmp, p], capture_output=True)
            print('  受保护的行：', r.stdout.decode('utf-8', 'replace').strip().split('\n')[0][:120])
            r = subprocess.run(['bash', 'tools/recv_check.sh', f], cwd=ROOT, capture_output=True)
            for l in r.stdout.decode('utf-8', 'replace').strip().split('\n')[-3:]:
                print('  ' + l.strip()[:230])
    if engine == 'codex' and os.path.isdir(os.path.join(d, '稿_Codex原样')):
        # 审稿人删掉的句子里，原稿别的节其实有的（洗稿把默认收束里的下场挪进了各人的条目，审稿人当成添的删了）。只印出来，主会话自己看
        r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, '查误删.py'), name, '--min', '0.25'], capture_output=True)
        ls = [l for l in r.stdout.decode('utf-8', 'replace').split('\n') if l.strip()]
        if any(l.startswith('  [') for l in ls):
            print('  查误删（审稿以后没了、原稿别处有的句子，逐句看要不要补回）：')
            for l in ls:
                if not l.startswith('=='):
                    print('  ' + l[:210])
    # Legend、Unique 的 Art 星头一段里做到头的那一件事洗薄了没有（留下不到六成的印出来，主会话对着原稿补回）
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, '查星头.py'), name], capture_output=True)
    ls = [l for l in r.stdout.decode('utf-8', 'replace').split('\n') if l.strip() and not l.startswith('列出 0')]
    if ls:
        print('  查星头（Legend、Unique 的 Art 头一段留下不到六成的，看那一拍要不要补回）：')
        for l in ls:
            print('  ' + l[:260])
    return ok


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    engine = sys.argv[sys.argv.index('--engine') + 1] if '--engine' in sys.argv else 'codex'
    if engine in args:
        args.remove(engine)
    res = [one(n, engine, '--apply' in sys.argv) for n in args]
    print('都过了' if all(res) else '有没过的，看上面带 ！ 和“错”的行')
