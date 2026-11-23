# 命星页（状态栏第三轮，11-23）。用户：“命星页的信息也可以更详细（ability每个熟练度等级能达成什么，没达成的灰着，达成了的亮着，
# 命路进阶要求和进度，更好更直观的各种信息显示）”。方向稿第四节第 3 条、样张 m3 是底子，画在现成的「成长与伟业」那一页上。
#
# 做法：
# - 页上原来就有的东西不拆：七境一条路、斩过、技能书（书签一类一页，左页一枚一枚，右页是选中那一枚）都留着，书签和右页怎么翻照旧（modules_css.tables）。
# - 进阶（RULES_UP，插在「伟业·目标」前头）：§伟业｜伟业 那一行拆成一块进阶牌（头上此刻的位阶、下一境、候选称号，底下等级、这一道门槛、蓄势、伟业簿、英雄阶段各一格），
#   §伟业｜职业 那一行画成四个节点；凡极以后位阶那一行带神力的，另出一条神力的台阶。对不上的那一行照旧落到原来的「伟业·目标」「伟业·职业」上。
# - 技能书里头（RULES_AB，插在「能力」前头）：Art 一门一条五个节点的线，Skill 五格熟练度，别的一枚一张小卡；数那一栏照 · 拆成小标。
#   壳照旧是 .sz-it.sz-ab（data-c、data-q、data-n）、.sz-face、.sz-tip，书签筛哪一类、右页摆哪一枚的样式一行不用改。
# - 记录行只添两小栏，都可以不写：Art 行末尾 `｜招 一阶的招、二阶的招、…`（五个，学到的写招名，没到的写要什么才解锁），
#   Skill 行末尾 `｜下一档 一句`。不写的照旧画得出来（只有五个节点、没有下一档那一行）。
import sys
import os
from urllib.parse import quote

sys.dont_write_bytecode = True
R = '.rili-markdown-renderer:has(.sz-hud)'

# ---------------- 规则 ----------------
V = r'[^｜\n"<>]'      # 一栏里的字：进属性的，引号和尖括号不收（对不上的那一行落到原来的规则上，原样留着）


def lw(w0, wm, ws, wb):
    """一处字四纪的说法（make_css_frame 的「字眼」那一段照这一条回复的纪露一个）"""
    return '<span class="lw"><span class="w0">%s</span><span class="wm">%s</span><span class="ws">%s</span><span class="wb">%s</span></span>' % (w0, wm, ws, wb)


# -- 进阶牌：§伟业｜伟业｜位阶→下一位阶｜LVL a/b · 这一道门槛｜命路五阶｜蓄势 a/b｜伟业簿 …n件｜破格铸史冠名 …｜候选称号 …
UP = ('<div class="sp-up" data-f="$2" data-t="$3" data-c="$6" data-h="$13" style="--lv:$4;--cap:$5;--xv:0$8;--xm:0$9;--bn:0$12"><i class="sz-goal" data-t="$2→$3"></i>'
      '<div class="up-h"><i class="up-em"></i><span class="up-fr"><b>$2</b></span><i class="up-ar"></i><span class="up-to"><b>$3</b></span>'
      '<span class="up-ti" data-v="$14"><small>候选称号</small><b>$14</b></span></div>'
      '<div class="up-g">'
      '<span class="up-c c-lv"><small>等级</small><b>LVL $4<em> / $5</em></b><i class="up-bar"></i><em class="up-s"></em><u class="up-ck"></u></span>'
      '<span class="up-c c-pl"><small>命路</small><b>$7</b><i class="up-pip"><i><b>共鸣</b></i><i><b>灵格</b></i><i><b>极境</b></i><i><b>英雄</b></i><i><b>传奇</b></i></i><em class="up-s">$6</em><u class="up-ck"></u></span>'
      '<span class="up-c c-xu" data-a="$8"><small>蓄势</small><b><span>$8</span><em> / $9</em>$10</b><i class="up-bar"></i></span>'
      '<span class="up-c c-bk" data-n="$12"><small>伟业簿</small><b>$11<i class="up-n">$12</i></b><i class="up-s3"><i></i><i></i><i></i></i></span>'
      '<span class="up-c c-hr"><small>英雄阶段</small><i class="up-3"><i title="LVL 121–146"><b>破格</b></i><i title="LVL 147–173"><b>铸史</b></i><i title="LVL 174–200"><b>冠名</b></i></i><em class="up-s">$13</em></span>'
      '</div></div>')
# -- 神力的台阶：凡极以后 §面板｜位阶 末一格 神力 n 档·薪 X·誓 一句话（档：候火、成躯、燃火、执柄、擎世）
GOD = ('<div class="sp-god" data-g="$3"><span class="gd-n"><small>神力</small><b>$2</b><em>$3</em></span>'
       '<span class="gd-tr"><i><b>候火</b></i><i><b>成躯</b></i><i><b>燃火</b></i><i><b>执柄</b></i><i><b>擎世</b></i></span>'
       '<span class="gd-f" data-v="$4"><small>薪</small>$4</span><span class="gd-f gd-v" data-v="$5"><small>誓</small>$5</span></div>')
# -- 职业：四个节点（就职Ⅰ、一转Ⅱ、二转Ⅲ、伟业职Ⅳ）。走到哪一个，先照这一行里的 Ⅰ 到 Ⅳ，没写的照位阶
JOB = ('<div class="sp-job" data-j="$2"><span class="jb-n"><small>职业</small><b>$2</b><em data-v="$3">$3</em></span>'
       '<span class="jb-tr"><i><b>%s</b></i><i><b>%s</b></i><i><b>%s</b></i><i><b>%s</b></i></span>'
       '<span class="jb-f"><small>评定</small><b>$4</b></span><span class="jb-f"><small>进阶</small><b>$5</b></span></div>') % (
    lw('就职', '认兵', '共鸣', '共鸣'), lw('一转', '成式', '灵格', '灵格'), lw('二转', '名器', '极境', '极境'), lw('伟业职', '冠名', '英雄', '英雄'))

RULES_UP = [
    ('星页·神力', r'/(§面板｜位阶｜LVL \d{1,3} [^｜\n]{1,20}｜EXP[^｜\n]{0,30}｜神力 ?(\d{1,2}) ?([^·・｜\n"<>]{0,6})(?:[·・｜] ?薪 ?([^·・｜\n"<>]{0,24})|)(?:[·・｜] ?誓 ?([^\n"<>]{0,120})|)[\s\S]*)ⓖ/',
     '$1ⓖ' + GOD),
    ('星页·进阶', r'/ⓖ([\s\S]*)§伟业｜伟业｜([^｜\n→"<>-]{1,8})(?:→|->|⇒)(' + V + r'{1,8})｜LVL ?(\d{1,3})\/(\d{1,3})[ ·・]{0,3}(' + V + r'{0,60})｜(?:命路五阶 ?|)(' + V + r'{0,40})｜蓄势 ?(?:(\d{1,6})\/(\d{1,6})|)(' + V + r'{0,20})'
     r'｜伟业簿 ?(' + V + r'*?)(?:(\d{1,3})件|)｜破格铸史冠名 (' + V + r'{0,60})｜候选称号 ([^\n"<>]*)/',
     UP + '$1ⓔ'),
    ('星页·进阶·简', r'/ⓖ([\s\S]*)§伟业｜伟业｜([^｜\n→"<>-]{1,8})(?:→|->|⇒)(' + V + r'{1,8})(?:｜([^\n"<>]*)|)$/m',
     '<div class="sp-up sp-up-s" data-f="$2" data-t="$3" style="--lv:0;--cap:1"><i class="sz-goal" data-t="$2→$3"></i>'
     '<div class="up-h"><i class="up-em"></i><span class="up-fr"><b>$2</b></span><i class="up-ar"></i><span class="up-to"><b>$3</b></span></div>'
     '<span class="up-x">$4</span></div>$1ⓔ'),
    ('星页·职业', r'/ⓙ([\s\S]*)§伟业｜职业｜([^｜\n←"<>]{0,40})(?:←(' + V + r'{0,30})|)｜(?:已评[：:]|)(' + V + r'{0,60})｜([^\n"<>]*)/',
     JOB + '$1ⓔ'),
]

# -- 技能书里的一枚：壳照旧（.sz-it.sz-ab、.sz-face、.sz-tip），里头添小标、线、格
HEAD = '<span class="sz-it sz-ab %s" data-c="%s" data-q="%s" data-n="%s"%s><label class="sz-face"><input type="radio" name="sz-ab"><i class="sz-hx"></i><b class="sz-nm">%s</b><small class="sp-q">%s</small>'
TIPH = '</label><span class="sz-tip"><span class="sz-tip-in"><span class="sz-tip-h"><i class="sz-ic"></i><b>%s</b><small>%s</small></span>'
TIPE = '<label class="sz-tip-x"><input type="radio" name="sz-ab"></label></span></span></span>ⓔ'
CHIPS = '<span class="sp-ch%s"><i class="c">%s</i></span><u class="sp-e"></u>'
N5 = ''.join('<i><b>$%d</b></i>' % k for k in range(6, 11))
LVC = '<span class="sp-ch%s"><i class="lvc"></i><i class="c">$4</i></span><u class="sp-e"></u>'
ART = (HEAD % ('sp-art', 'Art', '$2', '$1', ' data-lv="$3"', '$1', '$2') + LVC % '' + '<span class="sp-tr">' + N5 + '</span>'
       + TIPH % ('$1', 'Art · $2') + LVC % ' big' + '<span class="sz-tip-b">$5</span><span class="sp-ld">' + N5 + '</span>' + TIPE)
