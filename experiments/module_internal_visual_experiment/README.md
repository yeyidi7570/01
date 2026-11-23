# 11页模块内部视觉切割实验

打开module_internal_review.html即可离线验收，扫描底图已嵌入。切换页码、模块，勾选“聚焦所选模块”，点击彩框或右侧条目查看原文与识别结果。表格可查看多行/合并单元格，点击单元格高亮原图。不同类型可独立开关。边界外知识框用灰色提示，不是新模块。

result.json仅是临时实验记录；prompt.md保存本次Prompt，ambiguities.md列人工复核事项；build_result.py保存本次显式视觉判读坐标及装配/展示脚本。没有数据库、正式schema、KLP或新答案。

数据来源固定为ai_textbook_pilot已有模块及11张原扫描页。27模块和29个页片段的bbox逐项与原数据相同；原JSONL只读。原OCR行按原样引用，文字修改、错误符号补全均未进行。临时元素ID仅用于此HTML点击定位，不是正式模块ID。

执行：在本仓库运行 python experiments/module_internal_visual_experiment/build_result.py（Python、Pillow、numpy）。它只重新装配本次已经记录的视觉判断，不调用OCR，不自动重新理解扫描页。重新实验Prompt时应另存新结果，不能把脚本固定坐标复放当作新模型效果。
