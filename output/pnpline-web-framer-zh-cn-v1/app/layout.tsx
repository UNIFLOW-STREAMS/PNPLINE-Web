import type {Metadata} from 'next';
import './air.css';
import './framer.css';
import './service-menu.css';
import './zh-CN.css';
import './responsive-cards.css';
import {isStaticExport, siteData} from './site-data';
export const metadata: Metadata = {
  title: siteData.homeTitle,
  description: siteData.homeDescription,
  ...(isStaticExport && process.env.SITE_INDEXING !== 'allow' && {
    robots: { index: false, follow: false },
  }),
};
export default function Layout({children}:Readonly<{children:React.ReactNode}>){return <html lang={siteData.language}><body>{children}</body></html>;}
