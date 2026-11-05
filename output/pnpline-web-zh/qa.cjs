const {chromium}=require('playwright-core');
const fs=require('fs'),assert=require('assert/strict');
const out=__dirname+'/review';fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--no-proxy-server']});
 const results={browser:browser.version(),errors:[],layouts:[],checks:[]};
 try{
 const context=await browser.newContext({viewport:{width:1920,height:1080},reducedMotion:'reduce'});
 const page=await context.newPage();page.on('pageerror',e=>results.errors.push(e.message));
 await page.goto('http://127.0.0.1:3092/',{waitUntil:'networkidle'});
 assert.equal(await page.locator('html').getAttribute('lang'),'zh-CN');
 assert((await page.title()).includes('中国'));
 const ld=await page.locator('script[type="application/ld+json"]').textContent();assert(ld.includes('你们的美国仓库'));
 await page.screenshot({path:out+'/desktop-hero.png'});
 const english=await page.locator('body').innerText();
 results.englishPhrases=english.match(/[A-Za-z]+(?:\s+[A-Za-z]+){2,}/g)||[];
 for(const width of [1920,834,390,320]){
  await page.setViewportSize({width,height:width>1000?1080:844});
  for(const id of ['services','customers','freight-options','fulfillment-options','import-planning','system-connections','warehouse','process','pricing','faq','quote']){
   await page.locator('#'+id).scrollIntoViewIfNeeded();
   const fit=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
   results.layouts.push({width,id,...fit});assert(fit.scroll<=fit.width,`${width} ${id} overflows: ${fit.scroll}`);
  }
  if(width===390){await page.locator('#quote').screenshot({path:out+'/mobile-quote.png'});await page.locator('#services').screenshot({path:out+'/mobile-services.png'});}
 }
 await page.setViewportSize({width:1920,height:1080});
 await page.locator('#process').screenshot({path:out+'/desktop-process.png'});
 await page.locator('#pricing').screenshot({path:out+'/desktop-pricing.png'});
 await page.locator('.freight-picker button').nth(1).click();assert.equal(await page.locator('.freight-picker button').nth(1).getAttribute('aria-pressed'),'true');
 await page.locator('#warehouse-tab-2').click();assert.equal(await page.locator('#warehouse-tab-2').getAttribute('aria-selected'),'true');
 await page.locator('#faq-topic-1').click();await page.locator('#faq-group-1 summary').first().click();assert(await page.locator('#faq-answer-uncertain').isVisible());
 const form=page.locator('#quote');await form.getByRole('button',{name:'检查询价信息'}).click();assert(await form.getByRole('alert').isVisible());
 await form.locator('[name=cargo]').fill('服装与配件');await form.locator('[name=volume]').fill('不确定');assert(await form.locator('[name=unit]').isDisabled());
 await form.locator('[name=email]').fill('buyer@example.com');await form.locator('[name=consent]').check();
 let sent=0;page.on('request',r=>{if(r.method()==='POST'&&!r.url().includes('__next'))sent++;});
 await form.getByRole('button',{name:'检查询价信息'}).click();assert((await form.getByRole('status').innerText()).includes('未发送'));assert.equal(sent,0);
 await page.reload({waitUntil:'networkidle'});assert.equal(await form.locator('[name=cargo]').inputValue(),'服装与配件');
 await form.getByRole('button',{name:'清空表单'}).click();assert.equal(await form.locator('[name=cargo]').inputValue(),'');
 await form.locator('[name=volume]').fill('5');await form.locator('[name=unit]').selectOption('其他单位');assert(await form.locator('[name=otherUnit]').isVisible());
 await form.locator('[name=volume]').fill('-1');await form.getByRole('button',{name:'检查询价信息'}).click();assert((await form.locator('#inquiry-volume-error').innerText()).includes('大于零'));
 await page.goto('http://127.0.0.1:3092/privacy');assert((await page.locator('h1').innerText()).includes('询价'));assert(!(await page.locator('main').innerText()).includes('preview'));
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:out+'/mobile-privacy.png'});
 const mobile=await context.newPage();await mobile.setViewportSize({width:390,height:844});await mobile.goto('http://127.0.0.1:3092/',{waitUntil:'networkidle'});await mobile.getByRole('button',{name:'打开菜单'}).click();assert.equal(await mobile.getByRole('button',{name:'关闭菜单'}).getAttribute('aria-expanded'),'true');await mobile.keyboard.press('Escape');
 await mobile.screenshot({path:out+'/mobile-hero.png'});
 results.checks.push('Chinese metadata and FAQ JSON-LD','44 responsive section checks','freight and warehouse selection','FAQ topics and answer','Chinese validation','Chinese unknown volume disables units','other quantity unit','negative quantity error','no submission','draft restore and clear','privacy page','mobile menu and Escape');
 await context.close();
 const normal=await browser.newContext({viewport:{width:1920,height:1080}});const n=await normal.newPage();n.on('pageerror',e=>results.errors.push(e.message));await n.goto('http://127.0.0.1:3092/',{waitUntil:'domcontentloaded'});await n.waitForFunction(()=>document.querySelector('video')?.readyState>=2,{},{timeout:20000});await n.screenshot({path:out+'/desktop-blinds.png'});await n.waitForTimeout(1000);await n.mouse.wheel(0,3200);await n.waitForTimeout(1500);await n.screenshot({path:out+'/desktop-journey.png'});results.video=await n.locator('video').evaluate(v=>({paused:v.paused,readyState:v.readyState,time:v.currentTime}));assert(results.video.paused);assert(results.video.readyState>=2);assert(results.video.time>0);await n.mouse.wheel(0,-1500);await n.waitForTimeout(1200);const reverse=await n.locator("video").evaluate(v=>v.currentTime);assert(reverse<results.video.time);results.reverseTime=reverse;results.checks.push("wheel scroll advances and rewinds video");await normal.close();
 assert.equal(results.errors.length,0);results.passed=true;
 }finally{fs.writeFileSync(out+'/qa-results.json',JSON.stringify(results,null,2));await browser.close();console.log(JSON.stringify({passed:results.passed,layouts:results.layouts.length,checks:results.checks,errors:results.errors,video:results.video}));}
})().catch(e=>{console.error(e);process.exit(1)});
