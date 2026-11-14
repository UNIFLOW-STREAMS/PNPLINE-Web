const ots = require('tablestore');
const { main: { proto: { Error: TablestoreError } } } = require('tablestore/lib/protocol/tablestore_compiled_proto.js');
const { isEmail } = require('./core.cjs');
const { INQUIRY_MAILBOX, INQUIRY_TYPES, NOTIFICATION_ROUTE } = require('./notification-format.cjs');

class InquiryTablestoreClient extends ots.Client {
  extractError(response) {
    // The Node SDK's default error handler only decodes XML. Data APIs also return protobuf errors.
    const { body, headers, statusCode } = response.httpResponse;
    let decoded;
    try {
      if (body?.length) decoded = TablestoreError.decode(body);
    } catch {
      // Leave non-protobuf responses to the SDK.
    }
    if (/^OTS[A-Za-z0-9]+$/.test(decoded?.code ?? '')) {
      response.error = Object.assign(new Error(decoded.message), { code: decoded.code, headers, statusCode });
      return;
    }
    super.extractError(response);
  }
}

function requireEnv(name) {
  const value = process.env[name]?.trim();
  if (!value) throw new Error(`missing_${name}`);
  return value;
}

function assertRole(credentials) {
  if (!credentials?.accessKeyId || !credentials.accessKeySecret || !credentials.securityToken) {
    throw new Error('missing_fc_role_credentials');
  }
  return credentials;
}

function makeStore(credentials) {
  const { accessKeyId, accessKeySecret, securityToken } = assertRole(credentials);
  const tableName = requireEnv('OTS_TABLE');
  const client = new InquiryTablestoreClient({
    accessKeyId, secretAccessKey: accessKeySecret, stsToken: securityToken,
    endpoint: requireEnv('OTS_ENDPOINT'), instancename: requireEnv('OTS_INSTANCE'),
    maxRetries: 0, httpOptions: { timeout: 3500 },
  });
  const key = (id) => [{ inquiryId: id }];
  const attributes = (obj) => Object.entries(obj).map(([name, value]) => ({
    [name]: typeof value === 'number' ? ots.Long.fromNumber(value) : value,
  }));
  const valueOf = (value) => typeof value?.toNumber === 'function' ? value.toNumber() : value;
  const read = (row) => Object.fromEntries((row?.attributes || []).map(({ columnName, columnValue }) =>
    [columnName, valueOf(columnValue)]));
  const call = (method, options) => new Promise((resolve, reject) => {
    client[method]({ tableName, ...options }, (err, data) => err ? reject(err) : resolve(data));
  });
  const match = (name, value, compare = ots.ComparatorType.EQUAL) => {
    const condition = new ots.SingleColumnCondition(name, value, compare);
    condition.passIfMissing = false;
    return condition;
  };
  const conditional = async (method, options) => {
    try {
      await call(method, options);
      return true;
    } catch (error) {
      if (error.code === 'OTSConditionCheckFail') return false;
      throw error;
    }
  };
  return {
    insert: (id, row) => conditional('putRow', {
      primaryKey: key(id), attributeColumns: attributes(row),
      condition: new ots.Condition(ots.RowExistenceExpectation.EXPECT_NOT_EXIST, null),
    }),
    hash: async (id) => read((await call('getRow', {
      primaryKey: key(id), columnsToGet: ['payloadHash'], maxVersions: 1,
    })).row).payloadHash,
    transition: (id, revision, state, revisionColumn = 'notificationRevision') => conditional('updateRow', {
      primaryKey: key(id), updateOfAttributeColumns: [{ PUT: attributes(state) }],
      condition: new ots.Condition(ots.RowExistenceExpectation.EXPECT_EXIST, match(revisionColumn, revision)),
    }),
    due: async (before, cursor) => {
      const dueFor = (statusColumn, dueColumn) => {
        const statuses = new ots.CompositeCondition(ots.LogicalOperator.OR);
        statuses.addSubCondition(match(statusColumn, 'pending'));
        statuses.addSubCondition(match(statusColumn, 'sending'));
        const due = new ots.CompositeCondition(ots.LogicalOperator.AND);
        due.addSubCondition(statuses);
        due.addSubCondition(match(dueColumn, before, ots.ComparatorType.LESS_EQUAL));
        return due;
      };
      const dueChannels = new ots.CompositeCondition(ots.LogicalOperator.OR);
      dueChannels.addSubCondition(dueFor('notificationStatus', 'nextNotificationAt'));
      dueChannels.addSubCondition(dueFor('smsStatus', 'nextSmsAt'));
      const filter = new ots.CompositeCondition(ots.LogicalOperator.AND);
      filter.addSubCondition(match('notificationRoute', NOTIFICATION_ROUTE));
      filter.addSubCondition(dueChannels);
      const data = await call('getRange', {
        inclusiveStartPrimaryKey: key(cursor ?? ots.INF_MIN),
        exclusiveEndPrimaryKey: key(ots.INF_MAX), direction: ots.Direction.FORWARD,
        columnFilter: filter, maxVersions: 1, limit: 50,
        columnsToGet: ['notificationStatus', 'notificationAttempts', 'notificationRevision', 'nextNotificationAt',
          'smsStatus', 'smsAttempts', 'smsRevision', 'nextSmsAt', 'notificationRoute',
          'receivedAt', 'consentVersion', 'consentAcceptedAt', 'inquiryType', 'cargo', 'shipping', 'volume', 'unit', 'otherUnit', 'destination', 'ior', 'email'],
      });
      return {
        rows: data.rows.map((row) => ({ inquiryId: row.primaryKey[0].value, ...read(row) })),
        cursor: data.nextStartPrimaryKey?.[0]?.value,
      };
    },
  };
}

