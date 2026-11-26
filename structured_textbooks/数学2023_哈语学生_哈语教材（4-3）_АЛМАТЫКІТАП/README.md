# 数学2023_哈语学生_哈语教材（4-3）_АЛМАТЫКІТАП

四年级哈萨克语数学第三册，АЛМАТЫКІТАП БАСПАСЫ，2023 年。

## 来源与复用

- 原始 PDF 和仓库校对后的可搜索 PDF 均为 160 页。已核对两个文件的页数与 SHA-256，哈希与本册 Wiki 的来源记录一致。第一课以仓库的页面原图为视觉依据。[原始 PDF](../../wiki-data/数学2023_哈语学生_哈语教材（4-3）_АЛМАТЫКІТАП_数据/来源/数学2023_哈语学生_哈语教材（4-3）_АЛМАТЫКІТАП.pdf) · [OCR PDF](../../数学2023_哈语学生_哈语教材（4-3）_АЛМАТЫКІТАП_OCR.pdf) · [160 张原图](../../wiki-data/数学2023_哈语学生_哈语教材（4-3）_АЛМАТЫКІТАП_数据/来源/页面原图/) · [原 PDF 文字层](../../wiki-data/数学2023_哈语学生_哈语教材（4-3）_АЛМАТЫКІТАП_数据/来源/原PDF文字层/)
- 仓库保存全册原始 OCR、两轮校对、最终校对和版面分析，每类有整册和 160 份逐页数据。另有 1,205 个 PDF 插图和 212 个版面裁剪。Wiki 的题目、表格和阅读顺序为自动候选。第 81 课使用逐页 OCR、最终校对和 Wiki 辅助定位，再逐区对照原图。[整册来源目录](../../wiki-data/数学2023_哈语学生_哈语教材（4-3）_АЛМАТЫКІТАП_数据/) · [Wiki](../../wiki-data/数学2023_哈语学生_哈语教材（4-3）_АЛМАТЫКІТАП_数据/数学2023_哈语学生_哈语教材（4-3）_АЛМАТЫКІТАП_Wiki.json)
- 切割前未发现第三册的已归档结构化切割或审核反馈。第 81 课复用仓库共用脚本和连续问卷模板，第一册的 V4 产物仅作格式参考。[共用 Skill](../../.agents/skills/textbook-segmentation/SKILL.md) · [第一册参考](../数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП/)

## 第 81 课

**Шамалар арасындағы тәуелділікке есептер шығару. Дөңгелек диаграмма**（解答有关量之间关系的应用题。饼图）

PDF 一基页码与印刷页码均为 5–8。第 159 页目录列出第 81 课从第 5 页开始，第 82 课从第 9 页开始。第 6、8 页的延续页眉印有“81-сабақ”，第 7 页延续主题和题号。第 1–2、3、4–6、7–10 题分别在 PDF 第 5、6、7、8 页。每道编号题均在本页结束；第 6 页的饼图定义对第 7 页第 4–6 题的支持关系已记录。

| 切割进度 | 人工审核 | Module | Instructional Note | 子题 | 表格 | OCR 建议 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `segmentation_completed` | `pending_review` | 10 | 1 | 8 | 2 | 72 |

[content.json](01_segmentation/lesson_081/content.json) · [中文审核页](01_segmentation/lesson_081/review_zh.html) · [哈语审核页](01_segmentation/lesson_081/review_kk.html)

静态校验和教学关联单元测试已通过。中哈两版均在断网 Chromium 中通过原图切框定位、表格反馈、教学关联方向校验、遗漏框选、草稿恢复和审核记录交叉导入导出测试。系统策略拦截 `file://`，实测由本地拦截提供同一 HTML 文件，测试期间没有外部网络请求。

### 初始切割的待核记录

