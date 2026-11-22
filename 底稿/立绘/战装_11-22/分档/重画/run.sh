#!/usr/bin/env bash
# 11-22 五纪战装分档以后重画战斗格（fix_cell 只换战斗那一格，脸对齐还原）。工作目录 out/战装_1122/<纪>/，查过再 apply（旧格挪 备选/<键>/战装前_1122/）。
cd "$(dirname "$0")/../../../../状态栏/comfy"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
T="$(cd "$(dirname "$0")" && pwd)"
export CODEX_HOME=C:/Users/waitl/.codex_b FIX_WORK=战装_1122 CAST_WORKERS=3
for s in 纷争纪 萨尔维斯 诸国期 月银纪史诗 前传; do
  echo "== $s $(date +%H:%M)"
  CAST_SET=$s "$PY" -X utf8 fix_cell.py run "$T/$s.json"
  CAST_SET=$s "$PY" -X utf8 fix_cell.py sheet "out/战装_1122/对照_$s.jpg" "$T/$s.json"
done
echo "全跑完 $(date +%H:%M)"
