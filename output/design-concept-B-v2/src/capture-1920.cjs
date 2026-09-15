const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const { chromium } = require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const root = path.resolve(__dirname, '..');
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const server = http.createServer((req, res) => {
  let rel;
  try { rel = decodeURIComponent(new URL(req.url, 'http://local').pathname); }
  catch { res.writeHead(400).end(); return; }
  const file = path.resolve(root, `.${rel}`);
  if (!file.startsWith(root + path.sep) || req.method !== 'GET') { res.writeHead(403).end(); return; }
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404).end(); return; }
  const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.png': 'image/png', '.webp': 'image/webp', '.md': 'text/plain; charset=utf-8' };
  res.setHeader('Content-Type', types[path.extname(file)] || 'application/octet-stream');
  res.end(fs.readFileSync(file));
});

(async () => {
  const report = { at: new Date().toISOString(), failures: [], externalRequests: [], images: [], outputs: [] };
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Users/KIM TAEHYUNG/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe' });
  try {
    const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1, locale: 'zh-CN', reducedMotion: 'reduce' });
    await context.route('**/*', route => {
      if (!route.request().url().startsWith(`${base}/`)) {
        report.externalRequests.push(route.request().url());
        return route.abort();
      }
      return route.continue();
    });
    const page = await context.newPage();
    page.on('pageerror', error => report.failures.push(String(error)));

    async function open(file) {
      await page.goto(`${base}/${file}`, { waitUntil: 'networkidle' });
      await page.evaluate(async () => {
        await document.fonts.ready;
        await Promise.all([...document.images].map(image => image.decode()));
      });
    }

    async function shot(file, selector) {
      const opts = { path: path.join(root, file), animations: 'disabled' };
      const buffer = selector
        ? await page.locator(selector).screenshot(opts)
        : await page.screenshot({ ...opts, fullPage: true });
      report.outputs.push({ file, width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20), bytes: buffer.length, sha256: hash(opts.path) });
    }

    await open('index.html');
    report.browser = browser.version();
    report.images = await page.locator('.scene-image').evaluateAll(images => images.map(image => ({
      src: image.getAttribute('src'),
      naturalWidth: image.naturalWidth,
      naturalHeight: image.naturalHeight,
      renderedWidth: Math.round(image.getBoundingClientRect().width),
      renderedHeight: image.getBoundingClientRect().height,
      loaded: image.complete,
    })));
    report.layout = await page.evaluate(() => ({
      viewportWidth: innerWidth,
      scrollWidth: document.documentElement.scrollWidth,
      scenes: document.querySelectorAll('.scene').length,
      bodyHeight: document.body.scrollHeight,
      forms: document.forms.length,
      sceneGeometry: [...document.querySelectorAll('.scene')].map(scene => {
        const outer = scene.getBoundingClientRect();
        const content = scene.querySelector('.scene-content').getBoundingClientRect();
        const image = scene.querySelector('.scene-image').getBoundingClientRect();
        const style = getComputedStyle(scene);
        return {
          id: scene.id,
          outerWidth: Math.round(outer.width),
          contentWidth: Math.round(content.width),
          contentLeft: Math.round(content.left - outer.left),
          imageWidth: Math.round(image.width),
          paddingTop: Math.round(parseFloat(style.paddingTop)),
          paddingBottom: Math.round(parseFloat(style.paddingBottom)),
        };
      }),
      solid: [...document.querySelectorAll('.solid')].map(element => ({ text: element.textContent, color: getComputedStyle(element).backgroundColor })),
      logoSources: [...document.querySelectorAll('.brand img,.official-footer-logo img')].map(element => element.getAttribute('src')),
      footerBackground: getComputedStyle(document.querySelector('.footer')).backgroundColor,
      footerOverlayColor: getComputedStyle(document.querySelector('.footer .scene-content'), '::after').backgroundColor,
      footerOverlayBlendMode: getComputedStyle(document.querySelector('.footer .scene-content'), '::after').mixBlendMode,
      faqQuoteGap: Math.round(document.querySelector('#quote .scene-content').getBoundingClientRect().top - document.querySelector('#faq .scene-content').getBoundingClientRect().bottom),
      quoteBackgroundImage: getComputedStyle(document.querySelector('#quote')).backgroundImage,
    }));

    const geometryFailure = report.layout.sceneGeometry.some(scene => {
      const fullBleedQuote = scene.id === 'quote';
      const expectedContentWidth = fullBleedQuote ? 1920 : 1440;
      const expectedContentLeft = fullBleedQuote ? 0 : 240;
      return scene.outerWidth !== 1920 ||
        scene.contentWidth !== expectedContentWidth ||
        scene.contentLeft !== expectedContentLeft ||
        scene.imageWidth !== expectedContentWidth ||
        scene.paddingTop !== 32 ||
        scene.paddingBottom !== 32;
    });
    if (report.layout.viewportWidth !== 1920 || report.layout.scrollWidth !== 1920 || report.layout.scenes !== 13 || geometryFailure) {
      report.failures.push('Unexpected 1920/1440/240/32 layout geometry');
    }
    if (report.layout.solid.some(item => item.color !== 'rgb(0, 127, 168)')) report.failures.push('CTA token mismatch');
    if (report.layout.footerBackground !== 'rgb(8, 42, 69)' || report.layout.footerOverlayColor !== 'rgb(8, 42, 69)' || report.layout.footerOverlayBlendMode !== 'lighten') report.failures.push('Footer #082A45 treatment mismatch');
    if (report.layout.faqQuoteGap !== 64 || !report.layout.quoteBackgroundImage.includes('rgb(243, 248, 250)') || !report.layout.quoteBackgroundImage.includes('rgb(8, 42, 69)')) report.failures.push('FAQ-to-quote 64px light gap mismatch');
    if (report.images.some(image => !image.loaded || image.renderedWidth !== (image.src === '08-quote.png' ? 1920 : 1440))) report.failures.push('Image load or content-width failure');

    report.logo = {
      source: 'F:/pnpline-landing/resources/logo/PNP-LINE.webp',
      sha256: hash('F:/pnpline-landing/resources/logo/PNP-LINE.webp'),
      packagedSha256: hash(path.join(root, 'assets/PNP-LINE.webp')),
    };
    if (report.logo.sha256 !== report.logo.packagedSha256) report.failures.push('Official logo mismatch');

    await shot('00-fullpage.png');
    await shot('review/hero-1920.png', '#hero');
    await shot('review/services-1920.png', '#services');
    await shot('review/service-details-1920.png', '#service-details');
    await shot('review/service-support-1920.png', '#service-support');
    await shot('review/channels-1920.png', '#channels');
    await shot('review/warehouse-responsibility-1920.png', '#warehouse-evidence');
    await shot('review/wms-system-1920.png', '#system');
    await shot('review/policy-customs-1920.png', '#policy-customs');
    await shot('review/faq-1920.png', '#faq');
    await shot('review/quote-1920.png', '#quote');
    await shot('review/footer-1920.png', '#footer');

    await open('states.html');
    await shot('review/form-states-1920.png', '.state-board');
    await open('review.html');
    await shot('review/contact-sheet-1920.png');

    fs.writeFileSync(path.join(root, 'review/capture-report.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify(report, null, 2));
    if (report.failures.length || report.externalRequests.length) process.exitCode = 1;
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => {
  console.error(error);
  server.close();
  process.exitCode = 1;
});
