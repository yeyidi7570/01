# 实际校验报告

执行时间（UTC）：2026-11-23T03:58:59.455867+00:00。程序结果：**全部通过**。

输入父题27条；输出父题27条；递归子题61个（含字母组及其内部未编号项目）；标签27条。图片72张：原始完整来源页11张、既有范围裁图61张。

程序通过只证明格式与来源一致，不等于原实验的切割、材料归属或数学阅读顺序已经语义正确。原图边界没有扩大，也没有悄悄修正原结构。

## 已实际执行的检查

1. Strict JSONL parsing, duplicate-key rejection, Draft2020-12 schema for all rows, manifest and mapping：通过。
2. Unique parent IDs, exact input parent count, and bijective labels：通过。
3. All stable IDs recomputed from source anchors; lesson/exercise metadata renumbering has no effect：通过。
4. Every source ID, source text and bbox traced to final OCR; original badges separate from body：通过。
5. Readable text is an exact source-unit permutation: no omitted/rewritten/added body text：通过。
6. All nested nodes, labels and inherited boundaries/material ownership preserved：通过。
7. Cross-page parent continuations remain one record; only ten formal pages, page30 context-only：通过。
8. All explicit and implicit relation targets resolve; one explicit cross-exercise reference preserved：通过。
9. Every UNKNOWN and independence limitation preserved verbatim：通过。
10. All image references exist; no orphan files; full sources byte-identical and crop pixels exact：通过。
11. Pinned inputs, unchanged old experiment, script/config and generated-file hashes verified：通过。
12. Objective label rows complete, null reasons explicit; no KLP/type/difficulty/purpose/solution annotations generated：通过。

## 客观标签统计

| 标签 | true | false | null |
|---|---:|---:|---:|
| has_image | 8 | 18 | 1 |
| has_table | 3 | 24 | 0 |
| has_formula | 8 | 19 | 0 |
| has_subquestions | 14 | 13 | 0 |
| is_cross_page | 2 | 25 | 0 |
| has_explicit_references | 1 | 26 | 0 |

27条标签均已生成；null不是漏记录。截图自身不计has_image，题内装饰图计入；课程公共讲解另列，不计题目自有视觉属性。

- `ex_0a6bd78f74025d82829d1ced9e1cb8cc` / `has_image`：父题上沿与页首角色图存在少量重叠，装饰图归属未精确标注；主体表格不能单凭截图判为插图。

## 可读顺序与空间表达仍须复核的题目

以下只是原有块的无损调序，不声称这些表格、竖式、图注可脱离图片独立理解。含装饰口号的记录另外明确其集中排至末尾的展示口径。

| 课号 | 题号 | PDF页 | 稳定ID | 未解决的表达问题 |
|---|---|---|---|---|
| 3 | 1 | [14] | `ex_0a6bd78f74025d82829d1ced9e1cb8cc` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED |
| 7 | 2 | [29, 30] | `ex_dfebea8cdc715182964ab61681388dfd` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED；CONTEXT_ONLY_CONTINUATION_SCOPE |
| 11 | 5 | [46] | `ex_a6cb083ad8ae5ed884f32db5f6993898` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED |
| 11 | 7 | [46] | `ex_aa76a6d1f856588285f2ae08fa549eeb` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED |
| 15 | 8 | [62] | `ex_2b432dc1a5b65769b51a24b308a45758` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED |
| 15 | 10 | [62] | `ex_385f779a276d56b6be9ca85e90af6cc2` | DECORATIVE_LETTERING_SEPARATE_FROM_PROSE |
| 19 | 1 | [73] | `ex_9b8bf3a75e06521ab3a5fd734de8a917` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED |
| 19 | 2 | [73, 74] | `ex_e890fcd7817159168b234fb74a24b3f1` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED |
| 22 | 7 | [87] | `ex_c137548803f25742b4b37db3aba31219` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED |
| 22 | 8 | [87] | `ex_9fcf4742cdc8588483ec841c1003748e` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED |
| 29 | 4 | [109] | `ex_73a16f40c66d55dfad65314dc1aa1f66` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED |
| 29 | 10 | [110] | `ex_0d78170ca74c50e69859eb91e2b98c36` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED；DECORATIVE_LETTERING_SEPARATE_FROM_PROSE |
| 38 | 7 | [139] | `ex_dd42408c8ed35c7d8e993b542a4fd79a` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED |
| 38 | 8 | [139] | `ex_02381c54b1ae50639c901e39d7bba5a0` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED |
| 38 | 9 | [139] | `ex_f17b43ec27165e13b4091c609c82dc5d` | SPATIAL_MATERIAL_NOT_FULLY_LINEARIZED；DECORATIVE_LETTERING_SEPARATE_FROM_PROSE |

