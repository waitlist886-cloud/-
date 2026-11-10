# 主角立绘（11-10，用户：“根据我们现在的这个成长建档来，根据玩家最后判定得到的出生地（种族分支）与选择的命路，人类的话准备两种性别各三种体格……”）
# 一、体格表：建档器「体态」那一格添一排体格，点哪个就把体格写进凭证；人类男女各三种（用户定的），别的族照这张表（★，底稿/立绘/主角预设/计划.md）。
# 二、建档器：体格一排、预设立绘的预览、自己的立绘地址；凭证添一行「立绘：预设·族属·性别·体格」或者图片地址。
# 三、预设立绘的样式：图床清单 gh_pc.json 里有的预设，一个键一组变量（--pcp- 四套衣着、--pcf- 九格表情、--pca- 艺术照），对话框和面板照「§面板｜立绘」那一行指过去（make_rules_frame.py 的 主角·立绘）。
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
COMFY = os.path.join(os.path.dirname(HERE), 'comfy')
HOST = os.path.join(COMFY, 'out', '图床')

BODY = {
    '人类': {'男': [('健壮', '约两米，高大魁梧的肌肉身材'), ('中等', '一米八五上下，肩宽腰窄的倒三角'), ('偏瘦', '一米八五上下，修长偏瘦')],
             '女': [('丰腴', '丰满的曲线，G-cup 上下'), ('均匀', '黄金比例，E-cup 上下'), ('纤细', '纤细轻盈，C-cup 上下')]},
    '精灵': {'男': [('中等', '一米八八上下，修长挺拔'), ('偏瘦', '一米八五上下，清瘦颀长')],
             '女': [('均匀', '高挑匀称'), ('纤细', '纤细修长')]},
    '矮人': {'男': [('敦实', '一米四上下，宽肩粗臂，结实敦厚')], '女': [('敦实', '一米三五上下，结实圆润')]},
    '半身人': {'男': [('小个子', '一米上下，圆脸小个子')], '女': [('小个子', '一米上下，圆脸小个子')]},
    '兽耳族': {'男': [('健壮', '一米九上下，结实矫健'), ('中等', '一米八上下，精干匀称')],
              '女': [('均匀', '一米七上下，匀称矫健'), ('纤细', '一米六五上下，轻盈灵巧')]},
    '半兽人': {'男': [('魁梧', '两米一上下，獠牙壮汉'), ('健壮', '一米九五上下，结实粗壮')],
              '女': [('健壮', '一米八五上下，结实有力'), ('均匀', '一米七八上下，匀称有力')]},
    '龙裔': {'男': [('健壮', '一米九五上下，宽厚结实'), ('中等', '一米八五上下，匀称挺拔')],
            '女': [('均匀', '一米七五上下，高挑匀称'), ('纤细', '一米七上下，修长纤细')]},
    '真龙幼体': {'男': [('化形', '化成人形，刚成年的样子，一米八上下')], '女': [('化形', '化成人形，刚成年的样子，一米七上下')]},
    '魔族': {'男': [('健壮', '一米九五上下，高大结实'), ('中等', '一米八五上下，肩宽腰窄'), ('偏瘦', '一米八五上下，修长偏瘦')],
            '女': [('丰腴', '丰满的曲线'), ('均匀', '黄金比例'), ('纤细', '纤细轻盈')]},
    '提夫林': {'男': [('中等', '一米八五上下，匀称挺拔'), ('偏瘦', '一米八上下，修长偏瘦')],
              '女': [('均匀', '高挑匀称'), ('纤细', '纤细轻盈')]},
}


def presets():
    """图床上有的主角预设：键（晨曦人·男·健壮）→ {por, face, art}。清单是 gh_img_up.py 推 pc 那一套写的 gh_pc.json。"""
    p = os.path.join(HOST, 'gh_pc.json')
    if not os.path.exists(p):
        return {}
    man = {k: v['url'] for k, v in json.load(open(p, encoding='utf-8')).items()}
    names = {}
    for f in __import__('glob').glob(os.path.join(COMFY, 'cast', '主角', '*.json')):
        for e in json.load(open(f, encoding='utf-8')):
            names[e['en']] = e['name']
    out = {}
    for en, nm in names.items():
        if 'por_%s.webp' % en in man and 'face_%s.webp' % en in man:
            out[nm] = {'por': man['por_%s.webp' % en], 'face': man['face_%s.webp' % en], 'art': man.get('art_%s.webp' % en, '')}
    return out


def css_lines():
    """一个预设一组变量，挂在外壳上（:root 平台换成 .custom-styles），对话框和面板那一段样式照键指过来。"""
    lines = []
    for nm, u in sorted(presets().items()):
        k = nm.replace('·', '-')
        v = ['--pcp-%s:url("%s")' % (k, u['por']), '--pcf-%s:url("%s")' % (k, u['face']), '--pci-%s:none' % k, '--pcs-%s:auto 100%%' % k,
             '--pcn-%s:1' % k, '--pcz-%s:block' % k]
        if u['art']:
            v.append('--pca-%s:url("%s")' % (k, u['art']))
        lines.append(':root:has(#conversation){%s}' % ';'.join(v))
    return lines


