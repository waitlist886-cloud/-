# 照 az_strife.js（纷争纪中段）改出 az_futa.js（纷争纪·浮塔的年月，约7000年）。用法：python -I make_futa.py（az_strife.js 改了以后重跑一回）
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
s = open('az_strife.js', encoding='utf8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:90], s.count(a))
    s = s.replace(a, b)


def cut(a, b, new):
    global s
    i = s.index(a)
    j = s.index(b, i) + len(b)
    s = s[:i] + new + s[j:]


# 头注
i = s.index('(async () => {')
s = """// 纷争纪·浮塔的年月（约7000年）样张：照 az_strife.js（纷争纪中段）改的，build_late.sh futa 接着跑。
//   补卷_19 地图的几层：约5300年起浮空塔一座接一座升上死域的天，几十座排一列，塔底托的浮岩是从曜冠山南边的浮石峡谷里拽下来的，峡谷口起了锚石镇；
//   死域里烂得最深的几片化成了沙，连成沙海，北沿叫神焰烧成一片一片的玻璃平原（az_siyu.js 的 sand 那一支），7500年以后塔才一座一座往下落；
//   5945、5951、5958 白鸢、金穗、湖星把冠交给金鸢城，星湖边的城一年里走空；5959 湖心岛上立起观星的塔，月镜立国；5960 花谷里立了蔷薇；
//   西边的宴城、钟城、熔原上的营城这几千年里长大。高座照纷争纪中段那一张的位置（高座_纷争纪.json，跑以前用 embed.py 塞进 SEATS），约7000年取四十二尊在（★）。
""" + s[i:]

# 城：三国的王城交了冠，星湖城空了，月镜立在湖心岛上
cut("  // 墙东：金鸢城几百万人", "    ['yinfan', 2069.8, 747.3, 7, 'tide', 2], ['cuiguan', 2068, 308, 8, 'elf', 2],\n  ];\n",
    """  // 墙东：金鸢城、星冠圣城、炉城三座巨城，白鸢骑士城、金穗王仓城（冠都交给了金鸢城），白冠城是学城
  const EAST = [
    ['jinyuan', 1518, 742, 24, 'gold', 3], ['xingguan', 1386, 560, 15, 'holy', 2], ['luxin', 1562, 1106, 14, 'forge', 2],
    ['baiguan', 1186, 756, 9, 'holy', 2], ['baiyuan', 1408, 868, 8, 'imperial', 2], ['jinsui', 1606, 854, 8.5, 'gold', 2],
    ['yinfan', 2069.8, 747.3, 7.5, 'tide', 2], ['cuiguan', 2068, 308, 8, 'elf', 2],
  ];
""")
cut("  for (const m of EAST) { if (m[0] === 'xinghu') continue; cityPlan(...m); }", "stroke-width': 0.4, opacity: 0.95 }, free); }\n",
    """  for (const m of EAST) cityPlan(...m);
  // 星湖城：5958年秋冠送去金鸢城，城一年里走空，连城名也没有留下，北岸一片泡在水里的废墟；月镜：5959年湖心岛上立起头一座观星的塔，约6100年东岸书堡的丘陵上立第二座
  { const free = mk('g', { id: 'stXinghu' }, null); vb.insertBefore(free, document.getElementById('rivers')); free.appendChild(ruin(1952, 436, 9, '#5d6878'));
    const tower = (x, y, h) => { mk('circle', { cx: x, cy: y - h, r: 6, fill: 'url(#stSilver)' }, free); mk('path', { d: `M${x - 1.5},${y} L${x - 0.7},${y - h} L${x + 0.7},${y - h} L${x + 1.5},${y} Z`, fill: '#f4f1ea', stroke: '#3c3a44', 'stroke-width': 0.35, filter: 'url(#stShadow)' }, free); mk('circle', { cx: x, cy: y - h - 0.6, r: 1.1, fill: '#eaf2ff', stroke: '#5d6878', 'stroke-width': 0.3 }, free); window.__stHide.push([x, y, 4]); };
    tower(1952, 452, 9); tower(1972, 548, 7); }
""")
# 墙西的营城这几千年里长大
rep("    ['yancheng', 682, 435.4, 9, 'rose', 2], ['zhongcheng', 374, 658, 9, 'bone', 2], ['rongyuan', 528, 980, 9, 'ember', 2], ['huiying', 902, 686, 8, 'camp', 2],\n    ['wuhu', 497, 302, 8, 'mirror', 2], ['chaomen', 198, 868, 7.5, 'abyss', 2], ['shankou', 858, 462, 6, 'camp', 2], ['duanying', 616, 1134, 6, 'ember', 2],",
    "    ['yancheng', 682, 435.4, 10.5, 'rose', 2], ['zhongcheng', 374, 658, 10.5, 'bone', 2], ['rongyuan', 528, 980, 10.5, 'ember', 2], ['huiying', 902, 686, 9, 'camp', 2],\n    ['wuhu', 497, 302, 8.5, 'mirror', 2], ['chaomen', 198, 868, 8.5, 'abyss', 2], ['shankou', 858, 462, 6.5, 'camp', 2], ['duanying', 616, 1134, 7, 'ember', 2],")
rep("[1122, 868, 'imperial'], [1276, 938, 'imperial'], [1386, 224, 'silver'], [1080, 525, 'silver']];",
    "[1122, 868, 'imperial'], [1276, 938, 'imperial'], [1386, 224, 'silver'], [1080, 525, 'silver'], [1352, 370, 'imperial'], [814, 1078, 'gold'], [1851.5, 585.8, 'elf']];")

# 高座：照纷争纪中段那一张的位置
cut("  // 落在水里或者死域里的往近处的干地上挪", "  log.push('高座 ' + seatAt.length + '（空 ' + Math.min(DEAD, all.length) + '）');",
    """  // 高座照纷争纪中段那一张的位置：那时候空着的十六座照旧空，再空十四座（炮的年月末五十尊、浮塔的年月末三十五尊，约7000年取四十二尊在，★），有名的那十三座照旧亮着
  const SEATS = JSON.parse('SEATS');
  const deadIdx = new Set(SEATS.map((q, i) => (q[2] ? -1 : i)).filter((i) => i >= 0));
  { let extra = 0; for (let i = SEATS.length - 1; i >= 13 && extra < 14; i--) if (!deadIdx.has(i)) { deadIdx.add(i); extra++; } }
  SEATS.forEach(([x, y, lit, big], i) => seat(x, y, !deadIdx.has(i), big));
  log.push('高座 ' + SEATS.length + '（空 ' + deadIdx.size + '）');""")

# 浮空塔、锚石镇、骨脊、蔷薇篱：插在长垒前头
rep("  // ---- 长垒：一段墙从一座雪山连到下一座雪山，夜里泛白光；墙后的段城一座挨一座 ----",
    """  // ---- 浮空塔：几十座排一列浮在死域的天上，塔底托着浮岩，影子落在死域上 ----
  { const tg = mk('g', { id: 'stTowers' }, null); vb.insertBefore(tg, document.getElementById('labels'));
    const line = [[812, 1118], [870, 1092], [940, 1076], [1010, 1068], [1080, 1070], [1150, 1080], [1220, 1090], [1290, 1096], [1362, 1102]];
    const lp = mk('path', { d: smooth(line), fill: 'none' }, tg); const L = lp.getTotalLength(); const pts = []; for (let d = 6; d < L; d += 16.5) { const p = lp.getPointAtLength(d); pts.push([p.x, p.y]); } lp.remove();
    mk('path', { d: smooth(line.map(([x, y]) => [x + 9, y + 15])), fill: 'none', stroke: '#2b2626', 'stroke-width': 1.2, opacity: 0.12, 'stroke-dasharray': '3 3' }, tg);
    pts.forEach(([x, y], k) => { const big = k % 6 === 2 ? 1.35 : 1; mk('ellipse', { cx: x + 9, cy: y + 15, rx: 4.6 * big, ry: 1.8 * big, fill: '#2b2626', opacity: 0.22, filter: 'url(#stBlur)' }, tg); });
    pts.forEach(([x, y], k) => { const big = k % 6 === 2 ? 1.35 : 1; const w = 4.4 * big, h = 6.5 * big;
      mk('circle', { cx: x, cy: y - h * 0.9, r: 5 * big, fill: 'url(#stAmber)', opacity: 0.45 }, tg);
      mk('path', { d: `M${x - w},${y} Q${x - w * 0.7},${y + h * 0.55} ${x},${y + h} Q${x + w * 0.7},${y + h * 0.55} ${x + w},${y} Z`, fill: '#8a7e70', stroke: '#3f3830', 'stroke-width': 0.4, filter: 'url(#stShadow)' }, tg);
      mk('ellipse', { cx: x, cy: y, rx: w, ry: w * 0.32, fill: '#b9ad99', stroke: '#3f3830', 'stroke-width': 0.35 }, tg);
      mk('path', { d: `M${x - 1.3 * big},${y} L${x - 0.6 * big},${y - h} L${x + 0.6 * big},${y - h} L${x + 1.3 * big},${y} Z`, fill: '#f1ece2', stroke: '#3c3a44', 'stroke-width': 0.3 }, tg);
      mk('circle', { cx: x, cy: y - h - 0.5, r: 0.8 * big, fill: '#ffe6a3' }, tg); });
    window.__stTowerN = pts.length; }
  // 浮石峡谷：石头一年比一年浮得多，峡谷口的锚石镇最旺的那些年，一年拽下来的石头抵得上一座山
  { const rg2 = mk('g', {}, null); vb.insertBefore(rg2, document.getElementById('labels')); for (const [dx, dy, r] of [[-14, -6, 2.6], [-6, -12, 1.8], [4, -9, 3.2], [12, -14, 1.6], [-10, 4, 1.4], [16, -4, 2.2]]) { const x = 1340 + dx, y = 362 + dy; mk('ellipse', { cx: x + 2.5, cy: y + 5, rx: r, ry: r * 0.4, fill: '#2b2626', opacity: 0.2 }, rg2); mk('path', { d: `M${x - r},${y} Q${x},${y + r * 1.4} ${x + r},${y} Q${x},${y - r * 0.5} ${x - r},${y} Z`, fill: '#a99c88', stroke: '#4a4038', 'stroke-width': 0.3 }, rg2); } }
  // 骨脊：落星洼里最长的那一道，浮塔的年月起塔上管它叫骨脊
  { const bg = mk('g', {}, null); vb.insertBefore(bg, document.getElementById('labels')); const sp = [[1298, 1140], [1320, 1133], [1343, 1126], [1366, 1119], [1388, 1112]]; mk('path', { d: smooth(sp), fill: 'none', stroke: '#f6f1e6', 'stroke-width': 1.6, 'stroke-linecap': 'round' }, bg); mk('path', { d: smooth(sp), fill: 'none', stroke: '#6b5f50', 'stroke-width': 0.3 }, bg); for (let k = 0; k < 14; k++) { const t = k / 13, x = 1298 + 90 * t, y = 1140 - 28 * t; mk('path', { d: `M${x},${y} q1.6,-3.2 0.4,-5 M${x},${y} q-1.2,3.4 0.4,5`, fill: 'none', stroke: '#f6f1e6', 'stroke-width': 0.6, 'stroke-linecap': 'round' }, bg); } }
  // 蔷薇篱：6010年以后在花谷谷口外种的一圈
  { const hg = mk('g', {}, null); vb.insertBefore(hg, document.getElementById('labels')); for (let k = 0; k <= 16; k++) { const a = Math.PI * (0.15 + 0.7 * k / 16); const x = 1792 + Math.cos(a) * 46, y = 1082 + Math.sin(a) * 24; mk('circle', { cx: x, cy: y, r: 1.3, fill: '#c2557a', stroke: '#4f6b3a', 'stroke-width': 0.5 }, hg); } }

  // ---- 长垒：一段墙从一座雪山连到下一座雪山，夜里泛白光；墙后的段城一座挨一座 ----""")

# 地名
rep("for (const [s, x, y] of [['白鸢王国', 1408, 900], ['金穗王国', 1610, 890], ['湖星王国', 1900, 412], ['公国岭', 1700, 742]]) region(s, x, y, 9.5, { 'font-weight': 700, fill: '#6b5532', opacity: 0.75 });",
    "for (const [s, x, y] of [['月镜', 1992, 476], ['蔷薇', 1830, 1012], ['公国岭', 1700, 742]]) region(s, x, y, 9.5, { 'font-weight': 700, fill: '#6b5532', opacity: 0.75 });")
rep("  T1('死 域', 1150, 1170, 26, { 'font-weight': 900, fill: '#3e3a37', stroke: '#e8e3da', 'stroke-width': 2.4, 'letter-spacing': 18, opacity: 0.72 });",
    "  T1('死 域', 880, 1140, 22, { 'font-weight': 900, fill: '#3e3a37', stroke: '#e8e3da', 'stroke-width': 2.2, 'letter-spacing': 14, opacity: 0.72 });\n"
    "  T1('沙 海', 1080, 1200, 22, { 'font-weight': 900, fill: '#6b5532', stroke: '#f3ead6', 'stroke-width': 2.2, 'letter-spacing': 14, opacity: 0.7 });\n"
    "  region('玻璃平原', 1000, 1046, 8, { fill: '#4f6670' });")
rep("  region('落星洼', 1330, 1112, 10, { fill: '#5b4f43' });", "  region('落星洼', 1330, 1112, 10, { fill: '#5b4f43' });\n  T1('骨脊', 1343, 1146, 6.5, { 'font-weight': 700, fill: '#5b4f43', 'stroke-width': 1.2 });")
rep("['星湖城', 1952, 412, 0, 8.5], ['白鸢王城', 1408, 868, 8.5, 7.5], ['金穗的仓', 1606, 854, 8.5, 7.5]",
    "['白鸢骑士城', 1408, 868, 8, 7.5], ['金穗王仓城', 1606, 854, 8.5, 7.5]")
rep("['宴城', 682, 435.4, 9, 8.5], ['钟城', 374, 658, 9, 8.5], ['熔原', 528, 980, 9, 8.5], ['灰营', 902, 686, 8, 8], ['雾湖', 497, 302, 8, 8], ['潮门港', 198, 868, 7.5, 8], ['山口里的营', 858, 462, 6, 7], ['锻营', 616, 1134, 6, 7.5]",
    "['宴城', 682, 435.4, 10.5, 8.5], ['钟城', 374, 658, 10.5, 8.5], ['熔原', 528, 980, 10.5, 8.5], ['灰营', 902, 686, 9, 8], ['雾湖', 497, 302, 8.5, 8], ['潮门港', 198, 868, 8.5, 8], ['山口里的营', 858, 462, 6.5, 7], ['锻营', 616, 1134, 7, 7.5]")
rep("['天脊北路的最后一站', 1386, 236]]) T1(", "['天脊北路的最后一站', 1386, 236], ['锚石镇', 1366, 382], ['沙海西路的驿', 814, 1090], ['林隙', 1851, 598], ['星湖城的废墟', 1952, 452]]) T1(")
rep("['北辰塔', 380, 214, 7.5]", "['北辰塔', 380, 214, 7.5], ['夜翼的峭壁', 336, 232, 6.5], ['浮空塔的塔线', 1086, 1046, 7], ['月镜的塔', 1952, 418, 6.5], ['浮石峡谷', 1300, 352, 6.5]")
rep("t2.textContent = '炮的年月 · 约三千六百年 · 墙后的星纱轨刚通车';", "t2.textContent = '浮塔的年月 · 约七千年 · 浮空塔几十座排一列浮在死域的天上';")
rep("t3.textContent = '白线是长垒，紫线是星纱轨，黑台是高座（亮着的有主，灰的空了）';", "t3.textContent = '白线是长垒，紫线是星纱轨，黑台是高座（亮着的有主，灰的空了），沙海北沿是玻璃平原';")
open('az_futa.js', 'w', encoding='utf8').write(s)
print('ok', len(s))
