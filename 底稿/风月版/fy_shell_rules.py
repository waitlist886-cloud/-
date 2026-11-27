# 风月四张外壳的显示正则（11-25）。日里现行那一套（rules_convert.json、rules_frame.json，跟四纪大框一条流水线：补认不出纪元的那一条、
# four_era_art.rules、mod_page.apply_rules）转成风月的写法。转法照 11-04 的 make_fy_card.py，下面几处是这一回添的：
#   - 一张卡一纪：别纪的记号、字眼、认纪元、传唱战报碑那几行拿掉；这一纪的记号不看日期直接落（日期写歪了也照这一纪的字眼），
#     页上写齐四纪说法的那几处字（<span class="lw">）拆回这一纪的字。迷宫纪拆成前传、此刻两张（11-25 夜）：前传那一张只留前传的认纪元，认不出年份的照前传；
#     此刻那一张只留 1001 年的，认不出年份的照 1001 年。地图页两张都留（日里那边前传的回复也出地图页）。
#   - 回复里不能带 <style>：钟点换成空记号（照旧）；认纪元那几条只留空记号（样式照它换材质，见 fy_shell_css.py）；
#     主角立绘那三条原来往回复里写一段样式，换成给对话框、面板上那个人形挂 data-pc（预设）或者行内的大写变量（自己贴的图）。
#   - 行内 style 的自定义属性全换大写：这一个月新添的 --hv --hm --lv --cap --xv --xm --bn --pg --a --b 也在里头，名单从规则里现数。
#   - 转换那一组：此刻那一张顶替线上老卡，“转”（旧 HTML 回复转记录）和“稳”都放存、显两份；另外四张是新卡，只放“稳”两份。
# 这里不改日里的任何文件。用法见 fy_shell.py。
import copy
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BIG = os.path.join(ROOT, '底稿', '状态栏', '大框')
if BIG not in sys.path:
    sys.path.insert(0, BIG)
sys.dont_write_bytecode = True

# 五张卡。键是卡名（也是输出目录名）；key：图床文件名、简介页、快捷指令那几张表的键；eras：这一张里有哪几纪的材质（era-maze 是 1001 年，era-pre 是前传）；
# mark：这一纪的字眼记号；lw：页上那几处字取哪一格；fallback：认不出年份的回复算哪一纪；convert：顶替线上老卡，带“转”那一组、线上那张的旧样式整段留着
# （迷宫纪原来是一张，eras=['maze', 'pre']，11-25 夜拆成下面两张；fy_shell_css 两种材质切换那一段还认这种写法）
CARDS = {
    '迷宫纪前传': dict(key='pre', eras=['pre'], mark=None, lw='w0', fallback='pre', convert=False),
    '迷宫纪此刻': dict(key='now', eras=['maze'], mark=None, lw='w0', fallback='maze', convert=True),
    '月银纪': dict(key='moon', eras=['moon'], mark='Ⓜ', lw='wm', fallback='moon', convert=False),
    '纷争纪': dict(key='strife', eras=['strife'], mark='Ⓢ', lw='ws', fallback='strife', convert=False),
    '山铜纪': dict(key='bronze', eras=['bronze'], mark='Ⓑ', lw='wb', fallback='bronze', convert=False),
}
ROW_OF = {'传唱': 'moon', '战报': 'strife', '团': 'bronze'}     # §面板｜旅印 那一行各纪自己的写法（data-k）
LW = re.compile(r'<span class="lw"><span class="w0">([^<]*)</span><span class="wm">([^<]*)</span><span class="ws">([^<]*)</span><span class="wb">([^<]*)</span></span>')
LW_IX = {'w0': 1, 'wm': 2, 'ws': 3, 'wb': 4}
STYLE = re.compile(r'<style>[\s\S]*?</style>')
TAG_OK = set('a abbr address area article aside audio b base bdi bdo blockquote body br button canvas caption cite code col colgroup data datalist dd del details dfn dialog div dl dt em embed fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 head header hgroup hr html i iframe img input ins kbd label legend li link main map mark meta meter nav noscript object ol optgroup option output p param picture pre progress q rp rt ruby s samp script section select slot small source span strong style sub summary sup table tbody td template textarea tfoot th thead time title tr track u ul var video wbr'.split())
STRIP = set('script iframe object embed applet link meta base html head body form style'.split())


