'use client';

import {useEffect,useId,useLayoutEffect,useRef,useState,type ReactNode,type KeyboardEvent,type CSSProperties} from 'react';
import Image from 'next/image';
import Link from 'next/link';
import {ArrowUpRight,ArrowRight,ArrowUp,ChevronDown,Plus,Menu,X,Check,PackageCheck,PackageSearch,FileCheck2,UsersRound,Container,Boxes,Plane,Ship,Warehouse,Package,Truck,Layers,Braces,Store,Database,ClipboardList,ScanLine,Tags,CalendarCheck,PackageOpen,CalendarClock,ClipboardCheck,ListChecks,MapPin,UserRoundCheck,Files,Calculator,Receipt} from 'lucide-react';
import gsap from 'gsap';
import {ScrollTrigger} from 'gsap/ScrollTrigger';
import {mountHeroJourney} from './hero-journey';
import {mountHeroEntrance} from './hero-entrance';
import {mountSectionTitles} from './section-title-motion';
import {mountCardReadingState} from './card-reading-state';
import HeroServices from './hero-services';
import {scrollToServiceSection} from './service-navigation';
import QuoteInquiry from './quote-inquiry';
import {services} from './service-data';
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
const warehouseLabels = {"title":"US warehouse workflow","badge":"United States · Directly operated","sub":["Inbound checks","Storage requirements","Order preparation"],"review":"What to review","points":[["Carton or pallet format","Receiving checks","Shipment documents"],["Cargo dimensions & storage method","Inventory records","Expected storage period"],["Order preparation","Packing requirements","Delivery handover"]],"cta":"Review system requirements","alt":"Illustrative warehouse cutaway showing receiving docks, inventory racks and dispatch."};
const importTopicIcons = [PackageSearch, FileCheck2, UsersRound];
const importTopics = {"title":"Prepare your shipment","names":["Product","Docs","Roles"],"sub":["Cargo & transaction","Documents & product rules","People & handovers"],"head":["Tell us about your cargo","Review your documents","Clarify each responsibility"],"prep":"Information to prepare","ior":"Importer of record (IOR)","note":"Tell us whether an importer of record or broker is already appointed. If it is unclear, bring your product and transaction details so the roles and support scope can be discussed.","roles":"Who handles what","cta":"Discuss import support","fine":"This is a planning guide. Applicable requirements and available support are confirmed for your shipment."};
const freightModeIcons = [Container, Boxes, Plane];
const freightLabels = ["FCL","LCL","Air freight"];
const freightHints = ["Full container","Shared ocean space","Time-sensitive cargo"];
const serviceTargets=['freight-options','warehouse','fulfillment-options','b2b'];
const serviceArt = [
  {name: 'freight', width: 1536, height: 1024},
  {name: 'warehouse', width: 1536, height: 1024},
  {name: 'fulfillment', width: 1536, height: 1024},
  {name: 'distribution', width: 1536, height: 1024},
];

function ArrowLink({href='#quote',children,className=''}:{href?:string;children:ReactNode;className?:string}){
 return <a className={`arrow-link ${className}`} href={href}>{children}<ArrowUpRight size={19} aria-hidden="true"/></a>;
}
function Art({name,alt='',className=''}:{name:'warehouse'|'freight'|'fulfillment';alt?:string;className?:string}){
 const dimensions={warehouse:[1983,793],freight:[1774,887],fulfillment:[1920,819]}[name];
 return <Image className={`art art-${name} ${className}`} src={`/assets/air/${name}.png`} alt={alt} width={dimensions[0]} height={dimensions[1]} sizes="(max-width:767px) 90vw, (max-width:1200px) 80vw, 1300px"/>;
}
function Checks({items}:{items:string[]}){return <ul className="checks">{items.map(item=><li key={item}><Check size={17} aria-hidden="true"/><span>{item}</span></li>)}</ul>;}
const faqTopicIcons = {box:PackageCheck,quote:ClipboardList,clock:Truck};
const faqTopicHints = {box:"Warehouses, fulfillment and handover",quote:"What to share and what to check",clock:"Delivery timing and system connections"};
const costAreaIcons = [Ship, PackageCheck, Warehouse, PackageOpen, Truck];
const consultationStageIcons = [ClipboardList, ListChecks, FileCheck2];
const consultationItemIcons = [
 [Package, Ship, MapPin, UserRoundCheck],
 [Files, Warehouse, Truck, UsersRound],
 [Calculator, Layers, Receipt, ClipboardCheck],
];
const consultationContexts = ["Your shipment","Scope and handovers","Quote review"];

