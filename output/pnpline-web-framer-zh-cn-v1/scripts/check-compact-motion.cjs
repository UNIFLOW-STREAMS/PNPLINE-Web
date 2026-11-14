// Run against an already running local Version A Chinese site:
// node scripts/check-compact-motion.cjs [smoke|entry|full] [390,820,...]
// Override PNPLINE_TEST_URL, PNPLINE_TEST_BROWSER and PNPLINE_BROWSER_PATH as needed.
// No inquiry is sent.
const {chromium, webkit} = require('playwright-core');
const assert = require('node:assert/strict');
const baseURL = process.env.PNPLINE_TEST_URL || 'http://127.0.0.1:3322/';
const mode = process.argv[2] || 'full';
const widths = (process.argv[3] || '390,820').split(',').map(Number);
const frames = (page, count = 5) => page.evaluate(async count => {
  for (let i = 0; i < count; i++) await new Promise(requestAnimationFrame);
}, count);
async function position(locator, top = 120) {
  await locator.evaluate((element, top) =>
    window.scrollTo({top: scrollY + element.getBoundingClientRect().top - top, behavior: 'instant'}), top);
}
async function roundTrip(page, locator) {
  await position(locator, -await locator.evaluate(e => e.getBoundingClientRect().height) - 120);
  await frames(page);
  await position(locator);
  await frames(page);
}
async function installMonitor(page) {
  await page.evaluate(() => {
    const cards = [...document.querySelectorAll('main .glass, main .quote-inquiry')];
    const headings = [...document.querySelectorAll('main .chapter-heading h2, main .inquiry-intro h2')];
    const seen = new WeakSet();
    const problems = new Map();
    window.motionAudit = {stage: 'entry', problems, stopped: false, frames: 0};
    function record(type, element, opacity) {
      const section = element.closest('section[id]')?.id;
      const key = type + ':' + section + ':' + element.className;
      if (!problems.has(key)) problems.set(key, {type, section, stage: window.motionAudit.stage, opacity});
    }
    function read() {
      if (window.motionAudit.stopped) return;
      window.motionAudit.frames++;
      for (const card of cards) {
        const bounds = card.getBoundingClientRect();
        if (!bounds.height || bounds.bottom <= 85 || bounds.top >= innerHeight) continue;
        let opacity = 1;
        for (let node = card; node && node !== document.body; node = node.parentElement) {
          opacity *= +getComputedStyle(node).opacity;
        }
        if (opacity < .999) record('card-opacity', card, opacity);
      }
      for (const heading of headings) {
        const bounds = heading.getBoundingClientRect();
        const subtitle = heading.nextElementSibling;
        const bottom = subtitle?.matches('p') ? subtitle.getBoundingClientRect().bottom : bounds.bottom;
        if (!bounds.height || bottom <= 85 || bounds.top >= innerHeight) continue;
        const nodes = [heading, ...heading.querySelectorAll('.section-title-char'),
          ...(subtitle?.matches('p') ? [subtitle] : [])];
        const opacity = Math.min(...nodes.map(node => +getComputedStyle(node).opacity));
        if (opacity >= .999) seen.add(heading);
        else if (seen.has(heading)) record('heading-replay', heading, opacity);
      }
      requestAnimationFrame(read);
    }
    requestAnimationFrame(read);
  });
}
async function auditWidth(browser, width) {
  const page = await browser.newPage({
    viewport: {width, height: 844}, hasTouch: true, isMobile: true,
  });
  page.setDefaultTimeout(8000);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  // Protect against accidentally submitting a live inquiry if the server configuration changes.
  await page.route('**/v1/inquiries', route => route.abort());
  try {
    await page.goto(baseURL, {waitUntil: 'load'});
    await page.waitForFunction(() => document.querySelector('.air-site')?.dataset.heroEntrance === 'ready');
    await page.waitForTimeout(1200);
    await installMonitor(page);
    const cards = page.locator('main .glass, main .quote-inquiry');
    const cardCount = await cards.count();
    for (let i = 0; i < cardCount; i++) {
      const card = cards.nth(i);
      await position(card, 900);
      await frames(page, 3);
      await position(card, 770);
      await frames(page, 3);
      await position(card);
      await frames(page, 4);
    }
    const headings = page.locator(mode === 'smoke'
      ? '#freight-options .chapter-heading h2, #import-planning .chapter-heading h2'
      : 'main .chapter-heading h2, main .inquiry-intro h2');
    await page.evaluate(() => { window.motionAudit.stage = 'headings-return'; });
    for (let i = 0; i < await headings.count(); i++) {
      const heading = headings.nth(i);
      await position(heading);
      await page.waitForTimeout(1700);
      await roundTrip(page, heading);
    }
    console.log(JSON.stringify({width, stage: 'entry-and-return', problems: await page.evaluate(() => [...window.motionAudit.problems.values()])}));
    let detailsCount = 0, tabCount = 0;
    if (mode === 'full') {
      const sections = page.locator('main > section[id]');
      for (let s = 0; s < await sections.count(); s++) {
        const section = sections.nth(s);
        const id = await section.getAttribute('id');
        if (id === 'top' || id === 'quote') continue;
        await page.evaluate(id => { window.motionAudit.stage = id + ':interactions'; }, id);
        const tabs = section.locator('[role="tab"]').filter({visible: true});
        const count = await tabs.count();
        for (let t = 0; t < Math.max(1, count); t++) {
          if (count) {
            await tabs.nth(t).click();
            assert.equal(await tabs.nth(t).getAttribute('aria-selected'), 'true');
            tabCount++;
            const active = tabs.nth(t);
            const vertical = await active.evaluate(e => e.closest('[role=tablist]').getAttribute('aria-orientation') === 'vertical');
            await active.press(vertical ? 'ArrowDown' : 'ArrowRight');
            assert.equal(await tabs.nth((t + 1) % count).getAttribute('aria-selected'), 'true');
            await tabs.nth((t + 1) % count).press(vertical ? 'ArrowUp' : 'ArrowLeft');
            assert.equal(await active.getAttribute('aria-selected'), 'true');
          }
          const details = section.locator('details');
          const opened = [];
          for (let d = 0; d < await details.count(); d++) {
            const detail = details.nth(d);
            const summary = detail.locator(':scope > summary');
            if (!await summary.isVisible()) continue;
            if (!await detail.evaluate(e => e.open)) await summary.click();
            assert.equal(await detail.evaluate(e => e.open), true);
            opened.push(detail);
            detailsCount++;
            const parent = detail.locator('xpath=ancestor::*[contains(concat(" ", normalize-space(@class), " "), " glass ")][1]');
            await roundTrip(page, parent);
            assert.equal(await detail.evaluate(e => e.open), true, id + ': open state lost on scroll');
            await summary.focus();
            await frames(page, 2);
          }
          for (const detail of opened.reverse()) {
            const summary = detail.locator(':scope > summary');
            // Exclusive native details may have hidden an earlier nested disclosure.
            if (await detail.evaluate(e => e.open) && await summary.isVisible()) {
              await summary.press('Enter');
              assert.equal(await detail.evaluate(e => e.open), false);
            }
          }
          // Include both keyboard focus and trackpad-style pointer movement on compact cards.
          const links = section.locator('.glass a, .glass summary').filter({visible: true});
          for (let f = 0; f < Math.min(3, await links.count()); f++) {
            await links.nth(f).focus();
            await frames(page, 2);
          }
        }
        console.log(JSON.stringify({width, section: id, detailsCount, tabCount}));
      }
      await page.evaluate(() => { window.motionAudit.stage = 'quote'; });
      assert.equal(await page.locator('.inquiry-form').getAttribute('data-inquiry-step'), '1');
      await page.locator('[name=cargo]').fill('测试货物');
      await page.locator('[name=cargo]').press('Tab');
      assert.equal(await page.locator('.inquiry-form').getAttribute('data-inquiry-step'), '2');
      await page.locator('.inquiry-continue').click();
      assert.equal(await page.locator('.inquiry-form').getAttribute('data-inquiry-step'), '3');
      await roundTrip(page, page.locator('.quote-inquiry'));
      await page.locator('.inquiry-final-submit').click();
      assert.equal(await page.locator('[name=email]').getAttribute('aria-invalid'), 'true');
      assert.equal(await page.locator('[name=consent]').getAttribute('aria-invalid'), 'true');
      const summary = page.locator('.inquiry-error-summary').filter({visible: true});
      assert.equal(await summary.isVisible(), true);
      await summary.locator('button').first().click();
      assert.equal(await page.locator('[name=email]').evaluate(e => e === document.activeElement), true);
      await page.locator('[name=email]').fill('test@example.com');
      await page.locator('[name=consent]').check();
      const saved = await page.evaluate(() => sessionStorage.getItem('pnpline-inquiry-draft-zh-cn'));
      assert.ok(saved?.includes('测试货物') && saved.includes('test@example.com'));
      const footerDetails = page.locator('footer details');
      for (let i = 0; i < await footerDetails.count(); i++) {
        const summary = footerDetails.nth(i).locator(':scope > summary');
        if (!await summary.isVisible()) continue;
        await summary.click();
        assert.equal(await footerDetails.nth(i).evaluate(e => e.open), true);
        await summary.press('Enter');
        assert.equal(await footerDetails.nth(i).evaluate(e => e.open), false);
      }
      await position(page.locator('#top'), 0);
      await frames(page);
      const phoneMenu = page.locator('.mobile-menu');
      const menu = await phoneMenu.isVisible() ? phoneMenu : page.locator('.nav-links button[aria-expanded]');
      await menu.click();
      assert.equal(await menu.getAttribute('aria-expanded'), 'true');
      await menu.press('Escape');
      assert.equal(await menu.getAttribute('aria-expanded'), 'false');
      assert.equal(await page.locator('.nav-shell').evaluate(e => getComputedStyle(e).opacity), '1');
    }
    const result = await page.evaluate(() => {
      window.motionAudit.stopped = true;
      return {problems: [...window.motionAudit.problems.values()], frames: window.motionAudit.frames,
        overflow: document.documentElement.scrollWidth > innerWidth};
    });
    assert.deepEqual(errors, [], 'Browser runtime errors');
    assert.equal(result.overflow, false, 'Page horizontal overflow');
    assert.deepEqual(result.problems, [], JSON.stringify(result.problems));
    if (mode === 'full') {
      await page.reload({waitUntil: 'load'});
      await page.waitForFunction(() => document.querySelector('.inquiry-form')?.dataset.inquiryStep === '3');
      assert.equal(await page.locator('[name=cargo]').inputValue(), '测试货物');
      assert.equal(await page.locator('[name=email]').inputValue(), 'test@example.com');
    }
    console.log(JSON.stringify({PASS: width, cardCount, detailsCount, tabCount, frames: result.frames}));
  } finally { await page.close(); }
}
(async () => {
  const engine = process.env.PNPLINE_TEST_BROWSER === 'webkit' ? webkit : chromium;
  const browser = await engine.launch({
    executablePath: process.env.PNPLINE_BROWSER_PATH ||
      (engine === chromium ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : undefined),
    headless: true,
  });
  const failures = [];
  try {
    for (const width of widths) {
      try { await auditWidth(browser, width); }
      catch (error) { failures.push({width, message: error.message}); console.error('FAIL', width, error.stack); }
    }
  } finally { await browser.close(); }
  if (failures.length) process.exitCode = 1;
})().catch(error => { console.error(error); process.exitCode = 1; });

