const {chromium}=require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const results=[],errors=[];
try{
 for(const width of [1440,390]){
 const p=await b.newPage({viewport:{width,height:1000}});p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:8761/output/scroll-world-concept-v1/ko-c.html#animatic');
 await p.waitForFunction(()=>document.body.dataset.ready==='true');
 const check=(ok,name)=>{results.push({width,name,pass:!!ok});if(!ok)throw Error(name);};
 check(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'no horizontal overflow');
 for(let i=0;i<6;i++){await p.locator('.shot').nth(i+1).click();check(await p.locator('#stage').getAttribute('data-scene')===String(i+1),'scene '+(i+1));}
 await p.locator('#copy').uncheck();check(!await p.locator('#caption').isVisible(),'copy off');
 await p.locator('#copy').check();check(await p.locator('#caption').isVisible(),'copy on');
 await p.locator('#mask').check();check(await p.locator('#mask-note').isVisible(),'logo mask on');
 await p.locator('#mask').uncheck();check(!await p.locator('#mask-note').isVisible(),'logo mask off');
 await p.locator('.shot').nth(1).click();
 await p.locator('#route').uncheck();check(!await p.locator('#route-map').isVisible(),'route off');
 await p.locator('#route').check();
 await p.locator('#overview').click();check(await p.locator('#stage').getAttribute('data-overview')==='true','overview');
 await p.locator('#stage').screenshot({path:'output/scroll-world-concept-v1/high-angle-c/overview-'+width+'.png'});
 await p.locator('.shot').nth(1).click();await p.locator('#play').click();await p.waitForTimeout(450);
 check(await p.evaluate(()=>studyC.state.progress>0 && studyC.state.playing),'play advances');
 await p.locator('#play').click();check(await p.evaluate(()=>!studyC.state.playing),'pause');
 await p.locator('#mobile').click();check(await p.locator('#stage').evaluate(e=>Math.abs(e.clientWidth/e.clientHeight-9/16)<.01),'mobile ratio');
 await p.locator('#desktop').click();check(await p.locator('#stage').evaluate(e=>Math.abs(e.clientWidth/e.clientHeight-16/9)<.01),'desktop ratio');
 if(width===390)await p.locator('#mobile').click();
 await p.locator('.shot').nth(4).click();
 await p.locator('#stage').screenshot({path:'output/scroll-world-concept-v1/high-angle-c/camera-'+width+'.png'});
 await p.emulateMedia({reducedMotion:'reduce'});await p.waitForFunction(()=>document.querySelector('#play').disabled);check(await p.locator('#play').isDisabled(),'reduced motion');
 await p.close();
 }
 const p=await b.newPage();await p.goto('http://127.0.0.1:8761/output/scroll-world-concept-v1/ko.html');
 await p.locator('#tab-high-angle').click();
 results.push({name:'integrated C tab',pass:await p.locator('#panel-high-angle').isVisible()});await p.close();
}finally{await b.close();fs.writeFileSync('output/scroll-world-concept-v1/high-angle-c/qa-results.json',JSON.stringify({results,errors},null,2));}
console.log(JSON.stringify({passed:results.filter(r=>r.pass).length,total:results.length,errors}));if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
