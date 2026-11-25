# 风月四张外壳的样式（11-25）。日里那一份 frame.css（make_css_frame.py 出的，这里不改它）转成风月的页面结构，一张卡一份，推上图床，
# 卡的样式格只留一行 @import。转法接着 11-04 的 make_fy_css.py（外壳那一层 shell()、认钟点 hours()、各个选择器都从它那里取）：
#   - 那一份只收到「玩家说的话」以前的模块样式，后头接的字眼、超凡演出、战斗特效、队友浮栏、检定演出、命星页、家业页、背包格子没带上；
#     这里把 frame.css 末尾那一大段（字眼起到背包格子）照同一套选择器换过来，再接四纪的立绘、神、史诗战的图（four_era_art.css）。
#   - 一张卡一纪：别纪的变量、别纪的立绘和 Boss 图、只认别纪记号的样式不带（照规则一条一条筛，不照行筛）。
#     这一纪的 --fm- 变量直接写在外壳和输入栏上（风月的回复里不能带 <style>）。
#   - 迷宫纪那一张有前传和 1001 年两种材质：默认 1001 年；最新一对问答里的空记号（.sz-era.era-pre，显示正则认年份落的）是前传就换前传，
#     最新一对没有状态栏（功能轮）的看列表里的。跟认钟点一个路子。平台的主题变量（钮、分页、弹层读的）跟着换。
#   - 行内 style 的自定义属性换大写（名单 fy_shell_rules.inline_vars 现数的），样式里读它们的地方跟着换。
#   - 主角立绘：回复里挂 data-pc（预设）的照预设表给图，挂 data-pcu 的读行内的大写变量。
#   - 样式是 @import 载进来的，平台不会替它加 #installedBuiltInCss 前缀，这里照平台的规矩先加好（照复刻台 static_bench_fy.mjs 那一段抄的）。
import colorsys
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BIG = os.path.join(ROOT, '底稿', '状态栏', '大框')
if BIG not in sys.path:
    sys.path.insert(0, BIG)
sys.dont_write_bytecode = True
import era_vars                 # noqa: E402
import make_fy_css as MF        # noqa: E402
import old_css_trim as OT       # noqa: E402

REPO = 'waitlist886-cloud/aldran-img'
BRANCH = 'fy_css'
MAN = os.path.join(HERE, 'fy_css_manifest.json')
PFX = '#installedBuiltInCss'
ERAS = ('moon', 'strife', 'bronze', 'pre', 'maze')
R_FY = '.markdown-body:has(.sz-hud)'
FY_BASE = os.path.join(ROOT, 'src', 'fengyue_底卡_20261104.json')    # 线上那张卡原来带的旧样式从这里取（跟 make_fy_card.py 一个底）


def read(*p):
    return open(os.path.join(*p), encoding='utf-8', newline='').read().replace('\r\n', '\n')


def once(s, a, b, what=''):
    assert s.count(a) == 1, ('对不上', what, s.count(a), a[:70])
    return s.replace(a, b)


# ---------------- 一条一条的样式 ----------------
def rules_of(css):
    """顶层切成一条一条，@media 这一类往里再切。返回 [(头, 体或子表)]：普通规则是 (选择器, '{…}')，套着的是 (@media …, [子规则])，别的 @ 是 (整条, None)"""
    out = []
    for blk in OT.split_top(css):
        if blk.startswith('@'):
            if re.match(r'@(media|supports|layer|container)\b', blk) and '{' in blk:
                head, body = blk.split('{', 1)
                out.append((head, rules_of(body[:body.rindex('}')])))
            else:
                out.append((blk, None))
        elif '{' in blk:
            sel, body = blk.split('{', 1)
            out.append((sel, '{' + body))
    return out


def dump(rules):
    out = []
    for head, body in rules:
        if body is None:
            out.append(head)
        elif isinstance(body, list):
            inner = dump(body)
            if inner:
                out.append(head + '{' + inner + '}')
        else:
            out.append(head + body)
    return '\n'.join(out)