# ---------------- 建档器 ----------------
# 11-10 用户：“同时留给玩家自己填入预设立绘的入口”。三条路：照族属和体格自动挑；从全部预设里点一张；贴自己的图（全身一张，头像一张可留空）。
# 游戏里要换，输入框菜单里有「主角立绘」那一项（OPTION），AI 从那一轮起照新的抄。
PC_HTML = ('<div class="pc-pick" id="pc_pick"><h3>体格与立绘 <small>选一种体格，对话框里主角开口、面板上那个人都用这一族、这一种体格的立绘；也可以从下面的预设里点一张，或者贴自己的图</small></h3>'
           '<div class="chips" id="pc_body_row"></div><div class="pc-prev" id="pc_prev"></div>'
           '<div class="pc-gal-h">全部预设 <small>点一张就用那一张，再点一下取消</small></div><div class="pc-gal" id="pc_gal"></div>'
           '<input id="pc_url" placeholder="或者贴自己的立绘：全身图的图片地址（https 开头，竖图最好，可留空）" oninput="pcPrev()">'
           '<input id="pc_face" placeholder="头像的图片地址（可留空，留空就从全身图的上半截裁）" oninput="pcPrev()"></div>')
PC_CSS = ('<style>.pc-pick{margin-top:6px}.pc-pick .chips{display:flex;flex-wrap:wrap;gap:8px}.pc-pick .pick-chip small{display:block;font-size:11px;opacity:.75;font-weight:400}'
          '.pc-prev{display:flex;gap:12px;align-items:flex-start;margin:10px 0;font-size:12.5px;line-height:1.7;opacity:.9}'
          '.pc-prev img{width:120px;aspect-ratio:2/3;object-fit:cover;border-radius:10px;box-shadow:0 6px 18px rgba(0,0,0,.45)}'
          '.pc-prev img.f{width:64px;aspect-ratio:1;border-radius:50%}'
          '.pc-gal-h{margin:8px 0 6px;font-size:13px;opacity:.9}.pc-gal-h small{opacity:.7;margin-left:6px}'
          '.pc-gal{display:flex;gap:8px;overflow-x:auto;padding-bottom:6px;scrollbar-width:thin}'
          '.pc-g{flex:none;width:74px;padding:0;border:0;border-radius:9px;background:none;cursor:pointer;color:inherit;opacity:.82;text-align:center}'
          '.pc-g img{display:block;width:74px;aspect-ratio:2/3;object-fit:cover;border-radius:9px;box-shadow:0 0 0 1px rgba(214,178,106,.35)}'
          '.pc-g small{display:block;margin-top:3px;font-size:10.5px;line-height:1.3;opacity:.85}'
          '.pc-g.active{opacity:1}.pc-g.active img{box-shadow:0 0 0 2px #e6c66e,0 0 12px rgba(230,198,110,.5)}'
          '#pc_url,#pc_face{width:100%;margin-top:6px}</style>')


