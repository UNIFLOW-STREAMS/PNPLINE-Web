const {chromium}=require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const results=[],errors=[],root=__dirname;
 const check=(pass,name)=>{results.push({name,pass:!!pass});if(!pass)throw Error(name);};
 try{
  for(const [orientation,viewport] of [['desktop',{width:1440,height:1000}],['mobile',{width:390,height:844}]]){
   const page=await browser.newPage({viewport});page.on('pageerror',error=>errors.push(error.message));
   await page.goto('http://127.0.0.1:8761/output/scroll-world-concept-v1/ko-c.html?revision=6#animatic',{waitUntil:'networkidle'});
   await page.waitForFunction(()=>document.body.dataset.ready==='true');
   const seek=seconds=>page.locator('#progress').evaluate((input,value)=>{input.value=String(Math.round(value/34.5*1000));input.dispatchEvent(new Event('input',{bubbles:true}));},seconds);
   check(await page.evaluate(()=>studyC.duration===34.5&&studyC.introDuration===4.5),orientation+' 34.5 second timeline');
   check(await page.locator('.intro-keyframe').count()===3,orientation+' three intro keyframes');
   check(await page.locator('#shots>.shot').count()===7,orientation+' intro and six scene buttons');
   check(await page.locator('#stage').getAttribute('data-mode')==='intro',orientation+' starts with intro');
   check(await page.locator('#stage>.brand-intro:not([hidden])').count()===1,orientation+' single orientation intro');
   check(await page.locator('#stage>.brand-intro:not([hidden]) .brand-intro-photo').getAttribute('src')==='high-angle-c/intro-harbor.webp',orientation+' high-angle first frame used in intro');
   check(await page.locator('.intro-keyframe').first().locator('.brand-intro-photo').getAttribute('src')==='high-angle-c/intro-harbor.webp',orientation+' high-angle first frame used in review keyframes');
   const initialZoom=Number(await page.locator('#stage>.brand-intro:not([hidden])').getAttribute('data-zoom'));
   for(const [name,seconds] of [['logo',0],['expansion',1.9],['harbor',3.9],['handoff',4.6]]){
    await seek(seconds);await page.locator('#stage').screenshot({path:path.join(root,'intro-'+orientation+'-'+name+'.jpg'),type:'jpeg',quality:84});
   }
   await seek(1.9);check(Number(await page.locator('#stage>.brand-intro:not([hidden])').getAttribute('data-zoom'))>initialZoom,orientation+' logo mask grows');
   await seek(4.6);check(await page.locator('#stage').getAttribute('data-mode')==='aerial'&&await page.locator('#stage').getAttribute('data-scene')==='1',orientation+' hands off to aerial scene');
   check(await page.locator('#stage>.brand-intro:not([hidden])').count()===0,orientation+' intro hidden after handoff');
   await page.locator('#shots>.intro-shot').click();check(await page.locator('#stage').getAttribute('data-mode')==='intro',orientation+' intro button seeks to start');
   await page.locator('#shots>.shot').nth(1).click();check(await page.locator('#stage').getAttribute('data-scene')==='1',orientation+' first journey button follows intro');
   await page.locator('#shots>.intro-shot').click();const before=await page.evaluate(()=>studyC.state.progress);
   await page.locator(orientation==='desktop'?'#mobile':'#desktop').click();check(Math.abs((await page.evaluate(()=>studyC.state.progress))-before)<.001,orientation+' orientation switch keeps intro time');
   check(await page.locator('#stage>.brand-intro:not([hidden])').count()===1,orientation+' orientation switch keeps intro visible');
   await page.locator('#play').click();await page.waitForTimeout(250);check(await page.evaluate(()=>studyC.state.playing&&studyC.state.progress>0),orientation+' playback advances from intro');
   await page.locator('#play').click();
   await page.locator('.intro-keyframe').nth(2).click();check(await page.locator('#stage').getAttribute('data-mode')==='intro',orientation+' static keyframe seeks intro');
   await page.emulateMedia({reducedMotion:'reduce'});await page.waitForFunction(()=>document.querySelector('#play').disabled);await seek(2);
   check(await page.locator('#stage>.brand-intro:not([hidden])').getAttribute('data-zoom')==='1.000',orientation+' reduced motion freezes logo');
   await seek(5);check(await page.locator('#stage').getAttribute('data-mode')==='aerial',orientation+' reduced motion can skip intro');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),orientation+' no horizontal overflow');
   await page.close();
  }
 }finally{
  await browser.close();const report={results,errors,passed:results.filter(r=>r.pass).length,total:results.length};
  fs.writeFileSync(path.join(root,'intro-qa-results.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({passed:report.passed,total:report.total,errors}));
 }
 if(errors.length)process.exitCode=1;
})().catch(error=>{console.error(error);process.exitCode=1;});
