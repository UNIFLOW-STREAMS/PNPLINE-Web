"use client";

import { useLayoutEffect, useRef } from "react";
import Image from "next/image";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { CustomEase } from "gsap/CustomEase";

gsap.registerPlugin(ScrollTrigger, CustomEase);
const borderEase = CustomEase.create("pnpline-blind-border", ".5,0,.5,1");
const logoEase = CustomEase.create("pnpline-blind-logo", ".651,.013,.069,.994");
export const blindScrollDistance = () => Math.max(560, (document.querySelector<HTMLElement>(".journey-screen")?.offsetHeight || innerHeight) * 1.1);

// Measured curtain coverage in the attached recording, relative to 1.200 seconds.
// Duplicate capture frames are omitted. Columns run from left to right.
const revealDuration = 1.867;
// Preserve Figma border keyframe positions within the extended, recording-matched reveal.
const borderTimeScale = revealDuration / 1.3504;
const samples = [
  [.067, .1849, .1254, .0723, .0386, .0257, .0193],
  [.133, .4437, .3505, .2444, .1479, .1045, .0772],
  [.267, .6495, .5531, .4341, .3071, .2379, .1897],
  [.333, .7299, .6367, .5177, .3859, .3119, .2572],
  [.467, .8360, .7492, .6350, .5016, .4228, .3617],
  [.533, .9068, .8312, .7235, .5932, .5145, .4518],
  [.667, .9775, .9212, .8296, .7074, .6302, .5691],
  [.733, 1, .9646, .8842, .7717, .6977, .6367],
  [.867, 1, 1, .9325, .8328, .7621, .7042],
  [.933, 1, 1, .9486, .8521, .7846, .7267],
  [1.067, 1, 1, .9743, .8875, .8232, .7685],
  [1.133, 1, 1, .9904, .9164, .8553, .8023],
  [1.267, 1, 1, 1, .9486, .8939, .8441],
  [1.333, 1, 1, 1, .9678, .9180, .8714],
  [1.467, 1, 1, 1, .9871, .9453, .9003],
  [1.533, 1, 1, 1, 1, .9646, .9260],
  [1.667, 1, 1, 1, 1, .9887, .9582],
  [1.733, 1, 1, 1, 1, 1, .9743],
  [1.867, 1, 1, 1, 1, 1, 1],
];
const columns = [
  { left: 0, width: 53, borderEnd: .3 },
  { left: 53, width: 614, borderEnd: .3 },
  { left: 667, width: 614, borderEnd: .32 },
  { left: 1280, width: 614, borderEnd: .3568 },
  { left: 1894, width: 614, borderEnd: .368 },
  { left: 2508, width: 56, borderEnd: .3776 },
].map((column, i) => ({
  ...column,
  ease: CustomEase.create("pnpline-blind-" + i,
    "M0,0 " + samples.map(sample => "L" + sample[0] / revealDuration + "," + sample[i+1]).join(" ")),
}));

export default function SectionBlinds() {
  const ref = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    const mm = gsap.matchMedia();
    mm.add("(prefers-reduced-motion: no-preference)", () => {
      const overlay = ref.current!;
      const timeline = gsap.timeline({
        scrollTrigger: { start:0, end:blindScrollDistance, scrub:true, invalidateOnRefresh:true,
          onUpdate:self=>{overlay.style.visibility=self.progress===1?"hidden":"visible";} },
      });
      columns.forEach((column,i) => {
        const element = overlay.querySelectorAll(".blind-column")[i];
        timeline.fromTo(element, {y:0},
          {y:()=>-innerHeight - 1, duration:revealDuration, ease:column.ease}, 0);
        timeline.fromTo(element, {"--edge-opacity":0},
          {"--edge-opacity":1, duration:(column.borderEnd-.1)*borderTimeScale, ease:borderEase},
          .1*borderTimeScale);
      });
      timeline.fromTo(overlay.querySelector(".blind-logo"),{y:0},
        {y:()=>-innerHeight - 1,duration:.80,ease:logoEase},0);
      return () => {overlay.style.removeProperty("visibility");};
    });
    return () => mm.revert();
  }, []);
  return <div className="section-blinds" ref={ref} aria-hidden="true">
    {columns.map((column,i)=><div key={i} className="blind-column"
      style={{left:column.left/2564*100+"%",width:column.width/2564*100+"%"}} />)}
    <div className="blind-logo"><div><Image src="/assets/logo.webp" width={507} height={135} alt="" priority /></div><span>让物流衔接更顺畅</span></div>
  </div>;
}

