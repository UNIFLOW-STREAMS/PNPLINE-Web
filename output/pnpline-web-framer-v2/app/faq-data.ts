// Shared by the visible FAQ and server-rendered FAQPage JSON-LD.
// Source: output/faq-concept-20261101/content.json (user-selected concept).
export type FaqQuestion = {id:string;question:string;answer:string[];source:string};
export type FaqTopic = {title:string;icon:"box"|"quote"|"clock";questions:FaqQuestion[]};
export const faqTopics: FaqTopic[] = [
  {
    "title": "Services & handover",
    "icon": "box",
    "questions": [
      {
        "id": "operated",
        "question": "Are your US warehouses directly operated?",
        "answer": [
          "Yes. PNPLINE directly operates US warehouses. Confirm the acceptance conditions for your goods, the work required and the warehouse information available when you inquire."
        ],
        "source": "V4 FAQ 1"
      },
      {
        "id": "fba-fbm",
        "question": "How do individual orders differ from FBA replenishment?",
        "answer": [
          "FBA: temporary storage or handling, followed by planned dispatch to Amazon warehouses.",
          "Individual orders: pick, pack and dispatch from the US warehouse to buyers, including Amazon FBM orders.",
          "If you need both, describe each flow separately."
        ],
        "source": "V4 FAQ 2 + existing FAQ 2"
      },
      {
        "id": "partial",
        "question": "Can I use only one service or my own freight provider?",
        "answer": [
          "Tell us which transport, warehousing, fulfillment or documentation support you need and which parts another provider handles. Share the shipment details so scope, receiving documents and handover responsibilities can be confirmed."
        ],
        "source": "V4 FAQ 3 + existing FAQ 1"
      },
      {
        "id": "special",
        "question": "Can you handle special products or packing requirements?",
        "answer": [
          "Describe the product and any storage, labeling or packing requirements. Suitability and additional handling need to be confirmed before receiving goods."
        ],
        "source": "existing FAQ 4"
      }
    ]
  },
  {
    "title": "Quote preparation",
    "icon": "quote",
    "questions": [
      {
        "id": "uncertain",
        "question": "What should I share if volume or shipping method is undecided?",
        "answer": [
          "Start with your product and sales plan. Share the origin, destination, expected monthly volume and services needed where known. Mark undecided details as not sure. The plan and charges are confirmed once the information is clearer."
        ],
        "source": "V4 FAQ 4 + existing FAQ 3"
      },
      {
        "id": "ior",
        "question": "What if I am not sure whether I need IOR support?",
        "answer": [
          "Choose Not sure under IOR support in the form and describe your product and transaction. Confirm the documents needed, available support and each party’s responsibilities during the inquiry."
        ],
        "source": "V4 FAQ 5"
      },
      {
        "id": "fees",
        "question": "Does the quote include duties, taxes and additional charges?",
        "answer": [
          "Check the specific quotation. Confirm which service fees, applicable duties and taxes, minimum charges, long-term storage and special work are included, and when additional charges arise. Storage and fulfillment charges depend on the cargo profile and the agreed operating requirements."
        ],
        "source": "V4 FAQ 6 + existing FAQ 5"
      }
    ]
  },
  {
    "title": "Dispatch & systems",
    "icon": "clock",
    "questions": [
      {
        "id": "timing",
        "question": "When can goods be dispatched or delivered?",
        "answer": [
          "Dispatch and delivery arrangements depend on the product, receiving status, handling requirements, transport method and destination. Confirm the applicable conditions and timing in the plan."
        ],
        "source": "V4 FAQ 7"
      },
      {
        "id": "records",
        "question": "How can I review inventory, order progress and system connections?",
        "answer": [
          "Describe the records you need, your sales platform and existing system. Review the available functions, account permissions, update methods and supported connections for your setup."
        ],
        "source": "V4 FAQ 8"
      }
    ]
  }
];

export const faqs: [string,string][] = faqTopics.flatMap(topic=>
 topic.questions.map(item=>[item.question,item.answer.join(" ")] as [string,string])
);
