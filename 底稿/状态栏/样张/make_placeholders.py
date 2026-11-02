# 状态栏美化方向稿的占位浮雕（不进卡）：粗块面加 SVG 浮雕滤镜，单色灰、透明底，只为摆位置、看比例。
# 用法：python3 -I -X utf8 make_placeholders.py 输出目录
import sys, os, math
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

FILT = '''<defs>
<filter id="rel" x="-3%" y="-3%" width="106%" height="106%" color-interpolation-filters="sRGB">
 <feGaussianBlur in="SourceAlpha" stdDeviation="{b}" result="h"/>
 <feDiffuseLighting in="h" surfaceScale="{s}" diffuseConstant="1.15" lighting-color="#ffffff" result="l"><feDistantLight azimuth="225" elevation="38"/></feDiffuseLighting>
 <feComposite in="l" in2="SourceGraphic" operator="arithmetic" k1="1" k2="0" k3="0" k4="0" result="m"/>
 <feComposite in="m" in2="SourceAlpha" operator="in"/>
</filter>
<filter id="ghost" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>'''

def svg(w, h, body, b=3, s=5):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{FILT.format(b=b, s=s)}{body}</svg>'

def label(x, y, t, size=22, anchor='middle', fill='#8a94a8'):
    return f'<text x="{x}" y="{y}" font-family="Noto Sans CJK SC, sans-serif" font-size="{size}" fill="{fill}" text-anchor="{anchor}" opacity=".95">{t}</text>'

def person(x, y, sc=1.0, horns=False, ears=False, arm=None):
    """y 是脚底。返回一个站着的小人（头、躯干、腿）。"""
    hr = 9 * sc
    parts = [f'<ellipse cx="{x}" cy="{y-58*sc}" rx="{hr}" ry="{hr*1.1}"/>',
             f'<path d="M{x-14*sc},{y-46*sc} Q{x},{y-52*sc} {x+14*sc},{y-46*sc} L{x+12*sc},{y-18*sc} L{x+9*sc},{y} L{x+2*sc},{y} L{x},{y-16*sc} L{x-2*sc},{y} L{x-9*sc},{y} L{x-12*sc},{y-18*sc} Z"/>']
    if horns:
        parts.append(f'<path d="M{x-6*sc},{y-66*sc} L{x-11*sc},{y-80*sc} L{x-2*sc},{y-68*sc} Z M{x+6*sc},{y-66*sc} L{x+11*sc},{y-80*sc} L{x+2*sc},{y-68*sc} Z"/>')
    if ears:
        parts.append(f'<path d="M{x-8*sc},{y-60*sc} L{x-17*sc},{y-66*sc} L{x-8*sc},{y-55*sc} Z M{x+8*sc},{y-60*sc} L{x+17*sc},{y-66*sc} L{x+8*sc},{y-55*sc} Z"/>')
    if arm == 'up':
        parts.append(f'<path d="M{x+10*sc},{y-44*sc} L{x+24*sc},{y-78*sc} L{x+29*sc},{y-76*sc} L{x+15*sc},{y-40*sc} Z"/>')
    return ''.join(parts)

def slab(w, top, bot, ledge_top=True):
    # 一条石带，带一道线脚
    d = f'<path d="M30,{top} L{w-30},{top} Q{w-6},{top} {w-6},{top+24} L{w-6},{bot-24} Q{w-6},{bot} {w-30},{bot} L30,{bot} Q6,{bot} 6,{bot-24} L6,{top+24} Q6,{top} 30,{top} Z" fill="#cfd3da"/>'
    ly = bot - 26 if ledge_top else top + 10
    d += f'<rect x="18" y="{ly}" width="{w-36}" height="16" rx="6" fill="#e2e5ea"/>'
    return f'<g filter="url(#rel)">{d}</g>'

def towers(cx, base):
    g = []
    for dx, hh, ww in ((0, 190, 64), (-150, 140, 44), (150, 140, 44), (-270, 95, 30), (270, 95, 30)):
        x = cx + dx
        g.append(f'<path d="M{x-ww/2},{base-30} L{x-ww/2},{base-hh} L{x},{base-hh-ww*1.2} L{x+ww/2},{base-hh} L{x+ww/2},{base-30} Z"/>')
        g.append(f'<path d="M{x-ww*0.9},{base-30} L{x+ww*0.9},{base-30} L{x},{base+16} Z"/>')
        g.append(f'<ellipse cx="{x}" cy="{base-hh-ww*0.6}" rx="{ww*0.9}" ry="{ww*0.25}" fill="none" stroke="#d6dae2" stroke-width="5"/>')
    return f'<g filter="url(#rel)" fill="#e9ebef">{"".join(g)}</g>'

