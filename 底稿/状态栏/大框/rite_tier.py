# 超凡演出第三稿（11-10，用户：“演出效果也可以做的动态一些……这一块演出要专门给active和special的主动使用做的华丽一些来体现与普通运用，
# skill判定和art发动运用的区别，特效与动态也要体现出能力位阶（epic，legend，unique）的差异”）
# 类（data-c，记录里「类·稀有度」那一栏的前半）：
#   Skill（技能判定）——一条细条，打勾打叉，不起手
#   Art（照一门技艺的路数出手）——横幅收一号、不闪光；起手框（不该写，写了也认）收小，不放粒子
#   Active（主动的招和术，旧写法也算这一类）——起手框聚光、转进来、放一圈光；横幅砸进来、一下闪光、几道速度线
#   Special（命星主动的那一截）——在 Active 上再大一号，两道边，一颗大星，签上写 ✦
# 稀有度（data-r，后半）：Rare 一道蓝边；Epic 紫边、外头一层光、隔一阵扫过一道紫光；Legend 金边、金光、往上飘的火星、名字一道金光来回走；
#   Unique 七彩的边一直换颜色、放出去那一下整框一白、震一下、名字七彩
# 颜色照面板的品阶（modules_css.QUAL）：Rare #4f8fd8，Epic #a06be0，Legend #e0a63c，Unique #e25a4e
R = '.rili-markdown-renderer:has(.sz-hud)'


def _is(attr, names):
    return ':is(%s)' % ','.join('[%s="%s"]' % (attr, n) for n in names)


ACTIVE = _is('data-c', ['Active', '主动', ''])
SPECIAL = _is('data-c', ['Special', '命星'])
ART = _is('data-c', ['Art', '技艺'])
SKILL = _is('data-c', ['Skill', '技能'])
LOW = _is('data-r', ['Common', 'Normal', 'Uncommon', '普通', '精良'])
RARE = _is('data-r', ['Rare', '稀有'])
EPIC = _is('data-r', ['Epic', '史诗'])
LEGEND = _is('data-r', ['Legend', 'Legendary', '传说', '传奇'])
UNIQUE = _is('data-r', ['Unique', '唯一', '独有', '神话'])
HIGH = ':is(%s,%s,%s)' % (EPIC, LEGEND, UNIQUE)
QC = [(LOW, '#9aa0aa'), (RARE, '#4f8fd8'), (EPIC, '#a06be0'), (LEGEND, '#e0a63c'), (UNIQUE, '#e25a4e')]
PRISM = '#ff6b5a, #ffd36e, #fff6d0, #7fd0ff, #c08cff, #ff6b5a'
NAME_LEGEND = 'linear-gradient(100deg, #fff4cf 0%, var(--qc) 25%, #fff4cf 50%, var(--qc) 75%, #fff4cf 100%) 0 0/220% 100%'
NAME_UNIQUE = 'linear-gradient(100deg, #ffe2d8 0%, #ff6b5a 18%, #ffd36e 36%, #ffffff 50%, #7fd0ff 64%, #c08cff 82%, #ffe2d8 100%) 0 0/240% 100%'

KEYFRAMES = '''@keyframes sz-rt-enter{from{opacity:0;transform:translateY(10px) scale(.97)}to{opacity:1;transform:none}}
@keyframes sz-rt-spinin{0%{opacity:0;transform:scale(.25) rotate(-200deg)}60%{opacity:1;transform:scale(1.12) rotate(10deg)}100%{opacity:1;transform:none}}
@keyframes sz-rt-gather{0%{opacity:0;transform:scale(2.8) rotate(-60deg)}25%{opacity:1}100%{opacity:0;transform:scale(.3) rotate(0)}}
@keyframes sz-rt-ring{0%{opacity:.95;transform:scale(.7)}100%{opacity:0;transform:scale(2.6)}}
@keyframes sz-rt-shim{0%{background-position:100% 0}55%,100%{background-position:0 0}}
@keyframes sz-rt-embers{from{background-position:0 0}to{background-position:0 -64px}}
@keyframes sz-rt-sheen{from{background-position:0 0}to{background-position:100% 0}}
@keyframes sz-rt-hue{to{filter:hue-rotate(360deg)}}
@keyframes sz-rt-flash{0%{opacity:0}12%{opacity:1}100%{opacity:0}}
@keyframes sz-rt-shake{0%,100%{transform:none}15%{transform:translate(-4px,1px)}35%{transform:translate(4px,-1px)}55%{transform:translate(-3px,0)}75%{transform:translate(2px,1px)}}
@keyframes sz-rt-star{0%,100%{transform:translateY(-50%) rotate(0) scale(.92)}50%{transform:translateY(-50%) rotate(18deg) scale(1.06)}}
@keyframes sz-wz-in{0%{opacity:0;transform:translateX(-42px) skewX(-14deg)}65%{opacity:1;transform:translateX(5px) skewX(3deg)}100%{opacity:1;transform:none}}
@keyframes sz-wz-lite{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:none}}
@keyframes sz-wz-hit{0%{opacity:0;background-position:0 0, -90px 0}18%{opacity:1}100%{opacity:0;background-position:0 0, 90px 0}}'''


