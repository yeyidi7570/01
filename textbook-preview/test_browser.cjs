const assert = require("node:assert/strict");
const { chromium } = require("playwright");

const base = process.env.PREVIEW_URL ?? "http://127.0.0.1:8765";
const prefix = number => `math-2023-grade4-part1:lesson-${String(number).padStart(3, "0")}`;
const object = (page, id) => page.locator(`[data-object-id="${id}"]`);
const viewports = [
  {name: "projection", width: 1280, height: 720},
  {name: "tablet", width: 768, height: 1024},
  {name: "browser", width: 1440, height: 900},
];

async function open(page, lesson, key) {
  const id = prefix(lesson);
  await page.goto(`${base}/?${new URLSearchParams({lesson: id, module: `${id}:${key}`})}`);
  await object(page, `${id}:${key}`).waitFor();
}

async function assertFits(page) {
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
    "Page content must stay within the viewport");
}

async function assertOrder(page, ids) {
  const order = await page.locator("#textbook [data-object-id]").evaluateAll(nodes =>
    nodes.map(node => node.dataset.objectId));
  let previous = -1;
  for (const id of ids) {
    const current = order.indexOf(id);
    assert.ok(current > previous, `Missing or out-of-order object ${id}`);
    previous = current;
  }
}

async function screens(page, name) {
  if (process.env.PREVIEW_SCREENSHOTS) {
    await page.screenshot({path: `${process.env.PREVIEW_SCREENSHOTS}/${name}.png`});
  }
}

async function verifySamples(page, viewport) {
  const requests = [];
  const errors = [];
  page.on("request", request => requests.push(new URL(request.url()).pathname));
  page.on("pageerror", error => errors.push(error.message));

  await open(page, 1, "m04");
  const first = prefix(1);
  const time = object(page, `${first}:m04:ex-conversion:time`);
  assert.equal(await time.locator(".vertical .cell-digit").count(), 8);
  assert.match(await time.locator(".vertical").innerText(), /2\s*1\s*5/);
  assert.equal(await time.locator(".cell-rule").evaluate(node => node.style.gridColumnEnd), "span 4");
  const ys = await time.locator(".vertical > span").evaluateAll(nodes =>
    nodes.filter(node => node.style.gridRowStart === "4").map(node => node.getBoundingClientRect().top));
  assert.ok(ys.length > 4 && Math.max(...ys) - Math.min(...ys) < 1, "All cells on the result row share a baseline");
  assert.equal(await object(page, `${first}:m04`).locator(".formula-grid > div").count(), 4);
  assert.equal(await object(page, `${first}:m04:ex-conversion`).getByRole("listitem").count(), 3);
  assert.equal(await object(page, `${first}:m04:ex-borrow:first-layout`).locator(".vertical").innerText().then(t => t.includes("31")), false);
  assert.equal(await page.locator("#comparison img").count(), 0);
  assert.ok(!requests.includes("/api/scan"));
  await assertFits(page);
  await time.scrollIntoViewIfNeeded();
  await screens(page, `${viewport.name}-formula`);

  await page.locator("#module").selectOption(`${first}:m05`);
  const tableId = `${first}:m05:part-a:schedule`;
  const table = object(page, tableId);
  await table.waitFor();
  assert.equal(await table.locator("tr").count(), 7);
  assert.equal(await table.locator("th,td").count(), 49);
  assert.equal(await table.locator("sup u").count(), 12);
  assert.ok(await table.locator("th:empty,td:empty").count() === 5);
  const cellId = `${tableId}:r2c7`;
  await page.locator("#object-id").fill(cellId);
  await page.getByRole("button", {name: "定位"}).click();
  await object(page, cellId).locator("xpath=self::*[contains(@class, 'target')]").waitFor();
  assert.equal(await page.locator("#textbook .relation").count(), 2);
  await assertFits(page);
  await screens(page, `${viewport.name}-table`);
  await page.locator("#compare").check();
  await page.waitForFunction(() => {
    const image = document.querySelector("#comparison img");
    return image?.complete && image.naturalWidth > 0;
  });
  assert.equal(await page.locator("#comparison figure").count(), 1);
  assert.ok(requests.includes("/api/scan"));
  await assertFits(page);
  await page.locator("#compare").uncheck();

  await page.locator("#lesson").selectOption(prefix(7));
  const seventh = prefix(7);
  await object(page, `${seventh}:m02`).waitFor();
  await assertOrder(page, ["m02:prompt", "note-addition", "m02:continuation", "note-subtraction"].map(k => `${seventh}:${k}`));
  assert.equal(await page.locator(`[data-continuation-for="${seventh}:m02"]`).count(), 1);
  assert.equal(await object(page, `${seventh}:note-subtraction:algorithm`).getByRole("listitem").count(), 7);
  const borrow = object(page, `${seventh}:note-subtraction:example-3:calculation`);
  assert.equal(await borrow.locator(".cell-marker").getByText("10", {exact: true}).evaluate(node => node.style.gridColumnStart), "5");
  await assertFits(page);
  await screens(page, `${viewport.name}-cross-page`);

  await open(page, 10, "m03");
  const tenth = prefix(10);
  await assertOrder(page, ["note-volume-units", "m03:part-a", "m03:part-ae", "m03:part-b"].map(k => `${tenth}:${k}`));
  assert.match(await object(page, `${tenth}:m03:part-b:conversion-4`).innerText(), /□ см³ = □ мм³/);
  assert.match(await object(page, `${tenth}:m03:part-ae`).innerText(), /不支持的结构.*缺少公式网格字段/);
  assert.equal(await page.locator("#textbook .relation").getByText("提供方法", {exact: false}).count(), 1);
  await assertFits(page);

  await open(page, 28, "m03");
  const twentyEighth = prefix(28);
  const routes = object(page, `${twentyEighth}:m03`).locator("figure img");
  assert.equal(await routes.count(), 3);
  await page.waitForFunction(() => Array.from(document.querySelectorAll(".module figure img"))
    .every(img => img.complete && img.naturalWidth === img.width && img.naturalWidth > 0));
  const routeId = `${twentyEighth}:m03:3А:route`;
  assert.match(await object(page, routeId).locator("figcaption").innerText(), /S = 320 км/);
  assert.match(await object(page, routeId).innerText(), /不支持的结构.*括号/);
  assert.match(await routes.first().getAttribute("src"), /\/api\/crop/);
  assert.match(await object(page, `${twentyEighth}:m03:3Ә:number`).innerText(), /^ә\)$/);
  await assertFits(page);
  await object(page, routeId).scrollIntoViewIfNeeded();
  await screens(page, `${viewport.name}-image`);

  await page.locator("#audience").selectOption("teacher");
  await page.getByText("AI 教学组织 · 模拟").click();
  await page.getByLabel("教学请求").fill("请按第7课第2题讲解多位数笔算借位");
  await page.getByRole("button", {name: "查找教材"}).click();
  await page.getByRole("heading", {name: "教材原文引用"}).waitFor();
  assert.equal(await page.locator("#plan li a").count(), 4);
  for (const label of ["组织建议", "生成讲解", "生成练习"]) {
    assert.equal(await page.locator("#plan").getByRole("heading", {name: new RegExp(label)}).count(), 1);
  }
  const exercise = await page.locator("#plan section").filter({has: page.getByRole("heading", {name: "AI 生成练习（模拟）"})})
    .last().locator("p").innerText();
  assert.ok(!(await page.locator("#textbook").innerText()).includes(exercise));
  await page.locator("#plan li a").nth(3).click();
  await object(page, `${seventh}:note-subtraction`).waitFor();
  assert.match(await page.url(), /note-subtraction/);
  await page.locator("#audience").selectOption("student");
  assert.equal(await page.locator("#teaching").isVisible(), false);
  assert.deepEqual(errors, []);

  const direct = `${tenth}:m03:part-b:conversion-4`;
  await page.goto(`${base}/?${new URLSearchParams({id: direct})}`);
  await page.locator(".target").waitFor();
  assert.equal(await page.locator(".target").getAttribute("id"), direct);
}

