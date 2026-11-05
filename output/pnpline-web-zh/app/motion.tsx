"use client";
import { useLayoutEffect, useRef, useSyncExternalStore, type ReactNode } from "react";
import gsap from "gsap";
import { mountHeroJourney } from "./hero-journey";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { CustomEase } from "gsap/CustomEase";

gsap.registerPlugin(ScrollTrigger, CustomEase);
const ease = CustomEase.create("pnpline", ".241,0,.138,1");
export const reduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
export function topOfPage() {
  const finish = () => {
    history.replaceState(null,"","#top");
    document.querySelector<HTMLElement>(".nav-inner > a")?.focus({preventScroll:true});
  };
  const position = {y:window.scrollY};
  gsap.to(position,{y:0,duration:reduced()?0:.4,ease,
    onUpdate:()=>window.scrollTo({top:position.y,behavior:"instant"}),onComplete:finish});

}

const narrow = "(max-width:767px)";
function listenWidth(notify:()=>void) {
  const query = matchMedia(narrow);
  query.addEventListener("change",notify);
  return ()=>query.removeEventListener("change",notify);
}
export function useNarrowLayout() {
  return useSyncExternalStore(listenWidth,()=>matchMedia(narrow).matches,()=>false);
}

export function RevealPanel({open, id, duration, children}:{open:boolean;id:string;duration:number;children:ReactNode}) {
  const ref = useRef<HTMLDivElement>(null);
  const initial = useRef(open);
  useLayoutEffect(() => {
    const el = ref.current!;
    const mm = gsap.matchMedia();
    mm.add({ reduce:"(prefers-reduced-motion: reduce)", normal:"(prefers-reduced-motion: no-preference)" }, ctx => {
      const instant = ctx.conditions?.reduce || open === initial.current;
      // React owns the initial dimensions. On interruption start from the current pixels.
      const height = el.getBoundingClientRect().height;
      const opacity = getComputedStyle(el).opacity;
      const timeline = gsap.timeline({defaults:{ease},onComplete:()=>ScrollTrigger.refresh()});
      timeline.fromTo(el,{height},{height:open?"auto":0,duration:instant?0:duration},0)
        .fromTo(el,{opacity},{opacity:open?1:0,duration:instant?0:.18},0);
      return () => {timeline.kill();};
    });
    initial.current = open;
    return () => {
      // Preserve the interrupted geometry across effect cleanup (including rapid clicks).
      const h = el.getBoundingClientRect().height, o = getComputedStyle(el).opacity;
      mm.revert(); el.style.height = h+"px"; el.style.opacity = o;
    };
  },[open,duration]);
  const first = useRef(open);
  return <div className="reveal-panel" ref={ref} id={id} inert={!open} aria-hidden={!open}
    style={{height:first.current?"auto":0,opacity:first.current?1:0}}><div className="reveal-content">{children}</div></div>;
}

export function useSectionMotion() {
  useLayoutEffect(() => {
    const mm = gsap.matchMedia();
    mm.add("(prefers-reduced-motion: no-preference)", () => {
      const cleanupJourney = mountHeroJourney();
      gsap.utils.toArray<HTMLElement>("main h1, main h2").forEach(title => {
        if(title.closest(".import-consultation, .import-alternative, .consultation-process, .pricing-concept, .faq-concept, .quote-inquiry, .warehouse-workflow, .system-requirements")) return;
        if (!title.querySelector(".motion-word") && !title.closest("#pricing")) return;
        if (title.closest("#services")) {
          gsap.from(title.querySelectorAll(".motion-word"), {
            yPercent:110, opacity:0, duration:.65, stagger:.065, ease,
            scrollTrigger:{trigger:title,start:"top 94%",once:true}
          });
        } else if (title.closest("#pricing")) {
          gsap.from(title,{y:18,opacity:0,duration:.35,ease,scrollTrigger:{trigger:title,start:"top 95%",once:true}});
        } else {
          gsap.from(title.querySelectorAll(".motion-word"),{y:24,opacity:0,duration:.48,stagger:.04,ease,
            scrollTrigger:{trigger:title,start:"top 98%",once:true}});
        }
      });
      return cleanupJourney;
    });
    // Recalculate coordinates after accordions, font loads and responsive rearrangements settle.
    let timer:ReturnType<typeof setTimeout>;
    const observer = new ResizeObserver(()=>{clearTimeout(timer); timer=setTimeout(()=>ScrollTrigger.refresh(),100);});
    document.querySelectorAll("main > section").forEach(el=>observer.observe(el));
    return () => {observer.disconnect();clearTimeout(timer);mm.revert();};
  },[]);
}

export function Words({lines}:{lines:string[]}) {
  return <>{lines.map((line,i)=><span className="motion-line" key={line}>{i>0&&<span className="sr-only"> </span>}{line.split(" ").map((word,j)=><span key={j}>{j>0?" ":""}<span className="motion-word">{word}</span></span>)}</span>)}</>;
}

export function useSelectionMotion(menu:boolean, mega:boolean, service:number) {
  useLayoutEffect(()=>{
    const mm = gsap.matchMedia();
    mm.add("(prefers-reduced-motion: no-preference)",()=>{
      const panel = document.querySelector(mega?".mega-menu":".nav-links.is-open");
      if(panel && (mega||menu)) gsap.from(panel,{y:8,opacity:0,duration:.22,ease});
    });return ()=>mm.revert();
  },[menu,mega]);
  useLayoutEffect(()=>{
    const mm=gsap.matchMedia();mm.add("(prefers-reduced-motion: no-preference)",()=>{
      gsap.from(".service-visual > img",{opacity:.25,scale:.98,duration:.45,ease});
    });return ()=>mm.revert();
  },[service]);
}

export function arrowFeedback(el:HTMLElement,active:boolean) {
  const arrow=el.querySelector(".icon");
  if(arrow) gsap.to(arrow,{x:active&&!reduced()?3:0,duration:reduced()?0:.18,ease,overwrite:true});
}

