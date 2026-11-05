"use client";
import { useEffect, useRef, useState } from "react";
import { Words, RevealPanel, useSectionMotion, useSelectionMotion, arrowFeedback, topOfPage } from "./motion";
import SectionBlinds from "./section-blinds";
import ServiceDetails from "./service-details";
import CustomerTypes from "./customer-types";
import ConsultationProcess from "./consultation-process";
import PricingDetails from "./pricing-details";
import FaqTopics from "./faq-topics";
import QuoteInquiry from "./quote-inquiry";
import WarehouseWorkflow from "./warehouse-workflow";
import SystemRequirements from "./system-requirements";
import Image from "next/image";
import Link from "next/link";
import {services} from './service-data';

const sizes: Record<string,[number,number]> = { hero:[1672,433],freight:[825,683],warehouse:[1672,439],sellers:[784,220],factory:[408,286],ship:[531,286],storage:[394,286],delivery:[357,286],parcel:[336,252] };
function Visual({name,alt,className="",priority=false}:{name:string;alt:string;className?:string;priority?:boolean}) { const [w,h]=sizes[name];return <Image className={className} src={`/assets/images/${name}.webp`} alt={alt} width={w} height={h} sizes={name==="hero"||name==="warehouse"?"100vw":"(max-width: 767px) 100vw, (max-width: 1023px) 50vw, 660px"} priority={priority}/>; }
function Icon({name,className=""}:{name:string;className?:string}){return <img className={`icon ${className}`} src={`/assets/icons/${name}.svg`} width="24" height="24" alt="" aria-hidden="true"/>;}
function QuoteLink({children="获取物流报价",className=""}:{children?:React.ReactNode;className?:string}){return <a onPointerEnter={e=>arrowFeedback(e.currentTarget,true)} onPointerLeave={e=>arrowFeedback(e.currentTarget,false)} className={`button ${className}`} href="#quote">{children}<Icon name="arrow-up-right"/></a>;}


