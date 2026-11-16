// 验薄壳读指针那一段（11-16）：把薄壳的脚本放进一个假页面里跑，网络是真的。
//   node 底稿/门面/共用/test_ptr.mjs
// 三种情形：卡里带的是旧提交号（指针比它新，该换成指针的）；卡里带的就是现在这一版（照卡里的）；指针取不到（照卡里的）。
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PY = process.env.PYTHON || 'python';
const front = JSON.parse(fs.readFileSync(path.join(HERE, 'front.json'), 'utf8'));

function thin(cfgPatch, mirrors) {
  // 叫 make_thin.thin_html 出一份（cfg 可以改几样）
  const code = `
import sys, json, io
sys.path.insert(0, r'${HERE.replace(/\\/g, '/')}')
import make_thin
cfg = json.load(open(r'${path.join(HERE, 'front.json').replace(/\\/g, '/')}', encoding='utf-8'))
patch = json.loads(sys.argv[1])
for k, v in patch.items():
    if k == 'books':
        for b, o in v.items(): cfg['books'][b].update(o)
    else: cfg[k] = v
mir = json.loads(sys.argv[2]) or None
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdout.write(make_thin.thin_html(cfg=cfg, mirrors=mir))
`;
  return execFileSync(PY, ['-I', '-X', 'utf8', '-c', code, JSON.stringify(cfgPatch), JSON.stringify(mirrors || null)], { encoding: 'utf8', maxBuffer: 1 << 26 });
}