def crowd(x0, x1, y, n):
    g = []
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        g.append(person(x, y, 0.62, horns=(i % 5 == 2), ears=(i % 5 == 4)))
    return f'<g filter="url(#rel)" fill="#e4e7ec">{"".join(g)}</g>'

def demon(cx, cy, sc=1.0):
    d = (f'<path d="M{cx-150*sc},{cy+120*sc} Q{cx-120*sc},{cy-10*sc} {cx-60*sc},{cy-20*sc} Q{cx-70*sc},{cy-110*sc} {cx},{cy-120*sc} '
         f'Q{cx+70*sc},{cy-110*sc} {cx+60*sc},{cy-20*sc} Q{cx+120*sc},{cy-10*sc} {cx+150*sc},{cy+120*sc} Z"/>'
         f'<path d="M{cx-45*sc},{cy-100*sc} Q{cx-120*sc},{cy-170*sc} {cx-150*sc},{cy-90*sc} Q{cx-110*sc},{cy-130*sc} {cx-40*sc},{cy-80*sc} Z"/>'
         f'<path d="M{cx+45*sc},{cy-100*sc} Q{cx+120*sc},{cy-170*sc} {cx+150*sc},{cy-90*sc} Q{cx+110*sc},{cy-130*sc} {cx+40*sc},{cy-80*sc} Z"/>')
    eyes = f'<path d="M{cx-34*sc},{cy-62*sc} l22,6 l-22,4 Z M{cx+34*sc},{cy-62*sc} l-22,6 l22,4 Z" fill="#5d6577"/>'
    return f'<g opacity=".62" filter="url(#ghost)"><g filter="url(#rel)" fill="#dfe2e8">{d}</g></g><g opacity=".7">{eyes}</g>'

def emperor(x, foot, sc=1.0, lance_to=None):
    g = (f'<path d="M{x-46*sc},{foot} L{x-22*sc},{foot-120*sc} Q{x},{foot-138*sc} {x+22*sc},{foot-120*sc} L{x+56*sc},{foot} Z"/>'
         f'<ellipse cx="{x}" cy="{foot-150*sc}" rx="{15*sc}" ry="{17*sc}"/>'
         f'<path d="M{x-20*sc},{foot-196*sc} l8,-16 l8,12 l8,-16 l8,16 l8,-12 l8,16 Z"/>')
    if lance_to:
        lx, ly = lance_to
        hx, hy = x - 24 * sc, foot - 104 * sc
        ang = math.atan2(ly - hy, lx - hx)
        px, py = -math.sin(ang) * 4, math.cos(ang) * 4
        g += (f'<path d="M{hx+px},{hy+py} L{lx+px},{ly+py} L{lx-px},{ly-py} L{hx-px},{hy-py} Z"/>'
              f'<path d="M{lx},{ly} L{lx+math.cos(ang)*34 + px*3},{ly+math.sin(ang)*34 + py*3} L{lx+math.cos(ang)*34 - px*3},{ly+math.sin(ang)*34 - py*3} Z" transform="rotate(180 {lx} {ly})"/>')
    glow = f'<circle cx="{x}" cy="{foot-150*sc}" r="{26*sc}" fill="#ffffff" opacity=".9" filter="url(#ghost)"/>'
    return f'<g filter="url(#rel)" fill="#e6e9ee">{g}</g>{glow}'

def hands(cx, top):
    g = []
    for side in (-1, 1):
        x = cx + side * 95
        g.append(f'<path d="M{x-side*80},{top+40} Q{x},{top+130} {x+side*90},{top+60} L{x+side*120},{top+190} Q{x},{top+250} {x-side*110},{top+180} Z"/>')
        for k in range(4):
            fx = x - side * 70 + side * k * 32
            g.append(f'<rect x="{fx-11}" y="{top+10+abs(k-1.5)*10}" width="22" height="70" rx="11"/>')
    return f'<g filter="url(#rel)" fill="#eceef2">{"".join(g)}</g>'

