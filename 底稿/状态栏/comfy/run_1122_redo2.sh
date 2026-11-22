#!/usr/bin/env bash
# 11-22 新人重出查图以后的第二回（重出单_二回_*.tsv，旧图挪 <纪>_备选/<键>/查图二回前_1122/，单格在 out/新人二回_1122/），
# 再补琉妲正装一格（out/长相三回_1122/）。等倾向重画（WAITPID）跑完再起。
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
export CODEX_HOME=C:/Users/waitl/.codex_b
while [ -n "$WAITPID" ] && kill -0 "$WAITPID" 2>/dev/null; do sleep 60; done
REDO_LIST='重出单_二回_*.tsv' REDO_BAK=查图二回前_1122 REDO_WORK=新人二回_1122 "$PY" -X utf8 ../../立绘/tools/redo_newcast.py run
CAST_SET=山铜纪 FIX_WORK=长相三回_1122 "$PY" -X utf8 fix_cell.py run out/长相核对_1122/单格_三回.json
CAST_SET=山铜纪 FIX_WORK=长相三回_1122 "$PY" -X utf8 fix_cell.py sheet out/长相三回_1122/对照_琉妲.jpg out/长相核对_1122/单格_三回.json
echo "二回跑完 $(date +%H:%M)"
