const {chromium}=require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),{pathToFileURL}=require('node:url');
const root=path.resolve(__dirname),out=path.resolve(root,'..');
const checks=[],issues=[];
function check(name,pass,detail){checks.push({name,pass:!!pass,detail});if(!pass)issues.push(name);}
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  for(const [name,width,height,protocol] of [['ko',1440,900,'http'],['ko',390,844,'http'],['ko',360,800,'file'],['index',1440,900,'file']]){
   const context=await browser.newContext({viewport:{width,height}});
   const page=await context.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   const url=protocol==='file'?pathToFileURL(path.join(out,name+'.html')).href:'http://127.0.0.1:8761/output/scroll-world-concept-v1/'+name+'.html';
   const prefix=name+' '+width+' '+protocol;
   await page.goto(url,{waitUntil:'networkidle'});
   await page.waitForFunction(()=>window.reviewQA?.revision===3);
   await page.waitForFunction(()=>document.body.dataset.preloaded==='true');
   check(prefix+' no JS errors',errors.length===0,errors);
   check(prefix+' six static scenes',await page.locator('.scene-row').count()===6);
   check(prefix+' no horizontal overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   check(prefix+' independent orientations',await page.evaluate(()=>new Set(CONTINUITY_V2.assets.map(a=>a.path)).size===12));
   check(prefix+' all images decode',await page.evaluate(()=>Promise.all(CONTINUITY_V2.assets.map(a=>new Promise(resolve=>{const im=new Image();im.onload=()=>resolve(im.naturalWidth>0);im.onerror=()=>resolve(false);im.src=a.path;}))).then(v=>v.every(Boolean))));
   await page.locator('[data-orientation="desktop"]').click();
   check(prefix+' desktop six',await page.locator('.scene-row .frame.desktop').count()===6);
   await page.locator('[data-orientation="mobile"]').click();
   check(prefix+' mobile six',await page.locator('.scene-row .frame.mobile').count()===6);
   await page.locator('#overlay-toggle').uncheck();
   check(prefix+' static copy hidden',await page.locator('.scene-row .overlay-layer:visible').count()===0);
   await page.locator('#mask-toggle').check();
   check(prefix+' logo masks',await page.locator('.scene-row .frame-mask:visible').count()===6);
   await page.locator('#animatic').scrollIntoViewIfNeeded();
   for(const [value,phase,sid] of [['175','CN','S01'],['320','PACIFIC','S02'],['465','US','S03'],['610','US','S04'],['755','US','S05'],['950','US','S06']]){
    await page.locator('#progress').fill(value);await page.locator('#progress').dispatchEvent('input');
    check(prefix+' '+sid+' geography',await page.evaluate(()=>reviewQA.state.phase)===phase);
    check(prefix+' '+sid+' single active frame',await page.locator('#motion-stage .v2-frame:visible').count()===1&&await page.locator('#motion-stage .v2-frame:visible').getAttribute('data-scene')===sid);
    if(width===1440&&name==='ko')await page.locator('#motion-stage').screenshot({path:path.join(root,'qa',sid+'-desktop-browser.png')});
   }
   await page.locator('.shot-button[data-index="1"]').click();
   check(prefix+' shot navigation',await page.evaluate(()=>reviewQA.state.phase)==='PACIFIC');
   await page.locator('#animatic-orientation').selectOption(width<768?'mobile':'desktop');
   await page.locator('#animatic-copy').uncheck();
   check(prefix+' animatic image-only',await page.locator('#motion-stage .overlay-layer:visible').count()===0);
   await page.locator('#progress').focus();await page.keyboard.press('End');
   check(prefix+' keyboard End',await page.locator('#progress').inputValue()==='1000');
   await page.keyboard.press('Home');
   await page.locator('#play-animatic').click();await page.waitForTimeout(1100);
   const elapsed=Number(await page.locator('#progress').inputValue());
   check(prefix+' playback timing',elapsed>=25&&elapsed<=60,{progress:elapsed,expected:32});
   await page.locator('#play-animatic').click();const paused=await page.locator('#progress').inputValue();await page.waitForTimeout(150);
   check(prefix+' pause holds',await page.locator('#progress').inputValue()===paused);
   await page.emulateMedia({reducedMotion:'reduce'});
   await page.waitForFunction(()=>document.querySelector('#play-animatic').disabled);
   check(prefix+' reduced motion disables playback',await page.locator('#play-animatic').isDisabled());
   check(prefix+' reduced motion no camera move',await page.locator('#motion-stage .v2-frame:visible .shot-pixels').evaluate(e=>getComputedStyle(e).transform)==='none');
   await page.locator('.shot-button[data-index="2"]').click();
   await page.locator('#animatic').screenshot({path:path.join(root,'qa',prefix.replaceAll(' ','-')+'-animatic.png')});
   await context.close();
  }
  const context=await browser.newContext({viewport:{width:390,height:844}}),page=await context.newPage();
  await page.route('**/continuity-v2/keyframes/S01-mobile.jpg',route=>route.abort());
  await page.goto('http://127.0.0.1:8761/output/scroll-world-concept-v1/ko.html',{waitUntil:'networkidle'});
  await page.waitForFunction(()=>window.reviewQA);
  check('failed image readable Korean context',await page.locator('#scene-S01 .error-note').isVisible());
  await context.close();
  const nojs=await browser.newContext({javaScriptEnabled:false}),staticPage=await nojs.newPage();
  await staticPage.goto(pathToFileURL(path.join(out,'ko.html')).href,{waitUntil:'networkidle'});
  check('no JavaScript six new image links',await staticPage.locator('#journey noscript a[href*="continuity-v2"]').count()===6);
  await nojs.close();
 }catch(e){issues.push(String(e));}
 finally{await browser.close();const report={checks,issues,passed:checks.filter(c=>c.pass).length,total:checks.length,date:new Date().toISOString()};fs.writeFileSync(path.join(root,'qa/browser-results.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({passed:report.passed,total:report.total,issues}));if(issues.length)process.exitCode=1;}
})();
