#!/usr/bin/env bash
# 11-22 战装查图判重画的 11 格（纷争纪 8、前传 3），句子改过以后再出一回。等别的出图队列空了再跑。
cd "$(dirname "$0")/../../../../状态栏/comfy"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
T="$(cd "$(dirname "$0")" && pwd)"
export CODEX_HOME=C:/Users/waitl/.codex_b FIX_WORK=战装_1122 CAST_WORKERS=2
busy() { powershell -NoProfile -Command "\$p = Get-CimInstance Win32_Process | Where-Object { (\$_.Name -like 'python*' -and (\$_.CommandLine -like '*gpt_sheet*' -or \$_.CommandLine -like '*fix_cell*')) -or (\$_.Name -like 'bash*' -and (\$_.CommandLine -like '*run_1122_new*' -or \$_.CommandLine -like '*run_1122_look*')) }; if (\$p) { exit 0 } else { exit 1 }"; }
while busy; do sleep 60; done
for s in 纷争纪 前传; do
  CAST_SET=$s "$PY" -X utf8 fix_cell.py run "$T/${s}_二回.json"
  CAST_SET=$s "$PY" -X utf8 fix_cell.py sheet "out/战装_1122/对照_${s}_二回.jpg" "$T/${s}_二回.json"
done
echo "二回跑完 $(date +%H:%M)"
