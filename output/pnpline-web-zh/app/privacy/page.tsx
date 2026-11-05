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
  <main className="container prose-page"><Link href="/#quote">← 返回 PNPLINE</Link><p className="eyebrow">隐私说明</p><h1>您的询价信息</h1><p>本预览允许您填写商品、运输方式、货量、目的地、IOR 和联系信息。询价提交功能尚未接通，表单信息不会发送至服务器或下载为文件。勾选同意也不会发送您的信息。</p><p>草稿保存在当前浏览器标签页的会话存储中，以便刷新或阅读本说明后恢复填写内容。草稿不会与其他网站共享，也不会发送至 PNPLINE。点击“清空表单”可删除当前标签页的草稿。如浏览器存储不可用，信息仅保留在当前页面。</p><p>点击“返回 PNPLINE”可回到询价表单。如本说明在新标签页打开，可直接关闭该标签页。</p><p>本说明仅供预览。正式收集信息前，需确认实际询价服务及其隐私政策，包括处理目的、接收方、保留期限和联系方式。</p></main>
</>;}