def css():
    out = ['/* ==== 11-10 超凡演出第三稿（rite_tier.py）：类分演法，稀有度分华丽的程度 ==== */', KEYFRAMES]
    w = out.append
    # ---------- 起手框：几样共用的零件 ----------
    w(R + ''' .rt-pt{position:absolute;left:16px;top:50%;z-index:2;width:76px;height:76px;margin-top:-38px;pointer-events:none;--pc:color-mix(in srgb, var(--rc) 55%, #fff);'''
      '''background:radial-gradient(circle at 50% 4%, var(--pc) 0 2px, transparent 3px), radial-gradient(circle at 96% 50%, var(--pc) 0 2px, transparent 3px), radial-gradient(circle at 50% 96%, var(--pc) 0 2px, transparent 3px), radial-gradient(circle at 4% 50%, var(--pc) 0 2px, transparent 3px), '''
      '''radial-gradient(circle at 18% 18%, var(--pc) 0 1.5px, transparent 2.5px), radial-gradient(circle at 82% 18%, var(--pc) 0 1.5px, transparent 2.5px), radial-gradient(circle at 82% 82%, var(--pc) 0 1.5px, transparent 2.5px), radial-gradient(circle at 18% 82%, var(--pc) 0 1.5px, transparent 2.5px);'''
      '''animation:sz-rt-gather .95s cubic-bezier(.5,0,.8,.6) .05s both}''')
    w(R + ' .rt-bd::after{content:"";position:absolute;inset:4px;border-radius:50%;border:2px solid color-mix(in srgb, var(--rc) 75%, #fff);opacity:0;animation:sz-rt-ring 1.1s ease-out .95s both}')
    w(R + ' .rt-fl{position:absolute;inset:0;z-index:2;pointer-events:none;opacity:0}')
    w(R + ' .rt-st{display:none}')
    w(R + ' .rt-q{position:absolute;right:12px;top:10px;z-index:3;display:none;padding:1px 8px;border-radius:999px;font-size:10px;letter-spacing:.1em;line-height:1.6;color:var(--qc);background:rgb(0 0 0 / .28);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--qc) 65%, transparent)}')
    w(R + ' .rt-q:not([data-c=""]){display:block}')
    w(R + ' .rt-q::before{content:attr(data-c)}')
    w(R + ' .rt-q:not([data-r=""])::after{content:" · " attr(data-r)}')
    # ---------- 横幅：几样共用的零件。Active 和旧写法砸进来，一下闪光、几道速度线 ----------
    w(R + ' .sz-waza{box-shadow:inset 0 0 0 1px var(--wql, transparent), var(--wqg, inset 0 0 0 transparent);animation:sz-wz-in .5s cubic-bezier(.2,1.1,.3,1) both}')
    w(R + ' .wz-fx{position:absolute;inset:0;pointer-events:none;opacity:0;background:radial-gradient(ellipse 26% 95% at 10% 50%, rgb(255 255 255 / .75), transparent 70%), '
      'repeating-linear-gradient(100deg, transparent 0 22px, color-mix(in srgb, var(--wc) 32%, transparent) 22px 24px);animation:sz-wz-hit .7s ease-out .3s both}')
    w(R + ' :is(.wz-em,.wz-st){display:none}')
    w(R + ' .wz-q{display:none;margin-right:8px;padding:0 7px;border-radius:999px;font-style:normal;font-size:10px;letter-spacing:.08em;color:var(--qc, #e9cf8a);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--qc, #e9cf8a) 65%, transparent)}')
    w(R + ' .wz-q:not([data-c=""]){display:inline-block}')
    w(R + ' .wz-q::before{content:attr(data-c)}')
    w(R + ' .wz-q:not([data-r=""])::after{content:" · " attr(data-r)}')
    # ---------- 类 ----------
    # Skill：技能判定，一条细条，前头一个记号，判成了打勾、没成打叉，大成功一颗星
    w(R + ' .sz-waza%s{display:flex;align-items:baseline;flex-wrap:wrap;column-gap:10px;row-gap:2px;max-width:560px;margin:10px auto;padding:7px 16px 7px 40px;clip-path:none;border-radius:999px;'
          'background:color-mix(in srgb, var(--okc, var(--wc)) 14%%, var(--wsb, rgb(10 10 24 / .55)))!important;'
          'box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--okc, var(--wc)) 45%%, transparent);animation:sz-wz-lite .3s ease-out both}' % SKILL)
    w(R + ' .sz-waza%s::before{content:var(--okm, "◇");left:14px;top:50%%;transform:translateY(-50%%);font-size:15px;font-weight:700;opacity:1;color:var(--okc, var(--wc));text-shadow:none}' % SKILL)
    w(R + ' .sz-waza%s::after,%s .sz-waza%s :is(.wz-fx,.wz-em,.wz-st){display:none}' % (SKILL, R, SKILL))
    w(R + ' .sz-waza%s .wz-who{font-size:11px}' % SKILL)
    w(R + ' .sz-waza%s .wz-n{font-size:14px!important;font-weight:700!important;letter-spacing:.06em;text-shadow:none}' % SKILL)
    w(R + ' .sz-waza%s .wz-k{padding:0;font-size:10.5px}' % SKILL)
    w(R + ' .sz-waza%s .wz-d{margin:0;font-size:12.5px}' % SKILL)
    for ok, col, mark in [('成功', '#6fd39a', '✓'), ('失败', '#e0574a', '✗'), ('大成功', '#ffd36e', '★'), ('大失败', '#b3261e', '✗')]:
        w('%s .sz-waza[data-ok="%s"]{--okc:%s;--okm:"%s"}' % (R, ok, col, mark))
    # Art：照一门技艺的路数出手，横幅收一号，不闪光
    w(R + ' .sz-waza%s{padding:9px 22px 9px 62px;margin:12px -2px;animation:sz-wz-lite .35s ease-out both}' % ART)
    w(R + ' .sz-waza%s::before{font-size:40px;opacity:.38}' % ART)
    w(R + ' .sz-waza%s .wz-n{font-size:18px!important}' % ART)
    w(R + ' .sz-waza%s :is(.wz-fx,.wz-st){display:none}' % ART)
    # Art、Skill 写了起手的：框收小，纹样不转进来，不放粒子和光圈
    w(R + ' .sz-rite:is(%s,%s){padding:12px 18px 10px 82px;animation-duration:.35s}' % (ART, SKILL))
    w(R + ' .sz-rite:is(%s,%s) :is(.rt-c,.rt-bd){left:12px;width:54px;height:54px;margin-top:-27px}' % (ART, SKILL))
    w(R + ' .sz-rite:is(%s,%s) :is(.rt-pt,.rt-fx,.rt-fl,.rt-st){display:none}' % (ART, SKILL))
    w(R + ' .sz-rite:is(%s,%s) .rt-bd::after{display:none}' % (ART, SKILL))
    w(R + ' .sz-rite:is(%s,%s) .rt-c{animation:var(--rca)}' % (ART, SKILL))
    w(R + ' .sz-rite:is(%s,%s) .rt-n{font-size:16px!important;margin-top:4px}' % (ART, SKILL))
    # Special：命星主动的那一截，起手框和横幅都大一号，两道边，一颗大星慢慢转，签上写 ✦
    w(R + ' .sz-rite%s{padding-top:20px;padding-bottom:18px;--qline:var(--qc);--qdbl:inset 0 0 0 5px color-mix(in srgb, var(--qc) 45%%, transparent);--qglow:0 0 26px color-mix(in srgb, var(--qc) 32%%, transparent)}' % SPECIAL)
    w(R + ' .sz-rite%s .rt-st{display:block;position:absolute;right:18px;top:50%%;z-index:0;font-size:96px;line-height:1;background:radial-gradient(circle, #fff 0, color-mix(in srgb, var(--qc, #e9cf8a) 80%%, #fff) 22%%, var(--qc, #e9cf8a) 46%%, transparent 72%%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 10px var(--qc, #e9cf8a));opacity:.42;transform:translateY(-50%%);pointer-events:none;animation:sz-rt-star 5s ease-in-out 1.2s infinite}' % SPECIAL)
    w(R + ' .sz-rite%s .rt-st::before{content:"✦"}' % SPECIAL)
    w(R + ' .sz-rite%s .rt-n{font-size:22px!important}' % SPECIAL)
    w(R + ' :is(.rt-q,.wz-q)%s::before{content:"✦ " attr(data-c)}' % SPECIAL)
    w(R + ' .sz-waza%s{padding:16px 30px 16px 84px;--wql:var(--qc, #e9cf8a);--wqg:inset 0 0 22px color-mix(in srgb, var(--qc, #e9cf8a) 30%%, transparent)}' % SPECIAL)
    w(R + ' .sz-waza%s::before{font-size:66px;opacity:.6}' % SPECIAL)
    w(R + ' .sz-waza%s .wz-n{font-size:26px!important}' % SPECIAL)
    w(R + ' .sz-waza%s .wz-st{display:block;position:absolute;right:12px;top:50%%;z-index:-1;font-size:70px;line-height:1;font-style:normal;background:radial-gradient(circle, #fff 0, color-mix(in srgb, var(--qc, #e9cf8a) 80%%, #fff) 22%%, var(--qc, #e9cf8a) 46%%, transparent 72%%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 10px var(--qc, #e9cf8a));opacity:.34;transform:translateY(-50%%);pointer-events:none;animation:sz-rt-star 5s ease-in-out 1s infinite}' % SPECIAL)
    w(R + ' .sz-waza%s .wz-st::before{content:"✦"}' % SPECIAL)
    # ---------- 稀有度 ----------
    for sel, col in QC:
        w('%s :is(.sz-rite,.sz-waza)%s{--qc:%s}' % (R, sel, col))
    # Rare：一道蓝边
    w(R + ' .sz-rite%s{--qline:color-mix(in srgb, var(--qc) 80%%, transparent)}' % RARE)
    w(R + ' .sz-waza%s{--wql:color-mix(in srgb, var(--qc) 70%%, transparent)}' % RARE)
    # Epic 往上：边换成那一档的颜色，外头一层光，横幅扫过去的那道光也换颜色
    w(R + ' .sz-rite%s{--qline:var(--qc);--qglow:0 0 18px color-mix(in srgb, var(--qc) 40%%, transparent)}' % EPIC)
    w(R + ' .sz-rite%s{--qline:var(--qc);--qglow:0 0 30px color-mix(in srgb, var(--qc) 50%%, transparent)}' % LEGEND)
    w(R + ' .sz-rite%s{--qline:transparent;--qglow:0 0 36px color-mix(in srgb, var(--qc) 55%%, transparent)}' % UNIQUE)
    w(R + ' .sz-waza%s{--wql:var(--qc);--wqg:inset 0 0 18px color-mix(in srgb, var(--qc) 30%%, transparent)}' % HIGH)
    w(R + ' .sz-waza%s::after{background:linear-gradient(100deg, transparent 35%%, color-mix(in srgb, var(--qc) 40%%, transparent) 48%%, transparent 60%%) 0 0/260%% 100%% no-repeat}' % HIGH)
    # Epic、Legend：隔一阵从框上扫过一道光
    w(R + ' .sz-rite:is(%s,%s)::before{content:"";position:absolute;inset:0;z-index:2;pointer-events:none;background:linear-gradient(115deg, transparent 42%%, color-mix(in srgb, var(--qc) 30%%, transparent) 50%%, transparent 58%%) 0 0/300%% 100%% no-repeat;animation:sz-rt-shim 5s ease-in-out 1.3s infinite}' % (EPIC, LEGEND))
    # Legend、Unique：往上飘的火星，名字一道光来回走
    EMB = ('background-image:radial-gradient(circle at 14% 30%, var(--qc) 0 1.3px, transparent 2.2px), radial-gradient(circle at 38% 75%, color-mix(in srgb, var(--qc) 70%, #fff) 0 1px, transparent 2px), '
           'radial-gradient(circle at 63% 18%, var(--qc) 0 1.2px, transparent 2px), radial-gradient(circle at 87% 62%, color-mix(in srgb, var(--qc) 70%, #fff) 0 1.4px, transparent 2.3px);background-size:100% 64px;animation:sz-rt-embers 2.6s linear infinite')
    w(R + ' .sz-rite:is(%s,%s)::after{content:"";position:absolute;inset:0;z-index:1;pointer-events:none;%s}' % (LEGEND, UNIQUE, EMB))
    w(R + ' .sz-waza:is(%s,%s) .wz-em{display:block;position:absolute;inset:0;pointer-events:none;%s}' % (LEGEND, UNIQUE, EMB))
    for sel, grad, dur in [(LEGEND, NAME_LEGEND, '2.8s'), (UNIQUE, NAME_UNIQUE, '2.2s')]:
        w('%s .sz-rite%s .rt-n,%s .sz-waza%s .wz-n{background:%s;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;text-shadow:none!important;'
          'filter:drop-shadow(0 0 7px color-mix(in srgb, var(--qc) 60%%, transparent))}' % (R, sel, R, sel, grad))
        w('%s .sz-rite%s .rt-n{animation:var(--rn-a), sz-rt-sheen %s ease-in-out 1.5s infinite alternate}' % (R, sel, dur))
        w('%s .sz-waza%s .wz-n{animation:sz-rt-sheen %s ease-in-out .6s infinite alternate}' % (R, sel, dur))
    # Unique：七彩的边一直换颜色；放出去那一下整框一白，震一下；粒子是白的
    w(R + ' .sz-rite%s::before{content:"";position:absolute;inset:0;z-index:3;pointer-events:none;border-radius:12px;padding:2px;background:conic-gradient(from 210deg, %s);'
          '-webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;animation:sz-rt-hue 4s linear infinite}' % (UNIQUE, PRISM))
    w(R + ' .sz-rite%s .rt-fl{background:radial-gradient(circle at 54px 50%%, #fff 0, rgb(255 255 255 / .7) 14%%, transparent 62%%);animation:sz-rt-flash 1s ease-out .9s both}' % UNIQUE)
    w(R + ' .sz-rite%s{animation:sz-rt-enter .55s cubic-bezier(.2,.9,.3,1) both, sz-rt-shake .42s linear 1s}' % UNIQUE)
    w(R + ' .sz-rite%s .rt-pt{--pc:#fff}' % UNIQUE)
    w(R + ' .sz-rite%s .rt-bd{animation-duration:24s}' % UNIQUE)
    w(R + ' .sz-waza%s .wz-em::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg, %s) top/100%% 2px no-repeat, linear-gradient(90deg, %s) bottom/100%% 2px no-repeat;animation:sz-rt-hue 4s linear infinite}' % (UNIQUE, PRISM, PRISM))
    w(R + ' .sz-waza%s .wz-fx{background:radial-gradient(ellipse 60%% 140%% at 18%% 50%%, #fff, rgb(255 255 255 / .5) 30%%, transparent 72%%), repeating-linear-gradient(100deg, transparent 0 16px, rgb(255 255 255 / .35) 16px 18px)}' % UNIQUE)
    w(R + ' .sz-waza%s{animation:sz-wz-in .5s cubic-bezier(.2,1.1,.3,1) both, sz-rt-shake .4s linear .5s}' % UNIQUE)
    # 前传的羊皮纸上金字、七彩字看不清，名字照旧是墨色，光和边照样有
    pre = '.rili-markdown-renderer:has(.era-pre)'
    w('%s :is(.sz-rite,.sz-waza):is(%s,%s) :is(.rt-n,.wz-n){background:none;-webkit-text-fill-color:currentColor;filter:none}' % (pre, LEGEND, UNIQUE))
    w('%s{--wsb:rgb(255 248 230 / .7)}' % pre)
    w('%s .rt-q{background:rgb(255 250 238 / .55)}' % pre)
    # 手机
    w('@media (max-width:639px){%s .sz-waza{grid-template-columns:minmax(0,1fr)}%s .sz-waza .wz-k{justify-self:start;padding-bottom:0;margin-top:2px}}' % (R, R))   # 手机上名字一行，签和路挪到名字底下
    w('@media (max-width:639px){%s .sz-waza%s{padding:12px 20px 12px 64px}%s .sz-waza%s::before{font-size:50px}%s .sz-waza%s .wz-n{font-size:21px!important}%s .sz-waza%s .wz-st{font-size:52px;right:16px}'
      '%s .sz-rite%s .rt-st{font-size:70px;right:10px}%s .sz-rite%s .rt-n{font-size:19px!important}%s .sz-rite:is(%s,%s){padding-left:72px}%s .sz-rite:is(%s,%s) :is(.rt-c,.rt-bd){left:10px;width:48px;height:48px;margin-top:-24px}}'
      % (R, SPECIAL, R, SPECIAL, R, SPECIAL, R, SPECIAL, R, SPECIAL, R, SPECIAL, R, ART, SKILL, R, ART, SKILL))
    # 减少动画：全停，停在放完的样子
    w('@media (prefers-reduced-motion:reduce){%s :is(.sz-rite,.sz-waza,.rt-pt,.rt-fl,.rt-st,.wz-fx,.wz-em,.wz-st){animation:none!important}%s :is(.sz-rite,.sz-waza)::before,%s :is(.sz-rite,.sz-waza)::after,%s :is(.rt-bd,.wz-em)::before,%s :is(.rt-bd,.wz-em)::after{animation:none!important}%s :is(.rt-pt,.rt-fl,.wz-fx){display:none!important}}'
      % (R, R, R, R, R, R))
    return '\n'.join(out)


if __name__ == '__main__':
    print(len(css()))
