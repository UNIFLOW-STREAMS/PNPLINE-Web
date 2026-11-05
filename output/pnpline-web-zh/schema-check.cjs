const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');

// Load the pure TypeScript data builders without adding a test framework.
const originalLoader = require.extensions['.ts'];
require.extensions['.ts'] = (mod, filename) => mod._compile(ts.transpileModule(
  fs.readFileSync(filename, 'utf8'),
  {compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017}},
).outputText, filename);
const {homeStructuredData, privacyStructuredData, serializeStructuredData} = require('./app/structured-data.ts');
const {getSiteUrl} = require('./app/site-data.ts');
const {faqTopics} = require('./app/faq-data.ts');
const {services} = require('./app/service-data.ts');
require.extensions['.ts'] = originalLoader;

const savedUrl = process.env.SITE_URL;
delete process.env.SITE_URL;
try {
  assert.equal(getSiteUrl(), undefined);
  assert.equal(getSiteUrl('  '), undefined);
  assert.equal(getSiteUrl(' https://cn.example.test/ '), 'https://cn.example.test/');
  for (const invalid of ['relative', 'javascript:alert(1)', 'ftp://example.test', 'https://example.test/zh', 'https://example.test/?a=1', 'https://example.test/#', 'https://a:b@example.test/']) {
    assert.throws(() => getSiteUrl(invalid), /SITE_URL/);
  }
  for (const base of [undefined, 'https://cn.example.test/']) {
    const home = homeStructuredData(base), privacy = privacyStructuredData(base);
    for (const data of [home, privacy]) {
      const text = serializeStructuredData(data);
      assert.deepEqual(JSON.parse(text), data);
      assert(!text.includes('undefined'));
      const nodes = data['@graph'];
      const ids = [];
      const visit = value => {
        if (!value || typeof value !== 'object') return;
        if (value['@type'] && value['@id']) ids.push(value['@id']);
        Object.values(value).forEach(v => Array.isArray(v) ? v.forEach(visit) : visit(v));
      };
      visit(nodes);
      assert.equal(new Set(ids).size, ids.length, 'Duplicate entity definitions');
      const references = value => {
        if (!value || typeof value !== 'object') return;
        if (value['@id'] && !value['@type']) assert(ids.includes(value['@id']), 'Unresolved reference: ' + value['@id']);
        Object.values(value).forEach(v => Array.isArray(v) ? v.forEach(references) : references(v));
      };
      references(nodes);
      const page = nodes.find(n => n['@type'] === 'WebPage');
      assert.equal(page.inLanguage, 'zh-CN');
      if (base) {
        assert(ids.every(id => id.startsWith(base)));
        const org = nodes.find(n => n['@type'] === 'Organization');
        assert.equal(org.logo.contentUrl, base + 'assets/logo.webp');
      } else {
        assert(!text.includes('example.test') && !text.includes('127.0.0.1'));
        assert(!nodes.some(n => 'url' in n));
      }
      assert(!/"(offers|price|aggregateRating|review|address|telephone|contactPoint|potentialAction)"/.test(text));
    }
    const faq = home['@graph'].find(n => n['@type'] === 'FAQPage');
    const questions = faqTopics.flatMap(t => t.questions);
    assert.equal(faq.mainEntity.length, 9);
    assert.deepEqual(faq.mainEntity.map(q => [q.name, q.acceptedAnswer.text]), questions.map(q => [q.question, q.answer.join(' ')]));
    const sections = home['@graph'].find(n => n['@type'] === 'WebPageElement');
    assert.deepEqual(sections.hasPart.map(n => [n.name, n.text]), services.map(s => [s.title, s.copy + ' ' + s.detail]));
    assert(!privacy['@graph'].some(n => n['@type'] === 'FAQPage'));
    fs.mkdirSync(__dirname + '/review/schema', {recursive: true});
    fs.writeFileSync(__dirname + '/review/schema/' + (base ? 'configured' : 'preview') + '-home.json', JSON.stringify(home, null, 2));
    fs.writeFileSync(__dirname + '/review/schema/' + (base ? 'configured' : 'preview') + '-privacy.json', JSON.stringify(privacy, null, 2));
  }
  const injection = '</script><script>alert(1)</script>';
  const safe = serializeStructuredData({text: injection});
  assert(!safe.includes('<'));
  assert.equal(JSON.parse(safe).text, injection);
  console.log('PASS: preview and configured graphs, references, page scope, 9 FAQ pairs, 4 service sections, URL validation, script escaping.');
} finally {
  if (savedUrl === undefined) delete process.env.SITE_URL;
  else process.env.SITE_URL = savedUrl;
}
