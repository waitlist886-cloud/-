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