def keeper(x, foot):
    g = (f'<path d="M{x-70},{foot} Q{x-80},{foot-90} {x-30},{foot-120} Q{x},{foot-130} {x+30},{foot-112} L{x+60},{foot-40} L{x+80},{foot} Z"/>'
         f'<ellipse cx="{x-10}" cy="{foot-150}" rx="20" ry="22"/>'
         f'<path d="M{x+10},{foot-110} Q{x+60},{foot-130} {x+70},{foot-90} Q{x+40},{foot-82} {x+10},{foot-92} Z"/>')
    flame = f'<path d="M{x+45},{foot-175} Q{x+70},{foot-140} {x+58},{foot-118} Q{x+45},{foot-106} {x+32},{foot-118} Q{x+22},{foot-140} {x+45},{foot-175} Z" fill="#ffffff"/>'
    return f'<g filter="url(#rel)" fill="#e2e5ea">{g}</g><g filter="url(#ghost)" opacity=".9">{flame}</g>'

def dragon(cx, cy):
    g = (f'<path d="M{cx-200},{cy+80} Q{cx-150},{cy-40} {cx-20},{cy-20} Q{cx+80},{cy-10} {cx+110},{cy-70} L{cx+170},{cy-60} Q{cx+140},{cy+10} {cx+60},{cy+40} Q{cx+180},{cy+70} {cx+150},{cy+110} Q{cx-60},{cy+140} {cx-200},{cy+80} Z"/>'
         f'<path d="M{cx+120},{cy-70} L{cx+120},{cy-130} L{cx+140},{cy-74} Z M{cx+150},{cy-66} L{cx+170},{cy-120} L{cx+165},{cy-62} Z"/>')
    blade = f'<path d="M{cx+132},{cy-150} L{cx+142},{cy-148} L{cx+146},{cy-64} L{cx+136},{cy-64} Z"/>'
    return f'<g filter="url(#rel)" fill="#dde1e7">{g}</g><g filter="url(#rel)" fill="#f2f4f7">{blade}</g>'

def write(name, w, h, body, **kw):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        f.write(svg(w, h, body, **kw))

# ---------- 月银纪 ----------
W = 1600
L = slab(W, 34, 352) + towers(800, 275) + crowd(560, 1040, 330, 21) + demon(250, 210, 0.95) + emperor(1400, 330, 1.0, lance_to=(1060, 150))
L += label(250, 26, '左上 魔神的虚影') + label(800, 26, '正中 浮塔与各族、魔族') + label(1360, 26, '右上 凯尔萨斯·贯穹遥指（脸在光里）')
write('moon_lintel.svg', W, 360, L)
B = slab(W, 30, 410, ledge_top=False) + hands(800, 70) + dragon(330, 230) + keeper(1330, 360)
B += label(330, 392, '左下 无冠之龙焚原·断刃楔进龙颅（倾向）', fill='#3a4152') + label(800, 392, '正中 正神的一双手（只刻手）', fill='#3a4152') + label(1330, 392, '右下 希尔妲双手护火', fill='#3a4152')
write('moon_base.svg', W, 420, B)

def niche_col(w, h, items, lab):
    g = []
    step = h / len(items)
    for i, it in enumerate(items):
        y0 = i * step
        g.append(f'<rect x="6" y="{y0+8}" width="{w-12}" height="{step-16}" rx="{(w-12)/2}" fill="#cfd3da"/>')
    body = f'<g filter="url(#rel)">{"".join(g)}</g>'
    inner = []
    for i, it in enumerate(items):
        cy = i * step + step / 2
        inner.append(it(w / 2, cy))
    body += f'<g filter="url(#rel)" fill="#eef0f3">{"".join(inner)}</g>'
    return body

def beast_horn(x, y):
    return f'<path d="M{x-18},{y+30} Q{x-20},{y-4} {x},{y-10} Q{x+20},{y-4} {x+18},{y+30} Z M{x-10},{y-8} Q{x-26},{y-40} {x-6},{y-48} Q{x-16},{y-30} {x-4},{y-12} Z M{x+10},{y-8} Q{x+26},{y-40} {x+6},{y-48} Q{x+16},{y-30} {x+4},{y-12} Z"/>'
