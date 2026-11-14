'use client';

import {useEffect,useId,useLayoutEffect,useRef,useState,type ReactNode,type KeyboardEvent,type CSSProperties} from 'react';
import Image from 'next/image';
import Link from 'next/link';
import {ArrowUpRight,ArrowRight,ChevronDown,ChevronRight,CircleHelp,Plus,Menu,X,Check,PackageCheck,PackageSearch,FileCheck2,UsersRound,Container,Boxes,Plane,Ship,Warehouse,Package,Truck,Layers,Braces,Store,Database,ClipboardList,ScanLine,Tags,CalendarCheck,PackageOpen,CalendarClock,ClipboardCheck,ListChecks,MapPin,UserRoundCheck,Files,Calculator,Receipt,type LucideIcon} from 'lucide-react';
import gsap from 'gsap';
import {ScrollTrigger} from 'gsap/ScrollTrigger';
import {mountHeroJourney} from './hero-journey';
import {mountHeroEntrance} from './hero-entrance';
import {mountSectionTitles} from './section-title-motion';
import {mountCardReadingState} from './card-reading-state';
import HeroServices from './hero-services';
import {CardArtwork, WarehouseArtwork} from './responsive-artwork';
import {compactLayoutQuery, tabletLayoutQuery} from './responsive-layout';
import {navigateToSection} from './service-navigation';
import QuoteInquiry from './quote-inquiry';
import {services, serviceTargets} from './service-data';
import {faqTopics} from './faq-data';
import {freightModes,comparison,outboundFlows,channels,phases,questions,roles,stages,steps,costAreas,importItems,conditions,inputs,outputs} from './content';
import {sourceBackground} from './media-theme';

gsap.registerPlugin(ScrollTrigger);
const fulfillmentTabIcons = [Package, Warehouse];
const fulfillmentStepIcons = [
  [ClipboardList, ScanLine, Tags, Truck],
  [ClipboardList, Tags, Boxes, CalendarCheck],
];
const warehouseIcons = [PackageCheck, Boxes, Truck];
const warehouseMarkers = [[22,86],[45,77],[74,75]];
const warehouseLabels = {"title":"美国仓储操作流程","badge":"美国 · 自营仓","sub":["入库核对","存储要求","订单准备"],"review":"需要确认","points":[["纸箱或托盘入库形式","收货验收要求","随货单证"],["货物尺寸与存储方式","库存记录","预计存储时长"],["订单准备","包装要求","交付交接"]],"cta":"查看系统对接要求","alt":"仓库剖面示意图，展示收货月台、库存货架和出库月台。"};
const importTopicIcons = [PackageSearch, FileCheck2, UsersRound];
const importTopics = {"title":"做好发货前的准备","names":["产品信息","单证核对","各方责任"],"sub":["产品与交易","单证与产品要求","人员与交接"],"head":["先了解您的货物","核对所需单证","明确各方职责"],"prep":"需要准备的信息","ior":"进口记录人（IOR）","note":"请说明是否已指定进口记录人（IOR）或委托报关行。如果尚未确定，可先提供产品与交易信息，以便讨论各方职责和支持范围。","roles":"各方分工","cta":"咨询进口支持","fine":"本内容用于前期规划。适用要求和可提供的支持以实际货件确认为准。"};
const freightModeIcons = [Container, Boxes, Plane];
const freightLabels = ["整柜 FCL","拼箱 LCL","空运"];
const freightHints = ["整柜运输","共享箱位","时效优先"];
const serviceArt = ['freight', 'warehouse', 'fulfillment', 'distribution'];

function ArrowLink({href='#quote',children,className=''}:{href?:string;children:ReactNode;className?:string}){
 return <a className={`arrow-link ${className}`} href={href}>{children}<ArrowUpRight size={19} aria-hidden="true"/></a>;
}
function Art({name,alt='',className=''}:{name:'warehouse'|'freight'|'fulfillment';alt?:string;className?:string}){
 const dimensions={warehouse:[1983,793],freight:[1774,887],fulfillment:[1920,819]}[name];
 return <Image className={`art art-${name} ${className}`} src={`/assets/air/${name}.png`} alt={alt} width={dimensions[0]} height={dimensions[1]} sizes="(max-width:767px) 90vw, (max-width:1200px) 80vw, 1300px"/>;
}
function Checks({items}:{items:string[]}){return <ul className="checks">{items.map(item=><li key={item}><Check size={17} aria-hidden="true"/><span>{item}</span></li>)}</ul>;}
const faqTopicIcons = {box:PackageCheck,quote:ClipboardList,clock:Truck};
const faqTopicHints = {box:"仓库、履约和交接",quote:"需提供的信息和报价核对",clock:"交付时间和系统对接"};
const costAreaIcons = [Ship, PackageCheck, Warehouse, PackageOpen, Truck];
const consultationStageIcons = [ClipboardList, ListChecks, FileCheck2];
const consultationItemIcons = [
 [Package, Ship, MapPin, UserRoundCheck],
 [Files, Warehouse, Truck, UsersRound],
 [Calculator, Layers, Receipt, ClipboardCheck],
];
const consultationContexts = ["货物与运输需求","服务范围与交接","报价核对"];

