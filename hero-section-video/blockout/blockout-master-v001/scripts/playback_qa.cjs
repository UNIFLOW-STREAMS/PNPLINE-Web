const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require(process.env.PNPLINE_PLAYWRIGHT_PATH);
const root=path.resolve(__dirname,'..');
(async()=>{
  const dir=path.join(root,'review','playback');fs.mkdirSync(dir,{recursive:true});
  const browser=await chromium.launch({executablePath:process.env.PNPLINE_CHROME_PATH,headless:true,args:['--autoplay-policy=no-user-gesture-required']});
  const page=await browser.newPage({viewport:{width:960,height:720}});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto('http://127.0.0.1:8766/review/player.html');
  const video=page.locator('video');
  await page.waitForFunction(()=>document.querySelector('video').readyState>=3);
  await video.evaluate(v=>{v.playbackRate=1;return v.play()});
  let last=-1;const samples=[];const started=Date.now();
  while(Date.now()-started<145000){
    const state=await video.evaluate(v=>({time:v.currentTime,duration:v.duration,ended:v.ended,paused:v.paused,readyState:v.readyState,error:v.error?.message??null,quality:v.getVideoPlaybackQuality().toJSON?.()??{total:v.getVideoPlaybackQuality().totalVideoFrames,dropped:v.getVideoPlaybackQuality().droppedVideoFrames}}));
    const second=Math.floor(state.time);
    if(second>last){
      const name=`playing-${String(second).padStart(3,'0')}.png`;
      await video.screenshot({path:path.join(dir,name)});
      samples.push({...state,screenshot:name,wall_ms:Date.now()-started});last=second;
    }
    if(state.ended)break;
    if(state.error)throw Error(state.error);
    await page.waitForTimeout(180);
  }
  const final=await video.evaluate(v=>({time:v.currentTime,duration:v.duration,ended:v.ended,decoded:v.getVideoPlaybackQuality().totalVideoFrames,dropped:v.getVideoPlaybackQuality().droppedVideoFrames}));
  const report={method:'Actual 1x browser video playback; no seeking. Screenshots sampled once per playback second.',samples,final,errors,wall_ms:Date.now()-started};
  fs.writeFileSync(path.join(root,'review','playback-check.json'),JSON.stringify(report,null,2));
  await browser.close();
  if(!final.ended||Math.abs(final.duration-116)>.1||errors.length)throw Error('Playback incomplete or duration mismatch');
  console.log(JSON.stringify({samples:samples.length,final,errors},null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
