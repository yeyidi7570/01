export function el(tag, text, className) {
  const element = document.createElement(tag);
  if (text != null) element.textContent = text;
  if (className) element.className = className;
  return element;
}

export function ordered(children = [], order = []) {
  const byId = new Map(children.map(child => [child.id, child]));
  if (byId.size !== children.length || order.length !== children.length ||
      new Set(order).size !== order.length || order.some(id => !byId.has(id))) {
    throw Error("content_order 与子对象不一致");
  }
  return order.map(id => byId.get(id));
}

export function pagesOf(object) {
  return [...new Set((object.page_refs ?? []).map(ref => ref.pdf_page))];
}

function unsupported(id, reason) {
  return el("p", `不支持的结构 · ${reason}（${id}）`, "unsupported");
}

function sourceText(text) {
  return el("p", text, "original");
}

function linkedList(ids, context, separator) {
  const list = el("span");
  ids.forEach((id, i) => {
    if (i) list.append(separator);
    list.append(context.link(id));
  });
  return list;
}

function numberedText(text) {
  const lines = text.split("\n");
  if (lines.length > 1 && lines.every((line, i) => line.startsWith(`${i + 1}. `))) {
    const list = el("ol", null, "printed-list");
    for (const line of lines) list.append(el("li", line.replace(/^\d+\. /, "")));
    return list;
  }
  return sourceText(text);
}

function verticalGrid(layout, transcription) {
  const {columns, rows, units} = layout;
  if (!columns?.length || !rows?.length || !units || layout.kind === "long_division") {
    throw Error("竖式网格类型或字段");
  }
  const grid = el("div", null, "vertical");
  grid.setAttribute("role", "img");
  grid.setAttribute("aria-label", transcription);
  const columnsById = new Map(columns.map((col, i) => [col.id, i]));
  if (columnsById.size !== columns.length) throw Error("竖式列重复");
  grid.style.marginInlineStart = `${Math.max(0, Math.min(layout.indent_em ?? 0, 10))}em`;
  const digitWidth = rows.some(row => row.cells.some(cell => cell.kind === "marker" && String(cell.value).length > 1))
    ? "1.6ch" : "1ch";
  grid.style.gridTemplateColumns = columns.map(col =>
    col.place || col.digit_track ? `minmax(${digitWidth}, max-content)` : "max-content"
  ).join(" ");
  rows.forEach((row, r) => {
    let last = 0;
    for (const cell of row.cells) {
      const column = columnsById.get(cell.column);
      const span = cell.span ?? 1;
      if (!Number.isInteger(column) || !Number.isInteger(span) || span < 1 ||
          column < last || column + span > columns.length) throw Error("竖式单元位置或跨度");
      last = column + span;
      if (!["digit", "number", "unit", "operator", "relation", "marker", "blank", "rule"].includes(cell.kind)) {
        throw Error(`竖式单元 ${cell.kind}`);
      }
      const value = cell.kind === "unit" ? units[cell.value] : cell.value;
      if (value == null && !["rule", "blank"].includes(cell.kind)) throw Error("竖式单元缺值");
      const item = el("span", value, `cell-${cell.kind}`);
      item.style.gridArea = `${r + 1} / ${column + 1} / span 1 / span ${span}`;
      grid.append(item);
    }
  });
  return grid;
}