function Tabs({label,items,children,initial=0,renderLabel,stackAt}:{label:string;items:string[];children:(index:number)=>ReactNode;initial?:number;renderLabel?:(index:number)=>ReactNode;stackAt?:number}){
 const [active,setActive]=useState(initial),id=useId();
 const [vertical,setVertical]=useState(false);
 useEffect(()=>{
  if(stackAt===undefined)return;
  const media=window.matchMedia(`(max-width: ${stackAt}px)`);
  const sync=()=>setVertical(media.matches);
  sync();
  media.addEventListener('change',sync);
  return ()=>media.removeEventListener('change',sync);
 },[stackAt]);
 function key(event:KeyboardEvent<HTMLButtonElement>,index:number){
  const previousKey=vertical?'ArrowUp':'ArrowLeft';
  const nextKey=vertical?'ArrowDown':'ArrowRight';
  if(![previousKey,nextKey,'Home','End'].includes(event.key))return;
  event.preventDefault();
  const next=event.key==='Home'?0:event.key==='End'?items.length-1:(index+(event.key===nextKey?1:items.length-1))%items.length;
  setActive(next);document.getElementById(`${id}-tab-${next}`)?.focus();
 }
 return <div className="tabbed"><div className="tabs" role="tablist" aria-label={label} aria-orientation={stackAt===undefined?undefined:vertical?'vertical':'horizontal'}>{items.map((name,i)=><button key={name} type="button" role="tab" id={`${id}-tab-${i}`} aria-selected={active===i} aria-controls={`${id}-panel-${i}`} tabIndex={active===i?0:-1} onClick={()=>setActive(i)} onKeyDown={e=>key(e,i)}>{renderLabel ? renderLabel(i) : name}</button>)}</div>{items.map((name,i)=><div key={name} role="tabpanel" tabIndex={0} id={`${id}-panel-${i}`} aria-labelledby={`${id}-tab-${i}`} hidden={active!==i} className="tab-panel">{children(i)}</div>)}</div>;
}
function Disclosure({title,children,open=false}:{title:string;children:ReactNode;open?:boolean}){return <details className="disclosure" open={open||undefined}><summary>{title}<Plus size={20} aria-hidden="true"/></summary><div className="disclosure-body">{children}</div></details>;}
function WarehouseReview({title,items}:{title:string;items:string[]}){
 const panel=useRef<HTMLDetailsElement>(null);
 useEffect(()=>{if(panel.current)panel.current.open=window.matchMedia('(min-width: 901px)').matches;},[]);
 return <details className="warehouse-review" ref={panel}><summary>{title}<Plus size={20} aria-hidden="true"/></summary><Checks items={items}/></details>;
}

function Heading({children,copy,display=false}:{children:ReactNode;copy?:string;display?:boolean}){return <header className={`chapter-heading ${display?'display-heading':''}`}><h2>{children}</h2>{copy&&<p>{copy}</p>}</header>;}

function CompactChapter({label,children}:{label:string;children:ReactNode}){
 const id=useId();
 const [expanded,setExpanded]=useState(false);
 return (
  <div className="compact-chapter" data-expanded={expanded}>
   <button type="button" className="button button-secondary compact-chapter-toggle"
    aria-expanded={expanded} aria-controls={id} onClick={()=>setExpanded(value=>!value)}>
    {expanded?'Hide':'Show'} {label}<ChevronDown size={18} aria-hidden="true"/>
   </button>
   <div id={id} className="compact-chapter-content">{children}</div>
  </div>
 );
}

