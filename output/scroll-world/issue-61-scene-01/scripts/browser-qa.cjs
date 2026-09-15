const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");

const playwrightPath = process.env.PNPLINE_PLAYWRIGHT_PATH;
const chromePath = process.env.PNPLINE_CHROME_PATH;

if (!playwrightPath || !chromePath) {
  throw new Error("PNPLINE_PLAYWRIGHT_PATH and PNPLINE_CHROME_PATH are required");
}

const { chromium } = require(playwrightPath);
const root = path.resolve(__dirname, "..");
const previewUrl = pathToFileURL(path.join(root, "preview", "index.html")).href;
const screenshots = path.join(root, "screenshots");

async function waitForAssets(page) {
  await page.waitForFunction(() => {
    const images = [...document.images];
    return images.length >= 2 && images.every((image) => image.complete && image.naturalWidth > 0);
  });
}

async function pageMetrics(page) {
  return page.evaluate(() => ({
    innerWidth: window.innerWidth,
    innerHeight: window.innerHeight,
    scrollWidth: document.documentElement.scrollWidth,
    scrollHeight: document.documentElement.scrollHeight,
    overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    bodyOverflowFlag: document.body.dataset.horizontalOverflow,
    variant: document.body.dataset.variant,
    mode: document.body.dataset.mode,
    title: document.title,
    chineseGlyphsPresent: document.body.innerText.includes("中国发运") && document.body.innerText.includes("免费获取报价")
  }));
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: chromePath });
  const consoleErrors = [];
  const results = { tool: "Playwright with installed Chrome", checks: [], screenshots: [] };

  const desktop = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await desktop.newPage();
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });

  await page.goto(`${previewUrl}?variant=a&mode=overlay`, { waitUntil: "domcontentloaded" });
  await waitForAssets(page);
  for (const variant of ["a", "b", "c"]) {
    await page.locator(`button[data-variant="${variant}"]`).click();
    await waitForAssets(page);
    const expected = variant === "a" ? "review_pending" : "comparison_only";
    const status = await page.locator("#status-label").textContent();
    if (status !== expected) throw new Error(`Unexpected ${variant} status: ${status}`);
    const file = `desktop-${variant}-overlay-1440x900.png`;
    await page.screenshot({ path: path.join(screenshots, file) });
    results.screenshots.push(file);
    results.checks.push({ name: `desktop-${variant}-overlay`, pass: true, metrics: await pageMetrics(page) });
  }

  await page.locator('button[data-variant="a"]').click();
  await page.locator('button[data-mode="mask"]').click();
  if (await page.locator("#mask").evaluate((image) => image.naturalWidth !== 2048)) {
    throw new Error("Safe-area mask did not load with the 2048 viewBox width");
  }
  await page.screenshot({ path: path.join(screenshots, "desktop-a-mask-1440x900.png") });
  results.screenshots.push("desktop-a-mask-1440x900.png");
  results.checks.push({ name: "desktop-a-mask", pass: true, metrics: await pageMetrics(page) });

  await page.locator('button[data-mode="clean"]').click();
  await page.locator('button[data-mode="overlay"]').click();
  await page.locator('button[data-variant="a"]').click();
  results.checks.push({ name: "control-round-trip", pass: (await pageMetrics(page)).variant === "a" && (await pageMetrics(page)).mode === "overlay" });

  const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const mobilePage = await mobile.newPage();
  mobilePage.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  await mobilePage.goto(`${previewUrl}?variant=a&mode=overlay`, { waitUntil: "domcontentloaded" });
  await waitForAssets(mobilePage);
  const mobileMetrics = await pageMetrics(mobilePage);
  if (mobileMetrics.innerWidth !== 390 || mobileMetrics.innerHeight !== 844 || mobileMetrics.overflow) {
    throw new Error(`Mobile viewport mismatch or overflow: ${JSON.stringify(mobileMetrics)}`);
  }
  await mobilePage.screenshot({ path: path.join(screenshots, "mobile-a-overlay-390x844.png") });
  results.screenshots.push("mobile-a-overlay-390x844.png");
  results.checks.push({ name: "mobile-a-overlay", pass: true, metrics: mobileMetrics });

  await mobilePage.locator('button[data-variant="c"]').click();
  await mobilePage.locator('button[data-mode="mask"]').click();
  const exploratoryMetrics = await pageMetrics(mobilePage);
  results.checks.push({ name: "mobile-c-mask-exploratory", pass: !exploratoryMetrics.overflow, metrics: exploratoryMetrics });

  results.consoleErrors = consoleErrors;
  results.pass = results.checks.every((check) => check.pass) && consoleErrors.length === 0;
  fs.writeFileSync(path.join(screenshots, "browser-qa-results.json"), `${JSON.stringify(results, null, 2)}\n`, "utf8");
  await browser.close();

  if (!results.pass) process.exitCode = 1;
  console.log(JSON.stringify(results, null, 2));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
