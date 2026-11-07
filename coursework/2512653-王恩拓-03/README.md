# 个人学习档案页 第三次实训

## 基本信息

- 姓名：王恩拓
- 学号：2512653
- 班级：软件工程 2025 级 4 班
- 课程：前端开发实训

本项目基于第一次作业 `2512653-王恩拓-html-structure` 的页面升级，保留个人简介、学习方式、学习计划表格与列表、留言表单、头像和学习提醒。原作业不覆盖，第三次作业单独存放。

## 打开方式与文件结构

直接用 Chrome 打开 `index.html`，无需安装依赖，断网也能浏览。

```text
2512653-王恩拓-03/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── main.js
├── assets/
│   └── profile.jpg
└── README.md
```

`main.js` 只负责本地表单验证与提交提示。表单没有后端，不会发送或保存留言；刷新后提示消失。浏览器原生 `required` 验证和 label 关联仍保留。

## Flex 与 Grid 容器

| 容器 | 布局 | 控制的项目与作用 |
| --- | --- | --- |
| `.header-inner` | Flex | 标题身份区与导航；桌面端左右分布，`justify-content: space-between` 分配剩余空间，`align-items: center` 沿交叉轴对齐 |
| `.site-nav` | Flex | 四个内部导航链接；`gap` 设置间距，`flex-wrap: wrap` 允许换行 |
| `.form-row` | Flex | 称呼和关注方向；桌面横排，小屏纵排 |
| `.site-footer` | Flex | 作者、课程与日期；空间不足自动换行 |
| `.page-layout` | Grid | 主内容列与 260px 侧栏；轨道为 `minmax(0, 1fr) 260px`，栏间距 24px |
| `.skill-list` | Grid | 六张技能卡片；使用 `repeat(auto-fit, minmax(180px, 1fr))`，重点卡片跨两列 |

Flex 适合沿一个方向排列标题和导航，项目之间可灵活分配空余空间，不必预先指定列轨道。主体需要明确的主栏与侧栏，技能卡片需要二维轨道和跨列，因此使用 Grid。

### 技能卡片的三个关键属性

- `auto-fit` 根据容器宽度决定能容纳多少列；没有内容占用的多余列会折叠。
- `minmax(180px, 1fr)` 让每列最小 180px，剩余空间按相同 `fr` 比例分配；`repeat()` 生成重复轨道。
- `.featured-skill` 的 `grid-column: span 2` 让 Flexbox 重点卡片跨两列。小屏时改为 `auto`，避免单列布局仍强行跨列。

## 响应式断点

选择 `768px`。桌面主体除了 260px 侧栏，还需要两侧留白、24px 栏间距，以及足够的正文宽度；继续压缩双栏会影响阅读，因此在该宽度及以下改为单栏。

小屏页头改为纵向，导航仍允许换行；主体依次显示简介、技能、学习计划、表单、侧栏；表单短控件改成纵排。图片使用 `max-width: 100%`，表格固定轨道并允许单元格文字换行。没有通过隐藏内容适配手机。

在 375px 屏幕上，技能卡片可用区域约为 305px，适合单列；在 1200px 屏幕上，主栏技能区域约为 706px，适合三列。最终以浏览器实际显示为准。

## 调试问题与修正

代码检查中发现：原作业 README 记录的头像路径是 `assets/profile.svg`，实际 HTML 和素材却是 `assets/profile.jpg`。本次统一采用真实存在的 JPG 文件，修正说明，避免按说明迁移时引用不存在的文件。

另一个布局风险是重点卡片的 `span 2`：当手机只容得下一列时，如果仍保留跨两列，Grid 可能生成隐式列而引起溢出。本次在 768px 媒体查询内改为 `grid-column: auto`；主内容采用 `minmax(0, 1fr)` 和 `min-width: 0` 允许正确收缩。

## 可访问性与状态

- 保留 `header`、`nav`、`main`、`section`、`aside`、`footer`，页面语言为 `zh-CN`。
- 内部导航分别指向四个 section，section 的 `aria-labelledby` 对应标题 id。
- 图片保留 alt；学习表格保留 caption、thead 和 th 的 scope。
- 所有表单控件都有对应 label；按钮为 `type="submit"`。
- 提供跳到主要内容链接、键盘焦点边框、链接和按钮悬停状态。
- 表单提示使用 `role="status"`；动态文字用 `textContent` 输出。

