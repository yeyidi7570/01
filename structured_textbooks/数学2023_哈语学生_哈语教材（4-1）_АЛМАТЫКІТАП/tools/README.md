# 第一课 V4 生成工具

[v4](v4/) 保存原始 V4 的结构化数据和单对象审核界面生成代码。[review_continuous](review_continuous/) 保存后续连续问卷界面的代码。两套工具共享同一 V4 教材内容和历史来源。

## 复用原始 V4 生成程序

需要 Python 3.9 或更新版本、Pillow，以及包含来源提交的 Git 检出。现有产物以 Pillow 13.0.0 生成。程序从已记录的结构判断、源扫描和 OCR 证据装配产物。

将 [source_manifest.json](v4/source_manifest.json) 中 `paths` 的输入以映射键名放入临时输入目录。内容从 `revision` 对应的 Git 文件读取，例如使用 `git show "<revision>:<path>"`。将 `tree.json` 和 `sources.json` 按以下格式写入同一输入目录。

- `tree.json` 包含 `sha` 和 `tree`。将 `revision` 填入 `sha`，`tree` 至少包含一个对象，其 `path` 等于 `original_pdf`。
- `sources.json` 使用清单中的 `paths` 对象。键为 `book.pdf` 的条目用于记录 PDF 来源路径。

向 `lesson.py` 传入临时输入目录与已创建的输出目录。程序会写出 `math_grade4_lesson1_structured_v4.json` 和两个原始命名的审核 HTML，归档文件名对应为 `content.json`、`review_zh.html` 和 `review_kk.html`。

## 复用连续问卷界面生成程序

在临时工作目录中以原始命名放置两个 V4 审核 HTML。将 [review_continuous](review_continuous/) 下的四份工具文件复制到该临时目录的 `scratch/review_continuous/`，运行其中的 `build.py`。程序沿用 V4 内嵌数据和图像，并在临时工作目录写出两个 `_v4_continuous.html`。正式审核入口为 [中文连续审核](../01_segmentation/lesson_001/review_zh.html) 和 [哈语连续审核](../01_segmentation/lesson_001/review_kk.html)。
