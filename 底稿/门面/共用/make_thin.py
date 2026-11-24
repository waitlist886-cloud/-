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
BOOK_DIR = {'moon': '小样_月银纪书', 'strife': '小样_纷争纪书', 'bronze': '小样_山铜纪书', 'maze': '小样_迷宫纪书', 'now': '小样_此刻书'}

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
  var MIR = __MIR__, SH = __SH__, BOOKS = __BOOKS__, VER = '__VER__', PTR = __PTR__, PTRX = __PTRX__, N = __N__, RP = __RP__, G = __G__;
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
  function getj(u, ms) {
    return new Promise(function (ok, no) {
      var c = window.AbortController ? new AbortController() : null;
      var t = setTimeout(function () { if (c) c.abort(); no(new Error('timeout')); }, ms);
      fetch(u, c ? { signal: c.signal, cache: 'no-store' } : { cache: 'no-store' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (j) { clearTimeout(t); ok(j); }, function (e) { clearTimeout(t); no(e); });
    });
  }
  /* 图床上的指针：门面更新以后各段的新提交号（push_ptr.py 推的）。比卡里带的这一份新才用，写得不对就不用，取不到照卡里这一份。
     指针从几个镜像各取一份，另从 GitHub 自己那一头再取一份（PTRX）：镜像上的分支地址最久要十二个钟头才跟上，GitHub 那一头五分钟，连得上它的人就早拿到。
     取的时候不走浏览器的缓存（镜像给这个文件标的是七天）。 */
  var HEX = /^[0-9a-f]{40}$/;
  function usePtr(j) {
    if (!j || !(j.n > N) || !HEX.test(j.shell || '') || !j.books || !/^[\w.-]+\/[\w.-]+$/.test(j.repo || '') || (RP && j.repo !== RP)) return false;
    var at = function (c) { return 'gh/' + j.repo + '@' + c + '/'; }, nb = {};
    for (var k in BOOKS) if (!j.books[k]) return false;
    for (var k in j.books) {          // 指针上多出来的书（往后添的第六本、第七本）也收下，卡不用重打就看得到（11-24 此刻那一本起）
      var b = j.books[k];
      if (!b || !HEX.test(b.core || '')) return false;
      var o = { core: at(b.core), parts: {} };
      for (var p in (b.parts || {})) { if (!HEX.test(b.parts[p] || '')) return false; o.parts[p] = at(b.parts[p]); }
      nb[k] = o;
    }
    SH = at(j.shell); BOOKS = nb; N = j.n;
    return true;
  }
  function ptr() {
    if (!PTR) { tryAt(0); return; }
    var src = MIR.map(function (m, i) { return [m + PTR, i]; }).concat(PTRX.map(function (u) { return [u, -1]; }));
    var left = src.length, best = null, fi = -1, gone = false, tm = null, t1 = 0, chasing = 0, asked = {};
    function go() {
      if (gone) return;
      gone = true; clearTimeout(tm);
      if (best) usePtr(best);
      if (fi > 0) MIR = [MIR[fi]].concat(MIR.slice(0, fi), MIR.slice(fi + 1));   /* 头一个答话的镜像排到最前头 */
      tryAt(0);
    }
    function settle() {   /* 几路都答完了，或者头一个答了以后等够了四百毫秒，而且没有正在追的新一代，就走 */
      if (gone || chasing) return;
      if (left === 0 || (t1 && Date.now() - t1 >= 400)) go();
    }
    function take(j) {
      if (!j || typeof j.n !== 'number') return;
      if (!best || j.n > best.n) best = j;
      if (typeof j.g === 'number') chase(j.g + 1);
    }
    /* 指针一代一个分支（front_ptr_g<代>，push_ptr.py 推的）。老分支的地址镜像要缓存半天，还没有的分支不缓存、新推的一分钟里就取得到，
       所以从手里最新的一代顺着往后一代一代问，问到没有为止。问两个镜像，哪个先答有就算有。 */
    function chase(g) {
      if (!G || !RP || gone || asked[g] || g > G + 60) return;
      asked[g] = 1; chasing++;
      var two = [MIR[0], MIR[2] || MIR[1] || MIR[0]], n = two.length, hit = false;
      var done = function () { if (--n === 0) { chasing--; settle(); } };
      two.forEach(function (m) {
        getj(m + 'gh/' + RP + '@front_ptr_g' + g + '/front.json', 2500).then(function (j) {
          if (!hit && j && j.g === g) { hit = true; take(j); }
          done();
        }, done);
      });
    }
    src.forEach(function (s) {
      getj(s[0], 3000).then(function (j) {
        if (gone) return;
        if (fi < 0 && s[1] >= 0) fi = s[1];
        take(j);
        if (!t1) {                                                                 /* 头一个答了再等一小会儿，几路里挑最新的那一份；追新一代至多再多等九百毫秒 */
          t1 = Date.now();
          tm = setTimeout(function () { tm = setTimeout(go, 900); settle(); }, 400);
        }
        left--; settle();
      }, function () { left--; settle(); });
    });
    if (G) chase(G + 1);
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
    var cfg = { ver: VER, n: N, mirror: m, books: {}, old1001: m + SH + 'old1001.html' };
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
    document.getElementById('again').onclick = function () { wait(); ptr(); };
    bindOld();
  }
  wait();
  ptr();
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


LITE_TEXT = [   # 11-17 退路换成简式建档（lite_page.py）以后，薄壳里说退路的那几句跟着换
    ('取不到的时候退回卡里原来那一整页介绍页（迷宫纪 1001 年的建档器和世界之书），它就存在上面那一段里。', '取不到的时候换成一页简式建档（不连外网，迷宫纪 1001 年和四纪五个开局都能选），它就存在上面那一段里。'),
    ('载得慢？先用原来的介绍页', '载得慢？先用简式建档'),
    ('，也可以先用原来的介绍页，迷宫纪 1001 年的建档和世界之书都在里头。另外三纪不看门面也能开始，点输入框底下的开局快捷键就行。', '，也可以先用简式建档，迷宫纪 1001 年和另外四纪都能开始，填几样就行。'),
    ('用原来的介绍页</button>', '用简式建档</button>'),
]


def thin_html(cfg=None, local=None, ver='11-16', old=None, mirrors=None, lite=False):
    """old：卡里原来那一整页介绍页（给了就存进薄壳当退路）。lite：退路换成一页简式建档（11-17 起默认，into_card.py 照这个）。
    mirrors：只在验退路的时候用，换成连不上的地址。"""
    s = _thin(cfg, local, ver, mirrors)
    assert s.count('__OLD__') == 1
    if lite:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import lite_page
        old = lite_page.lite_html()
        for a, b in LITE_TEXT:
            assert s.count(a) == 1, ('薄壳里说退路的话对不上', a[:30])
            s = s.replace(a, b)
    return s.replace('__OLD__', old_block(old) if old else '')


def _thin(cfg, local, ver, mirrors):
    if local:
        q = lambda s: urllib.parse.quote(s)
        mir, sh = [local], q('小样_外壳') + '/'
        ptr, ptrx, n, rp, g = None, [], 0, '', 0
        books = {k: {'core': q(d) + '/', 'parts': {}} for k, d in BOOK_DIR.items()}
    else:
        cfg = cfg or json.load(open(os.path.join(HERE, 'front.json'), encoding='utf-8'))
        at = lambda c: 'gh/%s@%s/' % (cfg['repo'], c)
        mir, sh = (mirrors or MIRRORS), at(cfg['shell'])
        ptr, n = 'gh/%s@front_ptr/front.json' % cfg['repo'], int(cfg.get('n') or 0)
        ptrx = ['https://raw.githubusercontent.com/%s/front_ptr/front.json' % cfg['repo']]
        rp, g = cfg['repo'], int(cfg.get('g') or 0)
        books = {k: {'core': at(b['core']), 'parts': {p: at(c) for p, c in b.get('parts', {}).items()}} for k, b in cfg['books'].items()}
    js = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    s = TPL.replace('__MIR__', js(mir)).replace('__SH__', js(sh)).replace('__BOOKS__', js(books)).replace('__VER__', ver).replace('__PTR__', js(ptr)).replace('__PTRX__', js(ptrx)).replace('__N__', str(n)).replace('__RP__', js(rp)).replace('__G__', str(g))
    assert '__' not in s.replace('__proto__', '').replace('__OLD__', '').replace('__OLD1001', ''), '还有没换掉的占位'
    return s


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    local = sys.argv[sys.argv.index('--local') + 1] if '--local' in sys.argv else None
    out = os.path.join(FRONT, '小样_外壳', 'thin_local.html' if local else 'thin.html')
    s = thin_html(local=local, ver='11-18', lite='--no-lite' not in sys.argv)   # 11-17 起贴进介绍页的薄壳也带简式建档（一万八千字节）
    open(out, 'w', encoding='utf-8', newline='\n').write(s)
    print(os.path.basename(out), len(s), '字')
