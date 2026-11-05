"use client";

import {useLayoutEffect,useRef} from "react";
import Image from "next/image";
import {FileText,FileUser,ReceiptText,File,Percent,Ruler,Warehouse,Clock3,Package,ArrowUpRight} from "lucide-react";
import gsap from "gsap";
import {ScrollTrigger} from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);

const costAreas=[
 {name:"运输",confirmation:"整柜、拼箱或空运；路线、体积和重量",basis:"货件"},
 {name:"入库",confirmation:"纸箱或托盘形式及入库检查",basis:"托盘／纸箱"},
 {name:"存储",confirmation:"存储方式、占用空间和存储时长",basis:"空间／时长"},
 {name:"订单履约",confirmation:"拣货、包装、贴标、检验和退货",basis:"订单／件"},
 {name:"配送",confirmation:"目的地、包裹或托盘、服务和预约要求",basis:"包裹／货件"}
];
const importItems=[
 {title:"清关操作",copy:"确认服务范围与操作责任。",Icon:FileText},
 {title:"IOR 要求",copy:"确认是否需要 IOR 支持及其包含内容。",Icon:FileUser},
 {title:"服务费用",copy:"要求单独列明已确认的服务费用。",Icon:ReceiptText},
 {title:"适用关税与税费",copy:"确认适用金额及是否包含在报价中。",Icon:File}
];
const conditions=[
 {title:"最低收费",copy:"确认计费单位和最低收费。",Icon:Ruler},
 {title:"长期存储",copy:"确认存储期限、计费依据及额外收费起算条件。",Icon:Warehouse},
 {title:"特殊作业",copy:"确认特殊包装、贴标、检验和退货作业的费用。",Icon:Package}
];

export default function PricingDetails(){
 const root=useRef<HTMLDivElement>(null);
 useLayoutEffect(()=>{
  const mm=gsap.matchMedia();
  mm.add("(prefers-reduced-motion:no-preference)",()=>{
   root.current!.querySelectorAll<HTMLElement>(".pricing-concept-heading, .pricing-overview-heading").forEach(heading=>{
    gsap.from(heading,{opacity:0,y:14,duration:.35,ease:"power2.out",scrollTrigger:{trigger:heading,start:"top 94%",once:true}});
   });
  },root);
  return()=>mm.revert();
 },[]);
 return <div className="pricing-concept" ref={root}>
  <section id="pricing" className="section pricing-section pricing-overview" aria-labelledby="pricing-overview-title"><div className="container">
   <p className="eyebrow">05 / 费用说明</p>
   <div className="split-heading pricing-overview-heading"><h2 id="pricing-overview-title">先了解费用构成，<br/>再比较报价。</h2><p>费用取决于货物、货量、运输方式、存储时长和作业需求。</p></div>
   <p className="pricing-scope-note">服务以双方确认的货运范围为准。</p><nav className="pricing-detail-links" aria-label="费用明细"><a href="#pricing-import">进口费用与税费</a><a href="#pricing-conditions">附加费用</a></nav>
   <table className="pricing-table"><caption className="sr-only">费用项目、需确认事项及常见计费依据</caption><thead><tr><th scope="col">费用项目</th><th scope="col">需确认事项</th><th scope="col">常见计费依据</th></tr></thead><tbody>{costAreas.map(item=><tr key={item.name}><th scope="row">{item.name}</th><td data-label="需确认事项">{item.confirmation}</td><td data-label="常见计费依据">{item.basis}</td></tr>)}</tbody></table>
   <div className="pricing-cta"><p>提供货运信息，确认服务范围和费用。</p><a href="#quote" className="button">咨询物流报价 <ArrowUpRight className="icon" aria-hidden="true"/></a></div>

  </div></section>
  <section id="pricing-import" className="pricing-panel pricing-import" aria-labelledby="pricing-import-title"><div className="container">
   <header className="pricing-concept-heading"><div><p className="eyebrow">费用明细 / 01</p><h2 id="pricing-import-title">报价包含哪些进口费用和税费？</h2><p>除运输和仓储费用外，还应确认清关支持、IOR 服务及适用税费如何列明。</p></div><Image className="pricing-folder" src="/assets/pricing/folder-and-pen.webp" alt="青蓝色文件夹与笔示意图。" width={380} height={235} sizes="(max-width:767px) 110px, 230px"/></header>
   <ul className="pricing-open-list">{importItems.map(({title,copy,Icon},i)=><li key={title} className={i>1?"pricing-itemized":undefined}><span className="pricing-row-icon">{i===1?<img src="/assets/import-planning/ior.svg" width={44} height={44} alt="" aria-hidden="true"/>:<Icon aria-hidden="true"/>}{i===3&&<Percent className="pricing-tax-rate" aria-hidden="true"/>}</span><div><h3>{title}</h3><p>{copy}</p></div></li>)}</ul>

  </div></section>
  <section id="pricing-conditions" className="pricing-panel pricing-conditions" aria-labelledby="pricing-conditions-title"><div className="container">
   <header className="pricing-concept-heading"><div><p className="eyebrow">费用明细 / 02</p><h2 id="pricing-conditions-title">确认报价背后的适用条件。</h2><p>确认报价前，了解最低收费及仓储或额外作业费用的适用条件。</p></div></header>
   <ol className="pricing-condition-list">{conditions.map(({title,copy,Icon},i)=><li key={title}><span className="pricing-condition-number" aria-hidden="true">0{i+1}</span><span className="pricing-row-icon"><Icon aria-hidden="true"/>{i===1&&<Clock3 className="pricing-clock" aria-hidden="true"/>}</span><div><h3>{title}</h3><p>{copy}</p></div>{i===2&&<Image className="pricing-carton" src="/assets/pricing/pnpline-carton.webp" alt="带有 PNPLINE 标志的运输纸箱示意图。" width={245} height={155} sizes="(max-width:767px) 104px, 170px"/>}</li>)}</ol>
   <footer className="pricing-concept-footer"><p>最终费用以确认的报价为准。</p><a href="#quote" className="button">咨询报价范围 <ArrowUpRight aria-hidden="true"/></a></footer>
  </div></section>
 </div>;
}
