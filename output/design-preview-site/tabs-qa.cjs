const {chromium}=require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const results=[],errors=[],root=__dirname;
 const check=(ok,name,detail)=>{results.push({name,pass:!!ok,detail});if(!ok)throw Error(name);};
 try{
  for(const [width,height] of [[1440,1000],[390,844]]){
   const page=await browser.newPage({viewport:{width,height}});page.on('pageerror',e=>errors.push(e.message));
   await page.goto('http://127.0.0.1:8761/output/scroll-world-concept-v1/ko.html?revision=6#basic',{waitUntil:'networkidle'});
   await page.waitForFunction(()=>window.reviewQA&&window.demoTabs);
   const prefix=width+'px';
   check(await page.locator('[role=tab]').count()===2,prefix+' has two version tabs');
   check(await page.locator('#tab-basic').getAttribute('aria-selected')==='true',prefix+' basic initially selected');
   check(await page.locator('#panel-basic').isVisible()&&!await page.locator('#panel-high-angle').isVisible(),prefix+' only basic panel visible');
   check(await page.getByText('수정 전 보기',{exact:false}).count()===0,prefix+' old-version label removed');
   check(await page.locator('a[href*="ko-v1"],a[href*="index-v1"]').count()===0,prefix+' old-version links removed');
   await page.locator('#play-animatic').click();await page.waitForTimeout(100);
   check(await page.evaluate(()=>reviewQA.state.playing),prefix+' basic playback starts');
   await page.locator('#tab-high-angle').click();
   check(await page.evaluate(()=>demoTabs.active)==='high-angle',prefix+' high-angle tab activates');
   await page.waitForFunction(()=>Math.abs(scrollY-document.querySelector('#version-switch-anchor').offsetTop)<3);
   check(await page.evaluate(()=>Math.abs(scrollY-document.querySelector('#version-switch-anchor').offsetTop)<3),prefix+' tab change resets content position');
   check(!await page.evaluate(()=>reviewQA.state.playing),prefix+' switching pauses basic playback');
   const iframe=page.locator('#high-angle-frame');await iframe.contentFrame().locator('body[data-ready=true]').waitFor();
   check(await iframe.contentFrame().locator('html').evaluate(e=>e.classList.contains('embedded')),prefix+' high-angle embedded mode');
   check(!await iframe.contentFrame().locator('.mast').isVisible()&&!await iframe.contentFrame().locator('.intro').isVisible(),prefix+' duplicate chrome hidden');
   check(await iframe.contentFrame().locator('#animatic').isVisible(),prefix+' high-angle content visible');
   await page.waitForFunction(expected=>document.querySelector('#high-angle-frame').contentWindow.studyC.state.orientation===expected,width<768?'mobile':'desktop');
   check(await iframe.evaluate((e,expected)=>e.contentWindow.studyC.state.orientation===expected,width<768?'mobile':'desktop'),prefix+' high-angle starts in matching orientation');
   check(await iframe.evaluate(e=>e.contentWindow.scrollY===0),prefix+' high-angle starts at content top');
   await iframe.contentFrame().locator('#play').click();await page.waitForTimeout(100);
   check(await iframe.evaluate(e=>e.contentWindow.studyC.state.playing),prefix+' high-angle playback starts');
   await page.locator('#tab-basic').click();
   await page.waitForFunction(()=>document.querySelector('#high-angle-frame').contentWindow.studyC.state.playing===false);
   check(await page.evaluate(()=>demoTabs.active)==='basic',prefix+' basic tab restores');
   check(!await iframe.evaluate(e=>e.contentWindow.studyC.state.playing),prefix+' switching pauses high-angle playback');
   await page.locator('#tab-basic').focus();await page.keyboard.press('ArrowRight');
   check(await page.locator('#tab-high-angle').getAttribute('aria-selected')==='true',prefix+' keyboard changes tab');
   check(await iframe.evaluate(e=>e.contentWindow.scrollY===0),prefix+' reopened high-angle starts at top');
   check(await page.evaluate(()=>Math.abs(scrollY-document.querySelector('#version-switch-anchor').offsetTop)<3),prefix+' reopened panel resets page position');
   check(await page.locator('#tab-high-angle').getAttribute('tabindex')==='0',prefix+' roving tabindex');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),prefix+' no horizontal overflow');
   await page.screenshot({path:path.join(root,'tabs-'+width+'.jpg'),quality:72,fullPage:false});
   await page.close();
  }
  const direct=await browser.newPage({viewport:{width:1280,height:900}});
  await direct.goto('http://127.0.0.1:8761/output/scroll-world-concept-v1/ko.html?revision=6#high-angle',{waitUntil:'networkidle'});
  await direct.waitForFunction(()=>window.demoTabs);
  check(await direct.evaluate(()=>demoTabs.active)==='high-angle','hash opens high-angle tab');
  await direct.close();
 }finally{
  await browser.close();
  const report={results,errors,passed:results.filter(r=>r.pass).length,total:results.length};
  fs.writeFileSync(path.join(root,'tabs-qa-results.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify({passed:report.passed,total:report.total,errors}));
 }
 if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