function legacyVertical(vertical, transcription) {
  const {upper, lower, operator, result, result_blank_unit, equivalence_kk, highlight} = vertical;
  if (!upper || !lower || !["+", "−", "×", "÷"].includes(operator) ||
      (!result && !result_blank_unit)) throw Error("简式竖式缺少操作数、运算符或结果字段");
  const grid = el("div", null, "vertical");
  grid.setAttribute("role", "img");
  grid.setAttribute("aria-label", transcription);
  grid.style.gridTemplateColumns = "max-content max-content max-content max-content max-content";
  let rowNumber = 0;
  function row(text, sign, unit, highlighted, suffix = "") {
    rowNumber++;
    const match = text?.match(/^(?:(.*?[^\d\s])\s+)?(\d[\d ]*)(?:\s+(\S+))?$/u);
    if (text && !match) throw Error("简式竖式的数值或单位格式");
    const [, prefix = "", digits = "", printedUnit = unit] = match ?? [];
    const number = el("span", digits);
    number.style.textAlign = "end";
    if (highlighted) {
      const start = digits.indexOf(highlight.value);
      if (start < 0) throw Error("竖式高亮无法绑定数位");
      number.replaceChildren(digits.slice(0, start), el("mark", highlight.value),
        digits.slice(start + highlight.value.length));
    }
    const prefixCell = el("span", prefix ? `${prefix} ` : "");
    const unitCell = el("span", printedUnit ? ` ${printedUnit}` : "");
    const cells = [el("span", sign ? `${sign} ` : ""), prefixCell, number, unitCell, el("span", suffix)];
    cells.forEach((cell, i) => {
      cell.style.gridArea = `${rowNumber} / ${i + 1}`;
      grid.append(cell);
    });
  }

  row(upper, "", "", highlight?.position?.startsWith("upper_"));
  row(lower, operator, "");
  if (vertical.result_rule_printed !== false) {
    const rule = el("span", null, "cell-rule");
    rule.style.gridArea = `${++rowNumber} / 2 / span 1 / span 3`;
    grid.append(rule);
  }
  const suffix = result && equivalence_kk?.startsWith(result) ? equivalence_kk.slice(result.length) : "";
  row(result, "", result_blank_unit, highlight?.position?.startsWith("first_digit_"), suffix);
  return {grid, equivalence: suffix ? "" : equivalence_kk};
}

function formula(object) {
  const box = el("div", null, "formula");
  const vertical = object.vertical;
  if (vertical) {
    try {
      if (vertical.expression_kk) box.append(el("div", vertical.expression_kk));
      const result = vertical.layout
        ? {grid: verticalGrid(vertical.layout, object.text_kk)}
        : legacyVertical(vertical, object.text_kk);
      box.append(result.grid);
      if (result.equivalence) box.append(el("div", result.equivalence));
    } catch (error) {
      box.replaceChildren(unsupported(object.id, error.message));
    }
    return box;
  }
  if ([undefined, "linear", "continued_equation"].includes(object.notation) && object.text_kk &&
      (!object.text_kk.includes("\n") || object.notation === "continued_equation")) {
    box.textContent = object.printed_lines?.join("\n") ?? object.text_kk;
    return box;
  }
  return unsupported(object.id, "未识别的公式记法或缺少二维数据");
}

function tableOf(object, context) {
  const {row_count: rows, column_count: columns, cells} = object;
  if (!Number.isInteger(rows) || rows < 1 || !Number.isInteger(columns) || columns < 1 ||
      !Array.isArray(cells)) return unsupported(object.id, "缺少表格行列或单元格");
  const occupied = new Set();
  const orderedCells = [...cells].sort((a, b) => a.row - b.row || a.column - b.column);
  const table = el("table");
  const body = el("tbody");
  table.append(body);
  const tableRows = Array.from({length: rows}, () => body.appendChild(el("tr")));
  for (const cell of orderedCells) {
    const {row, column, rowspan, colspan} = cell;
    if (![row, column, rowspan, colspan].every(Number.isInteger) || row < 0 || column < 0 ||
        rowspan < 1 || colspan < 1 || row + rowspan > rows || column + colspan > columns) {
      return unsupported(object.id, `单元格尺寸无效 ${cell.id}`);
    }
    for (let r = row; r < row + rowspan; r++) {
      for (let c = column; c < column + colspan; c++) {
        const slot = r * columns + c;
        if (occupied.has(slot)) return unsupported(object.id, `单元格重叠 ${cell.id}`);
        occupied.add(slot);
      }
    }
    const td = el(cell.header || object.header_rows?.includes(row) ? "th" : "td");
    td.rowSpan = rowspan;
    td.colSpan = colspan;
    if (td.tagName === "TH") td.scope = object.header_rows?.includes(row) ? "col" : "row";
    context.identify(td, cell);
    const time = cell.time_interval;
    if (time) {
      if (time.minute_style !== "underlined_superscript" ||
          ![time.start, time.end].every(value => /^\d{2}:\d{2}$/.test(value))) {
        td.append(unsupported(cell.id, "时段记法"));
      } else {
        td.classList.add("time");
        for (const [i, value] of [time.start, time.end].entries()) {
          const [hour, minute] = value.split(":");
          const sup = el("sup");
          sup.append(el("u", minute));
          td.append(i ? " – " : "", String(Number(hour)), sup);
        }
      }
    } else if (!cell.empty) {
      td.textContent = cell.printed_text_kk ?? cell.text_kk ?? "";
      if (!td.textContent) td.append(unsupported(cell.id, "单元格缺少内容或空格标记"));
    }
    tableRows[row].append(td);
  }
  if (occupied.size !== rows * columns) return unsupported(object.id, "缺少单元格，无法区分遗漏与留白");
  const wrap = el("div", null, "scroller");
  wrap.tabIndex = 0;
  wrap.setAttribute("aria-label", "教材表格");
  wrap.append(table);
  return wrap;
}

