#!/usr/bin/env python3
# 风月外壳在本地复刻台上看一眼（11-25）。复刻台是 tools/rili_bench/static_bench_fy.mjs（11-04 照风月前端代码搭的页面层级，这里不改它）。
#   python -I -X utf8 底稿/风月版/bench/fy_shell_bench.py <纪|全部> <输出目录> [--cdn] [--tabs] [--dev=电脑|手机] [--set=1001,前传…]
#     --dev、--set 只跑其中几样（--set 里空着的那一格是单纪的卡那一组，写 --set=,前传 这样）
# 做的事：拿 out/发布卡_风月_四纪/<纪>/外壳_<纪>.json，一纪挑两三条样本记录，电脑宽 1920×945、手机宽 390×844 各截一张（--tabs 再各页签一张）。
#   默认样式走同目录那一份 样式_<纪>.css（file:// 的 @import，跟卡里走图床 @import 是一条路，只是不连外网取样式）；--cdn 就用卡里的地址，连图床取。
#   平台自己的样式没有下：用 tools/rili_bench/fy_tw_min/tw_min.css 加这里的 fy_plat_more.css（手写的一小份），所以宽高、间距跟真页面有出入。
import json
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BIG = os.path.join(ROOT, '底稿', '状态栏', '大框')
BENCH = os.path.join(ROOT, 'tools', 'rili_bench', 'static_bench_fy.mjs')
S3 = os.path.join(BIG, '第三轮')
# 一纪两条：前一条进列表（Virtuoso 的行），后一条是最新一对问答。迷宫纪那一张另跑一组前传的、一组线上老档的旧 HTML 回复
SETS = {
    # 11-25 夜迷宫纪拆成前传、此刻两张：此刻那一张跑 1001、旧档、主角三组，前传那一张跑前传那一组。下面 '迷宫纪' 是拆以前那一张的（外壳不再重出）
    '迷宫纪此刻': [('1001', [os.path.join(BIG, '样本_中期_交战.txt'), os.path.join(BIG, '样本_队友浮栏_战斗.txt')]),
                 ('旧档', [os.path.join(BIG, '发布', '试写', 'old_battle.html'), os.path.join(BIG, '样本_新手.txt')]),
                 ('主角', [os.path.join(S3, '样本_主角头像_剪影_魔族夜翼.txt'), os.path.join(S3, '样本_主角头像_预设_晨曦人男健壮.txt')])],
    '迷宫纪前传': [('', [os.path.join(S3, '样本_命星页_前传.txt'), os.path.join(S3, '样本_家业页_前传.txt')])],
    '迷宫纪': [('1001', [os.path.join(BIG, '样本_中期_交战.txt'), os.path.join(BIG, '样本_队友浮栏_战斗.txt')]),
               ('前传', [os.path.join(S3, '样本_命星页_前传.txt'), os.path.join(S3, '样本_家业页_前传.txt')]),
               ('旧档', [os.path.join(BIG, '发布', '试写', 'old_battle.html'), os.path.join(BIG, '样本_新手.txt')]),
               # 前传和 1001 年混在一屏：材质跟着最新一对问答（前一条在列表里、后一条是最新）
               ('混_新1001', [os.path.join(S3, '样本_命星页_前传.txt'), os.path.join(BIG, '样本_中期_交战.txt')]),
               ('混_新前传', [os.path.join(BIG, '样本_中期_交战.txt'), os.path.join(S3, '样本_家业页_前传.txt')]),
               # 11-25 日里那头添的检定面板主角那一边（剪影、预设头像）：有那几份样本才跑
               ('主角', [os.path.join(S3, '样本_主角头像_剪影_魔族夜翼.txt'), os.path.join(S3, '样本_主角头像_预设_晨曦人男健壮.txt')])],
    '月银纪': [('', [os.path.join(BIG, '样本_月银纪_焚原.txt'), os.path.join(S3, '样本_检定演出_月银纪.txt')])],
    '纷争纪': [('', [os.path.join(BIG, '样本_纷争纪_墙前.txt'), os.path.join(S3, '样本_检定演出_纷争纪.txt')])],
    '山铜纪': [('', [os.path.join(BIG, '样本_山铜纪_长阶.txt'), os.path.join(S3, '样本_检定演出_山铜纪.txt')])],
}
TABS = ['panel', 'deed', 'bag', 'party', 'news', 'mem', 'war', 'estate']
STEP = "const a=[...document.querySelectorAll('#customized-answer')].pop();const t=a.querySelector('.t-%s input');if(t){t.click();const c=document.querySelector('.chat-container');const p=a.querySelector('.sz-tabs');if(p)c.scrollTop=Math.max(0,p.getBoundingClientRect().top+c.scrollTop-c.getBoundingClientRect().height+80);}"
EVAL = r'''(()=>{const q=(s)=>document.querySelector(s);const sh=q('#fy-sh'),ft=q('#installedBuiltInCss > .bg-gradient-to-t');const cs=getComputedStyle(sh);
const a=[...document.querySelectorAll('#customized-answer')].pop();const md=a&&a.querySelector('.markdown-body');
const g=(el,p)=>el?getComputedStyle(el).getPropertyValue(p).trim().slice(0,60):'';
return JSON.stringify({era:[...document.querySelectorAll('.sz-era')].map(e=>e.className.replace('sz-era ','')+':'+e.dataset.y),ink:g(sh,'--fm-ink'),band2:g(sh,'--fm-band2'),left:g(sh,'--fm-l').slice(0,50),bg:cs.backgroundImage.slice(0,40),
 ftInk:g(ft,'--fm-ink'),h:g(sh,'--sz-h'),themeBg:g(sh,'--background'),tabs:a?a.querySelectorAll('.sz-tab').length:0,tabsShown:a&&a.querySelector('.sz-tabs')?getComputedStyle(a.querySelector('.sz-tabs')).display:'',
 panes:a?[...a.querySelectorAll('.sz-pane')].filter(e=>getComputedStyle(e).display!=='none').length:-1,pf:a&&a.querySelector('.sz-pf')?getComputedStyle(a.querySelector('.sz-pf')).display+'/'+a.querySelectorAll('.sz-pfc').length:'无',
 mdColor:md?getComputedStyle(md).color:'',rules:document.styleSheets.length,sheet:[...document.styleSheets].map(s=>{try{return s.cssRules.length}catch(e){return 'x'}}).join(',')});})()'''


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    cards = [c for c in SETS if c != '迷宫纪'] if args[0] == '全部' else [args[0]]
    out = os.path.abspath(args[1])
    os.makedirs(out, exist_ok=True)
    plat = os.path.join(out, '_plat')
    os.makedirs(plat, exist_ok=True)
    shutil.copyfile(os.path.join(ROOT, 'tools', 'rili_bench', 'fy_tw_min', 'tw_min.css'), os.path.join(plat, 'a_tw_min.css'))
    shutil.copyfile(os.path.join(HERE, 'fy_plat_more.css'), os.path.join(plat, 'b_more.css'))
    ev = os.path.join(out, '_eval.js')
    open(ev, 'w', encoding='utf-8').write(EVAL)
    steps = os.path.join(out, '_steps.json')
    json.dump([{'name': t, 'js': STEP % t} for t in TABS], open(steps, 'w', encoding='utf-8'), ensure_ascii=False)
    only_dev = next((a.split('=', 1)[1] for a in sys.argv if a.startswith('--dev=')), None)
    only_set = next((a.split('=', 1)[1].split(',') for a in sys.argv if a.startswith('--set=')), None)
    for card in cards:
        d = os.path.join(ROOT, 'out', '发布卡_风月_四纪', card)
        shell = json.load(open(os.path.join(d, '外壳_%s.json' % card), encoding='utf-8'))
        if '--cdn' not in sys.argv:
            shell['built_in_css'] = '@import url("file:///%s");\n' % os.path.join(d, '样式_%s.css' % card).replace('\\', '/')
        cj = os.path.join(out, '_card_%s.json' % card)
        json.dump(shell, open(cj, 'w', encoding='utf-8'), ensure_ascii=False)
        for tag, files in SETS[card]:
            if only_set is not None and tag not in only_set:
                continue
            if tag == '主角' and not all(os.path.exists(f) for f in files):
                print(card, tag, '样本还没有，跳过')
                continue
            for f in files:
                assert os.path.exists(f), f
            for dev, w, h in (('电脑', 1920, 945), ('手机', 390, 844)):
                if only_dev and dev != only_dev:
                    continue
                png = os.path.join(out, '%s%s_%s.png' % (card, ('_' + tag) if tag else '', dev))
                cmd = ['node', BENCH, cj.replace('\\', '/'), ','.join(x.replace('\\', '/') for x in files), png.replace('\\', '/'), 'css=' + plat.replace('\\', '/'),
                       'w=%d' % w, 'h=%d' % h, 'scroll=latest', 'wait=6000', 'eval=' + ev.replace('\\', '/')]
                if '--tabs' in sys.argv and dev == '电脑':
                    cmd.append('steps=' + steps.replace('\\', '/'))
                r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
                print(card, tag, dev, (r.stdout + r.stderr).strip().replace('\n', ' | ')[:900])


if __name__ == '__main__':
    main()
