#!/bin/bash
# 世界之书月银纪卷的两张底图（11-15）：bash build_moon_codex.sh <奥尔德兰.map> <输出目录> [倍数，默认1.6]
#   moon_base.jpg：月银纪的地形（碧湾和盐原、南原、那时候已有的海、三河），不画城，不写地名。天亮以前、天亮以后两个年代共用。
#   moon_salvis.jpg：再叠 az_salvis.js 的萨尔维斯末年（城的平面、上城、客星城、辉塔、七曜、空路），地名和题签藏掉。
# 地名和城在页面上画成能点的点，所以底图上不带字。要先照 README 第1条起好无头 Chrome（端口 9333），PY 指一个装了 PIL 的 Python。
set -e
cd "$(dirname "$0")"
PY=${PY:-python}
MAP="$1"; OUT="$2"; SC="${3:-1.6}"
mkdir -p "$OUT"
bash az_reset.sh "$MAP" >/dev/null
"$PY" -I embed.py az_biwan.js BAY_D 碧湾_月银纪.path.txt _az_biwan_run.js >/dev/null
node cdp.mjs file _az_biwan_run.js
node cdp.mjs file az_nanyuan.js
node cdp.mjs file az_seas_moon.js
# Azgaar 刚叠完几层会把地形符号整层重画一回，等它画完再藏，藏两遍（不等的话南原那一片露出原来的沙丘符号）
sleep 12
HIDE="(window.__hideBayIcons?window.__hideBayIcons():0)+','+(window.__hideMoonIcons?window.__hideMoonIcons():0)+','+(window.__mseaHideIcons?window.__mseaHideIcons():0)"
node cdp.mjs eval "$HIDE"; sleep 3; node cdp.mjs eval "$HIDE"
"$PY" -I stitch.py "$OUT/moon_base.jpg" "$SC" 2 2 88
node cdp.mjs file az_salvis.js
node cdp.mjs eval "(function(){var g=document.getElementById('svLabels');if(g)g.style.display='none';return (window.__hideBayIcons?window.__hideBayIcons():0)+','+(window.__svHideIcons?window.__svHideIcons():0)+','+(window.__hideMoonIcons?window.__hideMoonIcons():0)+','+(window.__mseaHideIcons?window.__mseaHideIcons():0)})()"
"$PY" -I stitch.py "$OUT/moon_salvis.jpg" "$SC" 2 2 88
rm -f _az_biwan_run.js
