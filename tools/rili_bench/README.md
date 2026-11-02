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
