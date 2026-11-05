"use client";

import { useLayoutEffect, useRef, useState, type KeyboardEvent } from "react";
import Image from "next/image";
import ImportAlternative from "./import-alternative";
import SystemConnections from "./system-connections";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { RevealPanel, Words } from "./motion";

gsap.registerPlugin(ScrollTrigger);
const assets = "/assets/service-details/";
function DetailIcon({name}:{name:string}) {
  return <img className="detail-icon" src={`${assets}${name}.svg`} alt="" width="32" height="32" aria-hidden="true"/>;
}
function DetailLink({children}:{children:React.ReactNode}) {
  return <a href="#quote" className="text-link">{children}<DetailIcon name="arrow"/></a>;
}
function tabKey(e:KeyboardEvent<HTMLButtonElement>,index:number,count:number,select:(value:number)=>void,prefix:string) {
  if (!["ArrowLeft","ArrowRight","Home","End"].includes(e.key)) return;
  e.preventDefault();
  const next=e.key==="Home"?0:e.key==="End"?count-1:(index+(e.key==="ArrowRight"?1:count-1))%count;
  select(next);document.getElementById(`${prefix}-${next}`)?.focus();
}
const freightModes = [
  {name:"FCL",caption:"整柜装载您的货物",icon:"container",tag:"整柜货量",copy:"根据货量、装柜计划和美国收货时段安排整柜运输。",checks:["柜型、装载方式和毛重","起运地提货、港口交接和交付条款","美国短驳、卸货要求和收货预约"]},
  {name:"LCL",caption:"共享舱位，灵活出货",icon:"shared",tag:"小批量海运",copy:"货量不足整柜时可考虑拼箱海运，并确认集货与拆箱环节的交接。",checks:["纸箱或托盘的尺寸、体积及可堆叠性","集货与拆箱地点","起运地和目的地操作费用"]},
  {name:"空运",caption:"围绕交付时限规划",icon:"plane",tag:"时效敏感货物",copy:"对于时效敏感或高货值货物，可结合产品情况和末端配送要求讨论空运方案。",checks:["备货日期、交付时限和路线选项","报价所需的实际重量和体积重量","电池、受限货物和所需文件"]}
];
const comparison = [
  ["适用情况","常规大批量补货","小批量或混合货物","紧急或高货值货物"],
  ["运力规划","柜型与装载计划","体积与拼箱安排","重量与尺寸"],
  ["主要交接","港口 → 短驳 → 仓库","集货 → 美国操作","机场 → 美国配送"],
  ["报价所需信息","柜型、重量、路线","体积、包装、当地费用","计费重量、货物类型"]
];
const freightArtwork = [
  { id: "fcl", label: "整柜运输", width: 1536 },
  { id: "lcl", label: "拼箱运输", width: 1536 },
  { id: "air", label: "空运", width: 1536 },
];

