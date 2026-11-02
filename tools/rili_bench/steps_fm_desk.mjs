// 第四版大框样张·宽屏：最新一条读到末尾、最新一条开头、往上翻到旧回复、点面板的转场几帧、面板、背包、同行、返回手札
const last = () => [...document.querySelectorAll('.rili-markdown-renderer')].pop();
export default async ({ page, shot }) => {
  const conv = async (fn, arg) => { await page.evaluate(fn, arg); await page.waitForTimeout(450); };
  const freeze = async (t) => page.evaluate((t) => { document.getAnimations().filter((a) => a.timeline instanceof DocumentTimeline).forEach((a) => { a.pause(); a.currentTime = t; }); }, t);
  const finish = async () => { await page.evaluate(() => document.getAnimations().filter((a) => a.timeline instanceof DocumentTimeline).forEach((a) => a.finish())); await page.waitForTimeout(250); };
  await conv(() => { const c = document.querySelector('#conversation'); c.scrollTop = c.scrollHeight; }); await shot('1end');
  await conv(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].pop(); r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 110; }); await shot('2latest');
  await conv(() => { const r = document.querySelectorAll('.rili-markdown-renderer')[0]; r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop += 380; }); await shot('3older');
  await conv(() => { const c = document.querySelector('#conversation'); c.scrollTop = c.scrollHeight; });
  await page.evaluate(() => { [...document.querySelectorAll('.t-panel')].pop().click(); });
  await freeze(120); await shot('4t120');
  await freeze(420); await shot('5t420');
  await freeze(780); await shot('6t780');
  await finish(); await shot('7panel');
  await conv(() => { const p = [...document.querySelectorAll('.p-panel')].pop(); p.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 150; }); await shot('8paneltop');
  await page.evaluate(() => { [...document.querySelectorAll('.t-bag')].pop().click(); }); await finish();
  await conv(() => { const p = [...document.querySelectorAll('.p-bag')].pop(); p.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 150; }); await shot('9bag');
  await page.evaluate(() => { [...document.querySelectorAll('.t-party')].pop().click(); }); await finish();
  await conv(() => { const p = [...document.querySelectorAll('.p-party')].pop(); p.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 150; }); await shot('10party');
  await page.evaluate(() => { [...document.querySelectorAll('.p-party .sz-x')].pop().click(); }); await freeze(300); await shot('11back');
  await finish(); await shot('12prose');
  // 框右边那一颗跟着滚动走：滚到顶、中间、底各读一回它的位置（宽屏才有）
  for (const f of [0, 0.5, 1]) {
    await page.evaluate((f) => { const c = document.querySelector('#conversation'); c.scrollTop = (c.scrollHeight - c.clientHeight) * f; }, f); await page.waitForTimeout(200);
    console.log('gem', f, await page.evaluate(() => { const sh = document.querySelector('#conversation').closest('.custom-styles'); return getComputedStyle(sh, '::before').backgroundPosition.split(', ')[4]; }));
  }
  console.log(await page.evaluate(() => JSON.stringify({ rows: document.querySelectorAll('div[style*="contain: layout"]').length, tabsVisible: [...document.querySelectorAll('.sz-tabs')].map((t) => getComputedStyle(t).display), anims: document.getAnimations().length })));
};
