export type FaqQuestion = { id: string; question: string; answer: string[]; source: string };
export type FaqTopic = { title: string; icon: "box" | "quote" | "clock"; questions: FaqQuestion[] };

export const faqTopics: FaqTopic[] = [
  { title: "服务与交接", icon: "box", questions: [
    { id: "operated", question: "你们的美国仓库是自营的吗？", answer: ["是。PNPLINE 自营美国仓库。咨询时请确认货物接收条件、所需操作和可以提供的仓库信息。"], source: "V4 FAQ 1" },
    { id: "fba-fbm", question: "单件订单和 FBA 补货有什么区别？", answer: ["FBA 补货：暂存或处理货物，再按计划发往亚马逊仓库。", "单件订单：从美国仓拣货、包装并直接发给买家，包括 Amazon FBM 订单。", "如果两种都需要，请分别说明各自的流程。"], source: "V4 FAQ 2 + existing FAQ 2" },
    { id: "partial", question: "能否只用一项服务，或使用自己的货代？", answer: ["请说明需要哪些运输、仓储、履约或单证支持，以及其他服务商负责哪些环节。提供货物信息后，可进一步确认服务范围、收货单证和交接责任。"], source: "V4 FAQ 3 + existing FAQ 1" },
    { id: "special", question: "可以接收特殊产品或处理特殊包装要求吗？", answer: ["请说明产品和存储、贴标或包装要求。收货前需确认能否接收以及是否需要额外操作。"], source: "existing FAQ 4" }
  ] },
  { title: "报价准备", icon: "quote", questions: [
    { id: "uncertain", question: "货量或运输方式未定时，需要提供什么？", answer: ["可以先提供产品和销售计划。已知的起运地、目的地、预计月货量和所需服务请一并提供，未确定的事项可标记为「不确定」。信息进一步明确后再确认方案和费用。"], source: "V4 FAQ 4 + existing FAQ 3" },
    { id: "ior", question: "不确定是否需要 IOR 支持怎么办？", answer: ["在表单的 IOR 支持一栏选择「不确定」，并说明产品和交易情况。咨询时再确认所需单证、可提供的支持和各方责任。"], source: "V4 FAQ 5" },
    { id: "fees", question: "报价包含关税、其他税费和附加费吗？", answer: ["请以具体报价为准。确认报价包含哪些服务费、适用税费、最低收费、长期存储和特殊操作，以及何时会产生附加费。存储及履约费用取决于货物情况和约定的操作要求。"], source: "V4 FAQ 6 + existing FAQ 5" }
  ] },
  { title: "出库与系统", icon: "clock", questions: [
    { id: "timing", question: "货物什么时候可以出库或交付？", answer: ["出库和交付安排取决于产品、收货状态、操作要求、运输方式及目的地。请在方案中确认适用条件和时间。"], source: "V4 FAQ 7" },
    { id: "records", question: "如何查看库存、订单进度和系统对接情况？", answer: ["请说明您需要的记录、销售平台和现有系统，再根据实际情况核对可用功能、账户权限、更新方式及支持的对接方式。"], source: "V4 FAQ 8" }
  ] }
];

export const faqs: [string, string][] = faqTopics.flatMap(topic =>
  topic.questions.map(item => [item.question, item.answer.join(" ")] as [string, string])
);
