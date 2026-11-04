# 日里聊天页本地复刻台

照 rili-chat-frontend 第7节搭的，11-02 状态栏美化方向稿那一轮用的。改了两处：bench.mjs 拿 createRequire 读系统里装好的 playwright（云端会话里 `require('playwright')` 在哪个目录都能用，别另装），添了 `extracss=` `extrarules=` 两个参数，把一层新样式、一组新显示正则接在卡原有的后面。

装：在一个临时目录里放这几个文件，`npm i react@18 react-dom@18 react-markdown remark-gfm remark-breaks rehype-raw postcss esbuild tailwindcss@4 safe-regex`（package.json 里记着）。node_modules 不进仓库。

用（在那个临时目录里）：
- `node bench.mjs <卡.json> <样本1.html,样本2.html> out/前缀 w=390 h=844 mobile=1 extracss=层.css extrarules=规则.json steps=steps_mobile.mjs`
- 宽屏：`w=1440 h=900 steps=steps_desk.mjs`
- 拼对照图：`node compose.cjs out/对照.png "标题" "标签=图.png" …`

样式里的图地址写成 `__ART__/x.svg`，跑之前 `sed "s#__ART__#file://<图目录>#g"` 换成本地路径。它复刻的是版面和规则，字体、图床、真实模型写歪的样子要到真页面上才看得见。

11-02 状态栏方向稿第二版（转紧凑记法）添的三个：
- `node expand.mjs 回复.txt 规则1.json [规则2.json…]`：拿规则把一条回复展开，报 safe-regex 不过的规则、残留的记号和换行，展开结果写在回复旁边（.expanded.html）。
- `node wake_cmp.mjs 卡.json 甲.html 乙.txt`：同一条回复的两种写法，各叫醒世界书里哪些范围含助手的条目（单条消息，不算深度、不带开局口令），列出只在一边醒的。
- `node rawshot.cjs 回复.txt 输出.png 行数`：把紧凑原文截成手机宽的一张图，记录行标金色。

11-02 状态栏方向稿第三版（照用户的电脑端构想图做的手札样张）添的：
- bench.mjs 添 `sidebar=0|1`（宽屏默认开着侧栏，对构想图时关掉），`extracss=`、`extrarules=` 可以写几个文件，逗号隔开。
- `python3 -I -X utf8 fetch_font.py <目录> <样本…>`：从 Google Fonts 只下样本里用到的思源宋体切片，写一份本地 font_local.css，跑的时候 `extracss=层.css,<目录>/font_local.css`。云端会话里只有文泉驿黑体，不带它截出来全是黑体。字体文件不进仓库。
- steps_sz_desk.mjs（整张、点开面板、点开同行、点开推演）、steps_sz_mobile.mjs（开头、读到一半、分支、点开面板）、steps_hdr.mjs（只截三条，顺带打印每一条按数算出来的长度）。
- 手札样张这样跑：`sed "s#__ART__#file://<仓库>/底稿/状态栏/手札/占位图#g" 底稿/状态栏/手札/shouzha.css > sz.css`，再 `node bench.mjs <卡> 样本.txt out/x w=1536 h=1024 sidebar=0 extracss=sz.css,<目录>/font_local.css extrarules=<仓库>/底稿/状态栏/手札/rules_shouzha.json steps=steps_sz_desk.mjs`。

11-02 状态栏方向稿第四版（大框）添的：steps_fm_desk.mjs（宽屏：读到末尾、最新一条、往上翻旧回复、点面板的转场三帧、面板、背包、同行、返回手札）、steps_fm_mobile.mjs、steps_fm_moon.mjs、steps_fm_swatch.mjs（五纪材质一条一条截）。转场那几帧是点完以后拿 `document.getAnimations()` 把动画停在某一刻截的。图地址照旧 `sed "s#__ART__#file://<目录>#g"`，目录里放 底稿/状态栏/样张/占位图/ 的月银纪四幅和 底稿/状态栏/手札/占位图/ 的两半。

11-02 第四版改层次那一回（浮雕是框的一部分，对话压在下面）添的：steps_fm_layers.mjs（同一屏拆成五层，一层截一张透明底的，再截一张合起来的，拼示意图用），steps_fm_era.mjs（一纪一张宽屏）。宽屏框右边那一颗是跟着滚动走的样式动画（滚动时间线），各个 steps_fm_* 停动画、跑完动画时都只动 `a.timeline instanceof DocumentTimeline` 的，给滚动时间线的动画设 currentTime 会报错。

11-03 大旻长夜（另一张卡）添的：steps_dm.mjs（最新一条的推演、行卷、玉牒、武藏天赋、群英、风闻、行止抉择并点一条看输入框、经纬、藏卷，再往上看旧回复）。跑法：`node bench.mjs <空卡或 大旻长夜/out/大旻长夜_日里版_紧凑.json> 样本1.txt,样本2.txt out/x w=1440 h=900 extracss=<仓库>/大旻长夜/状态栏/dm.css,<字体目录>/font_local.css extrarules=<仓库>/大旻长夜/状态栏/rules_dm.json steps=steps_dm.mjs`（用打好的紧凑卡就不用 extracss 的 dm.css 和 extrarules）。

