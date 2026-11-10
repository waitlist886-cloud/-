# 超凡演出的纹样（11-10）：一种起手一个纹样，单色 SVG，样式里当遮罩用，颜色和动画在样式里给。
# 画法：100×100 的框，线宽 2 上下，只用描边和少量填充；遮罩只认不透明的地方，颜色随便写。
from urllib.parse import quote
import math


def hept(r, rot=0):
    # 七芒星：七个点隔两个连一笔
    return ' '.join('%.1f,%.1f' % (50 + r * math.sin(2 * math.pi * (k * 3 % 7) / 7 + rot), 50 - r * math.cos(2 * math.pi * (k * 3 % 7) / 7 + rot)) for k in range(7))


def svg(body, vb='0 0 100 100'):
    s = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='%s' fill='none' stroke='%%23000' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>%s</svg>" % (vb, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' -.,()%")


def ticks(r1, r2, n, w=1.2):
    import math
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        out.append("<path d='M%.1f %.1fL%.1f %.1f' stroke-width='%s'/>" % (50 + r1 * math.sin(a), 50 - r1 * math.cos(a), 50 + r2 * math.sin(a), 50 - r2 * math.cos(a), w))
    return ''.join(out)


def poly(r, n, rot=0):
    import math
    pts = ['%.1f,%.1f' % (50 + r * math.sin(2 * math.pi * k / n + rot), 50 - r * math.cos(2 * math.pi * k / n + rot)) for k in range(n)]
    return "<polygon points='%s'/>" % ' '.join(pts)


