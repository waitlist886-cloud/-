// 第四版大框样张·宽屏：最新一条读到末尾、最新一条开头、往上翻到旧回复、点面板的转场几帧、面板、背包、同行、返回手札
const last = () => [...document.querySelectorAll('.rili-markdown-renderer')].pop();
export default async ({ page, shot }) => {
  const conv = async (fn, arg) => { await page.evaluate(fn, arg); await page.waitForTimeout(450); };
  const freeze = async (t) => page.evaluate((t) => { document.getAnimations().forEach((a) => { a.pause(); a.currentTime = t; }); }, t);
  const finish = async () => { await page.evaluate(() => document.getAnimations().forEach((a) => a.finish())); await page.waitForTimeout(250); };
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
  console.log(await page.evaluate(() => JSON.stringify({ rows: document.querySelectorAll('div[style*="contain: layout"]').length, tabsVisible: [...document.querySelectorAll('.sz-tabs')].map((t) => getComputedStyle(t).display), anims: document.getAnimations().length })));
};
