#!/usr/bin/env python3
# 简式建档（11-17）：薄壳取不到图床的时候换上的那一页，顶替原来存在卡里的那一整页旧介绍页（一百六十万字，2.6MB）。
# 用户 11-17 问还能压哪里，回“就做1吧”：退路换成一页轻的。这一页不连外网，五个开局（迷宫纪1001年和四纪）都能选，
# 填名字这几样，凭证照外壳 shell.js 的 credential() 的写法出，头一行照 slim_card.opening()（带年份）。
#   python -I -X utf8 底稿/门面/共用/lite_page.py            写 小样_外壳/lite.html（本地看）
# make_thin.thin_html(lite=True) 调 lite_html() 把它存进薄壳。
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.normpath(os.path.join(FRONT, '..', '状态栏', '大框')))
sys.dont_write_bytecode = True
import slim_card as SC  # noqa: E402

BOOKS = [('moon', '小样_月银纪书'), ('strife', '小样_纷争纪书'), ('bronze', '小样_山铜纪书'), ('maze', '小样_迷宫纪书')]

PAGE = r'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>奥尔德兰的旅印 · 简式建档</title>
<style>
html,body{margin:0;background:#06070c;color:#ece5d6;font-family:"Noto Serif SC","Songti SC","SimSun",serif}
main{max-width:640px;margin:0 auto;padding:28px 18px 60px}
h1{font-size:20px;letter-spacing:.3em;margin:0 0 10px;font-weight:600;color:#f3d9b0}
p.s{font-size:13.5px;line-height:1.9;color:rgba(236,229,214,.78);margin:0 0 18px}
label{display:block;margin:12px 0 0;font-size:13px;color:rgba(236,229,214,.86)}
label small{color:rgba(236,229,214,.5);margin-left:6px}
input,select,textarea{box-sizing:border-box;width:100%;margin-top:5px;font:inherit;font-size:14px;color:#ece5d6;background:#10121b;border:1px solid rgba(236,229,214,.22);padding:8px 10px}
textarea{min-height:58px;resize:vertical}
.row{display:flex;gap:10px}.row>label{flex:1}
button{font:inherit;font-size:13.5px;letter-spacing:.2em;color:#ece5d6;background:rgba(255,176,104,.16);border:1px solid rgba(255,176,104,.6);padding:9px 18px;cursor:pointer}
button.o{background:none;border-color:rgba(236,229,214,.32)}
.acts{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 8px}
pre{white-space:pre-wrap;font-size:12.5px;line-height:1.7;background:#0c0e15;border:1px solid rgba(236,229,214,.16);padding:12px;max-height:46vh;overflow:auto;margin:14px 0 0}
#tip{font-size:13px;min-height:1.6em;color:#f3d9b0;margin:6px 0 0}
[hidden]{display:none!important}
</style></head><body><main>
<h1>简 式 建 档</h1>
<p class="s">门面这会儿没有载下来，这一页不用连外网。挑一个时代，写下名字，点“填进输入框”再发送，就从那里睁眼。细的建档、世界之书和四本书在门面里，门面载得下来的时候再去看。</p>
<label>时代<select id="era"></select></label>
<label id="r-line">从哪里进<select id="line"></select></label>
<label id="r-year" hidden>哪一年<small id="yhint"></small><input id="year" inputmode="numeric"></label>
<label id="r-place" hidden>落在哪里<small>不写由 AI 照开局定一处</small><input id="place"></label>
<label id="r-soul" hidden>怎么来的<select id="soul"><option value="isekai">降临之魂（从别处落进来）</option><option value="native">本地之魂（生在这里）</option></select></label>
<div class="row"><label>名字<input id="name"></label><label>性别<input id="sex"></label></div>
<div class="row"><label>年龄<input id="age" inputmode="numeric"></label><label>种族<small>不写由 AI 定</small><input id="race"></label></div>
<label>容貌<small>一两句</small><textarea id="look"></textarea></label>
<label>想往哪条路上走<small>兵器、法术、手艺都行，不写由 AI 定</small><input id="path"></label>
<label>为什么出来<small>不写也行</small><textarea id="wish"></textarea></label>
<div class="acts"><button type="button" id="fill">填进输入框</button><button type="button" class="o" id="copy">复制</button><button type="button" class="o" id="again">再试一次门面</button></div>
<p id="tip" aria-live="polite"></p>
<pre id="out"></pre>
</main>
<script>
(function () {
  var D = __DATA__, $ = function (id) { return document.getElementById(id); };
  function yT(b, y) { return y == null ? '' : (y === 1 && b === 'strife' ? '元年' : y + '年'); }
  function yearOf(s) { var m = String(s || '').match(/(\d{1,5})/); return m ? +m[1] : (/元/.test(String(s || '')) ? 1 : null); }
  var era = $('era'), line = $('line');
  era.innerHTML = '<option value="1001">迷宫纪 1001 年</option>' + D.eras.map(function (E, i) { return '<option value="' + i + '">' + E.name + '</option>'; }).join('');
  function fillLines() {
    var E = D.eras[+era.value];
    line.innerHTML = E.pages.map(function (P, pi) {
      return '<optgroup label="' + P.t + '">' + P.l.map(function (L, li) { return '<option value="' + pi + ',' + li + '">' + L[0] + (L[1] != null ? '　' + yT(E.b, L[1]) : '') + '</option>'; }).join('') + '</optgroup>';
    }).join('') + (E.free ? '<option value="free">自己报年份（' + E.free.label + '）</option>' : '');
  }
  function shape() {
    var is1001 = era.value === '1001';
    $('r-line').hidden = is1001; $('r-place').hidden = !is1001; $('r-soul').hidden = !is1001;
    if (!is1001) { var E = D.eras[+era.value]; $('r-year').hidden = line.value !== 'free'; if (E.free) $('yhint').textContent = E.name + ' ' + E.free.from + ' 到 ' + E.free.to + ' 年之间'; }
    else $('r-year').hidden = true;
    render();
  }
  function v(id) { return ($(id).value || '').trim(); }
  function cred() {
    var is1001 = era.value === '1001', native = is1001 && $('soul').value === 'native', L = [], where, open = '';
    if (!is1001) {
      var E = D.eras[+era.value];
      if (line.value === 'free') {
        var y = yearOf(v('year'));
        if (y == null || y < E.free.from || y > E.free.to) return { err: '哪一年要写一个数，' + E.name + ' ' + E.free.from + ' 到 ' + E.free.to + ' 年之间。' };
        open = '纪元：' + E.name + yT(E.b, y) + '｜开局时段：' + E.free.cmd.replace('{year}', y === 1 && E.b === 'strife' ? '元' : y);
        where = E.name + y + '年（' + E.free.label + '，照那一年的时段总纲和地点起头）';
      } else {
        var ix = line.value.split(','), P = E.pages[+ix[0]], M = P.l[+ix[1]];
        var start = E.start === 'line' ? M[0] : (M[0].indexOf('·') >= 0 ? M[0].slice(M[0].indexOf('·') + 1) : M[0]);
        open = '纪元：' + E.name + yT(E.b, M[1]) + '｜开局时段：' + start;
        where = E.name + yT(E.b, M[1]) + '，' + P.t + '，主线「' + M[0] + '」的开局';
      }
    } else {
      where = '迷宫纪1001年，' + (v('place') || '未定（由 AI 照开局定一处，开场说明）');
    }
    if (!v('name')) return { err: '名字还没写。' };
    if (open) L.push(open, '');
    L.push(D.head, '', '【一·灵魂形态】', native ? '本地之魂（生于此世）' : D.soul);
    if (!native) L.push('来处：未详述（降临者报不出这里的出身）');
    L.push('', '【二·种族胎骨】', v('race') || '未选择', '', '【三·命路倾向】', v('path') || '未选择（由 AI 照这一纪的本事和我的来处定一个方向）', '');
    L.push('【四·姓名容貌】', '姓名：' + v('name'), '年龄：' + (v('age') ? v('age') + (native ? '' : D.age_suffix) : '未填写（' + (native ? '' : '落地多大就多大，') + '由 AI 按容貌与经历定一个，开场用一句话说明，不得默认十八岁）'),
      '性别：' + (v('sex') || '未填写'), '容貌：' + (v('look') || '未详述'),
      '体态数据：身高 未记录（由AI按种族与出身补全）｜体型 未记录（由AI补全）　（静态资产，状态栏逐轮照抄，正文不主动报数）', '立绘：无', '自定义设定：（无）', '初始实力：启源·初识', D.note, '');
    L.push('【五·命星天赋】', 'Passive/Special：未选择（照这一纪的规矩来，这一纪不给落进来的人的就写无）', 'Art/Active：未选择（同上）', '');
    if (native) L.push('【六·你的前半生】', '出生地：未定（由 AI 按种族定一处）', '誓心阵营：随便（由世界照我的出身推一个，开场明说是推的）', '出身家世：未选择（由AI按出生地与族属补全）', '');
    else L.push('【六·誓心与赐物】', '誓心阵营：随便（由世界照我的来处推一个，开场明说是推的）', '神殿赐物：未选择（拒绝了她的馈赠）', '');
    L.push('【七·现在何处】', '现在所在：' + where, '当前处境：' + (native ? '这一纪生下来的人，从开局起头。' : '刚从死之神殿落下来，身上只有这一身。'), '');
    L.push('【八·冒险初心】', v('wish') || '还没想好（先走着看，头一轮不必追问）', '', D.tail);
    return { text: L.join('\n') };
  }
  function render() { var c = cred(); $('out').textContent = c.err ? '' : c.text; $('tip').textContent = c.err || ''; return c; }
  function copy(t) {
    try { var ta = document.createElement('textarea'); ta.value = t; ta.style.cssText = 'position:fixed;left:-9999px;top:0'; document.body.appendChild(ta); ta.select(); var ok = document.execCommand('copy'); ta.remove(); if (ok) return Promise.resolve(true); } catch (e) {}
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(t).then(function () { return true; }, function () { return false; });
    return Promise.resolve(false);
  }
  era.onchange = function () { if (era.value !== '1001') fillLines(); shape(); };
  line.onchange = shape;
  ['year', 'place', 'soul', 'name', 'sex', 'age', 'race', 'look', 'path', 'wish'].forEach(function (id) { $(id).addEventListener('input', render); $(id).addEventListener('change', render); });
  $('fill').onclick = function () { var c = render(); if (c.err) return; try { window.parent.postMessage({ type: 'rili-set-input', value: c.text }, '*'); $('tip').textContent = '填进去了，点一下发送。输入框里没有的话，点“复制”再粘贴。'; } catch (e) { $('tip').textContent = '没填进去，点“复制”再粘贴。'; } };
  $('copy').onclick = function () { var c = render(); if (c.err) return; copy(c.text).then(function (ok) { $('tip').textContent = ok ? '复制好了，回到聊天的输入框里粘贴，再发送。' : '没复制上，长按下面那一段，全选了再复制。'; }); };
  $('again').onclick = function () { location.reload(); };
  shape();
})();
</script>
</body></html>
'''


def data():
    build = json.load(open(os.path.join(FRONT, '小样_外壳', 'data', 'build.json'), encoding='utf-8'))
    fm = build['format']
    eras = []
    for b, folder in BOOKS:
        E = build['eras'][b]
        Dd = json.load(open(os.path.join(FRONT, folder, 'data', b + '.json'), encoding='utf-8'))
        pages = Dd['eras'] if isinstance(Dd, dict) and 'eras' in Dd else Dd
        ps = []
        for pg in pages:
            ls = [[l['name'], SC.year_of(l.get('year'))] for l in pg.get('lines', [])]
            if ls:
                ps.append({'t': pg.get('title') or '', 'l': ls})
        fr = E.get('free')
        eras.append({'b': b, 'name': E['name'], 'start': E.get('start', 'tail'), 'pages': ps,
                     'free': {k: fr[k] for k in ('label', 'cmd', 'from', 'to')} if fr else None})
    return {'head': fm['head'], 'soul': fm['soul'], 'note': fm['note'], 'tail': fm['tail'], 'age_suffix': fm['age_suffix'], 'eras': eras}


def lite_html():
    js = json.dumps(data(), ensure_ascii=False, separators=(',', ':'))
    js = js.replace('</', '<\\/')
    s = PAGE.replace('__DATA__', js)
    assert '__DATA__' not in s and not re.search(r'[—；…！]', s.replace('<\\/', '')), '简式建档里有卡面不用的标点'
    return s


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    s = lite_html()
    out = os.path.join(FRONT, '小样_外壳', 'lite.html')
    open(out, 'w', encoding='utf-8', newline='\n').write(s)
    print(os.path.basename(out), len(s), '字', len(s.encode('utf-8')), '字节')