MOTIF = {
    # 法阵：两道圈、刻度、六芒（咏唱）
    'circle': svg("<circle cx='50' cy='50' r='46'/><circle cx='50' cy='50' r='38' stroke-dasharray='2 4'/>" + ticks(40, 46, 36, 1) + poly(36, 3) + poly(36, 3, 3.14159) + "<circle cx='50' cy='50' r='12'/>"),
    # 解析：方格和三道圈（真理、解构）
    'lattice': svg("<circle cx='50' cy='50' r='44'/><circle cx='50' cy='50' r='30' stroke-dasharray='3 3'/><path d='M50 4V96M4 50H96M18 18L82 82M82 18L18 82' stroke-width='1'/>" + poly(30, 4, 0.785) + "<circle cx='50' cy='50' r='6' fill='%23000'/>"),
    # 光放：一圈光芒（极光）
    'burst': svg(ticks(18, 46, 24, 2.4) + "<circle cx='50' cy='50' r='14' fill='%23000'/>"),
    # 光环：圈上一圈短光，正中一点（祷告）
    'halo': svg("<circle cx='50' cy='50' r='30' stroke-width='3'/>" + ticks(36, 46, 16, 2) + "<path d='M50 34V66M34 50H66' stroke-width='3'/>"),
    # 誓剑：剑和十字光（断罪）
    'verdict': svg("<path d='M50 8V78M38 26H62M44 78H56M50 78V92' stroke-width='3'/><circle cx='50' cy='50' r='40' stroke-dasharray='1 5'/>" + ticks(42, 47, 12, 2)),
    # 冲击：三道波和裂纹（摧锋）
    'shock': svg("<circle cx='50' cy='50' r='14' stroke-width='3'/><circle cx='50' cy='50' r='28' stroke-dasharray='6 5'/><circle cx='50' cy='50' r='42' stroke-dasharray='3 7'/><path d='M50 64L44 76L52 84L46 96M36 50L22 46L14 54L4 50M64 50L78 54L86 46L96 50' stroke-width='1.6'/>"),
    # 燃血：滴形火焰（沸血）
    'blood': svg("<path d='M50 8C64 30 76 44 76 62A26 26 0 0 1 24 62C24 44 36 30 50 8Z' stroke-width='3'/><path d='M50 40C56 50 62 56 62 64A12 12 0 0 1 38 64C38 56 44 50 50 40Z' fill='%23000'/>"),
    # 炉心：齿轮里一团火（熔心）
    'forgeheart': svg(poly(44, 12) + "<circle cx='50' cy='50' r='34'/><path d='M50 28C58 40 64 46 64 56A14 14 0 0 1 36 56C36 46 42 40 50 28Z' fill='%23000'/>"),
    # 准星：圈、十字和一根弦（射术）
    'reticle': svg("<circle cx='50' cy='50' r='38'/><circle cx='50' cy='50' r='8'/><path d='M50 4V30M50 70V96M4 50H30M70 50H96' stroke-width='2.4'/><path d='M14 14Q50 34 86 14' stroke-width='1.2' stroke-dasharray='2 3'/>"),
    # 兽迹：三道爪痕加一只脚印（行猎）
    'track': svg("<path d='M22 20L38 58M40 14L52 56M58 12L66 52' stroke-width='4'/><circle cx='70' cy='78' r='9' fill='%23000'/><circle cx='56' cy='66' r='4' fill='%23000'/><circle cx='70' cy='60' r='4' fill='%23000'/><circle cx='84' cy='66' r='4' fill='%23000'/>"),
    # 魔矢：一支箭穿过符环（魔梭）
    'arrow': svg("<circle cx='50' cy='50' r='30' stroke-dasharray='4 4'/><path d='M10 90L88 12M70 12H88V30M10 90L22 86M10 90L14 78' stroke-width='3'/>"),
    # 影：一只眼，眼外一圈散开的雾（影系）
    'eye': svg("<path d='M8 50Q50 12 92 50Q50 88 8 50Z' stroke-width='3'/><circle cx='50' cy='50' r='12' fill='%23000'/>" + ticks(40, 47, 20, 1.2)),
    # 绝影：一道斜斩，两头尖（绝影）
    'slash': svg("<path d='M12 88Q50 50 88 12' stroke-width='6'/><path d='M22 92Q56 56 92 22' stroke-width='1.5' stroke-dasharray='3 4'/><path d='M8 78Q44 44 78 8' stroke-width='1.5' stroke-dasharray='3 4'/>"),
    # 幻刃：三把错开的影子刀（诡刃）
    'mirror': svg("<path d='M30 84L52 16L58 20L38 86Z' fill='%23000' fill-opacity='1'/><path d='M50 84L72 16L78 20L58 86Z' stroke-width='1.6'/><path d='M10 84L32 16L38 20L18 86Z' stroke-width='1.6' stroke-dasharray='3 3'/>"),
    # 盾：盾形和正中一道（渊垒）
    'shield': svg("<path d='M50 8L86 20V48C86 70 70 86 50 94C30 86 14 70 14 48V20Z' stroke-width='3'/><path d='M50 22V80M30 40H70' stroke-width='2'/>"),
    # 舞步：一圈脚步落点（死舞）
    'dance': svg("<circle cx='50' cy='50' r='38' stroke-dasharray='1 6'/>" + ''.join("<ellipse cx='%.1f' cy='%.1f' rx='4' ry='7' fill='%%23000' transform='rotate(%d %.1f %.1f)'/>" % (50 + 30 * __import__('math').sin(a), 50 - 30 * __import__('math').cos(a), d, 50 + 30 * __import__('math').sin(a), 50 - 30 * __import__('math').cos(a)) for a, d in [(k * 0.785, k * 45) for k in range(8)])),
    # 剑阵：一把剑，剑身上三个符点（阵剑）
    'runeblade': svg("<path d='M50 6L58 20V74H42V20Z' stroke-width='2.6'/><path d='M32 74H68M50 74V94' stroke-width='3'/><circle cx='50' cy='30' r='3' fill='%23000'/><circle cx='50' cy='44' r='3' fill='%23000'/><circle cx='50' cy='58' r='3' fill='%23000'/><circle cx='50' cy='50' r='46' stroke-dasharray='2 6'/>"),
    # 天平（天平）
    'scales': svg("<path d='M50 10V86M30 90H70M14 28H86M50 10L46 18H54Z' stroke-width='2.6'/><path d='M14 28L4 56H24ZM86 28L76 56H96Z' stroke-width='2'/><path d='M4 56Q14 66 24 56M76 56Q86 66 96 56' stroke-width='2'/>"),
    # 鼎：一口锅和三道热气（鼎镬）
    'cauldron': svg("<path d='M14 46H86C86 70 70 84 50 84C30 84 14 70 14 46Z' stroke-width='3'/><path d='M8 46H92M30 84L24 94M70 84L76 94' stroke-width='2.6'/><path d='M34 36C30 28 38 22 34 12M50 36C46 28 54 22 50 12M66 36C62 28 70 22 66 12' stroke-width='2'/>"),
    # 锤和砧（千锤）
    'anvil': svg("<path d='M18 60H82L72 72H60V84H74V90H26V84H40V72H28Z' stroke-width='2.6'/><path d='M60 8L84 32L76 40L52 16ZM64 28L34 58' stroke-width='3'/><path d='M22 40L14 34M30 34L28 24M16 50L6 50' stroke-width='1.6'/>"),
    # 药瓶和一枝藤（枯荣）
    'flask': svg("<path d='M40 8H60M44 8V34L22 76C18 84 24 92 32 92H68C76 92 82 84 78 76L56 34V8' stroke-width='2.6'/><path d='M30 68H70' stroke-width='1.6'/><path d='M50 92C50 76 62 70 70 62M62 66C66 70 72 70 76 66' stroke-width='1.6'/>"),
    # 锁链和印（铁律）
    'chain': svg("<rect x='34' y='34' width='32' height='32' rx='4' stroke-width='3'/><path d='M50 42V58M42 50H58' stroke-width='2'/><path d='M8 20C8 12 20 12 20 20S32 28 32 20M68 80C68 72 80 72 80 80S92 88 92 80' stroke-width='2.4'/><path d='M26 26L34 34M66 66L74 74' stroke-width='2.4'/>"),
    # 罗盘和测线（解构）
    'compass': svg("<circle cx='50' cy='50' r='40'/><path d='M50 14L58 50L50 86L42 50Z' stroke-width='2.4'/><path d='M50 14L58 50H42Z' fill='%23000'/>" + ticks(40, 46, 16, 1.2)),
    # 火（月银纪的祭火、守火）
    'fire': svg("<path d='M50 6C60 26 78 36 78 60A28 28 0 0 1 22 60C22 44 32 36 36 22C40 34 44 38 50 40C50 28 46 18 50 6Z' stroke-width='3'/><path d='M50 50C56 58 60 62 60 70A10 10 0 0 1 40 70C40 62 44 58 50 50Z' fill='%23000'/>"),
    # 星（神眷、曜）
    'star': svg("<path d='M50 6L60 40L94 50L60 60L50 94L40 60L6 50L40 40Z' stroke-width='2.6'/><circle cx='50' cy='50' r='8' fill='%23000'/><circle cx='50' cy='50' r='44' stroke-dasharray='1 7'/>"),
    # 誓印（铸名、血誓）
    'seal': svg("<circle cx='50' cy='50' r='40' stroke-width='3'/><circle cx='50' cy='50' r='32' stroke-dasharray='2 3'/><path d='M36 36L64 64M64 36L36 64' stroke-width='3'/><circle cx='50' cy='50' r='8' fill='%23000'/>"),
    # 同念（纷争纪的术式兵团）：脚下一圈白线，三角朝哪边术就落在哪边，圈上一圈站着的人
    'formation': svg("<circle cx='50' cy='50' r='40' stroke-width='2.2' stroke-dasharray='5 3'/>" + poly(26, 3, 0.35) + ''.join("<circle cx='%.1f' cy='%.1f' r='3.2' fill='%%23000'/>" % (50 + 46 * math.sin(k * 0.5236), 50 - 46 * math.cos(k * 0.5236)) for k in range(12)) + "<path d='M62 26L74 14M74 14H64M74 14V24' stroke-width='2.6'/>"),
    # 军阵（旧的，留着不用）
    'legion': svg(''.join("<rect x='%d' y='%d' width='10' height='10' rx='2' fill='%%23000'/>" % (14 + 16 * i, 24 + 16 * j) for i in range(5) for j in range(4)) + "<path d='M8 14H92' stroke-width='2.4'/>"),
    # 呼吸（月银纪的呼吸法、调息）：两道吸进去又盘回来的气，正中一点
    'breath': svg("<path d='M10 34C30 18 52 22 50 40C48 54 30 50 34 40' stroke-width='3'/><path d='M90 66C70 82 48 78 50 60C52 46 70 50 66 60' stroke-width='3'/><path d='M14 62C26 56 36 58 42 64M86 38C74 44 64 42 58 36' stroke-width='1.8' stroke-dasharray='2 4'/><circle cx='50' cy='50' r='5' fill='%23000'/>"),
    # 冥想：一道合着的眼，眼外两道圈，额上一点
    'meditate': svg("<circle cx='50' cy='50' r='44' stroke-dasharray='1 6'/><circle cx='50' cy='50' r='32' stroke-width='1.6'/><path d='M22 54Q50 74 78 54' stroke-width='3.2'/><path d='M30 62L26 70M42 67L40 76M58 67L60 76M70 62L74 70' stroke-width='2'/><circle cx='50' cy='32' r='5' fill='%23000'/>"),
    # 圣歌（前传和今天的圣歌旅印：七芒星、光环、波纹）
    'song': svg("<circle cx='50' cy='50' r='44' stroke-width='1.4'/><circle cx='50' cy='50' r='38' stroke-dasharray='2 3'/><polygon points='%s' stroke-width='2.2'/>" % hept(32) + "<path d='M30 84Q40 78 50 84T70 84M34 92Q42 88 50 92T66 92' stroke-width='1.6'/><circle cx='50' cy='50' r='6' fill='%23000'/>"),
    # 结环（萨尔维斯的铭环、环印）：两道环，环上刻满字，各缺一个口
    'ring': svg("<path d='M50 6A44 44 0 1 1 18 20' stroke-width='3'/><path d='M50 18A32 32 0 1 0 82 50' stroke-width='2'/>" + ticks(36, 41, 28, 1.1) + "<circle cx='50' cy='50' r='9' stroke-width='2.4'/><circle cx='50' cy='50' r='3' fill='%23000'/>"),
    # 誓印：一枚封蜡，边上一圈波纹，当中一道竖、一道横（誓、宣判、契约）
    'oathseal': svg(''.join("<circle cx='%.1f' cy='%.1f' r='7' fill='%%23000'/>" % (50 + 38 * math.sin(k * 0.5236), 50 - 38 * math.cos(k * 0.5236)) for k in range(12)) + "<circle cx='50' cy='50' r='38' fill='%23000'/><path d='M50 28V72M34 44H66' stroke='%23fff' stroke-width='5'/>"),
    # 龙：一只竖瞳的眼，上下两排鳞（真龙、龙裔、古龙祷告）
    'drake': svg("<path d='M6 50Q50 10 94 50Q50 90 6 50Z' stroke-width='3'/><path d='M50 26Q60 50 50 74Q40 50 50 26Z' fill='%23000'/>" + ''.join("<path d='M%d %dq6 -6 12 0' stroke-width='1.6'/>" % (8 + 12 * k, 90 - (k % 2) * 4) for k in range(7)) + ''.join("<path d='M%d %dq6 6 12 0' stroke-width='1.6'/>" % (8 + 12 * k, 10 + (k % 2) * 4) for k in range(7))),
    # 铳（山铜纪的铳是施法的家什）：铳口一圈回路，口上一点光
    'gun': svg("<circle cx='50' cy='50' r='40' stroke-dasharray='3 4'/><circle cx='50' cy='50' r='22' stroke-width='3'/><circle cx='50' cy='50' r='10' fill='%23000'/>" + ticks(26, 34, 8, 2.4) + "<path d='M50 2V12M50 88V98M2 50H12M88 50H98' stroke-width='2'/>"),
}


