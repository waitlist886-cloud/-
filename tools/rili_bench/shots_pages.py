#!/usr/bin/env python3
# 大框七页一页一张图（11-04）：python3 shots_pages.py 输出目录 前缀 宽 高 [页,页] [样本]，在任何目录跑都行。
# 页签是点开的（eval 里点单选钮），点完等转场走完，把窗口滚到那一页的头再截。要看卡就在 extra 里点那一格的单选钮：
#   python3 shots_pages.py out x 1600 1000 bag 样本.txt "[...document.querySelectorAll('.p-bag .sz-cell[data-n*=\"黑牙\"] .sz-face input')].pop().click();await new Promise(r=>setTimeout(r,300));"
import os
import subprocess
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, '..', '..', '底稿', '状态栏')
out, tag, w, h = sys.argv[1:5]
pages = sys.argv[5].split(',') if len(sys.argv) > 5 else ['panel', 'deed', 'bag', 'party', 'news', 'mem', 'war']
sample = sys.argv[6] if len(sys.argv) > 6 else os.path.join(B, '大框', '样本_中期_交战.txt')
extra = sys.argv[7] if len(sys.argv) > 7 else ''
os.makedirs(out, exist_ok=True)
for pg in pages:
    js = os.path.join(out, '_eval_%s.js' % pg)
    open(js, 'w', encoding='utf-8').write("""(async()=>{
[...document.querySelectorAll('.t-%s input')].pop().click();
await new Promise(r=>setTimeout(r,1250));
for(const a of document.getAnimations()){if(a.timeline instanceof DocumentTimeline&&a.effect&&a.effect.getTiming().iterations!==Infinity){try{a.finish()}catch(e){}}}
const p=[...document.querySelectorAll('.p-%s')].pop(),c0=document.getElementById('conversation');
window.lay&&window.lay();c0.scrollTop=p.getBoundingClientRect().top-c0.getBoundingClientRect().top+c0.scrollTop-112;
%s
return 'ok'})()""" % (pg, pg, extra))
    r = subprocess.run(['node', 'static_bench.mjs', sample, os.path.abspath(os.path.join(out, '%s_%s.png' % (tag, pg))), 'w=' + w, 'h=' + h, 'chips=样本一,样本二,超程铭刻,防抢话',
                        'extracss=' + os.path.join(B, '大框', 'frame.css'), 'extrarules=' + os.path.join(B, '大框', 'rules_frame.json'),
                        'art=' + os.path.join(B, 'comfy', 'out', '四方_11-03', 'art_fu_ab'), 'eval=' + os.path.abspath(js), 'scroll=latest', 'wait=900'],
                       cwd=HERE, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(pg, r.stdout.strip().split('\n')[-1][-50:], r.stderr[-200:])
    os.remove(js)
