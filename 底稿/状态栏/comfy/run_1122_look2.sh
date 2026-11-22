#!/usr/bin/env bash
# 11-22 长相重画查图以后的二回：六位重出（旧图挪 立绘_<纪>_备选/<键>/长相二回前_1122/），桑托只重画战斗格（FIX_WORK=长相_1122，查过再 apply）。
# 等新人重出（WAITPID）和纳吉布补画跑完再起。
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
export CODEX_HOME=C:/Users/waitl/.codex_b
while [ -n "$WAITPID" ] && kill -0 "$WAITPID" 2>/dev/null; do sleep 60; done
pybusy() { powershell -NoProfile -Command "if (Get-CimInstance Win32_Process | Where-Object { \$_.Name -like 'python*' -and \$_.CommandLine -like '*gpt_sheet*' }) { exit 0 } else { exit 1 }"; }
while pybusy; do sleep 60; done
mv_old() {  # 纪 键 文件名…
  s=$1; k=$2; shift 2
  dst="out/立绘_${s}_备选/$k/长相二回前_1122"; mkdir -p "$dst"
  for n in "$@"; do for p in out/立绘_$s/$k/$n; do [ -f "$p" ] && mv "$p" "$dst/"; done; done
}
for sk in 前传:q5b_lumian 山铜纪:s4a_ruda 山铜纪:s5b_auro 山铜纪:s3b_dorkan 萨尔维斯:sa5_inriel; do
  s=${sk%%:*}; k=${sk#*:}
  mv_old "$s" "$k" '*.png' '*.log'
  echo "== $s $k $(date +%H:%M)"; CAST_SET=$s "$PY" -X utf8 gpt_sheet.py "$k"
done
mv_old 山铜纪 s4b_boru art.png art.log faces.png faces_raw.png faces.log
echo "== 山铜纪 s4b_boru $(date +%H:%M)"; CAST_SET=山铜纪 "$PY" -X utf8 gpt_sheet.py s4b_boru
CAST_SET=前传 FIX_WORK=长相_1122 "$PY" -X utf8 fix_cell.py run out/长相核对_1122/单格_二回.json
CAST_SET=前传 FIX_WORK=长相_1122 "$PY" -X utf8 fix_cell.py sheet out/长相_1122/对照_桑托.jpg out/长相核对_1122/单格_二回.json
echo "长相二回跑完 $(date +%H:%M)"
