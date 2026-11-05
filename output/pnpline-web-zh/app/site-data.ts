export const siteData = {
  name: "PNPLINE",
  language: "zh-CN",
  homeTitle: "PNPLINE｜中国至美国跨境物流与自营海外仓",
  homeDescription: "PNPLINE 提供运输协调、美国自营仓储与订单履约咨询，帮助您规划从中国出货到美国配送的跨境物流需求。",
  privacyTitle: "您的询价信息｜PNPLINE 隐私说明",
  privacyDescription: "了解 PNPLINE 询价预览的浏览器草稿保存方式。本预览不会将表单信息发送至服务器；正式服务及隐私政策尚待确认。",
} as const;

// A deployment origin must be explicitly supplied; never infer it from a request
// header, the English site's domain, or the local development server.
export function getSiteUrl(configured = process.env.SITE_URL): string | undefined {
  if (!configured?.trim()) return undefined;
  const value = configured.trim();
  let parsed: URL;
  try { parsed = new URL(value); } catch {
    throw new Error("SITE_URL must be an absolute HTTP(S) origin.");
  }
  if (!['http:', 'https:'].includes(parsed.protocol) || parsed.username || parsed.password ||
      parsed.pathname !== '/' || value.includes('?') || value.includes('#')) {
    throw new Error("SITE_URL must be an absolute HTTP(S) origin without credentials, a path, query, or fragment.");
  }
  return parsed.origin + '/';
}
