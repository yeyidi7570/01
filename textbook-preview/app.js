import {assetUrl, el, ordered, pagesOf, renderObject} from "./render.js";

const byId = id => document.getElementById(id);
const lessonSelect = byId("lesson");
const moduleSelect = byId("module");
const audience = byId("audience");
const compare = byId("compare");
const textbook = byId("textbook");
const comparison = byId("comparison");
const lookup = byId("object-id");
const status = byId("status");
const plan = byId("plan");
const query = new URLSearchParams(location.search);
const loaded = new Map();
let catalog;
let scene;
let navigation = 0;

async function json(url, options) {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) throw Error(body.error ?? `请求失败 (${response.status})`);
  return body;
}

function message(text = "") {
  status.hidden = !text;
  status.textContent = text;
}

function prepare(data) {
  const {lesson} = data;
  const index = new Map();
  function visit(object, root, kind) {
    if (index.has(object.id)) throw Error(`重复对象 ID ${object.id}`);
    index.set(object.id, {object, root, kind});
    for (const child of object.elements ?? []) visit(child, root, child.type);
    for (const cell of object.cells ?? []) visit(cell, root, "table_cell");
  }
  visit(lesson, lesson, "lesson");
  for (const unit of lesson.units) visit(unit, unit, unit.type);
  for (const link of lesson.teaching_links ?? []) visit(link, index.get(link.parent_id)?.root, "teaching_link");
  return {data, index, units: ordered(lesson.units, lesson.content_order)};
}

function href(lessonId, objectId, selection, compareMode = compare.checked) {
  const params = new URLSearchParams({lesson: lessonId, view: audience.value});
  if (selection) params.set("module", selection);
  if (objectId) params.set("id", objectId);
  if (compareMode) params.set("compare", "1");
  return `/?${params}`;
}

function label(entry) {
  if (!entry) return "未找到对象";
  const {object, kind} = entry;
  if (kind === "lesson") return `第 ${object.number} 课`;
  if (kind === "module") return `第 ${object.module_number} 题`;
  if (kind === "instructional_note") {
    const snippet = object.elements?.find(child => child.type === "text" && child.text_kk !== object.instructional_note_badge)?.text_kk;
    return snippet ? `${object.instructional_note_badge} · ${snippet.slice(0, 40)}…`
      : (object.instructional_note_badge ?? "教学说明");
  }
  if (kind === "table") return "表格";
  const text = object.printed_label_kk ?? object.text_kk ?? object.structured_description?.description_kk;
  return text ? text.split("\n")[0].slice(0, 36) + (text.length > 36 ? "…" : "") : object.id.split(":").at(-1);
}

function linkTo(lessonId, id, text, keepSelection = false) {
  const a = el("a", text);
  const selection = keepSelection ? scene?.selection : "";
  a.href = href(lessonId, id, selection);
  a.addEventListener("click", event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    openScene(lessonId, selection, id, keepSelection);
  });
  return a;
}

function pageGroups(units) {
  const byPage = new Map();
  function add(page, fragment) {
    if (!byPage.has(page)) byPage.set(page, []);
    byPage.get(page).push(fragment);
  }
  for (const unit of units) {
    const pages = pagesOf(unit);
    const first = pages[0];
    const fragments = new Map();
    if (unit.type === "module" && pages.length > 1) {
      try {
        const children = ordered(unit.elements, unit.content_order);
        for (const child of children) {
          const [page] = pagesOf(child);
          if (!pages.includes(page) || pagesOf(child).length !== 1) throw Error("跨页子对象缺少独立页码");
          if (!fragments.has(page)) fragments.set(page, []);
          fragments.get(page).push(child);
        }
        if (!pages.every(page => fragments.has(page)) || Array.from(fragments.keys()).some((page, i) => page !== pages[i])) {
          throw Error("跨页片段顺序无法确定");
        }
      } catch (error) {
        add(first, {unit, error: error.message});
        continue;
      }
    }
    if (!fragments.size) add(first, {unit});
    for (const [page, children] of fragments) add(page, {unit, children, continuation: page !== first});
  }
  const y = (unit, page) => unit.page_refs?.find(ref => ref.pdf_page === page)?.bbox[1] ?? 0;
  for (const [page, fragments] of byPage) {
    // The Lesson order records a cross-page task only once. Place later fragments
    // among the existing same-page units using their source position.
    for (const fragment of fragments.filter(item => item.continuation)) {
      fragments.splice(fragments.indexOf(fragment), 1);
      const before = fragments.findIndex(item => y(item.unit, page) > y(fragment.unit, page));
      fragments.splice(before < 0 ? fragments.length : before, 0, fragment);
    }
  }
  return Array.from(byPage.entries()).sort(([a], [b]) => a - b);
}

