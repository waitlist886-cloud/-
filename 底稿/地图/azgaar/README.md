# 在 Azgaar 里画时代地图（11-08）

本机 Chrome 无头打开 Azgaar 网页版，调试协议从外面驱动：载 .map、改它画好的 SVG、按倍数截图。

1. 起 Chrome（一直开着，固定调试端口 9333）：
   `"C:/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --hide-scrollbars --no-first-run --remote-debugging-port=9333 --user-data-dir=<临时目录> --window-size=1920,1080 https://azgaar.github.io/Fantasy-Map-Generator/`
   页面卡死了（eval 二十秒没回话）就把这个 Chrome 整个停掉重起，再 az_reset.sh。
2. 载图、摆好、关掉1001年那几层：`bash az_reset.sh <奥尔德兰.map>`（.map 在用户电脑 Downloads，用 9 月 26 日 23:09 那份，带 AUL 那一层）。
3. 改：`node cdp.mjs file <脚本.js>`。脚本里能用的：Azgaar 挂在全局的只有 `pack`、`grid`、`options`、`styles`，别的函数都打包成模块了，所以直接改 SVG。要点：
   - Azgaar 的样式表里 `#lakes { mask: url(#water) }`，湖只在水遮罩里显示；陆地、生物群系、纹理照 `land` 遮罩露。
   - 湖分组画：`#freshwater`、`#salt`、`#frozen`、`#dry`、`#lava`、`#sinkhole`，挪一个 `<use href="#feature_N">` 换一种样子。
   - 海：`#oceanBase` 一块底色加 `#oceanLayers` 里几层半透明的白（`#ecf2f9`，0.13），越近岸叠得越多。海岸线是 `#sea_island` 给陆地轮廓描边。
   - 生物群系是 `#biomes` 里一个群系一条路径（`biome4` 草原 `#d3d8a8` 这些），整组透明度 0.6 叠在陆地底色 `#eef6fb` 上。换一片地的群系：照这个先铺陆地底色、再叠 0.6 的群系色（az_nanyuan.js），别去点图层按钮叫它重画，关了再开它不画回来。
   - 地形符号是 `#terrain` 里一个一个 `<use>`（这张图用 gray 那一套）。Azgaar 有时候会整层重画，单个符号上改的样式、藏起来的都会丢，所以藏符号的写成 `window.__…()`，截图以前再跑一回。
   - 页面坐标就是地图坐标（2200×1400，az_plain.js 摆的）。
4. 截图：`node cdp.mjs clip <输出.png> x y w h 倍数`（地图坐标）；整张大图 `python stitch.py <输出.jpg> <倍数> 2 2`（分四块截再拼，要 PIL）。拼对照图 `python sheet.py <输出.jpg> <宽> <列> "<标题>" 图1 "说明1" …`。
5. 月银纪·萨尔维斯末年样张：`PY=<带 PIL 的 python> bash build_moon_salvis.sh <.map> <输出.jpg> 1.6`。
   - az_biwan.js：今天赤盐内海那一整片水面是碧湾，加 BAY_D 那一道朝西南的口子（bay_shape.py 算的，碧湾_月银纪.path.txt），湖那一组里的藏掉海自己露出来；湾北边画盐原（盐壳）和盐沼。跑以前用 embed.py 把 BAY_D 塞进去。
   - az_nanyuan.js：神陨沙海那一大片沙地、双月内海的湖底和湖岸、两片当中那一圈冷荒漠，照草原画；南边离海三格以内的沙照旧。
   - az_salvis.js：城市平面（几道城墙一层套一层，墙里有田、有卫城，放射的大道，城心的宫）、穹都的上城、神渡上空的客星城、星坑盆地的坑沿、月银原、扛岛、三百二十座辉塔和圣荫、七曜锁在哪、空路、王道、地名、题签和比例尺。
6. 试验场：az_play3.js（1001年那张图上画巨城、长垒和大迷宫的圈、寒天之钉、星环、曜冠空环城、星落群岛、玻璃沙坡、黑曜环山、赤盐沉宫、黑潮螺旋城），AUL 那一层用 embed_aul.py 从 .map 存出来的 SVG 里抠。
7. Azgaar 自带的几样：
   - 比例尺：`options.map.units.distance.scale = 19; options.map.units.distance.unit = '公里'`，再点比例尺那个图层按钮，没出字就再点一下。
   - 罗盘：点 compass 图层按钮，左上角一个罗盘，海上拉出几道方位线。
   - 3D：点 `#viewGlobe`（整张图包成一颗星球）或 `#viewMesh`（3D 地形，从正上方看），`node cdp.mjs drag x1 y1 x2 y2` 拖着转、斜着看，等十几秒再截。3D 里那几个选项（`#options3dScaleRange` 高度、`#options3dErosion` 侵蚀、`#options3dTimeOfDay` 光）能改，侵蚀这台机器上无头算了十几分钟没出来，别开。
   - 纹章（emblems）无头里画出来是空的盾，没用。