TIERS5 = ['生手', '熟手', '匠人', '名匠', '宗匠']
SKILL = (HEAD % ('sp-sk', 'Skill', '$2', '$1', ' data-p="$2" style="--pg:0$3"', '$1', '$2$4') + '<span class="sp-cl">' + '<i></i>' * 5 + '</span><em class="sp-bn">$5</em><em class="sp-nx" data-v="$7">$7</em>'
         + TIPH % ('$1', 'Skill · $2$4') + CHIPS % (' big', '$5') + '<span class="sp-cl big">' + ''.join('<i><b>%s</b></i>' % t for t in TIERS5) + '</span>'
         + '<span class="sz-tip-b">$6</span><span class="sp-nx" data-v="$7"><small>下一档</small>$7</span>' + TIPE)
CARD = (HEAD % ('sp-cd', '$1', '$3', '$2', '', '$2', '$3') + CHIPS % ('', '$4') + '<em class="sp-s">$5</em>'
        + TIPH % ('$2', '$1 · $3') + CHIPS % (' big', '$4') + '<span class="sz-tip-b">$5</span>' + TIPE)
NAME = r'(?!(?:无|暂无|未觉醒)(?:｜|\s*$))(' + V + r'{1,24})'
NODE = r'([^、，,｜\n"<>]{0,16})'
NONE = (HEAD % ('sp-cd sp-none', '命星', '', '未觉醒', '', '未觉醒', '') + '<em class="sp-s">这颗星还没有亮起来</em>'
        + TIPH % ('未觉醒', '命星') + '<span class="sz-tip-b">这颗星还没有亮起来。亮起来的那一天，名字、品阶和它做得到什么，都写在这一页上。</span>' + TIPE)
RULES_AB = [
    ('星页·未觉醒', r'/§能力｜命星｜未觉醒[^\n<]{0,40}$/gm', NONE),
    # Art：§能力｜Art｜名｜稀有度｜n阶·×修正｜一句｜招 甲、乙、丙、丁、戊   末一栏可以不写，写不满五个的后头空着
    ('星页·Art', r'/§能力｜(?:Art|技艺)｜' + NAME + r'｜(' + V + r'{0,10})｜ ?(?:第|)(?:([1-5一二三四五]) ?阶|)(' + V + r'{0,40})(?:｜([^｜\n<]*)|)'
     r'(?:｜ ?(?:招|阶)[ ：:]?' + NODE + (r'(?:[、，,]' + NODE + '|)') * 4 + r'|)[^\n<]{0,80}$/gm', ART),
    # Skill：§能力｜Skill｜名｜熟练度｜加成｜一句｜下一档 一句   熟练度写五档里的一个，后头可以接 ·62%；旧写法（共鸣7阶）照字出，不画格
    ('星页·Skill', r'/§能力｜(?:Skill|技能)｜' + NAME + r'｜([^｜\n"<>·・ %\d]{0,6})(?:[·・ ]{0,1}(\d{1,3})%|)(' + V + r'{0,12})(?:｜(' + V + r'{0,40})|)(?:｜([^｜\n<]*)|)'
     r'(?:｜ ?下一档[ ：:]?(?:[生熟匠名宗][手人匠][：:，, ]|)([^\n"<>]{0,80})|)$/gm', SKILL),
    # 别的（命星、Passive、Active、职业能力……）：一枚一张小卡，数那一栏拆成小标
    ('星页·卡', r'/§能力｜(' + V + r'{1,8})｜' + NAME + r'｜(' + V + r'{0,14})｜(' + V + r'{0,60})｜([^\n<]*)$/gm', CARD),
    # 数那一栏照 · 拆成一枚一枚（一串后头紧跟着收尾的 <u class="sp-e">，中间没有别的标签）
    ('星页·小标·拆', r'/[·・](?=[^<>\n]{0,80}<\/i><\/span><u class="sp-e">)/g', '</i><i class="c">'),
    # 小标认字：倍率、消耗、冷却、被动主动专长、阶，样式照这个换图形和颜色
    ('星页·小标·认', r'/<i class="c">(?=(×|SP(?= ?[\d全半])|MP(?= ?[\d全半])|HP(?= ?[\d全半])|冷却|每日|每场|每旬|被动|主动|专长|传奇专长|Special|Passive|Active|[ⅠⅡⅢⅣⅤ]|[一二三四五]阶)[^<\n]{0,60}<\/i>)/g', '<i class="c" data-k="$1">'),
    # Unique 职业能力摸熟的用法〔用法：一句〕单出一小块
    ('星页·用法', r'/〔用法[：:] ?([^〔〕\n<>]{1,160})〕(?=[^\n]*<label class="sz-tip-x">)/g', '<span class="sp-use"><small>用法</small>$1</span>'),
]
RULES = RULES_UP + RULES_AB
# 接在哪：RULES_UP 整组插在「伟业·目标」前头（要在各页开页以后、§面板｜位阶 展开以前），RULES_AB 整组插在「能力」前头
BEFORE = [('伟业·目标', RULES_UP), ('能力', RULES_AB)]


def rules(rs=None):
    return [{"name": n, "regex": rx, "replaceString": rep, "enabled": True, "messageRole": "assistant", "applyMode": "front-end"} for n, rx, rep in (rs or RULES)]


# ---------------- 样式 ----------------
def _mask(body, vb='0 0 24 24', stroke=True):
    attr = 'fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"' if stroke else 'fill="black"'
    s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" %s>%s</svg>' % (vb, attr, body)
    return 'url("data:image/svg+xml,%s")' % quote(s, safe="/:=' ")


M_LOCK = _mask('<rect x="5" y="11" width="14" height="10" rx="2" fill="black"/><path d="M8 11V8a4 4 0 018 0v3" stroke-width="2.4"/>')
M_CHECK = _mask('<path d="M5 12.5l4.5 4.5L19 7.5" stroke-width="3.2"/>')
M_HOUR = _mask('<path d="M6 3h12M6 21h12M7 3c0 5 10 5 10 9s-10 4-10 9M17 3c0 5-10 5-10 9s10 4 10 9"/>')
M_DROP = _mask('<path d="M12 3c4 5 6 8 6 11a6 6 0 01-12 0c0-3 2-6 6-11z"/>', stroke=False)
M_BOLT = _mask('<path d="M13 2L5 14h6l-1 8 8-12h-6z"/>', stroke=False)
M_STAR = _mask('<path d="M12 1l2.6 8.400L23 12l-8.400 2.600L12 23l-2.600-8.400L1 12l8.400-2.600z"/>', stroke=False)
M_FLAME = _mask('<path d="M12 2c1 4 6 6 6 12a6 6 0 01-12 0c0-3 2-4 3-7 1 2 2 3 3 3 0-3-1-5 0-8z"/>', stroke=False)
M_ARROW = _mask('<path d="M3 12h16M13 6l6 6-6 6"/>')
M_BOOK = _mask('<path d="M4 5c3-1.500 5.500-1.500 8 0c2.500-1.500 5-1.500 8 0v14c-3-1.500-5.500-1.500-8 0c-2.500-1.500-5-1.500-8 0zM12 5v14"/>')
M_SEAL = _mask('<path d="M12 2l2.200 2.700 3.400-.600.600 3.400L21 9.800 19.600 13l1.400 3.200-2.800 2.300-.600 3.400-3.400-.600L12 24l-2.200-2.700-3.400.600-.600-3.400L3 16.200 4.400 13 3 9.800l2.800-2.300.600-3.400 3.400.600z"/>', '0 0 24 26', stroke=False)
# 熟练度五档的徽：一到四道折线，宗匠一顶冠
M_TIER = [_mask(''.join('<path d="M5 %dl7-5 7 5" stroke-width="2.6"/>' % y for y in ys)) for ys in ([15], [12, 18], [9, 14, 19], [7, 11.5, 16, 20.5])]
M_TIER.append(_mask('<path d="M3 18h18M4 16L3 7l5 4 4-7 4 7 5-4-1 9z" fill="black"/>'))
HEX = 'polygon(50% 0,100% 25%,100% 75%,50% 100%,0 75%,0 25%)'
PRISM = '#ff6b5a, #ffd36e, #fff6d0, #7fd0ff, #c08cff, #ff6b5a'
CN = ['一', '二', '三', '四', '五']
ROMAN = ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ']
TIERN = ['启源', '共鸣', '灵格', '极境', '英雄', '传奇', '凡极']
FLOOR = {'启源': 0, '共鸣': 20, '灵格': 40, '极境': 80, '英雄': 120, '传奇': 200, '凡极': 299}
SKQ = ['#8f8676', '#5fae7b', '#4f8fd8', '#a06be0', '#e0a63c']
GODT = ['候火', '成躯', '燃火', '执柄', '擎世']
GODR = ['0–4', '5', '6–10', '11–14', '15–20']
DONE = ['已成', '已完成', '已达', '已齐', '✓', '√']
INK, INK2, RED, LINE = '#2a1a0c', '#6b5437', '#7a2e1d', 'rgb(91 58 30 / .22)'

