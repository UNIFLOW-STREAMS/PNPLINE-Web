"use client";

import {useLayoutEffect,useRef,useState} from "react";
import Image from "next/image";
import {Store,Layers,Braces,Warehouse,FileDown,Package} from "lucide-react";
import gsap from "gsap";


const inputs=[
 {name:"销售平台",Icon:Store,description:"说明平台、店铺地区及 SKU 对应要求。"},
 {name:"您的 ERP",Icon:Layers,description:"说明 ERP、订单字段及库存数据的权威来源。"},
 {name:"API 需求",Icon:Braces,description:"提供 API 文档、身份验证及字段映射需求。"}
];
const outputs=[
 {name:"库存查询",Icon:Warehouse,description:"您需要查看的库存信息"},
 {name:"入库记录",Icon:FileDown,description:"需要查看的入库信息"},
 {name:"订单与出库",Icon:Package,description:"备货与出库进度"}
];
const incoming=["M135 65H185Q198 65 210 78L225 87H375Q390 87 400 100L430 125","M135 185H195Q210 185 220 193H423","M135 305H205L225 300H390L468 225"];
const outgoing=["M906 116L975 65H1005","M936 179H1005","M924 213L1000 305H1005"];

export default function SystemConnections(){
 const root=useRef<HTMLElement>(null);
 const [selected,setSelected]=useState<string|null>(null);
 useLayoutEffect(()=>{
  const mm=gsap.matchMedia();
  mm.add("(prefers-reduced-motion:no-preference)",()=>{
   root.current!.querySelectorAll<SVGPathElement>("[data-system-route]").forEach(path=>{
    const active=selected===path.dataset.systemRoute;
    gsap.to(path,{opacity:selected?(active?1:.32):1,strokeWidth:active?3:1.25,duration:.3,ease:"power2.out",overwrite:"auto"});
   });
  },root);
  return()=>mm.revert();
 },[selected]);
 function choose(id:string){setSelected(previous=>previous===id?null:id);}
 function path(d:string,id:string,dashed=false){return <path key={id} d={d} data-system-route={id} data-active={selected===id} className={dashed?"system-route-dashed":""} vectorEffect="non-scaling-stroke"/>;}
 return <section id="system-connections" ref={root} className="systems-concept" aria-labelledby="systems-title" data-has-selection={!!selected}>
  <div className="container">
   <header className="systems-concept-heading"><p className="eyebrow">服务详情／系统连接</p><h2 id="systems-title">规划您的系统连接。</h2><p>说明平台、ERP 或 API 需求，确认支持的连接方式和所需仓库记录。</p></header>
   <div className="systems-map" aria-label="系统需求与仓库记录">
    <svg className="systems-map-lines" viewBox="0 0 1320 400" preserveAspectRatio="none" aria-hidden="true">
     {incoming.map((d,i)=>path(d,`in-${i}`,true))}{outgoing.map((d,i)=>path(d,`out-${i}`))}
     {[[135,65],[135,185],[135,305],[1005,65],[1005,185],[1005,305]].map(([cx,cy],i)=><circle key={i} cx={cx} cy={cy} r="4"/>)}
    </svg>
    <div className="systems-inputs" role="group" aria-label="连接需求">{inputs.map(({name,Icon,description},i)=><button type="button" key={name} aria-label={name} title={description} aria-pressed={selected===`in-${i}`} onClick={()=>choose(`in-${i}`)}><Icon aria-hidden="true"/><strong>{name}</strong><span className="systems-input-hint">待确认需求</span></button>)}</div>
    <div className="systems-mobile-in" aria-hidden="true"><svg viewBox="0 0 320 48" preserveAspectRatio="none">{[52,160,268].map((x,i)=>path(`M${x} 0V15L160 40V48`,`in-${i}`,true))}</svg></div>
    <div className="systems-warehouse"><Image src="/assets/systems/warehouse-cutaway.webp" width={620} height={420} sizes="(max-width:767px) 100vw, (max-width:1023px) 85vw, 570px" alt="包含库存货架、收货月台和出库货车的仓库剖面示意图。"/></div>
    <div className="systems-mobile-out" aria-hidden="true"><svg viewBox="0 0 320 48" preserveAspectRatio="none">{[52,160,268].map((x,i)=>path(`M160 0V8L${x} 33V48`,`out-${i}`))}</svg></div>
    <div className="systems-outputs" role="group" aria-label="仓库信息">{outputs.map(({name,Icon,description},i)=><button type="button" key={name} aria-pressed={selected===`out-${i}`} onClick={()=>choose(`out-${i}`)}><Icon aria-hidden="true"/><span><strong>{name}</strong><span>{description}</span></span></button>)}</div>
   </div>
   <p className="sr-only" aria-live="polite">{selected?selected.startsWith("in")?inputs[Number(selected.slice(-1))].description:`${outputs[Number(selected.slice(-1))].name}: ${outputs[Number(selected.slice(-1))].description}.`:"选择需求或记录以突出显示其连接。集成范围需根据您的业务另行确认。"}</p>
  </div>
  
 </section>;
}
