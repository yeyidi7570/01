---
name: textbook-segmentation
description: 对指定教材的单课、课次范围或整册逐课执行原书视觉切割、哈语 OCR 校对建议、结构化 JSON 和中哈双语离线连续问卷审核，并验证及归档到 GitHub。用于新课切割、复用已有切割或保护人工反馈的重跑。主观教学标签、习题或答案生成属于其他阶段。
---

# 教材逐课切割与归档

## 输入和范围

- 接受 `book`（仓库中的完整教材目录名）、`lessons`（正整数、闭区间、逗号列表或显式 `all`）、`rerun`（默认否）。课号是原书真实顺序。省略课号时先做只读盘点，范围不能从上下文确定时再确认。只有用户指定全册时才用 `all`。
- 使用仓库根目录的 Git 检出。默认仓库是 `yeyidi7570/01`。按用户指定的仓库和分支执行，核对远程后复用已有检出；只暂存本次文件。保留原始 PDF、扫描、OCR、校对、Wiki、历史实验及人工反馈。
- 交付限于第一阶段切割。KLP、Difficulty、Question Type、习题/答案生成、正式已审核内容及最终知识库属于后续流程。
- 若本次任务只是创建、安装、列出、预览或验证 Skill，只做对应的只读或合成验证。加载 Skill 本身不启动教材处理。

## 执行

1. **盘点来源和课次。** 检查 `git status`、remote、当前和远程分支，读取 `structured_textbooks/README.md` 与目标书 README。查找仓库实有的原始 PDF/原图、原始及最终校对 OCR、版面、Wiki、既有切割和通用脚本。以原书目录、课号、标题、页眉和相邻页确认边界，分别记录 PDF 一基页码和印刷页码。目录与正文冲突时保留证据并标待核，不能猜补。阅读 [内容规则](references/content.md)。
2. **确定复用或重跑。** 按 [脚本接口](references/tools.md) 运行 `scripts/lesson.py plan`。按课号排序，一次完成一课再进入下一课。有效的既有数据直接复用，只有界面过时时可保留数据升级界面。缺文件先查可复用来源；遇到身份或版本冲突，按 [重跑与归档](references/publish.md) 暂存候选版并处理。显式 `rerun` 也须保护反馈。
3. **视觉核对和结构化。** 优先把现有 OCR 与原图对齐；只为缺失或不可靠的区域补识别。保留 Lesson、Module、独立 Instructional Note、子题、Badge、元素阅读顺序、跨页、页坐标、教学证据和不确定项。按 [内容规则](references/content.md) 在临时目录生成或复用统一的待审核 JSON，并单独准备对应的中文辅助翻译。检查图、表和公式的二维结构。
4. **生成离线审核页。** 复用适用的仓库脚本；需要通用装配时使用 `scripts/lesson.py render` 和随 Skill 提供的连续问卷 UI。两个语言版由同一数据、资源和逻辑生成。按 [双语审核](references/review.md) 检查翻译、卡片、审核状态与导入导出。
5. **验证和归档。** 运行 `scripts/lesson.py check`，对照原图人工走查，并实际用断网浏览器测试两个语言版本。仅将通过检查的 `content.json`、`review_zh.html`、`review_kk.html` 放入 `structured_textbooks/<完整教材名称>/01_segmentation/lesson_XXX/`。填写该书 README 的真实进度。按 [重跑与归档](references/publish.md) 提交、非强推推送并验证 GitHub 上的提交及文件。推送受阻则区分本地完成和远程交付，报告具体情况。
6. **逐课报告。** 给出真实课号、标题、PDF 与印刷页、Module/Note/OCR 建议数量、主要疑点、三个远程路径、Commit SHA、分支和推送结果。范围任务汇总真实完成与剩余课次。切割完成状态与人工验收状态分别记录。

[仓库及 V4 参考案例](references/repository.md) 提供目录入口、历史实现和调用示例。案例数据不能充当新课模板输入或审核完成凭证。
