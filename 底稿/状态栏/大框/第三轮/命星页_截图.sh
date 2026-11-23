#!/bin/bash
# 命星页的截图，放 底稿/状态栏/大框/截图/第三轮_命星页/。在仓库根上跑：
#   bash 底稿/状态栏/大框/第三轮/命星页_截图.sh <临时目录> [只跑名字里带这几个字的]
# 先照 命星页_build.py 在临时目录里出一份接好的规则，再一张一张截（一张十几二十秒，全套五十几张）。
T="$1"; ONLY="$2"
D=底稿/状态栏/大框
OUT=$D/截图/第三轮_命星页
mkdir -p "$T" "$OUT"
python -I -X utf8 $D/第三轮/命星页_build.py "$T/merged.json" | tail -1
shot() {   # 样本 出图名 宽 高 [点页签的参数…]
  local smp="$1" name="$2" w="$3" h="$4"; shift 4
  case "$name" in *"$ONLY"*) ;; *) return ;; esac
  local f; case "$smp" in */*) f="$smp";; *) f="$D/第三轮/$smp.txt";; esac
  python -I -X utf8 $D/第三轮/命星页_点页签.py "$T/ev.js" "$@"
  MSYS_NO_PATHCONV=1 node tools/rili_bench/static_bench.mjs "$f" "$OUT/$name.png" w=$w h=$h sidebar=0 extracss=$D/frame.css,$D/第三轮/命星页.css extrarules="$T/merged.json" art=底稿/状态栏/comfy/out/frame_art scroll=latest eval="$T/ev.js" | grep -v '^ok' | grep -v '"over":\[\],"raw":\[\]'
  rm -f "$OUT/$name.html"
}
# ---- 迷宫纪 1001：中期（极境快到英雄）----
shot 样本_命星页 迷宫纪_电脑_整页_Art 1536 1500 cat=Art item=1 off=10
shot 样本_命星页 迷宫纪_电脑_进阶和职业 1536 1024 cat=命星 off=10
shot 样本_命星页 迷宫纪_电脑_命星_Unique 1536 1024 cat=命星 item=2 anchor=.sz-book off=150
shot 样本_命星页 迷宫纪_电脑_Art 1536 1024 cat=Art item=2 anchor=.sz-book off=150
shot 样本_命星页 迷宫纪_电脑_Passive 1536 1024 cat=Passive item=3 anchor=.sz-book off=150
shot 样本_命星页 迷宫纪_电脑_Active 1536 1024 cat=Active item=3 anchor=.sz-book off=150
shot 样本_命星页 迷宫纪_电脑_Skill 1536 1024 cat=Skill item=1 anchor=.sz-book off=110
shot 样本_命星页 迷宫纪_电脑_职业能力 1536 1024 cat=职业能力 item=3 anchor=.sz-book off=150
shot 样本_命星页 迷宫纪_电脑_1920 1920 945 cat=Art item=1 off=10
shot 样本_命星页 迷宫纪_手机_进阶和职业 390 844 cat=Art off=44
shot 样本_命星页 迷宫纪_手机_Art 390 844 cat=Art item=1 anchor=.sz-book off=60
shot 样本_命星页 迷宫纪_手机_Skill 390 844 cat=Skill item=2 anchor=.sz-book off=60
shot 样本_命星页 迷宫纪_手机_整页 390 2100 cat=Active item=4 off=44
# ---- 几种时候 ----
shot 样本_命星页_齐了 迷宫纪_电脑_都齐了 1536 1024 cat=Passive off=10
shot 样本_命星页_英雄 迷宫纪_电脑_英雄那一境 1536 1024 cat=Art off=10
shot 样本_命星页_神力 迷宫纪_电脑_凡极以后神力 1536 1024 cat=命星 off=10
shot 样本_命星页_神力 迷宫纪_手机_凡极以后神力 390 844 cat=命星 off=44
# ---- 新手 ----
shot 样本_命星页_新手 新手_电脑 1536 1024 cat=Art item=1 off=10
shot 样本_命星页_新手 新手_电脑_Skill 1536 1024 cat=Skill item=1 anchor=.sz-book off=150
shot 样本_命星页_新手 新手_手机 390 1500 cat=Art item=1 off=44
# ---- 另三纪 ----
for e in 月银纪 纷争纪 山铜纪; do
  shot 样本_命星页_$e ${e}_电脑_整页_Art 1536 1500 cat=Art item=1 off=10
  shot 样本_命星页_$e ${e}_电脑_Skill 1536 1024 cat=Skill item=2 anchor=.sz-book off=110
  shot 样本_命星页_$e ${e}_手机_进阶和职业 390 844 cat=Art off=44
  shot 样本_命星页_$e ${e}_手机_Art 390 844 cat=Art item=1 anchor=.sz-book off=60
done
# ---- 旧写法、写歪了的 ----
shot $D/样本_中期_交战.txt 旧写法_电脑_Art 1536 1500 cat=Art item=1 off=10
shot $D/样本_中期_交战.txt 旧写法_电脑_Skill 1536 1024 cat=Skill item=1 anchor=.sz-book off=150
shot 样本_命星页_写歪 写歪了_电脑_Art 1536 1500 cat=Art item=2 off=10
shot 样本_命星页_写歪 写歪了_电脑_Skill 1536 1024 cat=Skill item=3 anchor=.sz-book off=150
shot 样本_命星页_写歪 写歪了_电脑_职业能力 1536 1024 cat=职业能力 item=1 anchor=.sz-book off=150
shot 样本_命星页_写歪二 写歪了_电脑_进阶对不上 1536 1024 cat=命星 off=10
# ---- 动的：翻到 Art 那一下节点一颗一颗亮；Unique 那一道光 ----
for t in 0.10 0.25 0.45 0.90; do shot 样本_命星页 动_节点亮起_${t}秒 1536 1024 cat=Art item=1 anchor=.sz-book off=150 t=$t; done
for t in 3.5 4.0 4.5; do shot 样本_命星页 动_Unique那道光_${t}秒 1536 1024 cat=命星 item=2 anchor=.sz-book off=150 t=$t; done
