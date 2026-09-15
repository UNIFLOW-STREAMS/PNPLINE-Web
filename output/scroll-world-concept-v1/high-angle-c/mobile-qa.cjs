const {chromium}=require('C:/Users/KIM TAEHYUNG/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),crypto=require('crypto');
(async()=>{
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const checks=[],errors=[];
const check=(ok,name)=>{checks.push({name,pass:!!ok});if(!ok)throw Error(name);};
const files=['us-arrival-mobile','us-receiving-mobile','us-packing-mobile','us-dispatch-mobile'];
const root='output/scroll-world-concept-v1/high-angle-c/';
try{
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
files.forEach(f=>check(fs.existsSync(root+f+'.webp'),'WebP asset exists '+f));
for(const width of [390,320]){
const page=await browser.newPage({viewport:{width,height:1000}});page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8761/output/scroll-world-concept-v1/ko-c.html?revision=3#animatic');
await page.waitForFunction(()=>document.body.dataset.ready==='true');
const seek=t=>page.locator('#progress').evaluate((e,t)=>{e.value=String((4.5+t)/34.5*1000);e.dispatchEvent(new Event('input'));},t);
for(let i=0;i<4;i++){
await seek(12+i*5);
const frame=page.locator('.us-frame:not([hidden])');
const metrics=await frame.evaluate(e=>{const im=e.querySelector('img'),a=im.getBoundingClientRect(),b=document.querySelector('#stage').getBoundingClientRect();return{src:im.currentSrc,ratio:im.naturalWidth/im.naturalHeight,scaleX:a.width/b.width,scaleY:a.height/b.height};});
check(metrics.src.endsWith(files[i]+'.webp'),width+' correct portrait '+i);
check(Math.abs(metrics.ratio-9/16)<.001,width+' native portrait ratio '+i);
check(metrics.scaleX<=1.03&&metrics.scaleY<=1.03,width+' less than 3 percent crop '+i);
check(await page.locator('.shot').nth(i+3).locator('img').getAttribute('src')==='high-angle-c/'+files[i]+'.webp',width+' portrait thumbnail '+i);
await page.locator('#mask').check();check(await frame.locator('.us-logo-mask').first().isVisible(),width+' portrait masks '+i);await page.locator('#mask').uncheck();
if(width===390)await page.locator('#stage').screenshot({path:root+'portrait-'+i+'.jpg',quality:75});
await page.locator('#desktop').click();
check(await page.evaluate(()=>studyC.state.progress>.39),width+' keeps timeline position '+i);
if(i===0)check(await page.locator('#world').isVisible(),'desktop arrival stays aerial');
else check((await page.locator('.us-frame:not([hidden]) img').getAttribute('src')).endsWith(files[i].replace('-mobile','')+'.webp'),'desktop original '+i);
await page.locator('#mobile').click();
check((await page.locator('.us-frame:not([hidden]) img').getAttribute('src')).endsWith(files[i]+'.webp'),'switch back to portrait '+i);
}
await seek(30);check(await page.locator('.us-frame:not([hidden]) img').isVisible(),'final mobile frame stays visible');
check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),width+' no page overflow');
await page.close();
}
}finally{await browser.close();fs.writeFileSync(root+'mobile-qa-results.json',JSON.stringify({checks,errors},null,2));}
console.log(JSON.stringify({passed:checks.filter(c=>c.pass).length,total:checks.length,errors}));if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
