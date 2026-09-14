'use strict';
(()=>{
 const ns='http://www.w3.org/2000/svg', logo='assets/logo/PNP-LINE.webp', image='continuity-v2/intro/china-harbor.png';
 const ko=document.documentElement.lang.startsWith('ko');
 let serial=0;
 const clamp=x=>Math.max(0,Math.min(1,x)),ease=x=>{x=clamp(x);return x*x*(3-2*x);};
 const svgEl=(tag,attrs={})=>{const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));return e;};
 function create(orientation='desktop',source=image){
  const mobile=orientation==='mobile',w=mobile?900:1600,h=mobile?1600:900,id='brand-reveal-'+(++serial);
  const root=document.createElement('div');root.className='brand-intro '+orientation;root.dataset.scene='INTRO';
  const photo=document.createElement('img');photo.className='brand-intro-photo';photo.src=source;photo.alt=ko?'중국 출항 부두의 PNPLINE 컨테이너와 선박':'中国出发港的 PNPLINE 集装箱与货船';photo.decoding='async';root.append(photo);
  const svg=svgEl('svg',{viewBox:`0 0 ${w} ${h}`,preserveAspectRatio:'none','aria-hidden':'true'}),defs=svgEl('defs');
  // Preserve the supplied wordmark's alpha; its blue and gray colors must cut identical holes.
  const filter=svgEl('filter',{id:id+'-ink','color-interpolation-filters':'sRGB'});
  filter.append(svgEl('feColorMatrix',{type:'matrix',values:'0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0'}));
  const mask=svgEl('mask',{id,maskUnits:'userSpaceOnUse',x:0,y:0,width:w,height:h,'mask-type':'luminance'});
  const mark=svgEl('image',{href:logo,width:1500,height:400,filter:`url(#${id}-ink)`});mark.classList.add('intro-wordmark');
  mask.append(svgEl('rect',{width:w,height:h,fill:'white'}),mark);defs.append(filter,mask);
  svg.append(defs,svgEl('rect',{width:w,height:h,fill:'#f7f8f5',mask:`url(#${id})`}));root.append(svg);
  root._intro={mark,w,h,base:w*(mobile?.9:.78)/1500};render(root,0);return root;
 }
 function render(root,seconds){
  const {mark,w,h,base}=root._intro;
  // After a short readable hold, grow around a solid part of the L stem. At 96x
  // this stroke covers the viewport, so there is no fade that fills letter gaps.
  const zoom=Math.exp(Math.log(96)*ease((seconds-.6)/3.2)),scale=base*zoom;
  mark.setAttribute('transform',`matrix(${scale} 0 0 ${scale} ${w/2-770*scale+20*base} ${h/2-175*scale-25*base})`);
  root.dataset.zoom=zoom.toFixed(3);
  // The final half second settles into the existing first shot (portrait on mobile).
  root.style.opacity=String(1-ease((seconds-4)/.5));
 }
 function study(seek,source=image){
  const box=document.createElement('div');box.className='intro-study';
  const heading=document.createElement('h3');heading.textContent=ko?'로고에서 시작하는 여정':'从标志开始的旅程';
  const desc=document.createElement('p');desc.className='note';desc.textContent=ko?'4.5초 인트로 · 원본 로고 안으로 들어가 중국 출항 부두에 도착합니다. 키프레임을 클릭하면 해당 순간으로 이동합니다.':'4.5秒开场 · 穿过原始标志进入中国出发港。点击关键帧跳转到对应时刻。';
  const grid=document.createElement('div');grid.className='intro-keyframes';
  [[0,ko?'로고 안의 항만':'标志内的港口'],[1.9,ko?'글자 안으로 확대':'进入字形'],[3.9,ko?'항만 전체로 전환':'展开完整港口']].forEach(([seconds,title])=>{
   const button=document.createElement('button');button.type='button';button.className='intro-keyframe';
   const visual=create('desktop',source);render(visual,seconds);visual.setAttribute('aria-hidden','true');
   const label=document.createElement('span');label.textContent=seconds.toFixed(1)+'s · '+title;
   button.append(visual,label);button.addEventListener('click',()=>seek(seconds));grid.append(button);
  });box.append(heading,desc,grid);return box;
 }
 window.BRAND_INTRO={create,render,study,duration:4.5,assets:[logo,image],title:ko?'로고 인트로':'标志开场'};
})();
