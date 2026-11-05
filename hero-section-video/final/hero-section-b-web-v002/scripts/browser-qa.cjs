const {chromium}=require('F:/pnpline-landing/output/pnpline-web-zh/node_modules/playwright-core');
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'..'),review=path.join(root,'review');
const report={runtime:'isolated Chromium automated end-to-end',date:new Date().toISOString(),sites:{},limitations:['CUA and node_repl unavailable: Windows sandbox helper setup errors','Desktop and mobile emulation; not physical iOS/Safari']};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const state=p=>p.evaluate(()=>{const t=document.querySelector('.journey-track'),v=document.querySelector('.journey-video');return {version:t?.dataset.heroVersion,media:t?.dataset.heroMedia,target:Number(t?.dataset.heroTargetFrame),painted:Number(t?.dataset.heroFrame),section:t?.dataset.heroSection,current:v?.currentTime,duration:v?.duration,width:v?.videoWidth,ready:v?.readyState,src:v?.currentSrc,video:t?.dataset.video,scrollY:scrollY,overflow:document.documentElement.scrollWidth-innerWidth,buttons:[...document.querySelectorAll('.route-legend button')].map(b=>({text:b.textContent,current:b.getAttribute('aria-current'),disabled:b.disabled}))}});
async function settled(p){await p.waitForFunction(()=>{const t=document.querySelector('.journey-track'),v=document.querySelector('.journey-video');return v?.readyState>=2&&!v.seeking&&Math.abs(v.currentTime*30-Number(t?.dataset.heroTargetFrame))<2},{timeout:20000});}
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Users/KIM TAEHYUNG/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe'});
 try{
 for(const [lang,port]of [['en',3091],['zh',3092]]){
  const context=await browser.newContext({viewport:{width:1600,height:900}}),p=await context.newPage();
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(`http://127.0.0.1:${port}/`,{waitUntil:'domcontentloaded'});
  await p.waitForSelector('.journey-track[data-hero-version="B-cycles-v002"]');await settled(p);
  let s=await state(p);assert.equal(s.media,'1080p');assert.equal(s.width,1920);assert.equal(s.duration,33);assert.equal(s.buttons.length,7);assert(s.buttons.every(b=>!b.disabled));assert(s.overflow<=1);
  await p.mouse.move(800,450);await p.mouse.wheel(0,1800);await sleep(1200);await settled(p);
  const stages=[];
  for(let i=0;i<7;i++){
   await p.locator('.route-legend button').nth(i).click();await sleep(1500);await settled(p);s=await state(p);
   assert(Math.abs(s.target-[0,75,165,315,465,660,870][i])<3,JSON.stringify(s));
   console.log('STAGE',lang,i,JSON.stringify(s));assert.equal(s.buttons[i].current,'step');stages.push(s);
   if([1,3,5].includes(i))await p.screenshot({path:path.join(review,`site-${lang}-${['china','us-port','warehouse'][[1,3,5].indexOf(i)]}.png`)});
  }
  await p.locator('.route-legend button').nth(3).click();await sleep(1500);await settled(p);
  await p.mouse.wheel(0,650);await sleep(500);await settled(p);const forward=await state(p);
  await p.mouse.wheel(0,-400);await sleep(500);await settled(p);const reverse=await state(p);assert(reverse.target<forward.target);
  assert.equal(errors.length,0,errors.join('\n'));
  report.sites[lang]={desktop:{stages,forward,reverse,errors}};await context.close();
  const mc=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1}),mp=await mc.newPage();
  await mp.goto(`http://127.0.0.1:${port}/`,{waitUntil:'domcontentloaded'});await mp.waitForSelector('.journey-track[data-hero-version]');await settled(mp);
  await mp.mouse.wheel(0,1600);await sleep(1000);await settled(mp);
  await mp.locator('.route-legend button').nth(5).click();await sleep(1500);await settled(mp);
  const mobile=await state(mp);assert.equal(mobile.media,'720p');assert.equal(mobile.width,1280);assert(mobile.overflow<=1);
  const rects=await mp.evaluate(()=>{const v=document.querySelector('.journey-video').getBoundingClientRect(),n=document.querySelector('.route-legend').getBoundingClientRect();return {video:{x:v.x,y:v.y,width:v.width,height:v.height},nav:{x:n.x,y:n.y,width:n.width,height:n.height},viewport:{width:innerWidth,height:innerHeight}}});
  assert(Math.abs(rects.video.width/rects.video.height-16/9)<.01);assert(rects.nav.x>=0&&rects.nav.x+rects.nav.width<=390);
  await mp.screenshot({path:path.join(review,`site-${lang}-mobile.png`)});report.sites[lang].mobile={...mobile,rects};await mc.close();
 }
 const rc=await browser.newContext({viewport:{width:1280,height:720},reducedMotion:'reduce'}),rp=await rc.newPage();
 await rp.goto('http://127.0.0.1:3091/',{waitUntil:'domcontentloaded'});const reduced=await rp.evaluate(()=>({active:document.querySelector('.journey-track').dataset.video,src:document.querySelector('.journey-video').getAttribute('src'),poster:document.querySelector('.journey-fallback').naturalWidth}));assert(!reduced.active&&!reduced.src&&reduced.poster>0);report.reducedMotion=reduced;await rc.close();
 const fc=await browser.newContext({viewport:{width:1280,height:720}}),fp=await fc.newPage();await fp.route('**/hero-b-v002-*.mp4',r=>r.abort());
 await fp.goto('http://127.0.0.1:3092/',{waitUntil:'domcontentloaded'});await fp.waitForFunction(()=>!document.querySelector('.journey-track').dataset.video);
 const fallback=await fp.evaluate(()=>({active:document.querySelector('.journey-track').dataset.video,poster:document.querySelector('.journey-fallback').naturalWidth,display:getComputedStyle(document.querySelector('.journey-fallback')).display}));assert(fallback.poster>0&&fallback.display!=='none');report.mediaErrorFallback=fallback;await fc.close();
 report.passed=true;
 }catch(e){report.passed=false;report.error=e.stack;throw e;}finally{fs.writeFileSync(path.join(root,'audit/browser-qa.json'),JSON.stringify(report,null,2));await browser.close();}
 console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
