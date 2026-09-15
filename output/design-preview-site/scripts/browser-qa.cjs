const fs=require('node:fs');const path=require('node:path');
const {chromium}=require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..');const screenshots=path.join(root,'qa/screenshots');fs.mkdirSync(screenshots,{recursive:true});
const report={started:new Date().toISOString(),url:'http://127.0.0.1:8761/output/scroll-world-concept-v1/',browser:'Chrome via installed Playwright',head:'89f99568d3216814d1b57334bf467a3fdca8ddca',checks:[],errors:[],console:[]};
function check(name,ok,detail={}){report.checks.push({name,pass:!!ok,detail});if(!ok)report.errors.push(name);}
(async()=>{const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});report.browser_version=browser.version();
try{
 for(const [width,height] of [[1440,900],[390,844],[360,800]]){
  const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:1});const page=await context.newPage();const errs=[];page.on('pageerror',e=>errs.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.console.push({viewport:width,message:m.text()})});
  await page.goto(report.url,{waitUntil:'networkidle'});await page.waitForFunction(()=>window.reviewQA?.scenes.length===6);
  check(`${width}: no horizontal overflow`,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));check(`${width}: 6 static scenes`,await page.locator('.scene-row').count()===6);
  await page.screenshot({path:path.join(screenshots,`${width}x${height}-overview.png`)});
  await page.locator('#journey').scrollIntoViewIfNeeded();
  check(`${width}: default orientation`,await page.evaluate(()=>reviewQA.state.orientation)===(width<768?'mobile':'desktop'));
  await page.locator('#mask-toggle').check();
  for(let i=1;i<=6;i++){
   const row=page.locator(`#scene-S0${i}`);await row.scrollIntoViewIfNeeded();await row.locator('.scene-image').evaluate(im=>im.decode());
   check(`${width}: S0${i} image decoded`,await row.locator('.scene-image').evaluate(im=>im.naturalWidth>0));
   check(`${width}: S0${i} overlay bounded`,await row.locator('.frame').evaluate(f=>[...f.querySelectorAll('.copy-part')].every(p=>p.scrollHeight<=p.clientHeight+1&&p.scrollWidth<=p.clientWidth+1)));
   if(i===1||i===4||i===5||i===6)await row.screenshot({path:path.join(screenshots,`${width}x${height}-S0${i}-overlay-mask.png`)});
  }
  await page.locator('#mask-toggle').uncheck();await page.locator('#overlay-toggle').uncheck();check(`${width}: clean toggle`,await page.locator('.scene-row .overlay-layer:visible').count()===0);await page.locator('#overlay-toggle').check();
  const other=width<768?'desktop':'mobile';await page.locator(`[data-orientation="${other}"]`).click();check(`${width}: orientation change`,await page.locator('.scene-row .frame.'+other).count()===6);await page.locator(`[data-orientation="${width<768?'mobile':'desktop'}"]`).click();
  await page.locator('#animatic').scrollIntoViewIfNeeded();await page.locator('#progress').focus();await page.keyboard.press('End');check(`${width}: keyboard End`,await page.locator('#progress').inputValue()==='1000');await page.keyboard.press('Home');await page.keyboard.press('ArrowRight');check(`${width}: keyboard arrow`,await page.locator('#progress').inputValue()==='1');
  const focus=await page.locator('#progress').evaluate(e=>({active:document.activeElement===e,outline:getComputedStyle(e).outlineStyle}));check(`${width}: visible keyboard focus`,focus.active&&focus.outline!=='none',focus);
  for(let boundary=1;boundary<=5;boundary++){
   const value=Math.round(boundary*1000/6);
   for(const delta of [-2,2]){await page.locator('#progress').fill(String(value+delta));await page.locator('#progress').dispatchEvent('input');await page.locator('#motion-stage .scene-image').evaluate(im=>im.decode());const occlusion=await page.locator('.occluder').evaluate(e=>({offset:new DOMMatrixReadOnly(getComputedStyle(e).transform).m41,width:e.getBoundingClientRect().width}));check(`${width}: boundary ${boundary}/${delta} occlusion`,1-Math.abs(occlusion.offset)/occlusion.width>=.75,{coveredFraction:1-Math.abs(occlusion.offset)/occlusion.width});}
   if(width===1440){await page.locator('#motion-stage').screenshot({path:path.join(screenshots,`desktop-boundary-${boundary}.png`)});}
  }
  await page.locator('#progress').fill('420');await page.locator('#progress').dispatchEvent('input');await page.locator('#animatic-mask').check();await page.locator('#animatic-copy').uncheck();check(`${width}: animatic clean toggle`,await page.locator('#motion-stage .overlay-layer:visible').count()===0);await page.locator('#animatic-copy').check();check(`${width}: animatic mask`,await page.locator('#motion-stage .frame-mask').isVisible());
  await page.locator('#motion-stage').screenshot({path:path.join(screenshots,`${width}x${height}-animatic.png`)});
  const before=await page.evaluate(()=>scrollY);await page.mouse.wheel(0,200);await page.waitForTimeout(100);check(`${width}: natural wheel`,await page.evaluate(()=>scrollY)>before);
  // Off-happy path 1: reduced motion, including live preference change.
  await page.emulateMedia({reducedMotion:'reduce'});await page.locator('#progress').fill('500');await page.locator('#progress').dispatchEvent('input');check(`${width}: reduced-motion no transform`,await page.locator('#motion-stage .frame').evaluate(e=>getComputedStyle(e).transform)==='none');check(`${width}: reduced-motion all static scenes`,await page.locator('.scene-row').count()===6&&await page.locator('#reduced-note').isVisible());await page.locator('#animatic').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(screenshots,`${width}x${height}-reduced-motion.png`)});
  check(`${width}: no JS errors`,errs.length===0,{errors:errs});await context.close();
 }
 // Off-happy path 2: actual failed image request, usable text and no exception.
 const context=await browser.newContext({viewport:{width:390,height:844}});const page=await context.newPage();await page.route('**/keyframes/mobile/S01.jpg',r=>r.abort());await page.goto(report.url,{waitUntil:'networkidle'});await page.waitForFunction(()=>window.reviewQA);await page.locator('#scene-S01').scrollIntoViewIfNeeded();check('image failure gives readable stage explanation',await page.locator('#scene-S01 .error-note').isVisible());await page.locator('#scene-S01').screenshot({path:path.join(screenshots,'390x844-image-error.png')});await context.close();
 // Off-happy path 3: JavaScript disabled retains all six explicit still links.
 const nojs=await browser.newContext({viewport:{width:390,height:844},javaScriptEnabled:false});const nojsPage=await nojs.newPage();await nojsPage.goto(report.url,{waitUntil:'networkidle'});check('JavaScript-disabled six still links',await nojsPage.locator('noscript a').count()===6);await nojsPage.locator('noscript p').scrollIntoViewIfNeeded();await nojsPage.screenshot({path:path.join(screenshots,'390x844-no-javascript.png')});await nojs.close();
 // Links and every actual image path are fetched from the HTTP review root.
 const page2=await browser.newPage();await page2.goto(report.url,{waitUntil:'networkidle'});await page2.waitForFunction(()=>window.reviewQA);const urls=await page2.evaluate(()=>[...new Set([...document.querySelectorAll('[href]')].map(e=>e.getAttribute('href')).filter(h=>h&&!h.startsWith('#')&&!h.startsWith('http')&&!h.startsWith('data:')))]);for(const href of urls){const r=await page2.request.get(new URL(href,report.url).href);check('link '+href,r.ok(),{status:r.status()});}
 await page2.close();
}catch(e){report.errors.push(String(e));}finally{await browser.close();report.finished=new Date().toISOString();fs.writeFileSync(path.join(root,'qa/browser-results.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({checks:report.checks.length,failures:report.errors,console:report.console},null,2));if(report.errors.length)process.exitCode=1;}
})();
