"""洗稿层深改收稿查（11-09，全卡去八股往深里改那一轮）。

拿 git HEAD 那一版洗稿文件当改前，工作区这一版当改后，一条一条比：
  1. 改了多少：改动的字（逐字比，替换、删、添的字数）占改前这一条的几成，整份合计。
  2. 强弱字：必须、不得、禁止、不许、严禁、绝不、绝对、永远、永不、一律、只给 AI、硬设定、勿说破、不可、只能、一定
     这些字改前改后各数一遍，少了的列出来（合并成一句也会少，列出来是叫人看一眼，不算错）。
  3. 小标题：条目正文里 ## 、### 起头的行，改前改后要一样（别的条目按节号、小标题引），变了列出来。
  4. 一份里跨条目重复的句头（去掉行首标签以后的头四个字，出现在四条以上的），列出来，深改时换开用。

用法（仓库根上）：python -I -X utf8 tools/wash_deep_check.py 底卡洗稿/批次_XX.md [...] [--base HEAD] [--frames] [--quiet]
  --base 改前取哪一版（git 的修订号，默认 HEAD）。
  --frames 加查第4样（改前、改后各报一遍）。
  --quiet 每条只在有事的时候打印。
"""
import collections, difflib, os, re, runpy, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = runpy.run_path(os.path.join(HERE, 'wash_check.py'), run_name='lib')
LOCKS = ['必须', '不得', '禁止', '不许', '严禁', '绝不', '绝对', '永远', '永不', '一律', '只给 AI', '只给AI', '硬设定',
         '勿说破', '不可', '只能', '一定']


def parse_text(text):
    import tempfile
    fd, p = tempfile.mkstemp(suffix='.md')
    os.close(fd)
    open(p, 'w', encoding='utf-8').write(text)
    try:
        return W['parse_wash'](p)
    finally:
        os.remove(p)


def changed(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    n = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != 'equal':
            n += max(i2 - i1, j2 - j1)
    return n


def heads_of(body):
    out = []
    for line in body.split('\n')[1:]:
        for s in re.split(r'[。？！]', line):
            s = re.sub(r'^[\s\-#>*·]*【[^】]{1,12}】', '', s)
            s = re.sub(r'^[\s\-#>*·（(【「“"0-9.、]+', '', s).strip()
            s = re.sub(r'^[^：｜]{1,10}[：｜]', '', s).strip()
            if len(re.findall(r'[一-鿿]', s)) >= 6:
                out.append(s)
    return out


def frames(ents, label):
    h = collections.defaultdict(set)
    ex = {}
    for e in ents:
        for s in heads_of(e['body'] or ''):
            k = s[:4]
            h[k].add(e['idx'])
            ex.setdefault(k, s[:36])
    rows = sorted(((len(v), k) for k, v in h.items() if len(v) >= 4), reverse=True)
    print('  [%s] 跨条目重复的句头（四条以上）%d 个' % (label, len(rows)))
    for n, k in rows[:25]:
        print('    %3d条  %s  例：%s' % (n, k, ex[k]))


def main():
    args = sys.argv[1:]
    base = 'HEAD'
    if '--base' in args:
        base = args[args.index('--base') + 1]
    want_frames = '--frames' in args
    quiet = '--quiet' in args
    files = [a for i, a in enumerate(args) if not a.startswith('--') and (i == 0 or args[i - 1] != '--base')]
    gt = gc = 0
    for f in files:
        rel = f.replace('\\', '/')
        old_text = subprocess.run(['git', 'show', '%s:%s' % (base, rel)], capture_output=True).stdout.decode('utf-8')
        new_ents = W['parse_wash'](f)
        old_ents = {e['idx']: e for e in parse_text(old_text)}
        print('== %s（%d 条，改前取 %s）' % (rel, len(new_ents), base))
        ft = fc = 0
        for e in new_ents:
            o = old_ents.get(e['idx'])
            if not o:
                print('  #%d 改前没有这一条' % e['idx'])
                continue
            a, b = o['body'] or '', e['body'] or ''
            ca = len(a)
            c = changed(a, b)
            ft += ca
            fc += c
            notes = []
            for w in LOCKS:
                x, y = a.count(w), b.count(w)
                if y < x:
                    notes.append('%s %d→%d' % (w, x, y))
            ha = [l for l in a.split('\n') if re.match(r'#{2,4} ', l)]
            hb = [l for l in b.split('\n') if re.match(r'#{2,4} ', l)]
            if ha != hb:
                gone = [l for l in ha if l not in hb]
                new = [l for l in hb if l not in ha]
                notes.append('小标题变了：少 %s｜多 %s' % ('、'.join(gone) or '无', '、'.join(new) or '无'))
            pct = 100.0 * c / max(ca, 1)
            if not quiet or notes:
                print('  #%-5d %5.1f%%  %s%s' % (e['idx'], pct, e['title'][:24], ('  ⚑ ' + '；'.join(notes)) if notes else ''))
        print('  合计 改动 %.1f%%（%d / %d 字符）' % (100.0 * fc / max(ft, 1), fc, ft))
        gt += ft
        gc += fc
        if want_frames:
            frames(list(old_ents.values()), '改前')
            frames(new_ents, '改后')
    if len(files) > 1:
        print('全部合计 改动 %.1f%%' % (100.0 * gc / max(gt, 1)))


if __name__ == '__main__':
    main()