- 第 5 题乳品饼图有八个等大的扇区。两块各占八分之一的黄色、蓝色扇区没有印产品标签，数据保留两块的颜色和位置，产品对应留待核对。该题同一胶囊中的两项标签各自可审核，作用范围均为第 5 题。
- 第 7 题的 12 道口算保留原 4 行 3 列的裁图和各算式坐标。原书未指定读序，审核卡暂按行从左到右。第 9 题按印刷子题标签 а)、ә)、б)、в) 的顺序排列，保留原来的两栏裁图。
- 第 8 页页末“ОЙЛАСТЫР / ОЙЫҢМЕН БӨЛІС / ҰСЫН”暂列为课末 Other，请核对它是否只作用于第 10 题。
- 第 6 页“ЕСІҢЕ ТҮСІР!”回顾区按现行规则归入 Other。现有 `supports` 要求起点属于 Instructional Note，因此没有把回顾区与速度、面积或价量问题的概念对应登记为 `supports`。六个关系三角图的上下格、两处除号、乘点、下标和说明随原图保留在 `structured_description`。现有审核模板通过裁图和结构说明展示这类三角图及饼图，其专用图形结构没有独立的二维编辑器。

### 第一轮审核修订 1

本次修订待复核，共 10 个 Module、2 个 Instructional Note、8 个子题、2 张表和 72 条 OCR 建议。PDF 和印刷页码仍为 5–8。原始导出按字节归档，111 项有效通过状态已沿用，含 4 页完整性审核。

第 6 页“ЕСІҢЕ ТҮСІР!”回顾区改列独立说明，新增其数量关系图对第 3、6、8、10 题的支持。第 5 题的乳品图仍在题内，已移除指向该图的材料引用；第 4 题对天气图的直接引用及饼图定义对第 4–6 题的支持继续保留。新版 7 项待复核包括回顾区结构与标签、4 条新增关系及初版未审核的第 5 页主题。

[修订 JSON](02_segmentation_review/lesson_081/revision_1/content.json) · [新版中文审核页](02_segmentation_review/lesson_081/revision_1/review_zh.html) · [新版哈语审核页](02_segmentation_review/lesson_081/revision_1/review_kk.html) · [修订日志](02_segmentation_review/lesson_081/revision_1/change_log.md) · [原始审核记录](02_segmentation_review/lesson_081/submissions/review_001_original.json)

### 第一轮审核修订 2

按跨 Module 材料引用规则移除了第 4 题指向题内天气图的关联。天气图、图例、结构化描述和全部 7 条 `supports` 保留。新版继承 110 项有效通过（含 4 页切割完整性），继续待审核 7 项。被删除关联的旧通过记录留在原审核历史中。

[修订 JSON](02_segmentation_review/lesson_081/revision_2/content.json) · [新版中文审核页](02_segmentation_review/lesson_081/revision_2/review_zh.html) · [新版哈语审核页](02_segmentation_review/lesson_081/revision_2/review_kk.html) · [修订日志与历史影响范围](02_segmentation_review/lesson_081/revision_2/change_log.md)

### 第一轮审核修订 3

按图片必要性规则核对第 81 课。第 1 题图保留词语和算式配对，裁图聚焦必要区域。第 4 题天气图和六幅回顾三角图保留。第 5 题无标签作图参考和重复课题的吉祥物文字已从结构化数据移除，完整原扫描和 OCR 来源保留。新版保留 8 个必要图示和 71 条 OCR 建议，继承 107 项通过，尚有 8 项待审核。

[修订 JSON](02_segmentation_review/lesson_081/revision_3/content.json) · [新版中文审核页](02_segmentation_review/lesson_081/revision_3/review_zh.html) · [新版哈语审核页](02_segmentation_review/lesson_081/revision_3/review_kk.html) · [修订日志](02_segmentation_review/lesson_081/revision_3/change_log.md)

## 第 82 课

**Түсімділік**（单位面积产量）。PDF 一基页码与印刷页码均为 9–11。第 159 页目录列出第 82 课从第 9 页开始，第 83 课从第 12 页开始。第 10 页延续页眉印有“82-сабақ”，第 11 页延续主题并以第 9 题家庭作业收尾。第 83 课标题相同，按原书课号和主题区分。第 1–3、4–5、6–9 题分别在第 9、10、11 页，各 Module 在本页结束。

