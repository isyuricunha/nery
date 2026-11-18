import { ORIGIN } from '../../scripts/seo';

export const prerender = true;

export function GET() {
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>${ORIGIN}/sitemap-0.xml</loc></sitemap>
</sitemapindex>`, { headers: { 'content-type': 'application/xml; charset=utf-8' } });
}
