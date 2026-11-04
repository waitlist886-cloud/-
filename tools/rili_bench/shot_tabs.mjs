// 一纪的七页一张一张截（11-04 山铜纪那一轮添的）：每一页跑一遍 static_bench.mjs，eval 点那个页签，把转场跑完再截。
// 用法：node shot_tabs.mjs <样本> <输出目录> [tabs=panel,deed,bag,party,news,mem,war] [w=1920] [h=1080] [extracss= extrarules= art=]
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const [sample, outDir, ...rest] = process.argv.slice(2);
const opt = Object.fromEntries(rest.map((a) => a.split('=')));
const tabs = (opt.tabs || 'panel,deed,bag,party,news,mem,war').split(',');
fs.mkdirSync(outDir, { recursive: true });
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'shot_tabs_'));
for (const t of tabs) {
  const ev = path.join(tmp, t + '.js');
  // 无头里动画时钟不走，点完把按时间走的动画都跑完；滚回这一页的页头
  fs.writeFileSync(ev, `(async () => {
    const tab = [...document.querySelectorAll('.sz-tab.t-${t} input')].pop();
    if (!tab) return 'no tab ${t}';
    tab.click();
    await new Promise((r) => setTimeout(r, 60));
    document.getAnimations().forEach((a) => { try { if (a.timeline === document.timeline) a.finish(); } catch (e) {} });
    window.lay && window.lay();
    const c = document.getElementById('conversation');
    const p = [...document.querySelectorAll('.p-${t}')].pop();
    if (p) c.scrollTop += p.getBoundingClientRect().top - 110;
    await new Promise((r) => setTimeout(r, 120));
    return 'ok ${t}';
  })()`);
  const args = [path.join(here, 'static_bench.mjs'), sample, path.join(outDir, t + '.png'), `w=${opt.w || 1920}`, `h=${opt.h || 1080}`, `eval=${ev}`, 'scroll=latest'];
  for (const k of ['extracss', 'extrarules', 'art', 'chips', 'sidebar', 'theme']) if (opt[k]) args.push(`${k}=${opt[k]}`);
  const r = spawnSync(process.execPath, args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
  console.log(t, (r.stdout || '').trim().split('\n').slice(-2).join(' ').slice(0, 160), (r.stderr || '').slice(0, 200));
}
fs.rmSync(tmp, { recursive: true, force: true });
