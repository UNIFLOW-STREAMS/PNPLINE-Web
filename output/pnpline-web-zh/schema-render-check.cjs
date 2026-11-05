const {chromium} = require('playwright-core');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const normalize = text => text.replace(/\s+/g,' ').trim();
(async () => {
  const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
  try {
    const page = await browser.newPage({javaScriptEnabled:false});
    const results = [];
    for (const name of ['home','privacy']) {
      const filename = name === 'home' ? 'index' : 'privacy';
      await page.setContent(fs.readFileSync(__dirname+'/.next-production/server/app/'+filename+'.html','utf8'),{waitUntil:'domcontentloaded'});
      const scripts = page.locator('script[type="application/ld+json"]');
      assert.equal(await scripts.count(), 1, 'One JSON-LD graph per page');
      const graph = JSON.parse(await scripts.textContent());
      assert.deepEqual(graph, JSON.parse(fs.readFileSync(__dirname+'/review/schema/preview-'+name+'.json','utf8')));
      const webpage = graph['@graph'].find(n=>n['@type']==='WebPage');
      assert.equal(await page.title(), webpage.name);
      assert.equal(await page.locator('meta[name=description]').getAttribute('content'), webpage.description);
      assert.equal(await page.locator('html').getAttribute('lang'), 'zh-CN');
      assert.equal(await page.locator('link[rel=canonical]').count(),0,'Do not invent a canonical origin');
      if (name === 'home') {
        const faq = graph['@graph'].find(n=>n['@type']==='FAQPage');
        for (const question of faq.mainEntity) {
          const q = question['@id'].split('#')[1], a = question.acceptedAnswer['@id'].split('#')[1];
          const label = await page.locator('#'+q+' .faq-question-label').textContent();
          const answer = (await page.locator('#'+a+' p').allTextContents()).join(' ');
          assert.equal(normalize(label),normalize(question.name));
          assert.equal(normalize(answer),normalize(question.acceptedAnswer.text));
        }
        const serviceSection = graph['@graph'].find(n=>n['@type']==='WebPageElement');
        for (const section of serviceSection.hasPart) {
          const target = page.locator('#'+section['@id'].split('#')[1]);
          assert.equal(await target.count(),1);
          const paragraphs = await target.locator('p').allTextContents();
          assert.equal(normalize(paragraphs.join(' ')),normalize(section.text));
        }
        results.push('Home: 9 rendered FAQ question/answer pairs and 4 service descriptions exactly match JSON-LD.');
      } else {
        assert.equal(await page.locator('h1').innerText(),'您的询价信息');
        results.push('Privacy: independent WebPage and matching title/description; no homepage FAQ graph.');
      }
    }
    fs.writeFileSync(__dirname+'/review/schema/render-check.json',JSON.stringify({passed:true,results},null,2));
    console.log('PASS: built HTML, per-page metadata, JSON-LD and DOM content parity.');
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1)});
