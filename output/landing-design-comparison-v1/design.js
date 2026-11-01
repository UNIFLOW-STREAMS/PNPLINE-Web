const journey=document.querySelector('.journey'),pin=document.querySelector('.hero-pin'),video=document.querySelector('video');
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
const query=new URLSearchParams(location.search);
document.body.classList.toggle('overview',query.get('overview')==='1');
let desired=0,lastTarget=-1,scheduled=false,reportTick=0;
function limits(){const top=parseFloat(getComputedStyle(pin).top)||0;return{start:journey.getBoundingClientRect().top+scrollY-top,length:Math.max(1,journey.offsetHeight-pin.offsetHeight)}}
function commit(){if(video.hidden||!Number.isFinite(video.duration)||video.seeking)return;const target=desired*Math.max(0,video.duration-.001);if(Math.abs(target-lastTarget)>.012){lastTarget=target;video.currentTime=target}}
function update(){scheduled=false;const b=limits();desired=reduced.matches||document.body.classList.contains('overview')?0:Math.max(0,Math.min(1,(scrollY-b.start)/b.length));commit();if(parent!==window&&performance.now()-reportTick>60){parent.postMessage({type:'pnpline-progress',progress:desired,time:video.currentTime,duration:video.duration},location.origin);reportTick=performance.now()}}
function schedule(){if(!scheduled){scheduled=true;requestAnimationFrame(update)}}
function jump(fraction){document.body.classList.remove('overview');const b=limits();scrollTo({top:b.start+b.length*fraction,behavior:'instant'});schedule()}
addEventListener('scroll',schedule,{passive:true});addEventListener('resize',schedule);video.addEventListener('loadedmetadata',()=>{lastTarget=-1;update()});video.addEventListener('seeked',commit);video.addEventListener('play',()=>video.pause());video.addEventListener('error',()=>{document.body.classList.add('media-failed');video.hidden=true;schedule()});
function motion(){document.body.classList.toggle('reduced',reduced.matches);lastTarget=-1;schedule()}reduced.addEventListener('change',motion);motion();
addEventListener('message',e=>{if(e.source!==parent||e.origin!==location.origin)return;const data=e.data;if(!data||typeof data!=='object')return;if(data.type==='pnpline-seek'&&Number.isFinite(data.progress))jump(Math.max(0,Math.min(1,data.progress)));if(data.type==='pnpline-section'&&['journey','services','quote'].includes(data.section)){document.getElementById(data.section).scrollIntoView({behavior:'instant',block:'start'});schedule()}if(data.type==='pnpline-overview'){document.body.classList.toggle('overview',Boolean(data.value));scrollTo({top:0,behavior:'instant'});schedule()}});
document.querySelector('form').addEventListener('submit',e=>{e.preventDefault();document.querySelector('.form-status').textContent='设计预览：信息未发送。'});
update();
