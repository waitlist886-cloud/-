"""新料 290 条的触发分支，拿实测回复（状态栏加正文）试：哪些分支在一条寻常回复里就中了。
用法：python -I -X utf8 ambient_trig.py <仓库根> [--apply]
--apply：把中了的分支从那一条的触发里拿掉（年份正则、〔纪·正则〕不动；拿完一条分支不剩的不动、报出来）。"""
import glob, io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = sys.argv[1]
APPLY = '--apply' in sys.argv
BS = chr(92)
D = os.path.join(ROOT, '底稿', 'DLC', '新料')
FILES = [os.path.join(D, '样稿三条.md'), os.path.join(D, '第一拨.md')]
for sub, pat in (('律法志', 'L*.md'), ('风物志', 'F*.md'), ('谱系志', 'G*.md'), ('谱系志', 'C*.md')):
    FILES += sorted(glob.glob(os.path.join(D, sub, pat)))
SAMPLES = sorted(glob.glob(os.path.join(ROOT, 'moon', 'samples', 'reply*.html')))
texts = [(os.path.basename(p), open(p, encoding='utf-8').read()) for p in SAMPLES]
# 状态栏里回回都带的词（四纪大框的记录行）
texts.append(('状态栏常见词', '日报渠道 委托 公会 钱袋 背包 装备 地图 同行 位阶 命星 技艺 关系 好感 任务 主线 支线 潮汐 档位 防抢话 天气 时辰'))


def split_top(rx):
    out, depth, cur, esc, cls = [], 0, '', False, False
    for ch in rx:
        if esc:
            cur += ch; esc = False; continue
        if ch == BS:
            cur += ch; esc = True; continue
        if cls:
            cur += ch
            if ch == ']':
                cls = False
            continue
        if ch == '[':
            cls = True; cur += ch; continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == '|' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    return out


tot = 0
drop_n = 0
for f in FILES:
    L = open(f, encoding='utf-8').read().split('\n')
    title = ''
    changed = False
    for i, ln in enumerate(L):
        if ln.startswith('## '):
            title = ln[3:].strip()
        if not ln.startswith('> 条目设置：'):
            continue
        head, sep, tail = ln.partition('黑名单')

        def fix(m):
            global tot, drop_n
            rx = m.group(1)
            if rx.startswith('(?:<br>') or '纪元：' in rx:
                return m.group(0)
            toks = split_top(rx)
            keep = []
            for t in toks:
                hit = None
                try:
                    c = re.compile(t)
                except re.error:
                    keep.append(t); continue
                for name, tx in texts:
                    mm = c.search(tx)
                    if mm:
                        hit = (name, tx[max(0, mm.start() - 10):mm.end() + 10].replace('\n', ' '))
                        break
                if hit and t in ('仓签当钱',):          # 正对题的词，留着
                    hit = None
                if hit:
                    tot += 1
                    print('%s｜%s｜分支 %s｜%s｜%s' % (os.path.basename(f), title, t, hit[0], hit[1]))
                else:
                    keep.append(t)
            if not APPLY or len(keep) == len(toks):
                return m.group(0)
            if not keep:
                print('   !! 拿完就空了，没动：', title)
                return m.group(0)
            drop_n += len(toks) - len(keep)
            new = '|'.join(keep)
            re.compile(new)
            return '`/' + new + '/`'

        nh = re.sub(r'`/(.+?)/`', fix, head)
        if nh != head:
            L[i] = nh + sep + tail
            changed = True
    if changed and APPLY:
        open(f, 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
print('在寻常回复里就中的分支', tot, '个；拿掉', drop_n, '个')
