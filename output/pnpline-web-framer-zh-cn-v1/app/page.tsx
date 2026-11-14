import Landing from "./air-landing";
import type { Metadata } from 'next';
import JsonLd from './json-ld';
import {homeStructuredData} from './structured-data';
import {getSiteUrl, siteData} from './site-data';

export function generateMetadata(): Metadata {
  const base = getSiteUrl();
  return {title: siteData.homeTitle, description: siteData.homeDescription,
    ...(base && {alternates: {canonical: base}})};
}

export default function Home() {
  return <>
    <JsonLd data={homeStructuredData()}/>
    <Landing alternateUrl={getSiteUrl(process.env.EN_SITE_URL ?? '') ??
      (getSiteUrl() ? undefined : 'http://127.0.0.1:3212/')}/>
  </>;
}
