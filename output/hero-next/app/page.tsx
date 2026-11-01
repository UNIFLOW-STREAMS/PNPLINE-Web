"use client";
import { useRef, useState, type FormEvent } from "react";
import { ArrowRight, ArrowUpRight, X } from "lucide-react";

const stages = ["Origin", "Freight", "Warehouse", "Delivery"];
const services = [
  ["Warehousing & fulfillment", "Receiving, storage, picking, packing and dispatch from the US warehouse."],
  ["China shipping & US transport", "Discuss FCL, LCL or air freight, your route, and delivery requirements."],
  ["IOR & import consultation", "Confirm documents, applicable requirements and handoff responsibilities."],
  ["Inventory & systems", "Review the stock records and integration support your operation needs."],
];
export default function Home() {
  const [stage, setStage] = useState(0);
  const [panel, setPanel] = useState<"quote" | "services">("services");
  const dialog = useRef<HTMLDialogElement>(null);
  const [prepared, setPrepared] = useState(false);
  function openPanel(next: "quote" | "services") { setPanel(next); setPrepared(false); dialog.current?.showModal(); }
  function prepareInquiry(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const contents = ["PNPLINE — Logistics inquiry", ...Array.from(data.entries()).map(([key, value]) => key + ": " + value)].join("\n");
    const url = URL.createObjectURL(new Blob([contents], {type: "text/plain;charset=utf-8"}));
    const link = document.createElement("a"); link.href = url; link.download = "pnpline-inquiry.txt"; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000); setPrepared(true);
  }
  return <main>
    <section className="hero relative isolate overflow-hidden" aria-labelledby="hero-heading">
      <picture className="hero-art absolute inset-0 -z-10 block">
        <source media="(max-width: 767px)" srcSet="/images/hero-mobile.png" />
        <img src="/images/hero-desktop.png" alt="" fetchPriority="high" width="1672" height="941" className="h-full w-full object-cover" />
      </picture>
      <div className="hero-container relative mx-auto h-full">
        <div className="hero-copy">
          <p className="route flex items-center"><span>China</span><ArrowRight aria-hidden="true" className="route-arrow" strokeWidth={1.4}/><span>United States</span></p>
          <h1 id="hero-heading" className="hero-heading font-bold"><span className="block">Freight in motion.</span><span className="block"><span className="text-[#00abe1]">Fulfillment</span> in focus.</span></h1>
          <p className="hero-description text-[#58616e]">US warehousing and logistics,<br className="desktop-break"/> coordinated around your cargo.</p>
          <div className="hero-actions flex items-center">
            <button className="quote-button inline-flex items-center justify-center gap-3 bg-[#080a0a] text-white transition-colors hover:bg-[#26333b] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[#00abe1]" onClick={() => openPanel("quote")}>Get a Quote <ArrowUpRight aria-hidden="true" size={23} strokeWidth={1.5}/></button>
            <button className="services-button text-[#00abe1] transition-colors hover:text-[#007fa9] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[#00abe1]" onClick={() => openPanel("services")}>Explore Services</button>
          </div>
        </div>
        <div className="hero-bottom flex items-end justify-between">
          <nav className="journey" aria-label="Illustrative logistics stages"><ol className="flex">
            {stages.map((name, index) => <li key={name} className="relative flex-1"><button className={"stage-button relative flex flex-col items-center " + (index === stage ? "is-active" : "")} onClick={() => setStage(index)} aria-current={index === stage ? "step" : undefined}><span className="stage-dot" aria-hidden="true"/><span>{name}</span></button></li>)}
          </ol></nav>
          <p className="illustration-note text-[#58616e]">Illustrative logistics journey.</p>
        </div>
      </div>
    </section>
    <dialog ref={dialog} className="detail-dialog" aria-labelledby="dialog-title" onClick={(event) => {if(event.target === event.currentTarget) dialog.current?.close();}}>
      <div className="dialog-inner">
        <button className="dialog-close" aria-label="Close dialog" onClick={() => dialog.current?.close()}><X size={24}/></button>
        <p className="text-sm tracking-[0.15em] text-[#007fa9]">PNPLINE</p>
        <h2 id="dialog-title" className="mt-3 mb-6 text-3xl font-semibold">{panel === "services" ? "Logistics, around your cargo." : "Tell us about your shipment."}</h2>
        {panel === "services" ? <><div className="divide-y divide-slate-200">{services.map(([title, description]) => <article key={title} className="py-4"><h3 className="font-semibold">{title}</h3><p className="mt-2 text-slate-600">{description}</p></article>)}</div><button className="mt-6 bg-[#080a0a] px-6 py-3 text-white" onClick={() => openPanel("quote")}>Get a Quote</button></> :
          <form onSubmit={prepareInquiry} className="inquiry-form">
            <p className="mb-5 text-sm text-slate-600">Prepare a request to save locally. This preview does not send inquiries.</p>
            <div className="grid gap-4 sm:grid-cols-2">
              <label>Product category<input name="Product" placeholder="Product or category" required/></label>
              <label>Shipping method<select name="Shipping method" defaultValue="Undecided"><option>Undecided</option><option>FCL</option><option>LCL</option><option>Air</option></select></label>
              <label>Monthly volume<input name="Monthly volume" placeholder="Quantity and unit, or undecided"/></label>
              <label>Destination<input name="Destination" placeholder="City, warehouse or recipient"/></label>
              <label>IOR support<select name="IOR support" defaultValue="Not sure"><option>Not sure</option><option>Yes</option><option>No</option></select></label>
              <label>Contact email<input name="Email" type="email" placeholder="name@company.com" required/></label>
            </div>
            <button type="submit" className="mt-6 bg-[#080a0a] px-6 py-3 text-white">Save inquiry draft <ArrowRight className="ml-2 inline" size={18}/></button>
            {prepared && <p role="status" className="mt-4 text-sm text-[#007fa9]">Your inquiry draft has been prepared for download.</p>}
          </form>}
      </div>
    </dialog>
  </main>;
}

