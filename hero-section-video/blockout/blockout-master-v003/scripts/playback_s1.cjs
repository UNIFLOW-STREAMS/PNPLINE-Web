const fs=require('node:fs');const path=require('node:path');const {pathToFileURL}=require('node:url');
const {chromium}=require(process.env.PNPLINE_PLAYWRIGHT_PATH);
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.PNPLINE_CHROME_PATH,headless:true,args:['--autoplay-policy=no-user-gesture-required']});
 const page=await browser.newPage({viewport:{width:960,height:620}});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(path.join(root,'review','player.html')).href);
 await page.waitForFunction(()=>document.querySelector('video').readyState>=3);
 const v=page.locator('video');await v.evaluate(v=>{v.playbackRate=1;return v.play()});
 const samples=[];let last=-1;const started=Date.now();
 while(Date.now()-started<25000){
  const s=await v.evaluate(v=>({time:v.currentTime,ended:v.ended,error:v.error?.message??null}));
  if(Math.floor(s.time)>last){last=Math.floor(s.time);const file=`playing-${String(last).padStart(2,'0')}.png`;await v.screenshot({path:path.join(root,'review',file)});samples.push({...s,file});}
  if(s.error)throw Error(s.error);if(s.ended)break;await page.waitForTimeout(160);
 }
 const result=await v.evaluate(v=>({time:v.currentTime,duration:v.duration,ended:v.ended,decoded:v.getVideoPlaybackQuality().totalVideoFrames,dropped:v.getVideoPlaybackQuality().droppedVideoFrames}));
 fs.writeFileSync(path.join(root,'review','playback-check.json'),JSON.stringify({method:'Actual 1x playback without seeking of changed S1 and S2 reconnection (0–180). Full master encoded separately.',result,errors,samples},null,2));
 await browser.close();if(!result.ended||errors.length)throw Error('Playback incomplete');console.log(JSON.stringify(result));
})().catch(e=>{console.error(e);process.exitCode=1});
