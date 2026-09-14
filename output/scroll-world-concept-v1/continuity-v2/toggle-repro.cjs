const { chromium } = require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const chrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const url = 'http://127.0.0.1:8761/output/scroll-world-concept-v1/ko.html?revision=2#animatic';

async function inspect(page) {
  return page.locator('#motion-stage .v2-frame:not([hidden])').evaluate((frame) => {
    const copy = frame.querySelector('.v2-copybar');
    const mask = frame.querySelector('.frame-mask');
    const image = frame.querySelector('.shot-pixels');
    const copyRect = copy?.getBoundingClientRect();
    const imageRect = image?.getBoundingClientRect();
    return {
      copyHidden: copy?.hidden,
      copyDisplay: copy ? getComputedStyle(copy).display : null,
      copyInsideImage: Boolean(copyRect && imageRect && copyRect.top < imageRect.bottom && copyRect.bottom > imageRect.top),
      maskDisplay: mask ? getComputedStyle(mask).display : null,
      maskBadgeVisible: Boolean(image && getComputedStyle(image, '::after').content !== 'none'),
    };
  });
}

async function runViewport(browser, viewport) {
  const page = await browser.newPage({ viewport });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.locator('#animatic').scrollIntoViewIfNeeded();
  await page.waitForFunction(() => window.reviewQA?.revision === 3);
  await page.locator('.shot-button[data-index="0"]').click();

  const copyControl = page.locator('#animatic-copy');
  const maskControl = page.locator('#animatic-mask');
  await copyControl.check();
  await maskControl.uncheck();
  const initial = await inspect(page);

  await page.locator('label:has(#animatic-copy)').click();
  const copyOff = await inspect(page);
  await page.locator('label:has(#animatic-copy)').click();
  const copyOn = await inspect(page);

  await page.locator('label:has(#animatic-mask)').click();
  const maskOn = await inspect(page);

  const failures = [];
  if (!initial.copyInsideImage) failures.push('문구가 활성 프레임 이미지 내부에 표시되지 않음');
  if (!(copyOff.copyHidden && copyOff.copyDisplay === 'none')) failures.push('문구 끄기 동작이 화면에 반영되지 않음');
  if (copyOn.copyHidden || copyOn.copyDisplay === 'none' || !copyOn.copyInsideImage) failures.push('문구 켜기 동작이 명확히 보이지 않음');
  if (maskOn.maskDisplay === 'none') failures.push('보호 영역 도형이 표시되지 않음');
  if (!maskOn.maskBadgeVisible) failures.push('보호 영역 활성 상태가 명확히 보이지 않음');

  await page.locator('#motion-stage').screenshot({
    path: `output/scroll-world-concept-v1/continuity-v2/qa/toggles-${viewport.width}.png`,
  });
  await page.close();
  return { viewport, initial, copyOff, copyOn, maskOn, failures };
}

(async () => {
  const browser = await chromium.launch({ executablePath: chrome, headless: true });
  const results = [];
  try {
    results.push(await runViewport(browser, { width: 1440, height: 1000 }));
    results.push(await runViewport(browser, { width: 390, height: 844 }));
  } finally {
    await browser.close();
  }
  console.log(JSON.stringify(results, null, 2));
  if (results.some((result) => result.failures.length)) process.exit(1);
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