const serviceMenuItems = [
  {icon: 'freight', description: "FCL, LCL and air freight"},
  {icon: 'warehouse', description: "Receiving, storage and inventory"},
  {icon: 'fulfillment', description: "Picking, packing and labeling"},
  {icon: 'distribution', description: "Parcel and bulk delivery"},
  {icon: 'import-planning', description: "Documents and responsibilities"},
  {icon: 'systems', description: "Platforms, ERP and data"},
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
 const [open,setOpen]=useState(false),[mega,setMega]=useState<'hover' | 'click' | null>(null),[moreServices,setMoreServices]=useState(false),root=useRef<HTMLElement>(null),toggle=useRef<HTMLButtonElement>(null),servicesToggle=useRef<HTMLButtonElement>(null),megaPanel=useRef<HTMLDivElement>(null);

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
  const panel = megaPanel.current;
  const nav = panel?.closest('nav');
  if (!mega || !panel || !nav) return;
  const update = () => {
   setMoreServices(window.matchMedia('(max-width: 800px)').matches &&
    panel.getBoundingClientRect().bottom > nav.getBoundingClientRect().bottom + 2);
  };
  update();
  nav.addEventListener('scroll', update, {passive: true});
  const observer = new ResizeObserver(update);
  observer.observe(nav);
  observer.observe(panel);
  return () => {
   nav.removeEventListener('scroll', update);
   observer.disconnect();
  };
 }, [mega]);
 useEffect(()=>{const escape=(e:globalThis.KeyboardEvent)=>{if(e.key==='Escape'&&(open||mega)){if (mega) { setMega(null); servicesToggle.current?.focus(); } else { setOpen(false); toggle.current?.focus(); }}};const outside=(e:PointerEvent)=>{if(root.current&&!root.current.contains(e.target as Node)){setOpen(false);setMega(null);}};document.addEventListener('keydown',escape);document.addEventListener('pointerdown',outside);return()=>{document.removeEventListener('keydown',escape);document.removeEventListener('pointerdown',outside);};},[open,mega]);
 function close(){setOpen(false);setMega(null);}
 function navigateSection(event: React.MouseEvent<HTMLElement>) {
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const link = (event.target as Element).closest<HTMLAnchorElement>('a[href^="#"]');
  if (!link || !event.currentTarget.contains(link)) return;
  const section = document.getElementById(link.hash.slice(1));
  if (!section) return;
  event.preventDefault();
  close();
  if (window.location.hash !== link.hash) window.history.pushState(window.history.state, '', link.hash);
  // Let the disclosure close before moving focus and measuring the destination.
  requestAnimationFrame(() => scrollToServiceSection(section, root.current));
 }

 function openOnHover(event: React.PointerEvent<HTMLElement>){
  if(event.pointerType==='mouse' && window.matchMedia('(min-width: 801px) and (hover: hover)').matches) setMega(current => current ?? 'hover');
 }
 function closeOnLeave(event: React.PointerEvent<HTMLElement>){
  if(event.pointerType==='mouse' && !root.current?.querySelector(':focus-visible')) setMega(current => current === 'hover' ? null : current);
 }
 return <><div className="services-page-backdrop" data-open={Boolean(mega)} aria-hidden="true"/><header className="site-nav" data-services-open={Boolean(mega)} ref={root} onPointerLeave={closeOnLeave}><div className="nav-shell">
 <nav id="main-navigation" className={`nav-links ${open?'is-open':''}`} aria-label="Main navigation"><button ref={servicesToggle} type="button" aria-expanded={Boolean(mega)} aria-controls="service-navigation" onPointerEnter={openOnHover} onClick={() => setMega(current => current === 'click' ? null : 'click')}>Services<ChevronDown size={14}/></button>
  <div id="service-navigation" ref={megaPanel} hidden={!mega} className="service-menu" onClick={navigateSection}>
   <div className="service-menu-group" role="group" aria-labelledby="service-menu-main-label">
    <p className="service-menu-label" id="service-menu-main-label">Services</p>
    <div className="service-menu-grid">
     {services.map(({title}, index) => (
      <ServiceMenuLink key={title} href={`#${serviceTargets[index]}`} title={title}
       {...serviceMenuItems[index]} onClick={close}/>
     ))}
    </div>
   </div>
   <div className="service-menu-group service-menu-support" role="group" aria-labelledby="service-menu-support-label">
    <p className="service-menu-label" id="service-menu-support-label">Planning &amp; systems</p>
    <div className="service-menu-grid">
     <ServiceMenuLink href="#import-planning" title="Import planning" {...serviceMenuItems[4]} onClick={close}/>
     <ServiceMenuLink href="#systems" title="Warehouse systems" {...serviceMenuItems[5]} onClick={close}/>
    </div>
   </div>
   <a href="#services" className="service-menu-all" onClick={close}>View all services <ArrowRight size={16} aria-hidden="true"/></a>
   <div className="service-menu-scroll-hint" aria-hidden="true" data-visible={moreServices}>
    Scroll for more <ChevronDown size={16}/>
   </div>
  </div>
  <a href="#customers" onPointerEnter={()=>setMega(null)} onClick={navigateSection}>Who we help</a><a href="#pricing" onPointerEnter={()=>setMega(null)} onClick={navigateSection}>Pricing</a><a href="#faq" onPointerEnter={()=>setMega(null)} onClick={navigateSection}>FAQ</a></nav>
 <a className="brand" href="#top" aria-label="PNPLINE home" onClick={close}><Image src="/assets/logo.webp" alt="PNPLINE" width={180} height={48} priority/></a>
 <div className="nav-actions"><a className="button button-white" href="#quote" onClick={close}>Get a quote<ArrowUpRight size={16}/></a><button className="mobile-menu" ref={toggle} aria-controls="main-navigation" aria-expanded={open} aria-label={open?'Close menu':'Open menu'} onClick={()=>{setOpen(!open);setMega(null);}}>{open?<X/>:<Menu/>}</button></div>
 </div></header></>;
}

