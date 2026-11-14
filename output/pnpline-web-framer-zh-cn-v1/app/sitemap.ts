import type { MetadataRoute } from 'next';
import { getSiteUrl, privacyPath } from './site-data';

export const dynamic = 'force-static';

export default function sitemap(): MetadataRoute.Sitemap {
  const base = getSiteUrl();
  if (!base) return [];
  return ['/', privacyPath].map(path => ({ url: new URL(path, base).href }));
}
