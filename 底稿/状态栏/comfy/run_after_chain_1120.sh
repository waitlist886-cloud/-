#!/usr/bin/env bash
# 接力（run_chain_1120.sh）跑完以后，佩林挪开重出（头一回设定图灰发、艺术照棕发，资料改成铜锈红发、炉火橙眼）。
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
export CODEX_HOME="${CODEX_HOME:-C:/Users/waitl/.codex_b}"
while powershell -NoProfile -Command "if (Get-CimInstance Win32_Process | Where-Object { \$_.Name -like 'bash*' -and \$_.CommandLine -like '*run_chain_1120*' }) { exit 0 } else { exit 1 }"; do sleep 60; done
if [ -d out/立绘_山铜纪/s1n_perrin ] && [ ! -d out/立绘_山铜纪_备选/s1n_perrin/灰发 ]; then
  mkdir -p out/立绘_山铜纪_备选/s1n_perrin && mv out/立绘_山铜纪/s1n_perrin out/立绘_山铜纪_备选/s1n_perrin/灰发
fi
CAST_SET=山铜纪 "$PY" -X utf8 gpt_sheet.py s1n_perrin >> out/日志/1120_佩林重出.log 2>&1
echo "佩林重出 $(date +%H:%M)：$(tail -1 out/日志/1120_佩林重出.log | cut -c1-160)"
