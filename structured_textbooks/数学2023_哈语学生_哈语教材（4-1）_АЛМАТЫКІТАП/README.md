# 数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП

《Математика》四年级第 1 册，2023 年，哈萨克语西里尔文，出版方为 АЛМАТЫКІТАП БАСПАСЫ。

## 来源

以下链接指向仓库中的现有资料。Lesson 001 使用的源版本为 `ee2c52c10ef09958cd0a8563d343b41870bbf9e1`，具体页码、坐标及哈希记录在 [content.json](01_segmentation/lesson_001/content.json) 中。

- [原始教材 PDF](../../wiki-data/数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП_数据/来源/数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП.pdf)
- [带 OCR 文字层的 PDF](../../数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП_OCR.pdf)
- [页面原图](../../wiki-data/数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП_数据/来源/页面原图/)
- [逐页原始 OCR](../../wiki-data/数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП_数据/逐页数据/原始OCR/)
- [逐页最终校对 OCR](../../wiki-data/数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП_数据/逐页数据/最终校对/)
- [逐页版面分析](../../wiki-data/数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП_数据/逐页数据/版面分析/)
- [Wiki 数据](../../wiki-data/数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП_数据/数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП_Wiki.json)
- [历史切割实验](../../experiments/module_internal_visual_experiment/)

## 当前进度

| Lesson | 切割 | 内容审核 | 主观标签 | 标签审核 | 最终完成 |
| --- | --- | --- | --- | --- | --- |
| [lesson_001](01_segmentation/lesson_001/) | 已归档 V4，`pending_review` | 待审核 | 未开始 | 未开始 | 未完成 |
| [lesson_002](01_segmentation/lesson_002/) | `segmentation_completed` | `pending_review` | 未开始 | 未开始 | 未完成 |
| [lesson_003](01_segmentation/lesson_003/) | `segmentation_completed` | `pending_review` | 未开始 | 未开始 | 未完成 |
| lesson_004–lesson_040 | 本项目尚未归档 | 未开始 | 未开始 | 未开始 | 未完成 |

第 1 课 `3-сыныпта өткенді қайталау` 覆盖 PDF 第 7–10 页，对应印刷第 7–10 页。第 2 课从第 11 页开始，标题相同。教材按课号区分两课。

第一课标准入口为 [结构化 JSON](01_segmentation/lesson_001/content.json)、[中文审核 HTML](01_segmentation/lesson_001/review_zh.html) 和 [哈语审核 HTML](01_segmentation/lesson_001/review_kk.html)。两份标准 HTML 使用 V4 原始的单对象审核界面。后续的 [连续问卷界面](01_segmentation/lesson_001/variants/continuous/) 是同一份内容的双语界面变体，沿用原切割坐标、对象 ID 和审核记录格式。

第 2 课 `3-сыныпта өткенді қайталау` 以 `ЭКСПО-2017` 为情境，覆盖 PDF 和印刷第 11–13 页。第 14 页是第 3 课。保留 9 个 Module、1 个独立教学说明 `ОСЫЛАЙ ТАЛДА!`、6 个 Module Badge、2 幅信息性天平图、24 个公式对象、1 条支持关联和 27 条校对建议，其中 22 条为字符或排版建议，5 条为结构建议。建议人工复核第 4 题的变量字形、第 5 题的天平标注和第 9 题的右边框。子题的原书小写标记与大写索引并存。

第 2 课入口为 [结构化 JSON](01_segmentation/lesson_002/content.json)、[中文连续审核](01_segmentation/lesson_002/review_zh.html) 和 [哈语连续审核](01_segmentation/lesson_002/review_kk.html)。双语页面已通过断网交互及审核记录交叉导入测试。归档提交可查该课路径的 Git 历史。

第 3 课 `Көптаңбалы сандар. Сандардың реті` 以 `Қазақстан сандармен` 为情境，覆盖 PDF 和印刷第 14–17 页。第 18 页是第 4 课。保留 10 个 Module、3 条独立教学说明 `ЕСІҢДЕ САҚТА!`、5 个 Module Badge、1 张数位表、2 幅信息图、7 个公式对象、7 条教学关联和 35 条校对建议，其中 33 条为字符或排版建议，2 条为结构建议。

第 3 课入口为 [结构化 JSON](01_segmentation/lesson_003/content.json)、[中文连续审核](01_segmentation/lesson_003/review_zh.html) 和 [哈语连续审核](01_segmentation/lesson_003/review_kk.html)。数位表保留 3 个跨列标题和 17 个原印空白格。优先复核第 10 题统计图的学校数与学位数系列，另核对第 8 题是否引用第 7 题，以及 10Ә 是否承接 10А 的学位数系列。双语页面已通过断网测试及审核记录交叉导入，提交可查该课路径的 Git 历史。

[项目总览](../README.md) 说明六个阶段的文件用途。[工具目录](tools/README.md) 保存两种界面的生成代码与来源清单。其余阶段随实际审核、校正和标注推进时归档。

## 课程起页

教材目录位于原始 PDF 第 149–150 页，列出 40 课。下表记录目录起页，印刷页码与本 PDF 的一基页序一致。切割边界已核对第 1–3 课。

| Lesson | 印刷及 PDF 起页 |
| --- | ---: |
| lesson_001 | 7 |
| lesson_002 | 11 |
| lesson_003 | 14 |
| lesson_004 | 18 |
| lesson_005 | 22 |
| lesson_006 | 26 |
| lesson_007 | 29 |
| lesson_008 | 33 |
| lesson_009 | 36 |
| lesson_010 | 40 |
| lesson_011 | 44 |
| lesson_012 | 48 |
| lesson_013 | 52 |
| lesson_014 | 56 |
| lesson_015 | 60 |
| lesson_016 | 63 |
| lesson_017 | 66 |
| lesson_018 | 69 |
| lesson_019 | 73 |
| lesson_020 | 77 |
| lesson_021 | 81 |
| lesson_022 | 85 |
| lesson_023 | 89 |
| lesson_024 | 92 |
| lesson_025 | 95 |
| lesson_026 | 99 |
| lesson_027 | 102 |
| lesson_028 | 105 |
| lesson_029 | 108 |
| lesson_030 | 111 |
| lesson_031 | 114 |
| lesson_032 | 118 |
| lesson_033 | 121 |
| lesson_034 | 124 |
| lesson_035 | 127 |
| lesson_036 | 130 |
| lesson_037 | 134 |
| lesson_038 | 137 |
| lesson_039 | 140 |
| lesson_040 | 142 |