| 切割进度 | 人工审核 | Module | Instructional Note | 子题 | 表格 | OCR 建议 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `segmentation_completed` | `pending_review` | 9 | 1 | 2 | 2 | 56 |

保留第 1 题五组算式与字母的配对、第 2 题复合单位和括号、第 5 题两层表头与左上跨两行的关系图、第 6 题三个作答空格，以及原印的上下标和单位。第 9 页的产量说明支持第 3 题的表格计算及第 10 页第 4 题 ә) 的草莓产量计算，共 2 条 `supports`。题内图表通过父子结构表达归属。

[content.json](01_segmentation/lesson_082/content.json) · [中文审核页](01_segmentation/lesson_082/review_zh.html) · [哈语审核页](01_segmentation/lesson_082/review_kk.html)

### 待人工抽查

- 第 9 页产量三角图顶格 M 的小字下标暂录为“жалпы”，请放大对照原图。
- 第 5 题的工作效率三角图占表头左上一个跨两行的单元格。共用模板的重建格显示符号转写，图形及原位可通过表格裁图和独立图示核查。
- 第 7 题暂按原印的运算分栏，从左到右、栏内从上到下展示。原书未指定必读顺序。
- 第 11 页“НЕГЕ / АТА / ТҮСІНДІР”贴近第 9 题，暂列页末 Other，作用范围待核。

静态校验和 7 项教学关联回归测试已通过。中哈两版均在断网 Chromium 中通过合并格反馈、作答空格显示、跨页定位、同一 Module 引用拦截、遗漏框选、草稿恢复与双向导入导出。系统策略拦截 `file://`，实测由本地请求拦截载入原 HTML，期间无外部请求。

### 第一轮审核修订 1

第 4 题 ә) 的草莓配图移除，作答条件仍在题干，完整插图仍可在原扫描查看。新增第 9 页单位面积产量定义对第 11 页第 8 题的概念支持。原始 80 条记录已按字节归档，76 项有效通过均继承，新关联为唯一待复核项。

[修订 JSON](02_segmentation_review/lesson_082/revision_1/content.json) · [新版中文审核页](02_segmentation_review/lesson_082/revision_1/review_zh.html) · [新版哈语审核页](02_segmentation_review/lesson_082/revision_1/review_kk.html) · [修订日志](02_segmentation_review/lesson_082/revision_1/change_log.md) · [原始审核记录](02_segmentation_review/lesson_082/submissions/review_001_original.json)

### 第一轮审核修订 2

第 8 题已给出两处单位面积产量，所需方法是统一单位后比较。撤除修订 1 新增的定义支持关联，保留原有的两条支持关系。新版沿用 76 项有效通过，审核页显示 0 项待核。

[修订 JSON](02_segmentation_review/lesson_082/revision_2/content.json) · [新版中文审核页](02_segmentation_review/lesson_082/revision_2/review_zh.html) · [新版哈语审核页](02_segmentation_review/lesson_082/revision_2/review_kk.html) · [修订日志](02_segmentation_review/lesson_082/revision_2/change_log.md)

## 第 83 课

**Түсімділік**（单位面积产量），主题为“Сабантой”（萨班托伊节）。PDF 一基页码和印刷页码均为 12–14。第 159 页目录列出第 83 课从第 12 页开始，第 84 课从第 15 页开始。第 13 页续用主题，第 14 页页眉明确为“83-сабақ”，以第 11 题家庭作业收尾。第 1–4、5–7、8–11 题分别位于第 12、13、14 页，各题均在本页结束。

| 切割进度 | 人工审核 | Module | Instructional Note | 子题 | 表格 | OCR 建议 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `segmentation_completed` | `pending_review` | 11 | 0 | 2 | 2 | 46 |

