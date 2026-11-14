"use client";

import {useLayoutEffect,useRef,useState,type FormEvent,type KeyboardEvent} from "react";
import {ArrowRight, Info} from "lucide-react";
import {inquiryConfig} from "./inquiry-config";
import {compactLayoutQuery} from "./responsive-layout";

const inquiryTypes=["物流询价","仓储与履约咨询","进口咨询","其他咨询"];
const shippingMethods=["海运整柜（FCL）","海运拼箱（LCL）","空运","不确定"];
const destinations=["亚马逊 FBA 仓库","PNPLINE 美国自营仓","最终消费者","美国企业或零售收货点","不确定"];
const volumeUnits=[["CBM","立方米（CBM）"],["kg","千克（kg）"],["orders","订单数"],["Other unit","其他单位"]];
const fieldNames:Record<string,string>={inquiryType:"咨询类型",cargo:"产品／货物类别",shipping:"运输方式",destination:"目的地类型",ior:"IOR 支持",volume:"月货量",unit:"货量单位",otherUnit:"其他货量单位",email:"联系邮箱",consent:"隐私同意"};
const previewDraftKey = "pnpline-inquiry-draft-zh-cn";
const draftKey = inquiryConfig
 ? "pnpline-inquiry-live-zh-cn:" + inquiryConfig.consentVersion + ":business-inbox"
 : previewDraftKey;
const mobileProgressKey = draftKey + ":mobile-step";
type InquiryStep = 1 | 2 | 3;

function restoredStep(values: Record<string, string>, savedStep: string | null): InquiryStep {
 if (savedStep === "3" || values.email || values.consent) return 3;
 if (savedStep === "2" || values.cargo?.trim() || values.shipping || values.destination || values.ior) return 2;
 return 1;
}

const apiChoices = {
 shipping: new Map([["海运整柜（FCL）", "海运整柜"], ["海运拼箱（LCL）", "海运拼箱"]]),
 destination: new Map([["亚马逊 FBA 仓库", "FBA 仓库"], ["PNPLINE 美国自营仓", "PNPLINE 美国自营仓库"]]),
 unit: new Map([["orders", "订单"], ["Other unit", "其他单位"]]),
};

function isUncertain(value: string) {
 return ["不确定", "未定", "待定", "not sure"].includes(value.trim().normalize("NFKC").toLowerCase());
}

const receiptPattern=/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function saveDraft(values:Record<string,string>,requestId:string){
 try{sessionStorage.setItem(draftKey,JSON.stringify(inquiryConfig?{values,requestId}:values));}catch{/* Browser storage is optional. */}
}

