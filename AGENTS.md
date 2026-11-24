# 结构化教材项目

- 仓库为 `yeyidi7570/01`。工作前核对当前 Git 检出、远程分支和未提交改动。优先复用现有检出。
- 项目约定见 [structured_textbooks/README.md](structured_textbooks/README.md)。每本书使用完整教材目录名，每课用原书课号 `lesson_XXX`。
- 处理教材视觉切割、初始 JSON 或双语离线审核页时，加载 [$textbook-segmentation](.agents/skills/textbook-segmentation/SKILL.md)。明确本次教材、课次与重跑范围，逐课核验和归档。查看仓库或维护 Skill 时按当次任务范围执行。
- 原始 PDF、扫描、OCR、校对、Wiki、历史实验和人工反馈保留在原路径。待审数据、第一轮内容审核和后续语义标签遵守各阶段目录约定。
- 发布时只暂存任务相关文件。验证远程提交和文件后再报告已推送。
