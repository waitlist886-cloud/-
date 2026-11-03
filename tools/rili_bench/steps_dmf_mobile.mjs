// 《大旻长夜》大框样张·手机：末尾、开卷、玉牒、群英、风闻、旧回复
export default async ({ page, shot }) => {
  const conv = async (fn, arg) => { await page.evaluate(fn, arg); await page.waitForTimeout(400); };
  const finish = async () => { await page.evaluate(() => document.getAnimations().filter((a) => a.timeline instanceof DocumentTimeline).forEach((a) => a.finish())); await page.waitForTimeout(250); };
  const topOf = async (sel, off = 90) => conv(([sel, off]) => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].filter((r) => r.querySelector('.dm-run:not(.dm-fn)')).pop(); const el = r.querySelector(sel); el.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= off; }, [sel, off]);
  const tab = async (k) => { await page.evaluate((k) => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].filter((r) => r.querySelector('.dm-run:not(.dm-fn)')).pop(); r.querySelector('.t-' + k).click(); }, k); await finish(); };
  await conv(() => { const c = document.querySelector('#conversation'); c.scrollTop = c.scrollHeight; }); await shot('1末尾');
  await topOf('details.dm-hud', 70); await shot('2开卷');
  await tab('ming'); await topOf('.p-ming', 70); await shot('3玉牒');
  await tab('jian'); await topOf('.p-jian', 70); await shot('4群英');
  await tab('wen'); await topOf('.p-wen', 70); await shot('5风闻');
  await conv(() => { const r = document.querySelectorAll('.rili-markdown-renderer')[0]; r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop += 300; }); await shot('6旧回复');
};
