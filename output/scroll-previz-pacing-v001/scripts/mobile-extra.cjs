const {chromium}=require('playwright-core');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
let browser,page;
(async()=>{
 browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--no-proxy-server']});
 const c=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true});page=await c.newPage();
 await page.goto('http://127.0.0.1:3096/');await page.waitForFunction(()=>pacing.state.painted);
 const session=await c.newCDPSession(page);await session.send('Emulation.setCPUThrottlingRate',{rate:4});await page.touchscreen.tap(200,220);
 for(let i=0;i<4;i++){
  await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:200,y:550}]});
  for(let j=1;j<=12;j++){await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:200,y:550-j*28}]});await page.waitForTimeout(20);}
  await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await page.waitForTimeout(200);
 }
 await page.waitForFunction(()=>!pacing.state.seeking&&pacing.state.targetFrame===pacing.state.displayFrame);
 const stopped=await page.evaluate(()=>pacing.state);assert(stopped.progress>.03,'Touch gesture must actually advance the document');await page.waitForTimeout(400);assert.equal((await page.evaluate(()=>pacing.state)).displayFrame,stopped.targetFrame);
 await page.setViewportSize({width:390,height:740});await page.waitForTimeout(300);
 const nav=await page.locator('#scene-nav').boundingBox();assert(nav.y+nav.height<=740);
 await page.emulateMedia({reducedMotion:'reduce'});await page.locator('#static-scenes').waitFor({state:'visible',timeout:5000});
 await page.emulateMedia({reducedMotion:'no-preference'});await page.waitForFunction(()=>pacing.state.painted&&!pacing.state.seeking);
 fs.writeFileSync(path.resolve(__dirname,'../review/mobile-extra.json'),JSON.stringify({pass:true,emulated:true,cpuThrottle:4,touchGestures:4,stopped,navBottomAfterHeightResize:nav.y+nav.height,runtimeReducedMotionToggle:true},null,2));
 console.log('MOBILE_EXTRA_PASS');
})().catch(async e=>{console.error(e);if(page)console.log(await page.evaluate(()=>({body:document.body.className,mq:matchMedia('(prefers-reduced-motion:reduce)').matches,state:pacing.state,display:getComputedStyle(document.querySelector('#static-scenes')).display})));process.exitCode=1;}).finally(async()=>{await browser?.close();});