function FreightJourney({children,active,onSelect}:{children:React.ReactNode;active:number;onSelect:(index:number)=>void}) {
  const track = useRef<HTMLDivElement>(null);
  const frame = useRef<HTMLDivElement>(null);
  const stack = useRef<HTMLDivElement>(null);
  const trigger = useRef<ScrollTrigger | null>(null);
  const animation = useRef<gsap.core.Timeline | null>(null);
  const shown = useRef(0);
  const busyUntil = useRef(0);
  const scrollInputUntil = useRef(0);
  const activeRef = useRef(active);
  activeRef.current = active;
  const last = freightArtwork.length - 1;

  function select(index: number) {
    scrollInputUntil.current = 0;
    const t = trigger.current;
    if (t) window.scrollTo({ top: t.start + (t.end - t.start) * index / last, behavior: "instant" });
    onSelect(index);
  }

  useLayoutEffect(() => {
    const scenes = Array.from(stack.current!.querySelectorAll<HTMLElement>(".freight-scene"));
    animation.current?.kill();
    const incoming = scenes[active];
    gsap.to(track.current!.querySelector(".freight-progress"), {
      "--flow":(active * 50) + "%",
      duration:matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : .8,
      ease:"power2.inOut", overwrite:true,
    });
    if (matchMedia("(prefers-reduced-motion: reduce)").matches || shown.current === active) {
      scenes.forEach((scene, i) => {
        gsap.set(scene, {visibility:i===active ? "visible" : "hidden"});
        gsap.set(scene.querySelectorAll(".freight-facts, .freight-card"), {opacity:i===active ? 1 : 0, y:0});
      });
    } else {
      busyUntil.current = performance.now() + 1000;
      const outgoing = scenes.filter(scene => scene !== incoming);
      const tl = gsap.timeline();
      outgoing.forEach(scene => {
        tl.to(scene.querySelector(".freight-facts"), {opacity:0, y:-12, duration:.28, ease:"power2.in"}, 0);
        tl.to(scene.querySelector(".freight-card"), {opacity:0, y:-16, duration:.36, ease:"power2.inOut"}, 0);
        tl.set(scene, {visibility:"hidden"}, .36);
      });
      tl.set(incoming, {visibility:"visible"}, .22)
        .fromTo(incoming.querySelector(".freight-facts"), {opacity:0,y:18}, {opacity:1,y:0,duration:.48,ease:"power3.out"}, .22)
        .fromTo(incoming.querySelector(".freight-card"), {opacity:0,y:26}, {opacity:1,y:0,duration:.64,ease:"power3.out"}, .36);
      animation.current = tl;
    }
    shown.current = active;
  }, [active]);

  useLayoutEffect(() => () => { animation.current?.kill(); }, []);

  useLayoutEffect(() => {
    const el = track.current!, screen = frame.current!, slides = stack.current!;
    const comparisonPanel = screen.querySelector("details")!;
    const header = document.querySelector<HTMLElement>(".site-header");
    const reduce = matchMedia("(prefers-reduced-motion: reduce)");
    let pending = 0, quietUntil = 0;
    function scrollInput(event: Event) {
      if (event instanceof KeyboardEvent && !["PageDown","PageUp","ArrowDown","ArrowUp","Home","End"," "].includes(event.key)) return;
      if (event instanceof PointerEvent && event.pointerType !== "touch" && event.clientX < document.documentElement.clientWidth) return;
      scrollInputUntil.current = performance.now() + 1500;
    }
    const sync = (t: ScrollTrigger) => {
      if (performance.now() > scrollInputUntil.current || comparisonPanel.contains(document.activeElement)) return;
      onSelect(Math.round(t.progress * last));
    };
    function measure() {
      const head = Math.ceil(header?.getBoundingClientRect().height ?? 0);
      const room = window.innerHeight - head;
      const fits = slides.offsetHeight + 32 <= room;
      el.style.setProperty("--freight-room", room + "px");
      const enabled = fits && !reduce.matches && !comparisonPanel.open;
      el.dataset.pinned = String(enabled);
      // If the full composition won't fit, let the heading scroll away first.
      el.style.setProperty("--freight-top", Math.min(head, innerHeight - screen.offsetHeight) + "px");
      if (enabled && !trigger.current) {
        trigger.current = ScrollTrigger.create({
          trigger: el, start: () => "top " + el.style.getPropertyValue("--freight-top"),
          end: () => "+=" + (el.offsetHeight - screen.offsetHeight),
          onUpdate: sync,
        });
      } else if (!enabled && trigger.current) {
        trigger.current.kill();
        trigger.current = null;
      }
      ScrollTrigger.refresh();
    }
    function schedule() {
      cancelAnimationFrame(pending);
      pending = requestAnimationFrame(measure);
    }
    // Treat a wheel gesture and its inertia as one choice. Touch, scrollbar
    // dragging and keyboard page scrolling use the native scroll range.
    function wheel(event: WheelEvent) {
      scrollInput(event);
      const t = trigger.current;
      if (!t || !event.cancelable || event.ctrlKey || event.metaKey || !event.deltaY ||
          Math.abs(event.deltaX) > Math.abs(event.deltaY) ||
          (event.target instanceof Element && event.target.closest(".site-header, dialog, .freight-compare[open]"))) return;
      const y = window.scrollY, sign = Math.sign(event.deltaY);
      const dy = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? innerHeight : 1);
      let target: number;
      if (y < t.start - 1) {
        if (y + dy < t.start) return;
        target = 0;
      } else if (y > t.end + 1) {
        if (y + dy > t.end) return;
        target = last;
      } else {
        const now = performance.now();
        if (now < quietUntil || now < busyUntil.current) {
          quietUntil = now + 115;
          event.preventDefault();
          return;
        }
        const index = Math.round(Math.max(0, Math.min(1, (y - t.start) / (t.end - t.start))) * last);
        target = index + sign;
        if (target < 0 || target > last) return;
      }
      event.preventDefault();
      quietUntil = performance.now() + 115;
      window.scrollTo({ top:t.start + (t.end - t.start) * target / last, behavior:"instant" });
      onSelect(target);
    }
    function toggleComparison(event: MouseEvent) {
      const summary = comparisonPanel.querySelector("summary")!;
      if (!(event.target instanceof Node) || !summary.contains(event.target)) return;
      event.preventDefault();
      const top = summary.getBoundingClientRect().top;
      const selected = activeRef.current;
      comparisonPanel.open = !comparisonPanel.open;
      measure();
      const t = trigger.current;
      const target = t && !comparisonPanel.open
        ? t.start + (t.end - t.start) * selected / last
        : window.scrollY + summary.getBoundingClientRect().top - top;
      window.scrollTo({top:target,behavior:"instant"});
      onSelect(selected);
    }
    measure();
    comparisonPanel.addEventListener("click", toggleComparison);
    const observer = new ResizeObserver(schedule);
    observer.observe(screen);
    comparisonPanel.addEventListener("toggle", schedule);
    if (header) observer.observe(header);
    window.addEventListener("resize", schedule);
    reduce.addEventListener("change", schedule);
    window.addEventListener("wheel", wheel, { passive:false });
    window.addEventListener("keydown", scrollInput);
    window.addEventListener("touchmove", scrollInput, {passive:true});
    window.addEventListener("pointerdown", scrollInput);
    return () => {
      cancelAnimationFrame(pending);
      observer.disconnect();
      comparisonPanel.removeEventListener("toggle", schedule);
      comparisonPanel.removeEventListener("click", toggleComparison);
      window.removeEventListener("resize", schedule);
      reduce.removeEventListener("change", schedule);
      window.removeEventListener("wheel", wheel);
      window.removeEventListener("keydown", scrollInput);
      window.removeEventListener("touchmove", scrollInput);
      window.removeEventListener("pointerdown", scrollInput);
      trigger.current?.kill();
      trigger.current = null;
      delete el.dataset.pinned;
    };
  }, [last,onSelect]);

  return <div className="freight-journey" ref={track}>
    <div className="freight-frame" ref={frame}><div>{children}<div className="freight-stack" ref={stack}>
      <div className="freight-picker" aria-label="选择运输方式" role="group">
        {freightModes.map((mode,i)=><button type="button" key={mode.name} aria-pressed={active===i}
          aria-controls={`freight-scene-${freightArtwork[i].id}`} onClick={()=>select(i)}>{mode.name}</button>)}
      </div>
      <div className="freight-slides">
        <div className="freight-progress" aria-hidden="true"><i/><b/><span>滚动查看</span></div>
        {freightArtwork.map(({ id, label, width }, i) => {
          const mode = freightModes[i];
          return <article className="freight-scene" id={`freight-scene-${id}`} key={id}
            data-active={active===i} inert={active!==i} aria-hidden={active!==i} aria-labelledby={`freight-label-${id}`}>
            <div className="freight-facts">
              <span className="detail-kicker">0{i+1} / {i<2 ? "海运" : "航空运输"}</span>
              <h3 id={`freight-label-${id}`}>{label}{i<2 && <small> ({mode.name})</small>}</h3>
              <p>{mode.copy}</p>
            </div>
            <div className="freight-card"><figure className="freight-object">
              <div className="freight-render"><Image src={`${assets}freight/${id}-hd.webp`} width={width} height={1024}
                quality={90}
                sizes="(max-width: 700px) 85vw, (max-width: 1200px) 42vw, 480px"
                alt={["封闭的蓝色集装箱示意图","装有纸箱和托盘的拼箱集装箱示意图","货物装入货运飞机的示意图"][i]}/>
                {i<2 && <svg viewBox="0 0 600 400" aria-hidden="true" focusable="false">
                  <g transform={i===0 ? "matrix(1 .065 0 1 333 160)" : "matrix(.52 .095 0 1 465 164)"}>
                    <rect width="128" height="24" rx="1" fill="#fff" opacity=".95"/>
                    <image href="/assets/logo.webp" x="4" y="-4" width="120" height="32"/>
                  </g>
                </svg>}
              </div>
              <figcaption><DetailIcon name={mode.icon}/>{mode.caption}</figcaption>
            </figure>
            <dl>{comparison.map(([field,...values]) => <div key={field}><dt>{field}</dt><dd>{values[i]}</dd></div>)}</dl></div>
          </article>;
        })}
      </div>
    </div></div></div>
  </div>;
}
const outboundFlows = [
  {name:"一件代发",title:"每笔订单，为客户准备就绪。",copy:"为单个客户订单确认拣货、包装和出库规则。",steps:["接收订单","拣货核对","包装贴标","包裹交接"],input:"SKU 对应关系、订单格式和包装规则",output:"包裹编号、出库状态和异常记录"},
  {name:"FBA 中转补货",title:"为库存的下一站做好准备。",copy:"围绕 Amazon 目的仓规划临时存储、贴标和分批补货。",steps:["货件计划","预处理与贴标","纸箱／托盘","预约送仓"],input:"货件计划、SKU 标签及纸箱或托盘要求",output:"货件编号、配送计划和交接记录"}
];

