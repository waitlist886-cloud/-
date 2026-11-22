#!/usr/bin/env bash
# 11-22 长相核对以后整套重出的 28 版（单子 out/长相核对_1122/重画单.json）。等新人队列（run_1122_new.sh）跑完再起。
# 旧图挪进 out/立绘_<纪>/备选/<键>/长相前_1122/（1001 那一套在 立绘_v3/备选/），再照单子的次序一位一位出（s4c_torbe 要在 s3b_torbe 前头）。
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
export CODEX_HOME=C:/Users/waitl/.codex_b
busy() {
  powershell -NoProfile -Command "\$p = Get-CimInstance Win32_Process | Where-Object { (\$_.Name -like 'python*' -and (\$_.CommandLine -like '*gpt_sheet*' -or \$_.CommandLine -like '*fix_cell*')) -or (\$_.Name -like 'bash*' -and \$_.CommandLine -like '*run_1122_new*') }; if (\$p) { exit 0 } else { exit 1 }"
}
while busy; do sleep 60; done
"$PY" -X utf8 - <<'PYEOF'
import json, os, shutil
L = json.load(open('out/长相核对_1122/重画单.json', encoding='utf-8'))
for j in L:
    d = os.path.join('out', '立绘_v3' if j['set'] == '1001' else '立绘_' + j['set'])
    src = os.path.join(d, j['en'])
    if not os.path.isdir(src):
        continue
    dst = os.path.join(d, '备选', j['en'], '长相前_1122')
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(src):
        p = os.path.join(src, f)
        if os.path.isfile(p):
            shutil.move(p, os.path.join(dst, f))
    print('挪了', j['set'], j['en'])
PYEOF
"$PY" -X utf8 -c "
import json
for j in json.load(open('out/长相核对_1122/重画单.json',encoding='utf-8')): print(j['set'], j['en'])" | while read s k; do
  echo "== $s $k $(date +%H:%M)"
  if [ "$s" = "1001" ]; then "$PY" -X utf8 gpt_sheet.py $k; else CAST_SET=$s "$PY" -X utf8 gpt_sheet.py $k; fi
done
echo "长相重画跑完 $(date +%H:%M)"
