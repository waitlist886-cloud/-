export default async ({ page, shot, scrollTo }) => {
  await scrollTo('.rili-markdown-renderer', 'start', '0', 70); await shot('1top');
  await scrollTo('.choices', 'center', '0'); await shot('2choices');
  await page.evaluate(() => { const r=document.querySelectorAll('.rili-markdown-renderer')[0]; r.scrollIntoView({block:'end'}); document.querySelector('#conversation').scrollTop += 230; });
  await page.waitForTimeout(300); await shot('3bottom');
};
