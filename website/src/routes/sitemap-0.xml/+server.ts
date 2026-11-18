import { pageMetadata } from '../../scripts/seo';

export const prerender = true;

export function GET() {
  const pages = [pageMetadata('en'), pageMetadata('pt-br')];
  const alternatives = pages.map(({ language, canonical }) =>
    `<xhtml:link rel="alternate" hreflang="${language}" href="${canonical}" />`).join('\n');
  const urls = pages.map(({ canonical }) =>
    `<url><loc>${canonical}</loc>\n${alternatives}\n</url>`).join('\n');
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${urls}
</urlset>`, { headers: { 'content-type': 'application/xml; charset=utf-8' } });
}
