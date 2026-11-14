import type { NextConfig } from 'next';
const staticExport = process.env.PNPLINE_STATIC_EXPORT === '1';

if (staticExport && !process.env.SITE_URL?.trim()) {
  throw new Error('SITE_URL is required for a static deployment build.');
}

const config: NextConfig = staticExport ? {
  output: 'export',
  trailingSlash: true,
  poweredByHeader: false,
  images: { unoptimized: true },
} : {
  distDir: process.env.NODE_ENV === 'production' ? '.next-air' : '.next',
  poweredByHeader: false,
  images: { formats: ['image/avif','image/webp'] },
};
export default config;