def walk(rules, fn):
    """fn(选择器, 体) 返回新的 (选择器, 体) 或者 None（这一条不要）"""
    out = []
    for head, body in rules:
        if body is None:
            out.append((head, body))
        elif isinstance(body, list):
            inner = walk(body, fn)
            if inner:
                out.append((head, inner))
        else:
            r = fn(head, body)
            if r:
                out.append(r)
    return out


_ERA_CLS = re.compile(r'\.era-(' + '|'.join(ERAS) + r')(?![\w-])')
_ERA_VAR = re.compile(r'--(' + '|'.join(ERAS) + r')-[\w-]+\s*:')


def era_filter(rules, eras):
    """别纪的不带：选择器只认别纪记号的；整条只定义别纪变量的。返回 (留下的, 拿掉几条)"""
    n = [0]

    def fn(sel, body):
        sels = OT.split_sel(sel)
        keep = []
        for s in sels:
            found = set(_ERA_CLS.findall(s))
            if not found or (found & set(eras)):
                keep.append(s)
        if not keep:
            n[0] += 1
            return None
        vs = set(_ERA_VAR.findall(body))
        if vs and not (vs & set(eras)) and re.match(r'^\{\s*--(?:' + '|'.join(ERAS) + r')-', body):
            n[0] += 1
            return None
        return (','.join(keep), body)
    return walk(rules, fn), n[0]


def prefix_one(e):
    e = e.strip()
    if e in ('body', 'html'):
        return PFX + ' ' + e
    if e == '.dark' or e.startswith('.dark ') or e.startswith('.dark:'):
        return PFX + e
    if e == 'html.dark' or e.startswith('html.dark '):
        r = e[9:].strip()
        return ('html.dark ' + PFX + ' ' + r) if r else ('html.dark ' + PFX)
    return PFX + ' ' + e


def prefixed(rules):
    return walk(rules, lambda sel, body: (','.join(prefix_one(s) for s in OT.split_sel(sel)), body))


