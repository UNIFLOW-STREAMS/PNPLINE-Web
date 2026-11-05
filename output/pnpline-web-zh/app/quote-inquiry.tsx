"use client";

import {useLayoutEffect,useRef,useState,type FormEvent} from "react";
import Image from "next/image";
import {Package,Plane,Ruler,MapPin,ContactRound,Mail,ArrowUpRight} from "lucide-react";
import gsap from "gsap";
import {ScrollTrigger} from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);

const shippingMethods=["海运整柜","海运拼箱","空运","不确定"];
const destinations=["FBA 仓库","PNPLINE 美国自营仓库","最终消费者","美国企业或零售收货点","不确定"];
const fieldNames:Record<string,string>={cargo:"商品／货物类别",volume:"月货量",unit:"货量单位",otherUnit:"其他货量单位",email:"联系邮箱",consent:"隐私同意"};
const draftKey="pnpline-inquiry-draft-zh-CN-v1";

export default function QuoteInquiry(){
 const root=useRef<HTMLElement>(null),form=useRef<HTMLFormElement>(null);
 const [unit,setUnit]=useState(""),[volume,setVolume]=useState(""),[errors,setErrors]=useState<Record<string,string>>({}),[message,setMessage]=useState("");
 const [draft,setDraft]=useState<Record<string,string>>({});
 useLayoutEffect(()=>{try{const saved=JSON.parse(sessionStorage.getItem(draftKey)||"{}");if(saved&&typeof saved==="object"&&!Array.isArray(saved)){const values=Object.fromEntries(Object.entries(saved).filter(([,value])=>typeof value==="string")) as Record<string,string>;setDraft(values);setUnit(values.unit||"");setVolume(values.volume||"");}}catch{/* The form remains usable when browser storage is unavailable. */}},[]);
 function changed(event:FormEvent<HTMLFormElement>){
  const target=event.target;if(!(target instanceof HTMLInputElement||target instanceof HTMLSelectElement))return;
  clear(target.name);const values=Object.fromEntries(new FormData(event.currentTarget).entries()) as Record<string,string>;
  setDraft(values);try{sessionStorage.setItem(draftKey,JSON.stringify(values));}catch{/* Storage is optional; never block input. */}
 }
 const uncertain=["不确定","未定","待定","not sure"].includes(volume.trim().toLowerCase());
 useLayoutEffect(()=>{const mm=gsap.matchMedia();mm.add("(prefers-reduced-motion:no-preference)",()=>{
  gsap.from(root.current!.querySelectorAll(".inquiry-intro h2,.inquiry-intro>p:not(.eyebrow)"),{y:14,opacity:0,duration:.45,stagger:.06,ease:"power2.out",scrollTrigger:{trigger:root.current,start:"top 85%",once:true}});
  gsap.from(root.current!.querySelector(".inquiry-parcel"),{y:18,opacity:0,duration:.6,ease:"power2.out",scrollTrigger:{trigger:root.current,start:"top 75%",once:true}});
 },root);return()=>mm.revert();},[]);
 function focusField(name:string){form.current?.querySelector<HTMLElement>(`[name="${name}"]`)?.focus();}
 function clearDraft(){setDraft({});setUnit("");setVolume("");setErrors({});setMessage("");try{sessionStorage.removeItem(draftKey);}catch{}focusField("cargo");}
 function clear(name:string){setMessage("");setErrors(current=>{const next={...current};delete next[name];if(name==="volume"){delete next.unit;delete next.otherUnit;}if(name==="unit")delete next.otherUnit;return next;});}
 function submit(event:FormEvent<HTMLFormElement>){
  event.preventDefault();const fields=new FormData(event.currentTarget),next:Record<string,string>={};
  const text=(key:string)=>String(fields.get(key)||"").trim();
  if(!text("cargo"))next.cargo="请填写商品或货物类别。";
  const quantity=text("volume");
  if(quantity&&!uncertain){
   if(!/^\d+(?:\.\d+)?$/.test(quantity)||!Number.isFinite(Number(quantity))||Number(quantity)<=0)next.volume="请输入大于零的数量（可使用小数点），或填写“不确定”。";
   else if(!text("unit"))next.unit="请选择该数量的单位。";
   else if(text("unit")==="其他单位"&&!text("otherUnit"))next.otherUnit="请填写该数量使用的单位。";
  }
  const email=event.currentTarget.elements.namedItem("email") as HTMLInputElement;
  if(!text("email")||!email.validity.valid)next.email="请输入有效的联系邮箱。";
  if(!fields.has("consent"))next.consent="请阅读隐私说明并确认同意，以检查这些信息。";
  setErrors(next);setMessage("");
  if(Object.keys(next).length){focusField(Object.keys(next)[0]);return;}
  setMessage("信息已通过表单检查。本预览未发送询价，您可以继续编辑。");
 }
 const error=(name:string)=>errors[name]?<p id={`inquiry-${name}-error`} className="inquiry-error">{errors[name]}</p>:null;
 const described=(name:string,hint?:string)=>[hint,errors[name]?`inquiry-${name}-error`:null].filter(Boolean).join(" ")||undefined;
 return <section ref={root} id="quote" className="quote-inquiry" aria-labelledby="inquiry-heading"><div className="container inquiry-layout">
  <div className="inquiry-intro"><p className="eyebrow">07 / 物流询价</p><h2 id="inquiry-heading">请告诉我们<br/>您的货运需求。</h2><p>仅供预览。在此准备并检查您的货运信息。<br className="inquiry-desktop-break"/> 未知信息可填写“不确定”。</p><Image className="inquiry-parcel" src="/assets/quote/pnpline-parcel-logo.png" width={1600} height={983} sizes="(max-width:767px) 260px, (max-width:1023px) 320px, 430px" alt="PNPLINE 包裹与连接中国和美国的青蓝色路线示意图。"/><p className="inquiry-hint">尚未确定？先提供您已知的信息。</p></div>
  <form className="inquiry-form" ref={form} noValidate onSubmit={submit} onChange={changed} aria-describedby="inquiry-preview-note">
   <h3>预览您的询价需求</h3><p className="inquiry-preview-note" id="inquiry-preview-note">您可以在此检查货运信息。本表单不会将信息发送至 PNPLINE。检查时需要填写商品、联系邮箱并确认同意。</p>
   {Object.keys(errors).length>0&&<div className="inquiry-error-summary" role="alert"><p>请检查以下信息：</p><ul>{Object.entries(errors).map(([name,value])=><li key={name}><button type="button" onClick={()=>focusField(name)}>{fieldNames[name]}: {value}</button></li>)}</ul></div>}
   <div className="inquiry-field"><Package className="inquiry-field-icon" aria-hidden="true"/><div><label htmlFor="inquiry-cargo">商品／货物类别</label><input id="inquiry-cargo" name="cargo" value={draft.cargo||""} onChange={()=>{}} placeholder="商品名称或类别" required maxLength={160} aria-invalid={!!errors.cargo} aria-describedby={described("cargo")}/>{error("cargo")}</div></div>
   <fieldset className="inquiry-field"><Plane className="inquiry-field-icon" aria-hidden="true"/><legend>运输方式</legend><div className="inquiry-segments">{shippingMethods.map(method=><label key={method}><input type="radio" name="shipping" value={method} checked={draft.shipping===method} onChange={()=>{}}/><span>{method}</span></label>)}</div></fieldset>
   <div className="inquiry-field"><Ruler className="inquiry-field-icon" aria-hidden="true"/><div><label htmlFor="inquiry-volume">月货量</label><div className="inquiry-volume"><input id="inquiry-volume" name="volume" placeholder="数量或“不确定”" value={volume} onChange={e=>setVolume(e.target.value)} maxLength={32} aria-invalid={!!errors.volume} aria-describedby={described("volume","inquiry-volume-hint")}/><select name="unit" aria-label="月货量单位" value={uncertain?"":unit} onChange={e=>setUnit(e.target.value)} disabled={uncertain} aria-invalid={!!errors.unit} aria-describedby={described("unit")}><option value="">{uncertain?"无需单位":"立方米／千克／订单"}</option>{["CBM","kg","订单","其他单位"].map(option=><option key={option}>{option}</option>)}</select>{unit==="其他单位"&&!uncertain&&<input className="inquiry-other-unit" name="otherUnit" value={draft.otherUnit||""} onChange={()=>{}} aria-label="其他货量单位" placeholder="填写单位" maxLength={40} aria-invalid={!!errors.otherUnit} aria-describedby={described("otherUnit")}/>}</div><p className="inquiry-field-hint" id="inquiry-volume-hint">可填写体积、重量或订单数量，也可填写“不确定”。</p>{error("volume")}{error("unit")}{error("otherUnit")}</div></div>
   <div className="inquiry-field"><MapPin className="inquiry-field-icon" aria-hidden="true"/><div><label htmlFor="inquiry-destination">目的地类型</label><select id="inquiry-destination" name="destination" value={draft.destination||""} onChange={()=>{}}><option value="">选择目的地或“不确定”</option>{destinations.map(option=><option key={option}>{option}</option>)}</select></div></div>
   <fieldset className="inquiry-field"><ContactRound className="inquiry-field-icon" aria-hidden="true"/><legend>IOR 支持</legend><div className="inquiry-radios">{["需要","不需要","不确定"].map(option=><label key={option}><input type="radio" name="ior" value={option} checked={draft.ior===option} onChange={()=>{}}/><span>{option}</span></label>)}</div></fieldset>
   <div className="inquiry-field"><Mail className="inquiry-field-icon" aria-hidden="true"/><div><label htmlFor="inquiry-email">联系邮箱</label><input id="inquiry-email" name="email" value={draft.email||""} onChange={()=>{}} type="email" autoComplete="email" placeholder="you@company.com" required maxLength={254} aria-invalid={!!errors.email} aria-describedby={described("email")}/>{error("email")}</div></div>
   <div className="inquiry-consent"><input type="checkbox" id="inquiry-consent" name="consent" checked={draft.consent==="on"} onChange={()=>{}} required aria-invalid={!!errors.consent} aria-describedby={described("consent")}/><label htmlFor="inquiry-consent">我已阅读 <a href="/privacy/" target="_blank" rel="noopener noreferrer">隐私说明<span className="sr-only"> （在新标签页打开）</span></a> ，并同意将上述信息用于本次询价。</label></div>{error("consent")}
   <div className="inquiry-preview-row"><button type="button" onClick={clearDraft} className="inquiry-clear">清空表单</button></div>
   <button className="inquiry-submit" type="submit">检查询价信息 <ArrowUpRight aria-hidden="true"/></button>
   {message&&<p className="inquiry-submit-status" role="status">{message}</p>}
   <p className="inquiry-final-note">货运信息和支持范围确认后，可进一步确定报价及服务条款。</p>
  </form>
 </div></section>;
}
