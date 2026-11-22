#!/usr/bin/env bash
# 11-22 正神化身照本尊（用户定的三类）：拾穗姑娘脸照本尊；书箱老人、老牧人五官是本尊老了的样子；翻穿灰衣的人兜帽下是本尊的脸。
# 旧图挪 立绘_月银纪史诗_备选/<键>/化身前_1122/。等二回（WAITPID）跑完再起。
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
export CODEX_HOME=C:/Users/waitl/.codex_b
while [ -n "$WAITPID" ] && kill -0 "$WAITPID" 2>/dev/null; do sleep 60; done
for k in ge7x_gleaner ge15x_scribe ge7x_shepherd ge9x_greycloak; do
  d=out/立绘_月银纪史诗; dst="${d}_备选/$k/化身前_1122"; mkdir -p "$dst"
  for p in "$d/$k"/*.png "$d/$k"/*.log; do [ -f "$p" ] && mv "$p" "$dst/"; done
  echo "== $k $(date +%H:%M)"; CAST_SET=月银纪史诗 "$PY" -X utf8 gpt_sheet.py "$k"
done
echo "化身重画跑完 $(date +%H:%M)"
