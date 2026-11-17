import { messages, type Locale } from '../i18n/messages';

export const ORIGIN = 'https://nery.yuricunha.com';
export const OWNER = 'https://yuricunha.com/#person';
export const WEBSITE = `${ORIGIN}/#website`;
export const CHARACTER = `${ORIGIN}/#nery-mizuki`;

export function pageMetadata(locale: Locale, notFound = false) {
  const c = messages[locale];
  const language = locale === 'pt-br' ? 'pt-BR' : 'en';
  const canonical = `${ORIGIN}${locale === 'pt-br' ? '/pt-br' : '/'}`;
  const image = `${ORIGIN}/social/nery-${locale}.png`;
  const graph = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'Person', '@id': OWNER, name: 'Yuri Cunha', url: 'https://yuricunha.com',
        sameAs: ['https://github.com/isyuricunha', 'https://gitlab.com/isyuricunha'],
      },
      {
        '@type': 'WebSite', '@id': WEBSITE, name: 'Nery Mizuki', url: `${ORIGIN}/`,
        inLanguage: ['en', 'pt-BR'], publisher: { '@id': OWNER }, about: { '@id': CHARACTER },
      },
      {
        '@type': 'CreativeWork', '@id': CHARACTER, name: 'Nery Mizuki',
        description: c.description, creator: { '@id': OWNER }, copyrightHolder: { '@id': OWNER },
        copyrightYear: 2026, image: `${ORIGIN}/kit/nery-portrait.webp`,
        license: `${ORIGIN}${locale === 'pt-br' ? '/pt-br' : ''}#license`,
        sameAs: ['https://github.com/isyuricunha/nery', 'https://gitlab.com/isyuricunha/nery', 'https://git.yuricunha.com/isyuricunha/nery'],
      },
      {
        '@type': 'ImageObject', '@id': `${canonical}#primaryimage`, contentUrl: image,
        width: 1200, height: 630, caption: c.socialAlt, creator: { '@id': OWNER },
        creditText: 'Yuri Cunha', copyrightNotice: '© 2026 Yuri Cunha. All rights reserved.',
        license: `${canonical}#license`, acquireLicensePage: 'https://github.com/isyuricunha/nery/blob/main/assets/mascot/LICENSE.md',
      },
      {
        '@type': 'WebPage', '@id': `${canonical}#webpage`, url: canonical,
        name: c.title, description: c.description, inLanguage: language,
        isPartOf: { '@id': WEBSITE }, about: { '@id': CHARACTER }, author: { '@id': OWNER },
        primaryImageOfPage: { '@id': `${canonical}#primaryimage` },
      },
    ],
  };
  return { title: notFound ? `404 · ${c.notFoundTitle} — Nery Mizuki` : c.title, description: c.description, canonical, image, language, graph };
}