export default function ServiceDetails() {
  const root=useRef<HTMLDivElement>(null);
  const [freight,setFreight]=useState(0),[flow,setFlow]=useState(0),[returns,setReturns]=useState(false);

  useLayoutEffect(()=>{
    const mm=gsap.matchMedia();
    mm.add("(prefers-reduced-motion: no-preference)",()=>{
      root.current!.querySelectorAll<HTMLElement>(".detail-enter").forEach(el=>{
        gsap.from(el,{y:26,opacity:0,duration:.6,ease:"power2.out",scrollTrigger:{trigger:el,start:"top 92%",once:true}});
      });
    },root);
    return ()=>mm.revert();
  },[]);
  useLayoutEffect(()=>{
    const mm=gsap.matchMedia();
    mm.add("(prefers-reduced-motion: no-preference)",()=>{
      gsap.fromTo(".freight-matrix [data-selected=true]",{backgroundColor:"#ffffff"},{backgroundColor:"#e8f7fc",duration:.3,ease:"power2.out"});
      gsap.fromTo(".freight-choice-content",{opacity:.25,y:8},{opacity:1,y:0,duration:.3,ease:"power2.out"});
    },root);return ()=>mm.revert();
  },[freight]);
  useLayoutEffect(()=>{
    const mm=gsap.matchMedia();
    mm.add("(prefers-reduced-motion: no-preference)",()=>{
      gsap.fromTo(".outbound-step",{opacity:.2,y:10},{opacity:1,y:0,duration:.35,stagger:.08,ease:"power2.out",scrollTrigger:{trigger:".outbound-route",start:"top 93%",once:true}});
      gsap.fromTo(".outbound-track",{scaleX:0},{scaleX:1,duration:.7,ease:"power2.inOut",scrollTrigger:{trigger:".outbound-route",start:"top 93%",once:true}});
    },root);return ()=>mm.revert();
  },[flow]);


  const selected=freightModes[freight],outbound=outboundFlows[flow];
  return <div ref={root} className="service-details"><div className="container detail-navigation"><a href="#customers" className="text-link">选择您的业务类型</a></div>
    <section id="freight-options" className="detail-section freight-detail" aria-labelledby="freight-title">
      <div className="container">
        <FreightJourney active={freight} onSelect={setFreight}>
        <div className="detail-heading"><div><p className="eyebrow">运输方式选择</p><h2 id="freight-title"><Words lines={["从货物需求出发，", "选择合适的运输方案。"]}/></h2></div><p>比较从中国出货的三种方式，再确认影响报价的路线、操作和交接安排。</p></div>
        <details className="freight-compare"><summary>对比三种运输方式</summary>
        <p className="matrix-instruction">选择运输方式，查看需要准备的信息。<span>先比较服务范围，再规划路线。</span></p>
        <div className="freight-table-scroll" tabIndex={0} role="region" aria-label="运输方式对比表，小屏幕可横向滚动。">
          <table className="freight-matrix"><caption className="sr-only">整柜、拼箱与空运对比</caption><thead><tr><td>您的货物</td>{freightModes.map((mode,i)=><th scope="col" key={mode.name} data-selected={freight===i}><button type="button" aria-pressed={freight===i} aria-controls="freight-preparation" onClick={()=>setFreight(i)}><DetailIcon name={mode.icon}/><strong>{mode.name}</strong><span>{mode.caption}</span></button></th>)}</tr></thead><tbody>{comparison.map(row=><tr key={row[0]}><th scope="row">{row[0]}</th>{row.slice(1).map((cell,i)=><td data-selected={freight===i} key={cell}>{cell}</td>)}</tr>)}</tbody></table>
        </div>
        <div id="freight-preparation" className="freight-preparation" aria-live="polite"><div className="freight-choice-content"><span className="detail-kicker">{selected.name} / {selected.tag}</span><h3>准备以下货物信息。</h3><p>{selected.copy}</p><DetailLink>咨询运输方案</DetailLink></div><ul className="freight-choice-content">{selected.checks.map(item=><li key={item}><DetailIcon name="check"/>{item}</li>)}</ul></div>
        </details>
        </FreightJourney>
        <div className="freight-story-end"><p className="detail-footnote">路线、运力、运输时间和费用需根据您的货物另行确认。</p><DetailLink>咨询运输路线</DetailLink></div>
      </div>
    </section>

    <section id="fulfillment-options" className="detail-section fulfillment-detail" aria-labelledby="fulfillment-title"><div className="container">
      <div className="detail-heading"><div><p className="eyebrow">订单履约与出库方式</p><h2 id="fulfillment-title"><Words lines={["不同的目的地，","不同的作业流程。"]}/></h2></div><p>直达消费者的包裹、平台补货、退货和 B2B 配送各有不同的准备要求。</p></div>
      <div className="fulfillment-bento">
        <article className="outbound-workspace detail-enter"><div className="detail-tabs" role="tablist" aria-label="出库作业流程">{outboundFlows.map((item,i)=><button type="button" role="tab" id={`flow-tab-${i}`} aria-selected={flow===i} aria-controls="outbound-panel" tabIndex={flow===i?0:-1} key={item.name} onKeyDown={e=>tabKey(e,i,2,setFlow,"flow-tab")} onClick={()=>setFlow(i)}>{item.name}</button>)}</div>
          <div role="tabpanel" id="outbound-panel" aria-labelledby={`flow-tab-${flow}`}><h3>{outbound.title}</h3><p>{outbound.copy}</p><Image className="fulfillment-art" src={`${assets}fulfillment-workbench.webp`} width={1200} height={600} sizes="(max-width:767px) 100vw, 880px" alt="微缩仓库货架、包装工作台和待出库托盘示意图。"/>
          <div className="outbound-route"><span className="outbound-track" aria-hidden="true"/><ol>{outbound.steps.map((name,i)=><li className="outbound-step" key={name}><span>{i+1}</span><strong>{name}</strong></li>)}</ol></div><div className="outbound-handover"><div><small>需要准备</small><p>{outbound.input}</p></div><div><small>需要记录</small><p>{outbound.output}</p></div></div></div>
        </article>
        <article className="b2b-workspace detail-enter"><DetailIcon name="pallet"/><p className="detail-kicker">B2B 配送</p><h3>收货月台<br/>有各自的要求。</h3><p>根据批发或零售客户的收货要求安排配送。</p><ul><li>采购订单及纸箱／托盘要求</li><li>送货预约和收货时间</li><li>标签、卸货条件和签收凭证</li></ul><DetailLink>咨询 B2B 配送</DetailLink></article>
        <article className="returns-workspace detail-enter"><div><DetailIcon name="returns"/><div><p className="detail-kicker">退货与库存恢复</p><h3>为每件退货明确后续处理。</h3></div></div><p>在退货到仓前确认检验、重新贴标及批准重新入库的方式。</p><div className="return-path"><span>接收</span><span>检验</span><span>批准处理方案</span><span>重新入库或隔离</span></div><button className="text-link" aria-expanded={returns} aria-controls="returns-details" type="button" onClick={()=>setReturns(!returns)}>{returns?"收起退货处理说明":"查看退货处理说明"}<span aria-hidden="true">{returns?"−":"+"}</span></button><RevealPanel open={returns} id="returns-details" duration={.3}><div className="returns-details"><p>记录退货编号、SKU、数量和外观状况，确认照片记录、包装检查及产品专项检验范围。</p><p>确认是否需要重新贴标。仅在符合约定标准且处理方案获批后重新入库；损坏、缺件或待处理商品应单独存放。</p></div></RevealPanel></article>
      </div><p className="detail-footnote">业务启动前需确认备货规则、退货检验范围和 B2B 作业要求；平台要求以您的货件计划为准。</p>
    </div></section>

    <ImportAlternative/>

    <SystemConnections/>
  </div>;
}
