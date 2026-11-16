#!/usr/bin/env bash
# 一长串洗稿的活交给 Gemini 分块洗（一份里一回只洗几节），同一时刻至多并着跑 N 份，跑完一份补一份：
#   bash run_pool_gemini_chunk.sh <N> <份名…>
#   AGY_MODEL=gemini-3.8-flash-high（默认） CHUNK=4（一回至多几节）
# 每份先要跑过 改派_gemini.py。一份的洗、留底、自查、查添、再改都在 run_one_gemini_chunk.sh 里。
# 哪一份报了额度就不再往下派（已经在跑的让它跑完）。后台跑着的时候别改这两个脚本文件。
HERE="$(cd "$(dirname "$0")" && pwd)"
N="$1"; shift
LOG="${POOL_LOG:-}"
running=0
for j in "$@"; do
  if [ -n "$LOG" ] && grep -q "额度报错，停" "$LOG" 2>/dev/null; then echo "有一份报了额度，$j 起不再派"; break; fi
  while [ "$running" -ge "$N" ]; do
    wait -n
    running=$((running-1))
  done
  if [ -n "$LOG" ] && grep -q "额度报错，停" "$LOG" 2>/dev/null; then echo "有一份报了额度，$j 起不再派"; break; fi
  bash "$HERE/run_one_gemini_chunk.sh" "$j" "${CHUNK:-4}" &
  running=$((running+1))
  sleep 3
done
wait
echo "这一池都回来了 $(date +%H:%M:%S)"