def read(*p):
    return open(os.path.join(*p), encoding='utf-8', newline='').read().replace('\r\n', '\n')


def once(s, a, b, what=''):
    assert s.count(a) == 1, ('对不上', what, s.count(a), a[:70])
    return s.replace(a, b)


# ---------------- 日里那一头：照四纪大框的流水线拼一遍（带名字） ----------------
def rili_rules(with_convert):
    """返回日里写法的规则表（带 name）。with_convert：留不留“转”那一组（四纪大框 11-23 拿掉了）"""
    import four_era_art as FA
    import mod_page as MP
    convert = json.loads(read(BIG, 'rules_convert.json'))
    frame = json.loads(read(BIG, 'rules_frame.json'))
    if not with_convert:
        convert = [r for r in convert if not (r.get('name') or '').startswith('转')]
    rules = [dict(r) for r in convert + frame]
    k = max(i for i, r in enumerate(rules) if '<i class="sz-era era-' in r['replaceString']) + 1
    maze = next(r for r in rules if '<i class="sz-era era-maze"' in r['replaceString'])
    rules.insert(k, dict(maze, name='纪元·认不出', regex='/(<summary class="sz-head">)(?!<i class="sz-era)/',
                         replaceString=re.sub(r' data-y="[^"]*"', ' data-y=""', maze['replaceString'])))
    rules = FA.rules(rules)
    MP.apply_rules(rules)
    assert all(r.get('name') for r in rules)
    return rules


def sync_check(rili_card):
    """源稿拼出来的（不带“转”）跟日里全本里的规则一不一样。返回 (一样不一样, 说明)"""
    mine = [(r['regex'], r['replaceString'], r.get('applyMode')) for r in rili_rules(False)]
    card = [(r['regex'], r['replaceString'], r.get('applyMode')) for r in rili_card['assistantRegexReplace'] if 'data-aldran-css' not in r['replaceString']]
    if mine == card:
        return True, '跟日里全本的 %d 条一字不差' % len(card)
    n = next((i for i, (a, b) in enumerate(zip(mine, card)) if a != b), min(len(mine), len(card)))
    return False, '源稿拼出来 %d 条，日里全本 %d 条，从第 %d 条起不一样（源稿在日里全本打出来以后又改过，外壳照源稿）' % (len(mine), len(card), n)


# ---------------- 主角立绘：回复里不能带 <style>，换成挂属性 ----------------
_NAME = r'§面板｜身份｜\2(?=[｜·（(\s])'
_SAY = r'(<div class="sz-say" data-portrait="([^"<>]{1,14})")(?=[\s\S]*?' + _NAME + r'[\s\S]*?§面板｜立绘｜'
_URL = r'''(https?:\/\/[^\s"'<>()\\｜;]{8,400})'''
_URL_END = r'''(?![^\s"'<>()\\｜;])'''
_PRE = r'预设·([^｜\n·<>"\s;:{}]{1,8})·([男女])·([^｜\n·<>"\s;:{}]{1,4})'


def _r(name, rx, rep):
    return {'name': name, 'regex': rx, 'replaceString': rep, 'enabled': True, 'messageRole': 'assistant', 'applyMode': 'front-end'}