# ---------------- 这一纪的颜色：平台的主题变量（钮、分页、弹层读的） ----------------
def _hsl(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s * 100, l * 100


def era_colors(frame):
    """frame.css 头上那几行里各纪的 band、edge、acc"""
    out = {}
    for k in ERAS:
        m = re.search(r'--%s-band:(#[0-9a-fA-F]{6});' % k, frame), re.search(r'--%s-edge:(#[0-9a-fA-F]{6});' % k, frame), re.search(r'--%s-acc:(#[0-9a-fA-F]{6});' % k, frame)
        assert all(m), k
        out[k] = tuple(x.group(1) for x in m)
    return out


def theme(k, colors):
    """照这一纪的 band、edge、acc 推平台的主题变量。迷宫纪那一份是 11-04 调好的，照旧；别的纪照同一套比例推（拿迷宫纪的颜色推出来跟它那一份差不到两个点）"""
    if k == 'maze':
        return MF.THEME
    band, edge, acc = colors[k]
    h, s, l = _hsl(band)
    bg = '%d %d%% %d%%' % (round(h), round(s), round(l))
    sec = '%d %d%% %d%%' % (round(h), round(s * .76), round(l + 7))
    eh, es, el = _hsl(edge)
    bd = '%d %d%% %d%%' % (round(eh), round(es * .88), round(el * .72))
    ah, a_s, al = _hsl(acc)
    fg = '42 44% 88%'
    return ('--background:{bg};--foreground:{fg};--card:{bg};--card-foreground:{fg};--popover:{bg};--popover-foreground:{fg};'
            '--secondary:{sec};--secondary-foreground:{fg};--muted:{sec};--muted-foreground:42 30% 76%;--accent:{sec};--accent-foreground:{fg};'
            '--text-main:{fg};--text-secondary:42 18% 68%;--text-tertiary:{fg};--input-placeholder:42 20% 66%;--border:{bd};--input:{bd};'
            '--primary-secondary:{ac} / .16').format(bg=bg, fg=fg, sec=sec, bd=bd, ac='%d %d%% %d%%' % (round(ah), round(a_s), round(al)))


def fm_vars(k):
    return ';'.join('--fm-%s:var(--%s-%s)' % (n, k, n) for n in era_vars.NAMES)


# ---------------- 主角立绘：预设表（回复里挂 data-pc="族属-性别-体格"），自己贴的图读行内的变量 ----------------
def pc_css():
    import pc_portrait as PC
    out = []
    for nm, u in sorted(PC.presets().items()):
        k = nm.replace('·', '-')
        art = ';--art:url("%s")' % u['art'] if u['art'] else ''
        out.append('%s :is(.sz-say,.jg-w.jg-pc)[data-pc="%s"]{--face:url("%s")%s;--por:url("%s");--init:none}' % (R_FY, k, u['face'], art, u['por']))
        out.append('%s .sz-doll-fig[data-pc="%s"]{--pcd:url("%s");--pcsz:auto 100%%;--pcon:1%s;--por:url("%s");--pczd:block}' % (R_FY, k, u['por'], art, u['por']))
    out.append('%s :is(.sz-say,.jg-w.jg-pc)[data-pcu]{--face:var(--ufc);--fsz:cover;--fx:1!important;--fy:0!important;--init:none;--art:var(--uar);--por:none}' % R_FY)
    out.append('%s .sz-doll-fig[data-pcu]{--pcd:var(--udl);--pcsz:contain;--pcon:0;--art:var(--udl);--por:none;--pczd:block}' % R_FY)
    return '\n'.join(out), len(out) // 2 - 1


# ---------------- 外壳那一层：make_fy_css.shell() 是照迷宫纪一纪写的，四纪要用的另外几层在这里补 ----------------
def shell_four():
    """日里那一份宽屏最上头一层有十样（make_css_frame.py 的 TOPLAYERS）：四个框角、滚动那一颗、枪、楣、一双手、座。
    11-04 的风月外壳只画了那一颗、楣、座（迷宫纪用不着别的）。这里补上：
      月银纪的一双手（贴屏幕两个下角）和右上角那一截枪，没画四方的纪（前传）的四个框角；位置照日里那一份，顶栏的高换成风月的 --fm-hdr。
      上头两个框角、枪、手跟楣一起画在外壳的 ::before 上；下头两个框角跟座一起画在输入栏那一层（框的下沿跟着输入栏走）。
      纷争纪军册左边那一道红线，窄屏上推到窗外（日里那一份里有，风月那一份没带）。"""
    s = MF.shell()
    x1, x2 = 'calc(50% - var(--fm-win) / 2 + 29px)', 'calc(50% + var(--fm-win) / 2 - 29px)'
    yt = 'calc(var(--fm-hdr) + var(--fm-ftop) + 2px)'
    pos = ['left %s top %s' % (x1, yt), 'left %s top %s' % (x2, yt), None, 'left calc(50% + var(--fm-win) / 2) top 6dvh', 'center top',
           'left var(--fm-hx, 0px) bottom -8dvh', 'right var(--fm-hx, 0px) bottom -8dvh']
    img = ['var(--fm-c1, none)', 'var(--fm-c2, none)', 'var(--fm-gem)', 'var(--fm-lance, none)', 'var(--fm-top)', 'var(--fm-hl, none)', 'var(--fm-hr, none)']
    size = ['54px', '54px', '16px 16px', 'auto 25dvh', 'auto var(--fm-toph)', 'auto 37.6dvh', 'auto 37.6dvh']
    lay = ', '.join('%s %s/%s no-repeat' % (i, p or '@GEMTO@', z) for i, p, z in zip(img, pos, size))
    s = once(s, 'background:var(--fm-gem) @GEMTO@/16px 16px no-repeat, var(--fm-top) center top/auto var(--fm-toph) no-repeat;', 'background:' + lay + ';', '楣那一层')
    s = once(s, '@keyframes fm-gem{from{background-position:@GEMFROM@, center top}to{background-position:@GEMTO@, center top}}',
             '@keyframes fm-gem{from{background-position:%s}to{background-position:%s}}' % (', '.join(p or '@GEMFROM@' for p in pos), ', '.join(p or '@GEMTO@' for p in pos)), '那一颗的动画')
    # 座那一层：输入栏那一格的顶在这一层里离上沿 BOTH - KB，下头两个框角的下沿贴着它往上两像素
    yb = MF.BOTH - MF.KB - 2 - 54
    s = once(s, 'background:var(--fm-bot) center bottom/2500px 100% no-repeat;',
             'background:var(--fm-c3, none) left %s top %dpx/54px no-repeat, var(--fm-c4, none) left %s top %dpx/54px no-repeat, var(--fm-bot) center bottom/2500px 100%% no-repeat;' % (x1, yb, x2, yb), '座那一层')
    s += '\n@media (max-width:1099px){@ONF@{--fm-rl:-8px}}\n'
    return s


# ---------------- 一张卡的样式（还没加前缀） ----------------
def build(card_key, eras, names, ref_rules):
    """card_key：maze／moon／strife／bronze；eras：这一张里的纪（头一个是默认的）；names：行内 style 里要换大写的变量；
    ref_rules：这一张卡的规则（日里写法，清旧样式时认活着的类名）。返回 (样式, 账)"""
    import four_era_art as FA
    import mod_page as MP
    import fy_shell_rules as FR
    acct = {}
    frame = read(BIG, 'frame.css')
    banner = re.search(r'header>div:nth-child\(2\)::before\{[^}]*background:(url\("[^"]*"\))', frame).group(1)
    colors = era_colors(frame)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        full = FA.css(frame)
    acct['图'] = buf.getvalue().strip().split('\n')[0]
    a = full.index('/* ---------- 整页：外壳的底')
    m0 = full.index('.rili-markdown-renderer:has(.sz-hud){background:none!important', a)
    b = full.index('/* 玩家说的话：一道细线')
    lab = full.index('/* ---------- 字眼：一纪一套')
    art = full.index('/* ==== 四纪的立绘、神、史诗战的图（four_era_art.py） ==== */')
    assert a < m0 < b < lab < art
    head = '\n'.join(ln.replace(MF.SH_OLD + '{', MF.SHF + '{') for ln in full[:a].split('\n'))
    k0 = eras[0]
    parts = [head, '%s{%s}' % (MF.SHF, fm_vars(k0)), shell_four(), full[m0:b], full[lab:art], full[art:]]
    out = '\n'.join(parts)
    gx = 'calc(50% + var(--fm-win) / 2)'
    for k, v in [('@THEME@', theme(k0, colors)), ('@IDLE@', MF.IDLE), ('@ONF@', MF.ONF), ('@ON@', MF.ON), ('@SC@', MF.SC), ('@CO@', MF.CO), ('@FT@', MF.FT), ('@FI@', MF.FI),
                 ('@HD@', MF.HD), ('@AN@', MF.AN), ('@KB@', str(MF.KB)), ('@BOTH@', str(MF.BOTH)),
                 ('@GEMFROM@', 'left %s top calc(var(--fm-hdr) + var(--fm-ftop) + 70px)' % gx), ('@GEMTO@', 'left %s bottom calc(var(--fm-dock) + 64px)' % gx),
                 ('@BANNER@', banner), ('@R@', '.rili-markdown-renderer:has(.sz-hud)'), ('@L@', MF.L_NEW)]:
        out = out.replace(k, v)
    out = out.replace(MF.L_NEW, MF.L_ALL).replace(MF.R_OLD, MF.L).replace(MF.O_OLD, MF.O)
    out = out.replace('.rili-markdown-renderer', MF.MD)
    out = out.replace(MF.SH_OLD, MF.SH)
    out = out.replace('.is-assistant', MF.AN)
    out = once(out, 'bottom:calc(var(--fm-dock) + 6px)', 'bottom:var(--fm-stk)', '页签的 sticky')
    out += '\n' + MF.hours('[data-item-index]', '.chat-container > .pt-24 > #customized-answer') + '\n'
    # 迷宫纪那一张：前传的回复换前传的材质和主题
    if len(eras) > 1:
        assert eras == ['maze', 'pre'], eras
        last = '.chat-container > .pt-24 > #customized-answer .sz-era.era-%s'
        sw = []
        for k, sel in (('pre', '%s:has([data-item-index] .sz-era.era-pre):not(:has(.sz-era.era-maze))' % MF.SH), ('pre', '%s:has(%s)' % (MF.SH, last % 'pre')), ('maze', '%s:has(%s)' % (MF.SH, last % 'maze'))):
            sw.append('%s,%s ~ %s{%s;%s}' % (sel, sel, MF.FOOT, fm_vars(k), theme(k, colors)))
        out += '\n'.join(sw) + '\n'
    out += MP.css(MP.L_FY, MP.R_FY) + '\n'
    assert MP.L_FY + ':has(.t-news input:checked) .p-news{display:block}' in out, '扩展页的样式前缀跟这一张对不上'
    pc, n_pc = pc_css()
    out += pc + '\n'
    acct['主角预设'] = n_pc
    # 行内 style 的自定义属性：大写
    rx = FR.upvar_re(names)
    out = FR.upvar(out, rx)
    # 平台把行内 style 重写过一遍，属性名和值之间多一个空格，照属性值认的那一处两种都认
    out = once(out, '[style*="--V:0;"]', ':is([style*="--V:0;"],[style*="--V: 0;"])', '血条见底')
    assert not re.search(r'\[style[*^$~|]?="--', out.replace(':is([style*="--V:0;"],[style*="--V: 0;"])', '')), '还有别的照行内变量的值认的选择器'
    out = re.sub(r'/\*[\s\S]*?\*/', '', out)
    for fn, u in FA.URL.items():
        if '__ART__/' + fn in out:
            out = out.replace('__ART__/' + fn, u)
    assert '__ART__' not in out, re.findall(r'__ART__/[^"]*', out)[:5]
    for bad in [':root', '#conversation', '.is-user', 'rili-markdown', 'contain: layout', 'contain: size', 'header>', 'custom-styles']:
        t = re.sub(r'url\("data:[^"]*"\)', 'url()', out)
        hit = [m.start() for m in re.finditer(re.escape(bad), t)]
        assert not hit, (bad, len(hit), t[max(0, hit[0] - 80):hit[0] + 80])
    assert not re.search(r'@[A-Z]{1,8}@', re.sub(r'url\("data:[^"]*"\)', 'url()', out)), '还有没换掉的占位'
    rules = rules_of(out)
    rules, n_drop = era_filter(rules, eras)
    acct['别纪拿掉'] = n_drop
    new_css = dump(rules)
    # 线上那张卡原来带的旧样式：迷宫纪那一张照旧整段留着（老档里转不干净的旧回复还要它），另外三张是新卡，只留用得上的
    old = json.load(open(FY_BASE, encoding='utf-8'))['built_in_css']
    n = old.count('details:not([open])>summary')
    old = old.replace('details:not([open])>summary', 'details:not([open],.sz-hud)>summary')
    old = once(old, 'details>summary::after{content:"▾"', 'details:not(.sz-hud)>summary::after{content:"▾"', '旧样式')
    acct['旧样式'] = len(old)
    if card_key != 'maze':
        old, n_old, c_old = OT.for_card(old, ref_rules, new_css)
        acct['旧样式'] = len(old)
        acct['旧样式删'] = n_old
    css = dump(rules_of(old)) + '\n' + new_css + '\n'
    hit = MF_BAN.search(re.sub(r'url\("data:[^"]*"\)', 'url()', css))
    assert not hit, ('样式里有平台的屏蔽词', css[max(0, hit.start() - 40):hit.end() + 40])
    acct['字'] = len(css)
    return css, acct


MF_BAN = re.compile('rili|fengyue', re.I)


def scoped(css):
    """照平台的规矩给每条选择器加 #installedBuiltInCss（@import 载进来的样式平台不管，先加好）"""
    out = dump(prefixed(rules_of(css)))
    assert out.count('{') == css.count('{'), (out.count('{'), css.count('{'))
    return '@charset "UTF-8";\n' + out + '\n'


# ---------------- 推图床：fy_css 分支，照内容起名，不强推，旧文件留着 ----------------
def git(cwd, *a, check=True):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if check and r.returncode:
        raise RuntimeError('git %s 失败：%s' % (' '.join(a[:2]), (r.stderr or r.stdout).strip()[-400:]))
    return r


def push(files):
    """files：{文件名: 字节}。返回提交号"""
    tmp = tempfile.mkdtemp(prefix='ghfy_')
    try:
        url = 'https://github.com/%s.git' % REPO
        wd = os.path.join(tmp, 'r')
        if git(tmp, 'ls-remote', '--heads', url, BRANCH).stdout.strip():
            git(tmp, 'clone', '-q', '--depth', '1', '--branch', BRANCH, url, 'r')
        else:
            os.makedirs(wd)
            git(wd, 'init', '-q')
            git(wd, 'checkout', '-q', '-b', BRANCH)
            with open(os.path.join(wd, '.gitattributes'), 'w', newline='\n') as fh:
                fh.write('* -text\n')
        for fn, data in files.items():
            with open(os.path.join(wd, fn), 'wb') as fh:
                fh.write(data)
        git(wd, 'add', '-A')
        if not git(wd, 'status', '--porcelain').stdout.strip():
            return git(wd, 'rev-parse', 'HEAD').stdout.strip()
        git(wd, '-c', 'user.name=Claude', '-c', 'user.email=noreply@anthropic.com', 'commit', '-q', '-m', 'fy_css：%s' % '、'.join(sorted(files)))
        commit = git(wd, 'rev-parse', 'HEAD').stdout.strip()
        git(wd, 'push', '-q', url, 'HEAD:refs/heads/%s' % BRANCH)
        return commit
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def fetch_check(url, size):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=90) as r:
                body = r.read()
            if len(body) == size:
                return True
            print('  大小对不上', len(body), size)
        except Exception as ex:
            print('  第', i + 1, '回没取到：', ex)
    return False


def publish(card_key, css_scoped, do_push=True):
    """返回 (地址, 账)。同一份内容推过了就照清单用原来那个地址"""
    data = css_scoped.encode('utf-8')
    fname = 'fy_%s_%s.css' % (card_key, hashlib.sha256(data).hexdigest()[:12])
    man = json.load(open(MAN, encoding='utf-8')) if os.path.exists(MAN) else {}
    if fname in man:
        commit, how = man[fname]['commit'], '推过了'
    elif not do_push:
        commit, how = 'NOPUSH', '没推'
    else:
        commit = push({fname: data})
        man[fname] = {'commit': commit, 'bytes': len(data), 'card': card_key}
        json.dump(man, open(MAN, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
        how = '新推'
    url = 'https://cdn.jsdelivr.net/gh/%s@%s/%s' % (REPO, commit, fname)
    ok = None
    if commit != 'NOPUSH':
        ok = fetch_check(url, len(data))
        if not ok:
            raise SystemExit('图床上的样式取不到或者大小不对：' + url)
    return url, {'文件': fname, '字节': len(data), '提交': commit, '怎么来的': how, '取回核过': ok}
