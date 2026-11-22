#!/usr/bin/env bash
# 11-22 用户回“都照倾向”以后的重画：九位整套重出（旧图挪 <目录>_备选/<键>/倾向前_1122/）。等长相二回（WAITPID）跑完再起。
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
export CODEX_HOME=C:/Users/waitl/.codex_b
while [ -n "$WAITPID" ] && kill -0 "$WAITPID" 2>/dev/null; do sleep 60; done
for sk in 1001:mortus 1001:grom 1001:akasha 1001:septin 山铜纪:s5b_grom 山铜纪:s3b_grom 山铜纪:s4a_joren 纷争纪:z2_gaz 月银纪史诗:ge7x_gleaner; do
  s=${sk%%:*}; k=${sk#*:}
  if [ "$s" = 1001 ]; then d=out/立绘_v3; else d=out/立绘_$s; fi
  dst="${d}_备选/$k/倾向前_1122"; mkdir -p "$dst"
  for p in "$d/$k"/*.png "$d/$k"/*.log; do [ -f "$p" ] && mv "$p" "$dst/"; done
  echo "== $s $k $(date +%H:%M)"
  if [ "$s" = 1001 ]; then "$PY" -X utf8 gpt_sheet.py "$k"; else CAST_SET=$s "$PY" -X utf8 gpt_sheet.py "$k"; fi
done
echo "倾向重画跑完 $(date +%H:%M)"
