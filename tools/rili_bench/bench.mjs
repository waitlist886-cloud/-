// 用法：node bench.mjs <card.json> <fx1,fx2,…> <输出前缀> [w=1440] [h=900] [mobile=1] [theme=light] [steps=脚本.mjs] [extracss=文件] [extrarules=文件]
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { scopeCss, applyRules } from './platform.mjs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const here = path.dirname(new URL(import.meta.url).pathname);
const [cardPath, fxList, prefix, ...rest] = process.argv.slice(2);
const opt = Object.fromEntries(rest.map((a) => a.split('=')));
const W = Number(opt.w || 1440), H = Number(opt.h || 900), mobile = !!opt.mobile;
const card = JSON.parse(fs.readFileSync(cardPath, 'utf8'));
let styles = card.injectStyles || '';
if (opt.extracss) styles += '\n' + fs.readFileSync(opt.extracss, 'utf8');
let rules = card.assistantRegexReplace || [];
if (opt.extrarules) rules = rules.concat(JSON.parse(fs.readFileSync(opt.extrarules, 'utf8')));
const { css, dropped } = scopeCss(styles);
if (Object.keys(dropped).length) console.log('被平台丢掉的 at 规则：', JSON.stringify(dropped));
const messages = [];
for (const f of fxList.split(',')) {
  messages.push({ role: 'user', text: '（玩家输入）' });
  messages.push({ role: 'assistant', html: applyRules(fs.readFileSync(f, 'utf8'), rules) });
}
const outDir = path.dirname(path.resolve(prefix));
fs.mkdirSync(outDir, { recursive: true });
const bundle = path.join(here, 'bundle.js');
if (!fs.existsSync(bundle) || fs.statSync(bundle).mtimeMs < fs.statSync(path.join(here, 'app.jsx')).mtimeMs)
  execFileSync(path.join(here, 'node_modules/.bin/esbuild'), [path.join(here, 'app.jsx'), '--bundle', '--outfile=' + bundle, '--define:process.env.NODE_ENV="production"', '--log-level=warning']);
const preflight = fs.readFileSync(path.join(here, 'node_modules/tailwindcss/preflight.css'), 'utf8').replace(/@layer base\s*\{/, '').replace(/\}\s*$/, '').replace(/--theme\([^)]*\)/g, 'initial');
const page0 = `<!doctype html><html lang="zh" class="${opt.theme === 'light' ? 'light' : 'dark'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>${preflight}</style><style>${fs.readFileSync(path.join(here, 'shell.css'), 'utf8')}</style></head><body><div id="root"></div><script>window.BENCH=${JSON.stringify({ messages, css, sidebar: !mobile && W >= 1000 }).replace(/</g, '\\u003c')}</script><script src="file://${bundle}"></script></body></html>`;
const htmlPath = path.join(outDir, path.basename(prefix) + '.html');
fs.writeFileSync(htmlPath, page0);
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: W, height: H }, hasTouch: mobile, isMobile: mobile, deviceScaleFactor: mobile ? 2 : 1, colorScheme: opt.theme === 'light' ? 'light' : 'dark' });
const page = await ctx.newPage();
const logs = [];
page.on('console', (m) => { if (m.type() === 'error') logs.push(m.text().slice(0, 200)); });
page.on('pageerror', (e) => logs.push('pageerror: ' + e.message));
if (!opt.net) await page.route('**/*', (r) => (/^(file|data):/.test(r.request().url()) ? r.continue() : r.abort()));
await page.goto('file://' + htmlPath);
await page.waitForTimeout(900);
const conv = page.locator('#conversation');
const shot = async (name, clip) => page.screenshot({ path: `${prefix}-${name}.png`, ...(clip ? { clip } : {}) });
const scrollTo = async (sel, block = 'start', nth = 'last', off = 110) => { await page.evaluate(([sel, block, nth, off]) => { const all = [...document.querySelectorAll(sel)]; const el = nth === 'last' ? all.pop() : all[Number(nth)]; el.scrollIntoView({ block }); if (block === 'start') document.querySelector('#conversation').scrollTop -= off; }, [sel, block, nth, off]); await page.waitForTimeout(300); };
if (opt.steps) {
  const steps = await import(path.resolve(opt.steps));
  await steps.default({ page, conv, shot, scrollTo, prefix });
} else {
  await scrollTo('.is-assistant', 'start');
  await shot('top');
}
if (logs.length) console.log('控制台：\n' + [...new Set(logs)].join('\n'));
await browser.close();