PC_SAY = [
    _r('主角·话·预设', '/' + _SAY + _PRE + ')/g', '$1 data-pc="$3-$4-$5"'),
    _r('主角·话·地址·头像', '/' + _SAY + _URL + '｜头像[:：]' + _URL + _URL_END + ')/g', '''$1 data-pcu="1" style="--ufc:url('$4');--uar:url('$3')"'''),
    _r('主角·话·地址', '/' + _SAY + _URL + _URL_END + '(?!｜头像))/g', '''$1 data-pcu="1" style="--ufc:url('$3');--uar:url('$3')"'''),
]
# 检定面板主角那一边（11-25 日里那头在添的「判·主角」给它挂 jg-pc，日里的样式多认一个 .jg-w.jg-pc）：同样挂属性。那一条还没进规则表的时候这三条不中，白放着不碍事
_JG = r'(<span class="jg-w [lr] jg-pc")(?=[\s\S]*?§面板｜立绘｜'
PC_SAY += [
    _r('主角·判·预设', '/' + _JG + _PRE + ')/g', '$1 data-pc="$2-$3-$4"'),
    _r('主角·判·地址·头像', '/' + _JG + _URL + '｜头像[:：]' + _URL + _URL_END + ')/g', '''$1 data-pcu="1" style="--ufc:url('$3');--uar:url('$2')"'''),
    _r('主角·判·地址', '/' + _JG + _URL + _URL_END + '(?!｜头像))/g', '''$1 data-pcu="1" style="--ufc:url('$2');--uar:url('$2')"'''),
]
_DOLL = r'<i class="sz-doll-fig"(?=[^>]*>[\s\S]*?§面板｜立绘｜'
PC_DOLL = [
    _r('主角·人形·预设', '/' + _DOLL + _PRE + ')/', '<i class="sz-doll-fig" data-pc="$1-$2-$3"'),
    _r('主角·人形·地址', '/' + _DOLL + _URL + _URL_END + ')/', '''<i class="sz-doll-fig" data-pcu="1" style="--udl:url('$1')"'''),
]