function imageOf(object, context) {
  const figure = el("figure");
  const description = object.structured_description;
  const asset = context.data.crop_assets?.[object.crop_asset_id];
  const src = asset && context.image("crop", context.data.lesson.id, object.crop_asset_id);
  if (!src) {
    figure.append(unsupported(object.id, "缺少信息图裁图"));
  } else {
    const img = el("img");
    img.alt = description?.description_kk ?? "教材信息图";
    img.src = src;
    img.width = asset.bbox[2] - asset.bbox[0];
    img.height = asset.bbox[3] - asset.bbox[1];
    img.addEventListener("error", () => img.replaceWith(unsupported(object.id, "信息图资源加载失败")));
    figure.append(img);
  }
  if (description?.description_kk) {
    const caption = el("figcaption", "图示说明 · ");
    const text = el("span", description.description_kk);
    text.lang = "kk";
    caption.append(text);
    figure.append(caption);
  } else {
    figure.append(unsupported(object.id, "缺少结构化图示说明"));
  }
  for (const relation of description?.relations ?? []) {
    const path = el("div", null, "graph-link");
    if (typeof relation !== "object" || relation === null) {
      figure.append(unsupported(object.id, "图示关系记录"));
      continue;
    }
    path.append(`图示关系 · ${relation.direction ?? relation.kind ?? ""} · `);
    if (relation.from_id) path.append(context.link(relation.from_id), " → ");
    if (relation.to_id) path.append(context.link(relation.to_id));
    if (relation.target_label || relation.target_kk) path.append(relation.target_label ?? relation.target_kk);
    if (relation.explained_by_id) path.append(" · ", context.link(relation.explained_by_id));
    figure.append(path);
  }
  return figure;
}

function formulaGrouping(object, items) {
  if (!object.printed_expression_grid) return new Map();
  const rows = object.printed_expression_grid.row_major_ids;
  if (!rows?.length || !rows[0]?.length || !rows.every(row => row.length === rows[0].length)) {
    throw Error("算式网格缺少规则行列");
  }
  const ids = rows.flat();
  const start = items.findIndex(item => item.id === ids[0]);
  if (start < 0 || ids.some((id, i) => items[start + i]?.id !== id || items[start + i]?.type !== "formula")) {
    throw Error("算式网格与子对象顺序不一致");
  }
  return new Map([[start, {count: ids.length, columns: rows[0].length}]]);
}

const CONTAINERS = new Set(["module", "instructional_note", "subtask", "example", "other"]);

