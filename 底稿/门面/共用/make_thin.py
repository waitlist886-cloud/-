#!/usr/bin/env python3
# 卡里介绍页的那一段薄壳（11-15 拼装那一轮）。页面、数据和图都在图床上（deploy_front.py 推的），这一段只管：
#   挨个试 jsDelivr 的几个镜像，取到外壳那一页（front_shell 那一段的 index.html）就整页换上去，<base> 指到那一段，
#   四本书各段的地址写进 window.FRONT_CFG 交给外壳（shell.js）。都取不到就留一句话和一个重试的钮。
# 日里的介绍页是沙箱里的 srcdoc：外链能取（11-12 探针量过，六个镜像都通），没有 localStorage，这一格先按 0×0 建出来，所以等有了大小再换页。
#   python -I -X utf8 底稿/门面/共用/make_thin.py            照 共用/front.json 出 小样_外壳/thin.html（给本地的假日里壳看）
#   python -I -X utf8 底稿/门面/共用/make_thin.py --local http://localhost:8773/    不走图床，照本地带跨域头的服务器出（cors_server.py）
# into_card.py 调 thin_html() 把它写进卡的 introPage。
import io
import json
import os
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.normpath(os.path.join(HERE, '..'))
MIRRORS = ['https://cdn.jsdelivr.net/', 'https://fastly.jsdelivr.net/', 'https://gcore.jsdelivr.net/', 'https://testingcf.jsdelivr.net/', 'https://quantil.jsdelivr.net/']
BOOK_DIR = {'moon': '小样_月银纪书', 'strife': '小样_纷争纪书', 'bronze': '小样_山铜纪书', 'maze': '小样_迷宫纪书'}