export default function AirLanding({alternateUrl}: {alternateUrl?: string}){
 useLayoutEffect(mountHeroEntrance, []);
 useLayoutEffect(mountSectionTitles, []);
 useEffect(mountCardReadingState, []);
 useLayoutEffect(()=>{const media=gsap.matchMedia();media.add('(prefers-reduced-motion: no-preference)',()=>mountHeroJourney());return()=>media.revert();},[]);
 return <div className="air-site" data-source-background={sourceBackground}>
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
 <a className="skip-link" href="#main">Skip to content</a><Navigation/><HeroServices/>
 <main id="main">
  <section className="hero" id="top" aria-labelledby="hero-title"><div className="hero-copy"><h1 id="hero-title"><span className="hero-title-line">From China.</span><span className="hero-title-line">Ready for the US.</span></h1><p>Freight, US warehousing and order fulfillment.<br/>{' '}Connect each handover to support your operation.</p><div className="hero-actions"><a className="button button-secondary" href="#services">Explore services<ArrowRight size={19}/></a></div></div></section>

  <section className="chapter" id="services" aria-labelledby="services-title"><header className="chapter-heading"><h2 id="services-title">From shipment<br/>to delivery.</h2><p>Four services. One coordinated plan.<br/>Define the scope. Clarify every handover.</p></header><div className="service-grid">{services.map((service,i)=>(
    <article className={`glass service-card service-${i}`} key={service.title} aria-labelledby={`service-title-${i}`}>
     <div className="service-card-intro">
      <header className="service-card-heading">
       <p className="service-kicker"><span aria-hidden="true">{String(i+1).padStart(2,'0')}</span>{service.category}</p>
       <div className="service-title"><h3 id={`service-title-${i}`}>{service.title}</h3></div>
        <p className="service-summary">{service.copy}</p>
      </header>
      <div className="service-art"><Image src={`/assets/industrial-3d-v2/${serviceArt[i].name}.png`} alt="" width={serviceArt[i].width} height={serviceArt[i].height} sizes="(max-width: 700px) 90vw, (max-width: 1400px) 45vw, 650px"/></div>
     </div>
     <div className="service-body">
      <p className="service-region">{service.region}</p>
      <ul className="service-scope">{service.scope.map(item=><li key={item}>{item}</li>)}</ul>
      <ArrowLink href={`#${serviceTargets[i]}`}>{service.cta}</ArrowLink>
     </div>
    </article>
   ))}</div></section>

  <section className="chapter" id="customers"><Heading copy="Different channels. Different preparation.">Logistics around<br/>your business.</Heading>
   <CompactChapter label="customer types"><div className="customer-grid">{channels.map(channel=><article className="glass customer-card" key={channel.name}><div className="customer-identity"><Image src={`/assets/customer-icons/${channel.icon}.svg`} width={64} height={64} alt=""/><p className="customer-platform">{channel.platform}</p></div><h3>{channel.name}</h3><p className="card-intro">{channel.intro}</p><ul className="plain-list">{channel.items.map(item=><li key={item.title}><strong>{item.title}</strong><span>{item.copy}</span></li>)}</ul><ArrowLink>{channel.cta}</ArrowLink></article>)}</div></CompactChapter>
  </section>

  <section className="chapter" id="freight-options"><Heading display copy="Compare three ways to move goods from China. Then confirm the route, handling and handovers that shape your quote.">The right move<br/>starts with your cargo.</Heading>
   <CompactChapter label="freight options"><div className="glass freight-workspace"><header className="freight-topline"><p>Choose your freight mode</p><span className="freight-route">China<ArrowRight size={16} aria-hidden="true"/>United States</span></header>
    <Tabs label="Freight modes" items={freightLabels} renderLabel={index=>{const Icon=freightModeIcons[index];return <><Icon className="freight-mode-icon" strokeWidth={1.75} aria-hidden="true"/><span className="freight-mode-label"><strong>{freightLabels[index]}</strong><small>{freightHints[index]}</small></span></>;}}>{index=><div className="freight-copy"><div><h3>{freightModes[index].caption}</h3><p>{freightModes[index].copy}</p><ArrowLink>Plan your freight</ArrowLink></div><div className="freight-preparation"><h4>What to prepare</h4><Checks items={freightModes[index].checks}/></div></div>}</Tabs><Disclosure title="Compare all three shipping modes"><div className="table-scroll" role="region" aria-label="Freight comparison" tabIndex={0}><table><caption className="sr-only">FCL, LCL and air freight comparison</caption><thead><tr><th scope="col">Your shipment</th>{freightModes.map(mode=><th scope="col" key={mode.name}>{mode.name}</th>)}</tr></thead><tbody>{comparison.map(row=><tr key={row[0]}><th scope="row">{row[0]}</th>{row.slice(1).map(cell=><td key={cell}>{cell}</td>)}</tr>)}</tbody></table></div></Disclosure><p className="fine-print">Routing, capacity, transit time and charges are confirmed for your shipment.</p></div></CompactChapter>
  </section>

  <section className="chapter" id="import-planning"><Heading display copy="Start with your product and transaction details. Review IOR needs, documents and responsibilities before confirming the support scope.">Before<br/>you ship.</Heading>
   <CompactChapter label="import planning details"><div className="glass import-workspace">
    <p className="import-workspace-title">{importTopics.title}</p>
    <Tabs label="Import planning topics" items={importTopics.names} renderLabel={index=>{const Icon=importTopicIcons[index];return <><Icon className="import-topic-icon" strokeWidth={1.75} aria-hidden="true"/><span className="import-topic-label"><strong><span className="import-topic-number">0{index+1}</span> {importTopics.names[index]}</strong><small>{importTopics.sub[index]}</small></span></>;}}>{index=><div className="import-stage">
     <div className="import-intro"><h3>{importTopics.head[index]}</h3><p>{phases[index].copy}</p><h4>{importTopics.prep}</h4><Checks items={phases[index].inputs}/><ArrowLink>{importTopics.cta}</ArrowLink></div>
     <div className="import-detail">{index===0?<><h4>{importTopics.ior}</h4><p>{importTopics.note}</p></>:index===1?questions.map((question,q)=><Disclosure key={question.name} title={question.name} open={q===0}><p>{question.copy}</p><ul className="import-document-fields">{question.fields.map(field=><li key={field}>{field}</li>)}</ul></Disclosure>):<><h4>{importTopics.roles}</h4><dl className="responsibilities">{roles.map(([name,task])=><div key={name}><dt>{name}</dt><dd>{task}</dd></div>)}</dl></>}</div>
    </div>}</Tabs><div className="workspace-footer"><p>{importTopics.fine}</p></div>
   </div></CompactChapter>
  </section>

  <section className="chapter warehouse-chapter" id="warehouse"><Heading display copy="Review receiving, storage and order preparation in our directly operated US warehouses. Agree cargo acceptance, documents and handover responsibilities.">Your goods.<br/>Our US warehouses.</Heading><div className="glass warehouse-workspace warehouse-workspace--panorama">
    <div className="warehouse-topline"><p>{warehouseLabels.title}</p><span className="warehouse-badge">{warehouseLabels.badge}</span></div>
    <Tabs label={warehouseLabels.title} items={stages.map(stage=>stage.name)} initial={0} renderLabel={i=>{const Icon=warehouseIcons[i];return <><Icon className="warehouse-tab-icon" size={24} strokeWidth={1.8} aria-hidden="true"/><span className="warehouse-tab-label"><strong>{stages[i].name}</strong><small>{warehouseLabels.sub[i]}</small></span></>;}}>
      {i=><div className="warehouse-stage">
        <figure className="warehouse-visual">
          <div className="warehouse-drawing"><Image className="art warehouse-floor" src="/assets/industrial-3d-v2/warehouse-panorama.webp" alt={warehouseLabels.alt} width={2172} height={724} sizes="(max-width: 900px) 90vw, (max-width: 1800px) 94vw, 1672px"/>{warehouseMarkers.map(([x,y],j)=><span key={j} className={`warehouse-marker ${i===j?'is-active':''}`} style={{left:`${x}%`,top:`${y}%`}} aria-hidden="true" data-stage={j+1}>{String(j+1).padStart(2,'0')}</span>)}</div>
          <ol className="warehouse-flow" aria-hidden="true">{stages.map((stage,j)=><li key={stage.name} className={i===j?'is-active':''}><span>0{j+1}</span>{stage.name}</li>)}</ol>
        </figure>
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
    <Heading copy="Share your platform, ERP or API requirements. Review the supported connections and the warehouse records you need.">Plan your<br/>system connections.</Heading>
    <div className="glass systems-workspace">
      <header className="systems-intro">
        <p className="systems-eyebrow">System connections</p>
        <h3>Define how your systems connect.</h3>
        <p>Bring your platform, ERP and API requirements. Agree the connection scope and the warehouse records you need.</p>
      </header>
      <div className="systems-map">
        <div className="systems-group">
          <div className="systems-group-heading">
            <h4>Your systems</h4>
            <p>Information to share</p>
          </div>
          <ul className="systems-list" role="list">
            {inputs.map((item, index) => {
              const Icon = [Store, Database, Braces][index];
              return (
                <li className="system-node" key={item.name}>
                  <Icon size={24} strokeWidth={1.8} aria-hidden="true" />
                  <div>
                    <h5>{item.name}</h5>
                    <p>{item.description}</p>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
        <div className="systems-hub">
          <Image src="/assets/systems/connection-hub.svg" width={96} height={96} alt="" />
          <h4>Connection scope</h4>
          <p>Review together before setup</p>
        </div>
        <div className="systems-group">
          <div className="systems-group-heading">
            <h4>Warehouse records</h4>
            <p>Information you need</p>
          </div>
          <ul className="systems-list" role="list">
            {outputs.map((item, index) => {
              const Icon = [Boxes, PackageCheck, Truck][index];
              return (
                <li className="system-node" key={item.name}>
                  <Icon size={24} strokeWidth={1.8} aria-hidden="true" />
                  <div>
                    <h5>{item.name}</h5>
                    <p>{item.description}</p>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
      <Disclosure title="Access, updates &amp; supported connections"><div className="three-columns">{[['Access & functions','Confirm available functions and who can view or change information.'],['Data updates','Agree the methods and timing for the records you need.'],['Platform / ERP scope','Review the supported connections for your setup.']].map(([title,copy])=><div key={title}><h4>{title}</h4><p>{copy}</p></div>)}</div></Disclosure>
      <div className="workspace-footer"><p>Functions, permissions and connections depend on the agreed setup.</p><ArrowLink>Discuss system requirements</ArrowLink></div>
    </div>
  </section>

  <section className="chapter fulfillment-chapter" id="fulfillment-options">
   <Heading display copy="Different destinations. Different workflows. Prepare direct-to-customer parcels and marketplace replenishment around their next destination.">Fulfill.</Heading>
   <div className="glass fulfillment-workspace">
    <p className="fulfillment-topline">Order fulfillment</p>
    <Tabs label="Outbound workflow" items={outboundFlows.map(flow => flow.name)} renderLabel={index => {
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
         <Image
          className="fulfillment-art"
          src={'/assets/industrial-3d-v2/' + flow.art + '.png'}
          alt={flow.alt}
          width={1536}
          height={1024}
          sizes="(max-width: 620px) 90vw, (max-width: 900px) 580px, (max-width: 1440px) 44vw, 650px"
         />
         <div className="fulfillment-copy">
          <h3>{flow.title}</h3>
          <p>{flow.copy}</p>
          <div className="fulfillment-details">
           <div className="fulfillment-detail">
            <h4><ClipboardList size={20} strokeWidth={1.75} aria-hidden="true" />To prepare</h4>
            <ul>{flow.input.map(item => <li key={item}>{item}</li>)}</ul>
           </div>
           <div className="fulfillment-detail">
            <h4><FileCheck2 size={20} strokeWidth={1.75} aria-hidden="true" />To record</h4>
            <ul>{flow.output.map(item => <li key={item}>{item}</li>)}</ul>
           </div>
          </div>
         </div>
        </div>
        <div className="fulfillment-process">
         <h4>From preparation to handover</h4>
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
    <p className="fine-print">Preparation rules are confirmed before launch. Marketplace requirements depend on your shipment plan.</p>
   </div>
  </section>

  <section className="chapter distribution-chapter" id="b2b" aria-labelledby="b2b-title">
   <header className="chapter-heading">
    <h2 id="b2b-title">B2B delivery and returns</h2>
    <p>Plan deliveries around your customers’ receiving requirements, and decide in advance how returns will be inspected and handled.</p>
   </header>
   <article className="glass b2b-panel distribution-card">
    <div className="distribution-label"><span><Truck size={24} aria-hidden="true"/></span>Outbound delivery</div>
    <h3>B2B delivery</h3>
    <p>Prepare each delivery for your wholesale or retail customer’s receiving requirements.</p>
    <div className="distribution-inset">
     <h4>What to prepare</h4>
     <ul className="distribution-list" role="list">
      <li><ClipboardList size={22} absoluteStrokeWidth aria-hidden="true"/><div><strong>PO &amp; packing</strong><p>Purchase orders, cartons and pallets.</p></div></li>
      <li><CalendarClock size={22} absoluteStrokeWidth aria-hidden="true"/><div><strong>Delivery appointment</strong><p>Receiving hours and unloading access.</p></div></li>
      <li><FileCheck2 size={22} absoluteStrokeWidth aria-hidden="true"/><div><strong>Labels &amp; handover</strong><p>Label requirements and proof of delivery.</p></div></li>
     </ul>
    </div>
    <ArrowLink>Discuss B2B delivery</ArrowLink>
   </article>
   <article className="glass returns-panel distribution-card" id="returns">
    <div className="distribution-label"><span><PackageOpen size={24} aria-hidden="true"/></span>Returns handling</div>
    <h3>A clear path for returns</h3>
    <p>Agree inspection, relabeling and restocking criteria before returns arrive.</p>
    <div className="distribution-inset">
     <h4>Return workflow</h4>
     <ol className="distribution-list" role="list">
      <li><PackageCheck size={22} absoluteStrokeWidth aria-hidden="true"/><span className="distribution-step-number" aria-hidden="true">01</span>Receive</li>
      <li><ScanLine size={22} absoluteStrokeWidth aria-hidden="true"/><span className="distribution-step-number" aria-hidden="true">02</span>Inspect</li>
      <li><ClipboardCheck size={22} absoluteStrokeWidth aria-hidden="true"/><span className="distribution-step-number" aria-hidden="true">03</span>Approve disposition</li>
      <li><Boxes size={22} absoluteStrokeWidth aria-hidden="true"/><span className="distribution-step-number" aria-hidden="true">04</span>Restock or segregate</li>
     </ol>
     <Disclosure title="Review handling details">
      <p>Record the return reference, SKU, quantity and visible condition. Agree photo evidence, packaging checks and any product-specific inspection scope.</p>
      <p>Confirm any relabeling needed. Restock only when the agreed criteria are met and the disposition is approved. Keep damaged, incomplete or unresolved items separate.</p>
     </Disclosure>
    </div>
    <ArrowLink>Discuss return handling</ArrowLink>
   </article>
  </section>

  <section className="chapter" id="process">
   <Heading copy="Share your requirements, review the conditions and agree the quote.">From your brief<br/>to an agreed quote.</Heading>
   <div className="glass consultation-workspace">
    <Tabs label="Consultation steps" items={steps.map(step => step.title)} renderLabel={index => {
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
         <ArrowLink>Share your requirements</ArrowLink>
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
    <h2 id="pricing-heading">Review your logistics quote.</h2>
    <p>Check which services are included and when additional charges may apply.</p>
   </header>
   <div className="glass pricing-workspace">
    <header className="pricing-intro">
     <div>
      <span className="pricing-eyebrow">Pricing guide</span>
      <h3>Logistics costs at a glance</h3>
     </div>
     <p>See how freight, receiving, storage, fulfillment and delivery are typically billed, and what can affect your quote.</p>
    </header>
    <table className="cost-table" role="table">
     <caption className="sr-only">Cost areas and billing considerations</caption>
     <colgroup><col/><col/><col/></colgroup>
     <thead role="rowgroup">
      <tr role="row"><th scope="col" role="columnheader">Cost area</th><th scope="col" role="columnheader">What affects the quote</th><th scope="col" role="columnheader">Typical billing basis</th></tr>
     </thead>
     <tbody role="rowgroup">
      {costAreas.map((item, index)=>{
       const Icon = costAreaIcons[index];
       return <tr key={item.name} role="row">
        <th scope="row" role="rowheader"><span className="pricing-category"><span className="pricing-category-icon"><Icon size={24} strokeWidth={1.75} aria-hidden="true"/></span>{item.name}</span></th>
        <td role="cell">{item.confirmation}</td>
        <td role="cell"><span className="pricing-mobile-label" aria-hidden="true">Typical billing basis</span><span className="pricing-basis">{item.basis}</span></td>
       </tr>;
      })}
     </tbody>
    </table>
    <div className="pricing-reviews">
      <details className="pricing-review">
       <summary>
        <Receipt size={24} strokeWidth={1.75} className="pricing-review-icon" aria-hidden="true"/>
        <span><strong>Import fees &amp; taxes</strong><small>Customs, IOR and applicable taxes</small></span>
        <span className="pricing-toggle"><Plus size={18} strokeWidth={1.75} aria-hidden="true"/></span>
       </summary>
       <div className="pricing-review-body">
        <p>Check how customs support, IOR services and applicable taxes are listed in your quote.</p>
        <dl>{importItems.map(item=><div key={item.title}><dt>{item.title}</dt><dd>{item.copy}</dd></div>)}</dl>
       </div>
      </details>
      <details className="pricing-review">
       <summary>
        <ListChecks size={24} strokeWidth={1.75} className="pricing-review-icon" aria-hidden="true"/>
        <span><strong>Quote conditions</strong><small>Minimums, storage and special handling</small></span>
        <span className="pricing-toggle"><Plus size={18} strokeWidth={1.75} aria-hidden="true"/></span>
       </summary>
       <div className="pricing-review-body">
        <p>Check minimum charges and when storage or additional handling costs apply.</p>
        <dl>{conditions.map(item=><div key={item.title}><dt>{item.title}</dt><dd>{item.copy}</dd></div>)}</dl>
       </div>
      </details>
    </div>
    <div className="pricing-footer">
     <p>Service scope and final charges follow your confirmed quotation.</p>
     <ArrowLink>Discuss your quote scope</ArrowLink>
    </div>
   </div>
  </section>

  <section className="chapter" id="faq" aria-labelledby="faq-heading">
   <header className="chapter-heading">
    <h2 id="faq-heading">Before you request a quote</h2>
    <p>Check what services are available and what to prepare for your shipment.</p>
   </header>
   <div className="glass faq-workspace">
    <header className="faq-card-intro">
     <span>FAQ</span>
     <h3>Find answers by topic</h3>
    </header>
    <Tabs label="FAQ topics" items={faqTopics.map(topic=>topic.title)} stackAt={600} renderLabel={index=>{
     const topic=faqTopics[index];
     const Icon=faqTopicIcons[topic.icon];
     return <>
      <Icon className="faq-topic-icon" size={24} strokeWidth={1.75} aria-hidden="true"/>
      <span className="faq-topic-copy"><strong>{topic.title}</strong><small>{faqTopicHints[topic.icon]}</small></span>
     </>;
    }}>{index=>{
     const topic=faqTopics[index];
     return <div className="faq-questions">
      <div className="faq-topic-meta"><strong>{topic.title}</strong><span>{topic.questions.length} questions</span></div>
      {topic.questions.map(question=><details className="faq-question" key={question.id}>
       <summary><span>{question.question}</span><span className="faq-toggle"><Plus size={17} strokeWidth={1.75} aria-hidden="true"/></span></summary>
       <div className="faq-answer">{question.answer.map(answer=><p key={answer}>{answer}</p>)}</div>
      </details>)}
     </div>;
    }}</Tabs>
    <div className="faq-contact">
     <div><strong>Have a shipment-specific question?</strong><p>Tell us what you need so we can confirm the requirements and available support.</p></div>
     <ArrowLink>Discuss your requirements</ArrowLink>
    </div>
   </div>
  </section>

  <div className="chapter quote-chapter"><QuoteInquiry/></div>
 </main>
 <footer className="air-footer">
  <div className="pn-footer-content">
    <div className="pn-footer-top">
      <div>
        <p className="pn-footer-kicker">Plan your next shipment</p>
        <h2>From China.<br/>Connected in the US.</h2>
      </div>
      <a className="pn-footer-cta" href="#quote">Review shipment details<ArrowUpRight size={20} aria-hidden="true"/></a>
    </div>
    <div className="pn-footer-nav">
      <div className="pn-footer-brand">
        <Image className="pn-footer-logo" src="/assets/logo.webp" alt="PNPLINE" width={1500} height={400} unoptimized/>
        <p>Cross-border freight, directly operated US warehouses and order fulfillment.</p>
        <div className="pn-footer-route" role="img" aria-label="China to United States">
          <span>China</span>
          <ArrowRight size={22} aria-hidden="true"/>
          <span>United States</span>
        </div>
      </div>
      <nav aria-labelledby="footer-services-title">
        <h3 id="footer-services-title">Services</h3>
        <ul>
          {services.map((service, i) => (
            <li key={service.title}><a href={`#${serviceTargets[i]}`}>{service.title}</a></li>
          ))}
        </ul>
      </nav>
      <nav aria-labelledby="footer-planning-title">
        <h3 id="footer-planning-title">Plan &amp; learn</h3>
        <ul>
          <li><a href="#customers">Who we help</a></li>
          <li><a href="#systems">Warehouse systems</a></li>
          <li><a href="#process">How it works</a></li>
          <li><a href="#pricing">Costs &amp; quote details</a></li>
          <li><a href="#faq">FAQ</a></li>
        </ul>
      </nav>
    </div>
    <div className="pn-footer-utilities">
      <p>© {new Date().getFullYear()} PNPLINE. All rights reserved.</p>
      <Link href="/privacy">Privacy notice</Link>
      <div className="pn-footer-languages">
        <a href="#top" hrefLang="en" lang="en" aria-current="page">English</a>
        {alternateUrl && <a href={alternateUrl} hrefLang="zh-CN" lang="zh-CN">简体中文</a>}
      </div>
      <a className="pn-footer-back" href="#top">Back to top<ArrowUp size={16} aria-hidden="true"/></a>
    </div>
  </div>
 </footer>
 </div>;
}

