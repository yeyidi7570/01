# 教材消费端预览

预览器直接读取仓库中的教材 `content.json`。打开后可选择课次、整课或样本模块，在教师和学生视图间切换，或输入对象 ID 跳转。原书对照可随时打开。哈萨克语正文和数学内容来自所选版本的教材数据。

## 启动

在仓库根目录运行。需要 Python 3.10+、Pillow 和支持 CSS Grid 的浏览器。扫描 PNG 从仓库的 `wiki-data/` 读取，稀疏检出时需要加入 [样本](samples.json) 所引用课次的 `pages[].scan_path`。

```sh
python -m pip install -r textbook-preview/requirements.txt
python textbook-preview/server.py --port 8765
```

打开 [教材预览](http://127.0.0.1:8765/)。如需在同一局域网的平板或投影电脑打开，可用 `--host 0.0.0.0` 监听，再从设备访问运行主机的局域网 IP 和端口。

- 初始入口是第 1 课第 4 题。样本下拉框覆盖 4 课、5 个模块。整课及对象定位使用同课的数据，正式验证范围见[验证报告](VALIDATION.md)。
- 输入完整对象 ID 可定位课次、任务、教学说明、嵌套元素、表格单元格或教学关联。地址栏会保留当前的引用和显示设置，可以直接分享。例如 [第 7 课第 30 页的借位竖式](http://127.0.0.1:8765/?id=math-2023-grade4-part1%3Alesson-007%3Anote-subtraction%3Aexample-3%3Acalculation)。
- 学生视图显示教材和可跳转的教材关联。教师视图增加关联理由和模拟教学请求。勾选「原书对照」会加载原书页面。定位具体对象时，对照显示该对象涉及的页。
- 「不支持的结构」标记出无法恢复的对象或部分关系，并给出 ID。详见[支持清单](STRUCTURES.md)。

## 模拟教学接口

`POST /api/teaching-plan` 接收 UTF-8 JSON，以教师的自然语言请求查找样本。可匹配课程号、题号、完整对象 ID 或样本词汇。关键词匹配结果不唯一时，返回空引用。

```sh
curl -fsS http://127.0.0.1:8765/api/teaching-plan \
  -H 'Content-Type: application/json' \
  -d '{"request":"请按第7课第2题讲解多位数笔算借位"}'
```

响应包含 `mode: "mock"`、`references` 和 `generated`。每条引用仅有 `lesson_id`、`object_id` 和 `type`，其中 `type` 可为 `lesson`、`module` 或 `instructional_note`。课程中的 `supports` 与 `uses_as_material` 用于解析相关教学说明。预览器在打开引用时读取原 JSON 渲染教材，`generated` 中的 `organization`、`explanation` 和 `exercise` 各有独立标记。

样例使用本地确定性模拟器。它按课程和样本语汇检索，并返回预设建议。后续模型可通过 `teaching.plan(catalog, request, provider=...)` 接入相同契约。验证器拒绝跨课误配、类型不符、未知或重复 ID，以及夹带教材正文的额外字段。

## 示例测试

```sh
python -B -m unittest discover -s textbook-preview -v
```

浏览器测试需 Node.js、Playwright 与 Chromium。确保上面的服务正在运行，且项目环境可以解析 `playwright`。如使用系统 Chromium，可通过 `CHROMIUM_PATH` 指定其路径。

```sh
npm install --prefix /tmp/textbook-preview-test playwright
NODE_PATH=/tmp/textbook-preview-test/node_modules \
  /tmp/textbook-preview-test/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/textbook-preview-test/node_modules node textbook-preview/test_browser.cjs
```

`PREVIEW_URL` 可指定服务地址，`PREVIEW_SCREENSHOTS` 可指定截图输出目录。
