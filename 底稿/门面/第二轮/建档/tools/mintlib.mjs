// 铸印 → 确认页 → 书架上看看 → 往后的廊第二十一格 → 翻开 → 借阅卡。 node mintlib.mjs W H 前缀 书
import { open, sleep, BASE } from './cdp.mjs';
const [W, H] = [+(process.argv[2] || 1920), +(process.argv[3] || 945)];
const OUT = process.argv[4] || 'shots/m'; const book = process.argv[5] || 'bronze';
const MS = { bronze: { book: 'bronze', era: '山铜纪', at: 'p1', title: '犁的年月', line: '犁的年月·雨城清查', year: '2' }, moon: { book: 'moon', era: '月银纪', at: 'm07', title: '焚原断刃', line: '万兽·焚原', year: '1690' },
  strife: { book: 'strife', era: '纷争纪', at: 'free', title: '第二十二张', line: '', year: '' }, maze: { book: 'maze', era: '迷宫纪', at: 'q5', title: '黑潮的年月', line: '黑潮的年月·头一回斩首', year: '852' },
  now: { book: 'maze', era: '迷宫纪', at: '1001', site: '阿卡迪亚·外环棚区', ti: '井口边的不眠之城', line: '迷宫纪1001年·阿卡迪亚·外环棚区', year: '1001' } };
const M = MS[book];
const P = await open(W, H, { mobile: W < 861, url: BASE + '?t=' + Date.now() });
await P.until('window.__tb && window.Shell', 30000);
await P.ev('__tb.skip(); return 1'); await sleep(1200);
await P.ev(`await Shell.startBuild(${JSON.stringify(M)}); return 1`);
const idle = async () => { await sleep(150); await P.until('window.__bd && !__bd.busy', 15000); await sleep(250); };
await sleep(2200);
await P.ev(`const F = __bd.F; F.soul = 'native'; F.name = '诺拉'; F.year = '1150'; F.race = 'human'; F.tier = '共鸣·寻音'; __bd.way('direct'); return 1`); await idle();
await P.ev(`__bd.F._max = 11; __bd.go(11); return 1`); await idle(); await sleep(900);
await P.shot(OUT + '_11.jpg');
await P.ev(`document.querySelector('#sh-build .bx-ctl [data-a="next"]').click(); return 1`);
await sleep(700); await P.shot(OUT + '_m1.jpg'); await sleep(1300); await P.shot(OUT + '_m2.jpg'); await sleep(1500); await P.shot(OUT + '_m3.jpg');
await P.until(`document.querySelector('#sh-seal.on')`, 15000); await sleep(900); await P.shot(OUT + '_seal.jpg');
const raw = await P.ev(`return __bd.cred()`);
await P.ev(`document.querySelector('#sh-seal [data-a="lib"]').click(); return 1`);
await P.until(`window.Library && Library.isOpen() && Library.state.view === 'wing'`, 15000); await sleep(1500);
await P.shot(OUT + '_lib.jpg');
await P.ev(`const e = document.querySelector('#lib .lb-sp.lx-mine'); e.scrollIntoView({ block: 'center', inline: 'center' }); e.click(); return 1`);
await P.until(`Library.state.book`, 15000); await sleep(2500);
await P.shot(OUT + '_read.jpg');
const txt = await P.ev(`return document.querySelector('#lib .rd-flow').innerText.slice(0, 200)`);
console.log('reader', JSON.stringify(txt));
await P.ev(`Library.close(true); Library.open(); return 1`); await sleep(1500);
await P.ev(`document.querySelector('#lib .lb-card').click(); return 1`); await sleep(900);
await P.shot(OUT + '_lend.jpg');
console.log('lend', JSON.stringify(await P.ev(`return [...document.querySelectorAll('#lib .lb-lend tr')].slice(-2).map((t) => t.innerText).join(' / ')`)));
console.log('errs', JSON.stringify(P.errs.filter((e) => !/favicon/.test(e)).slice(0, 12)));
await P.close();
