#!/usr/bin/env python3
# 11-12 门面探针第二张：把真的牌桌小样（底稿/门面/小样_牌桌/index.html）整个装进一张日里卡的介绍页，看它在日里的沙箱里跑不跑得动。
# 图全部内嵌成 data: 地址（不靠外链，哪种安全策略下都能跑），所以介绍页有三兆半上下，顺带试了介绍页能不能这么大。
# 不改 index.html，只在打出来的这一份上换地址：
#   样式里那一处 url(assets/table.webp) 换成变量 --a-table；两张手的 <img> 先不给地址，紧跟着一句脚本从 __A 里取；
#   脚本里 'assets/名.webp' 换成 __A.名，模板串里 assets/名_${i}.webp 换成 ${__A['名_'+i]}。
# 日里的介绍页没有 localStorage，页面自己那套“上回开崩了下回换轻的画法”记不住，所以壳上加一个小钮（右上角“探”），
#   点开能换轻量画法（记在 window.name 里再重载）、把运行情况填进输入框。
# 用法：python -I -X utf8 make_table_card.py [输出目录]        默认 out/探针_11-12/
import base64
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, '底稿', '门面', '小样_牌桌')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', '探针_11-12')
os.makedirs(OUT, exist_ok=True)
VER = '11-12'
NAMES = ['table', 'hand9_open', 'hand9_take'] + ['%s_%d' % (p, i) for p in ('back', 'bb', 'era') for i in range(4)]


def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:70], s.count(a))
    return s.replace(a, b)


frag = open(os.path.join(SRC, 'index.html'), encoding='utf-8').read()
# 样式和标记里的三处
frag = rep(frag, 'url(assets/table.webp)', 'var(--a-table)')
frag = rep(frag, '<img id="hOpen" src="assets/hand9_open.webp" alt="">', '<img id="hOpen" alt="">')
frag = rep(frag, '<div id="hold" class="hbox"><img id="hHold" src="assets/hand9_take.webp" alt=""></div>',
           '<div id="hold" class="hbox"><img id="hHold" alt=""></div>\n'
           '<script>document.getElementById("hOpen").src = __A.hand9_open; document.getElementById("hHold").src = __A.hand9_take;</script>')
# 脚本里的
frag, n1 = re.subn(r"'assets/(\w+)\.webp'", lambda m: '__A.' + m.group(1), frag)
frag, n2 = re.subn(r"assets/([a-z]+)_\$\{(\w+)\}\.webp", lambda m: "${__A['%s_'+%s]}" % (m.group(1), m.group(2)), frag)
assert (n1, n2) == (3, 8), (n1, n2)
assert 'assets/' not in frag, re.findall(r'.{30}assets/.{30}', frag)[:3]
# 轻量画法：除了地址带 ?lite，壳也能指定；点“换回完整画法”时把壳记的那一笔也清掉
frag = rep(frag, "if (q.has('lite')) LITE = true;", "if (q.has('lite') || window.__TB_LITE) LITE = true;")
frag = rep(frag, "store.set('tb_step', 'ok'); location.reload(); });", "store.set('tb_step', 'ok'); try { window.name = ''; } catch (e) {} location.reload(); });")

A = {}
total = 0
for n in NAMES:
    raw = open(os.path.join(SRC, 'assets', n + '.webp'), 'rb').read()
    total += len(raw)
    A[n] = 'data:image/webp;base64,' + base64.b64encode(raw).decode('ascii')

