# 一次性补丁（11-22）：给 底稿/门面/共用/build_atlas.py 添神域栏。跑过一回就不用再跑，留档。
# 用法：python -I -X utf8 底稿/神域/tools/patch_atlas_dom.py
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
P = os.path.join(ROOT, '底稿', '门面', '共用', 'build_atlas.py')
s = open(P, encoding='utf-8').read()
assert 'make_dom' not in s, '已经打过了'


def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)


rep("""                if '倒下' not in d:            # 没写倒下的那几位""",
    """                dz = {mm.group(1): mm.group(2).strip() for mm in re.finditer(r'(?m)^- (神力|神性|神域专长|神国|国律|对上祂|陨落以后|倒下以后|剥离以后)：(.+)$', body)}
                qb = re.findall(r'(?m)^- 权柄[一二三]?｜([^：]+)：(.+)$', body)
                if dz or qb:
                    d['dom'] = (dz, qb)
                if '倒下' not in d:            # 没写倒下的那几位""")

rep("""        g['fellText'] = clean(dx, 120) if g['fell'] else ''
    return gods
""",
    """        g['fellText'] = clean(dx, 120) if g['fell'] else ''
        g['dom'] = {'moon': make_dom(a.get('dom'), doms), 'strife': make_dom(b.get('dom'), doms), 'now': make_dom(today.get(g['n']), doms)}
    return gods
""")

rep("""    moon = scan(sorted(glob(os.path.join(R, '月银纪补卷', '神谱_0*.md'))), '月银纪')""",
    """    doms = load_domains()
    today = load_today(gods)
    moon = scan(sorted(glob(os.path.join(R, '月银纪补卷', '神谱_0*.md'))), '月银纪')""")

rep("""# ---------------- 神 ----------------
def load_gods():""",
    r'''# ---------------- 神 ----------------
# 神域栏（11-22 神域玩法）：两纪神谱各条「- 锁：」前头那一块，和 底卡新条目/神域_今天的八位.md。
# 图鉴上神性、本域、三迹、权柄的名字和做得到什么、神域专长、神国是明着的；神力的数、带年份和死法的句子、对上祂、陨落以后归剧透开关。
SPOIL_SENT = re.compile(r'\d{3,5}年|倒下|陨落|同陨|死在|杀了|按倒|塌')


def noai(t):
    """拿掉只给主持的 AI 的句子"""
    if not t:
        return ''
    xs = [x.strip() for x in clean(t).split('。') if x.strip() and '只给 AI' not in x and '不裁定' not in x]
    return ('。'.join(xs) + '。') if xs else ''


def two(t):
    """一段话分成明着的和归剧透的两截"""
    a, b = [], []
    for x in noai(t).split('。'):
        if x.strip():
            (b if SPOIL_SENT.search(x) else a).append(x.strip())
    return ('。'.join(a) + '。' if a else ''), ('。'.join(b) + '。' if b else '')


def _blocks(path, head):
    s = open(path, encoding='utf-8').read().replace('\r', '')
    for m in re.finditer(head, s):
        e = s.find('\n## ', m.end())
        yield m.group(1).strip(), s[m.end():e if e > 0 else len(s)]


def load_domains():
    f = os.path.join(R, '通用条目', '神域_七十二域.md')
    out = {}
    if not os.path.exists(f):
        return out
    for name, body in _blocks(f, r'(?m)^## 奥尔德兰·神域｜(.+)$'):
        d = {}
        for lab in ('正位', '逆位', '三迹'):
            mm = re.search(r'(?m)^- %s：(.+)$' % lab, body)
            if mm:
                xs = [x.strip() for x in mm.group(1).split('。') if x.strip() and not re.match(r'^在.+手里', x.strip())
                      and '只给 AI' not in x and '只有这一域' not in x]
                d[lab] = clean('。'.join(xs) + '。')
        out[name] = d
    return out


def load_today(gods):
    f = os.path.join(R, '底卡新条目', '神域_今天的八位.md')
    out = {}
    if not os.path.exists(f):
        return out
    for name, body in _blocks(f, r'(?m)^## 迷宫纪·神域｜(.+?)的神域栏$'):
        g = next((x for x in gods if name.endswith(x['n'])), None)
        if not g:
            continue
        dz = {mm.group(1): mm.group(2).strip() for mm in re.finditer(r'(?m)^- (神力|神性|神域专长|神国|对上祂|今天)：(.+)$', body)}
        out[g['n']] = (dz, re.findall(r'(?m)^- 权柄[一二三]?｜([^：]+)：(.+)$', body))
    return out


def make_dom(src, doms):
    if not src:
        return None
    dz, qb = src
    d = {}
    if dz.get('神力'):
        d['gh'] = noai(dz['神力'])
    sx = dz.get('神性', '')
    if sx:
        d['sx'] = clean(re.split(r'[，。]', sx)[0])
        mm = re.search(r'(?:本域是|拿着)(.{1,6}之域)', sx)
        if mm and mm.group(1) in doms:
            side = '逆位' if ('逆位' in sx) else '正位'
            dd = doms[mm.group(1)]
            d['dm'] = [mm.group(1), side, dd.get(side, ''), dd.get('三迹', '') if side == '正位' else '']
        rest = [x.strip() for x in sx.split('。')[1:] if '另拿着' in x]
        if rest:
            d['dmx'] = clean(re.sub(r'^.*?另拿着', '另拿着', rest[0]) + '。')
    if qb:
        d['qb'] = [[n.strip()] + list(two(t)) for n, t in qb]
    if dz.get('神域专长'):
        d['zc'] = noai(dz['神域专长'])
    if dz.get('神国'):
        d['gk'] = ['神国', noai(dz['神国'])]
    elif dz.get('国律'):
        d['gk'] = ['高座的国律', noai(dz['国律'])]
    if dz.get('今天'):
        d['now'] = noai(dz['今天'])
    if dz.get('对上祂'):
        d['vs'] = noai(dz['对上祂'])
    af = dz.get('陨落以后') or dz.get('倒下以后') or dz.get('剥离以后')
    if af and noai(af):
        d['af'] = noai(af)
    return d


def load_gods():''')

rep("""        x = dict(n=g['n'], tag=g['tag'], side=g['side'], grp=g['grp'], img=g['img'], rule=g['rule'], look=g['look'], at=at)
""",
    """        x = dict(n=g['n'], tag=g['tag'], side=g['side'], grp=g['grp'], img=g['img'], rule=g['rule'], look=g['look'], at=at)
        dom = g['dom'].get(vol if vol in ('moon', 'strife') else 'now')
        if dom:
            x['dom'] = {k: v for k, v in dom.items() if not (vol == 'bronze' and k == 'now')}
""")

open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('打好了')
