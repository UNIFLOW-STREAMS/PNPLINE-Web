import type { Metadata } from "next";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "./globals.css";
export const metadata: Metadata = { title: "PNPLINE — Freight in motion. Fulfillment in focus.", description: "US warehousing and logistics, coordinated around your cargo." };
export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) { return <html lang="en"><body>{children}</body></html>; }

