import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
export default defineConfig({
  site: 'https://nery.yuricunha.com',
  output: 'static',
  trailingSlash: 'never',
  integrations: [sitemap({
    filter: page => ['/', '/pt-br'].includes(new URL(page).pathname.replace(/\/$/, '') || '/'),
    i18n: { defaultLocale: 'en', locales: { en: 'en', 'pt-br': 'pt-BR' } },
  })],
});