# ---------------- 一张卡要的那一份（还是日里的写法） ----------------
def adapt(rules, card):
    """rules：rili_rules() 的结果。返回 (convert, frame, 账)。convert 是转换那一组（存、显各放一份），frame 只显示"""
    C = CARDS[card]
    acct = {'拿掉': [], '改': []}
    k0 = next(i for i, r in enumerate(rules) if r['name'] == '去外层围栏')
    out = []
    pc_seen = 0
    for i, r in enumerate(rules):
        r = dict(r)
        n, rx, rep = r['name'], r['regex'], r['replaceString']
        drop = None
        # 一、字眼的记号：这一纪的不看日期直接落，别纪的拿掉
        if rep in ('$1Ⓜⓩ', '$1Ⓢⓩ', '$1Ⓑⓩ'):
            if rep[2] != C['mark']:
                drop = '别纪的记号'
            else:
                assert rx.startswith('/^((?:[\\s\\S]*\\n|)§底座｜纪元：') and rx.endswith('[\\s\\S]*)ⓩ\\s*$/'), rx
                rx = '/^((?:[\\s\\S]*\\n|)§底座｜[\\s\\S]*)ⓩ\\s*$/'
                acct['改'].append(n + '：不看日期')
        elif re.search(r'\(\?=\[\\s\\S\]\*[ⓂⓈⒷ]\)/g$', rx):          # 字眼·一处一条的那几条（/…(?=[\s\S]*Ⓜ)/g）
            if rx[-4] != C['mark']:
                drop = '别纪的字眼'
        # 二、认纪元：<style> 拿掉，只留空记号；一张卡里没有的纪拿掉；认不出的那一条照这一张的底
        m = re.search(r'<i class="sz-era era-(\w+)" data-y="([^"]*)"></i>', rep)
        if m and not drop:
            rep = STYLE.sub('', rep)
            if '(?!<i class="sz-era)' in rx:
                rep = rep.replace('era-' + m.group(1), 'era-' + C['fallback'])
                acct['改'].append(n + '：认不出的算 ' + C['fallback'])
            elif m.group(1) not in C['eras']:
                drop = '别纪的纪元'
        # 三、钟点：换成空记号（只认到小时）
        if rep == '$1<style>.custom-styles{--sz-on:1;--sz-h:$2;--sz-m:$3}</style>':
            rep = '$1<i class="sz-hh" data-h="$2"></i>'
        # 四、主角立绘：三条往回复里写样式的换成挂属性；衣着那一条后头接人形的两条
        # 三之二、骰盘（11-27，dice_fx.py）：回复里那一段认最新一条的 <style> 拿掉，风月照“最后一对问答是外壳的直接内容”认（dice_fx.fy_css）
        if n == '骰盘':
            rep = STYLE.sub('', rep)
            acct['改'].append(n + '：拿掉认最新一条的 <style>')
        if n.startswith('主角·立绘·') and '<style>' in rep:
            pc_seen += 1
            if pc_seen == 1:
                out.extend(copy.deepcopy(PC_SAY))
            continue
        # 五、各纪自己的那几行、地图页、专名表
        mk = re.search(r'<div class="sz-f sz-seal" data-k="(传唱|战报|团)">', rep)
        if mk and ROW_OF[mk.group(1)] not in C['eras']:
            drop = '别纪的旅印行'
        if 'sz-pane p-map' in rep and not ({'maze', 'pre'} & set(C['eras'])):
            drop = '地图页（只有迷宫纪）'
        if C['mark'] and n == '名词·表':
            assert rx.endswith('(?=[\\s\\S]*\\nⓩ)/gm'), rx[-40:]
            drop = '专名表（1001 年的）'
        if drop:
            acct['拿掉'].append((n, drop))
            continue
        # 六、页上那几处字：拆回这一纪的
        rep = LW.sub(lambda x: x.group(LW_IX[C['lw']]), rep)
        assert 'class="lw"' not in rep, n
        # 六之二、入局那一条（11-26d，entry_page.py）：门扉退成一行字，“哪里不对”“填进输入框”两个钮拿掉
        if n.startswith('入局'):
            import entry_page as _EP
            rep2 = _EP.fy_rep(n, rep)
            if rep2 != rep:
                acct['改'].append(n + '：风月没有点击，钮拿掉')
            rep = rep2
        # 七、分支点不了
        if 'data-action="set-textinput"' in rep:
            rep = once(rep, ' data-action="set-textinput" data-value="$1"', '', '分支')
        r['regex'], r['replaceString'] = rx, rep
        out.append(r)
        if n == '主角·衣着':
            out.extend(copy.deepcopy(PC_DOLL))
    assert pc_seen == 3, pc_seen
    assert sum(1 for r in out if r['name'].startswith('主角·人形·')) == 2
    k = next(i for i, r in enumerate(out) if r['name'] == '去外层围栏')
    convert, frame = out[:k], out[k:]
    assert all(r['applyMode'] == 'all' for r in convert), [r['name'] for r in convert if r['applyMode'] != 'all'][:5]
    for r in out:
        assert '<style' not in r['replaceString'] and 'data-action' not in r['replaceString'] and '<link' not in r['replaceString'], r['name']
        for t in re.findall(r'</?([a-zA-Z][\w-]*)', r['replaceString']):
            assert t.lower() in TAG_OK and (t.lower() not in STRIP), ('平台认不得或者会拿掉的标签', t, r['name'])
    # 认纪元：这一张里每一纪一条，后头一条认不出的
    eras = [m.group(1) for r in frame for m in [re.search(r'<i class="sz-era era-(\w+)" data-y="[^"]', r['replaceString'])] if m]
    assert sorted(eras) == sorted(C['eras']), eras
    return convert, frame, acct


# ---------------- 行内 style 的自定义属性：小写的会被平台改坏（--v 变成 -V），全换大写 ----------------
def inline_vars(rules):
    names = set()
    for r in rules:
        for m in re.finditer(r'style="([^"]*)"', r['replaceString']):
            names |= set(re.findall(r'(?:^|;)\s*--([\w-]+)\s*:', m.group(1)))
    return sorted(names, key=lambda s: (-len(s), s))


def upvar_re(names):
    return re.compile(r'(?<![\w-])--(' + '|'.join(re.escape(n) for n in names) + r')(?![\w-])')


def upvar(s, rx):
    return rx.sub(lambda m: '--' + m.group(1).upper(), s)


