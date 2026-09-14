const {chromium}=require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),crypto=require('crypto');
(async()=>{
 const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const results=[],errors=[];
 const check=(pass,name)=>{results.push({name,pass:!!pass});if(!pass)throw Error(name);};
 try {
  const pairs=[['11c4db85-2666-4ae7-a30d-1f498af8b532','us-receiving'],['d90f719d-edad-4897-9c68-8c5e1efa5a0e','us-packing'],['6f7d222c-f86a-4eb8-b5e7-7b5217a6cebc','us-dispatch']];
  const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
  pairs.forEach(([source,dest])=>check(hash('C:/Users/KIMTAE~1/AppData/Local/Temp/codex-clipboard-'+source+'.png')===hash('output/scroll-world-concept-v1/high-angle-c/'+dest+'.png'),'unchanged attachment '+dest));
  for(const width of [1440,390]){
   const page=await b.newPage({viewport:{width,height:1000}});page.on('pageerror',e=>errors.push(e.message));
   await page.goto('http://127.0.0.1:8761/output/scroll-world-concept-v1/ko-c.html?revision=2#animatic');
   await page.waitForFunction(()=>document.body.dataset.ready==='true');
   const seek=async seconds=>page.locator('#progress').evaluate((e,t)=>{e.value=String(Math.round((4.5+t)/34.5*1000));e.dispatchEvent(new Event('input',{bubbles:true}));},seconds);
   const camera=()=>page.locator('#world').evaluate(e=>({matrix:getComputedStyle(e).transform,width:e.getBoundingClientRect().width}));
   for(const start of (width<767?[0,5]:[0,5,10])){
    await seek(start);const a=await camera();await seek(start+2);const z=await camera();
    check(a.matrix!==z.matrix&&Math.abs(a.width-z.width)>5,width+' camera pans and zooms at '+start+'s');
   }
   for(const [sec,index] of [[16,4],[21,5],[26,6],[30,6]]){
    await seek(sec);
    check(!await page.locator('#world').isVisible(),width+' aerial gone at '+sec);
    check(await page.locator('.us-frame[data-scene="'+index+'"]:not([hidden])').isVisible(),width+' supplied image at '+sec);
    check(!await page.locator('#route-map').isVisible(),width+' route gone at '+sec);
    check(await page.locator('#route').isDisabled(),width+' route control disabled after arrival');
   }
   await seek(width<767?9.7:14.7);
   check(await page.locator('#world').isVisible()&&await page.locator('.us-frame:not([hidden])').count()===1,width+' arrival dissolve');
   for(const sec of [19.7,24.7]){
    await seek(sec);check(await page.locator('.us-frame:visible').count()===2,width+' two-frame dissolve at '+sec);
   }
   await seek(21);const low=page.locator('.us-frame[data-scene="5"]:not([hidden]) .us-pixels');
   const a=await low.evaluate(e=>e.style.transform);await seek(23);check(a!==await low.evaluate(e=>e.style.transform),width+' warehouse camera movement');
   await page.locator('#mask').check();check(await page.locator('.us-frame[data-scene="5"]:not([hidden]) .us-logo-mask').isVisible(),width+' attached logo mask');
   await page.locator('#mask').uncheck();await page.locator('#copy').uncheck();check(!await page.locator('#caption').isVisible(),width+' captions toggle');await page.locator('#copy').check();
   await page.locator('#stage').screenshot({path:'output/scroll-world-concept-v1/high-angle-c/hybrid-us-'+width+'.jpg',quality:72});
   await seek(7);await page.locator('#stage').screenshot({path:'output/scroll-world-concept-v1/high-angle-c/hybrid-aerial-'+width+'.jpg',quality:72});
   await page.locator('#overview').click();check(await page.locator('#stage').getAttribute('data-mode')==='overview',width+' overview');
   await page.locator('#play').click();await page.waitForTimeout(450);check(await page.evaluate(()=>studyC.state.playing&&!studyC.state.overview),width+' playback exits overview');await page.locator('#play').click();
   await seek(0);check(await page.locator('.us-frame:visible').count()===0,width+' reverse to departure');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),width+' no horizontal overflow');
   await page.emulateMedia({reducedMotion:'reduce'});await page.waitForFunction(()=>document.querySelector('#play').disabled);
   await seek(6);const fixed=await camera();await seek(8);check(fixed.matrix===(await camera()).matrix,width+' reduced motion fixed within shot');
   await page.close();
  }
 } finally {await b.close();fs.writeFileSync('output/scroll-world-concept-v1/high-angle-c/hybrid-qa-results.json',JSON.stringify({results,errors},null,2));}
 console.log(JSON.stringify({passed:results.filter(r=>r.pass).length,total:results.length,errors}));if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
