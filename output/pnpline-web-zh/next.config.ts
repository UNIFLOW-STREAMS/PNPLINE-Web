import type { NextConfig } from "next";
const nextConfig: NextConfig = { distDir: process.env.NODE_ENV === "production" ? ".next-production" : ".next", images: { formats: ["image/avif", "image/webp"], qualities: [75,90] }, poweredByHeader: false,
  async headers() { return [{ source: "/assets/video/hero-b-v002-:asset", headers: [
    { key: "Cache-Control", value: "public, max-age=31536000, immutable" }
  ] }]; } };
export default nextConfig;
