const { receiptNumber } = require('./notification-format.cjs');

const logoUrl = 'https://pnpline.cn/assets/logo.webp';
const font = "Arial, 'Microsoft YaHei', 'PingFang SC', sans-serif";
const entities = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => entities[character]);
}

function detail(label, value) {
  return `<tr>
    <th scope="row" align="left" valign="top" width="118" style="padding:12px 10px 12px 0;border-bottom:1px solid #ebe6dc;font-size:13px;line-height:1.5;font-weight:600;color:#5e625d;">${label}</th>
    <td valign="top" style="padding:12px 0;border-bottom:1px solid #ebe6dc;font-size:15px;line-height:1.5;color:#242826;overflow-wrap:anywhere;word-break:break-word;">${escapeHtml(value || '未填写')}</td>
  </tr>`;
}

function composeMail(row, { test = false } = {}) {
  const title = test ? 'PNPLINE 通知测试' : '收到新的客户咨询';
  const receipt = receiptNumber(row.inquiryId);
  const volume = [row.volume, row.otherUnit || row.unit].filter(Boolean).join(' ');
  const detailRows = [
    ['咨询类型', row.inquiryType],
    ['产品／货物类别', row.cargo],
    ['运输方式', row.shipping],
    ['月货量', volume],
    ['目的地类型', row.destination],
    ['IOR 支持', row.ior],
  ].map(([label, value]) => detail(label, value)).join('');
  const email = escapeHtml(row.email);
  const replyUrl = escapeHtml(`mailto:${encodeURIComponent(row.email).replace('%40', '@')}`);

  return {
    subject: `[PNPLINE] ${test ? '咨询通知测试' : '新客户咨询'} ${receipt}`,
    htmlBody: `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title}</title>
</head>
<body style="margin:0;padding:0;background:#f1eee7;color:#242826;font-family:${font};">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" bgcolor="#f1eee7" style="background:#f1eee7;">
    <tr><td align="center" style="padding:24px 12px;">
      <!--[if mso]><table role="presentation" width="600" cellspacing="0" cellpadding="0"><tr><td><![endif]-->
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" bgcolor="#fffcf7" style="width:100%;max-width:600px;background:#fffcf7;border:1px solid #e4ded2;border-radius:16px;">
        <tr><td style="padding:24px 24px 20px;border-bottom:3px solid #00abe1;">
          <img src="${logoUrl}" width="168" height="45" alt="PNPLINE" style="display:block;width:168px;height:45px;border:0;font-size:20px;font-weight:bold;color:#062c57;">
        </td></tr>
        <tr><td style="padding:24px;">
          <h1 style="margin:0 0 8px;font-size:26px;line-height:1.3;font-weight:700;color:#242826;">${title}</h1>
          <p style="margin:0 0 22px;font-size:14px;line-height:1.55;color:#5e625d;">${test ? '本邮件仅用于验证通知格式，使用模拟数据，无需回复。' : '请核对货运需求，并通过客户提供的邮箱跟进。'}</p>
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" bgcolor="#f4f1ea" style="background:#f4f1ea;border-radius:10px;">
            <tr><td style="padding:16px;">
              <p style="margin:0 0 4px;font-size:13px;line-height:1.5;font-weight:700;color:#006782;">客户联系邮箱</p>
              <a href="${replyUrl}" style="font-size:16px;line-height:1.6;font-weight:600;color:#006782;text-decoration:underline;overflow-wrap:anywhere;word-break:break-word;">${email}</a>
            </td></tr>
          </table>
          <h2 style="margin:24px 0 0;font-size:17px;line-height:1.5;font-weight:700;color:#242826;">货运需求</h2>
          <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;table-layout:fixed;">${detailRows}</table>
        </td></tr>
        <tr><td style="padding:16px 24px 20px;border-top:1px solid #e4ded2;font-size:12px;line-height:1.65;color:#5e625d;overflow-wrap:anywhere;word-break:break-word;">
          <strong>受理编号</strong> ${receipt}<br>
          <strong>接收时间（UTC）</strong> ${escapeHtml(row.receivedAt)}
        </td></tr>
      </table>
      <!--[if mso]></td></tr></table><![endif]-->
    </td></tr>
  </table>
</body>
</html>`,
  };
}

module.exports = { composeMail };

