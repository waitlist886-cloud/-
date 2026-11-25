# 风月四张外壳的简介页（11-25）：换成薄壳，门面的页面、数据和图从图床取，认指针，跟日里用同一套门面（底稿/门面/共用/make_thin.py 的模板，这里不改它）。
# 风月这一头不一样的三样，都只写在卡里这一段薄壳里，图床上的门面分支一个字不动：
#   一、每张卡直接开到它那一纪的书：薄壳往取回来的外壳页里先塞一小段（ADAPTER），等外壳的 Shell.openBook 有了就翻开这一纪的书
#       （迷宫纪那一张翻开“此刻”，1001 年那一本）。这一张卡没有的纪：书尾翻下一本、牌桌上选了别的纪、点“此刻”那张牌，拦下来说一句。
#       牌桌还回得去（迷宫纪那一张要从牌桌进前传那一本，大图书馆的入口也在牌桌上）。
#   二、风月没有“点一下填进输入框”：确认页和接续旅印里那一枚“填进输入框”拿掉，“复制”做成主钮，说明换成复制的说法。
#   三、图床连不上时的退路：一页简式建档（lite_page.py 的那一页），只留这一张卡里的纪，拿掉填输入框那一枚。日里那一页里有平台的指令名，风月的屏蔽词不让带。
# FRONT_CFG 里顺手带上 start、only、nofill 三格，外壳往后要是自己认了（见 外壳_说明.md“门面要是想做得更干净”），这一小段就可以拿掉。
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
COMMON = os.path.join(ROOT, '底稿', '门面', '共用')
if COMMON not in sys.path:
    sys.path.insert(0, COMMON)
sys.dont_write_bytecode = True

# 这一张卡开哪一本、认哪几本（书的键：moon strife bronze maze now；now 是迷宫纪 1001 年那一本“此刻”，maze 是前传那一本）
BOOKS = {
    'maze': dict(start='now', only=['now', 'maze'], name='迷宫纪（前传和 1001 年）', lite=['maze'], lite1001=True),
    'moon': dict(start='moon', only=['moon'], name='月银纪', lite=['moon'], lite1001=False),
    'strife': dict(start='strife', only=['strife'], name='纷争纪', lite=['strife'], lite1001=False),
    'bronze': dict(start='bronze', only=['bronze'], name='山铜纪', lite=['bronze'], lite1001=False),
}

ADAPTER = r'''(function(){
var START=__START__,ONLY=__ONLY__,CARD=__CARD__,BOOKS=['moon','strife','bronze','maze','now'],tipEl=null,tipT=0;
function note(){try{
 if(!tipEl){tipEl=document.createElement('div');tipEl.setAttribute('role','status');
  tipEl.style.cssText='position:fixed;left:0;right:0;bottom:12%;margin:0 auto;width:fit-content;box-sizing:border-box;z-index:99999;max-width:86vw;padding:12px 18px;font:14px/1.8 "Noto Serif SC","Songti SC",serif;letter-spacing:.06em;color:#ece5d6;background:rgba(10,11,18,.94);border:1px solid rgba(255,176,104,.6);box-shadow:0 10px 30px rgba(0,0,0,.6);text-align:center;transition:opacity .3s;pointer-events:none';
  document.body.appendChild(tipEl);}
 tipEl.textContent='这一张卡里只有'+CARD+'。别的纪元各是另一张卡，从那一张的简介页进。';
 tipEl.style.opacity='1';clearTimeout(tipT);tipT=setTimeout(function(){tipEl.style.opacity='0';},3600);
}catch(e){}}
function ok(b){return ONLY.indexOf(b)>=0;}
window.addEventListener('message',function(ev){var m=ev.data||{};if(m&&m.aldran&&m.t==='goto'&&m.book&&!ok(m.book)){ev.stopImmediatePropagation();note();}});
document.addEventListener('click',function(e){var t=e.target;if(!t||!t.closest)return;
 if(t.closest('#openBook')){var k=-1;try{k=window.Shell&&Shell.state?Shell.state.picked:-1;}catch(x){}if(!(k>=0)&&window.__tb)k=window.__tb.picked;if(k>=0&&BOOKS[k]&&!ok(BOOKS[k])){e.stopImmediatePropagation();e.preventDefault();note();}}
 else if(t.closest('#nowCard')&&!ok('now')){e.stopImmediatePropagation();e.preventDefault();note();}
},true);
var n=0;
(function w(){var S=window.Shell;
 if(S&&S.openBook){setTimeout(function(){try{var st=S.state||{};if(!st.cur&&!st.build&&!st.seal&&!st.old)S.openBook(START);}catch(e){}},200);return;}
 if(n++<300)setTimeout(w,100);})();
function fix(){try{
 var bs=document.querySelectorAll('[data-a="fill"],[data-a="rfill"]');
 for(var i=0;i<bs.length;i++){var b=bs[i],p=b.parentNode,c=p&&p.querySelector('[data-a="copy"],[data-a="rcopy"]');if(c)c.classList.add(b.getAttribute('data-a')==='fill'?'go':'pri');if(p)p.removeChild(b);}
 var s=document.querySelector('.sl-hd .sub');if(s&&s.textContent.indexOf('填进输入框')>=0)s.textContent='复制下来，回到聊天的输入框里粘贴，再发送。';
}catch(e){}}
try{new MutationObserver(fix).observe(document.documentElement,{childList:true,subtree:true});}catch(e){}
})();'''


