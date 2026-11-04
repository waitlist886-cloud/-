// 手机上输入栏折叠（11-04）：给 static_bench.mjs 的 eval= 用，量闲着、点进去、有字、失焦四种状态。
// 真页面的输入框往上好几层，这里先把输入框往里多包两层，选择器认不认得一起试。无头里动画时钟不走，过渡要 finish() 才到终点。
(async () => { try {
  const q = (s) => document.querySelector(s);
  const ta = q('#chat-input'), conv = q('#conversation'), shell = conv.closest('.custom-styles');
  const a = document.createElement('div'), b = document.createElement('div');
  a.className = 'wrap-a'; b.className = 'wrap-b'; a.style.padding = '6px 0'; b.style.minHeight = '40px';
  ta.parentNode.insertBefore(a, ta); a.appendChild(b); b.appendChild(ta);
  ta.style.minHeight = '60px';
  const extra = document.createElement('div'); extra.textContent = '0/8000'; a.appendChild(extra);
  const panel = q('.fake-input-inner'), chips = q('.fake-chips'), tools = q('.fake-tools');
  const finish = () => document.getAnimations().forEach((x) => { if (x.transitionProperty) x.finish(); });
  const r = (el) => { const c = el.getBoundingClientRect(); return { top: Math.round(innerHeight - c.top), bot: Math.round(innerHeight - c.bottom), h: Math.round(c.height), w: Math.round(c.width) }; };
  const shows = (el) => getComputedStyle(el).visibility !== 'hidden' && el.getBoundingClientRect().height > 0;
  const tabs = () => { const t = [...document.querySelectorAll('.sz-tabs')].pop(); return t ? r(t) : null; };
  const m = (name) => {
    window.lay && window.lay();
    const o = { 状态: name, 栏离底: r(panel).top, 栏高: r(panel).h, 输入框高: r(ta).h, 钮: shows(chips), 工具: shows(tools), 字数框: shows(extra), dock: getComputedStyle(shell).getPropertyValue('--fm-dock').trim(), 框下沿: getComputedStyle(shell, '::after').bottom, 页签: tabs(), 滚动总高: conv.scrollHeight };
    return o;
  };
  const out = [];
  conv.scrollTop = conv.scrollHeight;
  out.push(m('闲着·滚到底'));
  const t = [...document.querySelectorAll('.sz-tabs')].pop();
  ta.focus(); finish();
  out.push(m('点进去'));
  ta.blur();
  const trans = document.getAnimations().filter((x) => x.transitionProperty).map((x) => x.transitionProperty + ' 等' + x.effect.getTiming().delay);
  out.push({ 刚失焦: m('刚失焦·过渡结束以前'), 过渡: [...new Set(trans)].slice(0, 12) });
  finish();
  out.push(m('失焦以后'));
  ta.value = '往前走'; ta.dispatchEvent(new Event('input', { bubbles: true })); finish();
  out.push(m('有字·没焦点'));
  ta.value = ''; ta.dispatchEvent(new Event('input', { bubbles: true })); finish();
  // 菜单开着不收
  const bt = q('.fake-tools .pill'); bt.setAttribute('aria-haspopup', 'menu'); bt.setAttribute('aria-expanded', 'true'); finish();
  out.push(m('模型菜单开着'));
  bt.setAttribute('aria-expanded', 'false'); finish();
  // 钮上有焦点不收
  const ch = q('.fake-chips button'); ta.focus(); ch.focus(); finish();
  out.push(m('焦点在钮上'));
  ch.blur(); finish();
  // 对话里改一条回复的输入框不算
  const ed = document.createElement('textarea'); ed.placeholder = '改回复'; [...document.querySelectorAll('.rili-markdown-renderer')].pop().appendChild(ed); ed.focus(); finish();
  out.push(m('改回复·对话里的输入框有焦点'));
  ed.remove(); finish();
  out.push(m('复原'));
  return JSON.stringify(out, null, 0).replace(/\},\{/g, '},\n{');
} catch (e) { return "出错 " + e.stack; } })()
