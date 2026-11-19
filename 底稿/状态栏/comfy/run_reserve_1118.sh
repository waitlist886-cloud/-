#!/usr/bin/env bash
# 11-18 立绘预留的出图队列：等出图额度回来以后跑（单子和缘故在 底稿/立绘/待出图_11-18.md）。
#   bash 底稿/状态栏/comfy/run_reserve_1118.sh          全跑
#   bash 底稿/状态栏/comfy/run_reserve_1118.sh redo      只跑重画的四位
#   bash 底稿/状态栏/comfy/run_reserve_1118.sh new       只跑新添的十位
# 出过的图 gpt_sheet.py 会跳过，所以重画的先把旧图挪进备选（挪过的不再挪）。撞了额度就停，等重置以后再跑一遍，只补缺的。
# 跑之前先看进程表里有没有别的 gpt_sheet.py 在跑，同一批键只许一条队列。
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
WHAT="${1:-all}"
mkdir -p out/日志
aside() {   # 纪 键：旧图整个目录挪进 out/立绘_<纪>_备选/<键>/改年轻前/
  local src="out/立绘_$1/$2" dst="out/立绘_$1_备选/$2/改年轻前"
  if [ -d "$src" ] && [ ! -d "$dst" ]; then
    mkdir -p "$(dirname "$dst")" && mv "$src" "$dst" && echo "   旧图挪走 $1 $2"
  fi
}
run() {     # 纪（1001 那一套写 1001） 日志名 键…
  local s="$1" L="out/日志/$2"; shift 2
  : > "$L"
  for pass in 1 2; do   # 第二遍只补缺的
    if [ "$s" = "1001" ]; then
      CAST_WORKERS=${CAST_WORKERS:-3} "$PY" -X utf8 gpt_sheet.py "$@" >> "$L" 2>&1
    else
      CAST_SET="$s" CAST_WORKERS=${CAST_WORKERS:-3} "$PY" -X utf8 gpt_sheet.py "$@" >> "$L" 2>&1
    fi
  done
  echo "== $s $* 好了 $(grep -c 好了 "$L") 失败 $(grep -c 失败 "$L") 额度 $(grep -c usage_limit "$L") $(date +%H:%M)"
}
if [ "$WHAT" = "all" ] || [ "$WHAT" = "redo" ]; then
  # 一、看着的年纪变了、要重画的四位（资料 11-18 已经改好）
  aside 诸国期 zg2_bori      # 博里：七十岁看着十七的少年 → 二十二岁的成年矮人
  aside 前传 q2_bjarke       # 比亚克：看着三十五 → 二十五
  aside 前传 q3_zane         # 赞恩：看着三十五六 → 二十七
  aside 前传 q2_dulf         # 杜尔夫第二页那一张：老矮人 → 一百三十来岁正当年（长相照第一页那一张的头）
  run 诸国期 预留_重画_诸国期_1118.log zg2_bori
  run 前传 预留_重画_前传_1118.log q2_bjarke q3_zane q2_dulf
fi
if [ "$WHAT" = "all" ] || [ "$WHAT" = "new" ]; then
  # 二、新添的十位（长相都照现成那一版的头）：
  #   名字凝住时已经比现成那一版老了不少的四位：格里姆二百九十七岁、欧丝嘉三十三岁、鲁珀特六十岁、安瑟姆三十八岁
  run 纷争纪 预留_凝名以后_纷争纪_1118.log z7_grim_legend z7_osca_legend
  run 萨尔维斯 预留_凝名以后_萨尔维斯_1118.log sa2_rupert_legend
  run 诸国期 预留_凝名以后_诸国期_1118.log zg5_anselm_legend
  #   六位活到 1001 年的旧人在 1001 那一套里的样子
  run 1001 预留_旧人_1118.log reva suhaila tove dove candace kent
fi
echo "== 排完 $(date +%H:%M)。出完照 底稿/立绘/待出图_11-18.md 第五节：查图、烘图、推图床、书里重出人像、状态栏立绘表添人"
