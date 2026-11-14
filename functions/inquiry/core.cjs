const { createHash, randomUUID } = require('node:crypto');

const { composeMail } = require('./inquiry-email.cjs');
const { composeSms, INQUIRY_TYPES, NOTIFICATION_ROUTE, inquiryIdPattern, receiptNumber } = require('./notification-format.cjs');

const MAX_BODY = 16 * 1024;
const RETRY_MINUTES = [1, 5, 30];
const LEASE_MS = 3 * 60 * 1000;
const options = {
  inquiryType: INQUIRY_TYPES,
  shipping: ['海运整柜', '海运拼箱', '空运', '不确定'],
  unit: ['CBM', 'kg', '订单', '其他单位'],
  destination: ['FBA 仓库', 'PNPLINE 美国自营仓库', '最终消费者', '美国企业或零售收货点', '不确定'],
  ior: ['需要', '不需要', '不确定'],
};
const unknown = new Set(['不确定', '未定', '待定', 'not sure']);
const isEmail = (value) => value.length <= 254 && /^[^\s@<>]+@[^\s@<>.]+(?:\.[^\s@<>.]+)+$/.test(value);
const asIso = (time) => new Date(time).toISOString();

function validate(body, consentVersion) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) return { fields: ['cargo'] };
  const fields = new Set();
  function read(name, max, required = false) {
    const raw = body[name];
    if (raw === undefined && !required) return '';
    if (typeof raw !== 'string' || raw.length > max || /[\x00-\x1f\x7f]/.test(raw) || (required && !raw.trim())) {
      fields.add(name);
      return '';
    }
    return raw.trim();
  }
  function choice(name) {
    const value = read(name, 40);
    if (value && !options[name].includes(value)) fields.add(name);
    return value;
  }
  const inquiryType = choice('inquiryType') || INQUIRY_TYPES[0];
  const cargo = read('cargo', 160, true);
  const shipping = choice('shipping');
  let volume = read('volume', 32);
  let unit = choice('unit');
  let otherUnit = read('otherUnit', 40);
  const destination = choice('destination');
  const ior = choice('ior');
  const email = read('email', 254, true);
  if (!isEmail(email)) fields.add('email');
  if (body.consent !== true || body.consentVersion !== consentVersion) fields.add('consent');
  if (body.website !== undefined && body.website !== '') fields.add('website');
  if (unknown.has(volume.toLowerCase())) volume = '不确定';
  if (!volume || volume === '不确定') unit = otherUnit = '';
  else {
    if (!/^\d+(?:\.\d+)?$/.test(volume) || !Number.isFinite(Number(volume)) || Number(volume) <= 0) fields.add('volume');
    if (!unit) fields.add('unit');
    if (unit === '其他单位' && !otherUnit) fields.add('otherUnit');
    if (unit !== '其他单位') otherUnit = '';
  }
  return fields.size ? { fields: [...fields] } : {
    payload: { inquiryType, cargo, shipping, volume, unit, otherUnit, destination, ior, email, consentVersion },
  };
}

function expiryAfterYear(iso) {
  const date = new Date(iso);
  const month = date.getUTCMonth();
  date.setUTCFullYear(date.getUTCFullYear() + 1);
  if (date.getUTCMonth() !== month) date.setUTCDate(0);
  return date.toISOString();
}

async function accept({ id, body, consentVersion, store, now = Date.now }) {
  if (!inquiryIdPattern.test(id ?? '')) return { status: 400, body: { code: 'invalid_idempotency_key' } };
  const { fields, payload } = validate(body, consentVersion);
  if (fields) return { status: 422, body: { code: 'invalid_fields', fields } };
  const inquiryId = id.toLowerCase();
  const receivedAt = asIso(now());
  const payloadHash = createHash('sha256').update(JSON.stringify(payload)).digest('hex');
  const created = await store.insert(inquiryId, {
    ...payload, receivedAt, consentAcceptedAt: receivedAt, notificationRoute: NOTIFICATION_ROUTE, payloadHash, lastConsultedAt: receivedAt,
    deleteAfter: expiryAfterYear(receivedAt),
    notificationStatus: 'pending', notificationAttempts: 0,
    notificationRevision: randomUUID(), nextNotificationAt: receivedAt,
    smsStatus: 'pending', smsAttempts: 0, smsRevision: randomUUID(), nextSmsAt: receivedAt,
  });
  if (!created) {
    const existing = await store.hash(inquiryId);
    if (!existing) throw new Error('inquiry_not_readable');
    if (existing !== payloadHash) return { status: 409, body: { code: 'idempotency_conflict' } };
  }
  return { status: created ? 201 : 200, body: { inquiryId, receiptNumber: receiptNumber(inquiryId), status: 'accepted' } };
}

const CHANNELS = {
  mail: { status: 'notificationStatus', attempts: 'notificationAttempts', revision: 'notificationRevision', due: 'nextNotificationAt', compose: composeMail },
  sms: { status: 'smsStatus', attempts: 'smsAttempts', revision: 'smsRevision', due: 'nextSmsAt', compose: composeSms },
};

async function notifyOne({ row, store, send, channel = 'mail', now = Date.now }) {
  const keys = CHANNELS[channel];
  const time = now();
  if (!keys || row.notificationRoute !== NOTIFICATION_ROUTE ||
      !['pending', 'sending'].includes(row[keys.status]) || !row[keys.due] || row[keys.due] > asIso(time)) return 'skipped';
  const attempts = row[keys.attempts];
  const update = (revision, status, count, next, nextRevision = randomUUID()) =>
    store.transition(row.inquiryId, revision, {
      [keys.status]: status, [keys.attempts]: count, [keys.revision]: nextRevision, [keys.due]: next,
    }, keys.revision);
  if (!row.consentVersion || !row.consentAcceptedAt || attempts > RETRY_MINUTES.length) {
    return await update(row[keys.revision], 'failed', attempts, '') ? 'failed' : 'skipped';
  }
  const lease = randomUUID();
  const claimed = await update(row[keys.revision], 'sending', attempts + 1, asIso(time + LEASE_MS), lease);
  if (!claimed) return 'skipped';
  let sent = false;
  try {
    await send(keys.compose(row));
    sent = true;
  } catch {
    // Provider errors can contain message content. Persist only the retry state.
  }
  const delay = RETRY_MINUTES[attempts];
  const status = sent ? 'sent' : delay ? 'pending' : 'failed';
  const updated = await update(lease, status, attempts + 1, status === 'pending' ? asIso(now() + delay * 60_000) : '');
  return updated ? status : 'skipped';
}

module.exports = { accept, isEmail, MAX_BODY, notifyOne };
