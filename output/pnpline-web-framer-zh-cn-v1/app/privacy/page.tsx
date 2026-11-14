import Link from "next/link";
import type {Metadata} from 'next';
import JsonLd from '../json-ld';
import {privacyStructuredData} from '../structured-data';
import {getSiteUrl, privacyPath, siteData} from '../site-data';
import {inquiryConfig} from '../inquiry-config';

export function generateMetadata(): Metadata {
  const base = getSiteUrl();
  return {title: siteData.privacyTitle, description: siteData.privacyDescription,
    ...(base && {alternates: {canonical: new URL(privacyPath, base).href}})};
}

export default function Privacy() {return <>
  <JsonLd data={privacyStructuredData()}/>
  <main className="container prose-page"><Link href="/#quote">返回 PNPLINE</Link><h1>您的询价信息</h1>
    {inquiryConfig ? <>
      <p>{inquiryConfig.privacyOperator} 使用您提交的咨询类型、产品类别、运输方式、货量、目的地、IOR 支持需求及联系邮箱处理物流询价，并通过您填写的邮箱与您联系。接收时间及同意的声明版本会与询价一并记录。</p>
      <p>{inquiryConfig.privacyRecipientNotice}</p>
      <p>{inquiryConfig.privacyRetentionNotice} 您可通过 <a href={"mailto:" + inquiryConfig.privacyEmail}>{inquiryConfig.privacyEmail}</a> 咨询本声明，或申请查阅、更正、删除您的信息及撤回同意。</p>
      <p>草稿保存在当前浏览器标签页的会话存储中。点击「清空表单」或提交成功后，会删除当前标签页的草稿。</p>
      <p>声明版本：{inquiryConfig.consentVersion}</p>
    </> : <><p>在此预览版中，您可准备产品、运输方式、货量、目的地、IOR 需求和联系信息。询价提交功能尚未接通。表单信息不会发送到服务器，也不会下载为文件。勾选同意选项不会传输您的信息。</p><p>草稿保存在当前浏览器标签页的会话存储中，刷新或阅读本声明后仍可继续填写。信息不会与其他网站共享，也不会发送给 PNPLINE。选择「清空表单」可删除当前标签页中的草稿。如果浏览器存储不可用，信息仅保留在当前页面。</p><p>选择「返回 PNPLINE」回到询价表单。如果本声明在新标签页中打开，可以直接关闭该标签页。</p><p>本声明仅适用于预览版。正式收集信息前，须确认询价服务及相应隐私政策，包括处理目的、接收方、保留期限和联系方式。</p></>}</main>
</>;}
