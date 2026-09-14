'use strict';
(async()=>{
 const $=s=>document.querySelector(s);
 const status=$('#load-status');
 const errors=[];
 const isKo=document.documentElement.lang.toLowerCase().startsWith('ko');
 const ui=isKo?{
  imageUnavailable:'이미지를 현재 표시할 수 없습니다. 자산 목록과 검증 기록을 확인해 주세요.',
  seeValidation:' 검증 기록을 확인해 주세요.',cta:'서비스 알아보기 ↗',desktop:'데스크톱 독립 구도',mobile:'모바일 독립 구도',placeholder:'임시 검토 문구',
  assetStatus:'자산 상태',stillCount:'정지 이미지 생성',videoCount:'영상 생성 0회',seconds:'초',nextScene:'다음 장면',occluder:'가림 요소',journeyEnd:'여정 종료 / 분기 출고',
  loadFailed:'검토 데이터를 불러오지 못했습니다. 저장소 루트에서 로컬 HTTP 서버를 실행한 뒤 README를 확인해 주세요. 여섯 단계: 중국 출발 → 국제 운송 → 미국 도착 → 입고 및 보관 → 피킹 및 포장 → 분기 출고.'
 }:{
  imageUnavailable:'图像暂不可用。请查看素材清单与验证记录。',seeValidation:' 请查看验证记录。',cta:'了解服务 ↗',desktop:'桌面独立构图',mobile:'移动端独立构图',placeholder:'临时评审文案',
  assetStatus:'素材状态',stillCount:'静帧生成',videoCount:'视频生成 0 次',seconds:'秒',nextScene:'下一场景',occluder:'遮挡物',journeyEnd:'旅程结束 / 出库分流',
  loadFailed:'评审数据未能加载。请从仓库根目录启动本地 HTTP 服务，然后查看 README。六阶段： 中国发运 → 国际运输 → 美国到港 → 入库与保管 → 拣选与包装 → 分流出库。'
 };
 const koScenes={
  S01:{title:'중국 출발',body:'화물을 모아 출발을 준비합니다.',desktop_composition:'팔레트 무리가 오른쪽 컨테이너와 먼 창고를 향해 대각선으로 이어집니다.',mobile_composition:'가까운 팔레트 작업, 중앙의 주요 컨테이너, 먼 창고를 세로 깊이로 쌓았습니다.'},
  S02:{title:'국제 운송',body:'해상 또는 항공 운송을 필요에 맞게 연결합니다.',desktop_composition:'후경의 해상 운송과 오른쪽 활주로를 나누고, 전경 적재 공간에서 연결합니다.',mobile_composition:'중앙 물류 거점을 기준으로 해상과 항공 공간을 나누고 전경에 화물을 배치했습니다.'},
  S03:{title:'미국 도착',body:'검사 준비를 마치고 창고 입고로 연결합니다.',desktop_composition:'오른쪽 중앙에 검사 대기 팔레트를 두고 뒤에 도크를 배치했으며, 전경 경로를 비웠습니다.',mobile_composition:'가까운 검사 팔레트 뒤로 민간 도크를 세우고, 경로는 오른쪽 가장자리를 따라 휘어집니다.'},
  S04:{title:'입고 및 보관',body:'화물을 입고한 뒤 지정 위치에 보관합니다.',desktop_composition:'넓게 열린 창고 내부와 전경 오른쪽 입고 구역, 후경 랙을 한눈에 보여 줍니다.',mobile_composition:'중앙 통로를 세로로 길게 두고 가까운 입고 구역과 높은 랙의 깊이를 강조했습니다.'},
  S05:{title:'피킹 및 포장',body:'피킹부터 포장까지 출고 준비를 진행합니다.',desktop_composition:'오른쪽 전경 작업대에서 시작한 컨베이어가 대각선 후방으로 이어집니다.',mobile_composition:'가까운 작업대와 스캔 동작에서 시작해 컨베이어가 후경으로 흐릅니다.'},
  S06:{title:'분기 출고',body:'FBA 입고 또는 택배 배송 경로로 나눕니다.',desktop_composition:'팔레트 차량과 택배 차량의 병렬 출고 동선을 오른쪽으로 펼쳤습니다.',mobile_composition:'가까운 택배 차량과 뒤쪽 팔레트 도크를 세로로 나누어 배치했습니다.'}
 };
 const koOccluders={'container edge':'컨테이너 모서리','terminal pillar':'물류 거점 기둥','dock column':'도크 기둥','rack upright':'랙 기둥','parcel wall':'상자 벽','final dock edge':'최종 도크 모서리'};
 function wireErrors(root=document){root.querySelectorAll('img').forEach(img=>{if(img.dataset.errorWired)return;img.dataset.errorWired='true';img.addEventListener('error',()=>{img.closest('.frame')?.classList.add('has-error');if(!img.closest('.frame')){let p=document.createElement('p');p.className='error-caption';p.textContent=ui.imageUnavailable;img.after(p);}errors.push(img.getAttribute('src'));});});}
 wireErrors();
 try{
 const [story,timeline,manifest]=await Promise.all(['data/storyboard.json','data/timeline.json','data/assets.json'].map(async p=>{let r=await fetch(p);if(!r.ok)throw new Error(p+' '+r.status);return r.json();}));
 const scenes=story.scenes.map(scene=>isKo?{...scene,...koScenes[scene.scene_id]}:scene),assets=manifest.assets;
 const masks={};await Promise.all(scenes.flatMap(s=>['desktop','mobile'].map(async o=>{let r=await fetch(s.masks[o]);if(!r.ok)throw new Error(s.masks[o]);masks[s.scene_id+'-'+o]=await r.json();})));
 let orientation=matchMedia('(max-width:767px)').matches?'mobile':'desktop';
 let reduce=matchMedia('(prefers-reduced-motion:reduce)');
 const getAsset=(sid,o)=>assets.find(a=>a.scene_id===sid&&a.orientation===o&&a.kind==='clean-branded');
 function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;}
 function frame(s,o,copy=true,mask=false){const a=getAsset(s.scene_id,o);const box=el('div','frame '+o);box.dataset.scene=s.scene_id;const img=el('img','scene-image');img.alt=s.title+(isKo?' · ':'：')+s.body+(isKo?' 콘셉트 이미지':' 概念示意');img.src=a?.path||'missing-'+s.scene_id+'.png';img.decoding='async';box.append(img);let err=el('p','error-note',ui.imageUnavailable+' '+s.title+(isKo?' · ':'：')+s.body+ui.seeValidation);err.setAttribute('role','status');box.append(err);
 const overlay=el('div','overlay-layer');overlay.hidden=!copy;
 masks[s.scene_id+'-'+o].regions.filter(r=>r.role==='text_allowed').forEach(r=>{let p=el('div','copy-part '+r.id);let [x,y,w,h]=r.rect;Object.assign(p.style,{left:x*100+'%',top:y*100+'%',width:w*100+'%',height:h*100+'%'});if(r.id==='cta'){p.append(el('span','',ui.cta));}else p.textContent=r.id==='title'?s.title:s.body;overlay.append(p);});box.append(overlay);
 const mi=el('img','frame-mask');mi.alt='';mi.src='masks/'+o+'/'+s.scene_id+'.svg';mi.hidden=!mask;box.append(mi);return box;}
 function renderScenes(){const list=$('#scene-list');list.replaceChildren();scenes.forEach(s=>{const row=el('article','scene-row');row.id='scene-'+s.scene_id;const info=el('div','scene-info');info.append(el('span','scene-number',s.scene_id+' / 06'),el('h3','',s.title),el('p','',s.body),el('p','note',orientation==='desktop'?s.desktop_composition:s.mobile_composition));const fig=el('figure');fig.append(frame(s,orientation,$('#overlay-toggle').checked,$('#mask-toggle').checked),el('figcaption','',(isKo?'콘셉트 이미지':'概念示意')+' · '+(orientation==='desktop'?ui.desktop:ui.mobile)+' · '+ui.placeholder));row.append(info,fig);list.append(row);});document.querySelectorAll('[data-orientation]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.orientation===orientation)));wireErrors(list);}
 document.querySelectorAll('[data-orientation]').forEach(b=>b.addEventListener('click',()=>{orientation=b.dataset.orientation;renderScenes();}));$('#overlay-toggle').addEventListener('change',renderScenes);$('#mask-toggle').addEventListener('change',renderScenes);
 const descriptions=isKo?{A:['밝은 산업 미니어처 / 선정 방향','부드러운 주광 아래 공정과 로고가 선명하게 보입니다. 여섯 장면으로 확장할 수 있으며 실제 미니어처 느낌은 프레임별 검토가 필요합니다.'],B:['해 질 녘 시네마틱 / 비교안','조명이 재질과 깊이를 강조합니다. 어두운 영역과 문구 배경 제어가 어렵고 모바일에서 공정을 알아보기 힘들 수 있습니다.'],C:['하이 앵글 테크니컬 / 비교안','동선과 공간 구성이 더 명확합니다. 입면 로고의 원근이 강하고 공정 세부와 여섯 장면의 연속 전진은 약합니다.']}:{A:['明亮工业微缩 / 已选方向','工序与字标在柔和日光下清晰可见。可扩展至六场景；实际微缩感仍需逐帧检视。'],B:['暮色电影感 / 比较用','灯光强调材质与纵深；暗部与文案背景更难控制，移动端的工序识别压力较高。'],C:['俯视技术感 / 比较用','流线与空间组织更清楚；立面标志透视更强，工序细节与六场景连续前进较弱。']};
 Object.entries(descriptions).forEach(([v,[title,body]])=>{const a=assets.find(a=>a.kind==='styleframe'&&a.variant===v);const card=el('article','variant '+(v==='A'?'selected':''));card.append(el('span','badge',v==='A'?'SELECTED DIRECTION':'COMPARISON ONLY'));const img=el('img');img.src=a?.path||'missing-styleframe-'+v+'.png';img.alt='S01 '+title;card.append(img,el('h3','',v+' — '+title),el('p','',body));$('#variants').append(card);});
 let activeKey='';
 function updateAnimatic(){const p=Number($('#progress').value)/1000;const index=Math.min(5,Math.floor(p*6));const local=p===1?1:p*6-index;const o=$('#animatic-orientation').value;const seg=timeline.segments[index];const stage=$('#motion-stage');const key=index+'-'+o;
 if(key!==activeKey){stage.replaceChildren();stage.className='motion-stage '+o;const clip=el('div','motion-clip');clip.append(frame(scenes[index],o,$('#animatic-copy').checked,$('#animatic-mask').checked));stage.append(clip,el('div','occluder'));activeKey=key;wireErrors(stage);}
 const f=stage.querySelector('.frame');f.style.transform=reduce.matches?'none':`translate(${(-local*0.35).toFixed(3)}%,${(-local*0.22).toFixed(3)}%) scale(${(1+local*.009).toFixed(4)})`;
 const overlay=f.querySelector('.overlay-layer');overlay.hidden=!$('#animatic-copy').checked;let enter=Math.min(1,Math.max(0,(local-seg.text_enter[0])/(seg.text_enter[1]-seg.text_enter[0])));let leave=index<5?Math.min(1,Math.max(0,(seg.text_exit[1]-local)/(seg.text_exit[1]-seg.text_exit[0]))):1;overlay.style.opacity=reduce.matches?'1':String(Math.min(enter,leave));
 f.querySelector('.frame-mask').hidden=!$('#animatic-mask').checked;
 // An entering foreground wall covers the outgoing still; on the next segment it exits,
 // revealing the next still. Opaque boundary, never a crossfade or duplicate logo layer.
 let cover=local>.86&&index<5?(1-(local-.86)/.14)*105:index>0&&local<.08?-(local/.08)*105:110;
 stage.querySelector('.occluder').style.transform=`translateX(${cover}%)`;
 $('#progress-label').textContent=String(index+1).padStart(2,'0')+' / 06 · '+Math.round(p*100)+'% · '+(p*30).toFixed(1)+'s';$('#progress').setAttribute('aria-valuetext',scenes[index].title+(isKo?', ':'，')+Math.round(p*100)+'%'+(isKo?', ':'，')+(p*30).toFixed(1)+ui.seconds);const occluder=isKo?koOccluders[seg.transition.occluder]:seg.transition.occluder;const labelSeparator=isKo?': ':'：';$('#transition-label').textContent=index<5?ui.nextScene+labelSeparator+scenes[index+1].title+' / '+ui.occluder+labelSeparator+occluder:ui.journeyEnd;document.body.classList.toggle('reduce-motion',reduce.matches);$('#reduced-note').hidden=!reduce.matches;
 }
 ['progress','animatic-orientation','animatic-mask','animatic-copy'].forEach(id=>$('#'+id).addEventListener(id==='progress'?'input':'change',updateAnimatic));reduce.addEventListener('change',updateAnimatic);
 $('#animatic-orientation').value=orientation;renderScenes();updateAnimatic();wireErrors();const manifestStatus=isKo&&manifest.status==='ready_for_review'?'검토 준비 완료':manifest.status;status.textContent=ui.assetStatus+(isKo?': ':'：')+manifestStatus+' · '+ui.stillCount+' '+manifest.counts.generated_unique+(isKo?'장':' 张')+' · '+ui.videoCount;
 window.reviewQA={scenes:scenes.map(s=>s.scene_id),errors,get state(){return{orientation,progress:Number($('#progress').value),reducedMotion:reduce.matches,activeKey}}};
 }catch(e){status.textContent=ui.loadFailed;status.className='error-caption';console.error('Review data load failed',e);}
})();
