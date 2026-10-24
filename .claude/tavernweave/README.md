# TavernWeave 在这个仓库里装了什么

2026-10-24 装的。来源 https://github.com/LiarMTTT/TavernWeave ，版本 2.3.5，提交 d134ddd69f941e2320160101315d760a631bfa65。

用户只要写作相关的部分，不把这张卡转成 Tavern 的格式。所以 23 个 Skill 里只装了三个，原样复制进 `.claude/skills/`，一个字没改：

| Skill | 为什么装 |
|---|---|
| rewrite-natural-prose | 文本精修，洗稿、去 AI 味、去八股。10-20 润色那一轮用的就是它 |
| worldbook-design-and-writing | 世界书正文的写法。它的加载和配置那一半照 SillyTavern 写，这张卡是日里的，加载、触发、打包照 rili-card-studio 和本仓库 CLAUDE.md |
| consult-tavernweave-library | 上面两个的依赖。两个 Skill 入口都要读它的大白话规则和云端执行合同，写文件以前走它的 A0 检查。里面另有 SillyTavern 指南和前端设计库，用不上的不读 |

没装的二十个：tavern-card-builder 和 sillytavern-* 那一批是转 Tavern 格式和酒馆运行时的；build-work-library、orchestrate-project-blueprint、activate-tavernweave-soul、reflect-on-vibe-code-growth、code-quality-workflow、shadcn-tailwind-ui、rolecard-workshop-ops 不是写作。三个 Skill 里指到这些的链接是交接给它们的，留着不通，属正常。

没做的：
- Host Front Door 没写。它是给全部 23 个 Skill 的路由表，会把接手卡、续更送进 tavern-card-builder；云端容器的 `~/.claude/CLAUDE.md` 换容器就没了；10-20 用户也说过这条全局规则先不写。
- 洗稿的持续模式、工作区和客户端持久模式都没开，装上不等于开。
- 引导挡位没设。

许可证是 PolyForm Noncommercial 1.0.0，原文和第三方声明在本目录，非商业使用、修改、分发都行，商业用途要另找版权方。

核验：`install-receipt.json` 记着每个文件的 SHA-256。更新的时候先把新版本克隆到临时目录，再在仓库根上跑

```
python3 -I tools/verify_tavernweave.py <新克隆的目录> .claude/skills .claude/tavernweave/install-receipt.json rewrite-natural-prose worldbook-design-and-writing consult-tavernweave-library
```

旧目录先换成新版本的三个目录（整目录替换，不在里面改字），跑出来三个都是 identical、required paths 全在、library-manifest 的哈希全对，才算装对。
