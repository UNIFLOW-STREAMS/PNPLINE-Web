'use strict';
(() => {
 const tabs=[...document.querySelectorAll('[role="tab"][data-version]')];
 const panels={basic:document.querySelector('#panel-basic'),'high-angle':document.querySelector('#panel-high-angle')};
 const frame=document.querySelector('#high-angle-frame');let resizeObserver,highAnglePresented=false;
 function pauseBasic(){const play=document.querySelector('#play-animatic');if(window.reviewQA?.state?.playing&&play)play.click();}
 function pauseHighAngle(){frame.contentWindow?.postMessage({type:'pnpline:pause'},location.origin);}
 function sizeFrame(){try{const doc=frame.contentDocument;if(!doc)return;frame.contentWindow.scrollTo(0,0);const height=Math.max(doc.documentElement.scrollHeight,doc.body?.scrollHeight||0);if(height>0)frame.style.height=height+'px';}catch{}}
 function resetPageScroll(){
  const root=document.documentElement,anchor=document.querySelector('#version-switch-anchor'),previous=root.style.scrollBehavior;
  root.style.scrollBehavior='auto';window.scrollTo(0,anchor.offsetTop);
  requestAnimationFrame(()=>{window.scrollTo(0,anchor.offsetTop);root.style.scrollBehavior=previous;});
 }
 function watchFrame(){try{resizeObserver?.disconnect();const doc=frame.contentDocument;if(!doc)return;resizeObserver=new ResizeObserver(()=>requestAnimationFrame(sizeFrame));resizeObserver.observe(doc.documentElement);sizeFrame();}catch{}}
 function presentHighAngle(){
  if(highAnglePresented||!frame.contentWindow?.studyC)return;
  frame.contentWindow.postMessage({type:'pnpline:present',orientation:innerWidth<768?'mobile':'desktop'},location.origin);highAnglePresented=true;
 }
 function activate(version,{updateHash=true,focus=false}={}){
  if(!panels[version])version='basic';const leaving=document.body.dataset.activeVersion;
  if(leaving==='basic'&&version!=='basic')pauseBasic();if(leaving==='high-angle'&&version!=='high-angle')pauseHighAngle();
  tabs.forEach(tab=>{const selected=tab.dataset.version===version;tab.setAttribute('aria-selected',String(selected));tab.tabIndex=selected?0:-1;if(selected&&focus)tab.focus();});
  Object.entries(panels).forEach(([name,panel])=>panel.hidden=name!==version);document.body.dataset.activeVersion=version;
  if(updateHash){history.replaceState(null,'','#'+version);resetPageScroll();}
  if(version==='high-angle'){presentHighAngle();frame.contentWindow?.scrollTo(0,0);sizeFrame();requestAnimationFrame(()=>{presentHighAngle();frame.contentWindow?.scrollTo(0,0);sizeFrame();});}
 }
 tabs.forEach((tab,index)=>{tab.addEventListener('click',()=>activate(tab.dataset.version));tab.addEventListener('keydown',event=>{let next;if(event.key==='ArrowRight')next=(index+1)%tabs.length;if(event.key==='ArrowLeft')next=(index-1+tabs.length)%tabs.length;if(event.key==='Home')next=0;if(event.key==='End')next=tabs.length-1;if(next===undefined)return;event.preventDefault();activate(tabs[next].dataset.version,{focus:true});});});
 frame.addEventListener('load',()=>{watchFrame();if(document.body.dataset.activeVersion==='high-angle')presentHighAngle();});window.addEventListener('resize',()=>requestAnimationFrame(sizeFrame));
 window.addEventListener('hashchange',()=>{if(location.hash==='#high-angle')activate('high-angle',{updateHash:false});else if(location.hash==='#basic')activate('basic',{updateHash:false});});
 activate(location.hash==='#high-angle'?'high-angle':'basic',{updateHash:false});window.demoTabs={activate,get active(){return document.body.dataset.activeVersion;}};
})();
