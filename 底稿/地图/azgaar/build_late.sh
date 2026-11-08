#!/bin/bash
# 纷争纪后段到山铜纪那一张底图（时代地图方向稿第四节第3张），两个年份的样张：
#   bash build_late.sh <.map> <输出.jpg> futa   [倍数]   纷争纪·浮塔的年月（约7000年）
#   bash build_late.sh <.map> <输出.jpg> bronze [倍数]   山铜纪·麦的年月（约900年）
# 要先照 README 第1条起好无头 Chrome（调试端口 9333）。PY 指一个装了 PIL 的 Python。
#   地貌那几步跟纷争纪中段一样（碧湾、盐海、死域、海与三河），换的是：盐海更红；死域里露出沙海（Azgaar 自己画的那一片沙漠）、北沿烧成玻璃平原；
#   山铜纪落星洼是一大片水（止戈以后一年比一年湿，到麦的年月望不到边），三河流进落星洼，墙南头那一截南界往南让一点（南沼在线北边），潮门的湾这一纪叫深蓝海湾。
#   高座照纷争纪中段那一张存的位置（高座_纷争纪.json，build_strife_mid.sh 存的）。
set -e
cd "$(dirname "$0")"
PY=${PY:-python}
MAP="$1"; OUT="$2"; ERA="$3"; SC="${4:-1.6}"
SL_LATE='[[476,1128],[520,1138],[570,1144],[620,1146],[662,1138],[702,1122],[742,1102],[792,1082],[832,1066],[866,1052],[890,1036],[910,1018],[928,1006],[944,998],[972,996],[1010,997],[1050,999],[1090,1004],[1130,1012],[1170,1023],[1210,1031],[1250,1036],[1290,1040],[1330,1041],[1370,1043],[1408,1050],[1432,1066]]'
case "$ERA" in
  futa)   OV=az_futa.js;   PRE="window.__saltRedK=1.3;window.__siyuOpt={sand:true,lake:'dry'};window.__fseaOpt={river:'die'};'ok'";;
  bronze) OV=az_bronze.js; PRE="window.__saltRedK=1.6;window.__siyuOpt={sand:true,lake:'wet',SL:$SL_LATE};window.__fseaOpt={river:'lake',bay:'深蓝海湾'};window.__SL_LATE=$SL_LATE;'ok'";;
  *) echo "年代写 futa 或 bronze"; exit 1;;
esac
bash az_reset.sh "$MAP" >/dev/null
"$PY" -I embed.py az_biwan.js BAY_D 碧湾_月银纪.path.txt _az_biwan_run.js >/dev/null
"$PY" -I embed.py "$OV" WALL_PTS 长垒_用户画.json _ov1.js >/dev/null
"$PY" -I embed.py _ov1.js SEATS 高座_纷争纪.json _ov_run.js >/dev/null
node cdp.mjs file _az_biwan_run.js
node cdp.mjs eval "$PRE"
node cdp.mjs file az_salthai.js
node cdp.mjs file az_siyu.js
node cdp.mjs file az_seas_strife.js
node cdp.mjs file _ov_run.js
node cdp.mjs eval "[(window.__hideBayIcons?__hideBayIcons():0),(window.__saltHideIcons?__saltHideIcons():0),(window.__siyuHideIcons?__siyuHideIcons():0),(window.__fseaHideIcons?__fseaHideIcons():0),(window.__stHideIcons?__stHideIcons():0)].join(',')"
"$PY" -I stitch.py "$OUT" "$SC" 2 2 88
rm -f _az_biwan_run.js _ov1.js _ov_run.js
