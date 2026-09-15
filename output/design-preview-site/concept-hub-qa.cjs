const { chromium } = require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path = require('path');

const root = 'F:/pnpline-landing/output/scroll-world-concept-v1';
const url = process.env.CONCEPT_HUB_URL || 'http://127.0.0.1:8761/output/scroll-world-concept-v1/index.html?revision=11';

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  const errors = [];
  const failedResponses = [];
  page.on('pageerror', error => errors.push(String(error)));
  page.on('response', response => { if (response.status() >= 400) failedResponses.push({ status: response.status(), url: response.url() }); });

  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await page.locator('#view-a-site iframe').waitFor({ state: 'visible' });
  await page.waitForFunction(() => document.querySelector('#view-a-site iframe').contentDocument?.readyState === 'complete');
  const results = { initialHash: new URL(page.url()).hash, tabs: {} };

  results.tabs.a = {
    selected: await page.locator('#tab-a').getAttribute('aria-selected'),
    siteTitle: await page.locator('#view-a-site iframe').evaluate(frame => frame.contentDocument?.title)
  };

  await page.locator('#tab-a-keyframes').click();
  await page.waitForFunction(() => document.querySelector('#view-a-keyframes iframe').contentDocument?.querySelector('#version-tabs'));
  results.tabs.keyframes = {
    hash: new URL(page.url()).hash,
    title: await page.locator('#view-a-keyframes iframe').evaluate(frame => frame.contentDocument?.title),
    versions: await page.locator('#view-a-keyframes iframe').evaluate(frame => frame.contentDocument?.querySelectorAll('#version-tabs [role="tab"]').length)
  };

  const keyframes = page.frameLocator('#view-a-keyframes iframe');
  await keyframes.locator('#tab-high-angle').click();
  const highAngle = keyframes.frameLocator('#high-angle-frame');
  await highAngle.locator('#animatic').waitFor({ state: 'visible' });
  await highAngle.locator('#world-image').evaluate(image => image.complete && image.naturalWidth);
  results.tabs.highAngle = await highAngle.locator('body').evaluate(() => ({
    title: document.title,
    logoWidth: document.querySelector('.mast img')?.naturalWidth,
    worldWidth: document.querySelector('#world-image')?.naturalWidth,
    frameCount: document.querySelectorAll('.us-frame img').length
  }));

  await page.locator('#tab-b').click();
  await page.locator('#panel-b img').waitFor({ state: 'visible' });
  results.tabs.b = await page.locator('#panel-b img').evaluate(img => ({ hash: location.hash, width: img.naturalWidth, height: img.naturalHeight }));

  await page.locator('#tab-c').click();
  await page.waitForFunction(() => document.querySelector('#panel-c iframe').contentWindow?.location.pathname.includes('/concepts/c/'));
  await page.waitForFunction(() => document.querySelector('#panel-c iframe').contentDocument?.title.includes('PNPLINE'));
  results.tabs.c = {
    hash: new URL(page.url()).hash,
    title: await page.locator('#panel-c iframe').evaluate(frame => frame.contentDocument?.title)
  };

  await page.locator('#tab-d').click();
  await page.locator('#panel-d img').waitFor({ state: 'visible' });
  results.tabs.d = await page.locator('#panel-d img').evaluate(img => ({ hash: location.hash, width: img.naturalWidth, height: img.naturalHeight }));

  await page.locator('#tab-a').focus();
  await page.keyboard.press('ArrowRight');
  results.keyboard = {
    focused: await page.evaluate(() => document.activeElement?.id),
    selected: await page.locator('[role="tab"][aria-selected="true"]').first().getAttribute('id')
  };

  await page.goto(`${url}#a-site`, { waitUntil: 'domcontentloaded' });
  await page.screenshot({ path: path.join(root, 'concept-hub-1440.jpg'), type: 'jpeg', quality: 86 });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload({ waitUntil: 'domcontentloaded' });
  results.mobile = await page.evaluate(() => ({ viewport: innerWidth, bodyWidth: document.body.scrollWidth, navWidth: document.querySelector('.concept-nav').scrollWidth, visiblePanel: document.querySelector('.concept-panel:not([hidden])')?.id }));
  await page.screenshot({ path: path.join(root, 'concept-hub-390.jpg'), type: 'jpeg', quality: 86 });

  if (errors.length || failedResponses.length) throw new Error(JSON.stringify({ errors, failedResponses }));
  if (results.tabs.keyframes.versions !== 2 || !results.tabs.highAngle.logoWidth || !results.tabs.highAngle.worldWidth || results.tabs.highAngle.frameCount < 7 || !results.tabs.b.width || !results.tabs.d.width || results.mobile.bodyWidth !== 390) throw new Error(JSON.stringify(results));
  console.log(JSON.stringify({ ...results, errors, failedResponses }, null, 2));
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
