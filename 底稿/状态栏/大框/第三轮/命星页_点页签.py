# 出一段复刻台（tools/rili_bench/static_bench.mjs 的 eval=）用的脚本：点开伟业那一页，翻到哪一类书签，点第几枚，滚到哪里，按时间走的动画停在第几秒。
# 顺手查：有没有东西出了这一页的框（over），展开以后有没有剩下的 § 行和中间记号（raw），两样都该是空的。
# 用法：python -I -X utf8 命星页_点页签.py 出.js [cat=Art] [item=2] [anchor=.sz-book] [off=60] [t=1.2]
#   cat 书签（命星、Art、Passive、Active、Skill、职业能力），item 这一类里第几枚（不写不点），anchor 滚到哪个元素、off 离窗口顶多少像素，t 动画停在第几秒
import sys
out = sys.argv[1]
o = dict(a.split('=', 1) for a in sys.argv[2:])
js = r'''
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const all = [...document.querySelectorAll('.rili-markdown-renderer')];
  const last = all[all.length - 1];
  last.querySelector('.t-deed input').click();
  await sleep(250);
  const cat = %(cat)s, item = %(item)s;
  if (cat) { const c = last.querySelector('.sz-cat[data-c="' + cat + '"] input'); if (c) c.click(); }
  await sleep(120);
  if (cat && item) { const its = last.querySelectorAll('.sz-ab[data-c="' + cat + '"] > .sz-face > input'); if (its[item - 1]) its[item - 1].click(); }
  await sleep(200);
  for (const x of document.getAnimations()) { if (x.timeline !== document.timeline) continue; try { x.pause(); x.currentTime = %(t)s * 1000; } catch (e) {} }
  await sleep(100);
  window.lay();
  const c = document.getElementById('conversation');
  const a = last.querySelector(%(anchor)s);
  c.scrollTop += a.getBoundingClientRect().top - c.getBoundingClientRect().top - %(off)s;
  await sleep(250);
  const pane = last.querySelector('.p-deed');
  const over = [...pane.querySelectorAll('*')].filter((e) => { const b = e.getBoundingClientRect(); const p = pane.getBoundingClientRect(); return b.width > 0 && (b.right > p.right + 1 || b.left < p.left - 1) && getComputedStyle(e).display !== 'none'; }).slice(0, 6).map((e) => (e.className || e.tagName) + ':' + Math.round(e.getBoundingClientRect().right - pane.getBoundingClientRect().right));
  const raw = [...last.querySelectorAll('*')].filter((e) => e.children.length === 0 && /§|ⓔ|ⓖ|ⓙ|ⓡ/.test(e.textContent)).slice(0, 4).map((e) => e.textContent.slice(0, 60));
  const h = (q) => { const e = last.querySelector(q); return e ? Math.round(e.getBoundingClientRect().height) : -1; };
  return JSON.stringify({ h: h('.p-deed'), up: h('.sp-up'), job: h('.sp-job'), book: h('.sz-book'), over, raw });
})()
''' % dict(cat=repr(o.get('cat', '')), item=o.get('item', '0'), anchor=repr(o.get('anchor', '.p-deed')), off=o.get('off', '60'), t=o.get('t', '1.2'))
open(out, 'w', encoding='utf-8').write(js)