async function run(name, html, { blockPtr = false, blockRaw = false, stalePtr = null, gens = null } = {}) {
  const js = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]).pop();
  let written = '', resolveDone;
  const done = new Promise((r) => { resolveDone = r; });
  const boot = { innerHTML: '', appendChild() {} };
  const calls = [];
  const sandbox = {
    window: { innerWidth: 390, innerHeight: 800, AbortController },
    document: { getElementById: (id) => (id === 'boot' ? boot : null), open() {}, write(s) { written += s; }, close() { resolveDone(); }, createElement: () => ({}) },
    fetch: (u, o) => {
      calls.push(u);
      if (blockPtr && /front_ptr/.test(u)) return Promise.reject(new Error('blocked'));
      if (blockRaw && /raw\.githubusercontent/.test(u)) return Promise.reject(new Error('blocked'));
      // 一代一个分支的那一路：gens 里有的那几代答得出，没有的答 404（镜像对还没有的分支就是这样答的，不缓存）
      const gm = gens && u.match(/@front_ptr_g(\d+)\/front\.json/);
      if (gm) return new Promise((r) => setTimeout(() => r(gens[gm[1]] ? { ok: true, status: 200, json: async () => gens[gm[1]] } : { ok: false, status: 404, json: async () => ({}) }), 50));
      // 镜像上的指针还是旧的那一份（分支地址的缓存没过）：镜像一律答这一份，GitHub 那一头照真的取
      if (stalePtr && /jsdelivr[^/]*\/gh\/[^@]+@front_ptr\//.test(u)) return new Promise((r) => setTimeout(() => r({ ok: true, status: 200, json: async () => stalePtr }), 60));
      return fetch(u, o);
    },
    setTimeout, clearTimeout, Promise, JSON, Error, AbortController, console, Date,
  };
  sandbox.window.window = sandbox.window;
  vm.createContext(sandbox);
  const t0 = Date.now();
  vm.runInContext(js, sandbox);
  await Promise.race([done, new Promise((r) => setTimeout(r, 40000))]);
  const m = written.match(/window\.FRONT_CFG=(\{[\s\S]*?\});<\/script>/);
  const cfg = m ? JSON.parse(m[1]) : null;
  const sha = (u) => (u.match(/@([0-9a-f]{40})\//) || [])[1];
  const got = cfg && { n: cfg.n, mirror: cfg.mirror, shell: sha(cfg.old1001), strife: sha(cfg.books.strife.core), moon: sha(cfg.books.moon.core), ms: Date.now() - t0, ptrCalls: calls.filter((u) => /front_ptr/.test(u)).length };
  console.log(name, got ? JSON.stringify(got) : '没有换页（' + boot.innerHTML.slice(0, 60) + '）');
  return got;
}

const OLD = { strife: '4936489177970a043f6b0b911ac45749d6cb417e', moon: '4bb16b4e683c5f06e8e773e81435e8a85bd81eaa' };   // 11-15 那一版的两段
let bad = 0;
const want = (ok, what) => { if (!ok) { bad++; console.log('  ✗', what); } else console.log('  ✓', what); };

// 一、卡里带旧的，指针新
let g = await run('一 卡里旧、指针新', thin({ n: 1, books: { strife: { core: OLD.strife }, moon: { core: OLD.moon } } }));
want(g && g.strife === front.books.strife.core && g.moon === front.books.moon.core && g.n === front.n, '换成了指针上的提交号');
// 二、卡里就是这一版
g = await run('二 卡里就是这一版', thin({}));
want(g && g.strife === front.books.strife.core && g.n === front.n, '照卡里的（跟指针一样）');
// 三、卡里比指针新（指针旧，不许往回退）
g = await run('三 卡里比指针新', thin({ n: front.n + 1000, books: { strife: { core: OLD.strife } } }));
want(g && g.strife === OLD.strife && g.n === front.n + 1000, '没有叫旧指针带回去');
// 四、指针取不到
g = await run('四 指针取不到', thin({ n: 1, books: { strife: { core: OLD.strife } } }), { blockPtr: true });
want(g && g.strife === OLD.strife, '照卡里的那一份开');
// 五、镜像上的指针还是旧的（跟卡里一样旧），GitHub 那一头是新的：该拿到新的（11-16 修建档页滚不动那一回，镜像的分支缓存没跟上，就是这种情形）
const OLDSHELL = '03e4d85ac488feaa81b64b94ec38189dafac60b9';
const stale = { ...front, n: front.n - 1000, shell: OLDSHELL };
g = await run('五 镜像旧、GitHub 那一头新', thin({ n: front.n - 1000, shell: OLDSHELL }), { stalePtr: stale });
want(g && g.shell === front.shell && g.n === front.n, '从 GitHub 那一头拿到了新的外壳');
// 六、镜像旧、GitHub 那一头连不上：照卡里的开，不卡住
g = await run('六 镜像旧、GitHub 连不上', thin({ n: front.n - 1000, shell: OLDSHELL }), { stalePtr: stale, blockRaw: true });
want(g && g.shell === OLDSHELL && g.ms < 9000, '照卡里那一份开了，没有卡住');
// 七、卡里是第 5 代，镜像上的老地址还是第 5 代（缓存没过），GitHub 连不上；图床上已经有第 6、第 7 代的分支：顺着往后问，该拿到第 7 代
const g5 = { ...front, n: front.n - 1000, g: 5, shell: OLDSHELL };
g = await run('七 老地址旧、往后还有两代', thin({ n: front.n - 1000, g: 5, shell: OLDSHELL }), { stalePtr: g5, blockRaw: true, gens: { 6: { ...front, n: front.n - 500, g: 6, shell: OLDSHELL }, 7: { ...front, g: 7 } } });
want(g && g.shell === front.shell && g.n === front.n, '一代一代问到了最新的那一代');
// 八、卡里是第 5 代，往后没有新的一代：照卡里的开，不多等
g = await run('八 往后没有新的一代', thin({ n: front.n - 1000, g: 5, shell: OLDSHELL }), { stalePtr: g5, blockRaw: true, gens: {} });
want(g && g.shell === OLDSHELL && g.ms < 3000, '照卡里那一份开了，没有多等');
// 九、老地址和 GitHub 都取不到，只有往后一代的分支取得到：照样拿到
g = await run('九 只有新一代的分支取得到', thin({ n: front.n - 1000, g: 5, shell: OLDSHELL }), { blockPtr: false, stalePtr: null, blockRaw: true, gens: { 6: { ...front, g: 6 } } });
want(g && g.shell === front.shell, '光靠新一代的分支也拿到了');
console.log(bad ? '对不上的 ' + bad + ' 处' : '对不上的 0 处');
process.exit(bad ? 1 : 0);
