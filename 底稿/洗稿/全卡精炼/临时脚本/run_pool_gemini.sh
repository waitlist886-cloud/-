#!/usr/bin/env bash
# 一长串洗稿的活交给 Gemini，同一时刻至多并着跑 N 份，跑完一份补一份：
#   bash run_pool_gemini.sh <N> <份名…>
#   POOL_MODE=resume bash run_pool_gemini.sh <N> <份名…>   上一回断在半路的，只洗还没洗的节
#   AGY_MODEL=gemini-3.8-flash-high …                       换模型（默认 gemini-4-argon-high）
# 每份先要跑过 改派_gemini.py。一份的洗、留底、自查、再改都在 run_one_gemini.sh 里。
# 后台跑着的时候别改这两个脚本文件（bash 边读边跑）。
HERE="$(cd "$(dirname "$0")" && pwd)"
N="$1"; shift
running=0
for j in "$@"; do
  while [ "$running" -ge "$N" ]; do
    wait -n
    running=$((running-1))
  done
  bash "$HERE/run_one_gemini.sh" "$j" ${POOL_MODE:-} &
  running=$((running+1))
  sleep 3
done
wait
echo "这一池都回来了 $(date +%H:%M:%S)"
