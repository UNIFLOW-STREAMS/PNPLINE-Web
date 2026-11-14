"use client";

import {useLayoutEffect,useRef,useState,type FormEvent} from "react";
import {ArrowRight, Info} from "lucide-react";

const shippingMethods=["Ocean FCL","Ocean LCL","Air","Not sure"];
const destinations=["FBA warehouse","PNPLINE-operated US warehouse","Final consumer","US business or retail receiving point","Not sure"];
const fieldNames:Record<string,string>={cargo:"Product / cargo category",volume:"Monthly volume",unit:"Volume unit",otherUnit:"Other volume unit",email:"Contact email",consent:"Privacy consent"};
const draftKey="pnpline-inquiry-draft-air-v1";

export default function QuoteInquiry(){
 const form=useRef<HTMLFormElement>(null);
 const [unit,setUnit]=useState(""),[volume,setVolume]=useState(""),[errors,setErrors]=useState<Record<string,string>>({}),[message,setMessage]=useState("");
 const [draft,setDraft]=useState<Record<string,string>>({});
 useLayoutEffect(()=>{try{const saved=JSON.parse(sessionStorage.getItem(draftKey)||"{}");if(saved&&typeof saved==="object"&&!Array.isArray(saved)){const values=Object.fromEntries(Object.entries(saved).filter(([,value])=>typeof value==="string")) as Record<string,string>;setDraft(values);setUnit(values.unit||"");setVolume(values.volume||"");}}catch{/* The form remains usable when browser storage is unavailable. */}},[]);
 function changed(event:FormEvent<HTMLFormElement>){
  const target=event.target;if(!(target instanceof HTMLInputElement||target instanceof HTMLSelectElement))return;
  clear(target.name);const values=Object.fromEntries(new FormData(event.currentTarget).entries()) as Record<string,string>;
  setDraft(values);try{sessionStorage.setItem(draftKey,JSON.stringify(values));}catch{/* Storage is optional; never block input. */}
 }
 const uncertain=volume.trim().toLowerCase()==="not sure";
 function focusField(name:string){form.current?.querySelector<HTMLElement>(`[name="${name}"]`)?.focus();}
 function clearDraft(){setDraft({});setUnit("");setVolume("");setErrors({});setMessage("");try{sessionStorage.removeItem(draftKey);}catch{}focusField("cargo");}
 function clear(name:string){setMessage("");setErrors(current=>{const next={...current};delete next[name];if(name==="volume"){delete next.unit;delete next.otherUnit;}if(name==="unit")delete next.otherUnit;return next;});}
 function submit(event:FormEvent<HTMLFormElement>){
  event.preventDefault();const fields=new FormData(event.currentTarget),next:Record<string,string>={};
  const text=(key:string)=>String(fields.get(key)||"").trim();
  if(!text("cargo"))next.cargo="Describe the product or cargo category.";
  const quantity=text("volume");
  if(quantity&&!uncertain){
   if(!/^\d+(?:\.\d+)?$/.test(quantity)||!Number.isFinite(Number(quantity))||Number(quantity)<=0)next.volume="Enter a positive quantity using a decimal point, or enter Not sure.";
   else if(!text("unit"))next.unit="Choose the unit for this quantity.";
   else if(text("unit")==="Other unit"&&!text("otherUnit"))next.otherUnit="Enter the unit used for this quantity.";
  }
  const email=event.currentTarget.elements.namedItem("email") as HTMLInputElement;
  if(!text("email")||!email.validity.valid)next.email="Enter a valid contact email.";
  if(!fields.has("consent"))next.consent="Read the Privacy policy and confirm your consent to check these details.";
  setErrors(next);setMessage("");
  if(Object.keys(next).length){focusField(Object.keys(next)[0]);return;}
  setMessage("Your entries pass the form checks. This preview has not sent an inquiry. You can keep editing your details.");
 }
 const error=(name:string)=>errors[name]?<p id={`inquiry-${name}-error`} className="inquiry-error">{errors[name]}</p>:null;
 const described=(name:string,hint?:string)=>[hint,errors[name]?`inquiry-${name}-error`:null].filter(Boolean).join(" ")||undefined;
 return (
  <section id="quote" className="quote-inquiry" aria-labelledby="inquiry-heading">
   <div className="inquiry-layout">
    <div className="inquiry-intro">
     <span className="inquiry-eyebrow">Shipment planning</span>
     <h2 id="inquiry-heading">Plan your next shipment.</h2>
     <p>Start with the details you know. You can leave optional fields blank or choose “Not sure”.</p>
     <ul className="inquiry-guide">
      <li><span className="inquiry-guide-icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"><path d="m12 3 9 5-9 5-9-5 9-5Zm-9 5v10l9 5 9-5V8M12 13v10M7 5.8l9 5" /></svg></span><span><strong>Your cargo</strong><small>Product and monthly volume</small></span></li>
      <li><span className="inquiry-guide-icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"><circle cx="5" cy="6" r="3" /><circle cx="19" cy="18" r="3" /><path d="M8 6h7a4 4 0 0 1 0 8H9a4 4 0 0 0 0 8h7" /></svg></span><span><strong>Shipping needs</strong><small>Method, destination and IOR</small></span></li>
      <li><span className="inquiry-guide-icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"><rect x="2" y="5" width="20" height="14" rx="3" /><path d="m3 7 9 7 9-7" /></svg></span><span><strong>Contact details</strong><small>Email and privacy consent</small></span></li>
     </ul>
     <div className="inquiry-notice">
      <strong><Info aria-hidden="true" size={18}/> Preview only</strong>
      <p id="inquiry-preview-note">Check your entries here. This form does not send an inquiry to PNPLINE.</p>
     </div>
    </div>
    <form className="inquiry-form" ref={form} noValidate onSubmit={submit} onChange={changed} aria-describedby="inquiry-preview-note">
     {Object.keys(errors).length>0&&<div className="inquiry-error-summary" role="alert"><p>Check the following details:</p><ul>{Object.entries(errors).map(([name,value])=><li key={name}><button type="button" onClick={()=>focusField(name)}>{fieldNames[name]}: {value}</button></li>)}</ul></div>}
     <section className="inquiry-group" aria-labelledby="inquiry-group-1">
      <div className="inquiry-group-heading"><span aria-hidden="true">01</span><h3 id="inquiry-group-1">Your cargo</h3></div>
      <div className="inquiry-field"><div><label htmlFor="inquiry-cargo">Product / cargo category <span className="inquiry-field-meta">Required</span></label><input id="inquiry-cargo" name="cargo" value={draft.cargo||""} onChange={()=>{}} placeholder="e.g. Cotton T-shirts" required maxLength={160} aria-invalid={!!errors.cargo} aria-describedby={described("cargo")}/>{error("cargo")}</div></div>
      <div className="inquiry-field"><div><label htmlFor="inquiry-volume">Monthly volume <span className="inquiry-field-meta">Optional</span></label><div className="inquiry-volume"><input id="inquiry-volume" name="volume" placeholder="e.g. 20" value={volume} onChange={e=>setVolume(e.target.value)} maxLength={32} aria-invalid={!!errors.volume} aria-describedby={described("volume","inquiry-volume-hint")}/><select name="unit" aria-label="Monthly volume unit" value={uncertain?"":unit} onChange={e=>setUnit(e.target.value)} disabled={uncertain} aria-invalid={!!errors.unit} aria-describedby={described("unit")}><option value="">{uncertain?"Unit not needed":"Select unit"}</option>{["CBM","kg","orders","Other unit"].map(option=><option key={option}>{option}</option>)}</select>{unit==="Other unit"&&!uncertain&&<input className="inquiry-other-unit" name="otherUnit" value={draft.otherUnit||""} onChange={()=>{}} aria-label="Other volume unit" placeholder="Enter your unit" maxLength={40} aria-invalid={!!errors.otherUnit} aria-describedby={described("otherUnit")}/>}</div><p className="inquiry-field-hint" id="inquiry-volume-hint">Not sure yet? Leave this blank.</p>{error("volume")}{error("unit")}{error("otherUnit")}</div></div>
     </section>
     <section className="inquiry-group" aria-labelledby="inquiry-group-2">
      <div className="inquiry-group-heading"><span aria-hidden="true">02</span><h3 id="inquiry-group-2">Shipping needs</h3></div>
      <fieldset className="inquiry-field"><legend>Shipping method <span className="inquiry-field-meta">Optional</span></legend><div className="inquiry-segments">{shippingMethods.map(method=><label key={method}><input type="radio" name="shipping" value={method} checked={draft.shipping===method} onChange={()=>{}}/><span>{method}</span></label>)}</div></fieldset>
      <div className="inquiry-field"><div><label htmlFor="inquiry-destination">Destination type <span className="inquiry-field-meta">Optional</span></label><select id="inquiry-destination" name="destination" value={draft.destination||""} onChange={()=>{}}><option value="">Select destination</option>{destinations.map(option=><option key={option}>{option}</option>)}</select></div></div>
      <fieldset className="inquiry-field"><legend>Importer of record (IOR) support <span className="inquiry-field-meta">Optional</span></legend>
     <details className="inquiry-ior-help"><summary>What does IOR mean?</summary><p>IOR means importer of record. Choose “Not sure” if you have not confirmed who will take this role.</p></details><div className="inquiry-radios">{["Needed","Not needed","Not sure"].map(option=><label key={option}><input type="radio" name="ior" value={option} checked={draft.ior===option} onChange={()=>{}}/><span>{option}</span></label>)}</div></fieldset>
     </section>
     <section className="inquiry-group inquiry-contact" aria-labelledby="inquiry-group-3">
      <div className="inquiry-group-heading"><span aria-hidden="true">03</span><h3 id="inquiry-group-3">Contact details</h3></div>
      <div className="inquiry-field"><div><label htmlFor="inquiry-email">Contact email <span className="inquiry-field-meta">Required</span></label><input id="inquiry-email" name="email" value={draft.email||""} onChange={()=>{}} type="email" autoComplete="email" placeholder="you@company.com" required maxLength={254} aria-invalid={!!errors.email} aria-describedby={described("email")}/>{error("email")}</div></div>
      <div className="inquiry-consent"><input type="checkbox" id="inquiry-consent" name="consent" checked={draft.consent==="on"} onChange={()=>{}} required aria-invalid={!!errors.consent} aria-describedby={described("consent")}/><label htmlFor="inquiry-consent">I have read the <a href="/privacy/" target="_blank" rel="noopener noreferrer">Privacy policy<span className="sr-only"> (opens in a new tab)</span></a> and agree to the use of these details for this inquiry. <span className="inquiry-field-meta">Required</span></label></div>{error("consent")}
     </section>
     <div className="inquiry-actions">
      <button type="button" onClick={clearDraft} className="inquiry-clear">Clear form</button>
      <button className="inquiry-submit" type="submit">Check inquiry details <ArrowRight aria-hidden="true"/></button>
     </div>
     <p className="inquiry-final-note">This checks your entries only. No inquiry will be sent.</p>
     {message&&<p className="inquiry-submit-status" role="status">{message}</p>}
    </form>
   </div>
  </section>
 );
}
