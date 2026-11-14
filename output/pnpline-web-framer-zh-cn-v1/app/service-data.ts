export const services = [
  { title: "跨境运输协调", copy: "规划货物起运地、目的地及各环节的交接。", detail: "提供起运地、货物信息和美国目的地，我们将沟通运输路线和各环节的责任分工。", icon: "ship", image: "freight" ,category:"运输",region:"中国 → 美国",countries:["中国", "美国"],scope:["整箱", "拼箱", "空运"],cta:"了解运输服务"},
  { title: "美国自营仓储", copy: "由 PNPLINE 自营美国仓接收和存储您的库存。", detail: "明确入库形式、存储要求和您业务所需的库存操作。", icon: "warehouse", image: "warehouse" ,category:"仓储",region:"美国 · 自营仓",countries:["美国"],scope:["收货", "存储", "库存管理"],cta:"了解仓储服务"},
  { title: "订单履约", copy: "美国海外仓一件代发、B2B、FBA补货。", detail: "启动前确认订单类型、贴标、包装和补货要求。", icon: "box", image: "storage" ,category:"履约",region:"美国仓 · 订单出库",countries:["美国"],scope:["拣货", "包装", "贴标"],cta:"了解履约服务"},
  { title: "美国尾程配送", copy: "实现货物最终交付", detail: "根据目的地和货物情况，规划包裹配送、平台补货或批量交付。", icon: "truck", image: "delivery" ,category:"配送",region:"美国境内 · 最终交付",countries:["美国"],scope:["包裹配送", "渠道补货", "批量交付"],cta:"了解配送服务"}
];

export const serviceTargets = ['freight-options', 'warehouse', 'fulfillment-options', 'b2b'] as const;
