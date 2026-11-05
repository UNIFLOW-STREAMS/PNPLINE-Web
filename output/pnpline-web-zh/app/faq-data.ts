// Shared by the visible FAQ and server-rendered FAQPage JSON-LD.
// Source: output/faq-concept-20261101/content.json (user-selected concept).
export type FaqQuestion = {id:string;question:string;answer:string[];source:string};
export type FaqTopic = {title:string;icon:"box"|"quote"|"clock";questions:FaqQuestion[]};
export const faqTopics: FaqTopic[] = [
  {
    "title": "服务与交接",
    "icon": "box",
    "questions": [
      {
        "id": "operated",
        "question": "你们的美国仓库是自营的吗？",
        "answer": [
          "是的，PNPLINE 直接运营美国仓库。询价时请确认您的货物接收条件、所需作业及可提供的仓库资料。"
        ],
        "source": "V4 FAQ 1"
      },
      {
        "id": "fba-fbm",
        "question": "一件代发与 FBA 补货有什么区别？",
        "answer": [
          "FBA: 临时存储或作业处理后，按计划发往 Amazon 仓库。",
          "一件代发：从美国仓库拣货、包装并发往买家，也包括 Amazon FBM 订单。",
          "如同时需要两种服务，请分别说明各自的作业需求。"
        ],
        "source": "V4 FAQ 2 + existing FAQ 2"
      },
      {
        "id": "partial",
        "question": "可以只使用一项服务，或使用自己的承运商吗？",
        "answer": [
          "请说明所需的运输、仓储、订单履约或单证支持，以及由其他供应商负责的环节。提供货运信息后，可进一步确认服务范围、收货文件和交接责任。"
        ],
        "source": "V4 FAQ 3 + existing FAQ 1"
      },
      {
        "id": "special",
        "question": "能处理特殊商品或特殊包装要求吗？",
        "answer": [
          "请说明商品及其存储、贴标或包装要求。是否可以接收及所需额外作业，应在到货前确认。"
        ],
        "source": "existing FAQ 4"
      }
    ]
  },
  {
    "title": "询价准备",
    "icon": "quote",
    "questions": [
      {
        "id": "uncertain",
        "question": "货量或运输方式未定时，需要提供什么信息？",
        "answer": [
          "可先说明商品和销售计划，提供已知的起运地、目的地、预计月货量及所需服务。未决定的内容可标注“未定”，待信息明确后再确认方案与费用。"
        ],
        "source": "V4 FAQ 4 + existing FAQ 3"
      },
      {
        "id": "ior",
        "question": "不确定是否需要 IOR 支持怎么办？",
        "answer": [
          "可在表单的 IOR 支持中选择“不确定”，并说明商品和交易情况。咨询时再确认所需文件、可提供的支持及各方责任。"
        ],
        "source": "V4 FAQ 5"
      },
      {
        "id": "fees",
        "question": "报价包含关税、税费和附加费用吗？",
        "answer": [
          "请以具体报价为准，确认包含哪些服务费、适用关税及税费、最低收费、长期存储和特殊作业费用，以及何时产生附加费用。仓储和履约费用取决于货物情况及双方确认的作业要求。"
        ],
        "source": "V4 FAQ 6 + existing FAQ 5"
      }
    ]
  },
  {
    "title": "出库与系统",
    "icon": "clock",
    "questions": [
      {
        "id": "timing",
        "question": "货物何时可以出库或送达？",
        "answer": [
          "出库和配送安排取决于商品、收货状态、作业要求、运输方式及目的地。具体适用条件和时间需在方案中确认。"
        ],
        "source": "V4 FAQ 7"
      },
      {
        "id": "records",
        "question": "如何查看库存、订单进度和系统连接？",
        "answer": [
          "请说明所需记录、销售平台和现有系统，进一步确认适用于您的功能、账号权限、更新方式和支持的连接范围。"
        ],
        "source": "V4 FAQ 8"
      }
    ]
  }
];

export const faqs: [string,string][] = faqTopics.flatMap(topic=>
 topic.questions.map(item=>[item.question,item.answer.join(" ")] as [string,string])
);
