const {chromium}=require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),results=[],errors=[];
 const check=(pass,name)=>{results.push({name,pass:!!pass});if(!pass)throw Error(name);};
 try{
  for(const orientation of ['desktop','mobile']){
   const page=await browser.newPage({viewport:orientation==='desktop'?{width:1440,height:1080}:{width:390,height:844}});
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto('http://127.0.0.1:8761/output/scroll-world-concept-v1/ko.html?revision=7#basic',{waitUntil:'networkidle'});
   await page.waitForFunction(()=>document.body.dataset.preloaded==='true');
   check(await page.evaluate(()=>reviewQA.errors.length===0),orientation+' assets decode');
   check(await page.evaluate(()=>reviewQA.state.activeKey.startsWith('INTRO')),orientation+' starts with intro');
   check(await page.locator('.intro-keyframe').count()===3,orientation+' three review keyframes');
   check(await page.evaluate(()=>reviewQA.duration===34.5),orientation+' duration includes intro');
   const seek=async seconds=>{await page.locator('#progress').evaluate((e,t)=>{e.value=String(Math.round(t/34.5*1000));e.dispatchEvent(new Event('input',{bubbles:true}));},seconds);};
   for(const [name,seconds] of [['logo',0],['expansion',1.9],['harbor',3.9],['handoff',4.48]]){
    await seek(seconds);await page.locator('#motion-stage').scrollIntoViewIfNeeded();
    await page.locator('#motion-stage').screenshot({path:path.join(__dirname,orientation+'-'+name+'.jpg'),type:'jpeg',quality:85});
   }
   await seek(0);
   const initial=await page.locator('#motion-stage>.brand-intro').getAttribute('data-zoom');await seek(1.9);
   check(Number(await page.locator('#motion-stage>.brand-intro').getAttribute('data-zoom'))>Number(initial),orientation+' mask grows on scrub');
   await seek(4.6);check(await page.evaluate(()=>reviewQA.state.activeKey.startsWith('S01')),orientation+' intro hands off to S01');
   check(!await page.locator('#motion-stage>.brand-intro').isVisible(),orientation+' intro removed after handoff');
   for(const i of [0,1,2,3,4,5]){
    await page.locator('.shot-button[data-index="'+i+'"]').click();
    check(await page.evaluate(i=>reviewQA.state.activeKey.startsWith('S0'+(i+1)),i),orientation+' scene '+(i+1)+' seek');
   }
   await page.locator('#animatic-copy').uncheck();check(!await page.locator('#motion-stage .v2-frame:not([hidden]) .overlay-layer').isVisible(),orientation+' copy toggle off');
   await page.locator('#animatic-mask').check();check(await page.locator('#motion-stage .v2-frame:not([hidden]) .frame-mask').isVisible(),orientation+' logo guides on');
   await page.locator('.shot-button[data-index="-1"]').click();await page.locator('#play-animatic').click();await page.waitForTimeout(250);
   check(await page.evaluate(()=>reviewQA.state.playing&&reviewQA.state.progress>0),orientation+' intro playback advances');
   await page.locator('#tab-high-angle').click();check(!await page.evaluate(()=>reviewQA.state.playing),orientation+' hidden basic pauses');
   await page.locator('#tab-basic').click();
   await page.locator('.intro-keyframe').nth(1).click();check(await page.evaluate(()=>reviewQA.state.phase==='INTRO'&&reviewQA.state.progress>0),orientation+' keyframe navigates to intro');
   await page.emulateMedia({reducedMotion:'reduce'});await page.waitForFunction(()=>document.querySelector("#play-animatic").disabled);check(await page.locator('#play-animatic').isDisabled(),orientation+' reduced motion disables playback');
   await seek(2);check(await page.locator('#motion-stage>.brand-intro').getAttribute('data-zoom')==='1.000',orientation+' reduced motion has no zoom');
   await seek(5);check(await page.evaluate(()=>reviewQA.state.phase==='CN'),orientation+' reduced motion can skip intro');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),orientation+' no page overflow');
   await page.close();
  }
 }finally{await browser.close();fs.writeFileSync(path.join(__dirname,'qa-results.json'),JSON.stringify({results,errors},null,2));console.log(JSON.stringify({passed:results.filter(x=>x.pass).length,total:results.length,errors}));}
 if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
