#!/usr/bin/env bash
# 11-25 迷宫纪那一本主线节点原画的出图队列（gpt_cg5.py --queue）。用 ~/.codex_b 那个号，并两张。
#   bash 底稿/状态栏/comfy/run_1125_maze.sh        起一个脱开的队列进程就回（gpt_cg5.py --spawn）；已经在跑就只报一声，不起第二个。
#   bash 底稿/状态栏/comfy/run_1125_maze.sh alive  看队列在不在跑
# 日志追加在 out/日志/1125_maze_nodes.log，一张一行的结果在 out/门面_原画_迷宫纪_节点/_队列.log，进程号在同目录 _队列.pid。
# 断了原样再跑一遍，出过的跳过。撞了 Codex 额度它自己等到恢复再接着出；Codex 秒退、日志空，它歇十分钟起再试，不空转。
# 要它停：在 out/门面_原画_迷宫纪_节点/ 里放一个空文件 _停（再起的时候 --spawn 会把它拿掉）。
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
export CODEX_HOME="${CODEX_HOME:-C:/Users/waitl/.codex_b}" CG_WORKERS="${CG_WORKERS:-2}"
if [ "$1" = "alive" ]; then
  "$PY" -X utf8 gpt_cg5.py --alive
else
  "$PY" -X utf8 gpt_cg5.py --spawn
fi
