import type { Handle } from '@sveltejs/kit/hooks';

export const handle: Handle = ({ event, resolve }) => resolve(event, {
  transformPageChunk: ({ html }) =>
    html.replace('%nery.lang%', event.route.id === '/pt-br' ? 'pt-BR' : 'en'),
});