HUD = r'''<style>
#pbHud{position:fixed;right:6px;top:52px;z-index:99999;font:11px/1.3 system-ui,sans-serif;color:#e8e4da;text-align:right}
#pbChip{display:inline-block;padding:3px 7px;border-radius:10px;background:rgba(10,12,20,.55);border:1px solid rgba(201,164,92,.5);cursor:pointer;-webkit-tap-highlight-color:transparent}
#pbPan{display:none;margin-top:4px;padding:8px;border-radius:8px;background:rgba(10,12,20,.92);border:1px solid rgba(201,164,92,.6);text-align:left;max-width:250px}
#pbPan.on{display:block}
#pbPan button{display:block;width:100%;margin:5px 0 0;padding:8px;border:0;border-radius:6px;background:#c9a45c;color:#1a1408;font:13px system-ui,sans-serif}
#pbPan button.s{background:#2a3044;color:#e8e4da}
#pbTxt{white-space:pre-wrap;word-break:break-all;color:#9fc4ff;margin-bottom:2px}
</style>
<div id="pbHud"><span id="pbChip">探 …</span><div id="pbPan"><div id="pbTxt"></div><button id="pbFill">把运行情况填进输入框</button><button id="pbLite" class="s"></button><button id="pbClose" class="s">收起</button></div></div>
<script>
/* 探针的壳：右上角一个小签，记帧率、走到哪一步、出过什么错；点开能换画法、把情况填进输入框。正式的门面里没有这一块。 */
(function () {
  var E = [], t0 = performance.now(), fps = 0, minFps = 999, n = 0, last = performance.now(), stages = [], LITE = false;
  try { LITE = /tb:lite/.test(window.name || ''); } catch (e) {}
  window.__TB_LITE = LITE;
  window.addEventListener('error', function (e) { if (E.length < 5) E.push(String(e.message || e.type).slice(0, 90) + (e.lineno ? '@' + e.lineno : '')); });
  window.addEventListener('unhandledrejection', function (e) { if (E.length < 5) E.push('rej:' + String(e.reason && (e.reason.message || e.reason.name) || e.reason).slice(0, 80)); });
  document.addEventListener('securitypolicyviolation', function (e) { if (E.length < 5) E.push('策略拦:' + (e.effectiveDirective || e.violatedDirective)); });
  (function f() { n++; requestAnimationFrame(f); })();
  var $ = function (id) { return document.getElementById(id); };
  function info() {
    var tb = window.__tb, mode = document.querySelector('#world.lite') ? '轻量' : (tb && tb.rigs ? '完整' : '完整(骨骼没起)');
    return '【牌桌探针 __VER__】' + mode + ' 窗' + innerWidth + 'x' + innerHeight + ' dpr' + (+(window.devicePixelRatio || 1).toFixed(2)) + ' 开了' + Math.round((performance.now() - t0) / 1000) + 's\n' +
      '帧率 现' + fps + ' 最低' + (minFps === 999 ? '?' : minFps) + ' ｜ 走到：' + (stages.join('→') || '?') + '\n' +
      '世界：' + (document.getElementById('world') ? document.getElementById('world').className : '?') + '\n' +
      '出错：' + (E.join('；') || '无') + '\n' + (navigator.userAgent || '').slice(0, 140);
  }
  setInterval(function () {
    var now = performance.now(); fps = Math.round(n / ((now - last) / 1000)); n = 0; last = now;
    if (now - t0 > 3000 && document.visibilityState === 'visible' && fps < minFps) minFps = fps;
    var tb = window.__tb, st = tb && tb.stage; if (st && stages[stages.length - 1] !== st && stages.length < 14) stages.push(st);
    $('pbChip').textContent = '探 ' + fps + '帧' + (E.length ? ' 错' + E.length : '') + (document.querySelector('#world.lite') ? ' 轻' : '');
    if ($('pbPan').className === 'on') $('pbTxt').textContent = info();
  }, 1000);
  $('pbChip').addEventListener('click', function (e) { e.stopPropagation(); $('pbPan').className = $('pbPan').className === 'on' ? '' : 'on'; $('pbTxt').textContent = info(); });
  $('pbClose').addEventListener('click', function (e) { e.stopPropagation(); $('pbPan').className = ''; });
  $('pbLite').textContent = LITE ? '换回完整画法（会重开）' : '换成轻量画法（会重开）';
  $('pbLite').addEventListener('click', function (e) { e.stopPropagation(); try { window.name = LITE ? '' : 'tb:lite'; } catch (x) {} location.reload(); });
  $('pbFill').addEventListener('click', function (e) { e.stopPropagation(); try { window.parent.postMessage({ type: 'rili-set-input', value: info() }, '*'); $('pbFill').textContent = '填过去了，去输入框里复制'; } catch (x) { $('pbFill').textContent = '填不过去，截图这一块吧'; } });
  ['pointerdown', 'pointerup', 'mousedown', 'touchstart'].forEach(function (t) { $('pbHud').addEventListener(t, function (e) { e.stopPropagation(); }); });
})();
</script>
'''.replace('__VER__', VER)

doc = ('<!doctype html><html lang="zh"><head><meta charset="utf-8">'
       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
       '<style>html,body{margin:0;height:100%;background:#05060c}</style></head><body>\n'
       '<script>window.__A = ' + json.dumps(A, ensure_ascii=True) + ';\n'
       'document.documentElement.style.setProperty("--a-table", "url(" + __A.table + ")");</script>\n'
       + HUD + frag + '\n</body></html>')

SYS = '这是一张测试平台用的探针卡，不讲故事，不加解释。不管玩家发什么，只回复一行：探针回声｜后面接玩家这一句话的前二十个字。只输出这一行。'
card = {
    'title': '奥尔德兰门面探针_牌桌_' + VER,
    'description': '测平台用的小卡，不讲故事：把门面的牌桌小样整个装进介绍页，看它在日里里跑不跑得动。测完删。',
    'language': 'zh', 'containsNSFW': False, 'publicAccess': False, 'isAnonymous': False, 'enableSafeguard': False,
    'prompt': {'systemPrompt': SYS, 'headPrompt': '', 'rearPrompt': '', 'lorebook': []},
    'assistantRegexReplace': [],
    'injectStyles': '',
    'introPage': doc,
    'enableMemorySchema': False,
    'options': {'items': [{'order': 0, 'label': '发一句试试', 'type': 'SET-INPUT', 'value': '探针测试'}]},
    'cardsTags': [],
    'cardsVoices': [],
}
path = os.path.join(OUT, '奥尔德兰门面探针_牌桌_%s.json' % VER)
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(card, f, ensure_ascii=False, indent=1)
os.makedirs(os.path.join(OUT, '本地验'), exist_ok=True)
with open(os.path.join(OUT, '本地验', 'table_intro.html'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(doc)
print('ok', path, '%.2f MB，介绍页 %d 字，图 %d 张合 %.2f MB' % (os.path.getsize(path) / 1048576, len(doc), len(NAMES), total / 1048576))
