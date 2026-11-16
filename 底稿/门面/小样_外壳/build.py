#!/usr/bin/env python3
# 外壳（11-15 拼装那一轮）：牌桌那一页加上装书的那一格、建档、请离那一眼、确认页，就是整个门面的头一页。
#   python -I -X utf8 build.py        从 ../小样_牌桌/index.html 出 index.html，牌桌的图拷进 assets/
# 牌桌那一页（定在第十九版）不动，这里照原文对上了才改几处；外壳自己的东西在 shell.css、shell.js。
# 本地看：.claude/launch.json 的 front-shell（8772，根是 底稿/门面/），开 http://localhost:8772/小样_外壳/local.html
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.normpath(os.path.join(HERE, '..', '小样_牌桌'))


def main():
    s = open(os.path.join(TABLE, 'index.html'), encoding='utf-8').read()

    def rep(old, new, n=1):
        nonlocal s
        k = s.count(old)
        if k != n:
            raise SystemExit('对不上（%d 处）：%s' % (k, old[:80]))
        s = s.replace(old, new)

    # 1. 共用的世界之书、外壳自己的样式和脚本。A() 是图和数据的地址怎么换：这一页装进卡里的时候整页有 <base> 指到图床，原样就行
    rep("<script>\n(() => {\n  const $ = s => document.querySelector(s);",
        "<link rel=\"stylesheet\" href=\"common/codex.css\">\n<link rel=\"stylesheet\" href=\"shell.css\">\n"
        "<script>window.A = window.A || ((p) => p);</script>\n<script src=\"common/codex.js\"></script>\n"
        "<script>\n(() => {\n  const $ = s => document.querySelector(s);")
    rep("  intro();\n})();\n</script>", "  intro();\n})();\n</script>\n<script src=\"shell.js\"></script>")
    # 2. 选定一纪以后多一个“翻开这一本”，外壳接手
    rep('<div id="acts" hidden><button id="again" type="button">再选一纪</button>', '<div id="acts" hidden><button id="openBook" type="button">翻开这一本</button><button id="again" type="button">再选一纪</button>')
    rep("    say('', '往下是这一纪的书。小样到这里');\n    acts.hidden = false; stage = 'done'; phase('ok');",
        "    say('', '');\n    acts.hidden = false; stage = 'done'; phase('ok'); if (window.Shell) Shell.onEra(picked);")
    rep("  window.__tb = {   /* 本地验的时候用 */\n", "  window.__tb = {   /* 本地验的时候用；外壳也靠它问牌桌走到哪了 */\n    get picked() { return picked; }, again: () => enterChoose(true),\n")
    # 3. 书开着的时候牌桌不画（省显存和电）
    rep("  function frame(now) {\n", "  function frame(now) {\n    if (window.__tbPause) { last = now; raf(frame); return; }\n")
    # 4. 手的图要进画布和 WebGL：装进卡里是从图床载，得带跨域标记
    rep('<img id="hOpen" src="assets/hand9_open.webp" alt="">', '<img id="hOpen" crossorigin="anonymous" src="assets/hand9_open.webp" alt="">')
    rep('<img id="hHold" src="assets/hand9_take.webp" alt="">', '<img id="hHold" crossorigin="anonymous" src="assets/hand9_take.webp" alt="">')
    # 5. 日里的介绍页没有 localStorage，“换轻量画法”记不住：改记在 window.name 里（11-12 探针量过，重载以后还在），外壳左下角一枚小钮能手动换
    rep("if (q.has('lite')) LITE = true;", "if (q.has('lite') || /tb:lite/.test(window.name || '')) LITE = true;")
    rep("store.set('tb_step', 'ok'); location.reload(); });", "store.set('tb_step', 'ok'); try { window.name = ''; } catch (e) {} location.reload(); });")
    # 6. 这一格还没有大小（日里先按 0×0 建出来），或者书开着、牌桌整个收起来的时候，不照 0 去排版
    rep("    const W = view.clientWidth, H = view.clientHeight;\n    S = H / 1536;", "    const W = view.clientWidth, H = view.clientHeight;\n    if (!W || !H) return;\n    S = H / 1536;")
    # 7. 牌桌有一条“谁滚了就按回原位”的监听（捕获阶段，挂在 window 上），本意是不让整页和舞台被带着滚走。
    #    外壳添的那几层（建档、确认页、世界之书）也在这一页里，同样被它按回 0，建档页就滚不动、够不着底下那枚钮（11-16 用户在日里上碰到的）。
    #    改成只管整页和 #view 里头，外壳那几层在 #view 外头，各滚各的。
    rep("    if (t && (t.scrollTop || t.scrollLeft)) { t.scrollTop = 0; t.scrollLeft = 0; }",
        "    if (t && t !== document.scrollingElement && t !== document.body && !view.contains(t)) return;      /* 外壳添的几层自己要滚 */\n"
        "    if (t && (t.scrollTop || t.scrollLeft)) { t.scrollTop = 0; t.scrollLeft = 0; }")
    open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8', newline='\n').write(s)
    # 牌桌用的图（index_v*.html 那些旧图不拷）
    need = ['table.webp', 'hand9_open.webp', 'hand9_take.webp'] + ['%s_%d.webp' % (p, i) for p in ('era', 'back', 'bb') for i in range(4)]
    os.makedirs(os.path.join(HERE, 'assets'), exist_ok=True)
    for f in need:
        shutil.copy2(os.path.join(TABLE, 'assets', f), os.path.join(HERE, 'assets', f))
    print('index.html', len(s), '字，图', len(need), '张')


if __name__ == '__main__':
    main()