8. 1001 年的海与水路试样（海与水路_方向稿.md）：`python embed_aul.py <.map 存出来的 svg> az_seas1001.js _run.js`，az_reset.sh 以后跑 _run.js。赤盐内海、双月内海顺着各自出海的那条河（176、568）开海门、湖那一组里藏掉改成海；深蓝海湾、北辰湾、镰月海（三点定圆、照弧长加厚的月牙）、白碑湾照中线加半宽切；凛河、灰契河、白碑河照 Azgaar 的河色画、沿中线横着摆出弯；黑耀运河、王道运河画成带闸口短线的双线；航路是虚线，进内海的那几条顺着海门的河道走。截图以前跑一回 `window.__seaHideIcons()`。
9. 月银纪的海与三河：az_seas_moon.js，在 az_nanyuan.js 之后、az_salvis.js 以前跑（build_moon_salvis.sh 已经接上）。镰月海、北辰湾、长船湾跟 1001 年同一个形，深蓝海湾那时候叫珠湾；凛河、烬河、吟河在神渡城当中汇流，汇成的那一条往南过南原，顺着往后双月海门那道旧河道入海。自己画的河别放进 `#rivers` 里头（Azgaar 会整层重画冲掉），放在它后面的兄弟层。
10. 纷争纪·炮的年月（约3600年）样张：`PY=<带 PIL 的 python> bash build_strife_mid.sh <.map> <输出.jpg> 1.6`（时代地图方向稿第十三节）。
   - az_salthai.js：在碧湾那一步之后跑。1088年整片盐原塌下去连上碧湾：先拿一个椭圆盖住盐原和盐原跟湾之间那一溜地，跟赤盐内海那一片湖并起来，在画布上模糊再取阈值把接缝抹圆，marching squares 描出新岸（y 1090 以南照湖原来的岸），西边留一个岬角（往后盐沼灯镇 286,1076 在岬角尖上）；碧湾那一步做的遮罩、岸线、浅色层都添上这一块，水往东北越来越红。新岸存在 `window.__saltD`，build 脚本写成 盐海_纷争纪.path.txt。
   - az_siyu.js：南界那一条线照脚本里的 SL 画（西头接盐海东南角，过墙的南头，东到落星洼东边），南界以北的南原照月银纪画草，以南是死域（北沿一溜灰绿、往里灰烂、几团暗影），冰盖（群系 11）不算；落星洼是干的洼地加一堆一堆的骨，往后双月内海北边那一片圆海画成浅坑的坑沿，河 568 藏掉画干河床。
   - az_seas_strife.js：照 az_seas_moon.js 改，镰刀湾、潮门的湾、北辰湾、长船湾，三河在墙下水门（1021,751）汇流，往南进了死域就断了；新水面和盐海都不让 Azgaar 的河露出来。
   - az_strife.js：长垒照 长垒_用户画.json（../参考/长垒_用户画.tsv 转的，跑以前用 embed.py 塞进 WALL_PTS），墙东段城、魔晶炮阵的紫光、北段中段南段、水门、盾碑、四十七骑门；墙后星纱轨（墙线往东偏 24 格）和三条支线、星环；巨城和营城照城市平面，七十二座高座（空了十六座，不落在冰盖上）；穹都废墟、赤原的土垒、墙前焦土、北辰塔、寒天之钉、潮歌的岛；地名、题签、比例尺。
11. 1001 年海与水路试样从头出：`PY=<带 PIL 的 python> bash build_seas1001.sh <.map> ../参考/AUL_用户画.svg <输出.jpg> 1.6`（第二个参数原来是 .map 存出来的整张 svg，AUL 那一组抠出来放在 参考/AUL_用户画.svg，塞进去一字不差）。盐海_纷争纪.path.txt 在就塞进 az_seas1001.js 的 SALT_D，赤盐内海连上纷争纪塌下去的那一片盐原；不在就照 Azgaar 原来的湖。
12. az_reset.sh 摆视口那一张截图写到 `$TMP/_az_vp.png`（原来写 ../azmap/，在仓库里跑会找不到目录）。
13. 纷争纪后段到山铜纪那一张：`PY=<带 PIL 的 python> bash build_late.sh <.map> <输出.jpg> futa|bronze 1.6`（时代地图方向稿第十四节）。futa 是纷争纪·浮塔的年月（约7000年），bronze 是山铜纪·麦的年月（约900年）。
   - 地貌那几步跟纷争纪中段共用，跑以前在页面上设几个开关：`window.__saltRedK`（盐海红几档，中段 1），`window.__siyuOpt = { sand, lake, SL, sandWash }`（sand 露出 Azgaar 那一片沙漠当沙海、北沿画玻璃平原，lake 'wet' 时落星洼照 Azgaar 的湖留着水，SL 换南界），`window.__fseaOpt = { river, bay }`（river 'lake' 时三河流进落星洼，bay 是潮门的湾那一处的叫法）。不设就是纷争纪中段的样子。
   - az_futa.js 是 make_futa.py 照 az_strife.js 改出来的，az_bronze.js 是 make_bronze.py 拼的（共用的那几段从 az_strife.js 切，山铜纪自己的在 az_bronze_body.js）。az_strife.js 改了以后两个都重跑一回。
   - 高座照 高座_纷争纪.json（build_strife_mid.sh 存的那七十二座），embed.py 塞进 SEATS。
14. 灰河分两条（11-08）：az_seas_strife.js 和 az_seas1001.js 把 Azgaar 原来那一条往南入海的 32（加支流 44）藏掉，炉城底下那一条照它的上游往西画进落星洼（纷争纪两张画到死域边上、往里是干河床，山铜纪和1001年流进水里）；墙西的灰河从灰高原当中往西南，到断岭北头接上 Azgaar 的 74。月银纪那一张照旧是 Azgaar 原来的 32（那时候还往南入海）。
15. 量陆地占多少：az_geo_stats.js（照 pack 的格子算，原图 66.2%）；新切的海不在格子里，算的时候拿 #seaProbes 里那几块形扣掉（11-08 那一回在页面上直接跑的，1001 年大一档加上盐原那一块是 62.8%）。
