"use client";
import {useLayoutEffect,useRef,useState,type KeyboardEvent} from "react";
import Image from "next/image";
import gsap from "gsap";
import {Words,RevealPanel} from "./motion";
const base="/assets/customers/";
const channels=[
 {name:"Amazon FBA / FBM",teaser:"补货与单笔订单。",intro:"两种履约路径，分别确认要求。",image:"amazon-warehouse-photo",width:355,height:434,icon:"warehouse",cta:"咨询履约方案",items:[{icon:"warehouse",title:"FBA 中转补货",copy:"临时存储、贴标及分批发往 Amazon 仓库。"},{icon:"buyer",title:"FBM 订单",copy:"从美国仓库拣货、包装并发往买家。"},{icon:"checklist",title:"确认作业要求",copy:"包装、标签和放货要求。"}]},
 {name:"Shopify / TikTok Shop",teaser:"订单、退货与系统需求。",intro:"规划库存、订单及所需的系统连接。",image:"shopify-parcels",width:263,height:200,icon:"store",cta:"咨询订单履约",items:[{icon:"buyer",title:"订单准备",copy:"库存准备、拣货、包装和美国配送。"},{icon:"checklist",title:"退货交接",copy:"讨论退货要求和作业范围。"},{icon:"store",title:"系统需求",copy:"确认可用的平台连接和系统功能。"}]},
 {name:"工厂／B2B",teaser:"大宗出货与零售配送要求。",intro:"面向工厂、贸易公司和 B2B 供应商，规划大宗出货、库存及配送。",image:"b2b-pallet",width:250,height:218,icon:"pallet-truck",cta:"咨询 B2B 需求",items:[{icon:"pallet-truck",title:"大宗出货与库存",copy:"讨论运输、仓库收货和库存安排。"},{icon:"warehouse",title:"企业与零售配送",copy:"提供目的地，包括 Walmart 或其他零售渠道。"},{icon:"checklist",title:"收货要求",copy:"确认包装、标签和送货预约。"}]}
];
function AssetIcon({name,className=""}:{name:string;className?:string}){return <img className={`channel-icon ${className}`} src={`${base}${name}.svg`} width={80} height={80} alt="" aria-hidden="true"/>;}
export default function CustomerTypes(){
 const [active,setActive]=useState(0),root=useRef<HTMLElement>(null),timer=useRef<ReturnType<typeof setTimeout>|undefined>(undefined);
 const widths=useRef([3,1,1]);
 useLayoutEffect(()=>{const mm=gsap.matchMedia();mm.add("(min-width:1024px) and (prefers-reduced-motion:no-preference)",()=>{
  const panels=Array.from(root.current!.querySelectorAll<HTMLElement>(".channel-panel"));
  gsap.fromTo(panels,{flexGrow:i=>widths.current[i]},{flexGrow:i=>i===active?3:1,duration:.45,ease:"power2.inOut",onUpdate:()=>{widths.current=panels.map(el=>Number(el.style.flexGrow));}});
 });return()=>mm.revert();},[active]);
 useLayoutEffect(()=>()=>clearTimeout(timer.current),[]);
 function select(index:number){clearTimeout(timer.current);setActive(index);}
 function hover(index:number){clearTimeout(timer.current);if(root.current?.querySelector("a:focus"))return;timer.current=setTimeout(()=>setActive(index),140);}
 function keys(e:KeyboardEvent<HTMLButtonElement>,i:number){if(!["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(e.key))return;e.preventDefault();const n=e.key==="Home"?0:e.key==="End"?2:(i+(["ArrowLeft","ArrowUp"].includes(e.key)?2:1))%3;select(n);document.getElementById(`channel-choice-${n}`)?.focus();}
 return <section id="customers" className="channel-section" ref={root} aria-labelledby="channel-heading"><div className="container">
  <p className="eyebrow">02 / 适用客户</p><div className="channel-heading"><h2 id="channel-heading"><Words lines={["适配您的销售方式。"]}/></h2><p>选择销售渠道或业务类型，查看需要确认的服务和配送条件。</p></div>
  <div className="channel-panels">{channels.map((c,i)=><article key={c.name} className={`channel-panel ${active===i?"is-selected":""}`} onPointerEnter={e=>{if(e.pointerType==="mouse"&&matchMedia("(hover:hover)").matches)hover(i);}} onPointerLeave={()=>clearTimeout(timer.current)}>
   <button type="button" className="channel-choice" id={`channel-choice-${i}`} aria-expanded={active===i} aria-controls={`channel-content-${i}`} onFocus={()=>select(i)} onClick={()=>select(i)} onKeyDown={e=>keys(e,i)}><span className="channel-number">0{i+1}{active===i&&" / 已选择"}</span><span className="channel-title">{c.name}</span></button>
   {active!==i&&<><p className="channel-teaser">{c.teaser}</p><AssetIcon name={c.icon} className="channel-summary-icon"/></>}
   <RevealPanel open={active===i} id={`channel-content-${i}`} duration={.3}><div className="channel-content"><p className="channel-intro">{c.intro}</p><ul>{c.items.map(item=><li key={item.title}><AssetIcon name={item.icon}/><div><h3>{item.title}</h3><p>{item.copy}</p></div></li>)}</ul><a className="channel-cta" href="#fulfillment-options">查看履约方式<AssetIcon name="arrow"/></a><a className="channel-quote" href="#quote">{c.cta}</a></div></RevealPanel>
   <Image className={`channel-art channel-art-${i}`} src={`${base}${c.image}.webp`} alt={i===0?"仓库包装台及托盘上的包裹。":i===1?"运输纸箱与快递袋。":"托盘纸箱与叉车。"} width={c.width} height={c.height} sizes="(max-width:1023px) 90vw, 400px"/>
   {active!==i&&<button className="channel-expand" type="button" aria-label={`了解 ${c.name}`} onClick={()=>select(i)}><AssetIcon name="arrow"/></button>}
  </article>)}</div><p className="channel-note">平台名称仅用于描述业务场景，不代表官方合作或认证。</p>
 </div></section>;
}
