import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
export default defineConfig({ site: 'https://nery.yuricunha.com', output: 'static', trailingSlash: 'never', integrations: [sitemap()] });
