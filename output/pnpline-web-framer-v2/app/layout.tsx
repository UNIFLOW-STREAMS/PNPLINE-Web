import type {Metadata} from 'next';
import './air.css';
import './framer.css';
import './service-menu.css';
import {siteData} from './site-data';
export const metadata:Metadata={title:siteData.homeTitle,description:siteData.homeDescription};
export default function Layout({children}:Readonly<{children:React.ReactNode}>){return <html lang="en"><body>{children}</body></html>;}
