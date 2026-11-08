// 行囊、命星簿、同行三页在手机宽上量一遍（11-08，风月真页面截图上查出来的三样）：
// 行囊一排一排之间有没有被看不见的卡撑开；命星簿点一枚以后右页那张卡看不看得见；同行的头像那一排能不能横着滑、选了谁底下那一块跟不跟着走。
// static_bench_fy.mjs（或 static_bench.mjs）的 eval= 用，样本要有 §物品、§能力 和几个 §角色。
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const last = (s) => { const a = document.querySelectorAll(s); return a[a.length - 1]; };
  const R = (e) => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; };
  const cs = (e) => getComputedStyle(e);
  const out = [];
  const tab = async (t) => { const l = last('.sz-tab.' + t); if (!l) return false; l.click(); await sleep(500); return true; };

  // 一、行囊
  if (await tab('t-bag')) {
    const g = last('.p-bag .sz-gridit');
    const cells = [...g.querySelectorAll('.sz-cell')];
    const tops = [...new Set(cells.map((c) => Math.round(c.querySelector('.sz-face').getBoundingClientRect().top)))].sort((a, b) => a - b);
    const gaps = tops.slice(1).map((t, i) => t - tops[i]);
    const tips = cells.map((c) => c.querySelector('.sz-tip')).filter(Boolean);
    const shown = tips.filter((t) => cs(t).display !== 'none');
    const face = cells[0] && cells[0].querySelector('.sz-face');
    out.push('行囊 ' + cells.length + ' 件，排了 ' + tops.length + ' 行，行距 ' + gaps.join('/') + ' | 卡占位的 ' + shown.length + ' 张（没点时应当 0）| 头一格外框 ' + (face ? R(face).join(',') + ' 圆角 ' + cs(face).borderRadius + ' 虚线圈 ' + cs(face, '::before').content : ''));
    if (cells[1]) {
      cells[1].querySelector('.sz-face').click(); await sleep(400);
      const t = cells[1].querySelector('.sz-tip');
      out.push('  点第二件：卡 display ' + cs(t).display + ' opacity ' + cs(t).opacity + ' visibility ' + cs(t).visibility + ' 位置 ' + R(t).join(','));
    }
  }
  // 二、命星簿（伟业页的技能书）
  if (await tab('t-deed')) {
    const abs = [...document.querySelectorAll('.p-deed .sz-ab')].filter((e) => e.closest('.p-deed') === last('.p-deed'));
    const vis = abs.filter((e) => cs(e).display !== 'none');
    const f = vis[0] && vis[0].querySelector('.sz-face');
    out.push('命星簿 ' + abs.length + ' 枚，这一类露 ' + vis.length + ' 枚 | 头一枚外框 ' + (f ? R(f).join(',') + ' 圆角 ' + cs(f).borderRadius + ' 虚线圈 ' + cs(f, '::before').content : '无'));
    if (f) {
      f.click(); await sleep(400);
      const t = vis[0].querySelector('.sz-tip');
      out.push('  点头一枚：卡 display ' + cs(t).display + ' opacity ' + cs(t).opacity + ' visibility ' + cs(t).visibility + ' 位置 ' + R(t).join(',') + ' 字 ' + (t.innerText || '').slice(0, 24).split('\n').join(' '));
    }
  }
  // 三、同行
  if (await tab('t-party')) {
    const n = last('.p-party .sz-npcs');
    const avs = [...n.querySelectorAll('.sz-av')];
    const nr = n.getBoundingClientRect();
    const inView = avs.filter((a) => { const r = a.getBoundingClientRect(); return r.left >= nr.left - 1 && r.right <= nr.right + 1; }).length;
    out.push('同行 ' + avs.length + ' 人，一眼看得见 ' + inView + ' 人 | 那一排 overflow-x ' + cs(n).overflowX + ' 可滑 ' + (n.scrollWidth - n.clientWidth) + ' | 头像排成 ' + new Set(avs.map((a) => Math.round(a.getBoundingClientRect().top))).size + ' 行');
    const pick = avs[avs.length - 1];
    n.scrollLeft = n.scrollWidth; await sleep(300);
    pick.click(); await sleep(500);
    const body = [...n.querySelectorAll('.sz-npc-b')].find((b) => cs(b).display !== 'none');
    out.push('  滑到最右、点最后一个：选中 ' + (pick.innerText || '').trim() + ' | 档案那一块 ' + (body ? R(body).join(',') + '（框 ' + Math.round(nr.left) + '~' + Math.round(nr.right) + '）' : '没出来'));
  }
  return out.join('\n');
})();
