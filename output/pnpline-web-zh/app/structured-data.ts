import { faqTopics } from './faq-data';
import { services } from './service-data';
import { getSiteUrl, siteData } from './site-data';

function identifiers(base: string | undefined) {
  // Root-relative identifiers resolve against the preview document. Once SITE_URL
  // is configured, every identifier becomes an absolute production URL.
  const url = (path: string) => base ? new URL(path, base).href : path;
  return {url, organization: url('/#organization'), website: url('/#website')};
}

function sharedNodes(base: string | undefined) {
  const {url, organization, website} = identifiers(base);
  return [
    {
      '@type': 'Organization', '@id': organization, name: siteData.name,
      ...(base && {url: base, logo: {
        '@type': 'ImageObject', '@id': url('/#logo'),
        contentUrl: url('/assets/logo.webp'), caption: siteData.name,
      }}),
    },
    {
      '@type': 'WebSite', '@id': website, name: siteData.name,
      inLanguage: siteData.language,
      ...(base && {url: base}),
      publisher: {'@id': organization},
    },
  ];
}

export function homeStructuredData(base = getSiteUrl()) {
  const {url, organization, website} = identifiers(base);
  const page = url('/#webpage');
  const faq = url('/#faq');
  return {
    '@context': 'https://schema.org',
    '@graph': [
      ...sharedNodes(base),
      {
        '@type': 'WebPage', '@id': page,
        name: siteData.homeTitle, description: siteData.homeDescription,
        inLanguage: siteData.language,
        ...(base && {url: base}),
        isPartOf: {'@id': website}, about: {'@id': organization},
        publisher: {'@id': organization},
        hasPart: [{'@id': url('/#services')}, {'@id': faq}],
      },
      {
        '@type': 'WebPageElement', '@id': url('/#services'),
        name: '服务范围', inLanguage: siteData.language,
        isPartOf: {'@id': page},
        hasPart: services.map((service, index) => ({
          '@type': 'WebPageElement', '@id': url(`/#service-panel-${index}`),
          name: service.title, text: `${service.copy} ${service.detail}`,
          inLanguage: siteData.language,
          isPartOf: {'@id': url('/#services')},
        })),
      },
      {
        // This is the landing page's FAQ section, not a second standalone URL.
        // FAQPage remains valid Schema.org vocabulary, not a Google rich result.
        '@type': 'FAQPage', '@id': faq, name: '询价前的常见问题。',
        inLanguage: siteData.language, isPartOf: {'@id': page},
        mainEntity: faqTopics.flatMap(topic => topic.questions.map(item => ({
          '@type': 'Question', '@id': url(`/#faq-question-${item.id}`),
          name: item.question, inLanguage: siteData.language,
          acceptedAnswer: {
            '@type': 'Answer', '@id': url(`/#faq-answer-${item.id}`),
            text: item.answer.join(' '), inLanguage: siteData.language,
          },
        }))),
      },
    ],
  };
}

export function privacyStructuredData(base = getSiteUrl()) {
  const {url, organization, website} = identifiers(base);
  return {
    '@context': 'https://schema.org',
    '@graph': [
      ...sharedNodes(base),
      {
        '@type': 'WebPage', '@id': url('/privacy#webpage'),
        name: siteData.privacyTitle, description: siteData.privacyDescription,
        inLanguage: siteData.language,
        ...(base && {url: url('/privacy')}),
        isPartOf: {'@id': website}, about: {'@id': organization},
        publisher: {'@id': organization},
      },
    ],
  };
}

export function serializeStructuredData(data: unknown): string {
  return JSON.stringify(data).replace(/</g, '\\u003c');
}
