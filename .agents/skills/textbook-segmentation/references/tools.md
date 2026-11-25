# 通用脚本接口

以下命令在 Git 仓库根目录执行。Python 3.11+；仅生成界面需要 Pillow。脚本不执行 OCR，视觉判断、原书课次定位和人工依据由 Codex 核实。

```sh
tool=.agents/skills/textbook-segmentation/scripts/lesson.py
python "$tool" plan --book "$book" --lessons '2,5-8' --catalog "$catalog"
python "$tool" render --content "$data" --scans "$scans" --translations "$zh_aux" --output "$new_stage"
python "$tool" check --lesson-dir "$new_stage"
python "$tool" compare --old "$previous_content" --new "$new_stage/content.json"
```

- `plan` 是只读盘点，列出现有文件、复用或重跑候选及审核记录哈希。根据真实目录与正文建立导入目录 JSON，顶层为 `lessons` 列表，每项含正整数 `number`、`title_kk`、按顺序列出的 `pdf_pages`、逐页对应的 `printed_pages` 和非空 `boundary_evidence`。PDF 页码始终为一基。单课或范围的初查可先省略 `--catalog`，但输出的空边界不能用于切割。`all` 要求已确认的目录。`--rerun` 只标记候选，不写入归档。
- `render` 以待审核 JSON、扫描清单和中文辅助 JSON 为输入，在一个尚不存在且父目录已存在的暂存目录写出三件套。扫描清单是 `scan_asset_id → 路径` 的 JSON 对象，相对路径从清单所在目录解析。支持 PNG、JPEG、WebP。裁图按 `crop_assets` 从同批扫描生成。中文辅助文件包含 `title`、可选的 `theme` 与 `objects`，后者以对象、单元格或 OCR 建议 ID 为键，复核提示可用 `对象ID#code`。所有译文是字符串。保留已经生成的哈语数据原字节。修订时传入 `--prior-review` 指向未经改写的提交原件。教材 `review_revision` 保存 `source_version`、提交 SHA-256、来源对象 ID、经对照确认等同的对象 ID，以及已处理的旧问题记录 ID。两份 HTML 内嵌同一原始记录包。
- `check` 验证并输出统计，覆盖数据身份和结构、页坐标、标签/表格/关联、OCR 建议引用、两版内嵌数据/资源/行为完全一致以及基本离线壳和体积。旧 V4 单对象界面只能用 `--allow-legacy-review` 检验历史产物，该选项不能用于新交付。仍需 [人工和浏览器实测](review.md)。
- `compare` 以稳定 ID 报告相同、改变、删除和新增的对象。该命令不猜测拆分/合并对象的对应，也不迁移反馈。

## 通用审核界面使用的数据合同

- 顶层含 `data_version`、`review_status`、`book`、`source`、`schema_rules`、`lesson`、`pages`、`crop_assets`、`ocr_suggestions`。必要时添加坐标系、计数和证据元数据。使用一个明确稳定的复核版本。每个 `page` 有 `id`、`pdf_page`、`printed_page`、`width`、`height`、`scan_asset_id`、`scan_path`，可提供 `scan_sha256`。
- `lesson` 包含 `id`、`number`、`title_kk`、`review_status`、`pdf_page_range`、`printed_page_range`、`boundary_evidence`、`units`、`content_order` 和 `teaching_links`。 `schema_rules.instructional_note_badges` 记录经原书确认的标签。
- `units` 及嵌套 `elements` 的必需字段为 `id`、`parent_id`、`type`、`review_status` 和 `page_refs`。有子项时列出直接子项 ID 的 `content_order`。位置包括 `pdf_page`、`printed_page`、`scan_asset_id` 和像素 `bbox`。常见可选字段有 `text_kk`、`role`、`module_number`、`subtask_label`、`scope_ids`、`review_flags`；复核提示含 `code`、`description_kk`。
- `crop_assets` 以资源 ID 映射到上述定位；对象使用 `crop_asset_id`。图片使用包含 `description_kk` 和关系证据的 `structured_description`。表格使用 `row_count`、`column_count`、`header_rows` 和 `cells`，单元格含 `id`、零基 `row`/`column`、`rowspan`/`colspan`、`header`、`text_kk` 与定位，可用 `printed_text_kk` 保留原印刷分行。竖式使用 `vertical` 的 `upper`、`lower`、`operator`、`result` 和必要位置/等价式字段，复杂公式保留精确版面表示及原图。
- 教学关联是课内平铺的 `teaching_links`，须有 `id`、`parent_id`、`from_id`、`to_id`、`type=teaching_link`、`relationship`、`rationale_kk`、`page_refs`、证据和状态。OCR 建议包含 `id`、`object_id`、`category`、`reason_kk`、定位、状态、`source_lines`（含 `line_id`、`raw`、`existing_corrected`）、建议值及必要的结构更正。对象用 `ocr_suggestion_ids` 反向指向建议。确保页面抽查能追到源行。

共用模板位于 [assets/review](../assets/review/)，从仓库 V4 连续问卷实现抽取。书级旧生成器仅用于复现历史案例。连续竖式可在 Example 中使用 `worked_sequence`，以 `steps` 引用原顺序中的直接子项，并提供整组裁图、关系及哈语简述。其中文参考以 `对象ID#worked_sequence` 提供。
