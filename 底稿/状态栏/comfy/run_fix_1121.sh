#!/usr/bin/env bash
# 11-21：第三批里没出成的两张艺术照（Codex 调用壳报错），和逐张查出来要重出的四位（布罗佳脸太嫩、莫嘎晒黑、法提赫头发和角箍、伊斯坎皮色），等接力和佩林重出跑完再补，出过的跳过
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
export CODEX_HOME="${CODEX_HOME:-C:/Users/waitl/.codex_b}"
busy() {
  powershell -NoProfile -Command "\$p = Get-CimInstance Win32_Process | Where-Object { (\$_.Name -like 'python*' -and (\$_.CommandLine -like '*gpt_sheet*' -or \$_.CommandLine -like '*gpt_cg3*')) -or (\$_.Name -like 'bash*' -and (\$_.CommandLine -like '*run_chain_1120*' -or \$_.CommandLine -like '*run_after_chain_1120*' -or \$_.CommandLine -like '*reserve_1118*')) }; if (\$p) { exit 0 } else { exit 1 }"
}
while busy; do sleep 60; done
CAST_SET=山铜纪 "$PY" -X utf8 gpt_sheet.py s2n_sorend s4n_seyfried s3n_brodja s4n_moga s1n_fatih s3n_iskan >> out/日志/1121_补两张.log 2>&1
tail -4 out/日志/1121_补两张.log
