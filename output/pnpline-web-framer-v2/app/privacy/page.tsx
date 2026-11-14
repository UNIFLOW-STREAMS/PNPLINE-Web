import Link from "next/link";
import type {Metadata} from 'next';
import JsonLd from '../json-ld';
import {privacyStructuredData} from '../structured-data';
import {getSiteUrl, siteData} from '../site-data';

export function generateMetadata(): Metadata {
  const base = getSiteUrl();
  return {title: siteData.privacyTitle, description: siteData.privacyDescription,
    ...(base && {alternates: {canonical: new URL('/privacy', base).href}})};
}

export default function Privacy() {return <>
  <JsonLd data={privacyStructuredData()}/>
  <main className="container prose-page"><Link href="/#quote">Back to PNPLINE</Link><h1>Your inquiry information</h1><p>This preview lets you prepare product, shipping, volume, destination, IOR and contact details. Inquiry submission is not connected. Form information is not sent to a server or downloaded as a file. Checking the consent box does not transmit your information.</p><p>Your draft is stored in this browser tab’s session storage so you can continue after refreshing or reading this notice. It is not shared with other websites or sent to PNPLINE. Select “Clear form” to remove the draft in the current tab. If browser storage is unavailable, information remains only on the current page.</p><p>Select “Back to PNPLINE” to return to the inquiry form. If this notice opened in a new tab, you can close that tab.</p><p>This notice is for the preview only. Before collecting information, the inquiry service and its privacy policy must be confirmed, including processing purposes, recipients, retention and contact details.</p></main>
</>;}
