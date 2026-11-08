#!/bin/bash
# 1001年海与水路试样：bash build_seas1001.sh <奥尔德兰.map> <.map 存出来的 svg> <输出.jpg> [倍数，默认1.6]
# 要先照 README 第1条起好无头 Chrome（调试端口 9333）。PY 指一个装了 PIL 的 Python（ComfyUI 那个就有）。
#   盐海_纷争纪.path.txt（build_strife_mid.sh 存的）在就塞进 SALT_D：赤盐内海连上纷争纪1088年塌下去的那一片盐原
#   embed_aul.py 把用户在 .map 里画的 AUL 那一层（长垒、阿卡迪亚两道圈）从存出来的 svg 里抠出来塞进去
set -e
cd "$(dirname "$0")"
PY=${PY:-python}
MAP="$1"; SVG="$2"; OUT="$3"; SC="${4:-1.6}"
bash az_reset.sh "$MAP" >/dev/null
if [ -f 盐海_纷争纪.path.txt ]; then "$PY" -I embed.py az_seas1001.js SALT_D 盐海_纷争纪.path.txt _seas_salt.js >/dev/null; else cp az_seas1001.js _seas_salt.js; fi
"$PY" -I embed_aul.py "$SVG" _seas_salt.js _seas_run.js >/dev/null
node cdp.mjs file _seas_run.js
node cdp.mjs eval "window.__seaHideIcons ? __seaHideIcons() : 0"
"$PY" -I stitch.py "$OUT" "$SC" 2 2 88
rm -f _seas_salt.js _seas_run.js
