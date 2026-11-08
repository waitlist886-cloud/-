#!/bin/bash
# 月银纪·萨尔维斯末年样张：bash build_moon_salvis.sh <奥尔德兰.map> <输出.jpg> [倍数，默认1.6]
# 要先照 README 第1条起好无头 Chrome（调试端口 9333）。PY 指一个装了 PIL 的 Python（ComfyUI 那个就有）。
#   1. az_reset.sh 载图、关掉1001年的地名城镇国界路网
#   2. az_biwan.js：今天赤盐内海那一整片水面是碧湾，朝西南出海，湾北边是盐原和盐沼
#   3. az_nanyuan.js：神陨沙海那一片和双月内海都还没有，是南原的草原，南边沿海留一溜沙
#   3b. az_seas_moon.js：那时候已经有的海（镰月海、珠湾、北辰湾、长船湾），三河在神渡城当中汇流往南入海
#   4. az_salvis.js：萨尔维斯末年的城、上城、客星城、星坑盆地、辉塔、七曜、空路、地名、题签
#   5. 截图以前再藏一回地形符号（Azgaar 有时整层重画），分块截整张拼起来
set -e
cd "$(dirname "$0")"
PY=${PY:-python}
MAP="$1"; OUT="$2"; SC="${3:-1.6}"
bash az_reset.sh "$MAP" >/dev/null
"$PY" -I embed.py az_biwan.js BAY_D 碧湾_月银纪.path.txt _az_biwan_run.js >/dev/null
node cdp.mjs file _az_biwan_run.js
node cdp.mjs file az_nanyuan.js
node cdp.mjs file az_seas_moon.js
node cdp.mjs file az_salvis.js
node cdp.mjs eval "(window.__hideBayIcons?window.__hideBayIcons():0)+','+(window.__svHideIcons?window.__svHideIcons():0)+','+(window.__hideMoonIcons?window.__hideMoonIcons():0)+','+(window.__mseaHideIcons?window.__mseaHideIcons():0)"
"$PY" -I stitch.py "$OUT" "$SC" 2 2 88
rm -f _az_biwan_run.js