function Tabs({label,items,children,initial=0,renderLabel,renderShared,stackAt,stackOnTablet=false}:{label:string;items:string[];children:(index:number)=>ReactNode;initial?:number;renderLabel?:(index:number)=>ReactNode;renderShared?:(index:number)=>ReactNode;stackAt?:number;stackOnTablet?:boolean}){
 const verticalQuery = stackOnTablet ? tabletLayoutQuery : stackAt === undefined ? null : "(max-width: " + stackAt + "px)";
 const [active,setActive]=useState(initial),id=useId();
 const [vertical,setVertical]=useState(false);
 useEffect(()=>{
  if(!verticalQuery)return;
  const media=window.matchMedia(verticalQuery);
  const sync=()=>setVertical(media.matches);
  sync();
  media.addEventListener('change',sync);
  return ()=>media.removeEventListener('change',sync);
 },[verticalQuery]);
 function key(event:KeyboardEvent<HTMLButtonElement>,index:number){
  const previousKey=vertical?'ArrowUp':'ArrowLeft';
  const nextKey=vertical?'ArrowDown':'ArrowRight';
  if(![previousKey,nextKey,'Home','End'].includes(event.key))return;
  event.preventDefault();
  const next=event.key==='Home'?0:event.key==='End'?items.length-1:(index+(event.key===nextKey?1:items.length-1))%items.length;
  setActive(next);document.getElementById(`${id}-tab-${next}`)?.focus();
 }
 return <div className="tabbed"><div className="tabs" role="tablist" aria-label={label} aria-orientation={verticalQuery?vertical?'vertical':'horizontal':undefined}>{items.map((name,i)=><button key={name} type="button" role="tab" id={`${id}-tab-${i}`} aria-selected={active===i} aria-controls={`${id}-panel-${i}`} tabIndex={active===i?0:-1} onClick={()=>setActive(i)} onKeyDown={e=>key(e,i)}>{renderLabel ? renderLabel(i) : name}</button>)}</div>{renderShared?.(active)}{items.map((name,i)=><div key={name} role="tabpanel" tabIndex={0} id={`${id}-panel-${i}`} aria-labelledby={`${id}-tab-${i}`} hidden={active!==i} className="tab-panel">{children(i)}</div>)}</div>;
}
function Disclosure({title,children}:{title:string;children:ReactNode}){return <details className="disclosure"><summary>{title}<Plus size={20} aria-hidden="true"/></summary><div className="disclosure-body">{children}</div></details>;}

function FreightComparison() {
 return (
  <Disclosure title="比较三种运输方式">
   <div className="table-scroll freight-comparison-table" role="region" aria-label="运输方式对比" tabIndex={0}>
    <table>
     <caption className="sr-only">海运整柜、海运拼箱与空运对比</caption>
     <thead><tr><th scope="col">对比项目</th>{freightModes.map(mode=><th scope="col" key={mode.name}>{mode.name}</th>)}</tr></thead>
     <tbody>{comparison.map(([label,...values])=>(
      <tr key={label}>
       <th scope="row">{label}</th>
       {freightModes.map((mode,index)=><td key={mode.name}>{values[index]}</td>)}
      </tr>
     ))}</tbody>
    </table>
   </div>
   <div className="freight-comparison-phone">
    {freightModes.map((mode,index)=>(
     <article key={mode.name}>
      <h4>{mode.name}</h4>
      <dl>{comparison.map(([label,...values])=>(
       <div key={label}><dt>{label}</dt><dd>{values[index]}</dd></div>
      ))}</dl>
     </article>
    ))}
   </div>
  </Disclosure>
 );
}

function WarehouseReview({title,items}:{title:string;items:string[]}){
 return <details className="warehouse-review"><summary>{title}<Plus size={20} aria-hidden="true"/></summary><Checks items={items}/></details>;
}

function CardDisclosure({title,children,className='',name}:{
 title:ReactNode; children:ReactNode; className?:string; name?:string;
}){
 return <details className={"card-disclosure " + className} name={name}>
  <summary>{title}<span className="card-disclosure-icon" aria-hidden="true"><Plus size={16}/></span></summary>
  <div className="card-disclosure-body">{children}</div>
 </details>;
}

function DeliveryInsetContent(){
 return <>
     <ul className="distribution-list" role="list">
      <li><ClipboardList size={22} absoluteStrokeWidth aria-hidden="true"/><div><strong>采购订单与包装</strong><p>采购订单及纸箱、托盘要求。</p></div></li>
      <li><CalendarClock size={22} absoluteStrokeWidth aria-hidden="true"/><div><strong>预约交付</strong><p>收货时间与卸货通道。</p></div></li>
      <li><FileCheck2 size={22} absoluteStrokeWidth aria-hidden="true"/><div><strong>标签与交接</strong><p>标签要求与交付凭证。</p></div></li>
     </ul>
 </>;
}

function ReturnsInsetContent(){
 return <>
     <ol className="distribution-list" role="list">
      <li><PackageCheck size={22} absoluteStrokeWidth aria-hidden="true"/><span className="distribution-step-number" aria-hidden="true">01</span>接收退货</li>
      <li><ScanLine size={22} absoluteStrokeWidth aria-hidden="true"/><span className="distribution-step-number" aria-hidden="true">02</span>检查货物</li>
      <li><ClipboardCheck size={22} absoluteStrokeWidth aria-hidden="true"/><span className="distribution-step-number" aria-hidden="true">03</span>确认处置方式</li>
      <li><Boxes size={22} absoluteStrokeWidth aria-hidden="true"/><span className="distribution-step-number" aria-hidden="true">04</span>重新入库或隔离</li>
     </ol>
     <Disclosure title="查看处理细节">
      <p>记录退货编号、SKU、数量和外观状况。确认是否需要照片、包装检查和产品专项检查。</p>
      <p>确认是否需要重新贴标。仅在符合约定标准并获准后重新入库。将破损、缺件或待处理货物分开存放。</p>
     </Disclosure>
 </>;
}

function SystemsGroup({title, caption, items, icons}: {
 title: string;
 caption: string;
 items: typeof inputs;
 icons: LucideIcon[];
}){
 const list = <ul className="systems-list" role="list">
  {items.map((item, index) => {
   const Icon = icons[index];
   return <li className="system-node" key={item.name}>
    <Icon size={24} strokeWidth={1.8} aria-hidden="true"/>
    <div><h5>{item.name}</h5><p>{item.description}</p></div>
   </li>;
  })}
 </ul>;

 return <div className="systems-group">
  <div className="systems-group-heading"><h4>{title}</h4><p>{caption}</p></div>
  {list}
  <CardDisclosure className="systems-compact-group" title={<span>
   <strong>{title}</strong><small>{caption}</small>
  </span>}>
   {list}
  </CardDisclosure>
 </div>;
}

