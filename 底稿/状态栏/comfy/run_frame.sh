#!/bin/bash
# 重拼四方，跑真样式出预览。run_frame.sh [right left top bottom]；后面的宽高写在 SIZES 环境变量里
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
B="E:/aldran_art/底稿/状态栏"
ROOT="$B/comfy/out/四方_11-03"
cd "$B/comfy" && "$PY" -I -X utf8 maze1001_frame.py "$@" || exit 1
cd "$B/大框" && "$PY" -I -X utf8 make_css_frame.py frame.css > /dev/null
cd "E:/aldran_art/tools/rili_bench"
for size in ${SIZES:-1536x1024}; do
  w=${size%x*}; h=${size#*x}
  node static_bench.mjs "$B/紧凑/样本_迷宫纪1001_紧凑.txt,$B/手札/样本_迷宫纪1001_构想.txt" "$ROOT/preview_$w.png" w=$w h=$h extracss="$B/大框/frame.css" extrarules="$B/大框/rules_frame.json" art="$ROOT/art"
done
