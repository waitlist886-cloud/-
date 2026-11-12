#!/bin/bash
# 11-12 玩家反馈那一轮：在线上那四张底卡（日里、风月，各一张我们的、一张用户底）上打补丁。
# 头一回跑先把修复前的四张存进 修复前_11-10/（不进库），往后每回都从那里拿底子重打，改了 fix_1112.py、mod_page.py、底卡新条目 再跑一遍就行。
# 用法：bash 底稿/状态栏/大框/build_fix_1112.sh
set -e
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
[ -x "$PY" ] || PY=python
ROOT=/e/aldran_art
T="$ROOT/底稿/状态栏/大框"
RL="$ROOT/out/发布卡_迷宫纪大框"
FY="$ROOT/out/发布卡_风月_迷宫纪大框"
mkdir -p "$RL/修复前_11-10" "$FY/修复前_11-10"
for f in 奥尔德兰_底卡_迷宫纪大框.json 奥尔德兰_底卡_迷宫纪大框_用户底.json; do
  [ -f "$RL/修复前_11-10/$f" ] || cp "$RL/$f" "$RL/修复前_11-10/$f"
done
for f in 奥尔德兰_风月底卡_迷宫纪大框.json 奥尔德兰_风月底卡_迷宫纪大框_用户底.json; do
  [ -f "$FY/修复前_11-10/$f" ] || cp "$FY/$f" "$FY/修复前_11-10/$f"
done
for f in 奥尔德兰_底卡_迷宫纪大框.json 奥尔德兰_底卡_迷宫纪大框_用户底.json; do
  echo "== 日里 $f"
  "$PY" -I -X utf8 "$T/patch_pub_1112.py" "E:/aldran_art/out/发布卡_迷宫纪大框/修复前_11-10/$f" "E:/aldran_art/out/发布卡_迷宫纪大框/$f"
done
for f in 奥尔德兰_风月底卡_迷宫纪大框.json 奥尔德兰_风月底卡_迷宫纪大框_用户底.json; do
  echo "== 风月 $f"
  "$PY" -I -X utf8 "$T/patch_fy_1112.py" "E:/aldran_art/out/发布卡_风月_迷宫纪大框/修复前_11-10/$f" "E:/aldran_art/out/发布卡_风月_迷宫纪大框/$f"
done
