#!/usr/bin/env bash
# 11-20 夜山铜纪立绘铺开的出图队列（资料在 cast/山铜纪/s1n 到 s6n，底稿/立绘/tools/take_cast.py 收的稿）。
#   bash 底稿/状态栏/comfy/run_1120.sh <键单文件>      键单一行一批：门洞那一院、新旅伴、其余
# 先等 11-18 那一条队列（run_reserve_1118.sh）跑完，同一时间只跑一条队列。撞了额度就停，等重置以后再跑一遍，只补缺的。
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
Q="${1:?要键单文件}"
mkdir -p out/日志
busy() {   # 还有别的出图在跑：python 跑着 gpt_sheet，或者 bash 跑着 11-18 那一条（powershell 自己的命令行不算）
  powershell -NoProfile -Command "\$p = Get-CimInstance Win32_Process | Where-Object { (\$_.Name -like 'python*' -and \$_.CommandLine -like '*gpt_sheet*') -or (\$_.Name -like 'bash*' -and \$_.CommandLine -like '*reserve_1118*') }; if (\$p) { exit 0 } else { exit 1 }"
}
while busy; do
  sleep 60
done
n=0
while IFS= read -r line; do
  n=$((n+1))
  [ -z "$line" ] && continue
  echo "== 第 $n 批 $(date +%H:%M)：$line"
  CAST_SET=山铜纪 "$PY" -X utf8 gpt_sheet.py $line >> "out/日志/1120_批$n.log" 2>&1
  echo "   退出码 $?，末尾：$(tail -2 "out/日志/1120_批$n.log" | tr '\n' ' ' | cut -c1-200)"
done < "$Q"
echo "队列跑完 $(date +%H:%M)"
