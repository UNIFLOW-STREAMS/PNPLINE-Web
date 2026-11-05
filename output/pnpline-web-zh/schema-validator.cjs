// Optional online vocabulary check. Submits only generated public JSON-LD.
const {chromium} = require('playwright-core');
const fs = require('node:fs');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:900}});
    await page.goto('https://validator.schema.org/',{waitUntil:'networkidle',timeout:20000});
    await page.getByText('닫기', {exact:true}).click();
    for (const name of ['home', 'privacy']) {
      await page.locator('.CodeMirror').first().click();
      await page.keyboard.press('Control+A');
      await page.keyboard.insertText('<script type="application/ld+json">'+fs.readFileSync(__dirname+'/review/schema/configured-'+name+'.json','utf8')+'</script>');
      await page.locator('#validate-button').click();
      await page.waitForTimeout(5000);
      const text = await page.locator('body').innerText();
      assert(text.includes('오류 0개') && text.includes('경고 0개'), 'No completed validation result');
      assert(!/오류 [1-9]\d*개|경고 [1-9]\d*개/.test(text), 'Validator reported an issue');
      fs.writeFileSync(__dirname+'/review/schema/validator-'+name+'.txt',text);
      await page.screenshot({path:__dirname+'/review/schema/validator-'+name+'.png'});
      console.log(name+': Schema.org validator: 0 errors, 0 warnings (configured test origin; not a deployed URL).');
    }
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1)});