def beast_tusk(x, y):
    return f'<path d="M{x-22},{y-20} Q{x},{y-40} {x+22},{y-20} L{x+20},{y+24} Q{x},{y+34} {x-20},{y+24} Z M{x-6},{y+20} Q{x-4},{y+52} {x+4},{y+56} Q{x+2},{y+40} {x+6},{y+20} Z"/>'
def winged_horse(x, y):
    return f'<path d="M{x-20},{y+30} L{x-16},{y-10} Q{x-8},{y-30} {x+8},{y-34} L{x+14},{y-26} L{x+4},{y-14} L{x+12},{y+30} Z M{x-6},{y-6} Q{x-30},{y-40} {x-22},{y-56} Q{x-10},{y-30} {x+2},{y-14} Z"/>'
def hero_sword(x, y):
    return person(x, y + 40, 0.8, arm='up')
def hero_bow(x, y):
    return person(x, y + 40, 0.8) + f'<path d="M{x+16},{y-30} Q{x+34},{y-6} {x+16},{y+20}" fill="none" stroke="#eef0f3" stroke-width="4"/>'
def hero_spear(x, y):
    return person(x, y + 40, 0.8) + f'<rect x="{x+14}" y="{y-56}" width="4" height="96" rx="2"/>'

write('moon_pillar_l.svg', 80, 600, niche_col(80, 600, [beast_horn, beast_tusk, winged_horse], ''), b=2, s=4)
write('moon_pillar_r.svg', 80, 600, niche_col(80, 600, [hero_sword, hero_bow, hero_spear], ''), b=2, s=4)

# 两翼（宽屏）：左 万兽的原野，右 城与塔、传奇
def wing_left():
    g = ['<path d="M0,2000 L0,1300 L160,1080 L300,1260 L470,960 L660,1240 L860,1100 L900,1150 L900,2000 Z" fill="#d6dae1"/>']
    for (x, y, s) in ((260, 900, 2.2), (620, 700, 1.6), (420, 1500, 2.6)):
        g.append(f'<g transform="translate({x},{y}) scale({s})">{beast_horn(0,0)}{beast_tusk(60,40)}</g>')
    return f'<g filter="url(#rel)" fill="#e3e6eb">{"".join(g)}</g>' + label(450, 120, '左翼 万兽的原野（宽屏才有）', 34)
def wing_right():
    g = []
    for i, (x, hh) in enumerate(((150, 900), (330, 1200), (520, 980), (700, 1350))):
        g.append(f'<path d="M{x-50},2000 L{x-50},{2000-hh} L{x},{2000-hh-90} L{x+50},{2000-hh} L{x+50},2000 Z"/>')
    for x in (180, 360, 540, 720):
        g.append(f'<g transform="translate({x},1990) scale(2.4)">{person(0,0,1,arm="up" if x%360==0 else None)}</g>')
    return f'<g filter="url(#rel)" fill="#e3e6eb">{"".join(g)}</g>' + label(450, 120, '右翼 诸国与帝国的城，传奇站在城下', 34)
write('moon_wing_l.svg', 900, 2000, wing_left(), b=4, s=7)
write('moon_wing_r.svg', 900, 2000, wing_right(), b=4, s=7)

# ---------- 另三纪：只摆主景与字，看位置和色板 ----------
def wall(cx, base):
    g = [f'<rect x="{cx-560}" y="{base-120}" width="1120" height="120"/>']
    for i in range(28):
        g.append(f'<rect x="{cx-560+i*40}" y="{base-150}" width="24" height="34"/>')
    g.append(f'<path d="M{cx-40},{base-210} Q{cx},{base-250} {cx+40},{base-210} L{cx+30},{base-150} L{cx-30},{base-150} Z"/>')
    return f'<g filter="url(#rel)" fill="#e6e8ec">{"".join(g)}</g>'
def stone_sword(cx, base):
    g = (f'<path d="M{cx-150},{base} Q{cx-120},{base-90} {cx},{base-100} Q{cx+120},{base-90} {cx+150},{base} Z"/>'
         f'<rect x="{cx-9}" y="{base-230}" width="18" height="150" rx="4"/>'
         f'<rect x="{cx-60}" y="{base-236}" width="120" height="14" rx="6"/><rect x="{cx-11}" y="{base-276}" width="22" height="44" rx="8"/>')
    hands = ''.join(f'<ellipse cx="{cx-70+k*20}" cy="{base-150+abs(k-3)*6}" rx="9" ry="14"/>' for k in range(7) if k != 3)
    return f'<g filter="url(#rel)" fill="#e6e8ec">{g}{hands}</g>'
