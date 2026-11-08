// 风月手机输入栏（11-08 第二回）：快捷指令和翻页并成一行一直露着，输入框闲着压成一行。读闲着、点进去、打了字、清空四种样子，
// 和翻页那一排停在哪（应当停在最新那几页）。static_bench_fy.mjs 的 eval= 用（要手机宽）
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const q = (s) => document.querySelector(s);
  const ta = q('#ai-chat-input');
  const foot = q('.bg-gradient-to-t');
  const box = (s) => { const r = q(s).getBoundingClientRect(); return Math.round(r.left) + ',' + Math.round(r.top) + ' ' + Math.round(r.width) + '×' + Math.round(r.height); };
  const look = (tag) => [tag, '栏高 ' + Math.round(foot.getBoundingClientRect().height), '输入框 ' + Math.round(ta.getBoundingClientRect().height),
    '快捷指令 ' + box('#ai-mod-button2') + ' ' + getComputedStyle(q('#ai-mod-button2')).visibility,
    '翻页 ' + box('#customized-pagination-container'), '右下钮 ' + getComputedStyle(q('#ai-input-controls')).visibility].join(' | ');
  await sleep(1200);
  const pc = q('#customized-pagination-container');
  const a = look('闲着');
  const pr = pc.getBoundingClientRect();
  const seen = [...pc.querySelectorAll('a,button,input,nav>div>span,li>span')].filter((e) => !e.closest('.sr-only'))
    .filter((e) => { const r = e.getBoundingClientRect(); return r.left >= pr.left - 1 && r.right <= pr.right + 1; })
    .map((e) => e.tagName === 'INPUT' ? '[' + e.value + ']' : (e.textContent.trim().replace('More pages', '') || (e.getAttribute('aria-label') || '').replace('Go to previous page', '‹').replace('Go to next page', '›') || '…')).join(' ');
  const mb = q('#ai-mod-button2').getBoundingClientRect();
  const cmdSeen = [...q('#ai-mod-button2').children].filter((e) => { const r = e.getBoundingClientRect(); return r.right <= mb.right + 1; }).map((e) => e.textContent.trim()).join('、');
  const pos = '翻页滚动 ' + Math.round(pc.scrollLeft) + ' / 可滚 ' + Math.round(pc.scrollWidth - pc.clientWidth) + '（右往左排，0 是停在最右头）| 翻页露出来的 ' + seen +
    ' | 翻页里的背景图 ' + getComputedStyle(q('#customized-pagination')).backgroundImage.slice(0, 20) + '\n快捷指令露出来的 ' + cmdSeen;
  ta.focus();
  await sleep(700);
  const b = look('点进去');
  ta.value = '往北走';
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  ta.blur();
  await sleep(900);
  const c = look('有字、没焦点');
  ta.value = '';
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  await sleep(900);
  const d = look('清空、没焦点');
  const pb = [...pc.querySelectorAll('a,button')].find((e) => e.textContent.trim() === '8');
  if (pb) pb.focus();
  await sleep(700);
  const e = look('焦点在翻页钮上');
  return [a, pos, b, c, d, e].join('\n');
})();
