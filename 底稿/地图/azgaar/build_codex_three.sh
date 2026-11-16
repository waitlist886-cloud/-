#!/bin/bash
# 世界之书纷争纪、山铜纪、迷宫纪三卷的底图（11-15）：bash build_codex_three.sh <奥尔德兰.map> <AUL svg> <输出目录> [倍数，默认1.6] [只出哪几张，空格隔开]
#   strife_mid.jpg   纷争纪·炮的年月（约3600年），照 build_strife_mid.sh，地名和题签藏掉
#   strife_futa.jpg  纷争纪·浮塔的年月（约7000年），照 build_late.sh futa
#   bronze.jpg       山铜纪·麦的年月（约900年），照 build_late.sh bronze
#   maze1001.jpg     迷宫纪1001年的海与水路（大一档那一版），照 build_seas1001.sh
# 地名和城在页面上画成能点的点，所以底图上不带字（同 build_moon_codex.sh）。要先照 README 第1条起好无头 Chrome（端口 9333），PY 指一个装了 PIL 的 Python。
# 第二个参数是 ../参考/AUL_用户画.svg（只有 maze1001 那一张要）。不改 盐海_纷争纪.path.txt、高座_纷争纪.json。
set -e
cd "$(dirname "$0")"
PY=${PY:-python}
MAP="$1"; SVG="$2"; OUT="$3"; SC="${4:-1.6}"; ONLY="${5:-strife_mid strife_futa bronze maze1001}"
mkdir -p "$OUT"
HIDE_LAB="(function(){var n=0;for(const id of ['stLabels','stTitle','seaLabels','svLabels','svTitle']){const g=document.getElementById(id);if(g){g.style.display='none';n++}}return n})()"
ICONS="[(window.__hideBayIcons?__hideBayIcons():0),(window.__saltHideIcons?__saltHideIcons():0),(window.__siyuHideIcons?__siyuHideIcons():0),(window.__fseaHideIcons?__fseaHideIcons():0),(window.__stHideIcons?__stHideIcons():0),(window.__seaHideIcons?__seaHideIcons():0)].join(',')"
SL_LATE='[[476,1128],[520,1138],[570,1144],[620,1146],[662,1138],[702,1122],[742,1102],[792,1082],[832,1066],[866,1052],[890,1036],[910,1018],[928,1006],[944,998],[972,996],[1010,997],[1050,999],[1090,1004],[1130,1012],[1170,1023],[1210,1031],[1250,1036],[1290,1040],[1330,1041],[1370,1043],[1408,1050],[1432,1066]]'

shoot() {   # 等 Azgaar 把地形符号重画完，藏字、藏符号两遍，拼整张
  sleep 12
  node cdp.mjs eval "$HIDE_LAB" >/dev/null
  node cdp.mjs eval "$ICONS" >/dev/null; sleep 3; node cdp.mjs eval "$ICONS" >/dev/null
  "$PY" -I stitch.py "$OUT/$1.jpg" "$SC" 2 2 88
  echo "出了 $OUT/$1.jpg"
}

strife_like() {   # $1 名字，$2 叠哪一层（_cx_ov.js 已经塞好），$3 开头的开关
  bash az_reset.sh "$MAP" >/dev/null
  "$PY" -I embed.py az_biwan.js BAY_D 碧湾_月银纪.path.txt _cx_biwan.js >/dev/null
  node cdp.mjs file _cx_biwan.js >/dev/null
  [ -n "$3" ] && node cdp.mjs eval "$3" >/dev/null
  node cdp.mjs file az_salthai.js >/dev/null
  node cdp.mjs file az_siyu.js >/dev/null
  node cdp.mjs file az_seas_strife.js >/dev/null
  node cdp.mjs file "$2" >/dev/null
  shoot "$1"
}

for k in $ONLY; do
  case "$k" in
    strife_mid)
      "$PY" -I embed.py az_strife.js WALL_PTS 长垒_用户画.json _cx_ov.js >/dev/null
      strife_like strife_mid _cx_ov.js "";;
    strife_futa)
      "$PY" -I embed.py az_futa.js WALL_PTS 长垒_用户画.json _cx_ov1.js >/dev/null
      "$PY" -I embed.py _cx_ov1.js SEATS 高座_纷争纪.json _cx_ov.js >/dev/null
      strife_like strife_futa _cx_ov.js "window.__saltRedK=1.3;window.__siyuOpt={sand:true,lake:'dry'};window.__fseaOpt={river:'die'};'ok'";;
    bronze)
      "$PY" -I embed.py az_bronze.js WALL_PTS 长垒_用户画.json _cx_ov1.js >/dev/null
      "$PY" -I embed.py _cx_ov1.js SEATS 高座_纷争纪.json _cx_ov.js >/dev/null
      strife_like bronze _cx_ov.js "window.__saltRedK=1.6;window.__siyuOpt={sand:true,lake:'wet',SL:$SL_LATE};window.__fseaOpt={river:'lake',bay:'深蓝海湾'};window.__SL_LATE=$SL_LATE;'ok'";;
    maze1001)
      bash az_reset.sh "$MAP" >/dev/null
      if [ -f 盐海_纷争纪.path.txt ]; then "$PY" -I embed.py az_seas1001.js SALT_D 盐海_纷争纪.path.txt _cx_salt.js >/dev/null; else cp az_seas1001.js _cx_salt.js; fi
      "$PY" -I embed_aul.py "$SVG" _cx_salt.js _cx_ov.js >/dev/null
      node cdp.mjs file _cx_ov.js >/dev/null
      shoot maze1001;;
    *) echo "不认得 $k";;
  esac
done
rm -f _cx_biwan.js _cx_ov.js _cx_ov1.js _cx_salt.js
