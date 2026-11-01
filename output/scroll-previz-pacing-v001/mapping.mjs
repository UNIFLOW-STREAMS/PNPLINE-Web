// scroll-world adaptation: one existing film, arbitrary observed slow zones.
// PCHIP of source frame -> cumulative viewport heights; invert for scrubbing.
export function buildMapping(config) {
  const x=[],y=[],boundaries=[];let total=0;
  for(const s of config.sections){
    if(s.endFrame<=s.startFrame||s.scrollVh<=0)throw Error('Invalid section');
    const weights=[];let sum=0;
    for(let f=s.startFrame;f<s.endFrame;f++){
      let w=1;
      for(const z of s.slowZones){const u=(f+.5-z.startFrame)/(z.endFrame-z.startFrame);if(u>0&&u<1)w+=2*z.strength*Math.sin(Math.PI*u)**2;}
      weights.push(w);sum+=w;
    }
    boundaries.push({...s,scrollStart:total,scrollEnd:total+s.scrollVh});
    if(!x.length){x.push(s.startFrame);y.push(0);}
    let accum=0;
    for(let f=s.startFrame;f<s.endFrame;f++){
      accum+=weights[f-s.startFrame];
      if((f+1-s.startFrame)%5===0||f+1===s.endFrame){x.push(f+1);y.push(total+s.scrollVh*accum/sum);}
    }
    total+=s.scrollVh;y[y.length-1]=total;
  }
  const h=x.slice(1).map((v,i)=>v-x[i]),d=y.slice(1).map((v,i)=>(v-y[i])/h[i]);
  const m=[d[0]];
  for(let i=1;i<x.length-1;i++){const a=2*h[i]+h[i-1],b=h[i]+2*h[i-1];m.push((a+b)/(a/d[i-1]+b/d[i]));}m.push(d.at(-1));
  function index(f){let a=0,b=x.length-1;while(a+1<b){const k=(a+b)>>1;if(x[k]<=f)a=k;else b=k;}return a;}
  function scrollAtFrame(f){f=Math.max(x[0],Math.min(x.at(-1),f));const i=index(f),u=(f-x[i])/h[i];return (2*u**3-3*u*u+1)*y[i]+(u**3-2*u*u+u)*h[i]*m[i]+(-2*u**3+3*u*u)*y[i+1]+(u**3-u*u)*h[i]*m[i+1];}
  function slope(f){const i=index(Math.max(x[0],Math.min(x.at(-1),f))),u=(f-x[i])/h[i];return ((6*u*u-6*u)*y[i]+(3*u*u-4*u+1)*h[i]*m[i]+(-6*u*u+6*u)*y[i+1]+(3*u*u-2*u)*h[i]*m[i+1])/h[i];}
  function frameAtProgress(p,mode='paced'){p=Math.max(0,Math.min(1,p));if(mode==='linear')return config.frameStart+p*(config.frameEnd-config.frameStart);if(!p)return x[0];if(p===1)return x.at(-1);let a=x[0],b=x.at(-1);for(let k=0;k<36;k++){const mid=(a+b)/2;if(scrollAtFrame(mid)<p*total)a=mid;else b=mid;}return (a+b)/2;}
  return {total,boundaries,x,y,m,scrollAtFrame,slope,frameAtProgress,progressAtFrame:(f,mode='paced')=>mode==='linear'?(f-config.frameStart)/(config.frameEnd-config.frameStart):scrollAtFrame(f)/total,sectionAtFrame:f=>boundaries.find(s=>f>=s.startFrame&&f<s.endFrame)||boundaries.at(-1)};
}