async function verifyIncompleteStructures(page) {
  const first = prefix(1);
  await page.route("**/api/lesson?*", async route => {
    const response = await route.fetch();
    const data = await response.json();
    const module = data.lesson.units.find(x => x.id === `${first}:m05`);
    const subtask = module.elements.find(x => x.type === "subtask");
    const table = subtask.elements.find(x => x.type === "table");
    const top = table.cells.find(x => x.row === 0 && x.column === 0);
    table.cells = table.cells.filter(x => !(x.row === 0 && x.column === 1));
    top.colspan = 2;
    const firstBody = table.cells.find(x => x.row === 1 && x.column === 0);
    table.cells = table.cells.filter(x => !(x.row === 2 && x.column === 0));
    firstBody.rowspan = 2;
    const bad = {...table, id: `${subtask.id}:missing-grid`};
    delete bad.cells;
    const unknown = {id: `${subtask.id}:mystery`, type: "new_object_type", elements: []};
    subtask.elements.push(bad, unknown);
    subtask.content_order.push(bad.id, unknown.id);
    await route.fulfill({response, json: data});
  });
  await open(page, 1, "m05");
  const tableId = `${first}:m05:part-a:schedule`;
  assert.equal(await object(page, `${tableId}:r1c1`).getAttribute("colspan"), "2");
  assert.equal(await object(page, `${tableId}:r2c1`).getAttribute("rowspan"), "2");
  for (const [key, reason] of [["missing-grid", "缺少表格行列或单元格"], ["mystery", "new_object_type"]]) {
    const unsupported = object(page, `${first}:m05:part-a:${key}`);
    assert.ok((await unsupported.innerText()).includes(`不支持的结构 · ${reason}`));
    assert.equal(await unsupported.locator("img").count(), 0);
  }
}

(async () => {
  const browser = await chromium.launch({
    ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}),
    args: ["--no-sandbox"],
  });
  try {
    for (const viewport of viewports) {
      const page = await browser.newPage({viewport: {width: viewport.width, height: viewport.height}});
      await verifySamples(page, viewport);
      console.log(`PASS ${viewport.name} ${viewport.width}×${viewport.height} · five modules, navigation and mock API`);
      await page.close();
    }
    const page = await browser.newPage();
    await verifyIncompleteStructures(page);
    console.log("PASS table spans and explicit unsupported structures");
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
