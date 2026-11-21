#!/usr/bin/env bash
# 11-21 凌晨的接力（第二个号 ~/.codex_b）：等 run_1120.sh 那一队跑完 → 斐里安挪开重出（头一回画成了双眼眼镜，资料改成单片）
# → 11-18 那一批（run_reserve_1118.sh）→ 山铜纪八条新主线的节点原画（gpt_cg3.py scenes，出过的跳过）。撞了额度各步自己停。
#   CODEX_HOME=C:/Users/waitl/.codex_b bash 底稿/状态栏/comfy/run_chain_1120.sh
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
export CODEX_HOME="${CODEX_HOME:-C:/Users/waitl/.codex_b}"
busy() {
  powershell -NoProfile -Command "\$p = Get-CimInstance Win32_Process | Where-Object { (\$_.Name -like 'python*' -and \$_.CommandLine -like '*gpt_sheet*') -or (\$_.Name -like 'bash*' -and \$_.CommandLine -like '*run_1120.sh*') }; if (\$p) { exit 0 } else { exit 1 }"
}
while busy; do sleep 60; done
echo "== 山铜纪那一队跑完 $(date +%H:%M)"
if [ -d out/立绘_山铜纪/s1n_ferian ] && [ ! -d out/立绘_山铜纪_备选/s1n_ferian/双眼眼镜 ]; then
  mkdir -p out/立绘_山铜纪_备选/s1n_ferian && mv out/立绘_山铜纪/s1n_ferian out/立绘_山铜纪_备选/s1n_ferian/双眼眼镜
fi
CAST_SET=山铜纪 "$PY" -X utf8 gpt_sheet.py s1n_ferian >> out/日志/1120_斐里安重出.log 2>&1
echo "== 斐里安重出 $(date +%H:%M)：$(tail -1 out/日志/1120_斐里安重出.log | cut -c1-160)"
bash run_reserve_1118.sh >> out/日志/1120_接力_1118.log 2>&1
echo "== 11-18 那一批 $(date +%H:%M)：$(tail -2 out/日志/1120_接力_1118.log | tr '\n' ' ' | cut -c1-200)"
CG_WORKERS=2 "$PY" -X utf8 gpt_cg3.py scenes >> out/日志/1120_节点原画.log 2>&1
echo "== 节点原画 $(date +%H:%M)：$(tail -2 out/日志/1120_节点原画.log | tr '\n' ' ' | cut -c1-200)"
echo "接力跑完 $(date +%H:%M)"