def once(s, a, b, what=''):
    assert s.count(a) == 1, ('对不上', what, s.count(a), a[:60])
    return s.replace(a, b)


def lite_fy(card_key):
    """简式建档那一页的风月版：只留这一张卡里的纪，不带填输入框那一枚。lite_page.py 的模板对不上就不要这一页（返回 None）"""
    import lite_page as LP
    B = BOOKS[card_key]
    try:
        s = LP.PAGE
        s = once(s, '挑一个时代，写下名字，点“填进输入框”再发送，就从那里睁眼。', '写下名字，点“复制”，回到聊天的输入框里粘贴再发送，就从那里睁眼。', '说明')
        s = once(s, '<button type="button" id="fill">填进输入框</button><button type="button" class="o" id="copy">复制</button>', '<button type="button" id="copy">复制</button>', '钮')
        m = re.findall(r"^  \$\('fill'\)\.onclick = [^\n]*\n", s, re.M)
        assert len(m) == 1, len(m)
        s = s.replace(m[0], '')
        if not B['lite1001']:
            s = once(s, """era.innerHTML = '<option value="1001">迷宫纪 1001 年</option>' + D.eras.map(""", "era.innerHTML = D.eras.map(", '1001 那一格')
            s = once(s, '\n  shape();\n})();', '\n  fillLines();\n  shape();\n})();', '开页就列主线')
        d = LP.data()
        d['eras'] = [e for e in d['eras'] if e['b'] in B['lite']]
        assert len(d['eras']) == len(B['lite'])
        js = json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        s = once(s, '__DATA__', js, '数据')
        assert 'fill' not in re.sub(r'fillLines', '', s), '填输入框那一枚没拿干净'
        return s
    except AssertionError as e:
        print('  简式建档的模板跟这里对不上，这一张的薄壳不带退路：', e)
        return None


def build(card_key, ver='11-25fy'):
    """返回 (简介页的 HTML, 账)"""
    import make_thin as MT
    B = BOOKS[card_key]
    cfg = json.load(open(os.path.join(COMMON, 'front.json'), encoding='utf-8'))
    for b in B['only']:
        assert b in cfg['books'], ('指针里没有这一本', b)
    s = MT._thin(cfg, None, ver, None)
    lite = lite_fy(card_key)
    # 说退路的那几句
    s = once(s, '取不到的时候退回卡里原来那一整页介绍页（迷宫纪 1001 年的建档器和世界之书），它就存在上面那一段里。', '取不到的时候换成一页简式建档（不连外网），它就存在上面那一段里。', '注')
    s = once(s, '载得慢？先用原来的介绍页', '载得慢？先用简式建档', '慢')
    s = once(s, '，也可以先用原来的介绍页，迷宫纪 1001 年的建档和世界之书都在里头。另外三纪不看门面也能开始，点输入框底下的开局快捷键就行。', '，也可以先用简式建档，填几样就能开始。', '退路')
    s = once(s, '；也可以不看门面，直接点输入框底下的开局快捷键，照样能开始。', '；也可以不看门面，直接点输入框上头的开局快捷指令，照样能开始。', '没退路')
    s = once(s, '用原来的介绍页</button>', '用简式建档</button>', '钮')
    # 外壳页里先塞一小段
    js = ADAPTER.replace('__START__', json.dumps(B['start'])).replace('__ONLY__', json.dumps(B['only'])).replace('__CARD__', json.dumps(B['name'], ensure_ascii=False))
    assert not re.search(r'__[A-Z]+__', js) and '</' not in js and '<!--' not in js
    lit = json.dumps('<script>' + js + '</script>', ensure_ascii=False).replace('</', '<\\/')
    s = once(s, "  var boot = document.getElementById('boot'),", '  var FYAD = ' + lit + ', FYS = ' + json.dumps(B['start']) + ', FYO = ' + json.dumps(B['only']) + ';\n' + "  var boot = document.getElementById('boot'),", '塞变量')
    s = once(s, "old1001: m + SH + 'old1001.html' };", "old1001: m + SH + 'old1001.html', start: FYS, only: FYO, nofill: 1 };", '配置')
    s = once(s, "';<\\/script></head><body>' + html", "';<\\/script>' + FYAD + '</head><body>' + html", '塞脚本')
    s = once(s, '__OLD__', MT.old_block(lite) if lite else '', '退路')
    assert 'FRONT_CFG' in s and '__OLD1001' in s
    return s, {'字': len(s), '字节': len(s.encode('utf-8')), '翻开': B['start'], '认': B['only'], '退路': bool(lite), '指针': 'g%s' % cfg.get('g')}


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    out = sys.argv[2] if len(sys.argv) > 2 else None
    for k in ([sys.argv[1]] if len(sys.argv) > 1 else list(BOOKS)):
        s, a = build(k)
        print(k, a)
        if out:
            open(out, 'w', encoding='utf-8', newline='\n').write(s)