function render() {
  const {data, units, index, selection, objectId, entry} = scene;
  const {lesson} = data;
  const target = selection && index.get(selection);
  const allLinks = lesson.teaching_links ?? [];
  const connected = link => {
    const endpoints = [link.from_id, link.to_id].map(id => index.get(id)?.root?.id);
    return !target || endpoints.includes(selection) || link.id === objectId;
  };
  const links = allLinks.filter(connected);
  const roots = new Set([selection]);
  if (target) {
    for (const link of links) {
      for (const id of [link.from_id, link.to_id]) {
        const item = index.get(id);
        if (item?.root.type === "instructional_note") roots.add(item.root.id);
      }
    }
  }
  const visibleUnits = target ? units.filter(unit => roots.has(unit.id)) : units;
  const context = {
    data,
    gaps: entry.gaps,
    teacher: audience.value === "teacher",
    identify(element, obj) {
      element.dataset.objectId = obj.id;
      element.id = obj.id;
      if (obj.id === objectId) {
        element.classList.add("target");
        element.tabIndex = -1;
      }
    },
    link(id) {
      const item = index.get(id);
      return item ? linkTo(lesson.id, id, label(item), true)
        : el("span", `不支持的结构 · 缺少引用 ${id}`, "unsupported");
    },
  };
  const heading = el("h1", lesson.title_kk);
  heading.lang = "kk";
  textbook.replaceChildren(el("div", `教材原文 · 第 ${lesson.number} 课`, "kicker"), heading);
  context.identify(heading, lesson);

  for (const [page, fragments] of pageGroups(visibleUnits)) {
    const source = data.pages.find(p => p.pdf_page === page);
    if (source) {
      textbook.append(el("p", `原书第 ${source.printed_page ?? "—"} 页 · PDF ${source.pdf_page}`, "page-label"));
    }
    for (const {unit, children, continuation, error} of fragments) {
      const section = renderObject(unit, context, children, continuation);
      section.classList.add("unit");
      if (error) section.prepend(el("p", `不支持的结构 · ${error}（${unit.id}）`, "unsupported"));
      textbook.append(section);
    }
  }
  if (links.length) {
    const relations = el("section");
    relations.append(el("h2", "教材教学关联"));
    for (const link of links) {
      const kind = {supports: "提供方法", uses_as_material: "引用材料"}[link.relationship];
      const row = el("div", null, "relation");
      context.identify(row, link);
      row.append(kind ?? "不支持的结构 · 教学关联", " · ", context.link(link.from_id), " → ", context.link(link.to_id));
      if (context.teacher && link.rationale_kk) {
        const p = el("p", link.rationale_kk, "original");
        p.lang = "kk";
        row.append(p);
      }
      relations.append(row);
    }
    textbook.append(relations);
  }

  comparison.hidden = !compare.checked;
  byId("reader").classList.toggle("comparing", compare.checked);
  comparison.replaceChildren();
  if (compare.checked) {
    comparison.append(el("h2", "原书对照"));
    const selectedPages = objectId && objectId !== lesson.id ? pagesOf(index.get(objectId)?.object ?? {}) : [];
    const pages = new Set(selectedPages.length ? selectedPages : visibleUnits.flatMap(pagesOf));
    for (const page of data.pages.filter(p => pages.has(p.pdf_page))) {
      const figure = el("figure");
      const image = el("img");
      image.alt = `原书第 ${page.printed_page} 页`;
      image.loading = "lazy";
      image.width = page.width;
      image.height = page.height;
      image.src = assetUrl("scan", lesson.id, page.scan_asset_id);
      image.addEventListener("error", () => image.replaceWith(el("p", "原书扫描资源加载失败。", "unsupported")));
      figure.append(image, el("figcaption", `原书第 ${page.printed_page} 页 · PDF ${page.pdf_page}`));
      comparison.append(figure);
    }
  }
}

