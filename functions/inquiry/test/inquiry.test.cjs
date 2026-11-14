const assert = require('node:assert/strict');
const { randomUUID } = require('node:crypto');
const { createServer } = require('node:http');
const { once } = require('node:events');
const test = require('node:test');
const { MAX_BODY, accept, notifyOne } = require('../core.cjs');
const { makeHandler } = require('../server.cjs');

const { composeMail } = require('../inquiry-email.cjs');
const { receiptNumber } = require('../notification-format.cjs');
const { run } = require('../notify.js');

const consentVersion = 'test-v1';
const origin = 'https://pnpline.cn';
const originToken = randomUUID();
const body = { inquiryType: '仓储与履约咨询', cargo: '服装', shipping: '海运拼箱', volume: '2.5', unit: 'CBM',
  destination: 'FBA 仓库', ior: '不确定', email: 'buyer@example.com', consent: true, consentVersion };

function memoryStore() {
  const rows = new Map();
  return {
    rows,
    async insert(id, row) {
      if (rows.has(id)) return false;
      rows.set(id, { ...row, inquiryId: id });
      return true;
    },
    async hash(id) { return rows.get(id)?.payloadHash; },
    async transition(id, revision, state, revisionColumn) {
      const current = rows.get(id);
      if (current?.[revisionColumn] !== revision) return false;
      rows.set(id, { ...current, ...state });
      return true;
    },
    async due() { return { rows: [...rows.values()] }; },
  };
}

test('HTTP intake authorizes origin, validates data and only acknowledges durable storage', async (t) => {
  const store = memoryStore();
  const logs = [];
  let outage = false;
  const handler = makeHandler({ origins: [origin], originToken, consentVersion,
    storeFor: () => outage ? { insert: async () => { throw new Error(body.email); } } : store,
    log: (entry) => logs.push(entry) });
  const server = createServer(handler).listen(0, '127.0.0.1');
  t.after(() => server.close());
  await once(server, 'listening');
  const url = `http://127.0.0.1:${server.address().port}/v1/inquiries`;
  const id = randomUUID();
  const headers = { origin, 'x-pnpline-origin-token': originToken, 'idempotency-key': id, 'content-type': 'application/json' };
  const request = (payload, extra = {}) => fetch(url, { method: 'POST', headers: { ...headers, ...extra },
    body: JSON.stringify(payload) });

  const preflight = await fetch(url, { method: 'OPTIONS', headers });
  assert.equal(preflight.status, 204);
  assert.equal(preflight.headers.get('access-control-allow-origin'), origin);
  assert.equal((await request(body, { origin: 'https://example.com' })).status, 403);
  assert.equal((await request(body, { 'x-pnpline-origin-token': 'wrong' })).status, 403);
  assert.equal((await request({ cargo: 'X'.repeat(MAX_BODY) })).status, 413);
  async function* chunks() { yield Buffer.alloc(MAX_BODY, 97); yield Buffer.from('b'); }
  const streamed = await fetch(url, { method: 'POST', headers, body: chunks(), duplex: 'half' });
  assert.equal(streamed.status, 413);
  assert.equal((await request(body, { 'content-type': 'text/plain' })).status, 415);
  const invalid = await request({ ...body, consentVersion: 'old', shipping: 'other', website: 'bot' });
  assert.equal(invalid.status, 422);
  assert.deepEqual((await invalid.json()).fields, ['shipping', 'consent', 'website']);
  const rejected = await request({ ...body, inquiryType: 'buyer@example.com' });
  assert.equal(rejected.status, 422);
  assert.deepEqual((await rejected.json()).fields, ['inquiryType']);
  assert.equal(store.rows.size, 0);
  const responses = await Promise.all([request(body), request(body)]);
  assert.deepEqual(responses.map((r) => r.status).sort(), [200, 201]);
  for (const response of responses) assert.deepEqual(await response.json(), { inquiryId: id, receiptNumber: receiptNumber(id), status: 'accepted' });
  assert.equal((await request({ ...body, cargo: '机械' })).status, 409);
  assert.equal(store.rows.size, 1);
  const saved = store.rows.get(id);
  assert.equal(saved.notificationStatus, 'pending');
  assert.equal(saved.smsStatus, 'pending');
  assert.equal(saved.consentVersion, consentVersion);
  assert.equal(saved.consentAcceptedAt, saved.receivedAt);
  outage = true;
  const unavailable = await request(body);
  assert.equal(unavailable.status, 503);
  assert.equal((await unavailable.json()).code, 'storage_unavailable');
  assert.equal(logs.length, 1);
  assert.ok(!logs[0].includes(body.email));
});

