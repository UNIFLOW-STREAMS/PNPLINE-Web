"use client";
import {useLayoutEffect,useRef,useState,type KeyboardEvent} from "react";
import Image from "next/image";
import gsap from "gsap";
import {ScrollTrigger} from "gsap/ScrollTrigger";
import {RevealPanel} from "./motion";
gsap.registerPlugin(ScrollTrigger);
const base="/assets/import-planning/";
const phases=[
 {title:"说明商品情况",summary:"从货物和交易信息开始。",heading:"完整信息，让准备更充分。",copy:"说明货物是什么、来自哪里、发给谁。先提供已知信息，再共同梳理需要确认的问题。",inputs:["产品描述、材质和预期用途","原产国和交易信息","美国目的地和已指定的参与方"],label:"商品与交易",icon:"ior"},
 {title:"单证、HS 与产品要求",summary:"将货物信息与所需单证对应。",heading:"准备货运所需文件。",copy:"与您指定的报关行核对商品信息和货运单证，在订舱前确认归类及产品专项要求。",inputs:["商业发票和装箱信息","运输单证和货件编号","商品归类和产品专项问题"],label:"单证与要求",icon:"document"},
 {title:"明确责任分工",summary:"确认由谁提供、审核和交接。",heading:"明确责任，才能清晰交接。",copy:"明确登记进口商、报关行及税费支付方，在发货前确认范围、联系人和异常处理方式。",inputs:["登记进口商与指定报关行","文件负责方、税费支付方和联系人","放行、收货和异常交接"],label:"参与方与交接",icon:"review"}
];
const questions=[
 {name:"申报单证",icon:"document",heading:"让货运信息保持一致。",copy:"确保发票、装箱明细和运输信息与实际货物一致，并与指定报关行确认进口申报文件。",fields:["商业发票","装箱信息","运输单证"]},
 {name:"HS / US HTS",icon:"classification",heading:"从产品本身开始。",copy:"提供材质、预期用途、规格和原产地，以便与指定报关行确认商品归类。",fields:["材质与成分","预期用途","规格与原产地"]},
 {name:"FDA / FCC",icon:"review",heading:"尽早确认产品专项要求。",copy:"说明产品及其预期用途，确认是否适用 FDA 要求或 FCC 设备授权，以及需要哪些证明资料。",fields:["产品类别","预期用途","相关技术证明资料"]}
];
const roles=[
 ["卖家／制造商","产品、货值和原产地信息"],
 ["登记进口商（IOR）","进口申报责任和税费安排"],
 ["指定报关行","申报审核和约定的申报范围"],
 ["PNPLINE／收货团队","约定的物流范围与仓库交接"]
];
function Icon({name}:{name:string}){return <img src={`${base}${name}.svg`} alt="" aria-hidden="true" width="104" height="104" className="brief-icon"/>;}
export default function ImportAlternative(){
 const progress=useRef(1/3);
 const root=useRef<HTMLElement>(null),[phase,setPhase]=useState(0),[question,setQuestion]=useState(0),[ior,setIor]=useState(false);
 useLayoutEffect(()=>{const mm=gsap.matchMedia();mm.add("(prefers-reduced-motion:no-preference)",()=>{
  const q=(s:string)=>root.current!.querySelectorAll(s);
  gsap.timeline({scrollTrigger:{trigger:root.current,start:"top 82%",once:true},defaults:{ease:"power2.out"}})
   .from(q(".brief-title-line"),{y:20,opacity:0,duration:.55,stagger:.06},0)
   .from(q(".brief-phase"),{y:14,opacity:0,duration:.4,stagger:.08},.15)
   .from(q(".brief-workspace"),{y:18,opacity:0,duration:.55},.3);
 },root);return()=>mm.revert();},[]);
 useLayoutEffect(()=>{const mm=gsap.matchMedia();mm.add("(prefers-reduced-motion:no-preference)",()=>{
  gsap.fromTo(root.current!.querySelectorAll(".brief-phase-copy,.brief-visual-content"),{opacity:.15,y:8},{opacity:1,y:0,duration:.3,ease:"power2.out"});
  const bar=root.current!.querySelector(".brief-progress-fill");
  gsap.fromTo(bar,{scaleX:progress.current},{scaleX:(phase+1)/3,duration:.45,ease:"power2.inOut",onUpdate:()=>{progress.current=Number(gsap.getProperty(bar,"scaleX"));}});
 },root);
  ScrollTrigger.refresh();
  return()=>mm.revert();},[phase]);
 useLayoutEffect(()=>{const mm=gsap.matchMedia();mm.add("(prefers-reduced-motion:no-preference)",()=>{
  const content=root.current!.querySelector(".brief-question-content");
  if(content) gsap.fromTo(content,{opacity:.2,y:5},{opacity:1,y:0,duration:.3,ease:"power2.out"});
 },root);return()=>mm.revert();},[question,phase]);
 function keys(e:KeyboardEvent<HTMLButtonElement>,i:number){if(!["ArrowLeft","ArrowRight","Home","End"].includes(e.key))return;e.preventDefault();const n=e.key==="Home"?0:e.key==="End"?2:(i+(e.key==="ArrowLeft"?2:1))%3;setPhase(n);document.getElementById(`brief-tab-${n}`)?.focus();}
 const current=phases[phase],q=questions[question];
 return <section id="import-planning" className="import-alternative" ref={root} aria-labelledby="brief-heading"><div className="container">
  <div className="brief-heading"><div><p className="eyebrow">发货前的准备</p><h2 id="brief-heading"><span className="brief-title-line">先确认进口要求，</span><span className="brief-title-line">再安排发货。</span></h2></div><div><p>从商品和交易信息开始，在确认支持范围前梳理 IOR 需求、单证和责任。</p><span className="brief-route-label">中国 <span aria-hidden="true">→</span> 美国</span></div></div>
  <div className="brief-phases" role="tablist" aria-label="进口准备步骤">{phases.map((p,i)=><button type="button" role="tab" key={p.title} className="brief-phase" id={`brief-tab-${i}`} aria-selected={phase===i} aria-controls="brief-stage-panel" tabIndex={phase===i?0:-1} onKeyDown={e=>keys(e,i)} onClick={()=>setPhase(i)}><span className="brief-phase-number">0{i+1}</span><span><strong>{p.title}</strong><span>{p.summary}</span></span><span className="brief-phase-arrow" aria-hidden="true">↗</span></button>)}</div>
  <div className="brief-workspace" role="tabpanel" id="brief-stage-panel" aria-labelledby={`brief-tab-${phase}`}>
   <div className="brief-explanation"><div className="brief-phase-copy"><span className="brief-overline">{current.label}</span><h3>{current.heading}</h3><p>{current.copy}</p><ul>{current.inputs.map(input=><li key={input}>{input}</li>)}</ul></div>
    {phase===0&&<div className="brief-ior"><button type="button" aria-expanded={ior} aria-controls="brief-ior-details" onClick={()=>setIor(!ior)}><Icon name="ior"/><span><strong>不确定 IOR 要求？</strong><span>可以从这里开始咨询。</span></span><b aria-hidden="true">{ior?"−":"+"}</b></button><RevealPanel id="brief-ior-details" open={ior} duration={.25}><p>请说明是否已指定登记进口商或报关行。如尚不确定，可先提供商品和交易信息，再讨论各方角色与支持范围。</p></RevealPanel></div>}
    {phase>0&&<p className="brief-context-note">{phase===1?"所需单证和审核范围取决于您的商品及货件。":"发货前请与各指定参与方确认实际责任。"}</p>}
    <div className="brief-step-actions"><span>查看步骤 {phase+1} / 3</span><button type="button" onClick={()=>setPhase((phase+1)%3)}>{phase===2?"返回商品信息":"下一步："+phases[phase+1].title}<span aria-hidden="true">→</span></button></div>
   </div>
   <div className={`brief-visual brief-visual-${phase}`}><div className="brief-visual-content">
    {phase===0&&<><div className="brief-visual-label"><span>准备起点</span><Icon name="ior"/></div><h4>商品、起运地与目的地。</h4><Image className="brief-cargo-art" src={`${base}documents-and-cargo.webp`} width={960} height={281} sizes="(max-width:767px) 100vw, 700px" alt="运输纸箱、商业发票和青蓝色文件夹示意图。"/><dl className="brief-fields"><div><dt>商品</dt><dd>商品是什么，有什么用途。</dd></div><div><dt>交易</dt><dd>原产地、参与方和目的地。</dd></div><div><dt>待确认事项</dt><dd>需要共同确认的内容。</dd></div></dl></>}
    {phase===1&&<><div className="brief-visual-label"><span>待确认问题</span><span>选择主题</span></div><div className="brief-question-buttons" role="group" aria-label="单证确认主题">{questions.map((item,i)=><button type="button" key={item.name} aria-pressed={question===i} onClick={()=>setQuestion(i)}>{item.name}</button>)}</div><div className="brief-question-content" aria-live="polite"><Icon name={q.icon}/><h4>{q.heading}</h4><p>{q.copy}</p><div className="brief-document-list">{q.fields.map((field,i)=><div key={field}><span>0{i+1}</span>{field}</div>)}</div></div></>}
    {phase===2&&<><div className="brief-visual-label"><span>责任分工</span><Icon name="ior"/></div><h4>明确每个交接环节。</h4><p className="brief-visual-intro">确认范围，明确联系人。</p><dl className="brief-roles">{roles.map(([name,task],i)=><div key={name}><span aria-hidden="true">0{i+1}</span><div><dt>{name}</dt><dd>{task}</dd></div></div>)}</dl></>}
   </div></div>
  </div><div className="brief-progress" aria-hidden="true"><span className="brief-progress-fill" style={{transform:`scaleX(${(phase+1)/3})`}}/></div>
  <div className="brief-support"><div><span className="brief-overline">从一个问题开始咨询。</span><h3>讨论您的货物需要哪些支持。</h3></div><a className="button" href="#quote">咨询进口支持 <span aria-hidden="true">↗</span></a></div>
  <p className="brief-footnote">本内容用于准备咨询；适用要求及可提供的支持需根据您的货物确认。</p>
 </div></section>;
}
