'use strict';
(()=>{
 const $=s=>document.querySelector(s), data=window.CONTINUITY_V2;
 const ko=document.documentElement.lang.startsWith('ko'), lang=ko?'ko':'zh';
 const copy=ko?{
  error:'이미지를 불러오지 못했습니다. 아래 장면 설명을 확인해 주세요.',loadError:'수정안 데이터를 불러오지 못했습니다.',
  play:'30초 러프 재생',pause:'일시 정지',restart:'처음부터 재생',scene:'장면',next:'다음',end:'미국 출고까지 여정 완료',
  country:['중국 출발','태평양 횡단','미국 도착 · 출고'],camera:'카메라',proof:'장소 단서',geoLabel:'중국에서 태평양을 건너 미국으로 이동하는 경로',
  note:'국가·카메라·축척감을 수정한 V2 · 정지 프레임 기반 러프',
  status:'V2 검토 준비 완료 · 새 키프레임 12장 · 실제 영상 생성 0회',
  reduced:'동작 줄이기 설정에 따라 자동 재생과 카메라 이동을 멈춥니다. 슬라이더 또는 장면 버튼으로 확인할 수 있습니다.',
  cta:'서비스 알아보기 ↗',image:'콘셉트 미니어처',guard:'보라색: 원본 로고 보호 영역 · 문구는 이미지 밖에 배치',
  ready:'키프레임을 모두 불러왔습니다.',legacy:'초기 미술 방향 비교 · 수정안 키프레임은 아래에 있습니다.',
  sequence:'장면 바로 이동',cut:'공통 화물과 진행 방향으로 연결한 정지 프레임 컷입니다. 실제 카메라 연결 영상은 파일럿에서 검증합니다.'
 }:{
  error:'图像未能加载。请阅读下方场景说明。',loadError:'新版评审数据未能加载。',play:'播放30秒粗剪',pause:'暂停',restart:'从头播放',scene:'场景',next:'下一场景',end:'完成美国出库旅程',
  country:['中国出发','跨越太平洋','美国到达 · 出库'],camera:'镜头',proof:'地点线索',geoLabel:'从中国跨越太平洋到美国的路线',
  note:'V2：强化国家区分、镜头方向与微缩感 · 静帧粗剪',status:'V2待评审 · 新关键帧12张 · 实际视频生成0次',
  reduced:'已启用减少动态效果，自动播放和镜头移动已停止。可用滑块或场景按钮查看。',cta:'了解服务 ↗',image:'概念微缩场景',
  guard:'紫框：原始标志保护区域 · 文案置于图像之外',ready:'全部关键帧已加载。',legacy:'初期美术方向比较 · 修改后的关键帧见下方。',sequence:'跳转场景',
  cut:'以相同货物和前进方向衔接静帧。实际相机连续性将在试制中验证。'
 };
 if(!data){$('#load-status').textContent=copy.loadError;return;}
 const scenes=data.scenes, media=matchMedia('(prefers-reduced-motion:reduce)'),errors=[];
 const intro=window.BRAND_INTRO,introDuration=intro?intro.duration:0,duration=data.duration+introDuration;
 if(intro)copy.play=ko?duration+'초 인트로부터 재생':'从开场播放（'+duration+'秒）';
 let orientation=matchMedia('(max-width:767px)').matches?'mobile':'desktop', activeKey='', playing=false,raf=0,last=0,playProgress=0;
 const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
 const asset=(s,o)=>data.assets.find(a=>a.scene===s.id&&a.orientation===o);
 document.body.classList.add('continuity-v2');
 document.body.classList.toggle('reduce-motion',media.matches);
 $('#load-status').textContent=copy.status;
 $('.legend').textContent=copy.guard;
 $('#reduced-note').textContent=copy.reduced;
 document.querySelector('#animatic > .note:last-child').textContent=copy.cut;
 const oldLabels=ko?['밝은 산업 미니어처 / 초기안','해 질 녘 시네마틱 / 비교안','하이 앵글 / 비교안']:['明亮工业微缩 / 初稿','暮色电影感 / 比较案','俯视 / 比较案'];
 ['A','B','C'].forEach((v,i)=>{const a=el('article','variant'+(i===0?' selected':''));a.append(el('span','badge',ko?'초기 방향 비교':'初期方向比较'));const im=el('img');im.src='styleframes/S01-'+v+'.jpg';im.alt=oldLabels[i];im.loading='lazy';a.append(im,el('h3','',v+' · '+oldLabels[i]),el('p','',copy.legacy));$('#variants').append(a);});
 function frame(s,o,showCopy=true,showMask=false){
  const a=asset(s,o), t=s[lang], f=el('div','frame v2-frame '+o);f.dataset.scene=s.id;
  const surface=el('div','image-surface'),pixels=el('div','shot-pixels'),im=el('img','scene-image');
  im.src=a.path;im.alt=t.place+' · '+t.flow+' · '+copy.image;im.decoding='async';
  im.addEventListener('error',()=>{surface.classList.add('has-error');errors.push(a.path);});
  const mask=document.createElementNS('http://www.w3.org/2000/svg','svg');mask.classList.add('frame-mask');mask.setAttribute('viewBox','0 0 1000 1000');mask.setAttribute('preserveAspectRatio','none');mask.setAttribute('aria-hidden','true');mask.style.display=showMask?'block':'none';
  (a.protect_logos||[a.protect_logo]).forEach(bounds=>{const rect=document.createElementNS(mask.namespaceURI,'rect');['x','y','width','height'].forEach((key,i)=>rect.setAttribute(key,String(bounds[i]*1000)));rect.setAttribute('fill','#9652c2');rect.setAttribute('fill-opacity','.16');rect.setAttribute('stroke','#9652c2');rect.setAttribute('stroke-width','3');mask.append(rect);});
  const err=el('p','error-note',copy.error+' '+t.title+' · '+t.body);err.setAttribute('role','status');
  pixels.append(im,mask);surface.append(pixels,err);window.CINEMA?.mount(surface);
  const overlay=el('div','overlay-layer v2-copybar');overlay.hidden=!showCopy;overlay.append(el('strong','copy-part title',t.title),el('p','copy-part body',t.body));
  f.append(surface,overlay);return f;
 }
 function renderScenes(){
  const list=$('#scene-list');list.replaceChildren();
  scenes.forEach(s=>{
   const t=s[lang],row=el('article','scene-row');row.id='scene-'+s.id;
   const info=el('div','scene-info');info.append(el('span','scene-number',s.id+' / 06 · '+t.place),el('h3','',t.title),el('p','',t.body),el('p','camera-note',copy.camera+' · '+t.camera),el('p','note',orientation==='mobile'?t.mobileFlow:t.flow),el('p','note',copy.proof+' · '+t.proof));
   const fig=el('figure');fig.append(frame(s,orientation,$('#overlay-toggle').checked,$('#mask-toggle').checked),el('figcaption','',copy.image+' · V2 · '+(orientation==='mobile'?'9:16':'16:9')));
   row.append(info,fig);list.append(row);
  });
  document.querySelectorAll('[data-orientation]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.orientation===orientation)));
 }
 document.querySelectorAll('[data-orientation]').forEach(b=>b.addEventListener('click',()=>{orientation=b.dataset.orientation;renderScenes();}));
 ['overlay-toggle','mask-toggle'].forEach(id=>$('#'+id).addEventListener('change',renderScenes));
 const animatic=$('#animatic'),stage=$('#motion-stage');
 if(intro){
  const study=intro.study(seconds=>{stop();$('#progress').value=String(Math.round(seconds/duration*1000));update();stage.scrollIntoView({behavior:'instant',block:'center'});});
  $('#journey .toolbar').before(study);
  $('#animatic .section-head p:last-child').textContent=ko?'로고 안의 항만에서 시작해 전체 장면으로 들어갑니다. 4.5초 인트로에 이어 30초 동안 중국 출발부터 미국 출고까지 확인하세요.':'从标志内的港口进入完整场景。4.5秒开场后，继续30秒中国出发至美国出库旅程。';
 }
 const geo=el('nav','geo-track');geo.setAttribute('aria-label',copy.geoLabel);
 copy.country.forEach((text,i)=>{const part=el('div','geo-stop');part.append(el('span','geo-code',['CN','PACIFIC','US'][i]),el('strong','',text));geo.append(part);});
 stage.before(geo);
 const direction=el('p','direction-caption');geo.after(direction);
 const controls=el('div','playback-controls'),play=el('button','play-button',copy.play);play.type='button';play.id='play-animatic';play.setAttribute('aria-pressed','false');controls.append(play,el('span','note',copy.country.join(' → ')));$('.scrub').before(controls);
 const strip=el('div','shot-strip');strip.setAttribute('role','group');strip.setAttribute('aria-label',copy.sequence);
 if(intro){const b=el('button','shot-button');b.type='button';b.dataset.index='-1';b.setAttribute('aria-label',intro.title);const preview=intro.create();preview.setAttribute('aria-hidden','true');b.append(preview,el('span','',intro.title));b.addEventListener('click',()=>{stop();$('#progress').value='0';update();});strip.append(b);}
 scenes.forEach((s,i)=>{const b=el('button','shot-button');b.type='button';b.dataset.index=i;b.setAttribute('aria-label',copy.scene+' '+(i+1)+': '+s[lang].title);const im=el('img');im.src=asset(s,'desktop').path;im.alt='';im.loading='lazy';b.append(im,el('span','',s.id+' · '+s[lang].place));b.addEventListener('click',()=>{stop();$('#progress').value=String(Math.round((introDuration+(i+.25)*5)*1000/duration));update();});strip.append(b);});
 strip.querySelectorAll('.shot-button>img').forEach(im=>window.CINEMA?.thumbnail(im));
 controls.before(strip);
 const stageFrames={};let introFrame;
 function renderStage(o){
  stage.replaceChildren();stage.className='motion-stage '+o;
  scenes.forEach(s=>{const f=frame(s,o,$('#animatic-copy').checked,$('#animatic-mask').checked);f.hidden=true;stage.append(f);stageFrames[s.id]=f;});
  if(intro){introFrame=intro.create(o);stage.append(introFrame);}
 }
 function update(){
  const p=Number($('#progress').value)/1000,seconds=p*duration,inIntro=seconds<introDuration,journey=Math.max(0,seconds-introDuration)/5,index=Math.min(5,Math.floor(journey)),local=p===1?1:journey-index,o=$('#animatic-orientation').value,s=scenes[index],t=s[lang],key=(inIntro?'INTRO':s.id)+'-'+o;
  if(!stage.classList.contains(o)||!stage.firstElementChild)renderStage(o);
  scenes.forEach((scene,i)=>{const f=stageFrames[scene.id];f.hidden=i!==index;if(i===index){f.querySelector('.overlay-layer').hidden=!$('#animatic-copy').checked;f.querySelector('.frame-mask').style.display=$('#animatic-mask').checked?'block':'none';f.querySelector('.shot-pixels').style.transform=media.matches?'none':o==='desktop'?'translateX('+(-local*.9)+'%) scale(1.028)':'translateY('+(-local*.7)+'%) scale(1.025)';}});
  if(intro){introFrame.hidden=!inIntro;if(inIntro){intro.render(introFrame,media.matches?0:seconds);stageFrames.S01.querySelector('.overlay-layer').hidden=true;stageFrames.S01.querySelector('.frame-mask').style.display='none';}}
  activeKey=key;stage.dataset.phase=inIntro?'INTRO':s.phase;stage.dataset.playing=String(playing);
  geo.querySelectorAll('.geo-stop').forEach((e,i)=>{const active=i===(index===0?0:index===1?1:2);e.classList.toggle('current',active);if(active)e.setAttribute('aria-current','step');else e.removeAttribute('aria-current');});
  direction.textContent=inIntro?(ko?'원본 로고 → 글자 확대 → 중국 출항 부두':'原始标志 → 放大字形 → 中国出发港'):t.place+' / '+copy.camera+': '+t.camera;
  strip.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.index)===(inIntro?-1:index))));
  $('#progress-label').textContent=(inIntro?'INTRO':String(index+1).padStart(2,'0')+' / 06')+' · '+Math.round(p*100)+'% · '+seconds.toFixed(1)+'s';
  $('#progress').setAttribute('aria-valuetext',(inIntro?intro.title:t.place+', '+t.title)+', '+Math.round(p*100)+'%');
  $('#transition-label').textContent=inIntro?copy.next+': '+scenes[0][lang].place:index<5?copy.next+': '+scenes[index+1][lang].place+' · '+scenes[index+1][lang].camera:copy.end;
  $('#reduced-note').hidden=!media.matches;
  play.disabled=media.matches;play.setAttribute('aria-pressed',String(playing));play.textContent=playing?copy.pause:p===1?copy.restart:copy.play;
 }
 function stop(){playing=false;cancelAnimationFrame(raf);last=0;stage.dataset.playing='false';play.setAttribute('aria-pressed','false');}
 function tick(now){
  if(!playing)return;
  if(last){playProgress=Math.min(1000,playProgress+(now-last)/duration);$('#progress').value=String(playProgress);}
  last=now;update();if(Number($('#progress').value)>=1000){stop();update();return;}raf=requestAnimationFrame(tick);
 }
 play.addEventListener('click',()=>{if(playing){stop();update();return;}if(media.matches)return;if(Number($('#progress').value)>=1000)$('#progress').value='0';playProgress=Number($('#progress').value);playing=true;last=0;update();raf=requestAnimationFrame(tick);});
 $('#progress').addEventListener('input',()=>{stop();update();});
 ['animatic-orientation','animatic-copy','animatic-mask'].forEach(id=>$('#'+id).addEventListener('change',update));
 media.addEventListener('change',()=>{if(media.matches)stop();document.body.classList.toggle('reduce-motion',media.matches);update();});
 document.addEventListener('visibilitychange',()=>{if(document.hidden){stop();update();}});
 $('#animatic-orientation').value=orientation;renderScenes();update();
 // Decode both orientations before switching to keep the next scene available.
 const preloads=[...data.assets.map(a=>a.path),...(intro?intro.assets:[])].map(path=>{const im=new Image();im.src=path;return im.decode().catch(()=>{errors.push(path);});});
 Promise.all(preloads).then(()=>document.body.dataset.preloaded='true');
 window.reviewQA={revision:3,duration,introDuration,scenes:scenes.map(s=>s.id),errors,get state(){return{orientation,progress:Number($('#progress').value),reducedMotion:media.matches,activeKey,playing,phase:stage.dataset.phase};}};
})();