TPL = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>奥尔德兰的旅印</title>
<style>
html,body{margin:0;height:100%;background:#04050a;color:#ece5d6;font-family:"Noto Serif SC","Songti SC","SimSun",serif}
#boot{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;padding:24px;text-align:center}
#boot i{width:7px;height:7px;border-radius:50%;background:#ffb068;box-shadow:0 0 18px 6px rgba(255,176,104,.5);animation:bp 1.6s ease-in-out infinite}
#boot p{margin:0;font-size:13px;letter-spacing:.3em;text-indent:.3em;line-height:2.1;color:rgba(236,229,214,.72)}
#boot p.s{letter-spacing:.08em;text-indent:0;max-width:30em;font-size:13.5px}
#boot button{font:inherit;font-size:13px;letter-spacing:.3em;text-indent:.3em;color:#ece5d6;background:rgba(255,176,104,.16);border:1px solid rgba(255,176,104,.6);padding:9px 22px;cursor:pointer}
#boot button.o{background:none;border-color:rgba(236,229,214,.32);color:rgba(236,229,214,.8)}
#boot .row{display:flex;flex-wrap:wrap;gap:12px;justify-content:center}
#boot #slow{position:absolute;left:0;right:0;bottom:max(26px,env(safe-area-inset-bottom));display:flex;justify-content:center}
#boot #slow button{font-size:12px;letter-spacing:.16em;text-indent:.16em;padding:7px 16px}
@keyframes bp{0%,100%{transform:scale(1);opacity:.75}50%{transform:scale(1.5);opacity:1}}
</style>
</head>
<body>
<div id="boot"><i></i><p id="bt">死 之 神 殿</p></div>
__OLD__<script>
/* 奥尔德兰的旅印 · 门面 __VER__。这一页只是个壳：门面的页面、数据和图都放在图床上，这里挨个镜像去取。
   取不到的时候退回卡里原来那一整页介绍页（迷宫纪 1001 年的建档器和世界之书），它就存在上面那一段里。 */
(function () {
  var MIR = __MIR__, SH = __SH__, BOOKS = __BOOKS__, VER = '__VER__';
  var boot = document.getElementById('boot'), OLD = window.__OLD1001 || null, done = false, slow = null;
  function useOld() { if (done || !OLD) return; done = true; clearTimeout(slow); document.open(); document.write(OLD); document.close(); }
  function bindOld() { var b = document.getElementById('useold'); if (b) b.onclick = useOld; }
  function wait() {
    boot.innerHTML = '<i></i><p>死 之 神 殿</p>';
    clearTimeout(slow);
    if (OLD) slow = setTimeout(function () { if (done || document.getElementById('useold')) return; var d = document.createElement('div'); d.id = 'slow'; d.innerHTML = '<button type="button" class="o" id="useold">载得慢？先用原来的介绍页</button>'; boot.appendChild(d); bindOld(); }, 8000);
  }
  function get(u, ms) {
    return new Promise(function (ok, no) {
      var c = window.AbortController ? new AbortController() : null;
      var t = setTimeout(function () { if (c) c.abort(); no(new Error('timeout')); }, ms);
      fetch(u, c ? { signal: c.signal } : {}).then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
        .then(function (x) { clearTimeout(t); if (x.length < 2000 || x.indexOf('shell.js') < 0) no(new Error('short')); else ok(x); }, function (e) { clearTimeout(t); no(e); });
    });
  }
  function sized() { return new Promise(function (ok) { var n = 0; (function w() { if ((window.innerWidth > 0 && window.innerHeight > 0) || n++ > 50) ok(); else setTimeout(w, 100); })(); }); }
  function tryAt(i) {
    if (done) return;
    if (i >= MIR.length) { fail(); return; }
    var m = MIR[i];
    get(m + SH + 'index.html', i ? 9000 : 7000).then(function (html) { sized().then(function () { start(m, html); }); }, function () { tryAt(i + 1); });
  }
  function start(m, html) {
    if (done) return;
    done = true; clearTimeout(slow);
    var cfg = { ver: VER, mirror: m, books: {}, old1001: m + SH + 'old1001.html' };
    for (var k in BOOKS) { var b = BOOKS[k], o = { core: m + b.core, parts: {} }; for (var p in (b.parts || {})) o.parts[p] = m + b.parts[p]; cfg.books[k] = o; }
    var doc = '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>奥尔德兰的旅印</title>'
      + '<base href="' + m + SH + '"><script>window.FRONT_CFG=' + JSON.stringify(cfg) + ';<\/script></head><body>' + html + '</body></html>';
    document.open(); document.write(doc); document.close();
  }
  function fail() {
    clearTimeout(slow);
    boot.innerHTML = '<p>门 面 没 有 载 下 来</p><p class="s">图床这会儿连不上。可以点一下再试'
      + (OLD ? '，也可以先用原来的介绍页，迷宫纪 1001 年的建档和世界之书都在里头。另外三纪不看门面也能开始，点输入框底下的开局快捷键就行。' : '；也可以不看门面，直接点输入框底下的开局快捷键，照样能开始。')
      + '</p><div class="row"><button type="button" id="again">再试一次</button>' + (OLD ? '<button type="button" class="o" id="useold">用原来的介绍页</button>' : '') + '</div>';
    document.getElementById('again').onclick = function () { wait(); tryAt(0); };
    bindOld();
  }
  wait();
  tryAt(0);
})();
</script>
</body>
</html>
'''


def old_block(old):
    """卡里原来那一整页，写成一段脚本里的字符串（取不到图床时整页换回它）。
    放进 <script> 里的字照 HTML 的规矩躲开三样：<!--、<script、</script（在 JS 的字符串里 \\!、\\s、\\/ 就是原字）。"""
    import re
    s = json.dumps(old, ensure_ascii=False)
    s = s.replace('<!--', '<\\!--')
    s = re.sub(r'<(/?)(script)', lambda m: '<\\' + (m.group(1) or '') + m.group(2), s, flags=re.I)
    s = s.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    assert '</script' not in s.lower() and '<!--' not in s and '<script' not in s.lower()
    return '<script>window.__OLD1001=' + s + ';</script>\n'


def thin_html(cfg=None, local=None, ver='11-15', old=None, mirrors=None):
    """old：卡里原来那一整页介绍页（给了就存进薄壳当退路）。mirrors：只在验退路的时候用，换成连不上的地址。"""
    s = _thin(cfg, local, ver, mirrors)
    assert s.count('__OLD__') == 1
    return s.replace('__OLD__', old_block(old) if old else '')


def _thin(cfg, local, ver, mirrors):
    if local:
        q = lambda s: urllib.parse.quote(s)
        mir, sh = [local], q('小样_外壳') + '/'
        books = {k: {'core': q(d) + '/', 'parts': {}} for k, d in BOOK_DIR.items()}
    else:
        cfg = cfg or json.load(open(os.path.join(HERE, 'front.json'), encoding='utf-8'))
        at = lambda c: 'gh/%s@%s/' % (cfg['repo'], c)
        mir, sh = (mirrors or MIRRORS), at(cfg['shell'])
        books = {k: {'core': at(b['core']), 'parts': {p: at(c) for p, c in b.get('parts', {}).items()}} for k, b in cfg['books'].items()}
    js = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    s = TPL.replace('__MIR__', js(mir)).replace('__SH__', js(sh)).replace('__BOOKS__', js(books)).replace('__VER__', ver)
    assert '__' not in s.replace('__proto__', '').replace('__OLD__', '').replace('__OLD1001', ''), '还有没换掉的占位'
    return s


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    local = sys.argv[sys.argv.index('--local') + 1] if '--local' in sys.argv else None
    out = os.path.join(FRONT, '小样_外壳', 'thin_local.html' if local else 'thin.html')
    s = thin_html(local=local)
    open(out, 'w', encoding='utf-8', newline='\n').write(s)
    print(os.path.basename(out), len(s), '字')