function ImportTopicBody({index,phone=false}:{index:number;phone?:boolean}){
 return <div className="import-stage">
  <div className="import-intro">
   <h3>{importTopics.head[index]}</h3>
   <p>{phases[index].copy}</p>
   <h4>{importTopics.prep}</h4>
   <Checks items={phases[index].inputs}/>
   {!phone && <ArrowLink className="import-desktop-cta">{importTopics.cta}</ArrowLink>}
  </div>
  {index===0 ? <>
   {!phone && <div className="import-detail import-ior-desktop"><h4>{importTopics.ior}</h4><p>{importTopics.note}</p></div>}
   <CardDisclosure title={importTopics.ior} className={phone ? "import-ior" : "import-ior import-ior-tablet"}><p>{importTopics.note}</p></CardDisclosure>
  </> : <div className="import-detail">
   {index===1 ? questions.map(question=><Disclosure key={question.name} title={question.name}>
    <p>{question.copy}</p><ul className="import-document-fields">{question.fields.map(field=><li key={field}>{field}</li>)}</ul>
   </Disclosure>) : <><h4>{importTopics.roles}</h4><dl className="responsibilities">{roles.map(([name,task])=><div key={name}><dt>{name}</dt><dd>{task}</dd></div>)}</dl></>}
  </div>}
  <ArrowLink className="import-compact-cta">{importTopics.cta}</ArrowLink>
 </div>;
}

function ImportPhoneTopics(){
 const group = useId();
 return <div className="import-phone-topics">
  {importTopics.names.map((title,index)=>{
   const Icon=importTopicIcons[index];
   return <CardDisclosure key={title} name={group} title={<><Icon size={21} aria-hidden="true"/><span>{title}</span></>}>
    <ImportTopicBody index={index} phone/>
   </CardDisclosure>;
  })}
 </div>;
}

function Heading({children,copy,display=false}:{children:ReactNode;copy?:ReactNode;display?:boolean}){return <header className={`chapter-heading ${display?'display-heading':''}`}><h2>{children}</h2>{copy&&<p>{copy}</p>}</header>;}

function CompactChapter({label,children}:{label:string;children:ReactNode}){
 const id=useId();
 const [expanded,setExpanded]=useState(false);
 return (
  <div className="compact-chapter" data-expanded={expanded}>
   <button type="button" className="button button-secondary compact-chapter-toggle"
    aria-expanded={expanded} aria-controls={id} onClick={()=>setExpanded(value=>!value)}>
    {expanded?`收起${label}`:`展开${label}`}<ChevronDown size={18} aria-hidden="true"/>
   </button>
   <div id={id} className="compact-chapter-content">{children}</div>
  </div>
 );
}

const serviceMenuItems = [
  {icon: 'freight', description: "整箱、拼箱与空运"},
  {icon: 'warehouse', description: "收货、存储与库存管理"},
  {icon: 'fulfillment', description: "拣货、包装与贴标"},
  {icon: 'distribution', description: "包裹配送与批量交付"},
  {icon: 'import-planning', description: "单证与交接责任"},
  {icon: 'systems', description: "平台、ERP 与数据对接"},
];

const navigationLinks = [
 {href: '#customers', label: '适用客户', Icon: UsersRound},
 {href: '#pricing', label: '费用说明', Icon: Receipt},
 {href: '#faq', label: '常见问题', Icon: CircleHelp},
];

function ServiceMenuLink({href, title, icon, description, onClick}: {
 href: string;
 title: string;
 icon: string;
 description: string;
 onClick: () => void;
}) {
 return (
  <a className="service-menu-link" href={href} onClick={onClick}>
   <span className="service-menu-icon" aria-hidden="true"
    style={{'--service-menu-icon': `url("/assets/service-menu/${icon}.svg")`} as CSSProperties}/>
   <span><strong>{title}</strong><small>{description}</small></span>
   <ArrowRight size={18} aria-hidden="true"/>
  </a>
 );
}

