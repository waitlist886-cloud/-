// 用法：node run.mjs <日里卡.json> <样本目录> <输出目录>
// 1) 一种写法一条，整段渲染，量播放器的标签和属性、截图；2) 流式：一段一段长，数播放器换了几个、play 了几回；
// 3) 新回复出来以后上一条还在不在放；4) 卸载再挂上会不会又放。浏览器开着 no-user-gesture-required，只看机制，不看平台的自动播放策略。
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { scopeCss } from './platform.mjs';

const here = path.dirname(new URL(import.meta.url).pathname).replace(/^\/(\w:)/, '$1');
const [cardPath, smpDir, outDir] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const card = JSON.parse(fs.readFileSync(cardPath, 'utf8'));
const { css } = scopeCss(card.injectStyles);
const bundle = path.join(here, 'bundle_stream.js');
execFileSync(process.execPath, [path.join(here, 'node_modules/esbuild/bin/esbuild'), path.join(here, 'stream.jsx'), '--bundle', '--outfile=' + bundle, '--define:process.env.NODE_ENV="production"', '--log-level=warning']);
const html = path.join(outDir, 'bench.html');
fs.writeFileSync(html, `<!doctype html><html><head><meta charset="utf-8"><style>body{background:#0a0a0a;color:#eee;font:14px system-ui;margin:0}</style></head><body><div id="root"></div>
<script>window.RULES=${JSON.stringify(card.assistantRegexReplace).replace(/</g, '\\u003c')};window.BCSS=${JSON.stringify(css).replace(/</g, '\\u003c')};
window.LOG=[];let k=0;for(const ev of ['play','playing','pause','emptied','loadstart','error'])document.addEventListener(ev,e=>{const t=e.target;if(!t.__id)t.__id=++k;LOG.push([ev,t.__id,t.currentSrc.split('/').pop()||t.src.split('/').pop(),t.closest('.row')?.dataset.i]);},true);</script>
<script src="file:///${bundle.replace(/\\/g, '/')}"></script></body></html>`);
const chrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const browser = await chromium.launch({ executablePath: chrome, headless: true, args: ['--autoplay-policy=no-user-gesture-required', '--mute-audio'] });
const page = await browser.newPage({ viewport: { width: 720, height: 1400 } });
const errs = [];
page.on('pageerror', (e) => errs.push(e.message));
await page.goto('file:///' + html.replace(/\\/g, '/'));
await page.waitForTimeout(500);
const rep = [];
rep.push('浏览器认 :playing 吗：' + await page.evaluate(() => CSS.supports('selector(:playing)')));
const files = fs.readdirSync(smpDir).filter((f) => f.endsWith('.txt')).sort();
const set = (msgs) => page.evaluate((m) => window.setMsgs(m), msgs);
// 1) 整段渲染
for (const f of files) {
  const raw = fs.readFileSync(path.join(smpDir, f), 'utf8');
  await set([{ raw, show: true }]);
  await page.waitForTimeout(400);
  const info = await page.evaluate(() => {
    const r = document.querySelector('.rili-markdown-renderer');
    const media = [...r.querySelectorAll('audio:not([hidden]),video:not([hidden]),embed,object,iframe,[data-action]:not([hidden])')].map((e) => e.outerHTML.replace(/https:\/\/[^"]+\//g, '…/').slice(0, 220));
    const kk = [...r.querySelectorAll('.bgmp .kk')].map((e) => getComputedStyle(e, '::after').content.replace(/"/g, ''));
    const st = [...r.querySelectorAll('.bgmp-st')].map((e) => getComputedStyle(e, '::after').content.replace(/"/g, ''));
    const tj = [...r.querySelectorAll('.bgmk .r')].map((e) => e.textContent + getComputedStyle(e.querySelector('i'), '::after').content.replace(/"/g, ''));
    const gray = [...r.querySelectorAll('.bgml')].map((e) => e.textContent);
    return { n: r.querySelectorAll('.bgmp').length, media, kk, st, tj, gray, leftover: /§/.test(r.textContent) && r.innerText.split('\n').filter((l) => l.includes('§') && !l.includes('这一行')) };
  });
  rep.push(`\n## ${f}\n蓝框 ${info.n} 个；灰字 ${JSON.stringify(info.gray)}；漏网的 § 行 ${JSON.stringify(info.leftover)}\n属性行 ${info.kk.join(' ')}\n状态灯 ${info.st.join(' ')}\n播放器 ${info.media.join('\n        ')}`);
  if (f === '测零_首.txt') rep.push('体检：\n  ' + info.tj.join('\n  '));
  await page.screenshot({ path: path.join(outDir, f.replace('.txt', '.png')), fullPage: true });
}
// 2) 流式，3) 叠音，4) 卸载重挂
const raw = (f) => fs.readFileSync(path.join(smpDir, f), 'utf8');
for (const f of ['测一_首.txt', '测三_首.txt', '测三_尾.txt', '测四_首.txt', '测五_首.txt']) {
  await page.evaluate(() => { LOG.length = 0; });
  await set([]);
  const full = raw(f);
  const msgs = [{ raw: raw('测零_首.txt'), show: true }, { raw: '', show: true }];
  for (let n = 4; n <= full.length + 4; n += 4) { msgs[1] = { raw: full.slice(0, n), show: true }; await set(msgs); await page.waitForTimeout(15); }
  await page.waitForTimeout(600);
  const a = await page.evaluate(() => ({ ids: [...new Set(LOG.filter((x) => x[0] === 'play').map((x) => x[1]))], plays: LOG.filter((x) => x[0] === 'play').length, now: [...document.querySelectorAll('.row[data-i="1"] audio:not([hidden]),.row[data-i="1"] video')].map((e) => [e.__id, e.paused]) }));
  rep.push(`\n## 流式 ${f}：一段四个字长出来，播放器先后换了 ${a.ids.length} 个（id ${a.ids}），play ${a.plays} 回；写完以后挂着的 [id, 停着?] ${JSON.stringify(a.now)}`);
  // 叠音：再来一条
  await page.evaluate(() => { LOG.length = 0; });
  msgs.push({ raw: raw(f.replace('_首', '_尾').replace('_尾.txt', '_首.txt')).replace(/曲 甲/g, '曲 乙'), show: true });
  await set(msgs);
  await page.waitForTimeout(500);
  const b = await page.evaluate(() => [...document.querySelectorAll('.row')].map((r) => [r.dataset.i, [...r.querySelectorAll('audio:not([hidden]),video')].map((e) => (e.paused ? '停' : '放') + (e.currentSrc || '').split('/').pop())]));
  rep.push(`  再来一条以后各条：${JSON.stringify(b)}`);
  // 卸载第 1 条再挂上
  msgs[1] = { ...msgs[1], show: false };
  await set(msgs);
  await page.waitForTimeout(300);
  await page.evaluate(() => { LOG.length = 0; });
  msgs[1] = { ...msgs[1], show: true };
  await set(msgs);
  await page.waitForTimeout(600);
  const c = await page.evaluate(() => ({ plays: LOG.filter((x) => x[0] === 'play').map((x) => x.join(':')), now: [...document.querySelectorAll('.row[data-i="1"] audio:not([hidden]),.row[data-i="1"] video')].map((e) => [e.__id, e.paused, Math.round(e.currentTime * 10) / 10]) }));
  rep.push(`  第 1 条卸载再挂上：play ${JSON.stringify(c.plays)}，挂上以后 [id, 停着?, 放到几秒] ${JSON.stringify(c.now)}`);
}
if (errs.length) rep.push('\n页面报错：' + [...new Set(errs)].join('\n'));
fs.writeFileSync(path.join(outDir, '报告.txt'), rep.join('\n'));
console.log(rep.join('\n'));
await browser.close();