## 检查记录与开发者工具练习

已进行文件与静态代码核对：相对资源路径、导航锚点、label/id、语义结构、技能数量、Flex/Grid 与媒体查询均已检查；脚本通过语法检查。原始作业文件未修改。

当前工具的浏览器未能连接本机预览服务，因此未将 375px / 1200px 的浏览器渲染、控制台检查和布局标记操作记录为已完成。提交前请在本机 Chrome 完成以下课程练习：

1. 打开 `index.html`，按 F12。在 Elements 中选中 `.header-inner`，点击 flex 标记显示布局辅助线。临时切换 `justify-content` 为 `center` 或 `flex-start`，观察水平分配；切换 `align-items`，观察交叉轴对齐。
2. 选中 `.page-layout` 和 `.skill-list`，点击 grid 标记。临时修改主体轨道为 `1fr 1fr`，观察侧栏变化；修改后取消临时样式，保留原文件。
3. 打开设备工具栏，分别设置约 1200px 和 375px 宽度。确认桌面双栏、手机单栏，导航可换行，手机重点卡片不再跨列；检查页尾与表单，确认无横向溢出或遮挡。
4. 点击四个导航链接，展开学习方式；确认头像正常显示，Tab 能依次到达链接和控件，焦点清晰。
5. 空称呼提交应触发必填提示；输入称呼后提交，应出现本地演示提示且不跳转、不发送。只填空格时应提示重新输入。
6. 在 Console 检查脚本错误，在 Network 检查 CSS、JS、JPG 是否成功加载。

## CSS 与 ArkUI 迁移对照

以下按课程提供的对应关系说明布局思维。实际 ArkUI 工程还需按所用 SDK 和组件 API 调整；本次不要求转换整个网页。

| Web CSS | HarmonyOS ArkUI | 迁移说明 |
| --- | --- | --- |
| `display: flex` | `Row()` 或 `Column()` | 水平组织项目用 Row，垂直组织项目用 Column；对应 CSS 的主轴方向选择 |
| `justify-content` | `.justifyContent(...)` | 控制主轴上的子项分布，例如页头两端排列可对应 SpaceBetween 思路 |
| `align-items` | `.alignItems(...)` | 控制交叉轴对齐；Row 的交叉轴为竖向，Column 的交叉轴为横向，需按容器选择合适枚举 |
| `gap` | `Row({ space: ... })` | 将项目之间的间隔迁移为容器的 space；竖向排列也应在相应 Column 容器中设置间距 |
| `flex: 1` | `.layoutWeight(1)` | 将子项分配剩余空间的思路迁移为布局权重；不表示 flex 简写的增长、收缩和基础尺寸完全等价 |
| `display: grid` | `Grid()` + `GridItem()` | 外层定义网格，子项放进 GridItem；需要分别考虑轨道与项目占用位置 |
| `repeat(3, 1fr)` | `.columnsTemplate('1fr 1fr 1fr')` | 三列使用相同分数单位，按相同比例分配可用列空间 |
| `column-gap / row-gap` | `.columnsGap() / .rowsGap()` | 分别迁移列间距和行间距，统一卡片排列节奏 |

CSS 的 `auto-fit` 与媒体查询不是简单替换为固定三列模板；迁移时还需结合 ArkUI 可用宽度与断点策略改变轨道和排列方向。

## 参考资料与 AI 使用说明

- 参考资料：本次《CSS 现代布局：Flexbox 与 Grid》作业文档、第一次个人学习档案页源码及 README。
- AI 工具：使用 Codex 读取任务与原项目，协助改写 HTML、生成外部 CSS、实现本地表单提示、编写 README 并进行静态检查。代码和说明均有 AI 辅助，不宣称全部由本人独立编写。
- 姓名、学号、班级和头像沿用原作业；技能状态按实训内容描述，ArkUI 和 JavaScript 进阶标为后续学习内容。
