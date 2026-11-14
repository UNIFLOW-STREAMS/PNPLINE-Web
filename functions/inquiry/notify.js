const { notifyOne } = require('./core.cjs');
const { makeStore, makeSender, makeSmsSender } = require('./aliyun.cjs');

async function run({ store, senders, now = Date.now, log = console.error }) {
  const cutoff = now();
  const stats = {};
  for (const channel of Object.keys(senders)) stats[channel] = { sent: 0, pending: 0, failed: 0, skipped: 0, errors: 0 };
  if (!Object.keys(senders).length) return stats;
  let cursor;
  do {
    const page = await store.due(new Date(cutoff).toISOString(), cursor);
    for (const row of page.rows) {
      if (now() - cutoff > 35_000) return stats;
      await Promise.all(Object.entries(senders).map(async ([channel, send]) => {
        try {
          const result = await notifyOne({ row, store, send, channel, now });
          stats[channel][result]++;
          if (result === 'failed') log(JSON.stringify({ event: 'inquiry_' + channel + '_failed', inquiryId: row.inquiryId }));
        } catch {
          stats[channel].errors++;
          log(JSON.stringify({ event: 'inquiry_' + channel + '_worker_error', inquiryId: row.inquiryId }));
        }
      }));
    }
    cursor = page.cursor;
  } while (cursor && now() - cutoff <= 35_000);
  return stats;
}

exports.run = run;
exports.handler = async function (_event, context) {
  const senders = {};
  for (const [channel, make] of Object.entries({ mail: makeSender, sms: makeSmsSender })) {
    try {
      senders[channel] = make(context.credentials);
    } catch {
      console.error(JSON.stringify({ event: 'inquiry_' + channel + '_not_configured' }));
    }
  }
  try {
    return await run({ store: makeStore(context.credentials), senders });
  } catch {
    // Neither event contents nor SDK errors belong in application logs.
    throw new Error('inquiry_notification_worker_error');
  }
};
