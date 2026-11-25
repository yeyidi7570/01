const assert = require("node:assert/strict");
const { copyFile, mkdtemp, rm } = require("node:fs/promises");
const { tmpdir } = require("node:os");
const { join } = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");

const prefix = number => `math-2023-grade4-part1:lesson-${String(number).padStart(3, "0")}`;
const object = (page, id) => page.locator(`[data-object-id="${id}"]`);

(async () => {
  const folder = await mkdtemp(join(tmpdir(), "textbook-offline-"));
  const file = join(folder, "教材抽查 Demo.html");
  let browser;
  try {
    await copyFile(join(__dirname, "textbook-preview-offline.html"), file);
    browser = await chromium.launch({
      ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}),
    });
    const page = await browser.newPage({offline: true, viewport: {width: 1280, height: 800}});
    const external = [], errors = [];
    page.on("request", request => {
      if (!request.url().startsWith("data:") &&
          request.url().split("#")[0] !== pathToFileURL(file).href) external.push(request.url());
    });
    page.on("pageerror", error => errors.push(error.message));
    await page.goto(pathToFileURL(file).href);
    await object(page, `${prefix(1)}:m04`).waitFor();
    assert.equal(await page.locator("#comparison img").count(), 0);
    assert.equal(await page.locator("#compare").isChecked(), false);
    const time = object(page, `${prefix(1)}:m04:ex-conversion:time`);
    assert.equal(await time.locator(".vertical .cell-digit").count(), 8);
    await page.getByText("不支持的结构", {exact: false}).first().waitFor();

    await page.locator("#module").selectOption(`${prefix(1)}:m05`);
    const table = object(page, `${prefix(1)}:m05:part-a:schedule`);
    await table.waitFor();
    assert.equal(await table.locator("th,td").count(), 49);
    assert.equal(await table.locator("sup u").count(), 12);
    assert.equal(await table.locator("th:empty,td:empty").count(), 5);
    await page.locator("#compare").check();
    const scan = page.locator("#comparison img");
    await scan.scrollIntoViewIfNeeded();
    await page.waitForFunction(() => document.querySelector("#comparison img")?.naturalWidth > 0);
    assert.match(await scan.getAttribute("src"), /^data:image\/webp/);
    assert.equal(await page.locator("#textbook img").count(), 0);
    await page.locator("#compare").uncheck();
    assert.equal(await page.locator("#comparison img").count(), 0);

    for (const [number, module] of [[7, "m02"], [10, "m03"], [28, "m03"]]) {
      await page.locator("#lesson").selectOption(prefix(number));
      await object(page, `${prefix(number)}:${module}`).waitFor();
      if (number === 7) {
        assert.equal(await page.locator(`[data-continuation-for="${prefix(7)}:m02"]`).count(), 1);
      }
    }
    const route = object(page, `${prefix(28)}:m03:3А:route`);
    const image = route.locator("img");
    await page.waitForFunction(id => document.getElementById(id)?.querySelector("img")?.naturalWidth > 0,
      `${prefix(28)}:m03:3А:route`);
    assert.match(await image.getAttribute("src"), /^data:image\/png/);
    assert.match(await route.innerText(), /不支持的结构/);

    await page.locator("#audience").selectOption("teacher");
    await page.getByText("AI 教学组织 · 模拟").click();
    const request = page.getByLabel("教学请求");
    const submit = page.getByRole("button", {name: "查找教材"});
    await request.fill("展示第四课第五题");
    await submit.click();
    const called = object(page, `${prefix(4)}:m05`);
    await called.waitFor();
    assert.match(await called.innerText(), /Сандарды жаз/);
    assert.equal(await called.locator(".subtask").count(), 3);
    assert.equal(await page.locator("#plan").getByText("教材原文引用").count(), 1);
    assert.equal(await page.locator("#plan").getByText("AI 教学组织建议（模拟）", {exact: true}).count(), 1);
    await request.fill("请展示第7课第2题的跨页笔算");
    await submit.click();
    await object(page, `${prefix(7)}:m02`).waitFor();
    assert.equal(await page.locator("#plan li a").count(), 4);
    await request.fill("展示第四课第九题");
    await submit.click();
    await page.getByText("模拟接口未找到唯一匹配。", {exact: false}).waitFor();
    await page.locator("#audience").selectOption("student");
    await page.reload();
    await object(page, `${prefix(7)}:m02`).waitFor();
    assert.equal(await page.locator("#teaching").isVisible(), false);
    assert.deepEqual(external, []);
    assert.deepEqual(errors, []);
    console.log("PASS Chromium file:// offline · isolated HTML, five samples, comparison, and mock navigation");
  } finally {
    await browser?.close();
    await rm(folder, {recursive: true, force: true});
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
