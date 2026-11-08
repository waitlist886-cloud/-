#!/bin/bash
# 重新打开 Azgaar、载入 .map、摆成整张图 1:1 不带字（az_plain.js）。用法：bash az_reset.sh <.map>
set -e
cd "$(dirname "$0")"
node cdp.mjs nav "https://azgaar.github.io/Fantasy-Map-Generator/" >/dev/null
for i in $(seq 1 40); do
  r=$(node cdp.mjs eval "typeof pack==='object'&&!!document.getElementById('mapToLoad')" 2>/dev/null || true)
  [ "$r" = "true" ] && break
  sleep 1
done
sleep 4
node cdp.mjs upload "#mapToLoad" "$1" >/dev/null
for i in $(seq 1 60); do
  r=$(node cdp.mjs eval "(pack.states||[]).some(s=>s.name==='黑耀帝国')" 2>/dev/null || true)
  [ "$r" = "true" ] && break
  sleep 1
done
sleep 3
node cdp.mjs shot "${TMP:-/tmp}/_az_vp.png" 2200 1400 >/dev/null  # 截一张只为把视口摆成 2200×1400
node cdp.mjs file az_plain.js
node cdp.mjs eval "(()=>{for(const id of ['scaleBar','vignette']){const e=document.getElementById(id);if(e)e.style.display='none'};return 'ok'})()"
