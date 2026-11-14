import type { MetadataRoute } from 'next';
import { getSiteUrl, isStaticExport } from './site-data';

export const dynamic = 'force-static';

export default function robots(): MetadataRoute.Robots {
  const base = getSiteUrl();
  return {
    rules: { userAgent: '*', allow: '/' },
    ...(base && (!isStaticExport || process.env.SITE_INDEXING === 'allow') && {
      sitemap: new URL('/sitemap.xml', base).href,
    }),
  };
}
