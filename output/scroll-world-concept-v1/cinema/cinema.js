'use strict';
(()=>{
 const ns='http://www.w3.org/2000/svg';
 const node=(tag,attrs={})=>{const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));return e;};
 // AgX, Rec.2020 primaries and the polynomial sigmoid used by Three.js / Filament.
 // Source and license: cinema/README.md. Existing SDR images receive a 24% blend
 // of AgX, not a second full display transform. Browser SVG works in linear RGB.
 const to2020=[[.6274,.3293,.0433],[.0691,.9195,.0113],[.0164,.0880,.8956]];
 const inset=[[.856627153315983,.0951212405381588,.0482516061458583],[.137318972929847,.761241990602591,.101439036467562],[.11189821299995,.0767994186031903,.811302368396859]];
 const outset=[[1.1271005818144368,-.11060664309660323,-.016493938717834573],[-.1413297634984383,1.157823702216272,-.016493938717834257],[-.14132976349843826,-.11060664309660294,1.2519364065950405]];
 const toSRGB=[[1.6605,-.5876,-.0728],[-.1246,1.1329,-.0083],[-.0182,-.1006,1.1187]];
 const product=(a,b)=>a.map(row=>b[0].map((_,c)=>row.reduce((sum,v,k)=>sum+v*b[k][c],0)));
 const matrix=a=>a.map(row=>[...row,0,0].join(' ')).join(' ')+' 0 0 0 1 0';
 const values=Array.from({length:1025},(_,i)=>{
  const x=Math.max(0,Math.min(1,(Math.log2(Math.max(i/1024,1e-10))+12.47393)/16.499999));
  return Math.max(0,Math.min(1,15.5*x**6-40.14*x**5+31.96*x**4-6.868*x**3+.4298*x*x+.1191*x-.00232)).toFixed(7);
 }).join(' ');
 const svg=node('svg',{'aria-hidden':'true',width:0,height:0,focusable:'false'});svg.style.cssText='position:absolute;pointer-events:none;overflow:hidden';
 const defs=node('defs'),filter=node('filter',{id:'cinema-agx',x:'0%',y:'0%',width:'100%',height:'100%','color-interpolation-filters':'linearRGB'});
 filter.append(node('feColorMatrix',{in:'SourceGraphic',type:'matrix',values:matrix(product(inset,to2020))}));
 const logSigmoid=node('feComponentTransfer');['R','G','B'].forEach(c=>logSigmoid.append(node('feFunc'+c,{type:'table',tableValues:values})));filter.append(logSigmoid);
 filter.append(node('feColorMatrix',{type:'matrix',values:matrix(outset)}));
 const linearize=node('feComponentTransfer');['R','G','B'].forEach(c=>linearize.append(node('feFunc'+c,{type:'gamma',amplitude:1,exponent:2.2,offset:0})));filter.append(linearize);
 filter.append(node('feColorMatrix',{type:'matrix',values:matrix(toSRGB),result:'agx'}));
 filter.append(node('feComposite',{in:'agx',in2:'SourceGraphic',operator:'arithmetic',k1:0,k2:.24,k3:.76,k4:0}));
 filter.append(node('feColorMatrix',{type:'saturate',values:.96}));
 const exposure=node('feComponentTransfer');['R','G','B'].forEach(c=>exposure.append(node('feFunc'+c,{type:'linear',slope:.8,intercept:0})));filter.append(exposure);
 defs.append(filter);svg.append(defs);document.body.prepend(svg);
 document.documentElement.classList.add('cinema-ready');
 function mount(surface){
  if(surface.querySelector(':scope>.cinema-fx'))return;
  const fx=document.createElement('div');fx.className='cinema-fx';fx.setAttribute('aria-hidden','true');
  for(const name of ['dof','vignette','grain']){const layer=document.createElement('div');layer.className='cinema-'+name;fx.append(layer);}
  surface.append(fx);surface.classList.add('cinema-surface');
 }
 function thumbnail(image){
  // Keep the native image and its source for accessibility and existing navigation.
  const surface=document.createElement('div');surface.className='cinema-thumbnail';
  image.replaceWith(surface);surface.append(image);mount(surface);
 }
 window.CINEMA={mount,thumbnail,profile:{toneMapping:'AgX SDR blend',agxMix:.24,linearExposure:.8,saturation:.96,vignetteCorner:.76}};
})();
