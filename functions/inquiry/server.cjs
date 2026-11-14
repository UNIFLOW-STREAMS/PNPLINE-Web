const { createServer } = require('node:http');
const { randomUUID, timingSafeEqual } = require('node:crypto');
const { TextDecoder } = require('node:util');
const { accept, MAX_BODY } = require('./core.cjs');

function makeHandler({ origins, originToken, consentVersion, storeFor, log = console.error }) {
  const token = Buffer.from(originToken);
  if (token.length < 32 || !consentVersion || !origins.length || origins.some((o) => new URL(o).origin !== o)) {
    throw new Error('invalid_inquiry_api_configuration');
  }
  return async (req, res) => {
    const requestId = randomUUID();
    const finish = (status, body) => {
      res.writeHead(status, { 'Cache-Control': 'no-store', 'Content-Type': 'application/json; charset=utf-8',
        'X-Content-Type-Options': 'nosniff', 'X-Robots-Tag': 'noindex', Vary: 'Origin' });
      res.end(body ? JSON.stringify(body) : undefined);
    };
    if (req.url !== '/v1/inquiries') return finish(404, { code: 'not_found' });
    const offered = Buffer.from(req.headers['x-pnpline-origin-token'] ?? '');
    if (offered.length !== token.length || !timingSafeEqual(offered, token) || !origins.includes(req.headers.origin)) {
      return finish(403, { code: 'forbidden' });
    }
    res.setHeader('Access-Control-Allow-Origin', req.headers.origin);
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Idempotency-Key');
    if (req.method === 'OPTIONS') {
      res.setHeader('Access-Control-Max-Age', '600');
      return finish(204);
    }
    if (req.method !== 'POST') {
      res.setHeader('Allow', 'POST, OPTIONS');
      return finish(405, { code: 'method_not_allowed' });
    }
    if (req.headers['content-type']?.split(';')[0].trim().toLowerCase() !== 'application/json') {
      return finish(415, { code: 'json_required' });
    }
    if (Number(req.headers['content-length']) > MAX_BODY) return finish(413, { code: 'body_too_large' });
    const chunks = [];
    let size = 0;
    let body;
    try {
      for await (const chunk of req.iterator({ destroyOnReturn: false })) {
        size += chunk.length;
        if (size > MAX_BODY) {
          req.resume();
          return finish(413, { code: 'body_too_large' });
        }
        chunks.push(chunk);
      }
      body = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(Buffer.concat(chunks)));
    } catch {
      if (!res.destroyed) return finish(400, { code: 'invalid_json' });
      return;
    }
    try {
      const result = await accept({ id: req.headers['idempotency-key'], body, consentVersion,
        store: storeFor(req.headers) });
      finish(result.status, result.body);
    } catch {
      log(JSON.stringify({ event: 'inquiry_storage_error', requestId }));
      finish(503, { code: 'storage_unavailable', requestId });
    }
  };
}

if (require.main === module) {
  const { makeStore, requireEnv } = require('./aliyun.cjs');
  const handler = makeHandler({
    origins: requireEnv('INQUIRY_ORIGINS').split(',').map((value) => value.trim()),
    consentVersion: requireEnv('INQUIRY_CONSENT_VERSION'),
    originToken: requireEnv('INQUIRY_ORIGIN_TOKEN'),
    storeFor: (headers) => makeStore({
      accessKeyId: headers['x-fc-access-key-id'], accessKeySecret: headers['x-fc-access-key-secret'],
      securityToken: headers['x-fc-security-token'],
    }),
  });
  createServer({ requestTimeout: 15_000, headersTimeout: 10_000 }, handler)
    .listen(Number(process.env.FC_SERVER_PORT || 9000), '0.0.0.0');
}

module.exports = { makeHandler };
