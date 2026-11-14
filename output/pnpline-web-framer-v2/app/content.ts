// Content copied from the preserved English site. Only component icon references are omitted.
export const freightModes = [
    { name: "FCL", caption: "A container for your cargo", icon: "container", tag: "Consolidated volume", copy: "Plan a full-container move around your cargo volume, loading plan and US receiving window.", checks: ["Container size, loading method and gross weight", "Origin pickup, port handovers and delivery terms", "US drayage, unloading needs and receiving slot"] },
    { name: "LCL", caption: "Share space, keep flexibility", icon: "shared", tag: "Smaller ocean shipments", copy: "Use shared ocean capacity when your shipment does not need a full container. Map the consolidation handovers.", checks: ["Carton or pallet dimensions, volume and stackability", "Consolidation and deconsolidation locations", "Origin and destination handling charges"] },
    { name: "Air freight", caption: "Plan around the deadline", icon: "plane", tag: "Time-sensitive cargo", copy: "Discuss air freight for time-sensitive or high-value cargo, with the product profile and final delivery in view.", checks: ["Ready date, delivery deadline and routing options", "Actual and dimensional weight for quoting", "Batteries, restricted goods and required documents"] }
];
export const comparison = [
    ["Typical fit", "Regular bulk replenishment", "Smaller or mixed shipments", "Urgent or high-value goods"],
    ["Capacity planning", "Container & load plan", "Volume & consolidation", "Weight & dimensions"],
    ["Key handover", "Port → drayage → warehouse", "Consolidation → US handling", "Airport → US delivery"],
    ["Quote inputs", "Container size, weight, route", "CBM, packaging, local charges", "Chargeable weight, cargo type"]
];
export const outboundFlows = [
  {
    name: "Single orders",
    hint: "Direct to customer",
    title: "One order. Ready for its customer.",
    copy: "Define the pick, pack and dispatch rules for individual customer orders.",
    art: "fulfillment",
    alt: "Packing workstation with conveyor, scanner and label printer.",
    steps: ["Order received", "Pick and verify", "Pack and label", "Parcel handover"],
    input: ["SKU mapping","Order format","Packing rules"],
    output: ["Parcel reference","Dispatch status","Exceptions"],
  },
  {
    name: "FBA replenishment",
    hint: "Amazon destination",
    title: "Inventory, ready for its next destination.",
    copy: "Plan temporary storage, labeling and staged replenishment for your Amazon destination.",
    art: "warehouse",
    alt: "Warehouse racks and pallet handling area.",
    steps: ["Shipment plan", "Prep and labels", "Carton / pallet", "Delivery booking"],
    input: ["Shipment plan","SKU labels","Carton or pallet requirements"],
    output: ["Shipment reference","Delivery plan","Handover record"],
  },
];
export const channels = [
  {
    "name": "Amazon sellers",
    "platform": "Amazon FBA / FBM",
    "intro": "Two fulfillment routes, each with its own preparation.",
    "items": [
      {
        "title": "FBA replenishment",
        "copy": "Storage, labeling and staged dispatch to Amazon warehouses."
      },
      {
        "title": "FBM orders",
        "copy": "Pick, pack and dispatch from the US warehouse to buyers."
      },
      {
        "title": "Handling requirements",
        "copy": "Confirm packing, labels and release rules."
      }
    ],
    "cta": "Plan Amazon fulfillment",
    "icon": "marketplace"
  },
  {
    "name": "Online stores",
    "platform": "Shopify / TikTok Shop",
    "intro": "Plan orders, returns and the connections your store needs.",
    "items": [
      {
        "title": "Order preparation",
        "copy": "Inventory readiness, picking, packing and US delivery."
      },
      {
        "title": "Returns handover",
        "copy": "Confirm returns requirements and handling scope."
      },
      {
        "title": "System requirements",
        "copy": "Confirm available platform connections and functions."
      }
    ],
    "cta": "Discuss store fulfillment",
    "icon": "online-store"
  },
  {
    "name": "Factories & B2B",
    "platform": "Manufacturers · Trading companies",
    "intro": "Coordinate bulk shipments, inventory and retail delivery.",
    "items": [
      {
        "title": "Shipments & inventory",
        "copy": "Plan transport, receiving and stock arrangements."
      },
      {
        "title": "Business & retail delivery",
        "copy": "Share destination and retail channel requirements."
      },
      {
        "title": "Receiving requirements",
        "copy": "Confirm packaging, labels and delivery appointments."
      }
    ],
    "cta": "Plan B2B delivery",
    "icon": "business"
  }
];
export const phases = [
    { title: "Share the product", summary: "Start with the cargo and the transaction.", heading: "Good information makes a better starting point.", copy: "Tell us what you ship, where it comes from and who it is for. Bring what you know. We’ll identify the questions to discuss together.", inputs: ["Product description, materials and intended use", "Country of origin and transaction details", "US destination and parties already appointed"], label: "PRODUCT & TRANSACTION", icon: "ior" },
    { title: "Documents, HS & product rules", summary: "Connect the details with the right paperwork.", heading: "Gather the documents for your shipment.", copy: "Review the product profile and shipment documents with your appointed broker. Clarify classification and product-specific requirements before booking.", inputs: ["Commercial invoice and packing information", "Transport document and shipment references", "Classification and product-specific questions"], label: "DOCUMENTS & REQUIREMENTS", icon: "document" },
    { title: "Define responsibilities", summary: "Agree who provides, reviews and hands over.", heading: "A clear handover starts with clear ownership.", copy: "Identify the importer of record, customs broker and duty payer. Agree the scope, contacts and exception handling before the shipment moves.", inputs: ["Importer of record and appointed broker", "Document owners, duty payer and contacts", "Release, receiving and exception handovers"], label: "PEOPLE & HANDOVERS", icon: "review" }
];
export const questions = [
    { name: "Declaration documents", icon: "document", heading: "Bring the shipment story together.", copy: "Align the invoice, packing details and transport information with the actual shipment. Confirm the entry documents with your appointed broker.", fields: ["Commercial invoice", "Packing information", "Transport document"] },
    { name: "HS / US HTS", icon: "classification", heading: "Start with what the product is.", copy: "Share materials, intended use, specifications and origin so classification can be reviewed with your appointed customs broker.", fields: ["Materials & composition", "Intended use", "Specifications & origin"] },
    { name: "FDA / FCC", icon: "review", heading: "Ask the product-specific questions early.", copy: "Describe the product and its intended use. Review whether FDA requirements or FCC equipment authorization apply and what evidence is needed.", fields: ["Product category", "Intended use", "Relevant technical evidence"] }
];
export const roles = [
    ["Seller / manufacturer", "Product, value and origin information"],
    ["Importer of record", "Entry responsibilities and duty arrangements"],
    ["Appointed broker", "Entry review and agreed filing scope"],
    ["PNPLINE / receiving team", "Agreed logistics scope and warehouse handover"]
];
export const stages = [
    { name: "Receiving", label: "Inbound checks", title: "Start with a clear handover.", copy: "Align inbound format, receiving checks and shipment documents before your goods arrive.", x: 20, y: 56.9 },
    { name: "Inventory", label: "Storage requirements", title: "Know what your operation needs.", copy: "Review cargo dimensions, storage methods, inventory records and how long goods will be stored.", x: 45.75, y: 60.7 },
    { name: "Dispatch", label: "Order preparation", title: "Prepare the next move.", copy: "Confirm order preparation, packing and delivery requirements for each outbound flow.", x: 65.85, y: 54.7 }
];
export const steps = [
    { title: "Share requirements", summary: "Product, shipping method, volume, destination and IOR needs.", image: "shipping-brief", alt: "Shipping Brief clipboard, globe and shipping carton.", label: "YOUR REQUIREMENTS", heading: "Start with what you know.", detail: "Share the shipment information available. Mark undecided items as not sure.", items: [
            { title: "Product & volume", copy: "Describe your goods and expected quantity, with units." },
            { title: "Shipping method", copy: "FCL, LCL, air freight or not sure." },
            { title: "Destination", copy: "Tell us where the shipment needs to go." },
            { title: "IOR needs", copy: "Indicate whether IOR support is needed or unclear." }
        ] },
    { title: "Review conditions", summary: "Acceptance, documents, handling, delivery and responsibilities.", image: "requirements-review", alt: "Requirements Checklist folder and clipboard beside a warehouse and forklift.", label: "CONDITIONS REVIEW", heading: "Agree the scope and handovers.", detail: "Confirm the acceptance conditions and each party’s responsibilities.", items: [
            { title: "Acceptance & documents", copy: "Confirm the cargo scope and information required." },
            { title: "Warehouse handling", copy: "Review receiving, storage, picking and packing needs." },
            { title: "Delivery requirements", copy: "Confirm the destination and receiving conditions." },
            { title: "Responsibilities", copy: "Identify who handles each part and handover." }
        ] },
    { title: "Confirm the quote", summary: "Billing units, included items, additional charges and execution conditions.", image: "quotation", alt: "Open Quotation document on a cyan folder with a pen.", label: "QUOTE REVIEW", heading: "Know what the quote includes.", detail: "Confirm these items before arranging the next steps.", items: [
            { title: "Billing units", copy: "How the shipment is calculated and what units are used." },
            { title: "Included services", copy: "Which services, documents and handling are covered." },
            { title: "Additional charges", copy: "Potential extra costs and when they may apply." },
            { title: "Service terms", copy: "Terms, responsibilities and what happens after confirmation." }
        ] }
];
export const costAreas = [
    { name: "Freight", confirmation: "FCL, LCL or air; route, volume and weight", basis: "Shipment" },
    { name: "Receiving", confirmation: "Carton or pallet format and receiving checks", basis: "Pallet / carton" },
    { name: "Storage", confirmation: "Storage method, space and duration", basis: "Space / duration" },
    { name: "Fulfillment", confirmation: "Picking, packing, labels, inspection and returns", basis: "Order / item" },
    { name: "Delivery", confirmation: "Destination, parcel or pallet, service and appointments", basis: "Parcel / shipment" }
];
export const importItems = [
    { title: "Customs handling", copy: "Confirm the service scope and handling responsibilities." },
    { title: "IOR requirements", copy: "Confirm whether IOR support is needed and what is included." },
    { title: "Service charges", copy: "Ask for the agreed service fees to be listed separately." },
    { title: "Applicable duties & taxes", copy: "Confirm applicable amounts and whether they are included." }
];
export const conditions = [
    { title: "Minimum charges", copy: "Confirm the billing unit and any minimum charge." },
    { title: "Long-term storage", copy: "Confirm the storage period, charging basis and when extra charges begin." },
    { title: "Special handling", copy: "Confirm charges for special packing, labeling, inspection and returns work." }
];
export const inputs = [
    { name: "Sales platforms", description: "Platform, store region and SKU mapping" },
    { name: "Your ERP", description: "Order fields and inventory source of truth" },
    { name: "API requirements", description: "Documentation, authentication and field mapping" }
];
export const outputs = [
    { name: "Inventory queries", description: "Stock information you need to see" },
    { name: "Receiving records", description: "Inbound information to review" },
    { name: "Orders & dispatch", description: "Preparation and outbound progress" }
];
