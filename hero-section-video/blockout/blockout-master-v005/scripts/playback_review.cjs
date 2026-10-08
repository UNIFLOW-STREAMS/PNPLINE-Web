const fs=require('node:fs'),path=require('node:path');const {pathToFileURL}=require('node:url');
const {chromium}=require(process.env.PNPLINE_PLAYWRIGHT_PATH);const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.PNPLINE_CHROME_PATH,headless:true,args:['--autoplay-policy=no-user-gesture-required']});
 const page=await browser.newPage({viewport:{width:1000,height:630}});const errors=[];page.on('pageerror',e=>errors.push(String(e)));let reports=[];
 const clips=[['before','../preview/s3-before.mp4'],['after','../preview/s3-after.mp4'],['connection','../preview/s2-tail_s3_s4-head.mp4']];
 for(const [label,file] of clips){
  const html=path.join(root,'review','player.html');fs.writeFileSync(html,`<!doctype html><meta charset="utf-8"><title>S3 review</title><body style="margin:0;background:#17222a;color:white;font:18px sans-serif"><p>${label} — normal speed</p><video controls width="960" src="${file}"></video></body>`);
  await page.goto(pathToFileURL(html).href);await page.waitForFunction(()=>document.querySelector('video').readyState>=3);
  const v=page.locator('video');await v.evaluate(v=>{v.playbackRate=1;return v.play()});let last=-1;const started=Date.now();let samples=[];
  while(Date.now()-started<30000){let s=await v.evaluate(v=>({time:v.currentTime,ended:v.ended,error:v.error?.message||null}));if(Math.floor(s.time/2)>last){last=Math.floor(s.time/2);let image=`play-${label}-${last}.png`;await v.screenshot({path:path.join(root,'review',image)});samples.push({...s,image});}if(s.error)throw Error(s.error);if(s.ended)break;await page.waitForTimeout(120);}
  let result=await v.evaluate(v=>({time:v.currentTime,duration:v.duration,ended:v.ended,rate:v.playbackRate,decoded:v.getVideoPlaybackQuality().totalVideoFrames,dropped:v.getVideoPlaybackQuality().droppedVideoFrames}));
  reports.push({label,result,samples});fs.writeFileSync(path.join(root,'review','playback-check.json'),JSON.stringify({method:'Real-time 1x playback, no seeking, installed Chrome via Playwright',reports,errors},null,2));if(!result.ended)throw Error('Incomplete '+label);console.log(label,JSON.stringify(result));
 }
 await browser.close();if(errors.length)throw Error(errors.join('\n'));
})().catch(e=>{console.error(e);process.exitCode=1});