第 9 题保留水果饼图的图例、八个扇区和表格原印空白。第 10 题六个上下式分数分别记录分子、分母、原书位置和裁图。第 6 题浇水配图留在原扫描。题内饼图归属第 9 题，本课没有另立教学关联。

[content.json](01_segmentation/lesson_083/content.json) · [中文审核页](01_segmentation/lesson_083/review_zh.html) · [哈语审核页](01_segmentation/lesson_083/review_kk.html)

### 待人工抽查

- 第 5 题 а) 印有“收成相同”，而两人的种植株数不同，结尾询问一个单株产量。按原文转写，待核是否有勘误。
- 第 8 题前两步依次计算 5 公顷和 3 公顷的收获量，未标地块编号。第三步明确写“第二块地比第一块地多”，请核对编题时的对应。
- 第 10 题审核卡显示线性分数转写，原书上下式及句中位置通过逐个裁图和整段裁图核对。
- 第 14 页页末提示语印在第 11 题旁，作用范围待核。

静态校验和十项回归测试已通过。中哈两版均在断网 Chromium 中验证了原扫描与定位、表格空格、分数裁图、遗漏反馈、草稿恢复和双向导入导出。浏览器通过本地请求拦截载入同一 HTML，测试期间无外部请求。

### 第一轮审核修订 1

第 10 题新版以完整段落显示，六个分数在句中显示为上下式。逐项审核和原图定位保留。原始 88 条记录按字节归档，继承 83 项有效通过。第 1 题继续保留「无法判断」记录。

[修订 JSON](02_segmentation_review/lesson_083/revision_1/content.json) · [新版中文审核页](02_segmentation_review/lesson_083/revision_1/review_zh.html) · [新版哈语审核页](02_segmentation_review/lesson_083/revision_1/review_kk.html) · [修订日志](02_segmentation_review/lesson_083/revision_1/change_log.md) · [原始审核记录](02_segmentation_review/lesson_083/submissions/review_001_original.json)

## 第 84–90 课

切割进度为 `segmentation_completed`，七课的内容均为 `pending_review`。PDF 一基页码与印刷页码相同。第 159 页目录、各课课号与续页页眉、题号和相邻页共同确定页界，第 91 课从第 39 页开始。

| 课次与原书标题 | PDF / 印刷页码 | Module | Instructional Note | 子题 | 表格 | OCR 建议 | 文件 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 84 · Графиктер（图线） | 15–18 | 9 | 1 | 7 | 2 | 35 | [JSON](01_segmentation/lesson_084/content.json) · [中文](01_segmentation/lesson_084/review_zh.html) · [哈语](01_segmentation/lesson_084/review_kk.html) |
| 85 · Есеп шығару（解应用题） | 19–21 | 10 | 0 | 2 | 4 | 38 | [JSON](01_segmentation/lesson_085/content.json) · [中文](01_segmentation/lesson_085/review_zh.html) · [哈语](01_segmentation/lesson_085/review_kk.html) |
| 86 · Бір бағыттағы қуып жету қозғалысы（同向追及运动） | 22–24 | 9 | 1 | 2 | 4 | 52 | [JSON](01_segmentation/lesson_086/content.json) · [中文](01_segmentation/lesson_086/review_zh.html) · [哈语](01_segmentation/lesson_086/review_kk.html) |
| 87 · Бір бағыттағы қуып жету қозғалысы（同向追及运动） | 25–28 | 9 | 1 | 4 | 1 | 69 | [JSON](01_segmentation/lesson_087/content.json) · [中文](01_segmentation/lesson_087/review_zh.html) · [哈语](01_segmentation/lesson_087/review_kk.html) |
| 88 · Бір бағыттағы қуып жету қозғалысына берілген есептер. Қозғалыс графиктері（同向追及问题与运动图线） | 29–31 | 9 | 0 | 0 | 1 | 29 | [JSON](01_segmentation/lesson_088/content.json) · [中文](01_segmentation/lesson_088/review_zh.html) · [哈语](01_segmentation/lesson_088/review_kk.html) |
| 89 · Бір бағыттағы қалып қою қозғалысы（同向拉开距离的运动） | 32–34 | 9 | 1 | 0 | 1 | 36 | [JSON](01_segmentation/lesson_089/content.json) · [中文](01_segmentation/lesson_089/review_zh.html) · [哈语](01_segmentation/lesson_089/review_kk.html) |
| 90 · Бір бағыттағы қалып қою қозғалысы（同向拉开距离的运动） | 35–38 | 10 | 0 | 3 | 0 | 35 | [JSON](01_segmentation/lesson_090/content.json) · [中文](01_segmentation/lesson_090/review_zh.html) · [哈语](01_segmentation/lesson_090/review_kk.html) |

