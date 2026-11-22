#!/usr/bin/env bash
# 11-22 四本书新人（cast/<纪>/*x.json）和纷争纪对手补画的出图队列。等战装重画（1122_war_redraw）跑完再起，同一时间只跑一条队列。
# 同一个人的几版：先出时间晚的那一版（resolve_identity 的次序），所以一页一页从后往前跑，一页一回 gpt_sheet。
# q6x_santo（桑托·晴林）长相留给用户定，没定以前不出。撞了额度就停，额度回来再跑一遍，只补缺的。
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
export CODEX_HOME=C:/Users/waitl/.codex_b
mkdir -p out/日志
busy() {
  powershell -NoProfile -Command "\$p = Get-CimInstance Win32_Process | Where-Object { (\$_.Name -like 'python*' -and (\$_.CommandLine -like '*gpt_sheet*' -or \$_.CommandLine -like '*fix_cell*')) }; if (\$p) { exit 0 } else { exit 1 }"
}
while busy; do sleep 60; done
"$PY" -X utf8 resolve_identity.py --apply $(cd cast && ls */*x.json | xargs -n1 basename) > out/日志/1122_resolve.log 2>&1
run() {   # 纪 页文件
  local s=$1 f=$2
  local keys
  keys=$("$PY" -X utf8 -c "
import json,sys
d=json.load(open('cast/$s/$f',encoding='utf-8'))
print(' '.join(x['en'] for x in d if x.get('en') and x['en']!='q6x_santo'))")
  [ -z "$keys" ] && return
  echo "== $s $f $(date +%H:%M)"
  CAST_SET=$s "$PY" -X utf8 gpt_sheet.py $keys
}
for f in q6x q5x q4x q3x q2x q1x; do [ -f cast/前传/$f.json ] && run 前传 $f.json; done
for f in s6x s5x s4x s3x s2x s1x; do [ -f cast/山铜纪/$f.json ] && run 山铜纪 $f.json; done
for f in z7x z6x z5x z4x z3x z2x z1x z6r z4r; do [ -f cast/纷争纪/$f.json ] && run 纷争纪 $f.json; done
for f in sa6x sa5x sa4x sa3x sa2x sa1x; do [ -f cast/萨尔维斯/$f.json ] && run 萨尔维斯 $f.json; done
for f in zg6x zg5x zg4x zg3x zg2x zg1x; do [ -f cast/诸国期/$f.json ] && run 诸国期 $f.json; done
for f in ge15x ge9x ge7x ge5x ge4x ge2x ge1x; do [ -f cast/月银纪史诗/$f.json ] && run 月银纪史诗 $f.json; done
echo "新人队列跑完 $(date +%H:%M)"
