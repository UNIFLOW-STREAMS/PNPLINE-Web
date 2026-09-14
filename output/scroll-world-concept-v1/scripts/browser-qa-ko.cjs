const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const root=path.resolve(__dirname,'..');
const screenshots=path.join(root,'qa/screenshots');
const url='http://127.0.0.1:8761/output/scroll-world-concept-v1/ko.html';
const expectedScenes=['중국 출발','국제 운송','미국 도착','입고 및 보관','피킹 및 포장','분기 출고'];
const report={started:new Date().toISOString(),url,browser:'Chrome via installed Playwright',checks:[],errors:[],console:[]};
fs.mkdirSync(screenshots,{recursive:true});

function check(name,ok,detail={}){report.checks.push({name,pass:!!ok,detail});if(!ok)report.errors.push(name);}

(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 report.browser_version=browser.version();
 try{
  for(const [width,height] of [[1440,900],[390,844],[360,800]]){
   const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:1});
   const page=await context.newPage();
   const pageErrors=[];
   page.on('pageerror',error=>pageErrors.push(String(error)));
   page.on('console',message=>{if(message.type()==='error')report.console.push({viewport:width,message:message.text()});});
   await page.goto(url,{waitUntil:'networkidle'});
   await page.waitForFunction(()=>window.reviewQA?.scenes.length===6);

   check(`${width}: Korean document language`,await page.locator('html').getAttribute('lang')==='ko');
   check(`${width}: no horizontal overflow`,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   check(`${width}: six scenes`,await page.locator('.scene-row').count()===6);
   check(`${width}: Korean scene names`,JSON.stringify(await page.locator('.scene-info h3').allTextContents())===JSON.stringify(expectedScenes));
   check(`${width}: no Chinese UI residue`,await page.evaluate(()=>{const clone=document.body.cloneNode(true);clone.querySelectorAll('[lang="zh-CN"]').forEach(node=>node.remove());return !/[\u4E00-\u9FFF]/.test(clone.textContent);}));
   check(`${width}: Korean CTA`,await page.locator('.scene-row .copy-part.cta').first().textContent()==='서비스 알아보기 ↗');
   check(`${width}: Korean status`,(await page.locator('#load-status').textContent()).startsWith('자산 상태: 검토 준비 완료'));
   check(`${width}: default orientation`,await page.evaluate(()=>reviewQA.state.orientation)===(width<768?'mobile':'desktop'));

   for(let i=1;i<=6;i++){
    const row=page.locator(`#scene-S0${i}`);
    await row.locator('.scene-image').evaluate(image=>image.decode());
    check(`${width}: S0${i} image decoded`,await row.locator('.scene-image').evaluate(image=>image.naturalWidth>0));
    check(`${width}: S0${i} copy bounded`,await row.locator('.frame').evaluate(frame=>[...frame.querySelectorAll('.copy-part')].every(part=>part.scrollHeight<=part.clientHeight+1&&part.scrollWidth<=part.clientWidth+1)));
   }

   await page.screenshot({path:path.join(screenshots,`ko-${width}x${height}-top.png`)});
   await page.locator('#journey').scrollIntoViewIfNeeded();
   await page.locator('#mask-toggle').check();
   await page.locator('#scene-S01').screenshot({path:path.join(screenshots,`ko-${width}x${height}-journey.png`)});
   await page.locator('#mask-toggle').uncheck();
   await page.locator('#overlay-toggle').uncheck();
   check(`${width}: copy toggle`,await page.locator('.scene-row .overlay-layer:visible').count()===0);
   await page.locator('#overlay-toggle').check();
   const other=width<768?'desktop':'mobile';
   await page.locator(`[data-orientation="${other}"]`).click();
   check(`${width}: orientation change`,await page.locator('.scene-row .frame.'+other).count()===6);

   await page.locator('#animatic').scrollIntoViewIfNeeded();
   await page.locator('#progress').fill('420');
   await page.locator('#progress').dispatchEvent('input');
   check(`${width}: Korean transition`,(await page.locator('#transition-label').textContent()).startsWith('다음 장면: '));
   await page.emulateMedia({reducedMotion:'reduce'});
   await page.locator('#progress').dispatchEvent('input');
   check(`${width}: reduced motion`,await page.locator('#motion-stage .frame').evaluate(element=>getComputedStyle(element).transform)==='none'&&await page.locator('#reduced-note').isVisible());
   await page.locator('#motion-stage').screenshot({path:path.join(screenshots,`ko-${width}x${height}-animatic.png`)});
   check(`${width}: no JavaScript errors`,pageErrors.length===0,{errors:pageErrors});
   await context.close();
  }

  const errorContext=await browser.newContext({viewport:{width:390,height:844}});
  const errorPage=await errorContext.newPage();
  await errorPage.route('**/keyframes/mobile/S01.jpg',route=>route.abort());
  await errorPage.goto(url,{waitUntil:'networkidle'});
  await errorPage.waitForFunction(()=>window.reviewQA);
  check('failed image has Korean explanation',await errorPage.locator('#scene-S01 .error-note').isVisible()&&/이미지를 현재 표시할 수 없습니다/.test(await errorPage.locator('#scene-S01 .error-note').textContent()));
  await errorPage.locator('#scene-S01').screenshot({path:path.join(screenshots,'ko-390x844-image-error.png')});
  await errorContext.close();

  const noJsContext=await browser.newContext({viewport:{width:390,height:844},javaScriptEnabled:false});
  const noJsPage=await noJsContext.newPage();
  await noJsPage.goto(url,{waitUntil:'networkidle'});
  check('JavaScript-disabled Korean fallback',await noJsPage.locator('#journey noscript a').count()===6&&/중국 출발/.test(await noJsPage.locator('#journey noscript').textContent()));
  await noJsContext.close();

  const languagePage=await browser.newPage();
  await languagePage.goto(url,{waitUntil:'networkidle'});
  await languagePage.locator('a[hreflang="zh-CN"]').click();
  check('language switch opens Chinese page',new URL(languagePage.url()).pathname.endsWith('/index.html'));
  await languagePage.close();
 }catch(error){
  report.errors.push(String(error));
 }finally{
  await browser.close();
  report.finished=new Date().toISOString();
  fs.writeFileSync(path.join(root,'qa/browser-results-ko.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify({checks:report.checks.length,failures:report.errors,console:report.console},null,2));
  if(report.errors.length)process.exitCode=1;
 }
})();