test('concurrent notification workers send one internal mail with all inquiry fields', async () => {
  const id = randomUUID(), store = memoryStore();
  await accept({ id, body, consentVersion, store });
  const row = store.rows.get(id);
  const mails = [];
  const send = async (mail) => { mails.push(mail); };
  const results = await Promise.all([notifyOne({ row, store, send }), notifyOne({ row, store, send })]);
  assert.deepEqual(results.sort(), ['sent', 'skipped']);
  assert.equal(store.rows.get(id).notificationStatus, 'sent');
  assert.equal(mails.length, 1);
  assert.ok(mails[0].subject.includes(receiptNumber(id)));
  assert.ok(!mails[0].subject.includes(body.email));
  for (const content of [receiptNumber(id), body.inquiryType, '服装', '海运拼箱', '2.5 CBM', 'FBA 仓库', '不确定', body.email]) {
    assert.ok(mails[0].htmlBody.includes(content), content);
  }
});

test('the HTML notification includes the logo and safely escapes inquiry values', () => {
  const { htmlBody } = composeMail({
    cargo: '<img src=x onerror="alert(1)"> & boxes',
    email: 'buyer+test@example.com',
    inquiryId: randomUUID(),
    receivedAt: '2026-11-11T11:00:00.000Z',
  });
  assert.ok(htmlBody.includes('src="https://pnpline.cn/assets/logo.webp"'));
  assert.ok(htmlBody.includes('alt="PNPLINE"'));
  assert.ok(htmlBody.includes('mailto:buyer%2Btest@example.com'));
  assert.ok(htmlBody.includes('&lt;img src=x onerror=&quot;alert(1)&quot;&gt; &amp; boxes'));
  assert.ok(!htmlBody.includes('<img src=x'));
  assert.ok(htmlBody.includes('未填写'));
});

test('the worker skips previous routes and blocks new records without consent', async () => {
  const id = randomUUID(), store = memoryStore();
  await accept({ id, body, consentVersion, store });
  const row = store.rows.get(id);
  let sends = 0;
  const send = async () => { sends++; };
  assert.equal(await notifyOne({ row: { ...row, notificationRoute: undefined }, store, send }), 'skipped');
  delete row.consentAcceptedAt;
  assert.equal(await notifyOne({ row, store, send }), 'failed');
  assert.equal(await notifyOne({ row, store, send, channel: 'sms' }), 'failed');
  assert.equal(sends, 0);
  assert.equal(store.rows.get(id).notificationStatus, 'failed');
});

test('failed mail is retried on schedule, caps attempts, and preserves the inquiry', async () => {
  let current = Date.parse('2028-02-29T12:00:00Z');
  const now = () => current;
  const id = randomUUID(), store = memoryStore();
  await accept({ id, body, consentVersion, store, now });
  assert.equal(store.rows.get(id).deleteAfter, '2029-02-28T12:00:00.000Z');
  let sends = 0;
  const send = async () => { sends++; throw new Error('unavailable'); };
  const attempt = () => notifyOne({ row: store.rows.get(id), store, send, now });
  for (const minutes of [1, 5, 30]) {
    assert.equal(await attempt(), 'pending');
    assert.equal(Date.parse(store.rows.get(id).nextNotificationAt), current + minutes * 60_000);
    assert.equal(await attempt(), 'skipped');
    current += minutes * 60_000;
  }
  assert.equal(await attempt(), 'failed');
  assert.equal(await attempt(), 'skipped');
  assert.equal(sends, 4);
  assert.equal(store.rows.get(id).email, body.email);
});

for (const outage of ['mail', 'sms']) {
  test(`a failed ${outage} retries independently and SMS receives only type and receipt`, async () => {
    let current = Date.parse('2026-11-11T12:00:00Z'), unavailable = true;
    const now = () => current;
    const id = randomUUID(), store = memoryStore(), calls = { mail: [], sms: [] };
    await accept({ id, body, consentVersion, store, now });
    const senders = Object.fromEntries(Object.entries(calls).map(([channel, messages]) => [channel, async (message) => {
      messages.push(message);
      if (unavailable && channel === outage) throw new Error('unavailable');
    }]));
    const other = outage === 'sms' ? 'mail' : 'sms';
    const first = await run({ store, senders, now });
    assert.equal(first[outage].pending, 1);
    assert.equal(first[other].sent, 1);
    await run({ store, senders, now });
    assert.equal(calls[outage].length, 1);
    current += 60_000;
    unavailable = false;
    const second = await run({ store, senders, now });
    assert.equal(second[outage].sent, 1);
    assert.equal(calls[other].length, 1);
    assert.equal(calls[outage].length, 2);
    for (const sms of calls.sms) assert.deepEqual(sms, { type: body.inquiryType, number: receiptNumber(id) });
    assert.equal(calls.sms[0].number.length, 32);
    assert.ok(calls.mail[0].htmlBody.includes(body.email));
    assert.ok(calls.mail[0].htmlBody.includes(calls.sms[0].number));
  });
}