function Navigation(){
 const [open,setOpen]=useState(false),[mega,setMega]=useState<'hover' | 'click' | null>(null),root=useRef<HTMLElement>(null),toggle=useRef<HTMLButtonElement>(null),servicesToggle=useRef<HTMLButtonElement>(null);

 useEffect(() => {
  const header = root.current;
  const hero = document.querySelector('.hero');
  if (!header || !hero) return;
  const updateBackground = () => {
   const contentVisible = window.scrollY > 0 &&
    hero.getBoundingClientRect().bottom <= header.getBoundingClientRect().bottom + 72;
   header.toggleAttribute('data-content-visible', contentVisible);
  };
  updateBackground();
  window.addEventListener('scroll', updateBackground, {passive: true});
  window.addEventListener('resize', updateBackground);
  return () => {
   window.removeEventListener('scroll', updateBackground);
   window.removeEventListener('resize', updateBackground);
  };
 }, []);
 useEffect(() => {
  if (open && window.matchMedia(compactLayoutQuery).matches) {
   servicesToggle.current?.focus({preventScroll: true});
  }
 }, [open]);
 useEffect(()=>{const escape=(e:globalThis.KeyboardEvent)=>{if(e.key==='Escape'&&(open||mega)){if (mega) { setMega(null); servicesToggle.current?.focus(); } else { setOpen(false); toggle.current?.focus(); }}};const outside=(e:PointerEvent)=>{if(root.current&&!root.current.contains(e.target as Node)){setOpen(false);setMega(null);}};document.addEventListener('keydown',escape);document.addEventListener('pointerdown',outside);return()=>{document.removeEventListener('keydown',escape);document.removeEventListener('pointerdown',outside);};},[open,mega]);
 function close(){setOpen(false);setMega(null);}
 function openOnHover(event: React.PointerEvent<HTMLElement>){
  if(event.pointerType==='mouse' && !window.matchMedia(compactLayoutQuery).matches && window.matchMedia('(hover: hover)').matches) setMega(current => current ?? 'hover');
 }
 function closeOnLeave(event: React.PointerEvent<HTMLElement>){
  if(event.pointerType==='mouse' && !root.current?.querySelector(':focus-visible')) setMega(current => current === 'hover' ? null : current);
 }
 return <><div className="services-page-backdrop" data-open={Boolean(mega)} data-menu-open={open} aria-hidden="true"/>
 <header className="site-nav" data-services-open={Boolean(mega)} data-menu-open={open} ref={root} onPointerLeave={closeOnLeave}
  onBlur={({currentTarget, relatedTarget}) => {
   if (open && relatedTarget && !currentTarget.contains(relatedTarget) && window.matchMedia(compactLayoutQuery).matches) close();
  }}><div className="nav-shell">
 <nav id="main-navigation" className={`nav-links ${open?'is-open':''}`} aria-label="主导航">
  <button ref={servicesToggle} type="button" aria-expanded={Boolean(mega)} aria-controls="service-navigation" onPointerEnter={openOnHover} onClick={() => setMega(current => current === 'click' ? null : 'click')}>
   <span className="nav-item-icon" aria-hidden="true"><Layers size={18}/></span>
   <span>服务</span><ChevronDown size={14} className="nav-services-chevron" aria-hidden="true"/>
  </button>
  <div id="service-navigation" hidden={!mega} className="service-menu">
   <div className="service-menu-group" role="group" aria-labelledby="service-menu-main-label">
    <p className="service-menu-label" id="service-menu-main-label">服务范围</p>
    <div className="service-menu-grid">
     {services.map(({title}, index) => (
      <ServiceMenuLink key={title} href={`#${serviceTargets[index]}`} title={title}
       {...serviceMenuItems[index]} onClick={close}/>
     ))}
    </div>
   </div>
   <div className="service-menu-group service-menu-support" role="group" aria-labelledby="service-menu-support-label">
    <p className="service-menu-label" id="service-menu-support-label">准备与系统支持</p>
    <div className="service-menu-grid">
     <ServiceMenuLink href="#import-planning" title="进口准备" {...serviceMenuItems[4]} onClick={close}/>
     <ServiceMenuLink href="#systems" title="仓储系统" {...serviceMenuItems[5]} onClick={close}/>
    </div>
   </div>
   <a href="#services" className="service-menu-all" onClick={close}>查看全部服务 <ArrowRight size={16} aria-hidden="true"/></a>
  </div>
  {navigationLinks.map(({href, label, Icon}) => (
   <a key={href} href={href} onPointerEnter={() => {
    if (!window.matchMedia(compactLayoutQuery).matches) setMega(null);
   }} onClick={close}>
    <span className="nav-item-icon" aria-hidden="true"><Icon size={18}/></span>
    <span>{label}</span><ChevronRight size={16} className="nav-item-arrow" aria-hidden="true"/>
   </a>
  ))}
 </nav>
 <a className="brand" href="#top" aria-label="PNPLINE 首页" onClick={close}><Image src="/assets/logo.webp" alt="PNPLINE" width={180} height={48} priority/></a>
 <div className="nav-actions"><a className="button button-white" href="#quote" onClick={close}>获取报价<ArrowUpRight size={16}/></a><button className="mobile-menu" ref={toggle} aria-controls="main-navigation" aria-expanded={open} aria-label={open?'关闭菜单':'打开菜单'} onClick={()=>{setOpen(!open);setMega(null);}}>{open?<X/>:<Menu/>}</button></div>
 </div></header></>;
}

function FooterNavGroup({title, children}: {title: string; children: ReactNode}) {
 return <nav aria-label={title}>
  <div className="pn-footer-nav-wide">
   <h3>{title}</h3>
   {children}
  </div>
  <details className="pn-footer-nav-mobile">
   <summary>{title}<span aria-hidden="true"/></summary>
   {children}
  </details>
 </nav>;
}