# 纪元的底纹（彩色，不当遮罩）：垫在起手框左边那一块纹样底下
def svgc(body, vb='0 0 100 100'):
    s = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='%s' fill='none' stroke-linecap='round' stroke-linejoin='round'>%s</svg>" % (vb, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' -.,()%")


def _dots7(r):
    cols = ['%23ff5a3d', '%23ffa14a', '%23ffd257', '%237dd36a', '%234fd1c5', '%234f8cff', '%23b07cff']   # 七曜：赤火、橙冰、黄岩、绿草、青风、蓝水、紫雷
    return ''.join("<circle cx='%.1f' cy='%.1f' r='3.4' fill='%s'/>" % (50 + r * math.sin(2 * math.pi * k / 7), 50 - r * math.cos(2 * math.pi * k / 7), c) for k, c in enumerate(cols))


BACK = {
    # 迷宫纪：圣歌那一枚七芒星，金线
    'maze': svgc("<polygon points='%s' stroke='%%23d6b26a' stroke-width='1' stroke-opacity='.75'/><circle cx='50' cy='50' r='47' stroke='%%23d6b26a' stroke-width='.8' stroke-opacity='.5'/><circle cx='50' cy='50' r='41' stroke='%%23d6b26a' stroke-width='.6' stroke-dasharray='1 3' stroke-opacity='.6'/>" % hept(45)),
    # 迷宫纪前传：铜版画的排线，一个圈里斜着排满细线
    'pre': svgc("<defs><clipPath id='c'><circle cx='50' cy='50' r='46'/></clipPath></defs><g clip-path='url(%23c)' stroke='%233b2614' stroke-width='.7' stroke-opacity='.55'>" + ''.join("<path d='M%d 0L%d 100'/>" % (x, x - 60) for x in range(0, 170, 5)) + "</g><circle cx='50' cy='50' r='46' stroke='%233b2614' stroke-width='1.4'/><circle cx='50' cy='50' r='42' stroke='%233b2614' stroke-width='.6'/>"),
    # 山铜纪：碑的刻框，两道方线，四角一个钉
    'bronze': svgc("<rect x='6' y='6' width='88' height='88' stroke='%23d8b45a' stroke-width='1.4' stroke-opacity='.8'/><rect x='12' y='12' width='76' height='76' stroke='%23d8b45a' stroke-width='.6' stroke-opacity='.6'/>" + ''.join("<circle cx='%d' cy='%d' r='2.2' fill='%%23d8b45a' fill-opacity='.8'/>" % (x, y) for x in (6, 94) for y in (6, 94))),
    # 纷争纪：同念画在地上的那一圈白线和三角，粉笔画的
    'strife': svgc("<circle cx='50' cy='50' r='45' stroke='%%23efeadc' stroke-width='1.6' stroke-opacity='.55' stroke-dasharray='7 2 1 2'/><polygon points='%s' stroke='%%23efeadc' stroke-width='1.2' stroke-opacity='.5'/>" % ' '.join('%.1f,%.1f' % (50 + 40 * math.sin(2 * math.pi * k / 3 + 0.35), 50 - 40 * math.cos(2 * math.pi * k / 3 + 0.35)) for k in range(3))),
    # 月银纪：铭环和七曜，环上七个颜色的点
    'moon': svgc("<circle cx='50' cy='50' r='44' stroke='%23e6ecff' stroke-width='1' stroke-opacity='.6'/><circle cx='50' cy='50' r='38' stroke='%23e6ecff' stroke-width='.6' stroke-dasharray='1 2.5' stroke-opacity='.7'/>" + _dots7(44)),
}
