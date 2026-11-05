"use client";

import {useLayoutEffect,useRef,useState,type KeyboardEvent,type SyntheticEvent} from "react";
import {Package,ArrowRight,FileText,CircleDollarSign,Clock3,Warehouse,Boxes,UserRound,Plus,Minus,ArrowUpRight} from "lucide-react";
import gsap from "gsap";
import {ScrollTrigger} from "gsap/ScrollTrigger";
import {faqTopics,faqs} from "./faq-data";
gsap.registerPlugin(ScrollTrigger);

function TopicIcon({kind}:{kind:"box"|"quote"|"clock"}){
 return <span className="faq-topic-icon" aria-hidden="true">{kind==="box"?<><Package/><ArrowRight className="faq-icon-badge"/></>:kind==="quote"?<><FileText/><CircleDollarSign className="faq-icon-badge"/></>:<><Clock3/><Warehouse className="faq-icon-badge"/></>}</span>;
}
function AnswerText({text}:{text:string}){
 if(text.startsWith("FBA:"))return <p className="faq-flow-answer"><Boxes aria-hidden="true"/><span><strong>FBA:</strong>{text.slice(4)}</span></p>;
 if(text.startsWith("FBM:"))return <p className="faq-flow-answer"><span className="faq-buyer-icon" aria-hidden="true"><UserRound/><Package/></span><span><strong>FBM:</strong>{text.slice(4)}</span></p>;
 return <p>{text}</p>;
}
export default function FaqTopics(){
 const root=useRef<HTMLElement>(null),[topic,setTopic]=useState(0),[openId,setOpenId]=useState<string|null>("fba-fbm");
 useLayoutEffect(()=>{
  const media=window.matchMedia("(max-width:767px)");
  const tabs=root.current!.querySelector("[role=tablist]")!;
  const orient=()=>tabs.setAttribute("aria-orientation",media.matches?"vertical":"horizontal");
  orient();media.addEventListener("change",orient);
  return()=>media.removeEventListener("change",orient);
 },[]);
 useLayoutEffect(()=>{
  const mm=gsap.matchMedia();
  mm.add("(prefers-reduced-motion:no-preference)",()=>{
   gsap.from(root.current!.querySelector(".faq-concept-heading"),{opacity:0,y:14,duration:.4,ease:"power2.out",scrollTrigger:{trigger:root.current,start:"top 85%",once:true}});
  },root);return()=>mm.revert();
 },[]);
 useLayoutEffect(()=>{
  const mm=gsap.matchMedia();
  mm.add("(prefers-reduced-motion:no-preference)",()=>{
   const answer=root.current!.querySelector(`#faq-answer-${openId}`);
   if(answer&&!answer.closest("[role=tabpanel]")?.hasAttribute("hidden"))gsap.fromTo(answer,{opacity:.3,y:4},{opacity:1,y:0,duration:.24,ease:"power1.out"});
  },root);
  ScrollTrigger.refresh();
  return()=>mm.revert();
 },[openId,topic]);
 function toggle(event:SyntheticEvent<HTMLDetailsElement>,id:string){
  if(event.currentTarget.open)setOpenId(id);
  else setOpenId(current=>current===id?null:current);
 }
 function keys(event:KeyboardEvent<HTMLButtonElement>,index:number){
  if(!["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(event.key))return;
  event.preventDefault();
  const next=event.key==="Home"?0:event.key==="End"?2:(index+(event.key==="ArrowLeft"||event.key==="ArrowUp"?2:1))%3;
  setTopic(next);document.getElementById(`faq-topic-${next}`)?.focus();
 }
 return <section id="faq" ref={root} className="faq-concept" aria-labelledby="faq-title"><div className="container">
  <header className="faq-concept-heading"><p className="eyebrow">常见问题</p><h2 id="faq-title">询价前的常见问题。</h2><p>对服务、费用或准备信息仍有疑问？请选择以下主题。</p></header>
  <div className="faq-topic-bar"><div className="faq-topic-tabs" role="tablist" aria-label="常见问题主题">{faqTopics.map((group,i)=><button type="button" role="tab" key={group.title} id={`faq-topic-${i}`} aria-selected={topic===i} aria-controls={`faq-group-${i}`} tabIndex={topic===i?0:-1} onClick={()=>setTopic(i)} onKeyDown={e=>keys(e,i)}><TopicIcon kind={group.icon}/><span>{group.title} ({group.questions.length})</span></button>)}</div><p className="faq-total">{faqs.length} 个问题，涵盖 {faqTopics.length} 个主题</p></div>
  {faqTopics.map((group,i)=><div className="faq-topic-panel" key={group.title} role="tabpanel" id={`faq-group-${i}`} aria-labelledby={`faq-topic-${i}`} hidden={topic!==i}>{group.questions.map((item,j)=><details key={item.id} name="pnpline-faq-answer" open={openId===item.id} onToggle={e=>toggle(e,item.id)}>
   <summary id={`faq-question-${item.id}`} aria-controls={`faq-answer-${item.id}`}><span className="faq-question-number">0{j+1}</span><span className="faq-question-label">{item.question}</span><span className="faq-answer-toggle" aria-hidden="true">{openId===item.id?<Minus/>:<Plus/>}</span></summary>
   <div className="faq-concept-answer" id={`faq-answer-${item.id}`}>{item.answer.map(text=><AnswerText key={text} text={text}/>)}</div>
  </details>)}</div>)}
  <footer className="faq-concept-footer"><p>具体要求和可提供的支持需根据您的货物确认。</p><a href="#quote" className="text-link">咨询您的需求 <ArrowUpRight aria-hidden="true"/></a></footer>
 </div></section>;
}