async function openScene(lessonId, selection = "", objectId = "", keepSelection = false) {
  const turn = ++navigation;
  message();
  try {
    const entry = catalog.find(lesson => lesson.id === lessonId);
    if (!entry) throw Error(`试验目录中没有课次 ${lessonId}。`);
    if (!loaded.has(lessonId)) {
      const data = await json(assetUrl("lesson", lessonId, ""));
      loaded.set(lessonId, prepare(data));
    }
    if (turn !== navigation) return;
    const prepared = loaded.get(lessonId);
    const item = objectId ? prepared.index.get(objectId) : null;
    if (objectId && !item) throw Error(`试验目录中没有对象 ${objectId}。`);
    if (item && (!keepSelection || !selection)) {
      selection = item.root?.id === lessonId ? "" : item.root?.id ?? "";
    }
    if (selection && !prepared.units.some(u => u.id === selection)) throw Error(`试验目录中没有模块 ${selection}。`);
    scene = {...prepared, entry, selection, objectId};
    lessonSelect.value = lessonId;
    moduleSelect.replaceChildren(new Option("整课", ""));
    for (const module of entry.modules) {
      moduleSelect.add(new Option(`${module.number} · ${module.topic}`, module.id));
    }
    if (selection && !entry.modules.some(m => m.id === selection)) {
      moduleSelect.add(new Option(label(prepared.index.get(selection)), selection));
    }
    moduleSelect.value = selection;
    lookup.value = objectId;
    render();
    const focused = objectId && byId(objectId);
    if (objectId && !focused && keepSelection) return openScene(lessonId, "", objectId);
    history.replaceState(null, "", href(lessonId, objectId, selection));
    if (focused) {
      focused.focus({preventScroll: true});
      focused.scrollIntoView({block: "center"});
    } else if (objectId) message(`已定位对象 ${objectId}，其结构当前无法完整显示。`);
  } catch (error) {
    if (turn === navigation) {
      if (scene) {
        lessonSelect.value = scene.entry.id;
        moduleSelect.value = scene.selection;
      }
      message(error.message);
    }
  }
}

async function start() {
  catalog = await json("/api/catalog");
  for (const lesson of catalog) lessonSelect.add(new Option(`${lesson.number} · ${lesson.title}`, lesson.id));
  const id = query.get("id")?.trim() ?? "";
  const entry = catalog.find(l => l.id === query.get("lesson"))
    ?? catalog.find(l => l.id === id || id.startsWith(`${l.id}:`))
    ?? catalog[0];
  audience.value = query.get("view") === "teacher" ? "teacher" : "student";
  compare.checked = query.get("compare") === "1";
  byId("teaching").hidden = audience.value !== "teacher";
  const selection = query.has("lesson") ? query.get("module") ?? "" : entry.modules[0].id;
  await openScene(entry.id, selection, id, Boolean(query.get("module")));
  if (!scene) {
    const issue = status.textContent;
    await openScene(entry.id, entry.modules[0].id);
    message(issue);
  }
}

lessonSelect.addEventListener("change", () => {
  const entry = catalog.find(l => l.id === lessonSelect.value);
  openScene(entry.id, entry.modules[0].id);
});
moduleSelect.addEventListener("change", () => openScene(lessonSelect.value, moduleSelect.value));
audience.addEventListener("change", () => {
  byId("teaching").hidden = audience.value !== "teacher";
  if (scene) {
    render();
    history.replaceState(null, "", href(scene.entry.id, scene.objectId, scene.selection));
  }
});
compare.addEventListener("change", () => {
  if (scene) {
    render();
    history.replaceState(null, "", href(scene.entry.id, scene.objectId, scene.selection));
  }
});
byId("lookup").addEventListener("submit", event => {
  event.preventDefault();
  const id = lookup.value.trim();
  const entry = catalog.find(l => l.id === id || id.startsWith(`${l.id}:`));
  if (!entry) return message(`试验目录中没有对象 ${id}。`);
  openScene(entry.id, scene?.entry.id === entry.id ? scene.selection : "", id, true);
});
byId("teacher-request").addEventListener("submit", async event => {
  event.preventDefault();
  const submit = event.submitter;
  submit.disabled = true;
  plan.textContent = "正在查找教材…";
  try {
    const result = await json("/api/teaching-plan", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({request: byId("request").value}),
    });
    plan.replaceChildren();
    if (!result.references.length) {
      plan.textContent = "模拟接口未找到唯一匹配。请补充课次、题号或主题。";
      return;
    }
    const section = el("section", null, "plan-result");
    section.append(el("h3", "教材原文引用"));
    const refs = el("ul");
    for (const ref of result.references) {
      const li = el("li");
      const entry = catalog.find(l => l.id === ref.lesson_id);
      const prepared = loaded.get(ref.lesson_id);
      const text = prepared?.index.has(ref.object_id) ? label(prepared.index.get(ref.object_id)) :
        `第 ${entry.number} 课 · ${entry.modules.find(m => m.id === ref.object_id)?.topic ?? ref.object_id.split(":").at(-1)}`;
      li.append(linkTo(ref.lesson_id, ref.object_id, text));
      refs.append(li);
    }
    section.append(refs);
    for (const [field, title] of Object.entries({
      organization: "AI 教学组织建议（模拟）",
      explanation: "AI 生成讲解（模拟）",
      exercise: "AI 生成练习（模拟）",
    })) {
      if (!result.generated[field]) continue;
      const block = el("section", null, "plan-result");
      block.append(el("h3", title), el("p", result.generated[field]));
      section.append(block);
    }
    plan.append(section);
  } catch (error) {
    plan.textContent = error.message;
  } finally {
    submit.disabled = false;
  }
});

start().catch(error => message(error.message));
