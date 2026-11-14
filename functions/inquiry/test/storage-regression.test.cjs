const assert = require('node:assert/strict');
const { createServer } = require('node:http');
const test = require('node:test');
const ots = require('tablestore');
const { main: { proto } } = require('tablestore/lib/protocol/tablestore_compiled_proto.js');
const { makeStore } = require('../aliyun.cjs');

test('a Tablestore protobuf conditional conflict returns false, and permission errors still fail', async (t) => {
  let code = 'OTSConditionCheckFail';
  const server = createServer((req, res) => {
    req.resume();
    res.writeHead(403, { 'x-ots-requestid': 'synthetic-request', 'content-type': 'application/octet-stream' });
    res.end(Buffer.from(proto.Error.encode({ code, message: 'Synthetic fixture' }).finish()));
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise((resolve) => server.close(resolve)));
  process.env.OTS_ENDPOINT = 'http://127.0.0.1:' + server.address().port;
  process.env.OTS_INSTANCE = 'inquiry-test';
  process.env.OTS_TABLE = 'inquiries';
  const store = makeStore({ accessKeyId: 'test-id', accessKeySecret: 'test-secret', securityToken: 'test-token' });
  const id = '18201f70-c517-4b5a-a23f-b7422c8fc937';
  assert.equal(await store.insert(id, { payloadHash: 'test' }), false);
  assert.equal(await store.transition(id, 'revision-1', { notificationStatus: 'sent' }), false);
  code = 'OTSNoPermissionAccess';
  await assert.rejects(store.insert(id, { payloadHash: 'test' }), (error) => error.code === code);
});
