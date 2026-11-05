"use client";

import {useLayoutEffect,useRef,useState,type KeyboardEvent} from "react";
import Image from "next/image";
import {FileText,Warehouse,FileSearch,Ruler,CirclePlus,ClipboardList,Package,Ship,MapPin,UserRound,Truck,ArrowUpRight} from "lucide-react";
import gsap from "gsap";
import {ScrollTrigger} from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);

const steps=[
 {title:"说明需求",summary:"商品、运输方式、货量、目的地和 IOR 需求。",image:"shipping-brief",alt:"货运需求表、地球仪和运输纸箱示意图。",Icon:FileText,label:"您的需求",heading:"从已知信息开始。",detail:"提供已有的货运信息，未决定的项目可填写“未定”。",items:[
  {title:"商品与货量",copy:"说明商品和预计数量，并注明单位。",Icon:Package},
  {title:"运输方式",copy:"整柜、拼箱、空运或未定。",Icon:Ship},
  {title:"目的地",copy:"说明货物需要送达的地点。",Icon:MapPin},
  {title:"IOR 需求",copy:"说明是否需要 IOR 支持，或目前尚不确定。",Icon:UserRound}]},
 {title:"确认条件",summary:"接收条件、单证、作业、配送和责任划分。",image:"requirements-review",alt:"仓库和叉车旁的需求清单文件夹与记录板示意图。",Icon:Warehouse,label:"条件确认",heading:"确认范围与交接安排。",detail:"确认货物接收条件和各方责任。",items:[
  {title:"接收条件与单证",copy:"确认货物范围及所需信息。",Icon:FileText},
  {title:"仓库作业",copy:"确认收货、存储、拣货和包装需求。",Icon:Warehouse},
  {title:"配送要求",copy:"确认目的地与收货条件。",Icon:Truck},
  {title:"责任划分",copy:"明确各环节及交接的负责方。",Icon:UserRound}]},
 {title:"确认报价",summary:"计费单位、包含项目、附加费用和执行条件。",image:"quotation",alt:"青蓝色文件夹上展开的报价文件与笔示意图。",Icon:FileSearch,label:"报价确认",heading:"了解报价包含哪些内容。",detail:"在安排后续工作前确认以下项目。",items:[
  {title:"计费单位",copy:"确认费用计算方式和所用单位。",Icon:Ruler},
  {title:"包含服务",copy:"确认包含哪些服务、文件和作业。",Icon:FileText},
  {title:"附加费用",copy:"可能产生的额外费用及适用条件。",Icon:CirclePlus},
  {title:"服务条款",copy:"服务条款、责任及确认后的安排。",Icon:ClipboardList}]}
];

export default function ConsultationProcess(){
 const root=useRef<HTMLElement>(null);
 const [selected,setSelected]=useState(0);
 useLayoutEffect(()=>{
  const media=window.matchMedia("(max-width:767px)");
  const tabs=root.current!.querySelector("[role=tablist]")!;
  const orient=()=>tabs.setAttribute("aria-orientation","horizontal");
  orient();media.addEventListener("change",orient);
  return()=>media.removeEventListener("change",orient);
 },[]);
 useLayoutEffect(()=>{
  const mm=gsap.matchMedia();
  mm.add("(prefers-reduced-motion:no-preference)",()=>{
   const q=(selector:string)=>root.current!.querySelectorAll(selector);
   gsap.timeline({scrollTrigger:{trigger:root.current,start:"top 85%",once:true},defaults:{ease:"power2.out"}})
    .from(q(".consultation-heading"),{opacity:0,y:14,duration:.45})
    .from(q(".consultation-art"),{opacity:0,y:12,duration:.45,stagger:.07},.12)
    .from(q(".consultation-route"),{scaleX:0,duration:.6},.2);
  },root);
  return()=>mm.revert();
 },[]);
 useLayoutEffect(()=>{
  const mm=gsap.matchMedia();
  mm.add("(prefers-reduced-motion:no-preference)",()=>{
   gsap.fromTo(root.current!.querySelector(".consultation-panel-content"),{opacity:0,y:4},{opacity:1,y:0,duration:.2,ease:"power1.out"});
  },root);
  ScrollTrigger.refresh();
  return()=>mm.revert();
 },[selected]);
 function onKeys(event:KeyboardEvent<HTMLButtonElement>,index:number){
  if(!["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(event.key))return;
  event.preventDefault();
  const next=event.key==="Home"?0:event.key==="End"?2:(index+(event.key==="ArrowLeft"||event.key==="ArrowUp"?2:1))%3;
  setSelected(next);document.getElementById(`consultation-step-${next}`)?.focus();
 }
 const current=steps[selected];
 return <section id="process" ref={root} className="consultation-process" aria-labelledby="consultation-title"><div className="container">
  <header className="consultation-heading"><h2 id="consultation-title">从需求说明到报价确认。</h2><p>明确所需服务后，说明需求、确认条件，再共同确认报价。</p></header>
  <div className="consultation-tabs" role="tablist" aria-label="查看咨询步骤"><span className="consultation-route" aria-hidden="true"/>{steps.map(({title,summary,image,alt,Icon},i)=><button type="button" role="tab" id={`consultation-step-${i}`} key={title} aria-label={`0${i+1} ${title}`} aria-selected={selected===i} aria-controls="consultation-step-panel" tabIndex={selected===i?0:-1} onClick={()=>setSelected(i)} onKeyDown={e=>onKeys(e,i)}>
   <span className="consultation-art"><Image src={`/assets/process/${image}-art.webp`} width={i===2?558:557} height={i===2?254:258} sizes="(max-width:767px) 34vw, (max-width:1023px) 30vw, 440px" alt={alt}/></span>
   <span className="consultation-stop" aria-hidden="true"/>
   <span className="consultation-step-summary"><Icon aria-hidden="true"/><span><span className="consultation-number">0{i+1}</span><strong>{title}</strong><span className="consultation-summary">{summary}</span></span></span>
  </button>)}</div>
  <div role="tabpanel" id="consultation-step-panel" aria-labelledby={`consultation-step-${selected}`} tabIndex={0} className="consultation-panel"><div className="consultation-panel-content">
   <div className="consultation-panel-intro"><p className="eyebrow">0{selected+1} / {current.label}</p><h3>{current.heading}</h3><p>{current.detail}</p></div>
   <ul>{current.items.map(({title,copy,Icon})=><li key={title}><Icon aria-hidden="true"/><div><h4>{title}</h4><p>{copy}</p></div></li>)}</ul>
  </div></div>
  <footer className="consultation-footer"><p>尚未决定？未知的货运信息可填写“未定”。</p><div><p>选择步骤，查看详情。</p><a href="#quote" className="button">说明您的需求 <ArrowUpRight aria-hidden="true"/></a></div></footer>
 </div></section>;
}
