import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit({
    adapter: adapter({ pages: 'dist', assets: 'dist' }),
    files: { assets: 'public' },
  })],
  server: { port: 4321 },
  preview: { port: 4322 },
});