function makeSender(credentials) {
  const role = assertRole(credentials);
  const { default: DirectMail, SingleSendMailRequest } = require('@alicloud/dm20151123');
  const { Config } = require('@alicloud/openapi-client');
  const sender = requireEnv('DM_SENDER');
  if (!isEmail(sender) || /[,;]/.test(sender)) {
    throw new Error('invalid_mailbox_configuration');
  }
  const client = new DirectMail(new Config({
    ...role, endpoint: 'dm.aliyuncs.com', protocol: 'HTTPS', regionId: 'cn-hangzhou',
    connectTimeout: 3500, readTimeout: 6000,
  }));
  return async ({ subject, htmlBody }) => {
    const result = await client.singleSendMail(new SingleSendMailRequest({
      accountName: sender, toAddress: INQUIRY_MAILBOX, subject, htmlBody,
      addressType: 1, replyToAddress: false,
    }));
    if (!result.body?.requestId) throw new Error('direct_mail_not_acknowledged');
  };
}

function makeSmsSender(credentials) {
  const role = assertRole(credentials);
  const { default: Sms, SendSmsRequest } = require('@alicloud/dysmsapi20170525');
  const { Config } = require('@alicloud/openapi-client');
  const phoneNumbers = requireEnv('INQUIRY_SMS_PHONE');
  const signName = requireEnv('INQUIRY_SMS_SIGN');
  const templateCode = requireEnv('INQUIRY_SMS_TEMPLATE');
  if (!/^1[3-9]\d{9}$/.test(phoneNumbers) || !/^SMS_\d+$/.test(templateCode)) {
    throw new Error('invalid_sms_configuration');
  }
  const client = new Sms(new Config({
    ...role, endpoint: 'dysmsapi.aliyuncs.com', protocol: 'HTTPS',
    connectTimeout: 3500, readTimeout: 6000,
  }));
  return async ({ type, number }) => {
    if (!INQUIRY_TYPES.includes(type) || !/^[a-f0-9]{32}$/.test(number)) throw new Error('invalid_sms_content');
    const result = await client.sendSms(new SendSmsRequest({
      phoneNumbers, signName, templateCode, templateParam: JSON.stringify({ type, number }), outId: number,
    }));
    if (result.body?.code !== 'OK' || !result.body.bizId) throw new Error('sms_not_acknowledged');
  };
}

module.exports = { makeStore, makeSender, makeSmsSender, requireEnv };
