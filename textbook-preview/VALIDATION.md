# 预览与调用验证报告

验证日期为 2026-11-25。教材是《数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП》，来源仓库基线为 `4d0cf1a`。验证覆盖 4 课的 5 个 Module 及其关联教学说明。

**结果**　已有 JSON 足以支撑按课次、任务及说明 ID 的引用和呈现。样本的文字、表格、数位竖式、作答留白、教学关联和跨页归属均通过测试。需要重建精确图形或原书图文布局的结构仍有明确的数据缺口，见下表。

## 已查阅的实现与数据

- `.agents/skills/textbook-segmentation/SKILL.md` 及其内容规则描述了 Lesson、Module、教学说明、元素阅读顺序、跨页和图文证据。
- `experiments/ai_textbook_pilot/schema.json` 的 JSON Schema 约束早期 AI 实验中的 JSONL 习题和标签，`wiki-data/wiki.schema.json` 约束 Wiki 数据。现行 Lesson JSON 声明 `textbook-lesson/4.0`，本仓库以 `.agents/skills/textbook-segmentation/scripts/lesson.py` 的校验器及各课 `schema_rules` 表达现行约束。四份样本均通过现行 `validate_content`。
- 审核模板的 `review.js` 和书级 `tools/v4/render.py` 提供了现有渲染依据，包括竖式、表格、裁图与关联方向。消费端独立使用教材 JSON 和坐标对应的原书图像资源。
- 第 1 课选用书级 README 记录第三轮复核通过的 `revision_3/content.json`（`v4.1-r003`）。第 7、10、28 课使用原归档 `01_segmentation` 中的 `v4.1-audit1`，保留其来源和待审状态。

## 五个样本

| 课次 / 模块 | PDF 页 | 检查内容和结果 |
| --- | --- | --- |
| 001 / `m04` | 8 | 共享的三条步骤、长度和时间算例、进借位、复合单位、印刷留白。时间竖式通过 `vertical.layout` 展示，对齐分钟数位和结果横线。四道练习按现有 2×2 网格归组。两段箭头保留图示、方向及已记录端点引用。 |
| 001 / `m05` | 9 | 课表 7×7，含 5 个明确空白格和 6 个时段。分钟上标下划线由数据生成。保留只适用于 5А 的 Badge 和原书 4 个子题，子题引用可跳到课表或前一子题。 |
| 007 / `m02` | 29–30 | 一个任务 ID 对应两段指令，按原书顺序为第 29 页任务 → 加法说明 → 第 30 页续段 → 减法说明。两条 `uses_as_material` 均可跳转；说明内四个算例和七条步骤可分别定位。三加数及跨零借位竖式使用结构化数位列。 |
| 010 / `m03` | 41–42 | 原书顺序为单位说明、三个立方体、比较子题、下一页换算子题。保留立方单位上标和印刷空框。说明通过 `supports` 指向任务。缺少公式网格的三个位置均显示提示。 |
| 028 / `m03` | 105–106 | 三个路线图保留各自子题归属、裁图、方向和全程括号说明，`uses_as_material` 可回到速度说明。可用哈萨克语小写子题标识和图对象 ID 定位。 |

## 实测

- 在 Chromium 156 使用 **1280×720（投影尺寸）**、**768×1024（平板尺寸）**、**1440×900（浏览器尺寸）** 跑过五个样本、导航、模拟调用和教师/学生切换。检查了页面横向溢出、竖式网格、时间上标、信息图请求、原书对照开关和定位高亮。查看了实际浏览器截图并对照原书扫描第 8、9、29、30、41、42、105、106 页。此次测试的设备尺寸由浏览器模拟，未使用实体投影机或平板。
- 五项 Python 测试通过。覆盖 JSON 字节一致性、5 条教师请求、按课或教学说明 ID 查找、无匹配请求、拒绝无效模型引用、按坐标核对裁图像素。浏览器另用临时变体检查合并单元格、缺表格数据、未知对象类型及其明确提示。
- 教学接口在本地以模拟模式执行。教师请求可得到 Lesson、Module 及适用 Instructional Note 的 ID，引文交由同一预览器呈现。组织建议、讲解和练习各在独立区域。真实模型驱动的理解与编排准确性留待接入模型后验证。

## JSON 表达缺口及建议

下列对象 ID 完整列出。扩展建议面向对应对象类型，影响范围以本次实际确认的对象为准。

| 对象 ID | 已有内容与缺失字段 | 建议扩展及确认影响 |
| --- | --- | --- |
| `math-2023-grade4-part1:lesson-001:m04:ex-conversion` | 有 `worked_sequence.steps`、`relationships`，缺少共同步骤居左、两个竖式居右的列布局。 | 增加可选的 `worked_sequence.layout`，用有序行和列中的对象 ID 表示共用步骤及并排示例。影响复合单位两道算例的原书横向布局。 |
| `math-2023-grade4-part1:lesson-001:m04:ex-borrow` | 有顺序和关系路径，缺少说明、换算和右侧并列竖式的组内二维布局。 | 同样用 `worked_sequence.layout` 表示分列及同列上下顺序。影响一组时间借位示范的空间关联。 |
| `math-2023-grade4-part1:lesson-001:m04:ex-carry:arrow`、`math-2023-grade4-part1:lesson-001:m04:ex-borrow:arrow` | `structured_description.relations` 有方向和对象或标签线索，缺少可附着到具体数位或文字位置的两端锚点和路径。 | 增加 `from_anchor`、`to_anchor` 的统一对象和单元格引用，配合归一化路径点表达曲线。影响第 8 页两根箭头的可缩放重绘。 |
| `math-2023-grade4-part1:lesson-007:note-addition`、`math-2023-grade4-part1:lesson-007:note-subtraction` | 各 Note 有四个算例和独立的七步列表，缺少示例 2×2 分组和列表右栏信息。 | 为 Note 增加可选 `layout.groups`，注明算例区域网格及步骤区域列位置。影响第 29、30 页的两个独立说明在宽屏上的对照阅读。 |
| `math-2023-grade4-part1:lesson-010:note-volume-units`、`math-2023-grade4-part1:lesson-010:m03:part-ae`、`math-2023-grade4-part1:lesson-010:m03:part-b` | 有行优先 `content_order`，缺少印刷版的 3×2、3×2、2×2 算式网格。 | 将第 1 课已使用的 `printed_expression_grid.row_major_ids` 填入这三个对象，并把字段约定扩至 Note 和 Subtask。影响第 41、42 页这三组原书二维排列。 |
| `math-2023-grade4-part1:lesson-028:m03:3А:route`、`math-2023-grade4-part1:lesson-028:m03:3Ә:route`、`math-2023-grade4-part1:lesson-028:m03:3Б:route` | 有 `direction`、`whole_bracket_kk`、`annotations_kk`，时段、刻度、钟面和全程括号端点缺少独立位置记录。 | 增加带 ID 的 `segments`、`ticks`、`markers` 和 `brackets`，用锚点或归一化坐标关联。影响三道行程图的重新绘制和按图元教学。 |
| `math-2023-grade4-part1:lesson-028:note-speed:formula-triangle` | `positions` 记录 S、v、t 的相对位置。分区形状及分区之间的运算符仅有文字描述和扫描证据。 | 增加 `regions` 的多边形点和带区域端点的 `operators`。影响该速度说明图的可交互重绘，应先确认原图运算点。 |

本次仅提交独立预览工具及其测试和文档。原教材、审核模板和来源文件保持原有版本。