export default function AirLanding({alternateUrl}: {alternateUrl?: string}){
 useLayoutEffect(mountHeroEntrance, []);
 useLayoutEffect(mountSectionTitles, []);
 useEffect(mountCardReadingState, []);
 useLayoutEffect(()=>{const media=gsap.matchMedia();media.add('(prefers-reduced-motion: no-preference)',()=>mountHeroJourney());return()=>media.revert();},[]);
 return <div className="air-site" data-source-background={sourceBackground} onClick={navigateToSection}>
 <svg className="card-art-grade-definitions" width={0} height={0} aria-hidden="true" focusable="false">
  <defs>
   <filter id="pnpline-card-art-grade" x="0%" y="0%" width="100%" height="100%" colorInterpolationFilters="sRGB">
    <feColorMatrix type="matrix" values="
      0.980 -0.045  0.008  0  0.023
     -0.165  1.454 -0.388  0  0.062
     -0.062  0.482  0.464  0  0.049
      0      0      0      1  0"/>
   </filter>
  </defs>
 </svg>
 <a className="skip-link" href="#main">跳转到正文</a><Navigation/><HeroServices/>
 <main id="main">
  <section className="hero" id="top" aria-labelledby="hero-title"><div className="hero-copy"><h1 id="hero-title"><span className="hero-title-line">中国起运，</span><span className="hero-title-line">扎根北美。</span></h1><p>PNPLINE 自营美仓，<span className="hero-subtitle-phrase">跨境运输</span>&nbsp;+ 仓储+订单履约一体化</p><div className="hero-actions"><a className="button button-secondary" href="#services">了解服务<ArrowRight size={19}/></a></div></div></section>

  <section className="chapter" id="services" aria-labelledby="services-title"><header className="chapter-heading"><h2 id="services-title">从发运<br/>到交付。</h2><p>四项服务，一套协调方案。<br/>确认服务范围，明确每一次交接。</p></header><div className="service-grid">{services.map((service,i)=>(
    <article className={`glass service-card service-${i}`} key={service.title} aria-labelledby={`service-title-${i}`}>
     <div className="service-card-intro">
      <header className="service-card-heading">
       <p className="service-kicker"><span aria-hidden="true">{String(i+1).padStart(2,'0')}</span>{service.category}</p>
       <div className="service-title"><h3 id={`service-title-${i}`}>{service.title}</h3></div>
        <p className="service-summary">{service.copy}</p>
      </header>
      <div className="service-art"><CardArtwork name={serviceArt[i]} alt="" sizes="(max-width: 700px) 90vw, (max-width: 1400px) 45vw, 650px"/></div>
     </div>
     <div className="service-body">
      <p className="service-region">{service.region}</p>
      <ul className="service-scope">{service.scope.map(item=><li key={item}>{item}</li>)}</ul>
      <ArrowLink href={`#${serviceTargets[i]}`}>{service.cta}</ArrowLink>
     </div>
    </article>
   ))}</div></section>

  <section className="chapter" id="customers"><Heading copy={<>不同的销售渠道，<br/>提供差异化物流解决方案</>}>适配业务场景，<br/>定制物流规划</Heading>
   <CompactChapter label="适用客户"><div className="customer-grid">{channels.map(channel=><article className="glass customer-card" key={channel.name}><div className="customer-identity"><Image src={`/assets/customer-icons/${channel.icon}.svg`} width={64} height={64} alt=""/><p className="customer-platform">{channel.platform}</p></div><h3>{channel.name}</h3><p className="card-intro">{channel.intro}</p><ul className="plain-list customer-desktop-details">{channel.items.map(item=><li key={item.title}><strong>{item.title}</strong><span>{item.copy}</span></li>)}</ul>
      <CardDisclosure className="customer-compact-details" title="查看操作要求">
       <ul className="plain-list">{channel.items.map(item=><li key={item.title}><strong>{item.title}</strong><span>{item.copy}</span></li>)}</ul>
      </CardDisclosure><ArrowLink>{channel.cta}</ArrowLink></article>)}</div></CompactChapter>
  </section>

  <section className="chapter" id="freight-options"><Heading display copy={<>中美海运整柜、拼箱、空运对比，<br/>区分报价的路线、操作和交接要求</>}>按货量和时效，<br/>挑选运输渠道。</Heading>
   <CompactChapter label="运输方案"><div className="glass freight-workspace"><header className="freight-topline"><p>选择适合的运输方式</p><span className="freight-route">中国<ArrowRight size={16} aria-hidden="true"/>美国</span></header>
    <Tabs label="运输方式" items={freightLabels} renderLabel={index=>{const Icon=freightModeIcons[index];return <><Icon className="freight-mode-icon" strokeWidth={1.75} aria-hidden="true"/><span className="freight-mode-label"><strong>{freightLabels[index]}</strong><small>{freightHints[index]}</small></span></>;}}>{index=><div className="freight-copy"><div><h3>{freightModes[index].caption}</h3><p>{freightModes[index].copy}</p><ArrowLink>规划运输方案</ArrowLink></div><div className="freight-preparation freight-preparation-desktop"><h4>需要准备的信息</h4><Checks items={freightModes[index].checks}/></div><CardDisclosure className="freight-preparation freight-preparation-phone" title="需要准备的信息"><Checks items={freightModes[index].checks}/></CardDisclosure></div>}</Tabs>
    <FreightComparison/>
    <p className="fine-print">运输路线、运力、时效和费用以实际货件确认为准。</p>
   </div></CompactChapter>
  </section>

  <section className="chapter" id="import-planning"><Heading display copy={<>先梳理产品与交易信息。<br/>确认支持范围前，<br className="import-subtitle-mobile-break"/>请核对 IOR 需求、单证和各方责任。</>}>发货前做好<br/>进口准备。</Heading>
   <CompactChapter label="进口准备详情"><div className="glass import-workspace">
    <p className="import-workspace-title">{importTopics.title}</p>
    <ImportPhoneTopics/>
    <Tabs label="进口准备主题" items={importTopics.names} stackOnTablet renderLabel={index=>{const Icon=importTopicIcons[index];return <><Icon className="import-topic-icon" strokeWidth={1.75} aria-hidden="true"/><span className="import-topic-label"><strong><span className="import-topic-number">0{index+1}</span> {importTopics.names[index]}</strong><small>{importTopics.sub[index]}</small></span></>;}}>{index=><ImportTopicBody index={index}/>}</Tabs><div className="workspace-footer"><p>{importTopics.fine}</p></div>
   </div></CompactChapter>
  </section>

  <section className="chapter warehouse-chapter" id="warehouse"><Heading display copy={<>标准化海外仓操作，<br className="warehouse-subtitle-mobile-break"/>定制化仓储服务，智能系统管理流程</>}>美国海外仓服务</Heading><div className="glass warehouse-workspace warehouse-workspace--panorama">
    <div className="warehouse-topline"><p>{warehouseLabels.title}</p><span className="warehouse-badge">{warehouseLabels.badge}</span></div>
    <Tabs label={warehouseLabels.title} items={stages.map(stage=>stage.name)} initial={0} renderLabel={i=>{const Icon=warehouseIcons[i];return <><Icon className="warehouse-tab-icon" size={24} strokeWidth={1.8} aria-hidden="true"/><span className="warehouse-tab-label"><strong>{stages[i].name}</strong><small>{warehouseLabels.sub[i]}</small></span></>;}}
      renderShared={i=><figure className="warehouse-visual">
          <div className="warehouse-drawing"><WarehouseArtwork alt={warehouseLabels.alt}/>{warehouseMarkers.map(([x,y],j)=><span key={j} className={`warehouse-marker ${i===j?'is-active':''}`} style={{left:`${x}%`,top:`${y}%`}} aria-hidden="true" data-stage={j+1}>{String(j+1).padStart(2,'0')}</span>)}</div>
          <ol className="warehouse-flow" aria-hidden="true">{stages.map((stage,j)=><li key={stage.name} className={i===j?'is-active':''}><span>0{j+1}</span>{stage.name}</li>)}</ol>
        </figure>}>
      {i=><div className="warehouse-stage">
        <div className="warehouse-stage-copy">
          <div className="warehouse-stage-intro"><p className="warehouse-eyebrow">0{i+1} / {warehouseLabels.sub[i]}</p>
          <h3>{stages[i].title}</h3><p className="warehouse-description">{stages[i].copy}</p></div>
          <WarehouseReview title={warehouseLabels.review} items={warehouseLabels.points[i]}/>
          <ArrowLink href="#systems">{warehouseLabels.cta}</ArrowLink>
        </div>
      </div>}
    </Tabs>
  </div></section>

  <section className="chapter" id="systems">
    <Heading copy={<>提供您的平台、ERP 或 API 需求，确认支持的对接<br className="tablet-heading-break"/>方式以及需要查看的仓库记录。</>}>规划仓储<br/>系统对接。</Heading>
    <div className="glass systems-workspace">
      <header className="systems-intro">
        <p className="systems-eyebrow">系统对接</p>
        <h3>明确系统如何对接。</h3>
        <p>提供平台、ERP 和 API 需求，共同确认对接范围与需要查看的仓库记录。</p>
      </header>
      <div className="systems-map">
        <SystemsGroup title="您的系统" caption="需要提供的信息" items={inputs} icons={[Store, Database, Braces]}/>
        <div className="systems-hub">
          <Image src="/assets/systems/connection-hub.svg" width={96} height={96} alt="" />
          <h4>对接范围</h4>
          <p>配置前共同确认</p>
        </div>
        <SystemsGroup title="仓库记录" caption="需要查看的信息" items={outputs} icons={[Boxes, PackageCheck, Truck]}/>
      </div>
      <Disclosure title="访问权限、数据更新与支持的对接"><div className="three-columns">{[['访问权限与功能','确认可用功能，以及谁可以查看或修改信息。'],['数据更新','约定所需记录的更新方式和时间。'],['平台／ERP 对接范围','根据您的系统确认可支持的对接方式。']].map(([title,copy])=><div key={title}><h4>{title}</h4><p>{copy}</p></div>)}</div></Disclosure>
      <div className="workspace-footer"><p>可用功能、权限和对接方式以约定方案为准。</p><ArrowLink>咨询系统对接</ArrowLink></div>
    </div>
  </section>

  <section className="chapter fulfillment-chapter" id="fulfillment-options">
   <Heading display copy="FBM和FBA的操作流程">订单履约。</Heading>
   <div className="glass fulfillment-workspace">
    <p className="fulfillment-topline">订单履约</p>
    <Tabs label="出库流程" items={outboundFlows.map(flow => flow.name)} renderLabel={index => {
     const flow = outboundFlows[index];
     const Icon = fulfillmentTabIcons[index];
     return (
      <>
       <Icon className="fulfillment-tab-icon" size={26} strokeWidth={1.75} aria-hidden="true" />
       <span className="fulfillment-tab-label"><strong>{flow.name}</strong><small>{flow.hint}</small></span>
      </>
     );
    }}>
     {index => {
      const flow = outboundFlows[index];
      return (
       <>
        <div className="fulfillment-body">
         <CardArtwork
          className="fulfillment-art"
          name={flow.art}
          alt={flow.alt}
          sizes="(max-width: 620px) 90vw, (max-width: 900px) 580px, (max-width: 1440px) 44vw, 650px"
         />
         <div className="fulfillment-copy">
          <h3>{flow.title}</h3>
          <p>{flow.copy}</p>
          <div className="fulfillment-details">
           <div className="fulfillment-detail fulfillment-detail-desktop">
            <h4><ClipboardList size={20} strokeWidth={1.75} aria-hidden="true" />准备事项</h4>
            <ul>{flow.input.map(item => <li key={item}>{item}</li>)}</ul>
           </div>
           <CardDisclosure className="fulfillment-detail fulfillment-detail-phone" title={<><ClipboardList size={20} strokeWidth={1.75} aria-hidden="true"/><span>准备事项</span></>}>
            <ul>{flow.input.map(item => <li key={item}>{item}</li>)}</ul>
           </CardDisclosure>
           <div className="fulfillment-detail fulfillment-detail-desktop">
            <h4><FileCheck2 size={20} strokeWidth={1.75} aria-hidden="true" />记录事项</h4>
            <ul>{flow.output.map(item => <li key={item}>{item}</li>)}</ul>
           </div>
           <CardDisclosure className="fulfillment-detail fulfillment-detail-phone" title={<><FileCheck2 size={20} strokeWidth={1.75} aria-hidden="true"/><span>记录事项</span></>}>
            <ul>{flow.output.map(item => <li key={item}>{item}</li>)}</ul>
           </CardDisclosure>
          </div>
         </div>
        </div>
        <div className="fulfillment-process">
         <h4>从准备到交接</h4>
         <ol className="fulfillment-steps" role="list">
          {flow.steps.map((step, stepIndex) => {
           const Icon = fulfillmentStepIcons[index][stepIndex];
           return (
            <li key={step}>
             <span className="fulfillment-step-icon"><Icon size={23} strokeWidth={1.75} aria-hidden="true" /></span>
             <span><small aria-hidden="true">{String(stepIndex + 1).padStart(2, '0')}</small><strong>{step}</strong></span>
            </li>
           );
          })}
         </ol>
        </div>
       </>
      );
     }}
    </Tabs>
    <p className="fine-print">准备规则在启动前确认。平台要求取决于您的发货计划。</p>
   </div>
  </section>

  <section className="chapter distribution-chapter" id="b2b" aria-labelledby="b2b-title">
   <header className="chapter-heading">
    <h2 id="b2b-title">B2B 交付<br className="tablet-heading-break"/>与退货处理</h2>
    <p>按客户的收货要求安排 B2B 交付，<br className="b2b-subtitle-mobile-break"/>并提前确认退货<br className="tablet-heading-break"/>的检查与处理方式。</p>
   </header>
   <article className="glass b2b-panel distribution-card">
    <div className="distribution-label"><span><Truck size={24} aria-hidden="true"/></span>出库交付</div>
    <h3>B2B 交付</h3>
    <p>根据批发或零售客户的收货要求，提前准备交付。</p>
    <div className="distribution-inset distribution-inset-desktop">
     <h4>交付前需确认</h4>
     <DeliveryInsetContent/>
    </div>
    <CardDisclosure className="distribution-inset distribution-inset-phone" title="交付前需确认">
     <DeliveryInsetContent/>
    </CardDisclosure>
    <ArrowLink>咨询 B2B 交付</ArrowLink>
   </article>
   <article className="glass returns-panel distribution-card" id="returns">
    <div className="distribution-label"><span><PackageOpen size={24} aria-hidden="true"/></span>退货处理</div>
    <h3>明确退货去向</h3>
    <p>退货到仓前，约定检查、重新贴标及重新入库的条件。</p>
    <div className="distribution-inset distribution-inset-desktop">
     <h4>退货处理流程</h4>
     <ReturnsInsetContent/>
    </div>
    <CardDisclosure className="distribution-inset distribution-inset-phone" title="退货处理流程">
     <ReturnsInsetContent/>
    </CardDisclosure>
    <ArrowLink>咨询退货处理</ArrowLink>
   </article>
  </section>

  <section className="chapter" id="process">
   <Heading copy="提供需求、核对条件并确认报价。">从物流需求<br/>到确认报价。</Heading>
   <div className="glass consultation-workspace">
    <Tabs label="咨询流程" items={steps.map(step => step.title)} renderLabel={index => {
     const Icon = consultationStageIcons[index];
     return <>
      <Icon size={24} aria-hidden="true"/>
      <span>
       <span className="consultation-tab-number">0{index + 1}</span>{' '}
       <strong className="consultation-tab-title">{steps[index].title}</strong>
      </span>
     </>;
    }}>
     {index => {
      const step = steps[index];
      return (
       <div className="consultation-content">
        <div className="consultation-intro">
         <span className="consultation-context">0{index + 1} / {consultationContexts[index]}</span>
         <h3>{step.heading}</h3>
         <p>{step.detail}</p>
         <ArrowLink>填写物流需求</ArrowLink>
        </div>
        <dl className="consultation-checks">
         {step.items.map((item, itemIndex) => {
          const Icon = consultationItemIcons[index][itemIndex];
          return (
           <div key={item.title}>
            <Icon size={24} aria-hidden="true"/>
            <dt>{item.title}</dt>
            <dd>{item.copy}</dd>
           </div>
          );
         })}
        </dl>
       </div>
      );
     }}
    </Tabs>
   </div>
  </section>

  <section className="chapter" id="pricing" aria-labelledby="pricing-heading">
   <header className="chapter-heading">
    <h2 id="pricing-heading">核对您的物流报价。</h2>
    <p>确认报价包含哪些服务，<br className="pricing-subtitle-mobile-break"/>以及何时可能产生额外费用。</p>
   </header>
   <div className="glass pricing-workspace">
    <header className="pricing-intro">
     <div>
      <span className="pricing-eyebrow">报价指南</span>
      <h3>物流费用一览</h3>
     </div>
     <p>了解运输、收货、存储、订单履约和配送的常见计费方式，以及哪些因素会影响您的报价。</p>
    </header>
    <div className="pricing-columns">
     <div className="pricing-phone-rates">
      {costAreas.map((item,index)=>{
       const Icon=costAreaIcons[index];
       return <CardDisclosure key={item.name} title={<>
        <Icon size={21} aria-hidden="true"/><span>{item.name}</span>
        <span className="pricing-basis"><span className="sr-only">常见计费依据：</span>{item.basis}</span>
       </>}><p>{item.confirmation}</p></CardDisclosure>;
      })}
     </div>
    <table className="cost-table" role="table">
     <caption className="sr-only">费用项目与计费依据</caption>
     <colgroup><col/><col/><col/></colgroup>
     <thead role="rowgroup">
      <tr role="row"><th scope="col" role="columnheader">费用项目</th><th scope="col" role="columnheader">影响报价的因素</th><th scope="col" role="columnheader">常见计费依据</th></tr>
     </thead>
     <tbody role="rowgroup">
      {costAreas.map((item, index)=>{
       const Icon = costAreaIcons[index];
       return <tr key={item.name} role="row">
        <th scope="row" role="rowheader"><span className="pricing-category"><span className="pricing-category-icon"><Icon size={24} strokeWidth={1.75} aria-hidden="true"/></span>{item.name}</span></th>
        <td role="cell">{item.confirmation}</td>
        <td role="cell"><span className="pricing-mobile-label" aria-hidden="true">常见计费依据</span><span className="pricing-basis">{item.basis}</span></td>
       </tr>;
      })}
     </tbody>
    </table>
    <div className="pricing-reviews">
      <details className="pricing-review">
       <summary>
        <Receipt size={24} strokeWidth={1.75} className="pricing-review-icon" aria-hidden="true"/>
        <span><strong>进口费用与税费</strong><small>报关、IOR 与适用税费</small></span>
        <span className="pricing-toggle"><Plus size={18} strokeWidth={1.75} aria-hidden="true"/></span>
       </summary>
       <div className="pricing-review-body">
        <p>核对报关协作、IOR 服务及适用税费如何在报价中列示。</p>
        <dl>{importItems.map(item=><div key={item.title}><dt>{item.title}</dt><dd>{item.copy}</dd></div>)}</dl>
       </div>
      </details>
      <details className="pricing-review">
       <summary>
        <ListChecks size={24} strokeWidth={1.75} className="pricing-review-icon" aria-hidden="true"/>
        <span><strong>报价适用条件</strong><small>最低收费、存储与特殊操作</small></span>
        <span className="pricing-toggle"><Plus size={18} strokeWidth={1.75} aria-hidden="true"/></span>
       </summary>
       <div className="pricing-review-body">
        <p>核对最低收费，以及何时计收存储费或额外操作费。</p>
        <dl>{conditions.map(item=><div key={item.title}><dt>{item.title}</dt><dd>{item.copy}</dd></div>)}</dl>
       </div>
      </details>
    </div>
    </div>
    <div className="pricing-footer">
     <p>服务范围与最终费用以确认后的报价为准。</p>
     <ArrowLink>咨询报价范围</ArrowLink>
    </div>
   </div>
  </section>

  <section className="chapter" id="faq" aria-labelledby="faq-heading">
   <header className="chapter-heading">
    <h2 id="faq-heading">获取报价前<br className="faq-heading-mobile-break"/>的常见问题</h2>
    <p>了解可提供的服务，<br className="faq-subtitle-mobile-break"/>以及发货前需要准备的信息。</p>
   </header>
   <div className="glass faq-workspace">
    <header className="faq-card-intro">
     <span>常见问题</span>
     <h3>按主题查找答案</h3>
    </header>
    <Tabs label="常见问题分类" items={faqTopics.map(topic=>topic.title)} renderLabel={index=>{
     const topic=faqTopics[index];
     const Icon=faqTopicIcons[topic.icon];
     return <>
      <Icon className="faq-topic-icon" size={24} strokeWidth={1.75} aria-hidden="true"/>
      <span className="faq-topic-copy"><strong>{topic.title}</strong><small>{faqTopicHints[topic.icon]}</small></span>
     </>;
    }}>{index=>{
     const topic=faqTopics[index];
     return <div className="faq-questions">
      <div className="faq-topic-meta"><strong><span className="faq-meta-title">{topic.title}</span><span className="faq-meta-hint">{faqTopicHints[topic.icon]}</span></strong><span>{topic.questions.length} 个问题</span></div>
      {topic.questions.map(question=><details className="faq-question" key={question.id}>
       <summary><span>{question.question}</span><span className="faq-toggle"><Plus size={17} strokeWidth={1.75} aria-hidden="true"/></span></summary>
       <div className="faq-answer">{question.answer.map(answer=><p key={answer}>{answer}</p>)}</div>
      </details>)}
     </div>;
    }}</Tabs>
    <div className="faq-contact">
     <div><strong>有具体的货件问题？</strong><p>告诉我们您的需求，以便确认具体要求和可提供的支持。</p></div>
     <ArrowLink>咨询您的物流需求</ArrowLink>
    </div>
   </div>
  </section>

  <div className="chapter quote-chapter"><QuoteInquiry/></div>
 </main>
 <footer className="air-footer">
  <div className="pn-footer-content">
    <div className="pn-footer-top">
      <div>
        <p className="pn-footer-kicker">规划下一票货物</p>
        <h2>从中国出发，<br/>衔接美国物流。</h2>
      </div>
      <a className="pn-footer-cta" href="#quote">核对货件信息<ArrowUpRight size={20} aria-hidden="true"/></a>
    </div>
    <div className="pn-footer-nav">
      <div className="pn-footer-brand">
        <Image className="pn-footer-logo" src="/assets/logo.webp" alt="PNPLINE" width={1500} height={400} unoptimized/>
        <p>跨境运输、美国自营仓储与订单履约。</p>
        <div className="pn-footer-route" role="img" aria-label="中国到美国">
          <span>中国</span>
          <ArrowRight size={22} aria-hidden="true"/>
          <span>美国</span>
        </div>
      </div>
      <FooterNavGroup title="服务">
        <ul>
          {services.map((service, i) => (
            <li key={service.title}><a href={`#${serviceTargets[i]}`}>{service.title}</a></li>
          ))}
        </ul>
      </FooterNavGroup>
      <FooterNavGroup title="规划与了解">
        <ul>
          <li><a href="#customers">适用客户</a></li>
          <li><a href="#systems">仓储系统</a></li>
          <li><a href="#process">咨询流程</a></li>
          <li><a href="#pricing">费用与报价说明</a></li>
          <li><a href="#faq">常见问题</a></li>
        </ul>
      </FooterNavGroup>
    </div>
    <div className="pn-footer-utilities">
      <p>© {new Date().getFullYear()} PNPLINE。保留所有权利。</p>
      <Link href="/privacy">隐私声明</Link>
      {alternateUrl && <div className="pn-footer-languages">
        <a href={alternateUrl} hrefLang="en" lang="en">English</a>
      </div>}
      <div className="pn-footer-registration">
        <a href="https://beian.miit.gov.cn/">粤ICP备19055173号-2</a>
      </div>
    </div>
  </div>
 </footer>
 </div>;
}

