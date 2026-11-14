const INQUIRY_TYPES = Object.freeze(['物流询价', '仓储与履约咨询', '进口咨询', '其他咨询']);
const INQUIRY_MAILBOX = 'contact@inquiry.pnpline.cn';
const NOTIFICATION_ROUTE = 'pnpline-inbox-and-sms-v1';
const inquiryIdPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

// The mainland notification template allows up to 35 characters per variable.
// Keep the full UUID as the storage key, and use the same compact receipt everywhere people read it.
function receiptNumber(inquiryId) {
  if (!inquiryIdPattern.test(inquiryId ?? '')) throw new Error('invalid_inquiry_id');
  return inquiryId.replaceAll('-', '').toLowerCase();
}

function composeSms(row) {
  if (!INQUIRY_TYPES.includes(row.inquiryType)) throw new Error('invalid_inquiry_type');
  return { type: row.inquiryType, number: receiptNumber(row.inquiryId) };
}

module.exports = { INQUIRY_TYPES, INQUIRY_MAILBOX, NOTIFICATION_ROUTE, inquiryIdPattern, receiptNumber, composeSms };