# ---------------- 日里的 /pat/flags 换成风月只认 g 的写法（照 make_fy_card.py 抄的，那一份是脚本，引不进来） ----------------
def scan(p):
    i, in_cls = 0, False
    while i < len(p):
        c = p[i]
        if c == '\\':
            yield i, p[i:i + 2], in_cls, True
            i += 2
            continue
        if in_cls:
            if c == ']':
                in_cls = False
        elif c == '[':
            in_cls = True
            yield i, c, False, False
            i += 1
            continue
        yield i, c, in_cls, False
        i += 1


def groups(p):
    n = 0
    for i, c, cls, esc in scan(p):
        if c == '(' and not cls and not esc:
            if p[i + 1:i + 2] != '?' or p[i + 1:i + 3] == '?<' and p[i + 3:i + 4] not in ('=', '!'):
                n += 1
    return n


def no_m(p):
    out, last = [], 0
    for i, c, cls, esc in scan(p):
        if cls or esc:
            continue
        if c == '^':
            out += [p[last:i], r'(?<![^\n])']
            last = i + 1
        elif c == '$':
            out += [p[last:i], r'(?![^\n])']
            last = i + 1
    out.append(p[last:])
    return ''.join(out)


def shift_backrefs(p, k=1):
    out, last = [], 0
    for i, c, cls, esc in scan(p):
        if esc and not cls and len(c) == 2 and c[1] in '123456789':
            assert p[i + 2:i + 3] not in '0123456789' or i + 2 >= len(p), ('两位数的反向引用', p[i:i + 4])
            out += [p[last:i], '\\%d' % (int(c[1]) + k)]
            last = i + 2
    out.append(p[last:])
    return ''.join(out)


def port(r, render_only, title=None):
    m = re.match(r'^/([\s\S]*)/([^/]*)$', r['regex'])
    assert m, r['regex'][:60]
    pat, flags = m.group(1), m.group(2)
    assert set(flags) <= set('gm'), flags
    rep = r['replaceString']
    if 'm' in flags:
        pat = no_m(pat)
    if 'g' not in flags:
        # 只换第一处：从字符串头懒惰地找到第一处，尾巴接在后面
        n = groups(pat)
        assert n + 2 < 100, (r['name'], n)
        rep = re.sub(r'\$(\d{1,2})', lambda x: '$%d' % (int(x.group(1)) + 1) if 1 <= int(x.group(1)) <= n else x.group(0), rep)
        pat = '^([\\s\\S]*?)(?:' + shift_backrefs(pat) + ')([\\s\\S]*)$'
        rep = '$1' + rep + '$%d' % (n + 2)
    return {'title': title or r['name'], 'match_regex': pat, 'replace_text': rep, 'scope': 1, 'is_enable': True, 'is_only_render': render_only}


def build(card):
    """一张卡的风月规则。返回 (regex_rp, 日里写法的参照 {convert, frame}, 大写的变量名单, 账)"""
    C = CARDS[card]
    convert, frame, acct = adapt(rili_rules(C['convert']), card)
    names = inline_vars(convert + frame)
    rx = upvar_re(names)
    for r in convert + frame:
        r['regex'], r['replaceString'] = upvar(r['regex'], rx), upvar(r['replaceString'], rx)
    fy = [port(r, False, '存·' + r['name']) for r in convert] + [port(r, True, '显·' + r['name']) for r in convert] + [port(r, True) for r in frame]
    for r in fy:
        try:
            re.compile(r['match_regex'].replace('(?<![^\\n])', '(?<![^\n])'))
        except re.error as e:
            # (?=(X))\2 学原子组的那几条、反向引用写在组里头的，Python 不认、JS 认，交给 fy_shell_check.mjs 用 node 编
            assert 'open group' in str(e) or 'invalid group reference' in str(e), (r['title'], e)
    acct.update({'转换': len(convert), '展开': len(frame), '风月': len(fy), '字数': sum(len(r['match_regex']) + len(r['replace_text']) for r in fy)})
    return fy, {'convert': convert, 'frame': frame}, names, acct


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for c in CARDS:
        fy, ref, names, acct = build(c)
        print(c, '风月', acct['风月'], '条（转换', acct['转换'], '×2，展开', acct['展开'], '），', acct['字数'], '字；拿掉', len(acct['拿掉']), '条；大写变量', len(names))