CSS = r'''
/* ==== 命星页（star_page.py，状态栏第三轮）：进阶牌、职业四节点、神力的台阶，技能书里 Art 的五阶、Skill 的五档、一枚一张小卡 ==== */
@R@{@MASKVARS@}
/* ---------- 进阶牌 ---------- */
@R@ .sp-up{position:relative;margin:0 0 12px;padding:12px 12px 12px;border-radius:14px;--fl:0;--gk:0;--ps:0;--ok:clamp(0, calc(var(--lv) - var(--cap) + 1), 1);
  background:radial-gradient(120% 90% at 0% 0%, color-mix(in srgb, var(--fm-acc) 16%, transparent), transparent 60%), var(--fm-panel);
  box-shadow:inset 0 0 0 1px var(--fm-line), inset 0 1px 0 color-mix(in srgb, var(--fm-acc2) 35%, transparent), 0 8px 22px rgb(0 0 0 / .18)}
@R@ .sp-up>.sz-goal{display:none!important}
@R@ .sp-up :is(i,em,u){font-style:normal;text-decoration:none}
@R@ .up-h{display:flex;align-items:center;gap:12px;margin:0 0 9px;padding:0 2px 9px;border-bottom:1px solid color-mix(in srgb, var(--fm-acc) 22%, transparent)}
@R@ .up-em{position:relative;flex:none;width:34px;height:34px;border-radius:50%;background:radial-gradient(circle at 50% 30%, color-mix(in srgb, var(--fm-acc2) 34%, transparent), transparent 72%);box-shadow:inset 0 0 0 1px var(--fm-edge2), 0 0 0 4px color-mix(in srgb, var(--fm-acc) 8%, transparent)}
@R@ .up-em::before{content:"";position:absolute;inset:4px;border-radius:50%;border:1px dashed color-mix(in srgb, var(--fm-acc) 55%, transparent);animation:sp-spin 60s linear infinite}
@R@ .up-em::after{content:"";position:absolute;inset:8px;background:linear-gradient(160deg, #fff, var(--fm-acc2) 45%, var(--fm-acc));-webkit-mask:@STAR@ center/contain no-repeat;mask:@STAR@ center/contain no-repeat;filter:drop-shadow(0 0 5px var(--fm-glow))}
@R@ :is(.up-fr,.up-to,.up-ti){display:grid;gap:1px;min-width:0}
@R@ .sp-up small{display:block;font-size:10.5px;letter-spacing:.12em;color:var(--fm-acc)}
@R@ .up-ti{grid-auto-flow:column;align-items:baseline;gap:9px}
@R@ :is(.up-fr,.up-to)>b{font-family:var(--fm-serif);font-size:19px!important;font-weight:700!important;line-height:1.25;letter-spacing:.1em;white-space:nowrap}
@R@ .up-fr>b{color:var(--fm-ink)!important}
@R@ .up-to>b{color:var(--fm-head)!important;text-shadow:0 0 calc(4px + var(--ok) * var(--gk) * 14px) color-mix(in srgb, var(--fm-glow) calc(35% + var(--ok) * var(--gk) * 65%), transparent)}
@R@ .up-ar{position:relative;flex:1 1 30px;min-width:26px;max-width:110px;height:16px;overflow:hidden}
@R@ .up-ar::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg, color-mix(in srgb, var(--fm-acc) 25%, transparent), var(--fm-acc2));-webkit-mask:linear-gradient(#000,#000) left center/calc(100% - 9px) 2px no-repeat, @ARROWH@ right center/14px 14px no-repeat;mask:linear-gradient(#000,#000) left center/calc(100% - 9px) 2px no-repeat, @ARROWH@ right center/14px 14px no-repeat}
@R@ .up-ar::after{content:"";position:absolute;left:0;top:4px;width:26px;height:8px;border-radius:50%;background:radial-gradient(closest-side, #fff, color-mix(in srgb, var(--fm-glow) 80%, transparent) 45%, transparent);animation:sp-run 2.6s ease-in-out infinite}
@R@ .up-ti{margin-left:auto;justify-items:end;text-align:right;padding:5px 12px 5px 16px;border-radius:3px 10px 10px 3px;background:linear-gradient(270deg, color-mix(in srgb, var(--fm-acc) 22%, transparent), transparent);box-shadow:inset -2px 0 0 var(--fm-acc)}
@R@ .up-ti>b{font-family:var(--fm-serif);font-size:15px!important;font-weight:700!important;letter-spacing:.14em;color:var(--fm-head)!important}
@R@ .up-ti:is([data-v=""],[data-v="无"],[data-v="暂无"]){display:none}
@R@ .up-x{display:block;padding:0 2px;font-size:12.5px;line-height:1.7;color:var(--fm-ink)}
@R@ .up-x:empty{display:none}
@R@ .sp-up-s:has(.up-x:empty) .up-h{margin-bottom:0;padding-bottom:0;border-bottom:0}
@R@ .up-g{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-template-areas:"lv pl pl" "xu pl pl" "bk bk hr";gap:7px}
@R@ .up-c{position:relative;display:grid;grid-template-columns:auto minmax(0,1fr);align-content:start;align-items:baseline;gap:5px 10px;min-width:0;padding:8px 11px 9px;border-radius:10px;background:var(--fm-slot);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc) calc(18% + var(--k, 0) * 55%), transparent);transition:box-shadow .2s}
@R@ .up-c::before{content:"";position:absolute;inset:0;border-radius:10px;pointer-events:none;opacity:var(--k, 0);background:radial-gradient(90% 120% at 100% 0%, rgb(127 217 160 / .16), transparent 60%)}
@R@ .c-lv{grid-area:lv;--k:var(--ok)}
@R@ .c-pl{grid-area:pl;--k:var(--gk)}
@R@ .c-xu{grid-area:xu}
@R@ .c-bk{grid-area:bk}
@R@ .c-hr{grid-area:hr}
@R@ .up-c>:not(small,b,.up-ck){grid-column:1 / -1}
@R@ .up-c>b{display:block;min-width:0;font-size:14px!important;font-weight:700!important;line-height:1.35;color:var(--fm-ink)!important;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
@R@ .up-c>b em{font-weight:400;font-size:12px;color:var(--fm-ink2)}
@R@ .up-s{display:block;font-size:11.5px;line-height:1.5;color:var(--fm-ink2)}
@R@ .up-s:empty{display:none}
@R@ .up-ck{position:absolute;right:-5px;top:-5px;width:17px;height:17px;border-radius:50%;background:#7fd9a0;opacity:var(--k, 0);transform:scale(calc(.6 + var(--k, 0) * .4));box-shadow:0 0 10px rgb(127 217 160 / .7)}
@R@ .up-ck::after{content:"";position:absolute;inset:3px;background:#0f2a1c;-webkit-mask:@CHECK@ center/contain no-repeat;mask:@CHECK@ center/contain no-repeat}
@R@ .up-bar{position:relative;display:block;height:6px;border-radius:3px;overflow:hidden;background:color-mix(in srgb, var(--fm-ink) 12%, transparent);box-shadow:inset 0 0 0 1px rgb(0 0 0 / .18)}
@R@ .up-bar::after{content:"";position:absolute;left:0;top:0;bottom:0;width:calc(var(--p) * 100%);border-radius:3px;background:linear-gradient(90deg, color-mix(in srgb, var(--c) 60%, #fff), var(--c));box-shadow:0 0 8px color-mix(in srgb, var(--c) 60%, transparent)}
@R@ .c-lv .up-bar{--c:#e6c67a;--p:clamp(0, calc((var(--lv) - var(--fl)) / max(calc(var(--cap) - var(--fl)), 1)), 1)}
@R@ .c-xu .up-bar{--c:#d08a5e;--p:clamp(0, calc(var(--xv) / max(var(--xm), 1)), 1)}
@R@ .c-lv>b,@R@ .c-xu>b{justify-self:end;text-align:right}
@R@ .c-lv .up-s{display:grid;justify-items:end;margin-top:-2px}
@R@ .c-lv .up-s::before,@R@ .c-lv .up-s::after{grid-area:1 / 1}
@R@ .c-lv .up-s::before{opacity:calc(1 - var(--ok))}
@R@ .c-lv .up-s::after{content:"等级到了";color:#7fd9a0;opacity:var(--ok)}
@R@ .c-lv .up-s::before{counter-reset:spd max(0, calc(var(--cap) - var(--lv)));content:"还差 " counter(spd) " 级"}
/* 这一道门槛：五道里走过几道照此刻的位阶，眼下要过的那一道一下一下亮；做成了（那一栏写了已成）才打勾 */
@R@ .up-pip{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));position:relative;margin:5px 0 0}
@R@ .up-pip::before{content:"";position:absolute;left:10%;right:10%;top:7px;height:2px;background:linear-gradient(90deg, var(--fm-acc2) calc(max(var(--ps) - 1, 0) * 25%), color-mix(in srgb, var(--fm-ink) 16%, transparent) calc(max(var(--ps) - 1, 0) * 25%))}
@R@ .up-pip>i{position:relative;z-index:1;display:grid;justify-items:center;gap:4px;--on:0;--cur:0}
@R@ .up-pip>i::before{content:"";width:16px;height:16px;transform:rotate(45deg) scale(calc(.72 + var(--cur) * .28));border-radius:2px;
  background:color-mix(in srgb, var(--fm-acc2) calc(var(--on) * 100%), var(--fm-band));box-shadow:inset 0 0 0 1.5px color-mix(in srgb, var(--fm-acc2) calc(45% + var(--cur) * 55%), transparent), 0 0 calc(var(--on) * 8px + var(--cur) * 4px) var(--fm-glow)}
@R@ .up-pip>i::after{content:"";position:absolute;left:50%;top:-4px;width:24px;height:24px;margin-left:-12px;border-radius:50%;border:1.5px solid var(--fm-acc2);opacity:0}
@R@ .up-pip>i>b{font-size:11px!important;font-weight:calc(400 + var(--cur) * 300)!important;letter-spacing:.06em;color:color-mix(in srgb, var(--fm-head) calc(40% + max(var(--on), var(--cur)) * 60%), transparent)!important}
/* 伟业簿：数一枚小牌；英雄那一境要三件，三格 */
@R@ .c-bk>b{font-size:13px!important;font-weight:600!important}
@R@ .up-n{display:inline-block;margin-left:7px;padding:0 7px;border-radius:999px;font-size:11px;font-weight:600;line-height:18px;vertical-align:1px;color:#1b1408;background:var(--fm-acc2)}
@R@ .up-n:empty{display:none}
@R@ .up-n::after{content:" 件"}
@R@ .up-s3{display:none;grid-template-columns:repeat(3,1fr);gap:5px;max-width:220px}
@R@ .up-s3>i{--on:0;height:20px;border-radius:4px;background:color-mix(in srgb, var(--fm-acc2) calc(var(--on) * 26%), transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc2) calc(25% + var(--on) * 60%), transparent);position:relative}
@R@ .up-s3>i::after{content:"";position:absolute;inset:3px;background:color-mix(in srgb, var(--fm-acc2) calc(22% + var(--on) * 78%), transparent);-webkit-mask:@BOOK@ center/contain no-repeat;mask:@BOOK@ center/contain no-repeat}
/* 破格、铸史、冠名：英雄那一境的三个小能级（121、147、174），照等级亮 */
@R@ .c-hr>.up-3{grid-column:2}
@R@ .up-3{display:grid;grid-template-columns:repeat(3,1fr);gap:3px;min-width:0}
@R@ .up-3>i{--on:0;position:relative;display:flex;align-items:center;justify-content:center;gap:2px;padding:2px 0;border-radius:6px;background:color-mix(in srgb, var(--fm-acc2) calc(var(--on) * 20%), transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc2) calc(20% + var(--on) * 60%), transparent)}
@R@ .up-3>i::before{content:"";display:none;flex:none;width:11px;height:12px;background:color-mix(in srgb, var(--fm-acc2) calc(24% + var(--on) * 76%), transparent);-webkit-mask:@SEAL@ center/contain no-repeat;mask:@SEAL@ center/contain no-repeat;filter:drop-shadow(0 0 calc(var(--on) * 4px) var(--fm-glow))}
@R@ .up-3>i>b{white-space:nowrap;font-size:10.5px!important;font-weight:600!important;letter-spacing:0;color:color-mix(in srgb, var(--fm-head) calc(40% + var(--on) * 60%), transparent)!important}
/* ---------- 神力的台阶 ---------- */
@R@ .sp-god{position:relative;display:grid;grid-template-columns:auto minmax(0,1fr);gap:10px 16px;align-items:center;margin:0 0 14px;padding:13px 16px;border-radius:14px;overflow:hidden;
  background:radial-gradient(80% 140% at 0% 50%, color-mix(in srgb, var(--fm-glow) 22%, transparent), transparent 70%), linear-gradient(90deg, color-mix(in srgb, var(--fm-acc2) 10%, transparent), transparent), var(--fm-panel);
  box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc2) 60%, transparent), 0 0 22px color-mix(in srgb, var(--fm-glow) 18%, transparent)}
@R@ .sp-god small{display:block;font-size:10.5px;letter-spacing:.14em;color:var(--fm-acc)}
@R@ .gd-n{display:grid;justify-items:center;min-width:64px}
@R@ .gd-n>b{font-family:var(--fm-serif);font-size:34px!important;font-weight:700!important;line-height:1.05;color:var(--fm-head)!important;text-shadow:0 0 16px var(--fm-glow)}
@R@ .gd-n>em{font-style:normal;font-family:var(--fm-serif);font-size:12.5px;letter-spacing:.2em;color:var(--fm-acc2)}
@R@ .gd-tr{position:relative;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));--gn:0}
@R@ .gd-tr::before{content:"";position:absolute;left:10%;right:10%;top:13px;height:2px;background:linear-gradient(90deg, var(--fm-acc2) calc((var(--gn) - 1) * 25%), color-mix(in srgb, var(--fm-ink) 16%, transparent) calc((var(--gn) - 1) * 25%))}
@R@ .gd-tr>i{--on:0;--cur:0;position:relative;z-index:1;display:grid;justify-items:center;gap:3px;font-style:normal}
@R@ .gd-tr>i::before{content:"";width:28px;height:28px;border-radius:50%;background:radial-gradient(circle at 50% 70%, color-mix(in srgb, var(--fm-glow) calc(var(--on) * 55%), transparent), transparent 70%), var(--fm-band);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fm-acc2) calc(30% + var(--on) * 70%), transparent), 0 0 calc(var(--cur) * 14px) var(--fm-glow)}
@R@ .gd-tr>i::after{content:"";position:absolute;left:50%;top:5px;width:18px;height:18px;margin-left:-9px;background:color-mix(in srgb, #fff calc(var(--cur) * 55%), color-mix(in srgb, var(--fm-acc2) calc(22% + var(--on) * 78%), transparent));-webkit-mask:@FLAME@ center/contain no-repeat;mask:@FLAME@ center/contain no-repeat;transform-origin:50% 90%}
@R@ .gd-tr>i>b{font-family:var(--fm-serif);font-size:12px!important;font-weight:calc(500 + var(--cur) * 200)!important;letter-spacing:.1em;color:color-mix(in srgb, var(--fm-head) calc(40% + var(--on) * 60%), transparent)!important}
@R@ .gd-tr>i>b::after{display:block;font-family:var(--fm-sans, inherit);font-size:9.5px;font-weight:400;letter-spacing:.04em;text-align:center;color:var(--fm-ink2);opacity:.75}
@R@ .gd-f{grid-column:1 / -1;display:flex;gap:10px;align-items:baseline;font-size:13px;line-height:1.6;color:var(--fm-ink)}
@R@ .gd-f>small{flex:none}
@R@ .gd-v{font-family:var(--fm-serif);font-size:14px;letter-spacing:.06em;color:var(--fm-head)}
@R@ .gd-f:is([data-v=""]){display:none}
@R@ .gd-f+.gd-f{margin-top:-6px}
/* ---------- 职业：四个节点 ---------- */
@R@ .sp-job{--jn:var(--je, var(--jt, 0));--q:var(--fm-acc2);display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:8px 18px;align-items:center;margin:0 0 16px;padding:11px 14px 10px;border-radius:14px;background:var(--fm-panel);box-shadow:inset 0 0 0 1px var(--fm-line)}
@R@ .sp-job small{display:block;font-size:10.5px;letter-spacing:.12em;color:var(--fm-acc)}
@R@ .jb-n{min-width:0}
@R@ .jb-n>b{display:block;margin-top:2px;font-family:var(--fm-serif);font-size:16px!important;font-weight:700!important;line-height:1.35;letter-spacing:.06em;color:color-mix(in srgb, var(--q) 55%, var(--fm-head))!important;overflow-wrap:anywhere}
@R@ .jb-n>em{display:block;font-style:normal;font-size:11.5px;color:var(--fm-ink2)}
@R@ .jb-n>em::before{content:"← "}
@R@ .jb-n>em:is([data-v=""],[data-v="无"]){display:none}
@R@ .jb-tr{position:relative;display:grid;grid-template-columns:repeat(4,minmax(0,1fr))}
@R@ .jb-tr::before{content:"";position:absolute;left:12.5%;right:12.5%;top:13px;height:2px;background:linear-gradient(90deg, var(--fm-acc2) calc((var(--jn) - 1) * 33.4%), color-mix(in srgb, var(--fm-ink) 16%, transparent) calc((var(--jn) - 1) * 33.4%))}
@R@ .jb-tr>i{--on:clamp(0, calc(var(--jn) - var(--k) + 1), 1);--cur:clamp(0, calc(1 - (var(--jn) - var(--k)) * (var(--jn) - var(--k))), 1);position:relative;z-index:1;display:grid;justify-items:center;gap:4px;font-style:normal}
@R@ .jb-tr>i::before{display:grid;place-items:center;width:28px;height:28px;border-radius:50%;font-family:var(--fm-serif);font-size:13px;font-weight:700;line-height:1;
  color:color-mix(in srgb, #1b1408 calc(var(--on) * 100%), color-mix(in srgb, var(--fm-ink2) 70%, transparent));
  background:radial-gradient(circle at 50% 28%, color-mix(in srgb, #fff calc(var(--on) * 70%), transparent), transparent 60%), color-mix(in srgb, var(--fm-acc2) calc(var(--on) * 100%), var(--fm-band));
  box-shadow:inset 0 0 0 1.5px color-mix(in srgb, var(--fm-acc2) calc(35% + var(--on) * 65%), transparent), 0 0 0 calc(var(--cur) * 3px) color-mix(in srgb, var(--fm-acc2) 28%, transparent), 0 0 calc(var(--cur) * 14px) var(--fm-glow)}
@R@ .jb-tr>i>b{font-size:11.5px!important;font-weight:calc(400 + var(--cur) * 300)!important;letter-spacing:.06em;white-space:nowrap;color:color-mix(in srgb, var(--fm-head) calc(40% + var(--on) * 60%), transparent)!important}
@R@ .jb-tr>i>b::after{display:block;font-size:9.5px;font-weight:400;letter-spacing:.04em;text-align:center;color:var(--fm-ink2);opacity:.75}
@R@ .jb-f{display:flex;gap:9px;align-items:baseline;min-width:0;padding-top:7px;border-top:1px solid color-mix(in srgb, var(--fm-acc) 20%, transparent)}
@R@ .jb-f>small{flex:none}
@R@ .jb-f>b{display:block;min-width:0;font-size:12.5px!important;font-weight:500!important;line-height:1.5;color:var(--fm-ink)!important}
/* ---------- 技能书里：一枚一条 ---------- */
@R@ .sz-abs .sz-ab>.sz-face{grid-column:1 / 5;position:relative;display:grid;grid-template-columns:42px minmax(0,1fr) auto;column-gap:10px;row-gap:4px;align-items:center;justify-items:start;margin:0 0 7px;padding:8px 10px 8px 9px;border-radius:9px;text-align:left;overflow:hidden;
  background:linear-gradient(100deg, color-mix(in srgb, var(--q) 17%, transparent), transparent 64%), rgb(255 251 238 / .55);
  box-shadow:inset 0 0 0 1px rgb(91 58 30 / .2), inset 3px 0 0 color-mix(in srgb, var(--q) 78%, #5b3a1e), 0 1px 0 rgb(255 255 255 / .5);transition:transform .16s, box-shadow .16s}
@R@ .sz-abs .sz-it:hover>.sz-face,@R@ .sz-abs .sz-it:has(>.sz-face input:checked)>.sz-face{transform:translateX(2px);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--q) 62%, #5b3a1e), inset 4px 0 0 var(--q), 0 5px 14px rgb(60 36 12 / .22)}
@R@ .sz-abs .sz-it:has(>.sz-face input:checked)>.sz-face::before{content:"";position:absolute;right:3px;top:50%;margin-top:-5px;border:5px solid transparent;border-left-color:color-mix(in srgb, var(--q) 70%, #5b3a1e);border-right-width:0}
@R@ .sz-abs .sz-ab>.sz-face>.sz-hx{grid-column:1;grid-row:1 / span 2;width:42px;height:47px}
@R@ .sz-abs .sz-ab>.sz-face>.sz-hx::after{inset:12px 10.5px}
@R@ .sz-abs .sz-ab>.sz-face>.sz-nm{grid-column:2;grid-row:1;width:auto;max-width:100%;margin:0;font-family:var(--fm-serif);font-size:14.5px!important;font-weight:700!important;line-height:1.3;letter-spacing:.04em;text-align:left;color:@INK@!important}
@R@ .sz-abs .sz-ab>.sz-face:not(:has(.sp-q))>.sz-nm{grid-row:1 / span 2}
@R@ .sp-q{grid-column:3;grid-row:1;justify-self:end;padding:0 8px;border-radius:999px;font-size:10px;line-height:17px;letter-spacing:.08em;white-space:nowrap;color:color-mix(in srgb, var(--q) 58%, @INK@);background:color-mix(in srgb, var(--q) 12%, rgb(255 251 238 / .7));box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--q) 62%, transparent)}
@R@ .sp-q:empty{display:none}
@R@ .sp-ch{grid-column:2 / 4;grid-row:2;display:flex;flex-wrap:wrap;gap:4px;min-width:0}
@R@ .sp-ch>i{display:inline-flex;align-items:center;gap:3px;padding:0 7px;border-radius:5px;font-style:normal;font-size:11px;line-height:18px;letter-spacing:.02em;white-space:nowrap;color:#4a3118;background:rgb(91 58 30 / .1);box-shadow:inset 0 0 0 1px rgb(91 58 30 / .14);font-variant-numeric:tabular-nums}
@R@ .sp-ch>i:empty{display:none}
@R@ .sp-ch>i.lvc{display:inline-flex;font-family:var(--fm-serif);font-weight:700;letter-spacing:.08em;color:color-mix(in srgb, var(--q) 45%, #fff6dc);background:linear-gradient(180deg, #55351b, #33200f);box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--q) 70%, transparent)}
@R@ .sp-ch>i.lvc::after{content:var(--lvt, "")}
@R@ .sp-art[data-lv=""] .lvc{display:none}
@R@ .sp-ch>i[data-k]::before{content:"";flex:none;width:10px;height:10px;background:currentColor;-webkit-mask:var(--g) center/contain no-repeat;mask:var(--g) center/contain no-repeat}
@R@ .sp-ch>i[data-k="×"]{font-weight:700;font-size:12px;color:#f6e3ae;background:linear-gradient(180deg, #5a3a1c, #38220f);box-shadow:inset 0 0 0 1px rgb(214 178 106 / .55)}
@R@ .sp-ch>i[data-k="×"]::before{display:none}
@R@ .sp-ch>i:is([data-k="SP"],[data-k="MP"],[data-k="HP"]){--g:@DROP@}
@R@ .sp-ch>i[data-k="SP"]{color:#8a6410;background:rgb(212 169 76 / .2);box-shadow:inset 0 0 0 1px rgb(212 169 76 / .6)}
@R@ .sp-ch>i[data-k="MP"]{color:#2c5796;background:rgb(95 146 214 / .18);box-shadow:inset 0 0 0 1px rgb(95 146 214 / .6)}
@R@ .sp-ch>i[data-k="HP"]{color:#9a2f24;background:rgb(226 90 78 / .14);box-shadow:inset 0 0 0 1px rgb(226 90 78 / .55)}
@R@ .sp-ch>i:is([data-k="冷却"],[data-k^="每"]){--g:@HOUR@;color:#51606e;background:rgb(110 130 150 / .16);box-shadow:inset 0 0 0 1px rgb(110 130 150 / .5)}
@R@ .sp-ch>i:is([data-k="被动"],[data-k="主动"],[data-k="专长"],[data-k="传奇专长"],[data-k="Special"],[data-k="Passive"],[data-k="Active"]){letter-spacing:.1em;color:color-mix(in srgb, var(--q) 55%, @INK@);background:none;box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--q) 60%, rgb(91 58 30 / .4))}
@R@ .sp-ch>i:is([data-k="被动"],[data-k="主动"],[data-k="专长"],[data-k="传奇专长"],[data-k="Special"],[data-k="Passive"],[data-k="Active"])::before{display:none}
@R@ .sp-ch>i:is([data-k="主动"],[data-k="Active"],[data-k="Special"])::before{display:block;--g:@BOLT@}
@R@ .sp-ch>i:is([data-k="Ⅰ"],[data-k="Ⅱ"],[data-k="Ⅲ"],[data-k="Ⅳ"],[data-k="Ⅴ"],[data-k$="阶"]){font-family:var(--fm-serif);font-weight:700;color:@RED@;background:rgb(122 46 29 / .08);box-shadow:inset 0 0 0 1px rgb(122 46 29 / .4)}
@R@ .sp-ch>i:is([data-k="Ⅰ"],[data-k="Ⅱ"],[data-k="Ⅲ"],[data-k="Ⅳ"],[data-k="Ⅴ"],[data-k$="阶"])::before{display:none}
@R@ .sp-s{grid-column:2 / 4;grid-row:3;max-width:100%;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font-style:normal;font-size:11.5px;line-height:1.5;color:@INK2@}
@R@ .sp-s:empty,@R@ .sp-s .sp-use{display:none}
@R@ .sp-e{display:none}
/* 右页：小标居中一排 */
@R@ .sz-abs .sz-tip .sp-ch.big{justify-content:center;padding:10px 0 0;gap:5px}
@R@ .sz-abs .sz-tip .sp-ch.big>i{padding:1px 9px;font-size:12px;line-height:20px}
@R@ .sz-abs .sz-tip .sp-ch.big>i[data-k="×"]{font-size:13.5px}
@R@ .sp-use{display:block;margin-top:9px;padding:7px 10px;border-radius:7px;font-size:12.5px;line-height:1.65;background:rgb(122 46 29 / .07);box-shadow:inset 2px 0 0 @RED@}
@R@ .sp-use>small{display:block;font-size:10px;letter-spacing:.16em;color:@RED@}
/* 品阶的质感：Legend 一道金箔边，Unique 七彩的边、一道光扫过去、右页一行“只此一份” */
@R@ .sz-abs .sz-ab:is([data-q*="Legend"],[data-q*="传说"],[data-q*="专属"])>.sz-face{border:1px solid transparent;padding:7px 9px 7px 8px;
  background:linear-gradient(100deg, rgb(255 244 207 / .9), rgb(255 251 238 / .7) 60%) padding-box, linear-gradient(120deg, #b8862f, #f4dc9a 30%, #b8862f 55%, #f8e7b4 80%, #a8772a) border-box;box-shadow:inset 3px 0 0 #d49a2c, 0 2px 8px rgb(184 134 47 / .28)}
@R@ .sz-abs .sz-ab:is([data-q*="Unique"],[data-q*="唯一"])>.sz-face{border:1.5px solid transparent;padding:6.5px 8.5px 6.5px 7.500px;
  background:linear-gradient(100deg, rgb(255 236 230 / .92), rgb(255 251 238 / .8) 55%, rgb(236 244 255 / .8)) padding-box, linear-gradient(120deg, @PRISM@) border-box;box-shadow:0 2px 12px rgb(226 90 78 / .28), 0 0 0 3px rgb(255 211 110 / .12)}
@R@ .sz-abs .sz-ab:is([data-q*="Legend"],[data-q*="传说"],[data-q*="专属"],[data-q*="Unique"],[data-q*="唯一"])>.sz-face::after{content:"";position:absolute;top:-20%;bottom:-20%;left:-30%;width:26%;pointer-events:none;background:linear-gradient(100deg, transparent, rgb(255 255 255 / .75), transparent);transform:skewX(-18deg);animation:sp-sheen 5.2s ease-in-out infinite}
@R@ .sz-abs .sz-ab:is([data-q*="Legend"],[data-q*="传说"],[data-q*="专属"])>.sz-face::after{animation-duration:7.5s;opacity:.7}
@R@ .sz-ab:is([data-q*="Unique"],[data-q*="唯一"]) .sp-q{color:#fff;font-weight:700;background:linear-gradient(100deg, #e25a4e, #e0a63c 45%, #5aa6e0 75%, #a06be0);box-shadow:0 0 8px rgb(226 90 78 / .5)}
@R@ .sz-ab:is([data-q*="Unique"],[data-q*="唯一"]) .sp-q::before{content:"✦ "}
@R@ .sz-ab:is([data-q*="Unique"],[data-q*="唯一"])>.sz-face>.sz-hx{filter:drop-shadow(0 0 6px rgb(226 90 78 / .7))}
@R@ .sz-abs .sz-ab:is([data-q*="Unique"],[data-q*="唯一"]) .sz-tip-h b{color:transparent!important;background:linear-gradient(100deg, #b5322a, #c98a14 35%, #2f6fb0 68%, #7a3fc0);-webkit-background-clip:text;background-clip:text}
@R@ .sz-abs .sz-ab:is([data-q*="Unique"],[data-q*="唯一"]) .sz-tip-in::after{content:"同一时刻，世上只此一份";display:block;margin-top:12px;padding-top:8px;border-top:1px solid @LINE@;font-size:10.5px;letter-spacing:.28em;text-align:center;color:#b5322a}
.sz-it:is([data-q*="专属"]){--q:#e0a63c}
.sz-it:is([data-q^="通用"]){--q:#93a1b8}
@R@ .sz-abs .sp-none>.sz-face{background:repeating-linear-gradient(135deg, rgb(91 58 30 / .05) 0 6px, transparent 6px 12px), rgb(255 251 238 / .4);box-shadow:inset 0 0 0 1px rgb(91 58 30 / .22);filter:saturate(.4)}
@R@ .sz-abs .sp-none>.sz-face>.sz-nm{color:#8d7a5c!important}
@R@ .sz-abs .sp-none>.sz-face>.sz-hx{opacity:.5}
/* ---------- Art：五个节点一条线 ---------- */
@R@ .sp-art{--n:0}
@R@ .sp-tr{grid-column:1 / 4;grid-row:3;position:relative;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));width:100%;margin:5px 0 1px}
@R@ .sp-tr::before{content:"";position:absolute;left:10%;right:10%;top:11px;height:2px;border-radius:1px;background:rgb(91 58 30 / .2)}
@R@ .sp-tr::after{content:"";position:absolute;left:10%;top:10px;height:4px;width:calc(max(var(--n) - 1, 0) * 20%);border-radius:2px;background:linear-gradient(90deg, color-mix(in srgb, var(--q) 60%, #3a2410), var(--q));box-shadow:0 0 7px color-mix(in srgb, var(--q) 75%, transparent)}
@R@ :is(.sp-tr,.sp-ld)>i{--on:0;--cur:0;position:relative;z-index:1;font-style:normal;min-width:0}
@R@ .sp-tr>i{display:grid;justify-items:center;align-content:start;gap:3px}
@R@ :is(.sp-tr,.sp-ld)>i::before{display:grid;place-items:center;width:22px;height:24px;clip-path:@HEX@;font-family:var(--fm-serif);font-size:12px;font-weight:900;line-height:1;text-shadow:0 1px 1px rgb(0 0 0 / calc(var(--on) * .55));
  color:color-mix(in srgb, #fffdf2 calc(var(--on) * 100%), rgb(91 58 30 / .6));
  background:linear-gradient(165deg, color-mix(in srgb, color-mix(in srgb, var(--q) 86%, #fff) calc(var(--on) * 100%), rgb(120 92 58 / .26)), color-mix(in srgb, color-mix(in srgb, var(--q) 58%, #1a0f05) calc(var(--on) * 100%), rgb(91 58 30 / .2)));
  transform:scale(calc(1 + var(--cur) * .2));transition:transform .2s}
@R@ .sp-tr>i{filter:drop-shadow(0 0 calc(var(--on) * 3px + var(--cur) * 3px) color-mix(in srgb, var(--q) 80%, transparent))}
@R@ .sp-tr>i>b{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;max-width:100%;padding:0 1px;overflow:hidden;text-align:center;overflow-wrap:anywhere;font-size:calc(9.5px + var(--on) * 1px)!important;font-weight:calc(400 + var(--on) * 200)!important;line-height:1.25;letter-spacing:0;color:color-mix(in srgb, @INK@ calc(var(--on) * 100%), #8d7a5c)!important}
@R@ .sp-tr>i>b:empty{display:none}
@R@ .sp-tr>i>b::before{content:"";display:inline-block;width:calc((1 - var(--on)) * 8px);height:8px;margin-right:calc((1 - var(--on)) * 2px);vertical-align:-0.5px;background:currentColor;-webkit-mask:@LOCK@ center/contain no-repeat;mask:@LOCK@ center/contain no-repeat}
/* 右页：五阶一级一级排下来 */
@R@ .sp-ld{display:grid;margin-top:11px;padding-top:11px;border-top:1px solid @LINE@}
@R@ .sp-ld>i{display:grid;grid-template-columns:22px minmax(0,1fr);column-gap:9px;align-items:start;padding-bottom:9px;--ln:0}
@R@ .sp-ld>i:last-child{padding-bottom:0}
@R@ .sp-ld>i:not(:last-child)::after{content:"";position:absolute;left:10px;top:25px;bottom:-1px;width:2px;border-radius:1px;background:color-mix(in srgb, var(--q) calc(var(--ln) * 100%), rgb(91 58 30 / .2))}
@R@ .sp-ld>i::before{filter:drop-shadow(0 0 calc(var(--on) * 3px) color-mix(in srgb, var(--q) 80%, transparent))}
@R@ .sp-ld>i>b{display:block;padding-top:1px;font-family:var(--fm-serif);font-size:13px!important;font-weight:calc(500 + var(--on) * 200)!important;line-height:1.45;color:color-mix(in srgb, @INK@ calc(var(--on) * 100%), #8d7a5c)!important;overflow-wrap:anywhere}
@R@ .sp-ld>i>b::before{content:var(--t) var(--s, " · 未到");display:block;font-family:var(--fm-sans, system-ui);font-size:10px;font-weight:600;letter-spacing:.14em;color:color-mix(in srgb, color-mix(in srgb, var(--q) 55%, @INK@) calc(var(--on) * 100%), #a08c6c)}
@R@ .sp-art[data-lv=""] .sp-ld>i{--s:""}
@R@ .sp-art[data-lv=""] .sp-tr>i>b::before{display:none}
/* ---------- Skill：五格熟练度 ---------- */
@R@ .sz-abs .sp-sk>.sz-face{row-gap:3px;padding-top:7px;padding-bottom:7px}
@R@ .sz-abs .sp-sk@FIVE@>.sz-face>.sz-hx::after{inset:11px 10px;-webkit-mask-image:var(--tg);mask-image:var(--tg)}
@R@ .sp-cl{grid-column:2;grid-row:2;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:3px;width:100%;max-width:168px}
@R@ .sp-cl>i{--f:0;position:relative;height:8px;border-radius:4px;overflow:hidden;font-style:normal;background:rgb(91 58 30 / .13);box-shadow:inset 0 0 0 1px rgb(91 58 30 / .2)}
@R@ .sp-cl>i::after{content:"";position:absolute;left:0;top:0;bottom:0;width:calc(var(--f) * 100%);border-radius:4px;background:linear-gradient(180deg, #f3d98a, #c4902f 70%, #a8772a);box-shadow:inset 0 1px 0 rgb(255 255 255 / .6)}
@R@ .sp-sk:not(@FIVE@) .sp-cl{display:none}
@R@ .sp-sk:not(@FIVE@) .sp-bn{grid-column:2 / 4}
@R@ .sp-bn{grid-column:3;grid-row:2;justify-self:end;font-style:normal;font-size:11.5px;font-weight:600;white-space:nowrap;color:@RED@}
@R@ .sz-face>.sp-nx{grid-column:2 / 4;grid-row:3;max-width:100%;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font-style:normal;font-size:11px;line-height:1.5;color:@INK2@}
@R@ .sp-nx[data-v=""]{display:none!important}
@R@ .sz-face>.sp-nx::before{content:"下一档" var(--nx, "") "　";font-weight:600;letter-spacing:.06em;color:color-mix(in srgb, var(--nq, #8a6410) 70%, @INK@)}
/* 右页：五档的徽一排，到了的亮着，下一档虚线圈着 */
@R@ .sz-abs .sz-tip .sp-cl.big{grid-column:auto;display:grid;max-width:none;gap:2px;margin:13px 0 2px}
@R@ .sp-cl.big>i{--f:0;--nxt:0;display:grid;justify-items:center;gap:4px;height:auto;overflow:visible;border-radius:0;background:none;box-shadow:none}
@R@ .sp-cl.big>i::before{content:"";width:28px;height:28px;border-radius:50%;background:radial-gradient(circle at 50% 28%, rgb(255 255 255 / calc(var(--f) * .7)), transparent 60%), color-mix(in srgb, #d4a23a calc(var(--f) * 100%), rgb(91 58 30 / .1));
  box-shadow:inset 0 0 0 1.5px color-mix(in srgb, #8a6410 calc(var(--f) * 100%), rgb(91 58 30 / .3)), 0 0 calc(var(--f) * 8px) rgb(212 162 58 / .6);outline:1.5px dashed rgb(138 100 16 / calc(var(--nxt) * .9));outline-offset:2px}
@R@ .sp-cl.big>i::after{content:"";position:absolute;left:50%;top:6px;width:16px;height:16px;margin-left:-8px;border-radius:0;box-shadow:none;background:color-mix(in srgb, #3a2410 calc(var(--f) * 100%), rgb(91 58 30 / .42));-webkit-mask:var(--g) center/contain no-repeat;mask:var(--g) center/contain no-repeat}
@R@ .sp-cl.big>i>b{font-size:10.5px!important;font-weight:calc(400 + var(--f) * 300)!important;letter-spacing:.04em;color:color-mix(in srgb, @INK@ calc(var(--f) * 100%), #8d7a5c)!important}
@R@ .sz-tip .sp-nx{display:block;margin-top:10px;padding:8px 10px;border-radius:7px;font-size:12.5px;line-height:1.65;color:@INK@;background:rgb(212 162 58 / .12);box-shadow:inset 0 0 0 1px rgb(138 100 16 / .3)}
@R@ .sz-tip .sp-nx>small{display:block;font-size:10px;font-weight:600;letter-spacing:.16em;color:#8a6410}
@R@ .sz-tip .sp-nx>small::after{content:var(--nx, "")}
/* ---------- 动的：只动位移和明暗 ---------- */
@keyframes sp-spin{to{transform:rotate(360deg)}}
@keyframes sp-run{0%{transform:translateX(-30px);opacity:0}20%{opacity:1}80%{opacity:1}100%{transform:translateX(120px);opacity:0}}
@keyframes sp-sheen{0%,62%{transform:translateX(0) skewX(-18deg)}100%{transform:translateX(620%) skewX(-18deg)}}
@keyframes sp-ping{0%{opacity:.9;transform:scale(.6)}100%{opacity:0;transform:scale(1.25)}}
@keyframes sp-flick{0%,100%{transform:scale(1)}50%{transform:scale(1.12,1.2)}}
@keyframes sp-pop{0%{opacity:0;transform:scale(.4)}70%{opacity:1;transform:scale(1.14)}100%{opacity:1;transform:none}}
@keyframes sp-grow{from{transform:scaleX(0)}to{transform:none}}
@keyframes sp-stamp{0%{opacity:0;transform:scale(2.2) rotate(-18deg)}60%{opacity:1;transform:scale(.92)}100%{transform:scale(1)}}
@keyframes sp-rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@R@ .sp-tr>i{animation:sp-pop .42s cubic-bezier(.2,1.2,.4,1) both;animation-delay:calc(var(--i) * 70ms)}
@R@ .sp-tr::after{transform-origin:0 50%;animation:sp-grow .55s ease-out .05s both}
@R@ .sp-ld>i{animation:sp-rise .3s ease-out both;animation-delay:calc(var(--i) * 60ms)}
@R@ .sp-cl>i::after{transform-origin:0 50%;animation:sp-grow .35s ease-out both;animation-delay:calc(var(--i) * 80ms)}
@R@ .sp-cl.big>i::after{animation:none}
@R@ .sp-cl.big>i{animation:sp-pop .4s cubic-bezier(.2,1.2,.4,1) both;animation-delay:calc(var(--i) * 70ms)}
@R@ :is(.up-pip,.jb-tr,.gd-tr,.up-3)>i{animation:sp-pop .42s cubic-bezier(.2,1.2,.4,1) both;animation-delay:calc(120ms + var(--i) * 80ms)}
@R@ .up-bar::after{transform-origin:0 50%;animation:sp-grow .7s cubic-bezier(.2,.8,.2,1) .1s both}
@R@ .up-ck{animation:sp-stamp .45s cubic-bezier(.2,1.3,.4,1) .55s both}
@R@ :is(.sp-tr,.sp-ld,.sp-cl,.up-pip,.jb-tr,.gd-tr,.up-3)>i:nth-child(1){--i:0}
@R@ :is(.sp-tr,.sp-ld,.sp-cl,.up-pip,.jb-tr,.gd-tr,.up-3)>i:nth-child(2){--i:1}
@R@ :is(.sp-tr,.sp-ld,.sp-cl,.up-pip,.jb-tr,.gd-tr,.up-3)>i:nth-child(3){--i:2}
@R@ :is(.sp-tr,.sp-ld,.sp-cl,.up-pip,.jb-tr,.gd-tr,.up-3)>i:nth-child(4){--i:3}
@R@ :is(.sp-tr,.sp-ld,.sp-cl,.up-pip,.jb-tr,.gd-tr,.up-3)>i:nth-child(5){--i:4}
@media (prefers-reduced-motion:reduce){
  @R@ .up-em::before,@R@ .up-ar::after,@R@ .sz-abs .sz-ab>.sz-face::after,@R@ .up-pip>i::after,@R@ .gd-tr>i::after,@R@ :is(.sp-tr,.sp-ld,.sp-cl,.up-pip,.jb-tr,.gd-tr,.up-3)>i,@R@ :is(.sp-tr,.sp-cl>i,.up-bar)::after,@R@ .up-ck{animation:none!important}
  @R@ .up-ar::after{opacity:0}
}
/* ---------- 窄窗和手机：进阶牌两列，职业上下排，书里一条占满一行 ---------- */
@media (max-width:1099px){
  @R@ .sz-abs .sz-ab>.sz-face{grid-column:1 / -1}
  @R@ .sz-abs .sz-it>.sz-face::before{display:none}
  @R@ .sz-abs .sz-tip .sp-ch.big{justify-content:flex-start}
}
@media (max-width:720px){
  @R@ .sp-up{padding:12px 10px 11px}
  @R@ .up-h{flex-wrap:wrap;gap:8px 10px}
  @R@ .up-em{width:38px;height:38px}
  @R@ :is(.up-fr,.up-to)>b{font-size:17px!important}
  @R@ .up-ti{flex:1 1 100%;margin-left:0;justify-items:start;text-align:left;border-radius:10px 3px 3px 10px;padding:5px 16px 6px 12px;background:linear-gradient(90deg, color-mix(in srgb, var(--fm-acc) 22%, transparent), transparent);box-shadow:inset 2px 0 0 var(--fm-acc)}
  @R@ .up-g{grid-template-columns:repeat(2,minmax(0,1fr));grid-template-areas:"lv xu" "pl pl" "bk bk" "hr hr";gap:7px}
  @R@ .up-pip>i>b{font-size:10.5px!important;letter-spacing:0}
  @R@ .up-ti{grid-auto-flow:row;gap:1px}
  @R@ .up-3>i::before{display:block}
  @R@ .sp-job{grid-template-columns:minmax(0,1fr);gap:10px;padding:11px 12px}
  @R@ .jb-f{padding-top:8px}
  @R@ .sp-god{grid-template-columns:minmax(0,1fr);padding:12px}
  @R@ .gd-n{grid-template-columns:auto auto 1fr;align-items:baseline;justify-items:start;column-gap:10px}
  @R@ .gd-tr>i>b{font-size:11px!important;letter-spacing:0}
  @R@ .sp-tr>i>b{font-size:10px!important}
  @R@ .sz-abs .sz-ab>.sz-face{padding:8px 9px 8px 8px}
}
'''


