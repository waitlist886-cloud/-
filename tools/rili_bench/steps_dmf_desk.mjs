// 《大旻长夜》大框样张·宽屏：末尾、开卷、推演、旧回复、点玉牒的转场几帧、各页、返回、点行策、滚动那一枚铜钱
export default async ({ page, shot }) => {
  const C = '#conversation';
  const conv = async (fn, arg) => { await page.evaluate(fn, arg); await page.waitForTimeout(450); };
  const freeze = async (t) => page.evaluate((t) => { document.getAnimations().filter((a) => a.timeline instanceof DocumentTimeline).forEach((a) => { a.pause(); a.currentTime = t; }); }, t);
  const finish = async () => { await page.evaluate(() => document.getAnimations().filter((a) => a.timeline instanceof DocumentTimeline).forEach((a) => a.finish())); await page.waitForTimeout(250); };
  const lastRun = () => [...document.querySelectorAll('.rili-markdown-renderer')].filter((r) => r.querySelector('.dm-run:not(.dm-fn)')).pop();
  const topOf = async (sel, off = 150) => conv(([sel, off]) => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].filter((r) => r.querySelector('.dm-run:not(.dm-fn)')).pop(); const el = r.querySelector(sel); el.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= off; }, [sel, off]);
  const tab = async (k) => { await page.evaluate((k) => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].filter((r) => r.querySelector('.dm-run:not(.dm-fn)')).pop(); r.querySelector('.t-' + k).click(); }, k); };
  await conv(() => { const c = document.querySelector('#conversation'); c.scrollTop = c.scrollHeight; }); await shot('01末尾');
  await topOf('details.dm-hud', 120); await shot('02开卷');
  await page.evaluate(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].filter((r) => r.querySelector('.dm-run:not(.dm-fn)')).pop(); r.querySelector('details.dm-hud').open = true; }); await page.waitForTimeout(300); await shot('03推演');
  await page.evaluate(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].filter((r) => r.querySelector('.dm-run:not(.dm-fn)')).pop(); r.querySelector('details.dm-hud').open = false; });
  await conv(() => { const r = document.querySelectorAll('.rili-markdown-renderer')[0]; r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop += 520; }); await shot('04旧回复');
  await topOf('.dm-acts-box', 260); await shot('05行止');
  await tab('ming');
  await freeze(120); await shot('06转场120');
  await freeze(480); await shot('07转场480');
  await freeze(800); await shot('08转场800');
  await finish(); await topOf('.p-ming', 140); await shot('09玉牒');
  await topOf('.p-ming .dm-sec-skill', 140); await shot('10武藏');
  for (const [k, n] of [['jian', '11群英'], ['wen', '12风闻'], ['li', '13经纬'], ['cang', '14藏卷']]) { await tab(k); await finish(); await topOf('.p-' + k, 140); await shot(n); }
  await page.evaluate(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].filter((r) => r.querySelector('.dm-run:not(.dm-fn)')).pop(); r.querySelector('.p-cang .dm-x').click(); }); await finish();
  await topOf('.dm-acts-box', 260); await shot('15返回行卷');
  await page.evaluate(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].filter((r) => r.querySelector('.dm-run:not(.dm-fn)')).pop(); r.querySelector('.dm-act').dispatchEvent(new MouseEvent('click', { bubbles: true })); });
  await page.waitForTimeout(250); await shot('16点行策');
  for (const f of [0, 0.5, 1]) {
    await page.evaluate((f) => { const c = document.querySelector('#conversation'); c.scrollTop = (c.scrollHeight - c.clientHeight) * f; }, f); await page.waitForTimeout(200);
    console.log('铜钱', f, await page.evaluate(() => { const sh = document.querySelector('#conversation').closest('.custom-styles'); return getComputedStyle(sh, '::before').backgroundPosition.split(', ')[4]; }));
  }
  console.log(await page.evaluate(() => JSON.stringify({
    rows: document.querySelectorAll('div[style*="contain: layout"]').length,
    tabs: [...document.querySelectorAll('.dm-tabs')].map((t) => getComputedStyle(t).display),
    hud: [...document.querySelectorAll('details.dm-hud')].map((t) => getComputedStyle(t).display),
    paneParent: (document.querySelector('.dm-pane') || {}).parentElement?.className,
    actsParent: (document.querySelector('.dm-acts-box') || {}).parentElement?.className,
    input: document.querySelector('#chat-input').value,
  })));
};
