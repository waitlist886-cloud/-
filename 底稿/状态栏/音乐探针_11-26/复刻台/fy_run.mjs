// 用法：node fy_run.mjs <风月卡.json> <样本目录> <输出目录> <static_bench_fy.mjs>
// 拿风月复刻台里抄的三道工序（正则脚本、消息标签过滤、样式前缀），展开每一种写法，塞进页面（innerHTML），量留下了什么。
// 风月真页面怎么挂 HTML（整段换 innerHTML 还是 React 对着改）不知道，所以这里只验展开和过滤，不量流式。
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright-core';

const [cardPath, smpDir, outDir, fySrc] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const src = fs.readFileSync(fySrc, 'utf8');
const body = src.slice(src.indexOf('// ---- 正则脚本'), src.indexOf('const rules = card.regex_rp'));
const lib = path.join(outDir, 'fy_lib.mjs');
fs.writeFileSync(lib, body.replace('export function applyRegexScripts', 'function applyRegexScripts') + '\nexport { applyRegexScripts, fyMarkdown, prefix };\n');
const { applyRegexScripts, fyMarkdown, prefix } = await import('file:///' + lib.replace(/\\/g, '/'));
const card = JSON.parse(fs.readFileSync(cardPath, 'utf8'));
const css = prefix(card.built_in_css);
const files = fs.readdirSync(smpDir).filter((f) => f.endsWith('.txt')).sort();
const rows = files.map((f) => {
  const raw = fs.readFileSync(path.join(smpDir, f), 'utf8');
  const html = fyMarkdown(applyRegexScripts(raw, card.regex_rp, 1, 'renderOnly'));
  return { f, html };
});
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true, args: ['--autoplay-policy=no-user-gesture-required', '--mute-audio'] });
const page = await browser.newPage({ viewport: { width: 720, height: 1400 } });
await page.setContent(`<!doctype html><html><head><meta charset="utf-8"></head><body style="background:#fff"><div id="installedBuiltInCss"><style>${css}</style><div id="box" class="markdown-body"></div></div></body></html>`);
const rep = [];
for (const { f, html } of rows) {
  const info = await page.evaluate((h) => {
    const b = document.getElementById('box');
    b.innerHTML = h;
    const media = [...b.querySelectorAll('audio:not([hidden]),video:not([hidden]),embed,object,iframe,[data-action]:not([hidden])')].map((e) => e.outerHTML.replace(/https:\/\/[^"]+\//g, '…/').slice(0, 200));
    const kk = [...b.querySelectorAll('.bgmp .kk')].map((e) => getComputedStyle(e, '::after').content.replace(/"/g, ''));
    const tj = [...b.querySelectorAll('.bgmk .r')].map((e) => e.textContent + getComputedStyle(e.querySelector('i'), '::after').content.replace(/"/g, ''));
    const gray = [...b.querySelectorAll('.bgml')].map((e) => e.textContent);
    return { n: b.querySelectorAll('.bgmp').length, media, kk, tj, gray, sect: b.innerText.includes('§') };
  }, html);
  rep.push(`\n## ${f}\n蓝框 ${info.n}；灰字 ${JSON.stringify(info.gray)}；正文里还有 § 字 ${info.sect}\n属性行 ${info.kk.join(' ')}\n播放器 ${info.media.join('\n        ')}`);
  if (f === '测零_首.txt') rep.push('体检：\n  ' + info.tj.join('\n  '));
  await page.screenshot({ path: path.join(outDir, f.replace('.txt', '.png')), fullPage: true });
}
fs.writeFileSync(path.join(outDir, '报告.txt'), rep.join('\n'));
console.log(rep.join('\n'));
await browser.close();