def pc_js(arts):
    return ('<script>(function(){'
            'var PC_BODY=%s;var PC_ART=%s;'
            'function S(){return (typeof state!=="undefined")?state:{};}'
            'function race(){var r=S().race||"";if(PC_BODY[r])return r;for(var k in PC_BODY){if(r.indexOf(k)>=0)return k;}return r;}'
            'function eth(){var e=S().birthEthnic||"";if(e)return e;try{var p=birthplacePool[race()];if(p&&p[0])return p[0].e;}catch(x){}return "";}'
            'function url(id){var u=((document.getElementById(id)||{}).value||"").trim();return /^https?:\\/\\/[^\\s"\'<>()\\\\｜]{8,400}$/.test(u)?u:"";}'
            'window.pcLine=function(){var u=url("pc_url"),f=url("pc_face");if(u)return u+(f?"｜头像:"+f:"");if(S().pcPick)return "预设·"+S().pcPick;'
            'var r=race(),g=S().gender||"",b=S().pcBody||"";'
            'var L=(PC_BODY[r]||{})[g]||[];for(var i=0;i<L.length;i++){if(L[i][0]===b){var e=eth();return e?("预设·"+e+"·"+g+"·"+b):"无";}}return "无";};'
            'window.pcPrev=function(){var box=document.getElementById("pc_prev");if(!box)return;var u=url("pc_url"),f=url("pc_face");var line=pcLine();'
            'var img=u||PC_ART[line.replace(/^预设·/,"")]||"";'
            'box.innerHTML=(img?"<img src=\\""+img+"\\" alt=\\"\\">":"")+(f?"<img class=\\"f\\" src=\\""+f+"\\" alt=\\"\\">":"")+"<div>"+(u?("用你贴的这张图"+(f?"，头像用另一张。":"，头像从它的上半截裁。")):(line==="无"?"还没选体格。选了以后，凭证里写上这一族、这一种体格的预设立绘。":("凭证里写："+line+(img?"":"<br>这一族、这一种体格的预设立绘还在画，先用剪影。"))))+"</div>";};'
            'function gal(){var g=document.getElementById("pc_gal");if(!g)return;var ks=Object.keys(PC_ART).filter(function(k){return PC_ART[k];});'
            'if(!ks.length){g.innerHTML="<span class=\\"hint\\">预设立绘还在画。</span>";return;}'
            'g.innerHTML=ks.map(function(k){return "<button class=\\"pc-g"+(S().pcPick===k?" active":"")+"\\" type=\\"button\\" data-k=\\""+k+"\\"><img src=\\""+PC_ART[k]+"\\" alt=\\"\\" loading=\\"lazy\\"><small>"+k+"</small></button>";}).join("");'
            'Array.prototype.forEach.call(g.querySelectorAll(".pc-g"),function(b){b.onclick=function(){var k=b.getAttribute("data-k");if(typeof state!=="undefined"){state.pcPick=(state.pcPick===k)?"":k;}'
            'Array.prototype.forEach.call(g.querySelectorAll(".pc-g"),function(o){o.classList.toggle("active",S().pcPick===o.getAttribute("data-k"));});pcPrev();};});}'
            'window.pcRender=function(){gal();var row=document.getElementById("pc_body_row");if(!row)return;var r=race(),g=S().gender||"";'
            'var L=(PC_BODY[r]||{})[g]||[];if(!L.length){row.innerHTML="<span class=\\"hint\\">"+(g&&g!=="男"&&g!=="女"?"这个性别没有按体格分的预设，可以从下面挑一张，或者贴自己的图。":"先选种族和性别，这里会列出能选的体格。")+"</span>";pcPrev();return;}'
            'row.innerHTML=L.map(function(x){return "<button class=\\"pick-chip"+(S().pcBody===x[0]?" active":"")+"\\" type=\\"button\\" data-b=\\""+x[0]+"\\">"+x[0]+"<small>"+x[1]+"</small></button>";}).join("");'
            'Array.prototype.forEach.call(row.querySelectorAll(".pick-chip"),function(b){b.onclick=function(){if(typeof state!=="undefined")state.pcBody=b.getAttribute("data-b");'
            'Array.prototype.forEach.call(row.querySelectorAll(".pick-chip"),function(o){o.classList.toggle("active",o===b);});'
            'var pb=document.getElementById("p_build");var d="";for(var i=0;i<L.length;i++){if(L[i][0]===S().pcBody)d=L[i][1];}if(pb)pb.value=S().pcBody+"（"+d+"）";pcPrev();};});pcPrev();};'
            'document.addEventListener("DOMContentLoaded",function(){try{pcRender();}catch(e){}});'
            'document.addEventListener("click",function(ev){if(ev.target&&ev.target.closest&&ev.target.closest("#p_gender_row,.race-card,[onclick*=Race],[onclick*=race]")){setTimeout(function(){try{pcRender();}catch(e){}},30);}},true);'
            '})();</script>') % (json.dumps({r: {g: [list(x) for x in v] for g, v in d.items()} for r, d in BODY.items()}, ensure_ascii=False), json.dumps(arts, ensure_ascii=False))


# 输入框菜单：游戏里换主角立绘（贴图片地址，或者写 预设·族属·性别·体格）
OPTION = ('主角立绘', '【主角立绘】立绘：https://（全身图的图片地址，或者写 预设·族属·性别·体格）｜头像：https://（头像的图片地址，可留空）')


def options(o):
    items = [dict(x) for x in o['items']]
    if OPTION[0] not in {x['label'] for x in items}:
        items.append({'order': len(items), 'label': OPTION[0], 'type': 'SET-INPUT', 'value': OPTION[1]})
    return {'items': items}


def intro(t):
    """建档器添体格一排、预览、自己的立绘地址；凭证添一行立绘。对不上就停。"""
    arts = {nm: (u['art'] or '') for nm, u in presets().items()}
    a = '<input id="p_build" placeholder="体格 如 修长紧实 / 结实敦厚 / 纤细"></div>'
    assert t.count(a) == 1, ('体态那一格', t.count(a))
    t = t.replace(a, a + PC_HTML)
    a = "（静态资产，状态栏逐轮照抄，正文不主动报数）\\n自定义设定："
    assert t.count(a) == 1, ('凭证', t.count(a))
    t = t.replace(a, "（静态资产，状态栏逐轮照抄，正文不主动报数）\\n立绘：${(typeof pcLine==='function'?pcLine():'无')}\\n自定义设定：")
    a = 'function pickGender(g,el){\n state.gender=g;'
    assert t.count(a) == 1, ('性别', t.count(a))
    t = t.replace(a, a + " try{pcRender();}catch(e){}")
    i = t.rindex('</body>')
    return t[:i] + PC_CSS + pc_js(arts) + t[i:]
