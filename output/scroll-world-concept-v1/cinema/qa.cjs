const {chromium}=require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path');
const {PNG}=require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pngjs');
function unchanged(a,b){if(a.equals(b))return true;const x=PNG.sync.read(a),y=PNG.sync.read(b);if(x.width!==y.width||x.height!==y.height)return false;let changed=0;for(let i=0;i<x.data.length;i++){const d=Math.abs(x.data[i]-y.data[i]);if(d>1)return false;if(d)changed++;}return changed/x.data.length<.01;}
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),checks=[],errors=[];
 const check=(pass,name)=>{checks.push({name,pass:!!pass});if(!pass)throw Error(name);};
 try{
  for(const variant of ['basic','high'])for(const width of [1440,390]){
   const page=await browser.newPage({viewport:{width,height:1000}}),high=variant==='high',prefix=variant+'-'+width;
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto('http://127.0.0.1:8761/output/scroll-world-concept-v1/'+(high?'ko-c.html':'ko.html')+'?revision=10',{waitUntil:'networkidle'});
   await page.waitForFunction(high?()=>document.body.dataset.ready==='true':()=>document.body.dataset.preloaded==='true');
   const stage=page.locator(high?'#stage':'#motion-stage'),seek=async t=>{await page.locator('#progress').evaluate((e,t)=>{e.value=String(Math.round(t/34.5*1000));e.dispatchEvent(new Event('input',{bubbles:true}));},t);};
   const toggle=async bypass=>{await page.evaluate(b=>document.documentElement.classList.toggle('cinema-bypass',b),bypass);};
   for(const t of [0,1.9,3.9,4.3]){
    await seek(t);await toggle(false);const after=await stage.screenshot();await toggle(true);const before=await stage.screenshot();
    check(unchanged(before,after),prefix+' intro unaffected at '+t+'s (1 LSB compositor tolerance)');
   }
   await toggle(false);
   for(const [tag,t] of (high?[['aerial',6],['warehouse',21]]:[['departure',6],['warehouse',21]])){
    await seek(t);const activeImage=page.locator(high?(tag==='aerial'?'#world-image':'.us-frame:not([hidden]) .us-pixels>img'):'#motion-stage .v2-frame:not([hidden]) .scene-image').first();
    check((await activeImage.evaluate(e=>getComputedStyle(e).filter)).includes('cinema-agx'),prefix+' '+tag+' AgX enabled');
    const activeFx=high?stage.locator(':scope>.cinema-fx'):stage.locator('.v2-frame:not([hidden]) .cinema-fx');
    check(await activeFx.isVisible(),prefix+' '+tag+' optics visible');
    check((await activeFx.locator('.cinema-vignette').evaluate(e=>getComputedStyle(e).backgroundImage)).includes('0.76'),prefix+' '+tag+' pronounced vignette');
    const caption=page.locator(high?'#caption':'#motion-stage .v2-frame:not([hidden]) .v2-copybar');
    check(await caption.evaluate(e=>getComputedStyle(e).filter)==='none',prefix+' '+tag+' caption remains ungraded');
    const graded=await stage.screenshot({path:path.join(__dirname,prefix+'-'+tag+'-after.png')});
    await stage.screenshot({path:path.join(__dirname,prefix+'-'+tag+'-after.jpg'),quality:83});
    await toggle(true);const original=await stage.screenshot({path:path.join(__dirname,prefix+'-'+tag+'-before.png')});
    check(!original.equals(graded),prefix+' '+tag+' visible processing change');await toggle(false);
   }
   if(!high){
    for(const o of ['desktop','mobile']){await page.locator('[data-orientation="'+o+'"]').click();check(await page.locator('#scene-list .cinema-fx').count()===6,prefix+' static '+o+' six processed frames');}
   }
   const shots=page.locator(high?'.shot:not(.intro-shot)':'.shot-button:not([data-index="-1"])');
   for(let i=0;i<6;i++){await shots.nth(i).click();check(await stage.locator('.cinema-fx:visible').count()>0,prefix+' scene '+(i+1)+' processing survives seek');}
   const copy=page.locator(high?'#copy':'#animatic-copy');await copy.uncheck();check(!await page.locator(high?'#caption':'#motion-stage .v2-frame:not([hidden]) .v2-copybar').isVisible(),prefix+' copy toggle');await copy.check();
   const mask=page.locator(high?'#mask':'#animatic-mask');await mask.check();check(await page.locator(high?'#mask-note':'#motion-stage .v2-frame:not([hidden]) .frame-mask').isVisible(),prefix+' logo guides');
   await seek(6);await page.locator(high?'#play':'#play-animatic').click();await page.waitForTimeout(350);check(await stage.getAttribute('data-playing')==='true',prefix+' grain runs during playback');
   await page.locator(high?'#play':'#play-animatic').click();check(await stage.getAttribute('data-playing')==='false',prefix+' grain pauses');
   await page.emulateMedia({reducedMotion:'reduce'});await page.waitForFunction(()=>document.querySelector('#play,#play-animatic').disabled);
   const grain=stage.locator('.cinema-grain:visible').first();check(await grain.evaluate(e=>getComputedStyle(e).animationName)==='none',prefix+' reduced motion freezes grain');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),prefix+' no overflow');await page.close();
  }
 }finally{await browser.close();const report={checks,errors,passed:checks.filter(c=>c.pass).length,total:checks.length};fs.writeFileSync(path.join(__dirname,'qa-results.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({passed:report.passed,total:report.total,errors}));}
 if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
