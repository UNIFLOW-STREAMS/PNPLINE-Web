"use client";

import {useState,type KeyboardEvent} from "react";
import Image from "next/image";
import {ArrowUpRight} from "lucide-react";

const stages=[
 {name:"入库",label:"入库检查",title:"从清晰的交接开始。",copy:"在货物到仓前确认入库形式、收货检查和货运文件。",x:20,y:56.9},
 {name:"库存",label:"存储要求",title:"明确您的业务需求。",copy:"确认货物尺寸、存储方式、库存记录及存储时长。",x:45.75,y:60.7},
 {name:"出库",label:"订单准备",title:"为下一步出库做好准备。",copy:"针对每种出库方式确认订单准备、包装和配送要求。",x:65.85,y:54.7}
];
export default function WarehouseWorkflow(){
 const [selected,setSelected]=useState(1);
 function keys(event:KeyboardEvent<HTMLButtonElement>,index:number){if(!["ArrowLeft","ArrowRight","Home","End"].includes(event.key))return;event.preventDefault();const next=event.key==="Home"?0:event.key==="End"?2:(index+(event.key==="ArrowRight"?1:2))%3;setSelected(next);document.getElementById(`warehouse-tab-${next}`)?.focus();}
 return <section id="warehouse" className="warehouse-workflow" aria-labelledby="warehouse-workflow-title"><div className="container">
  <header id="evidence" className="warehouse-workflow-heading"><div><p className="eyebrow">03 / 仓库与系统</p><h2 id="warehouse-workflow-title">您的货物，<br/>交由我们的美国自营仓库。</h2></div><p>了解美国自营仓库的收货、存储和订单准备流程，确认货物接收条件、单证和交接责任。</p></header>
  <div className="warehouse-workflow-tabs" role="tablist" aria-label="仓库作业流程">{stages.map((item,i)=><button type="button" role="tab" id={`warehouse-tab-${i}`} key={item.name} aria-selected={selected===i} aria-controls="warehouse-workflow-panel" tabIndex={selected===i?0:-1} onClick={()=>setSelected(i)} onKeyDown={event=>keys(event,i)}>{item.name}</button>)}</div>
 </div>
 <div className="warehouse-workflow-art"><Image src="/assets/warehouse-workflow/warehouse-floor.webp" width={1672} height={455} sizes="(max-width:1672px) 100vw, 1672px" alt="仓库剖面示意：左侧为收货月台，中间为库存货架，右侧为包装台和出库货车。"/>
  {stages.map((item,i)=><button type="button" tabIndex={-1} className="warehouse-workflow-pin" key={item.name} style={{left:`${item.x}%`,top:`${item.y}%`}} aria-label={`查看${item.name}详情`} aria-pressed={selected===i} onClick={()=>setSelected(i)}><span className="sr-only">{item.name}</span></button>)}
 </div>
  <div className="container"><div className="warehouse-workflow-labels" aria-hidden="true">{stages.map((item,i)=><span className="warehouse-workflow-label" key={item.label} data-selected={selected===i}><span>0{i+1}</span>{item.label}</span>)}</div>
  <div className="warehouse-workflow-bottom"><p className="warehouse-workflow-note">仓库作业流程示意</p><div role="tabpanel" id="warehouse-workflow-panel" aria-labelledby={`warehouse-tab-${selected}`}><h3>{stages[selected].title}</h3><p>{stages[selected].copy}</p></div><a className="text-link" href="#system-requirements">查看系统使用要求 <ArrowUpRight aria-hidden="true"/></a></div>
 </div></section>;
}
