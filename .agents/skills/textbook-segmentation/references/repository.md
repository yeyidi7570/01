# 仓库与已有 V4 实例

- GitHub 为 [yeyidi7570/01](https://github.com/yeyidi7570/01)。项目说明在 [structured_textbooks/README.md](../../../../structured_textbooks/README.md)。书名使用 `书名年份_x语学生_x语教材（年级-分册）_出版社`，书之间无额外分类层。
- 先调研 Git 已有的 `wiki-data/`、`experiments/`、目标书 README、书级 `tools/` 与 01–06 阶段目录。可用稀疏检出或从已追踪 Git 对象读取必要源文件，避免下载或复制全书原始资料。实际缺失的来源如实报告。
- V4 参考书为 `数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП`。书 README 记录 PDF、印刷页、40 课目录与归档状态。第 1 课覆盖 PDF/印刷 7–10 页，第 2 课从第 11 页开始且标题相同，第 4–5 页是使用指南。任务抽样和历史跨页示例位于 `experiments/`，可用于判断版式，不能当作其他课的识别结果。
- 该书 `01_segmentation/lesson_001/` 是三件套参考。顶层的 `review_zh.html` 和 `review_kk.html` 提供正式连续问卷入口，共享待人工审核的数据。默认对新课提供连续模式。仅更新界面时可直接复用已核对的数据与内嵌资产。

## 调用示例

```text
$textbook-segmentation 教材「数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП」，课次 2，重跑 否。
$textbook-segmentation 教材「数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП」，课次 5–8，重跑 否。
$textbook-segmentation 教材「数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП」，课次 1，重跑 是，保留原审核反馈与旧版，核对新旧对象 ID。
```
