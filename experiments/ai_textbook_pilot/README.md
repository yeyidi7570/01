# AI 专用教材库：10页保存格式试点

本目录只转换commit `6d67153ea65b105366c0ebf436ff76a3373a0650` 的已有Codex实验；没有重新OCR、切题、改动旧实验或正式Wiki，也没有生成KLP、题型语义、难度、用途、答案或新解法。原书已打印的算例、结果、算法讲解是原文留存，不是本次生成的解答。

## 数据入口

- `exercises.jsonl`：一行一父题；子题递归嵌套。检索 `(book_id,lesson_number,exercise_number)` 可返回一个或多个稳定ID，印刷编号不担任永久身份。
- `labels.jsonl`：每父题一行客观标签，`exercise_id`关联；将来添加KLP/题型/难度应另写`extension_labels`文件，通过相同ID关联，避免修改正文。
- `schema.json`：JSON Schema 2020-12。根规范验证一条exercise/objective_labels/extension_labels；manifest和ID映射分别用`$defs.manifest`与`$defs.id_mapping`验证。支持多教材、未知编号、多页、递归子题、多图、跨题/外部引用及独立扩展标签。
- `manifest.json`：教材、输入commit、实际页范围、所有图片及来源、校验和和检索索引。
- `id_mapping.json`：旧实验父题/子题/材料ID到新ID的映射；不读取或覆盖正式Wiki模块ID。
- `validation_report.md`：实际执行的自动检查、阅读顺序与图片转录限制、所有UNKNOWN。
- `images/source/`：原始完整页PNG，原字节复制；`images/crops/`：直接使用已有bbox裁剪，无新增语义边界。
- `conversion_config.json`及`scripts/`：固定输入/规则和实际生成、校验、检索程序。

## 文字保存口径

`original_text`只由最终校对OCR的原行拼接，包含题内题干、图表标签、原印算法和同题上下文续页；独立题号徽章行移到`numbering_evidence`。没有删除数学运算中的数字或正文引用。完整旧实验文字另存`provenance.verbatim_experiment_text`，用于审核，不能当作经过整理的题干。

`text_units`为逐行不可变文字、原ID和原bbox；`text_order`给出原始及可读的unit-key序列。`readable_text`仅按已有子题/材料关联整块调序，同一父题的body unit恰好出现一次。保留行末连字符、空格和标点，不翻译、不补字、不修正文句。嵌入在同一OCR行内的а)、ә)等原印子题前缀保留，不能为去标签而改写整行。

表格、竖式、括号示意、阴影格等不伪装成可靠线性公式；`transcription_status=image_required`表示仍须看原图。没有生成单元格答案、LaTeX或几何推理。课程共用讲解框保存在`shared_materials(scope=lesson_context)`，不混入父题正文。

所有source_line_ids通过manifest的source_bundle_id指向最终校对JSON；实际身份为bundle+PDF页序+原页内line_id。原文、展示顺序、继承的AI结构和本轮客观观察分字段保存。

## 范围与稳定身份

正式样本固定为PDF页14、29、46、62、73、74、87、109、110、139。30页只完成旧父题2的context_only续接，没有新增正式页/父题；86/108/138页仅保留旧课号证据，不新增课程切分或练习。

UUIDv5 ID取固定命名空间、教材标识/来源PDF哈希、物理锚点（原页序、原行ID、原bbox），不读取课号或题号内容。相同输入重复生成的ID和数据/图片字节一致；修改课号、题号元数据不会改ID。将来重新OCR、换版或改变物理锚点时必须通过现有ID映射显式迁移，不声称跨任意来源版本自动保持身份。

## 客观标签

has_image只统计题目自有片段与同题续页的实际插图/示意/题内装饰，不统计截图自身、纯表格、竖式格纸、答题框；仅继承的课程讲解不计入。has_table为真实数据表格；has_formula为原印运算/等式/换算/竖式，单独数量、单位、变量表头或要求写算式的指令不计。

每个标签有证据、判断口径和unknown理由；null不等于false。第14页第1题装饰图上沿归属未精确标注，has_image保守为null。其余三个结构标签由旧结构直接计算，不生成主观标签。

## 重现与调用

在仓库根目录，使用Python及requirements.txt列出的依赖：

```bash
python experiments/ai_textbook_pilot/scripts/build.py
python experiments/ai_textbook_pilot/scripts/validate.py
python experiments/ai_textbook_pilot/scripts/reproducibility.py
python experiments/ai_textbook_pilot/scripts/query.py --book math-2023-grade4-part1 --lesson 29 --exercise 4 --include-references
```

build也支持`--repo REPOSITORY --out EMPTY_OR_PILOT_DIRECTORY`。脚本先检查固定输入哈希，拒绝被替换的旧实验。生成时间固定在配置中，以免同输入重跑造成数据差异；validation_report是实际校验审计，执行时间可变化，不参与可重现内容摘要。

下一阶段TrueNorth先读本README、schema、manifest、validation_report，再读exercises与labels及所需images；通过id_mapping回溯旧实验。不要以图片存在就判has_image，不要忽略UNKNOWN或image_required，不要在已有text内混写推理标签；生成新题时将本库当参考来源，另存新题及source_exercise_ids，勿覆盖原题。
