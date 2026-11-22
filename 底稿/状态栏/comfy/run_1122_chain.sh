#!/usr/bin/env bash
# 11-22 新人队列跑完以后串着跑：长相重画（28 版加桑托）→ 新人队列失败的三位补缺 → 战装二回 11 格。
# 原来两支各自等“空闲”，判断把自己的父进程也算进去，一直等着，所以改成一条串起来（NOWAIT=1 跳过等待）。
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
export CODEX_HOME=C:/Users/waitl/.codex_b NOWAIT=1
bash run_1122_look.sh > out/日志/1122_look_queue.log 2>&1
tail -2 out/日志/1122_look_queue.log
{
  echo "== 补缺 $(date +%H:%M)"
  CAST_SET=前传 "$PY" -X utf8 gpt_sheet.py q5x_bjorg
  CAST_SET=山铜纪 "$PY" -X utf8 gpt_sheet.py s5x_zahir
  CAST_SET=月银纪史诗 "$PY" -X utf8 gpt_sheet.py ge1x_dian
  echo "补缺跑完 $(date +%H:%M)"
} > out/日志/1122_fill.log 2>&1
tail -2 out/日志/1122_fill.log
bash ../../立绘/战装_11-22/分档/重画/run_二回.sh > out/日志/1122_war_redo.log 2>&1
tail -2 out/日志/1122_war_redo.log