其中14道父题含image_required材料：3课1题；7课2题；11课5、7题；15课8题；19课1、2题；22课7、8题；29课4、10题；38课7、8、9题。它们包括数位表、价格表、速度表、竖式、单位碎片、多空框换算、数卡/气球、括号/线段示意和几何/阴影格。未生成可靠单元格结构、逻辑公式、LaTeX或答案。15课10题另只有装饰口号排列审计提示，不是公式转录。

## 原有UNKNOWN及独立性限制

### U01 — UNKNOWN

UNKNOWN：第29–30页独立“ЕСІҢДЕ САҚТА!”框可同时视为课程讲解或第2题解释算法时的共用材料。本实验关联第2题但明确标为教学材料；不把框内1–7认作新题。第30页仅提供上下文，不计测试样本。

### U02 — UNKNOWN

UNKNOWN：14页底部黄色记忆框并不在第1题绿色外框内。本实验以课程讲解单独保存并关联第1题，不将其1、2、3误计为练习。课程材料是否应计入题目裁剪范围由第三方统一口径。

### U03 — UNKNOWN

UNKNOWN：74页顶部除法记忆框位于2ә之前，属于课程解释还是父题2的共用材料没有显式归属标记。本实验保存为课程背景并为父题2建立依赖，不重复分配文字行。

### U04 — UNKNOWN

UNKNOWN：109页黄色速度换算讲解框的教学作用明确，但未印题号。本实验保留为课程共用背景并关联3、4、5题；不会仅凭邻近位置把它硬归某一道题。

### U05 — INDEPENDENCE_LIMITATION

全部10页：同一本书的历史OCR任务存在于本对话，不能证明完全没有既往接触；当前可见上下文没有这10页具体切割答案。本次没有读取旧Wiki结构候选或任何对方输出；全部样本标为NOT_PROVABLE fully blind，供第三方单独统计。

## 格式边界和已知设计限制

- 未发现阻碍本次10页试点的根本性schema问题；数据定义没有把27道题、特定年级/语言/科目写死到通用schema中。
- 稳定ID以固定来源版本和物理锚点为边界，课号/题号修正不改ID；重新OCR、改版或调整锚点必须显式迁移映射，不能声称自动跨所有版本保持身份。
- original_text的正文口径明确排除独立题号徽章行；编号原文仍存numbering_evidence/text_units，完整旧文本也保留。因此不是删除原文证据。
- 30页是原父题2的上下文，不是第11个正式测试页；86/108/138仅为既有课号证据。
- 原书已打印算例、算法及其结果原样保留，不能误认为本次新增解答。

## 交接TrueNorth

先读README、schema、manifest与本报告，再通过exercises.jsonl读取完整父题/子题/共用材料，结合images及source_line_ids回查。labels.jsonl只作为客观属性；id_mapping.json负责追溯旧实验。新增KLP、题型、难度应写独立extension_labels记录，以exercise_id关联，不覆盖正文，不把UNKNOWN或image_required当作已解决。

## 重复生成检查

实际双次生成：passed；87个确定性文件字节一致。报告执行时间等审计信息不参与确定性内容摘要。

## 校验程序错误拦截实测

实际向临时副本注入6类错误，均被校验程序拒绝：readable_text_changed、dangling_exercise_reference、missing_image、lost_unknown、wrong_child_parent、wrong_source_bundle。正式输出没有注入这些错误。
