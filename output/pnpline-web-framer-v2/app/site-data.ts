export const siteData = {
  name: "PNPLINE",
  language: "en",
  homeTitle: "PNPLINE | China-to-US freight, warehousing and fulfillment",
  homeDescription: "Plan China-to-US freight, directly operated US warehousing and order fulfillment with PNPLINE.",
  privacyTitle: "Your inquiry information | PNPLINE Privacy Notice",
  privacyDescription: "How this PNPLINE preview stores your inquiry draft in your browser. No inquiry data is sent to a server.",
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
