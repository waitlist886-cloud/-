#!/usr/bin/env bash
# 11-22 新人查图以后的重出（底稿/立绘/新人查图_1122/重出单_*.tsv，89 位，单格 10 位）。接在长相重画后头跑。
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
export CODEX_HOME=C:/Users/waitl/.codex_b
while [ -n "$WAITPID" ] && kill -0 "$WAITPID" 2>/dev/null; do sleep 60; done
"$PY" -X utf8 ../../立绘/tools/redo_newcast.py run