export function renderObject(object, context, partial = null, continuation = false) {
  const {type, id} = object;
  const wrapper = el(CONTAINERS.has(type) ? "section" : "div", null, `object ${type === "formula" ? "formula-object" : type}`);
  wrapper.lang = "kk";
  if (!continuation) context.identify(wrapper, object);
  else wrapper.dataset.continuationFor = id;
  try {
    let items = partial ?? ordered(object.elements, object.content_order);
    if (type === "formula") wrapper.append(formula(object));
    else if (type === "table") wrapper.append(tableOf(object, context));
    else if (type === "informative_image") wrapper.append(imageOf(object, context));
    else if (["module_badge", "instructional_note_badge", "badge"].includes(type)) {
      wrapper.append(el("span", object.text_kk, "badge"));
      if (object.scope_ids?.length) {
        const scope = el("span", "适用范围 · ", "scope");
        scope.append(linkedList(object.scope_ids, context, " · "));
        wrapper.append(scope);
      }
    } else if (["module_number", "subtask_number"].includes(type)) {
      wrapper.append(el("h3", object.printed_label_kk ?? object.text_kk, "number"));
    } else if (type === "text") {
      wrapper.append(object.text_kk ? numberedText(object.text_kk) : unsupported(id, "文字缺失"));
    } else if (CONTAINERS.has(type)) {
      const noteBadge = object.instructional_note_badge;
      if (noteBadge && !items.some(child => child.text_kk === noteBadge)) {
        wrapper.append(el("h2", noteBadge, "badge"));
      }
      if (type === "module" && !continuation && !items.some(child => child.type === "module_number") &&
          !items.some(child => child.type === "subtask")) {
        wrapper.append(el("h2", object.module_number, "number"));
      }
      if (type === "subtask" && !items.some(child => child.type === "subtask_number")) {
        wrapper.append(el("h3", object.printed_label_kk ?? object.subtask_label, "number"));
      }
      if (object.text_kk && object.text_kk !== noteBadge) wrapper.append(numberedText(object.text_kk));
      if (continuation) {
        const label = el("p", `第 ${object.module_number} 题 · 续`, "kicker");
        label.lang = "zh-CN";
        wrapper.append(label);
      }
    } else {
      wrapper.append(unsupported(id, type ?? "缺少对象类型"));
    }
    if (object.exercise_input_ids?.length) {
      const first = items.findIndex(item => item.id === object.exercise_input_ids[0]);
      if (first >= 0 && object.exercise_input_ids.every((id, i) => items[first + i]?.id === id)) {
        const group = el("div", null, "exercise-input");
        for (const child of items.slice(first, first + object.exercise_input_ids.length)) {
          group.append(renderObject(child, context));
        }
        items = [...items.slice(0, first), group, ...items.slice(first + object.exercise_input_ids.length)];
      } else if (!partial) wrapper.append(unsupported(id, "题目输入分组与阅读顺序不一致"));
    }
    const groups = partial ? new Map() : formulaGrouping(object, items);
    const algorithm = object.role === "printed_algorithm_steps";
    const children = algorithm ? el("ol", null, "printed-steps") : el("div");
    for (let i = 0; i < items.length;) {
      const group = groups.get(i);
      if (group) {
        const grid = el("div", null, "formula-grid");
        grid.style.setProperty("--columns", group.columns);
        for (const item of items.slice(i, i + group.count)) grid.append(renderObject(item, context));
        children.append(grid);
        i += group.count;
      } else {
        const item = items[i++];
        const rendered = item instanceof Node ? item : renderObject(item, context);
        if (algorithm) {
          const li = el("li");
          li.append(rendered);
          children.append(li);
        } else children.append(rendered);
      }
    }
    if (items.length) wrapper.append(children);
    if (type === "other" && !items.length && !object.text_kk) {
      wrapper.append(unsupported(id, "Other 没有可呈现的正文或子对象"));
    }
    if (object.worked_sequence) {
      const {steps, relationships, description_kk: description} = object.worked_sequence;
      if (!steps || steps.join() !== object.content_order?.join() ||
          (relationships ?? []).some(path => path.length < 2 || path.some(id => !steps.includes(id)))) {
        wrapper.append(unsupported(id, "算例步骤或关系不完整"));
      } else {
        const explanation = el("p", null, "graph-link");
        explanation.append("算例结构说明 · ", el("span", description));
        wrapper.append(explanation);
        for (const path of relationships ?? []) {
          const row = el("p", null, "graph-link");
          row.append(linkedList(path, context, " → "));
          wrapper.append(row);
        }
      }
    }
  } catch (error) {
    wrapper.append(unsupported(id, error.message));
  }
  if (context.gaps[id] && !continuation) wrapper.append(unsupported(id, context.gaps[id]));
  for (const warning of wrapper.querySelectorAll(".unsupported")) warning.lang = "zh-CN";
  return wrapper;
}
