bash "/e/aldran_art/底稿/状态栏/comfy/out/日志/排队/run_redo2.sh"
cd /e/aldran_art/底稿/状态栏/comfy
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
keys=$(cat "/e/aldran_art/底稿/状态栏/comfy/out/日志/排队/keys_redo_q1.txt")
echo "== 第一页重出 $(date +%H:%M)"
CAST_SET=前传 CAST_WORKERS=2 "$PY" -X utf8 gpt_sheet.py $keys > out/日志/重出_q1.log 2>&1
CAST_SET=前传 CAST_WORKERS=2 "$PY" -X utf8 gpt_sheet.py $keys >> out/日志/重出_q1.log 2>&1
echo "   好了 $(grep -c 好了 out/日志/重出_q1.log)  失败 $(grep -c 失败 out/日志/重出_q1.log)  切不开 $(grep -c 切不开 out/日志/重出_q1.log)"
echo "== 排完 $(date +%H:%M)"