export default function Landing(){
 const [menu,setMenu]=useState(false),[mega,setMega]=useState(false),[service,setService]=useState(0);
 useSectionMotion();
 useSelectionMotion(menu,mega,service);
 const nav=useRef<HTMLElement>(null), servicesButton=useRef<HTMLButtonElement>(null),menuButton=useRef<HTMLButtonElement>(null);
 useEffect(()=>{function close(e:KeyboardEvent){if(e.key==="Escape" && (menu||mega)){setMega(false);setMenu(false);(menu?menuButton:servicesButton).current?.focus();}}function outside(e:PointerEvent){if(nav.current&&!nav.current.contains(e.target as Node)){setMega(false);setMenu(false);}}document.addEventListener("keydown",close);document.addEventListener("pointerdown",outside);return()=>{document.removeEventListener("keydown",close);document.removeEventListener("pointerdown",outside);};},[menu,mega]);
 function closeNav(){setMenu(false);setMega(false);}
 return <>
 <a href="#main" className="skip-link">跳至主要内容</a>
 <header onClick={e=>{if((e.target as Element).closest("a"))closeNav();}} ref={nav} className="site-header">
  <div className="container nav-inner"><a href="#top" aria-label="PNPLINE 首页" onClick={closeNav}><Image className="logo" src="/assets/logo.webp" alt="PNPLINE" width={180} height={48} priority/></a>
  <nav aria-label="主导航" className={`nav-links ${menu?"is-open":""}`}>
  <button className={mega?"selected":""} ref={servicesButton} aria-expanded={mega} aria-controls="services-menu" onClick={()=>setMega(!mega)}>服务范围 <span aria-hidden="true">⌄</span></button>
  <a href="#customers" onClick={closeNav}>适用客户</a><a href="#evidence" onClick={closeNav}>自营仓库</a><a href="#process" onClick={closeNav}>咨询流程</a><a href="#pricing" onClick={closeNav}>费用说明</a><a href="#faq" onClick={closeNav}>常见问题</a></nav>
  <div className="nav-actions"><span className="language">中文</span><QuoteLink/><button ref={menuButton} className="menu-toggle" aria-label={menu?"关闭菜单":"打开菜单"} aria-expanded={menu} onClick={()=>{setMenu(!menu);setMega(false);}}><Icon name={menu?"close":"menu"}/></button></div></div>
  {mega&&<div id="services-menu" className="mega-menu"><div className="container mega-grid"><div><p className="eyebrow">服务范围</p><h2>围绕您的<br/>货物需求。</h2><p>选择从中国出货到美国客户收货所需的服务。</p><a className="text-link" href="#services" onClick={closeNav}>了解服务范围 <Icon name="arrow"/></a></div><div className="mega-services">{services.map((s,i)=><a href="#services" key={s.title} onClick={()=>{setService(i);closeNav();}}><Icon name={s.icon}/><strong>{s.title}</strong><span>{s.copy}</span></a>)}</div></div></div>}
 </header>
 <main id="main">
 <section id="top" className="hero"><SectionBlinds/><div className="container hero-heading"><div><p className="eyebrow">中国至美国</p><h1><Words lines={["从中国出发。","为美国市场做好准备。"]}/></h1></div><div className="hero-support"><p>运输、美国仓储与订单履约。<br className="desktop-break"/> 衔接每个物流环节，支持您的业务安排。</p><div className="flex flex-wrap items-center gap-6"><QuoteLink/><a className="text-link" href="#services">了解服务 <Icon name="arrow"/></a></div></div></div>
 <div className="journey-track"><div className="journey-screen">
 <div className="journey-frame"><img className="journey-fallback" src="/assets/video/hero-b-v002-poster.webp" width={1920} height={1080} fetchPriority="high" alt="PNPLINE 物流旅程三维示意图。"/>
 <canvas className="journey-ambient" width={128} height={72} aria-hidden="true"/>
 <video className="journey-video" muted playsInline preload="none" disablePictureInPicture
   poster="/assets/video/hero-b-v002-poster.webp" aria-label="从中国集装箱装货到美国仓库履约及出库的三维物流示意。"/>
 <img className="journey-final" src="/assets/video/hero-b-v002-final.webp" alt="" width={1920} height={1080}/>
 <div className="journey-caption" aria-hidden="true">{["中国港口集装箱装货", "中国城市与港口起运", "跨越太平洋", "美国港口卸货", "货车抵达美国仓库", "仓库拣货与包装", "美国出库与配送"].map((text,i)=><div className="journey-label" key={text}><small>CN → US　 /　 0{i+1}</small><strong>{text}</strong></div>)}</div></div>
 <nav className="container route-legend" aria-label="物流视频阶段">{["中国装货", "中国起运", "跨洋运输", "美国卸货", "货车入仓", "拣货包装", "美国配送"].map(text=><button type="button" disabled key={text}>{text}</button>)}</nav></div></div></section>

 <section id="services" className="section services-section"><div className="container"><div className="section-heading"><p className="eyebrow">服务范围</p><div><h2><Words lines={["选择适合您的", "物流服务。"]}/></h2><p>从运输、仓储、订单履约或进口单证支持开始，在发货前确认服务范围和交接安排。</p></div></div><div className="services-layout"><div className="service-visual"><Visual name={services[service].image} alt={services[service].title+"微缩示意图"}/><span className="image-caption">从起运到订单交付</span></div><div className="service-list">{services.map((s,i)=><div className={`service-row ${service===i?"active":""}`} key={s.title}><button onPointerEnter={e=>arrowFeedback(e.currentTarget,true)} onPointerLeave={e=>arrowFeedback(e.currentTarget,false)} aria-expanded={service===i} aria-controls={`service-panel-${i}`} onClick={()=>setService(i)}><span className="row-number">0{i+1}</span><span>{s.title}</span><Icon name="arrow"/></button><RevealPanel id={`service-panel-${i}`} open={service===i} duration={.28}><p>{s.copy}</p><p className="service-detail">{s.detail}</p><a className="text-link service-details-link" href={["#freight-options","#warehouse","#fulfillment-options","#fulfillment-options"][i]}>查看服务详情 <Icon name="arrow"/></a><a className="text-link" href="#quote">咨询您的需求 <Icon name="arrow"/></a></RevealPanel></div>)}</div></div></div></section>

 <CustomerTypes/>
 <ServiceDetails/>

 <WarehouseWorkflow/>
 <SystemRequirements/>

 <ConsultationProcess/>

 <PricingDetails/>

 <FaqTopics/>

 <QuoteInquiry/>
 </main>
 <footer className="site-footer"><div className="container"><div className="footer-grid"><div><a href="#top" aria-label="PNPLINE 首页"><Image className="logo" src="/assets/logo.webp" alt="PNPLINE" width={180} height={48}/></a><p>跨境物流服务。<br/>美国自营海外仓。</p><span className="footer-route">中国 <span>⟶</span> 美国</span></div><div><h3>服务范围</h3>{services.map((s,i)=><a key={s.title} href="#services" onClick={()=>setService(i)}>{s.title}</a>)}</div><div><h3>了解更多</h3><a href="#customers">适用客户</a><a href="#evidence">仓库与系统</a><a href="#process">咨询流程</a><a href="#pricing">费用构成与明细</a><a href="#faq">常见问题</a></div><div><h3>联系我们</h3><a className="text-link" href="#quote">咨询我们的团队 <Icon name="arrow-up-right"/></a><span className="footer-language">简体中文</span></div></div><div className="footer-bottom"><p>© {new Date().getFullYear()} PNPLINE. 保留所有权利。</p><Link href="/privacy">隐私说明</Link><a href="#top" onClick={e=>{e.preventDefault();topOfPage();}}>返回顶部 ↑</a></div></div></footer>
 </>;
}