def well(cx, base):
    g = (f'<ellipse cx="{cx}" cy="{base-40}" rx="260" ry="46"/>'
         f'<rect x="{cx-3}" y="{base-250}" width="6" height="210"/>')
    for i, dx in enumerate((-300, -200, -100, 0, 100, 200, 300)):
        g += f'<path d="M{cx+dx-14},{base-170} L{cx+dx-14},{base-230} L{cx+dx},{base-256} L{cx+dx+14},{base-230} L{cx+dx+14},{base-170} Z"/>'
    ring = f'<ellipse cx="{cx}" cy="{base-250}" rx="360" ry="34" fill="none" stroke="#e6e8ec" stroke-width="8"/>'
    return f'<g filter="url(#rel)" fill="#e6e8ec">{g}{ring}</g>'
def pillars(cx, top):
    g = ''.join(f'<rect x="{cx-300+i*100-20}" y="{top}" width="40" height="300" rx="8"/>' for i in range(7))
    g += f'<rect x="{cx-360}" y="{top-10}" width="720" height="24" rx="8"/>'
    return f'<g filter="url(#rel)" fill="#e9ebef">{g}</g>'
def mech_hands(cx, top):
    g = []
    for side in (-1, 1):
        x = cx + side * 110
        g.append(f'<path d="M{x-side*90},{top+40} L{x+side*100},{top+60} L{x+side*120},{top+200} L{x-side*110},{top+190} Z"/>')
        for k in range(4):
            g.append(f'<rect x="{x - side*75 + side*k*34 - 12}" y="{top}" width="24" height="64" rx="3"/>')
    return f'<g filter="url(#rel)" fill="#e6e8ec">{"".join(g)}</g>'
def cradle(cx, top):
    g = (f'<path d="M{cx-150},{top+70} Q{cx},{top+200} {cx+150},{top+70} Z"/>'
         f'<path d="M{cx-230},{top+60} Q{cx-170},{top+150} {cx-110},{top+120} L{cx-120},{top+230} L{cx-260},{top+220} Z M{cx+230},{top+60} Q{cx+170},{top+150} {cx+110},{top+120} L{cx+120},{top+230} L{cx+260},{top+220} Z"/>'
         f'<path d="M{cx+190},{top-40} Q{cx+210},{top} {cx+198},{top+20} Q{cx+190},{top+28} {cx+182},{top+20} Q{cx+172},{top} {cx+190},{top-40} Z" fill="#ffffff"/>')
    return f'<g filter="url(#rel)" fill="#e6e8ec">{g}</g>'

ERAS = {
  'strife': (wall, mech_hands, ['左上 高座上的魔神（不刻脸）', '正中 长垒的垛口与挂上墙的号角', '右上 诺伦举剑（不摘盔）'],
             ['左下 塔妮丝拉开骨弓', '正中 擎天级跪着，一双铁手托起', '右下 辛美尔小队的背影']),
  'bronze': (stone_sword, cradle, ['左上 巴尔缇娜（黑曜那一半）', '正中 破晓插在石里，十四只手', '右上 索恩薇娅提着挽昼（白石那一半）'],
             ['左下 插着的兵器（剑碑）', '正中 人的手捧着篮子与门洞火', '右下 插着的兵器（剑碑）']),
  'maze': (well, pillars, ['左上 巴尔缇娜立在井口西沿', '正中 井口与绳，远处天上的环和七座浮塔', '右上 索恩薇娅立在井口东沿'],
           ['左下 雾门', '正中 七支柱托起', '右下 雾门']),
}
for era, (top_fn, base_fn, tl, bl) in ERAS.items():
    L = slab(W, 34, 352) + top_fn(800, 300)
    L += label(250, 26, tl[0]) + label(800, 26, tl[1]) + label(1360, 26, tl[2])
    write(f'{era}_lintel.svg', W, 360, L)
    B = slab(W, 30, 410, ledge_top=False) + base_fn(800, 80)
    B += label(330, 392, bl[0], fill='#3a4152') + label(800, 392, bl[1], fill='#3a4152') + label(1330, 392, bl[2], fill='#3a4152')
    write(f'{era}_base.svg', W, 420, B)
print('ok', sorted(os.listdir(OUT)))
