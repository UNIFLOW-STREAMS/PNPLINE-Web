const $ = s => document.querySelector(s);
const hero = $('#journey'), pin = $('.hero-pin'), video = $('#hero-video');
const reduce = matchMedia('(prefers-reduced-motion: reduce)');
const compact = matchMedia('(max-width: 1024px)');
let progress = 0, mediaURL = null, queued = false, lastRequest = -1;
function bounds() {
  const top = parseFloat(getComputedStyle(pin).top) || 0;
  return {start: hero.getBoundingClientRect().top + scrollY - top, distance: Math.max(1, hero.offsetHeight - pin.offsetHeight)};
}
function seekVideo() {
  if (!video.hidden && Number.isFinite(video.duration) && !video.seeking) {
    const time = reduce.matches ? 0 : progress * Math.max(0, video.duration - .001);
    if (Math.abs(lastRequest - time) > .015) { lastRequest = time; video.currentTime = time; }
  }
}
function render() {
  queued = false;
  const b = bounds();
  progress = reduce.matches || document.body.classList.contains('overview') ? 0 : Math.min(1, Math.max(0,(scrollY-b.start)/b.distance));
  $('#progress-value').textContent = Math.round(progress*100)+'%';
  $('#progress').value = progress;
  $('#time-value').textContent = !video.hidden && Number.isFinite(video.duration) ? (progress*video.duration).toFixed(2)+' / '+video.duration.toFixed(2)+' s' : progress.toFixed(3)+' × T';
  const route = $('#route'), point = route.getPointAtLength(route.getTotalLength()*progress);
  $('#cargo').setAttribute('transform',`translate(${point.x} ${point.y})`);
  $('#world-camera').setAttribute('transform',`translate(${progress*-35} ${progress*12}) rotate(${progress*-9} 760 420)`);
  seekVideo();
}
function schedule() { if (!queued) { queued=true; requestAnimationFrame(render); } }
addEventListener('scroll',schedule,{passive:true}); addEventListener('resize',schedule);
video.addEventListener('seeked',seekVideo); video.addEventListener('loadedmetadata',()=>{lastRequest=-1;render();});
video.addEventListener('play',()=>video.pause());
function mediaFailure() {
  video.hidden=true; $('#world').style.display='';
  $('#media-status').textContent='영상을 읽을 수 없어 도식으로 표시합니다. 다른 파일을 선택할 수 있습니다.';
  render();
}
video.addEventListener('error',mediaFailure);
$('#media-input').addEventListener('change',e=>{
  const file=e.target.files[0]; if (!file) return;
  video.pause(); if(mediaURL) URL.revokeObjectURL(mediaURL);
  mediaURL=URL.createObjectURL(file);video.src=mediaURL;video.hidden=false;$('#world').style.display='none';video.load();
  $('#media-status').textContent=file.name+' · 스크롤로 시점을 제어합니다.';
});
document.querySelectorAll('[data-seek]').forEach(button=>button.addEventListener('click',()=>{
  document.body.classList.remove('overview');$('#overview').setAttribute('aria-pressed','false');
  const b=bounds();scrollTo({top:b.start+Number(button.dataset.seek)*b.distance,behavior:'instant'});schedule();
}));
$('#overview').addEventListener('click',()=>{
  const enabled=document.body.classList.toggle('overview');$('#overview').setAttribute('aria-pressed',String(enabled));
  scrollTo({top:0,behavior:'instant'});schedule();
});
function syncNotes(){
  const visible=compact.matches ? document.body.classList.contains('mobile-inspector') : !document.body.classList.contains('clean');
  $('#notes').textContent=visible ? (compact.matches?'검토 패널 닫기':'검토 패널 숨기기') : '검토 패널 열기';
  $('#notes').setAttribute('aria-pressed',String(visible));
}
$('#notes').addEventListener('click',()=>{
  if(compact.matches){document.body.classList.remove('clean');document.body.classList.toggle('mobile-inspector');}
  else{document.body.classList.toggle('clean');}
  syncNotes();
  schedule();
});
compact.addEventListener('change',()=>{document.body.classList.remove('mobile-inspector');syncNotes();schedule();});
syncNotes();
function motionPreference(){document.body.classList.toggle('reduced',reduce.matches);schedule();}
reduce.addEventListener('change',motionPreference);motionPreference();
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',()=>{document.body.classList.remove('mobile-inspector');syncNotes();}));
document.querySelectorAll('a[href="/privacy/"]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();$('#privacy-preview').showModal();}));
$('#close-privacy').addEventListener('click',()=>$('#privacy-preview').close());
$('form').addEventListener('submit',e=>{e.preventDefault();$('.form-result').textContent='线框预览：此表单未连接提交服务，信息未发送。';});
render();
