'use strict';
(() => {
 document.documentElement.classList.toggle('embedded',new URLSearchParams(location.search).has('embedded'));
 const $=s=>document.querySelector(s),reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const clamp=(v,a,b)=>Math.max(a,Math.min(b,v)),lerp=(a,b,t)=>a+(b-a)*t;
 const intro=window.BRAND_INTRO,introDuration=intro?.duration||0,totalDuration=30+introDuration,introImage='high-angle-c/intro-harbor.png';
 const scenes=[
  {place:'중국 · 출항 부두',title:'중국에서 출발',body:'카메라가 붉은 크레인에서 선박을 향해 전진합니다.',x:.115,region:'CN',camera:'하이 앵글 · 부두에서 선박으로 이동'},
  {place:'태평양 · 해상 운송',title:'선박을 따라 태평양 횡단',body:'선박과 함께 이동하며 오른쪽의 미국 항만을 드러냅니다.',x:.32,region:'PACIFIC',camera:'하이 앵글 · 선박 추적과 항만 접근'},
  {place:'미국 · 도착 항만',title:'미국 도착, 창고로 접근',body:'미국 항만에 도착한 뒤 창고를 향해 카메라를 좁힙니다.',x:.46,region:'US',camera:'하이 앵글 접근 → 창고의 낮은 시점으로 전환'},
  {place:'미국 · 입고 및 보관',title:'컨테이너에서 창고 안으로',body:'도착한 화물을 내리고 지게차와 보관 랙을 따라 들어갑니다.',region:'US',camera:'낮은 사선 시점 · 컨테이너에서 보관 랙으로',file:'us-receiving.png',focus:[.32,.61],masks:[[.198,.222,.183,.093],[.15,.51,.116,.104]]},
  {place:'미국 · 피킹 및 포장',title:'포장 작업대에서 출고 도어로',body:'주문별 상자를 포장한 뒤 컨베이어를 따라 트럭으로 연결합니다.',region:'US',camera:'작업대 높이 · 컨베이어를 따라 오른쪽으로',file:'us-packing.png',focus:[.43,.65],masks:[[.341,.601,.274,.145]]},
  {place:'미국 · 출고 및 배송',title:'창고를 나서 미국 내 배송으로',body:'출고 도어에서 배송 차량과 미국 내 도로로 시선을 옮깁니다.',region:'US',camera:'출고장 사선 시점 · 배송 차량으로 이동',file:'us-dispatch.png',focus:[.53,.73],masks:[[.458,.572,.219,.133]]}
 ];
 const mobileAssets={
  2:{file:'us-arrival-mobile.png',masks:[[.30,.517,.26,.075]]},
  3:{file:'us-receiving-mobile.png',masks:[[.218,.257,.41,.063],[.28,.531,.17,.06]]},
  4:{file:'us-packing-mobile.png',masks:[[.30,.568,.5,.163]]},
  5:{file:'us-dispatch-mobile.png',masks:[[.30,.553,.377,.083]]}
 };
 const cameraKeys=[
  {x:.105,y:.52,z:1.9},{x:.285,y:.50,z:1.55},
  {x:.445,y:.48,z:1.9},{x:.595,y:.46,z:2.45}
 ];
 let p=0,playing=false,overview=false,raf=0,last=0;
 let orientation=matchMedia('(max-width:767px)').matches?'mobile':'desktop';
 const stage=$('#stage'),world=$('#world'),image=$('#world-image'),buttons=[],frames=[];
 const introFrames=intro?{desktop:intro.create('desktop',introImage),mobile:intro.create('mobile',introImage)}:{};
 Object.values(introFrames).forEach(frame=>stage.append(frame));
 let introPreview,introButton;
 if(intro){
  introButton=document.createElement('button');introButton.className='shot intro-shot';introButton.type='button';introButton.setAttribute('aria-label','로고 인트로');
  introPreview=intro.create(orientation,introImage);introPreview.dataset.orientation=orientation;introPreview.setAttribute('aria-hidden','true');
  const title=document.createElement('span');title.textContent='INTRO · 로고에서 항만으로';introButton.append(introPreview,title);
  introButton.addEventListener('click',()=>{stop();p=0;overview=false;draw();});$('#shots').append(introButton);
  const study=intro.study(seconds=>{stop();p=seconds/totalDuration;overview=false;draw();stage.scrollIntoView({behavior:'instant',block:'center'});},introImage);
  document.querySelector('#animatic .toolbar').before(study);
 }
 scenes.forEach((s,i)=>{
  for(const format of ['desktop','mobile']){
   const source=format==='mobile'?mobileAssets[i]:s;
   if(!source?.file)continue;
   const layer=document.createElement('div');layer.className='us-frame';layer.dataset.scene=String(i+1);layer.dataset.orientation=format;layer.hidden=true;
   const pixels=document.createElement('div');pixels.className='us-pixels';
   const im=document.createElement('img');im.src='high-angle-c/'+source.file;im.alt=s.place+' · '+s.body;
   pixels.append(im);
   source.masks.forEach(bounds=>{const mask=document.createElement('span');mask.className='us-logo-mask';mask.setAttribute('aria-hidden','true');['left','top','width','height'].forEach((key,n)=>mask.style[key]=bounds[n]*100+'%');pixels.append(mask);});
   layer.append(pixels);world.after(layer);frames.push({layer,pixels,im,index:i,format});
  }
  const b=document.createElement('button');b.className='shot';b.type='button';b.setAttribute('aria-label',String(i+1)+'. '+s.place);
  const thumb=document.createElement('img');thumb.src=s.file?'high-angle-c/'+s.file:image.getAttribute('src');thumb.alt='';thumb.loading='lazy';
  if(!s.file)thumb.style.objectPosition=(clamp((s.x-.267)/.466,0,1)*100)+'% 50%';
  const title=document.createElement('span');title.textContent=String(i+1).padStart(2,'0')+' · '+s.place;
  b.append(thumb,title);b.addEventListener('click',()=>{stop();p=(introDuration+i*5)/totalDuration;overview=false;draw();});
  $('#shots').append(b);buttons.push(b);window.CINEMA?.thumbnail(thumb);
 });
 window.CINEMA?.mount(stage);
 function stop(){playing=false;last=0;stage.dataset.playing='false';cancelAnimationFrame(raf);}
 function draw(){
  const arrivalTime=orientation==='mobile'?10:15;
  const seconds=p*totalDuration,inIntro=!overview&&seconds<introDuration,journeySeconds=clamp(seconds-introDuration,0,30),active=Math.min(5,Math.floor(journeySeconds/5)),s=scenes[active];
  // Reduced motion uses fixed compositions for each scene, including manual scrubbing.
  const motionTime=reduced.matches?active*5:journeySeconds;
  const highTime=clamp(motionTime,0,15),keyIndex=Math.min(2,Math.floor(highTime/5)),u=(highTime-keyIndex*5)/5;
  const from=cameraKeys[keyIndex],to=cameraKeys[keyIndex+1];
  const x=lerp(from.x,to.x,u),y=lerp(from.y,to.y,u),zoom=lerp(from.z,to.z,u);
  stage.classList.toggle('mobile',orientation==='mobile');
  const w=stage.clientWidth,h=stage.clientHeight;
  let worldHeight=h*zoom,worldWidth=worldHeight*3;
  let tx=clamp(w/2-x*worldWidth,w-worldWidth,0),ty=clamp(h/2-y*worldHeight,h-worldHeight,0);
  if(overview){worldWidth=Math.min(w,h*3);worldHeight=worldWidth/3;tx=(w-worldWidth)/2;ty=(h-worldHeight)/2;}
  world.hidden=inIntro||(!overview&&journeySeconds>=arrivalTime);
  world.style.width=worldWidth+'px';world.style.transform='translate('+tx+'px,'+ty+'px)';
  frames.forEach(({layer,pixels,index,format,im})=>{
   // Dissolve over the last 0.7s of each preceding scene, then keep the new frame fully visible.
   const start=index*5,alpha=reduced.matches?Number(journeySeconds>=start):clamp((journeySeconds-(start-.7))/.7,0,1);
   layer.hidden=inIntro||format!==orientation||overview||alpha===0||(index<5&&journeySeconds>=(index+1)*5);
   layer.style.opacity=String(alpha);layer.style.zIndex=String(index);
   const local=reduced.matches?.5:clamp((journeySeconds-start+.7)/5.7,0,1);
   const portrait=format==='mobile',ratio=im.naturalWidth/im.naturalHeight||(portrait?941/1672:1672/941);
   // Portrait artwork already contains the complete composition; only a gentle 2.5% push-in is needed.
   const scale=portrait?lerp(1,1.025,local):lerp(1.035,1.17,local);
   const cw=Math.max(w,h*ratio)*scale,ch=cw/ratio;
   const focus=portrait?.5:lerp(.46,.57,local);
   pixels.style.width=cw+'px';pixels.style.height=ch+'px';
   pixels.style.transform='translate('+clamp(w/2-focus*cw,w-cw,0)+'px,'+clamp(h/2-.49*ch,h-ch,0)+'px)';
  });
  stage.classList.toggle('show-mask',$('#mask').checked);
  $('#mask-note').hidden=inIntro||!$('#mask').checked;
  $('#caption').hidden=inIntro||!$('#copy').checked;
  $('#route-map').style.display=!inIntro&&$('#route').checked&&(overview||journeySeconds<arrivalTime)?'block':'none';
  $('#route').disabled=inIntro||(!overview&&journeySeconds>=arrivalTime);
  $('#route-label').textContent=journeySeconds>=arrivalTime&&!overview?'이동 경로 · 하이 앵글 구간 전용':'이동 경로';
  $('#scene-kicker').textContent=inIntro?'INTRO · 00 / 06':String(active+1).padStart(2,'0')+' / 06 · '+s.place;
  $('#scene-title').textContent=inIntro?'로고에서 중국 항만으로':s.title;$('#scene-body').textContent=inIntro?'원본 로고 안의 항만으로 들어가 첫 여정을 시작합니다.':s.body;
  $('#camera-note').textContent=inIntro?'원본 로고 → 글자 확대 → 중국 출항 부두':overview?'전체 지도 · 국제 운송 경로 확인 / 재생하면 카메라 추적으로 돌아갑니다.':(orientation==='mobile'&&active===2?'낮은 사선 시점 · 미국 항만 하역에서 창고로':s.camera)+' / '+s.place;
  $('#progress').value=String(Math.round(p*1000));
  $('#progress').setAttribute('aria-valuetext',(inIntro?'로고 인트로':s.place)+', '+seconds.toFixed(1)+'초');
  $('#time').textContent=seconds.toFixed(1).padStart(4,'0')+' / '+totalDuration+'s';
  $('#overview').setAttribute('aria-pressed',String(overview));
  ['desktop','mobile'].forEach(o=>$('#'+o).setAttribute('aria-pressed',String(orientation===o)));
  $('#shots').classList.toggle('portrait-shots',orientation==='mobile');
  if(intro&&introPreview.dataset.orientation!==orientation){const next=intro.create(orientation,introImage);next.dataset.orientation=orientation;next.setAttribute('aria-hidden','true');introPreview.replaceWith(next);introPreview=next;}
  buttons.forEach((b,n)=>{
   const thumb=b.querySelector('img'),source=orientation==='mobile'?mobileAssets[n]:scenes[n];
   const src=source?.file?'high-angle-c/'+source.file:image.getAttribute('src');
   if(thumb.getAttribute('src')!==src)thumb.src=src;
   thumb.style.objectPosition=source?.file?'50% 50%':(clamp((scenes[n].x-.267)/.466,0,1)*100)+'% 50%';
   b.setAttribute('aria-pressed',String(!inIntro&&active===n));if(!inIntro&&n===active)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current');});
  if(introButton){introButton.setAttribute('aria-pressed',String(inIntro));if(inIntro)introButton.setAttribute('aria-current','step');else introButton.removeAttribute('aria-current');}
  Object.entries(introFrames).forEach(([format,frame])=>{frame.hidden=!inIntro||format!==orientation;if(!frame.hidden)intro.render(frame,reduced.matches?0:seconds);});
  document.querySelectorAll('[data-region]').forEach(e=>e.classList.toggle('active',!inIntro&&e.dataset.region===s.region));
  $('#play').textContent=playing?'일시 정지':p>=1?'처음부터 재생':'인트로부터 재생';$('#play').setAttribute('aria-pressed',String(playing));
  $('#play').disabled=reduced.matches;$('#reduced-note').hidden=!reduced.matches;
  const path=$('#route-path'),point=path.getPointAtLength(path.getTotalLength()*clamp(motionTime/15,0,1));
  $('#cargo').setAttribute('cx',point.x);$('#cargo').setAttribute('cy',point.y);
  stage.dataset.scene=inIntro?'INTRO':String(active+1);stage.dataset.overview=String(overview);stage.dataset.mode=inIntro?'intro':overview?'overview':journeySeconds<arrivalTime?'aerial':'warehouse';stage.dataset.playing=String(playing);
 }
 function tick(now){if(!playing)return;if(last)p=Math.min(1,p+(now-last)/(totalDuration*1000));last=now;if(p>=1)stop();draw();if(playing)raf=requestAnimationFrame(tick);}
 $('#play').addEventListener('click',()=>{if(playing){stop();draw();return;}if(reduced.matches)return;if(p>=1)p=0;overview=false;playing=true;last=0;draw();raf=requestAnimationFrame(tick);});
 $('#progress').addEventListener('input',()=>{stop();p=Number($('#progress').value)/1000;overview=false;draw();});
 $('#overview').addEventListener('click',()=>{stop();overview=!overview;draw();});
 ['desktop','mobile'].forEach(o=>$('#'+o).addEventListener('click',()=>{orientation=o;draw();}));
 ['copy','mask','route'].forEach(id=>$('#'+id).addEventListener('change',draw));
 reduced.addEventListener('change',()=>{stop();draw();});
 document.addEventListener('visibilitychange',()=>{if(document.hidden){stop();draw();}});
 window.addEventListener('message',event=>{
  if(event.data?.type==='pnpline:pause'){stop();draw();}
  if(event.data?.type==='pnpline:present'&&['desktop','mobile'].includes(event.data.orientation)){orientation=event.data.orientation;stop();draw();}
 });
 new ResizeObserver(draw).observe(stage);
 const assets=[image,...frames.map(f=>f.im),...Object.values(introFrames).map(frame=>frame.querySelector('.brand-intro-photo'))];
 assets.forEach(im=>im.addEventListener('error',()=>{$('#image-error').hidden=false;stop();draw();}));
 Promise.all(assets.map(im=>im.decode())).then(()=>{document.body.dataset.ready='true';draw();}).catch(()=>{$('#image-error').hidden=false;});
 window.studyC={duration:totalDuration,introDuration,get state(){return{progress:p,playing,overview,orientation,scene:stage.dataset.scene,mode:stage.dataset.mode,reduced:reduced.matches};}};
 draw();
})();
