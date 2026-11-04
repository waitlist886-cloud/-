# 一纪一组变量的名字，样式（make_css_frame.py）和展开规则（make_rules_frame.py）共用。
# 样式把一纪的值写在外壳上，名字带这一纪（--moon-ink）。整页用哪一组，由回复里那一段 <style> 指（把 --fm-ink 指到 --moon-ink）：
# 行按先后排，后写的盖先写的，所以整页跟着 DOM 里最靠后的那条回复走，换了纪元就换，往上翻到哪一纪就是哪一纪。
# 不能写成 :has(.era-x)：同一屏里有两纪的回复时两条都中，后写的那一纪永远赢，换了纪元也切不回来（11-04 用户要两纪做进同一张卡时查出来的）。
NAMES = ['base', 'mat', 'ink', 'ink2', 'head', 'acc', 'acc2', 'line', 'band', 'band2', 'panel', 'slot', 'veil', 'glow', 'edge', 'edge2',
         'l', 'r', 'top', 'bot', 'por1', 'por2', 'emblem', 'sep', 'c1', 'c2', 'c3', 'c4', 'pl', 'pr', 'gem', 'matc', 'fw', 'bb', 'hl', 'hr', 'hx', 'lance', 'bimg', 'bw']
BAND2 = {'maze': '#0d0c2a', 'moon': '#111824', 'strife': '#181412', 'bronze': '#0e0f11', 'pre': '#24190f'}


def sheet(k):
    """一条回复里那一段 <style>。顶栏和 main 不在外壳里，读不到外壳上的变量，直接写颜色；浅色主题下平台的顶栏是白的，框是一整片深色，压成这一纪的底色"""
    return ('.custom-styles{%s}' % ';'.join('--fm-%s:var(--%s-%s)' % (n, k, n) for n in NAMES) +
            '.custom-styles:has(~ main .sz-hud){background-color:color-mix(in srgb, %s 72%%, transparent)!important}'
            '.custom-styles ~ main:has(.sz-hud){background-color:%s}' % (BAND2[k], BAND2[k]))