def css():
    P = R + ' '
    o = [CSS]
    w = o.append
    # 七境的底数（等级那一条从这一境的头一级起算）、走过几道门槛、眼下要过哪一道
    for i, t in enumerate(TIERN):
        w(P + '.sp-up[data-f^="%s"]{--fl:%d;--ps:%d}' % (t, FLOOR[t], min(i, 5)))
        if i:
            w(P + '.sp-up[data-f^="%s"] .up-pip>i:nth-child(-n+%d){--on:1}' % (t, min(i, 5)))
        if i < 5:
            w(P + '.sp-up[data-f^="%s"] .up-pip>i:nth-child(%d){--cur:1}' % (t, i + 1))
            w(P + '.sp-up[data-f^="%s"] .up-pip>i:nth-child(%d)::after{animation:sp-ping 1.8s ease-out infinite}' % (t, i + 1))
            w(P + '.sp-up[data-f^="%s"]:is(%s) .up-pip>i:nth-child(%d){--on:1}' % (t, ','.join('[data-c*="%s"]' % d for d in DONE), i + 1))
    w(P + '.sp-up:is(%s){--gk:1}' % ','.join('[data-c*="%s"]' % d for d in DONE))
    # 英雄那一境：伟业簿三格、三个小能级照等级亮；传奇以后都亮着
    w(P + '.sp-up[data-f^="英雄"] .up-s3{display:grid}')
    for k in range(3):
        w(P + '.sp-up[data-f^="英雄"] .up-s3>i:nth-child(%d){--on:clamp(0, calc(var(--bn) - %d), 1)}' % (k + 1, k))
    for k, lv in enumerate([120, 146, 173]):
        w(P + '.sp-up[data-f^="英雄"] .up-3>i:nth-child(%d){--on:clamp(0, calc(var(--lv) - %d), 1)}' % (k + 1, lv))
    w(P + '.sp-up:is([data-f^="传奇"],[data-f^="凡极"]) .up-3>i{--on:1}')
    w(P + '.sp-up:is([data-h=""],[data-h="无"],[data-h="暂无"],[data-h="未开"]) .c-hr .up-s{display:none}')
    w(P + '.sp-up:not([data-f^="英雄"],[data-f^="传奇"],[data-f^="凡极"]) .c-hr .up-s{display:none}')
    w(P + '.c-xu[data-a=""] b>em{display:none}')
    # 神力：五档
    for i, t in enumerate(GODT):
        w(P + '.sp-god[data-g^="%s"] .gd-tr{--gn:%d}' % (t, i + 1))
        w(P + '.sp-god[data-g^="%s"] .gd-tr>i:nth-child(-n+%d){--on:1}' % (t, i + 1))
        w(P + '.sp-god[data-g^="%s"] .gd-tr>i:nth-child(%d){--cur:1}' % (t, i + 1))
        w(P + '.sp-god[data-g^="%s"] .gd-tr>i:nth-child(%d)::after{animation:sp-flick 2.4s ease-in-out infinite}' % (t, i + 1))
        w(P + '.gd-tr>i:nth-child(%d)>b::after{content:"%s"}' % (i + 1, GODR[i]))
    # 职业：照位阶定走到哪一个节点，这一行里写了 Ⅰ 到 Ⅳ 的照写的；品阶的颜色照名字后头括号里那一档
    for i, t in enumerate(TIERN):
        w('%s .p-deed:has(.sz-goal[data-t^="%s"]) .sp-job{--jt:%d}' % (R, t, min(max(i, 0), 4)))
    for i, r in enumerate(ROMAN):
        w(P + '.sp-job[data-j*="%s"]{--je:%d}' % (r, i + 1))
        w(P + '.jb-tr>i:nth-child(%d){--k:%d}' % (i + 1, i + 1))
        w(P + '.jb-tr>i:nth-child(%d)::before{content:"%s"}' % (i + 1, r))
        w(P + '.jb-tr>i:nth-child(%d)>b::after{content:"LVL %d"}' % (i + 1, [21, 41, 81, 121][i]))
    w(P + '.sp-job:is([data-j^="未就职"],[data-j^="未认兵"],[data-j^="待校准"],[data-j=""]){--je:0}')
    for c, kws in [('#4f8fd8', ['Rare', '稀有']), ('#a06be0', ['Epic', '史诗']), ('#e0a63c', ['Legend', '传说']), ('#e25a4e', ['Unique', '唯一'])]:
        w(P + '.sp-job:is(%s){--q:%s}' % (','.join('[data-j*="%s"]' % k for k in kws), c))
    # Art：学到第几阶（阿拉伯数字和汉字都认），亮几个节点，线走到哪
    for i in range(5):
        lv = ':is([data-lv="%d"],[data-lv="%s"])' % (i + 1, CN[i])
        w(P + '.sp-art%s{--n:%d;--lvt:"%s阶"}' % (lv, i + 1, CN[i]))
        w(P + '.sp-art%s :is(.sp-tr,.sp-ld)>i:nth-child(-n+%d){--on:1;--s:""}' % (lv, i + 1))
        w(P + '.sp-art%s :is(.sp-tr,.sp-ld)>i:nth-child(%d){--cur:1;--s:" · 此刻"}' % (lv, i + 1))
        if i:
            w(P + '.sp-art%s .sp-ld>i:nth-child(-n+%d){--ln:1}' % (lv, i))
        w(P + ':is(.sp-tr,.sp-ld)>i:nth-child(%d)::before{content:"%s"}' % (i + 1, CN[i]))
        w(P + '.sp-ld>i:nth-child(%d){--t:"%s阶"}' % (i + 1, CN[i]))
    # Skill：五档（生手、熟手、匠人、名匠、宗匠），到了几档亮几格；后头写了百分数的，下一格填到那里
    five = ':is(%s)' % ','.join('[data-p^="%s"]' % t for t in TIERS5)
    for i, t in enumerate(TIERS5):
        w('.sz-it.sp-sk[data-p^="%s"]{--q:%s;--tg:@T%d@}' % (t, SKQ[i], i + 1))
        w(P + '.sp-sk[data-p^="%s"] .sp-cl>i:nth-child(-n+%d){--f:1}' % (t, i + 1))
        w(P + '.sp-cl.big>i:nth-child(%d){--g:@T%d@}' % (i + 1, i + 1))
        if i < 4:
            w(P + '.sp-sk[data-p^="%s"] .sp-cl:not(.big)>i:nth-child(%d){--f:calc(var(--pg) / 100)}' % (t, i + 2))
            w(P + '.sp-sk[data-p^="%s"] .sp-cl.big>i:nth-child(%d){--nxt:1}' % (t, i + 2))
            w(P + '.sp-sk[data-p^="%s"]{--nx:" · %s";--nq:%s}' % (t, TIERS5[i + 1], SKQ[i + 1]))
    out = '\n'.join(o) + '\n'
    masks = [('STAR', M_STAR), ('CHECK', M_CHECK), ('LOCK', M_LOCK), ('HOUR', M_HOUR), ('DROP', M_DROP), ('BOLT', M_BOLT), ('FLAME', M_FLAME),
             ('ARROWH', _mask('<path d="M8 5l8 7-8 7"/>')), ('BOOK', M_BOOK), ('SEAL', M_SEAL)] + [('T%d' % (i + 1), m) for i, m in enumerate(M_TIER)]
    out = out.replace('@MASKVARS@', ';'.join('--spm-%s:%s' % (k.lower(), v) for k, v in masks))
    for k, v in masks:
        out = out.replace('@%s@' % k, 'var(--spm-%s)' % k.lower())
    for a, b in [('@FIVE@', five), ('@HEX@', HEX), ('@PRISM@', PRISM),
                 ('@INK2@', INK2), ('@INK@', INK), ('@RED@', RED), ('@LINE@', LINE), ('@R@', R)]:
        out = out.replace(a, b)
    return out


if __name__ == '__main__':
    import json
    json.dump(rules(), open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if len(sys.argv) > 2:
        open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(css())
    print(len(RULES), '条规则', len(css()), '字样式')
