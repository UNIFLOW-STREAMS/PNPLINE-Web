import Image from "next/image";
import {UserRound,KeyRound,History,Layers,Waypoints,ArrowUpRight} from "lucide-react";

const checks=[
 {title:"访问权限与功能",copy:"确认可用功能及可查看或修改记录的人员。"},
 {title:"数据更新",copy:"确认所需记录的更新方式和时间。"},
 {title:"平台／ERP 范围",copy:"确认您的业务配置可支持哪些平台或 ERP 连接。"}
];
function CheckIcon({index}:{index:number}){return <span className="system-requirement-icon" aria-hidden="true">{index===0?<><UserRound/><KeyRound className="system-requirement-badge"/></>:index===1?<History/>:<><Layers/><Waypoints className="system-requirement-badge"/></>}</span>;}
export default function SystemRequirements(){return <div className="system-requirements" id="system-requirements" role="region" aria-labelledby="system-requirements-title"><div className="container">
 <header className="system-requirements-heading"><div><p className="eyebrow">系统使用要求</p><h2 id="system-requirements-title">确认记录访问与更新方式。</h2><p>了解仓库作业流程后，进一步确认库存、入库和出库记录的访问方式。</p></div><Image src="/assets/warehouse-workflow/system-folder.webp" width={285} height={185} sizes="(max-width:767px) 140px, 210px" alt="青蓝色系统文件夹与包裹示意图。"/></header>
 <ol className="system-requirements-list">{checks.map((item,i)=><li key={item.title}><CheckIcon index={i}/><span className="system-requirement-number">0{i+1}</span><div><h3>{item.title}</h3><p>{item.copy}</p></div></li>)}</ol>
 <footer className="system-requirements-footer"><p>功能、权限和连接范围以双方确认的配置为准。</p><a className="text-link" href="#quote">咨询系统需求 <ArrowUpRight aria-hidden="true"/></a></footer>
 </div></div>;}
