import {inquiryConfig} from "./inquiry-config";

export const siteData = {
  name: "PNPLINE",
  language: "zh-CN",
  homeTitle: "PNPLINE｜中美跨境运输、美国自营仓储与订单履约",
  homeDescription: "与 PNPLINE 一起规划从中国到美国的运输、美国自营仓储和订单履约。",
  privacyTitle: "您的询价信息｜PNPLINE 隐私声明",
  privacyDescription: inquiryConfig ? "了解 PNPLINE 如何处理询价信息及如何行使您的个人信息权利。" : "了解 PNPLINE 预览版如何在浏览器中保存询价草稿。询价信息不会发送到服务器。",
} as const;

export const isStaticExport = process.env.PNPLINE_STATIC_EXPORT === '1';
export const privacyPath = isStaticExport ? '/privacy/' : '/privacy';

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