11-03 大旻长夜大框（另一张卡）添的：steps_dmf_desk.mjs（宽屏：末尾、开卷、推演、旧回复、点玉牒的转场三帧、玉牒武藏群英风闻经纬藏卷、返回、点行策，再读滚动那一枚铜钱的位置）、steps_dmf_mobile.mjs（手机六张）、steps_dmf_fn.mjs（存档轮在最后时上一条叙事轮照旧带页签）。跑法：`node bench.mjs <空卡或 大旻长夜/out/大旻长夜_日里版_紧凑.json> 样本1.txt,样本2.txt out/x w=1440 h=900 extracss=<仓库>/大旻长夜/状态栏/frame_dm.css,<字体目录>/font_local.css extrarules=<仓库>/大旻长夜/状态栏/rules_frame_dm.json steps=steps_dmf_desk.mjs`（用打好的紧凑卡就不用带 extracss 的 frame_dm.css 和 extrarules）。

11-03 大旻长夜第三轮照日里真页面的截图改了复刻台：输入框上头添一排预设小签（读卡的 options，横着滚），框里底下一排工具钮（齿轮、说明、模型签、实时、发送），大小照真页面量的，预设一排连输入框离底一百二十像素上下。原来没有这一排，框底和页签贴的位置在真页面上会被它压住。

11-03 奥尔德兰 v12 主线进状态栏添的：steps_quest.mjs（截推演底座折着那一行，打印 hud-quest 那一格的位置和颜色，再截见闻的在办）。跑法：`node bench.mjs <快打出来的 v12 卡> 样本.html out/q w=1440 h=900 steps=steps_quest.mjs`，样本照 moon/samples 里的回复在 hud-meta 后头添一格 `<span class="hud-quest">…</span>`。

11-03 添的 static_bench.mjs：不装依赖，用本机的 Chrome 或 Edge 无头出图（node 24 自带 WebSocket，走 DevTools 协议定视口）。版面照 app.jsx 和 shell.css，作用域照 platform.mjs，省掉了 markdown，回复展开成 HTML 以后一条一条放进 innerHTML。不能点页签，点页签那些步骤还要 bench.mjs。用法：`node static_bench.mjs 样本1,样本2 输出.png w=1536 h=1024 extracss=frame.css extrarules=rules_frame.json art=图目录 [sidebar=1] [scroll=latest|end|数字] [scrolls=end,300] [eval=查东西.js]`。Windows 上样本检出来是 CRLF，规则认 LF，脚本里去掉了 CR。

11-03 大框上真页面以前给 static_bench.mjs 添的：输入框上头一排预设（`chips=甲,乙`，默认超程铭刻、防抢话）和框里的工具钮，大小照 shell.css；`eval=` 的脚本可以返回 Promise，点页签、等动画都能写在里面（点完拿 `document.getAnimations()` 停在某一刻再截）。点开以后回复变高，这里不重排虚拟列表，读到的列表高度是旧的。

11-03 用户把大框测试卡导进日里，发了三张真页面截图（电脑，视口 3125×1150 上下），复刻台照它改了：输入栏是一整块圆角黑底（宽 640、高 118 上下、离底 12，底色 `rgb(10,10,10)` 正是 `bg-background`），上面一排平台的钮（模组、评论、往下、图、搜索）接预设小签，中间输入框，底下工具钮，预设不在块外头；回复底下一行左边两个数、右边一排小图标；滚到底时最后一条底下留约 140 的空；内容列比外壳正中偏右 7（宽屏，原因没查，手机上没量）。`w=3125 h=1150 sidebar=1 scroll=end` 跑出来跟真页面几乎重合。手机还没有真页面截图。

11-04 用户又发了手机截图以后给复刻台添的：平台给回复套的气泡（灰底、边框、内边距 16，卡要自己清掉）；手机（≤639）顶栏 48 高，main 还照 64 往上提，底下多出 16 露页面底色；static_bench.mjs 添 `theme=light`。上一回写的“内容列偏右 7”不是固定偏移，是气泡的内边距减去滚动条的一半，已经从 shell.css 拿掉。

11-04 大旻长夜大框搬奥尔德兰修法时添的两个 `eval=` 脚本（给 static_bench.mjs 用，认的是 dm- 类名）：eval_dmf_measure.js（量内容列、框下沿到输入栏、气泡、输入栏几层的底色，再把输入框往里多包两层、回复底下添一排带 bg- 类的钮，看选择器认不认得）；eval_dmf_tab.js（点玉牒页签进页。无头里动画时钟不走，等多久都停在转场开头，要把 DocumentTimeline 上的动画 finish() 掉，滚动时间线的不能动）。这里输入框是圆角块的直接孩子，比真页面浅，旧的 `:has(> textarea)` 在这里也认得到，所以光看图看不出输入栏的毛病。
