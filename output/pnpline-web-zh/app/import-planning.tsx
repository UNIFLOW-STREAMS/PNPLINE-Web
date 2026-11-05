"use client";
import {useLayoutEffect,useRef,useState} from "react";
import Image from "next/image";
import gsap from "gsap";
import {ScrollTrigger} from "gsap/ScrollTrigger";
import {RevealPanel} from "./motion";
gsap.registerPlugin(ScrollTrigger);
const base="/assets/import-planning/";
const topics=[
 {icon:"document",title:["Declaration","documents"],summary:"Review the product and transaction information needed.",detail:"Bring the commercial invoice, packing details and transport document information. Confirm the required entry documents with your appointed customs broker."},
 {icon:"classification",title:["HS","classification"],summary:"Confirm the classification questions for your goods.",detail:"Share the product’s materials, intended use, specifications and country of origin. Confirm US HTS classification with your appointed customs broker."},
 {icon:"review",title:["FDA / FCC","questions"],summary:"Describe the product, then check applicable requirements.",detail:"Share the product type, intended use and relevant technical specifications. Review whether FDA requirements or FCC equipment authorization apply before booking."}
];
const steps=[
 {title:"说明商品情况",summary:"Tell us about your product, transaction and destination.",detail:"Prepare the product description, specifications, origin, transaction details and intended US destination. Share what is already known and what needs discussion."},
 {title:"Review documents",summary:"Confirm the information and documents needed.",detail:"Review the invoice, packing list, transport information and any product-specific documents with the appointed broker. Identify missing information before shipment."},
 {title:"明确责任分工",summary:"Clarify the support scope and each party’s responsibilities.",detail:"Identify the importer of record, customs broker and duty payer. Agree who provides documents, handles exceptions and coordinates the warehouse handover."}
];
function Icon({name}:{name:string}){return <img src={`${base}${name}.svg`} className="import-icon" width={104} height={104} alt="" aria-hidden="true"/>;}
export default function ImportPlanning(){
 const root=useRef<HTMLElement>(null),[ior,setIor]=useState(false),[topic,setTopic]=useState<number|null>(null),[step,setStep]=useState<number|null>(null);
 useLayoutEffect(()=>{const mm=gsap.matchMedia();mm.add("(prefers-reduced-motion:no-preference)",()=>{
  const section=root.current!;
  const q=(s:string)=>section.querySelectorAll(s);
  const tl=gsap.timeline({scrollTrigger:{trigger:section,start:"top 82%",once:true},defaults:{ease:"power2.out"}});
  tl.from(q(".import-title-line"),{y:16,opacity:0,duration:.5,stagger:.05},0)
   .from(q(".ior-requirement"),{y:16,opacity:0,duration:.5},.08)
   .from(q(".import-topic"),{y:12,opacity:0,duration:.4,stagger:.07},.18)
   .from(q(".import-stage-line"),{scaleY:0,transformOrigin:"top",duration:.6},.25)
   .from(q(".import-stage-dot"),{opacity:0,scale:.5,duration:.3,stagger:.1},.25)
   .from(q(".import-document-image"),{y:18,scale:.98,opacity:0,duration:.6},.3);
 },root);return()=>mm.revert();},[]);
 return <section id="import-planning" className="import-consultation" aria-labelledby="import-title" ref={root}><div className="container import-consultation-grid">
  <div className="import-information"><p className="eyebrow">SERVICE DETAILS / 03</p>
   <article className={`ior-requirement ${ior?"is-open":""}`}><button className="ior-toggle" type="button" aria-expanded={ior} aria-controls="ior-preparation" onClick={()=>setIor(!ior)}><span className="ior-icon-wrap"><Icon name="ior"/></span><span><strong>IOR 要求</strong><span>Tell us whether an Importer of Record<br className="ior-desktop-break"/> is needed or still unclear.</span><small>{ior?"Hide preparation details −":"What to prepare +"}</small></span></button><RevealPanel open={ior} id="ior-preparation" duration={.24}><div className="import-extra">Share the parties involved, your product and transaction details, and whether an importer of record or broker has already been appointed. Confirm the responsibilities and agreed scope before shipment.</div></RevealPanel></article>
   <div className="import-topics">{topics.map((t,i)=><article className={`import-topic ${topic===i?"is-open":""}`} key={t.icon}><button type="button" aria-expanded={topic===i} aria-controls={`import-topic-${i}`} onClick={()=>setTopic(topic===i?null:i)}><Icon name={t.icon}/><strong>{t.title.map(line=><span key={line}>{line}</span>)}</strong><span className="import-topic-summary">{t.summary}</span><small>{topic===i?"Less −":"Details +"}</small></button><RevealPanel open={topic===i} id={`import-topic-${i}`} duration={.28}><p className="import-extra">{t.detail}</p></RevealPanel></article>)}</div>
   <Image className="import-document-image" src={`${base}documents-and-cargo.webp`} alt="A shipping carton, commercial invoice papers and a cyan document folder, extracted from the concept design." width={960} height={281} sizes="(max-width:1023px) 100vw, 800px"/>
  </div>
  <div className="import-conversation"><h2 id="import-title"><span className="import-title-line">Clarify the</span><span className="import-title-line">import requirements.</span></h2><p className="import-lead">Start with your product and transaction details.<br/>Confirm the support scope and each party’s responsibilities.</p>
   <div className="import-stages"><span className="import-stage-line" aria-hidden="true"/><ol>{steps.map((s,i)=><li className={step===i?"is-open":""} key={s.title}><span className="import-stage-dot" aria-hidden="true"/><button type="button" aria-expanded={step===i} aria-controls={`import-stage-${i}`} onClick={()=>setStep(step===i?null:i)}><span className="import-stage-number">0{i+1}</span><span><strong>{s.title}</strong><span>{s.summary}</span></span><small aria-hidden="true">{step===i?"−":"+"}</small></button><RevealPanel open={step===i} id={`import-stage-${i}`} duration={.28}><p className="import-extra">{s.detail}</p></RevealPanel></li>)}</ol></div>
   <div className="import-support"><h3>不确定 IOR 要求？</h3><p>Bring the basic product and transaction details to your inquiry.</p><a href="#quote">咨询进口支持<Icon name="arrow"/></a></div>
   <p className="import-disclaimer">Applicable requirements and available support are confirmed for the shipment.</p>
  </div>
 </div></section>;
}
