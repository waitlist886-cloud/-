// 复刻台上量：内容列居中、框下沿和输入栏、页签、气泡清干净没有；再把输入框往里包几层、回复底下那行加 bg- 类，看选择器认不认得
(() => {
  const r = (el) => { const b = el.getBoundingClientRect(); return { l: +b.left.toFixed(1), r: +b.right.toFixed(1), t: +b.top.toFixed(1), b: +b.bottom.toFixed(1), w: +b.width.toFixed(1), h: +b.height.toFixed(1) }; };
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => [...document.querySelectorAll(s)];
  const vh = innerHeight;
  const shell = $('main div.custom-styles');
  const after = getComputedStyle(shell, '::after');
  const out = {};
  out.vw = innerWidth; out.vh = vh;
  out.shell = r(shell);
  out.main = r($('main'));
  out.conv = r($('#conversation'));
  const allR = $$('.rili-markdown-renderer');
  const last = allR[allR.length - 1];
  out.reply = r(last);
  out.replyCenter = (r(last).l + r(last).r) / 2;
  out.tabs = r(last.querySelector('.dm-tabs'));
  out.tabsCenter = (out.tabs.l + out.tabs.r) / 2;
  out.hud = r(last.querySelector('details.dm-hud'));
  out.inputBlock = r($('.fake-input-inner'));
  out.inputTopFromBottom = +(vh - out.inputBlock.t).toFixed(1);
  out.frame = { left: after.left, right: after.right, top: after.top, bottom: after.bottom, width: after.width, height: after.height };
  const fb = shell.getBoundingClientRect().bottom - parseFloat(after.bottom);
  out.frameBottomY = +fb.toFixed(1);
  out.gapFrameToInput = +(out.inputBlock.t - fb).toFixed(1);
  const bub = last.closest('.bubble');
  const cs = getComputedStyle(bub);
  out.bubble = { bg: cs.backgroundColor, bl: cs.borderLeftWidth, pl: cs.paddingLeft, pr: cs.paddingRight, w: cs.width };
  const ass = last.closest('.is-assistant');
  out.isAssistant = { w: getComputedStyle(ass).width, color: getComputedStyle(ass).color };
  out.dock = getComputedStyle(shell).getPropertyValue('--fm-dock');
  out.hudtop = getComputedStyle(shell).getPropertyValue('--fm-hudtop');
  out.gutter = getComputedStyle($('#conversation')).scrollbarGutter;
  const inner = $('.fake-input-inner');
  out.input = { bg: getComputedStyle(inner).backgroundColor, border: getComputedStyle(inner).borderTopColor, color: getComputedStyle(inner).color };
  out.outer = { bg: getComputedStyle($('.fake-input')).backgroundColor, color: getComputedStyle($('.fake-input')).color, varBg: getComputedStyle($('.fake-input')).getPropertyValue('--background') };
  out.chipBtn = { color: getComputedStyle($('.fake-chips button')).color, border: getComputedStyle($('.fake-chips button')).borderTopColor };
  out.nav = { bg: getComputedStyle($('nav.custom-styles')).backgroundColor, color: getComputedStyle($('nav header')).color };
  out.mainBg = getComputedStyle($('main')).backgroundColor;
  const ub = $('.is-user .bubble');
  out.user = { bg: getComputedStyle(ub).backgroundColor, border: getComputedStyle(ub).borderTopColor, color: getComputedStyle(ub).color };
  // 真页面的结构：输入框往上好几层，圆角块带 bg-background，中间几层没有底色或者 bg-transparent
  const ta = $('#chat-input');
  const w1 = document.createElement('div'); w1.className = 'relative flex';
  const w2 = document.createElement('div'); w2.className = 'bg-transparent grow';
  ta.parentNode.insertBefore(w1, ta); w1.appendChild(w2); w2.appendChild(ta);
  out.deep = {
    block: getComputedStyle(inner).backgroundColor,
    w1: getComputedStyle(w1).backgroundColor,
    w2: getComputedStyle(w2).backgroundColor,
    outer: getComputedStyle($('.fake-input')).backgroundColor,
    flexWrap: getComputedStyle($('.flex.flex-col.items-center')).color === getComputedStyle(inner).color ? 'same' : 'differ',
    textareaColor: getComputedStyle(ta).color,
  };
  // 回复底下那一排钮带底色时（手机上真页面就是这样）
  const tool = last.closest('.is-assistant').querySelector('.msg-tools');
  const fakeBar = document.createElement('div'); fakeBar.className = 'bg-background border';
  const btn = document.createElement('button'); btn.textContent = 'x'; fakeBar.appendChild(btn); tool.appendChild(fakeBar);
  out.toolbar = { bg: getComputedStyle(fakeBar).backgroundColor, border: getComputedStyle(fakeBar).borderTopColor, color: getComputedStyle(fakeBar).color, btn: getComputedStyle(btn).color };
  fakeBar.remove();
  // 回复里面带 bg- 类的元素不该被认成那一排钮
  const inside = document.createElement('div'); inside.className = 'bg-x'; last.appendChild(inside);
  out.insideReply = getComputedStyle(inside).backgroundColor;
  inside.remove();
  w1.parentNode.insertBefore(ta, w1); w1.remove();
  return JSON.stringify(out, null, 1);
})()
