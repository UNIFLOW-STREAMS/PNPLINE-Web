import { faqTopics } from './faq-data';
import { services, serviceTargets } from './service-data';
import { getSiteUrl, privacyPath, siteData } from './site-data';

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
      description: siteData.homeDescription,
      ...(base && {url: base, logo: url('/assets/logo.webp')}),
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
  const serviceNodes = services.map((service, index) => ({
    '@type': 'Service',
    '@id': url(`/#service-${index + 1}`),
    url: url(`/#${serviceTargets[index]}`),
    name: service.title,
    description: service.copy,
    serviceType: service.category,
    areaServed: service.countries.map(name => ({'@type': 'Country', name})),
    provider: {'@id': organization},
  }));
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
        mainEntity: serviceNodes.map(node => ({'@id': node['@id']})),
        hasPart: {'@id': faq},
      },
      ...serviceNodes,
      {
        '@type': 'WebPageElement', '@id': faq, url: faq,
        name: '获取报价前的常见问题',
        inLanguage: siteData.language, isPartOf: {'@id': page},
        mainEntity: faqTopics.flatMap(topic => topic.questions.map(({question, answer}) => ({
          '@type': 'Question',
          name: question,
          acceptedAnswer: {'@type': 'Answer', text: answer.join('\n\n')},
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
        '@type': 'WebPage', '@id': url(privacyPath + '#webpage'),
        name: siteData.privacyTitle, description: siteData.privacyDescription,
        inLanguage: siteData.language,
        ...(base && {url: url(privacyPath)}),
        isPartOf: {'@id': website}, about: {'@id': organization},
        publisher: {'@id': organization},
      },
    ],
  };
}

export function serializeStructuredData(data: unknown): string {
  return JSON.stringify(data).replace(/</g, '\\u003c');
}