export default function QuoteInquiry(){
 const form=useRef<HTMLFormElement>(null);
 const errorSummary=useRef<HTMLDivElement>(null);
 const phoneErrorSummary=useRef<HTMLDivElement>(null);
 const active=useRef(false),requestId=useRef("");
 const [pending,setPending]=useState(false);
 const [unit,setUnit]=useState(""),[volume,setVolume]=useState(""),[errors,setErrors]=useState<Record<string,string>>({}),[message,setMessage]=useState("");
 const [draft,setDraft]=useState<Record<string,string>>({});
 const [step,setStep]=useState<InquiryStep>(1);
 const [revealedStep,setRevealedStep]=useState<InquiryStep>();
 const composingCargo=useRef(false);
 const contactHeading=useRef<HTMLHeadingElement>(null);
 const pendingErrorFocus=useRef<{name:string;summary:boolean}|null>(null);
 useLayoutEffect(() => {
  try {
   const saved = JSON.parse(sessionStorage.getItem(draftKey) || "null");
   const previous = inquiryConfig && !saved
    ? JSON.parse(sessionStorage.getItem(previewDraftKey) || "null")
    : null;
   const entries = inquiryConfig ? saved?.values ?? previous : saved;
   if (!entries || typeof entries !== "object" || Array.isArray(entries)) return;
   const values = Object.fromEntries(Object.entries(entries).filter(([,value]) => typeof value === "string")) as Record<string,string>;
   if (inquiryConfig && !saved) delete values.consent;
   setDraft(values);
   setStep(restoredStep(values,sessionStorage.getItem(mobileProgressKey)));
   setUnit(values.unit || "");
   setVolume(values.volume || "");
   if (inquiryConfig && typeof saved?.requestId === "string" && receiptPattern.test(saved.requestId)) {
    requestId.current = saved.requestId;
   }
  } catch {/* The form remains usable when browser storage is unavailable. */}
 }, []);

 useLayoutEffect(() => {
  const destination = pendingErrorFocus.current;
  if (!destination) return;
  pendingErrorFocus.current = null;
  const phoneSummary = phoneErrorSummary.current;
  const summary = errorSummary.current;
  const headerBottom = document.querySelector(".site-nav")?.getBoundingClientRect().bottom ?? 0;
  if (destination.summary && phoneSummary?.getClientRects().length) {
   phoneSummary.focus({preventScroll:true});
   const viewport = window.visualViewport;
   const visibleBottom = viewport ? viewport.offsetTop + viewport.height : window.innerHeight;
   const controls = document.querySelector(".film-controls")?.getBoundingClientRect();
   const availableBottom = controls?.height ? Math.min(visibleBottom, controls.top) : visibleBottom;
   const summaryBounds = phoneSummary.getBoundingClientRect();
   const actionsBottom = phoneSummary.nextElementSibling?.getBoundingClientRect().bottom ?? summaryBounds.bottom;
   const scrollDelta = Math.min(
    summaryBounds.top - headerBottom - 24,
    Math.max(0, actionsBottom - availableBottom + 10),
   );
   window.scrollBy({top:scrollDelta, behavior:"instant"});
   return;
  }
  if (destination.summary && summary) {
   summary.focus({preventScroll:true});
   window.scrollBy({top:summary.getBoundingClientRect().top - headerBottom - 28, behavior:"instant"});
   return;
  }

  const {name} = destination;
  const field = form.current?.querySelector<HTMLElement>(`[name="${name}"]`);
  if (!field) return;

  field.focus({preventScroll:true});
  const fieldBounds = field.getBoundingClientRect();
  const summaryTop = summary?.getBoundingClientRect().top ?? fieldBounds.top;
  const viewportTop = headerBottom + 12;
  const availableHeight = window.innerHeight - viewportTop - 12;
  // Keep the error summary in view when it fits above the focused field.
  const contentTop = fieldBounds.bottom - summaryTop <= availableHeight ? summaryTop : fieldBounds.top;
  const centerOffset = (availableHeight - (fieldBounds.bottom - contentTop)) / 2;
  window.scrollBy({top:contentTop - viewportTop - centerOffset, behavior:"instant"});
 }, [errors]);

 function changed(event:FormEvent<HTMLFormElement>){
  const target=event.target;
  if(active.current || !(target instanceof HTMLInputElement || target instanceof HTMLSelectElement)) return;
  if(target.name === "website") return;
  clear(target.name);
  const values=Object.fromEntries(new FormData(event.currentTarget).entries()) as Record<string,string>;
  delete values.website;
  requestId.current="";
  setDraft(values);
  saveDraft(values,requestId.current);
  if((target.name==="email" || target.name==="consent") && !window.matchMedia(compactLayoutQuery).matches){
   advanceTo(3);
  }
 }

 function advanceTo(nextStep: 2 | 3){
  if(step>=nextStep)return;
  setStep(nextStep);
  setRevealedStep(nextStep);
  try{sessionStorage.setItem(mobileProgressKey,String(nextStep));}catch{/* Storage is optional. */}
 }

 function finishCargo(value:string){
  if(!composingCargo.current && value.trim())advanceTo(2);
 }

 function handleCargoEnter(event:KeyboardEvent<HTMLInputElement>){
  if(event.key!=="Enter" || !window.matchMedia(compactLayoutQuery).matches)return;
  if(composingCargo.current || event.nativeEvent.isComposing || event.keyCode===229)return;
  event.preventDefault();
  finishCargo(event.currentTarget.value);
 }

 function continueToContact(){
  advanceTo(3);
  requestAnimationFrame(()=>contactHeading.current?.focus({preventScroll:true}));
 }

 const uncertain=isUncertain(volume);
 function focusField(name:string,centerInView=false){
  const field=form.current?.querySelector<HTMLElement>(`[name="${name}"]`);
  if(centerInView){
   field?.focus({preventScroll:true});
   field?.scrollIntoView({block:"center",behavior:"instant"});
  }else{
   field?.focus();
  }
 }
 function resetDraft(){
  requestId.current="";
  setDraft({});
  setStep(1);
  setRevealedStep(undefined);
  composingCargo.current=false;
  setUnit("");
  setVolume("");
  setErrors({});
  try{
   sessionStorage.removeItem(draftKey);
   sessionStorage.removeItem(mobileProgressKey);
   if(inquiryConfig)sessionStorage.removeItem(previewDraftKey);
  }catch{/* Storage is optional. */}
 }
 function clearDraft(){resetDraft();setMessage("");focusField("cargo");}
 function clear(name:string){setMessage("");setErrors(current=>{const next={...current};delete next[name];if(name==="volume"){delete next.unit;delete next.otherUnit;}if(name==="unit")delete next.otherUnit;return next;});}
 async function submit(event:FormEvent<HTMLFormElement>){
  event.preventDefault();
  const compactLayout = window.matchMedia(compactLayoutQuery);
  if(active.current || (step<3 && compactLayout.matches))return;
  const fields=new FormData(event.currentTarget),next:Record<string,string>={};
  const text=(key:string)=>String(fields.get(key)||"").trim();
  if(!text("cargo"))next.cargo="请描述产品或货物类别。";
  const quantity=text("volume").normalize("NFKC");
  if(quantity&&!uncertain){
   if(!/^\d+(?:\.\d+)?$/.test(quantity)||!Number.isFinite(Number(quantity))||Number(quantity)<=0)next.volume="请输入大于零的数量（小数使用小数点），或填写「不确定」。";
   else if(!text("unit"))next.unit="请选择数量单位。";
   else if(text("unit")==="Other unit"&&!text("otherUnit"))next.otherUnit="请填写所使用的单位。";
  }
  const email=event.currentTarget.elements.namedItem("email") as HTMLInputElement;
  if(!text("email")||!email.validity.valid)next.email="请输入有效的联系邮箱。";
  if(!fields.has("consent"))next.consent=inquiryConfig?"请阅读隐私声明并勾选同意后提交。":"请阅读隐私声明并勾选同意，再检查这些信息。";
  const firstError = Object.keys(next)[0];
  if(firstError)pendingErrorFocus.current = {name:firstError,summary:compactLayout.matches};
  setErrors(next);setMessage("");
  if(firstError)return;
  if(!inquiryConfig){setMessage("填写的信息已通过检查。此预览不会发送询价，您可以继续修改。");return;}
  if(!globalThis.crypto?.randomUUID){setMessage("当前浏览器无法安全提交。请使用新版浏览器后重试。");return;}
  const choice=(field:keyof typeof apiChoices)=>apiChoices[field].get(text(field)) ?? text(field);
  const payload={inquiryType:text("inquiryType"),cargo:text("cargo"),shipping:choice("shipping"),volume:quantity,unit:quantity&&!uncertain?choice("unit"):"",
   otherUnit:quantity&&!uncertain&&text("unit")==="Other unit"?text("otherUnit"):"",
   destination:choice("destination"),ior:text("ior"),email:text("email"),consent:true,
   consentVersion:inquiryConfig.consentVersion,
   website:String(fields.get("website")||"")};
  const key=requestId.current||globalThis.crypto.randomUUID();
  const submitted=Object.fromEntries(fields.entries()) as Record<string,string>;
  delete submitted.website;
  requestId.current=key;saveDraft(submitted,key);
  active.current=true;setPending(true);
  const controller=new AbortController(),timer=window.setTimeout(()=>controller.abort(),12_000);
  let invalidField="";
  try{
   const response=await fetch(inquiryConfig.api,{method:"POST",credentials:"omit",redirect:"error",signal:controller.signal,
    headers:{"Content-Type":"application/json","Idempotency-Key":key},body:JSON.stringify(payload)});
   if(response.status===200||response.status===201){
    const body=await response.json();
    if(body?.status!=="accepted"||body?.inquiryId!==key||body?.receiptNumber!==key.replaceAll("-",""))throw new Error("invalid receipt");
    resetDraft();setMessage(`咨询已收到。您的受理编号是 ${body.receiptNumber}。`);return;
   }
   if(response.status===422){
    const body=await response.json();
    const invalid:Record<string,string>={};
    if(Array.isArray(body?.fields))for(const name of body.fields){
     if(typeof name==="string"&&Object.hasOwn(fieldNames,name))invalid[name]=name==="consent"
      ?"请刷新页面，阅读最新隐私说明后重新确认。":"请检查此项并重新提交。";
    }
    const firstInvalidField=Object.keys(invalid)[0];
    if(firstInvalidField){
     if(compactLayout.matches)pendingErrorFocus.current = {name:firstInvalidField,summary:true};
     else invalidField=firstInvalidField;
     setErrors(invalid);
     return;
    }
   }
   if(response.status===409){setMessage("此询价编号已用于另一份内容。请确认您的信息并修改后重新提交。");return;}
   if(response.status===429){setMessage("提交过于频繁，请稍后重试。");return;}
   if(response.status===413){setMessage("提交内容过长，请缩短后重试。");return;}
   setMessage("暂时无法确认接收结果。您的输入已保留，请稍后重试。");
  }catch{setMessage("暂时无法确认接收结果。您的输入已保留，请重试。");}
  finally{window.clearTimeout(timer);active.current=false;setPending(false);if(invalidField)requestAnimationFrame(()=>focusField(invalidField));}
 }
 const error=(name:string)=>errors[name]?<p id={`inquiry-${name}-error`} className="inquiry-error">{errors[name]}</p>:null;
 const described=(name:string,hint?:string)=>[hint,errors[name]?`inquiry-${name}-error`:null].filter(Boolean).join(" ")||undefined;
 const errorEntries = Object.entries(errors);
 function renderErrorSummary(phone = false) {
  if (!errorEntries.length) return null;
  return (
   <div className={phone ? "inquiry-error-summary inquiry-error-summary--phone" : "inquiry-error-summary inquiry-error-summary--wide"}
    ref={phone ? phoneErrorSummary : errorSummary} role="alert" tabIndex={-1}>
    <p>请检查以下信息：</p>
    <ul>{errorEntries.map(([name,value])=>(
     <li key={name}><button type="button" onClick={()=>focusField(name,window.matchMedia(compactLayoutQuery).matches)}>{fieldNames[name]}: {value}</button></li>
    ))}</ul>
   </div>
  );
 }
 return (
  <section id="quote" className="quote-inquiry" aria-labelledby="inquiry-heading">
   <div className="inquiry-layout">
    <div className="inquiry-intro">
     <span className="inquiry-eyebrow">货件规划</span>
     <h2 id="inquiry-heading">预估价格</h2>
     <p>先填写您已掌握的信息。选填项可留空，也可选择「不确定」。</p>
     <ul className="inquiry-guide">
      <li><span className="inquiry-guide-icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"><path d="m12 3 9 5-9 5-9-5 9-5Zm-9 5v10l9 5 9-5V8M12 13v10M7 5.8l9 5" /></svg></span><span><strong>货物信息</strong><small>产品与月货量</small></span></li>
      <li><span className="inquiry-guide-icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"><circle cx="5" cy="6" r="3" /><circle cx="19" cy="18" r="3" /><path d="M8 6h7a4 4 0 0 1 0 8H9a4 4 0 0 0 0 8h7" /></svg></span><span><strong>运输需求</strong><small>方式、目的地与 IOR</small></span></li>
      <li><span className="inquiry-guide-icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"><rect x="2" y="5" width="20" height="14" rx="3" /><path d="m3 7 9 7 9-7" /></svg></span><span><strong>联系信息</strong><small>邮箱与隐私同意</small></span></li>
     </ul>
     <div className="inquiry-notice">
      <strong><Info aria-hidden="true" size={18}/> {inquiryConfig?"询价说明":"仅供预览"}</strong>
      <p id="inquiry-preview-note">{inquiryConfig?"提交后，PNPLINE 将通过您填写的邮箱跟进。":"可在此检查填写的信息。此表单不会向 PNPLINE 发送询价。"}</p>
     </div>
    </div>
    <form className="inquiry-form" ref={form} noValidate onSubmit={submit} onChange={changed} aria-describedby="inquiry-preview-note" data-inquiry-step={step}>
     <p className="inquiry-progress" role="status">第 {step} 步，共 3 步</p>
     {inquiryConfig&&<input type="text" name="website" hidden tabIndex={-1} autoComplete="off"/>}
     {renderErrorSummary()}
     <section inert={pending} className="inquiry-group" aria-labelledby="inquiry-group-1">
      <div className="inquiry-group-heading"><span aria-hidden="true">01</span><h3 id="inquiry-group-1">货物信息</h3></div>
      {inquiryConfig&&<div className="inquiry-field"><div><label htmlFor="inquiry-type">咨询类型</label><select id="inquiry-type" name="inquiryType" value={draft.inquiryType||inquiryTypes[0]} onChange={()=>{}} aria-invalid={!!errors.inquiryType} aria-describedby={described("inquiryType")}>{inquiryTypes.map(type=><option key={type}>{type}</option>)}</select>{error("inquiryType")}</div></div>}
      <div className="inquiry-field"><div><label htmlFor="inquiry-cargo">产品／货物类别 <span className="inquiry-field-meta">必填</span></label><input id="inquiry-cargo" name="cargo" value={draft.cargo||""} onChange={()=>{}} placeholder="例如：棉质 T 恤" enterKeyHint="done" onBlur={e=>finishCargo(e.currentTarget.value)}
        onCompositionStart={()=>{composingCargo.current=true;}} onCompositionEnd={()=>{composingCargo.current=false;}}
        onKeyDown={handleCargoEnter} required maxLength={160} aria-invalid={!!errors.cargo} aria-describedby={described("cargo")}/>{error("cargo")}</div></div>
      <div className="inquiry-field"><div><label htmlFor="inquiry-volume">月货量 <span className="inquiry-field-meta">选填</span></label><div className="inquiry-volume"><input id="inquiry-volume" name="volume" placeholder="例如：20" value={volume} onChange={e=>setVolume(e.target.value)} maxLength={32} aria-invalid={!!errors.volume} aria-describedby={described("volume","inquiry-volume-hint")}/><select name="unit" aria-label="月货量单位" value={uncertain?"":unit} onChange={e=>setUnit(e.target.value)} disabled={uncertain} aria-invalid={!!errors.unit} aria-describedby={described("unit")}><option value="">{uncertain?"无需选择单位":"选择单位"}</option>{volumeUnits.map(([value,label])=><option key={value} value={value}>{label}</option>)}</select>{unit==="Other unit"&&!uncertain&&<input className="inquiry-other-unit" name="otherUnit" value={draft.otherUnit||""} onChange={()=>{}} aria-label="其他货量单位" placeholder="填写您的计量单位" maxLength={40} aria-invalid={!!errors.otherUnit} aria-describedby={described("otherUnit")}/>}</div><p className="inquiry-field-hint" id="inquiry-volume-hint">尚不确定？此项可留空。</p>{error("volume")}{error("unit")}{error("otherUnit")}</div></div>
     </section>
     <section inert={pending} className="inquiry-group" aria-labelledby="inquiry-group-2" data-inquiry-reveal={revealedStep===2 || undefined}>
      <div className="inquiry-group-heading"><span aria-hidden="true">02</span><h3 id="inquiry-group-2">运输需求</h3></div>
      <fieldset className="inquiry-field"><legend>运输方式 <span className="inquiry-field-meta">选填</span></legend><div className="inquiry-segments">{shippingMethods.map(method=><label key={method}><input type="radio" name="shipping" value={method} checked={draft.shipping===method} onChange={()=>{}} aria-invalid={!!errors.shipping} aria-describedby={described("shipping")}/><span>{method}</span></label>)}</div>{error("shipping")}</fieldset>
      <div className="inquiry-field"><div><label htmlFor="inquiry-destination">目的地类型 <span className="inquiry-field-meta">选填</span></label><select id="inquiry-destination" name="destination" value={draft.destination||""} onChange={()=>{}} aria-invalid={!!errors.destination} aria-describedby={described("destination")}><option value="">选择目的地</option>{destinations.map(option=><option key={option}>{option}</option>)}</select>{error("destination")}</div></div>
      <fieldset className="inquiry-field"><legend>进口记录人（IOR）支持 <span className="inquiry-field-meta">选填</span></legend>
     <details className="inquiry-ior-help"><summary>什么是 IOR？</summary><p>IOR 指进口记录人。如尚未确认由谁承担此角色，请选择「不确定」。</p></details><div className="inquiry-radios">{["需要","不需要","不确定"].map(option=><label key={option}><input type="radio" name="ior" value={option} checked={draft.ior===option} onChange={()=>{}} aria-invalid={!!errors.ior} aria-describedby={described("ior")}/><span>{option}</span></label>)}</div>{error("ior")}</fieldset>
      <button className="inquiry-submit inquiry-continue" type="button" onClick={continueToContact} aria-controls="inquiry-contact">
       继续填写联系信息 <ArrowRight aria-hidden="true"/>
      </button>
     </section>
     <section inert={pending} className="inquiry-group inquiry-contact" id="inquiry-contact" aria-labelledby="inquiry-group-3" data-inquiry-reveal={revealedStep===3 || undefined}>
      <div className="inquiry-group-heading"><span aria-hidden="true">03</span><h3 id="inquiry-group-3" tabIndex={-1} ref={contactHeading}>联系信息</h3></div>
      <div className="inquiry-field"><div><label htmlFor="inquiry-email">联系邮箱 <span className="inquiry-field-meta">必填</span></label><input id="inquiry-email" name="email" value={draft.email||""} onChange={()=>{}} type="email" autoComplete="email" placeholder="you@company.com" required maxLength={254} aria-invalid={!!errors.email} aria-describedby={described("email")}/>{error("email")}</div></div>
      <div className="inquiry-consent"><input type="checkbox" id="inquiry-consent" name="consent" checked={draft.consent==="on"} onChange={()=>{}} required aria-invalid={!!errors.consent} aria-describedby={described("consent")}/><label htmlFor="inquiry-consent">我已阅读<a href="/privacy/" target="_blank" rel="noopener noreferrer">隐私声明<span className="sr-only">（在新标签页打开）</span></a>，并同意将这些信息用于处理本次咨询。 <span className="inquiry-field-meta">必填</span></label></div>{error("consent")}
     </section>
     {renderErrorSummary(true)}
     <div className="inquiry-actions">
      <button type="button" onClick={clearDraft} onPointerDown={event=>{
       // Clearing a focused cargo field must not reveal step 02 and move the button before the click.
       if(step===1 && document.activeElement?.id==="inquiry-cargo" && window.matchMedia(compactLayoutQuery).matches){
        event.preventDefault();
       }
      }} className="inquiry-clear" disabled={pending}>清空表单</button>
      <button className="inquiry-submit inquiry-final-submit" type="submit" disabled={pending}>{pending?"正在提交…":inquiryConfig?"提交咨询":"检查询价信息"} <ArrowRight aria-hidden="true"/></button>
     </div>
     <p className="inquiry-final-note">{inquiryConfig?"提交后，页面会显示您的受理编号。":"仅检查填写的信息，不会发送询价。"}</p>
     {message&&<p className="inquiry-submit-status" role="status">{message}</p>}
    </form>
   </div>
  </section>
 );
}