### 结构与人工抽查

- 第 84 课把原印的 3А、3Ә、3Б 保留为同一 Module 的三个子题，图线的原印辅助线和表格作答空位可分别核查。第 16 页照录“84-сурет”，请核对是否有勘误。第 4 题中文参考译为“按原价的三分之一降价”，请复核折扣语义。第 18 页页末提示暂列 Other，作用范围待核。
- 第 85 课第 3 题的二分之一保留在完整题干中，中文与哈语审核页使用上下式。第 5、6 题之间有原文明示的引用，图线标注和空白表格可对照原书。
- 第 86 课保留追及速度公式的下标、第 1 题用于读图的示意图和原印作答空格。第 87 课保留互逆题的示意图、第 4 题明确引用的子题、第 26 页的列方程步骤和河流数据表。
- 第 88 课保留第 2 题三幅图的箭头与旗标位置、第 3–4 题图中方向，以及第 5 题运动图线的颜色、折点和重合段。第 89 课第 1 题的三组速度只见于图中，保留其原印标签。第 2 题数轴保留细刻度、起点和弧线。
- 第 90 课第 2 题引用第 1 题，并明确引用第 26 页第 87 课的规则。跨课引用保存了印刷原文、页码和目标 ID。现行 Teaching Link 端点仅限本课，请复核跨课定位。第 8 题保留行人与滑雪者的图线折点及停留段。

保留理解题意及作答所需的图，装饰、情境和仅重复题干的配图留在原扫描中。图线和运动示意保留裁图、结构化关系与坐标，由现有审核页显示。原始来源沿用仓库扫描、Wiki 与 OCR 文件。

七课均通过静态检查和断网 Chromium 双语审核测试。浏览器通过本地请求拦截载入同一 HTML，期间无外部请求。

### 第 84 课第一轮审核修订 1

第 16 页 3Б 明确要求读取 3Ә 的运动图线来填表，新增 3Б → 3Ә 图线的 `uses_as_material`。初版 118 个对象均为等同对象，旧版审核记录可导入。新增关联待审核。

[修订 JSON](02_segmentation_review/lesson_084/revision_1/content.json) · [新版中文审核页](02_segmentation_review/lesson_084/revision_1/review_zh.html) · [新版哈语审核页](02_segmentation_review/lesson_084/revision_1/review_kk.html) · [修订日志与历史盘点](02_segmentation_review/lesson_084/revision_1/change_log.md)

### 第 84 课第一轮审核修订 2

第 16 页 3Ә 的图线说明补全横轴时刻、网格单位与折线经过的七个点。原始 JSON 中的 76 条记录按原字节归档。新版保留 72 项有效通过，含 3Б → 3Ә 图线的材料关联。唯一待复核项是更新后的 3Ә 图线说明。

[修订 JSON](02_segmentation_review/lesson_084/revision_2/content.json) · [新版中文审核页](02_segmentation_review/lesson_084/revision_2/review_zh.html) · [新版哈语审核页](02_segmentation_review/lesson_084/revision_2/review_kk.html) · [修订日志](02_segmentation_review/lesson_084/revision_2/change_log.md) · [原始审核记录](02_segmentation_review/lesson_084/submissions/review_001_original.json)
