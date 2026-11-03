# 状态栏美术 · 接用户电脑上的 ComfyUI 出图（11-03 起）

照状态栏美化方向稿第四版第七节、第九节第5条出大框两侧的画，先出迷宫纪 1001 年那一套（用户的电脑端构想图当风格参照）。

## 怎么接

这个会话跑在云端，连不到用户电脑上的 127.0.0.1:8188。用户在电脑上建一个文件夹（11-03 建议桌面上的 `aldran_art`），在 Claude 桌面版 设置 → Claude Code → Remote Control 里加进去，或者在那个文件夹里跑 `claude remote-control`。这边 list_computer_folders 看得到以后，request_computer_folder 请求连，用户点允许，连上以后命令在用户电脑上那个文件夹里跑。

## 这一份的文件

- comfy_run.py：出图脚本，只用标准库，画底稿和收图用 Pillow（ComfyUI 自带的 python 就有）。
  - `python comfy_run.py probe`：查系统、显卡显存、装了哪些模型和节点，写 probe.json、object_info.json。
  - `python comfy_run.py sketch maze1001`：画构图底稿，彩色那一张给图生图打底，线稿给 ControlNet。
  - `python comfy_run.py run plan_maze1001.json [--only left] [--seeds 11,22] [--dry]`：照计划出图，图、WebP 和工作流写 out/<套>/<件>/，每件拼一张小样 _sheet.jpg。
  - 节点入参照 /object_info 补默认值，ComfyUI 版本不同多出来的必填项也跑得起来。SDXL 一路（底模、区域提示、ControlNet、IPAdapter、高清修复）和 Flux 一路（UNET、双 CLIP、FluxGuidance、图生图）都写了，用哪一路看 probe。
- plan_maze1001.json：左右两扇的提示词、区域提示（七支柱照底卡 #86 到 #92 显相，双王照底卡）、尺寸（出 704×1408，高清修复到 1000×2000）、种子。config 一栏等 probe 以后照用户装的模型填。
- sketches/maze1001/：构图底稿，左扇是大迷宫一圈一圈往下的井和城、井底的影子（不画脸）、黑日、崖边一个旅人；右扇是七支柱各一圈圆光、底下双王、再往下阿卡迪亚和空艇。左扇左边是外侧、右边贴窗，右扇反过来。
- refs/：用户构想图裁的左右两半，缩到 768 高，给 IPAdapter 当风格参照。

## 画的规矩（方向稿第四版第九节）

- 两扇压在对话上面，靠窗那一边七十像素上下给花边切，要紧的人和物别贴着那一边，上下各一成给裁。
- 宽屏上两扇按 cover 裁，窄一点的屏幕裁掉的是外侧，所以要紧的东西偏窗那一边、离窗边七十像素以外。
- 全彩不抠底，暗面偏紫、亮面偏金，金线勾边。提示词里不写月相（反面提示词里写了 crescent moon、moon phases）。
- 七支柱不画成构想图那几处：欧巴德斯半身不朽石躯、山脉鳞层的翼，库米罗妮一百四十二公分、幼鹿角，伊兹帕鲁特翼里火焰冰雾雷光，朱亚头顶细小羽翼、翠玉眼，耶万朴素长袍。艾赫卡托尔先画她本人带着黑猫（用户还没定）。
- 出的图换掉大框样式里的 `__ART__/maze_left.webp`、`maze_right.webp`。
