#!/usr/bin/env python3
# 迷宫纪 1001 年那一条路：卡里原来的介绍页（建档器、接续旧档、1001 年的世界之书和大陆全图）原样留着，装在外壳的一格里。
#   python -I -X utf8 底稿/门面/小样_外壳/make_old1001.py <打好的卡.json>      （卡的 introPage 还是原来那一整页的时候跑）
# 取出 introPage，在 </body> 前添一小段，写成 小样_外壳/old1001.html：
#   1. 载好了直接翻到目录那一幕（新的旅印、接续旅印、世界之书），不再过“推开界门”。
#   2. 铸印那一幕出来的时候把凭证交给外壳（外壳出请离那一眼和确认页，能一下填进聊天的输入框）。它自己的复制照旧能用。
#   3. 左下角一枚小钮回牌桌。
# 别的一个字不动。卡重打以后（介绍页的字变了）重跑这一支，再推图床。
# 11-27：原来那一页的脚本里有 ?. 和 ??，安卓系统 WebView 八十版以前解析不了。跑完这一支以后再跑 载入页/tools/downlevel.mjs 改成老写法、头上补几样兜底（用法写在那一份头上）。
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BRIDGE = '''
<style>
#aldran-back{all:unset;position:fixed;left:max(10px,env(safe-area-inset-left));bottom:max(10px,env(safe-area-inset-bottom));z-index:2147483000;cursor:pointer;padding:6px 12px;border:1px solid rgba(236,229,214,.3);background:rgba(4,5,10,.55);color:#ece5d6;font:12px/1.4 "Noto Serif SC","Songti SC",serif;letter-spacing:.2em;opacity:.7}
#aldran-back:hover{opacity:1}
</style>
<script>
(function(){
  if (!window.parent || window.parent === window) return;
  var last = '';
  function post(m){ m.aldran = 1; try { window.parent.postMessage(m, '*'); } catch (e) {} }
  setInterval(function(){
    try {
      if (typeof SC_CUR !== 'undefined' && SC_CUR === 'seal') {
        var o = document.getElementById('final_output'), v = (o && o.value) || '';
        if (v && v !== last) { last = v; post({ t: 'cred', text: v }); }
      } else last = '';
    } catch (e) {}
  }, 350);
  function boot(){
    try { if (typeof go === 'function' && typeof SC_CUR !== 'undefined' && SC_CUR === 'gate') go('menu'); } catch (e) {}
    var b = document.createElement('button'); b.id = 'aldran-back'; b.type = 'button'; b.textContent = '回到牌桌';
    b.addEventListener('click', function(){ post({ t: 'table' }); });
    document.body.appendChild(b);
    post({ t: 'old-ready' });
  }
  if (document.readyState === 'complete') boot(); else window.addEventListener('load', boot);
})();
</script>
'''


def main():
    card = json.load(open(sys.argv[1], encoding='utf-8'))
    ip = card.get('introPage') or ''
    assert len(ip) > 500000 and 'finishBuild' in ip and 'final_output' in ip and "SC_CUR" in ip, '这张卡的介绍页不是原来那一整页（已经换成薄壳了？）'
    assert 'aldran-back' not in ip
    i = ip.rfind('</body>')
    assert i > 0
    out = ip[:i] + BRIDGE + ip[i:]
    p = os.path.join(HERE, 'old1001.html')
    open(p, 'w', encoding='utf-8', newline='').write(out)
    print('old1001.html', len(out), '字')


if __name__ == '__main__':
    main()
