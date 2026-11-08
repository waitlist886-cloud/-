#!/bin/bash
# 纷争纪·炮的年月（约3600年）样张：bash build_strife_mid.sh <奥尔德兰.map> <输出.jpg> [倍数，默认1.6]
# 要先照 README 第1条起好无头 Chrome（调试端口 9333）。PY 指一个装了 PIL 的 Python（ComfyUI 那个就有）。
#   1. az_reset.sh 载图、关掉1001年的地名城镇国界路网
#   2. az_biwan.js：碧湾（今天赤盐内海那一整片水面加湾口），盐原在湾北边
#   3. az_salthai.js：1088年盐原塌下去，海从碧湾的湾口灌进来成了盐海，水一年一年染红，盐原北沿剩一溜老滩
#   4. az_siyu.js：南界以北照月银纪的南原画草（沙海浮塔的年月才有），以南是死域，落星洼是干的，往后双月海门那道河没水
#   5. az_seas_strife.js：镰刀湾（往后的镰月海）、潮门的湾、北辰湾、长船湾，三河在墙下水门汇流，进了死域就断了
#   6. az_strife.js：长垒（长垒_用户画.json，照 ../参考/长垒_用户画.tsv 转的）、墙后的段城和星纱轨、巨城、营城、七十二座高座、地名、题签
#   7. 截图以前再藏一回地形符号，分块截整张拼起来；盐海的新岸存成 盐海_纷争纪.path.txt（1001年那一张画赤盐内海用），七十二座高座的位置存成 高座_纷争纪.json（后段和山铜纪那几张接着用）
set -e
cd "$(dirname "$0")"
PY=${PY:-python}
MAP="$1"; OUT="$2"; SC="${3:-1.6}"
bash az_reset.sh "$MAP" >/dev/null
"$PY" -I embed.py az_biwan.js BAY_D 碧湾_月银纪.path.txt _az_biwan_run.js >/dev/null
"$PY" -I embed.py az_strife.js WALL_PTS 长垒_用户画.json _az_strife_run.js >/dev/null
node cdp.mjs file _az_biwan_run.js
node cdp.mjs file az_salthai.js
node cdp.mjs file az_siyu.js
node cdp.mjs file az_seas_strife.js
node cdp.mjs file _az_strife_run.js
node cdp.mjs eval "[(window.__hideBayIcons?__hideBayIcons():0),(window.__saltHideIcons?__saltHideIcons():0),(window.__siyuHideIcons?__siyuHideIcons():0),(window.__fseaHideIcons?__fseaHideIcons():0),(window.__stHideIcons?__stHideIcons():0)].join(',')"
"$PY" -I stitch.py "$OUT" "$SC" 2 2 88
node cdp.mjs eval "window.__saltD" > 盐海_纷争纪.path.txt
node cdp.mjs eval "JSON.stringify(window.__stSeats)" > 高座_纷争纪.json   # 七十二座高座的位置（往后几纪接着用）
rm -f _az_biwan_run.js _az_strife_run.js
