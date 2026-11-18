# Website development

The site has two static language routes: `/` for English and `/pt-br` for
Brazilian Portuguese. Both use `website/src/components/NerySite.svelte` and the
catalogs in `website/src/i18n/`. The language switch retains the current section.
On the home route, the site uses the first supported language in the browser's
preference list and defaults to English. The language switch saves an explicit
choice locally. A direct visit to `/pt-br` always opens Brazilian Portuguese.
Page titles, metadata, accessibility labels, animation labels and speech are
localized. Canonical and alternate-language URLs are rendered at build time.

With Node.js 22.17 or newer, run `pnpm install` and
`pnpm dev --host 127.0.0.1` from `website/`.
The development server normally uses `http://127.0.0.1:4321`; it reloads local
changes. This does not update the published site.

`pnpm build` creates the SvelteKit static export in `website/dist/`.
`pnpm preview --host 127.0.0.1` serves the build on port 4322.
Run `pnpm lint`, `pnpm check` and `pnpm test` before committing, then
`pnpm build && pnpm test:seo` to check the exported pages and sitemap.

On Vercel, `website/vercel.json` selects static hosting and extensionless URLs.
For other static hosts, map `/pt-br` to `pt-br.html` and serve `404.html`
with status 404 for missing files. The build needs no application server.

## Interface and accessibility

The redesigned site uses `website/src/styles/site.css` and small Svelte components
under `website/src/components/site/`. It preserves the original character art.
The navigation, language switch and preferences are available at every screen
size. Its measured header height sets the anchor offset without determining the
header's own size, avoiding a ResizeObserver feedback loop.

The gallery progressively enables filters and a native image dialog. Escape closes
the dialog and restores focus to the illustration; left/right arrows move through
the current filter. New titles and descriptions are announced politely. With
JavaScript disabled, all artwork and page text remain available.

Settings can pause every animation, hide the walking Nery, or disable speech.
Manual pause preserves the selected animation frame. The device's reduced-motion
preference takes precedence and shows representative still poses. The walking
character stops moving under pointer hover or keyboard focus.

The target is WCAG 2.2 AA. Color-token checks cover text contrast, control boundaries
and keyboard focus. These checks complement browser audits and keyboard/reflow
review; they are not a certification of full conformance or a screen-reader audit.

## Search and image delivery

Both language pages are rendered as complete static HTML. Metadata includes
self-referencing canonicals, reciprocal language alternatives, localized social
cards and a connected schema.org graph for the website, page, artwork and Yuri.
Nery is represented as a fictional creative work rather than a real person.
The sitemap contains only the two language pages. The 404 and internal animation
review pages have `noindex,follow`.

`prepare-web-art.mjs` generates responsive AVIF/WebP versions of the hero and lightweight WebP
gallery thumbnails. The dialog loads the native artwork when opened. The web
atlases use high-quality optimized copies at the original pixel dimensions; the
approved source atlases remain unchanged. Animation loading yields to the hero,
and the occasion atlas loads when its stage approaches the viewport.

`website/scripts/build-social.mjs` composes the existing portrait and typography
into 1200 × 630 English/PT-BR cards. Asset preparation regenerates these cards.

Indexing, search appearance and real-user Core Web Vitals require the published
site and subsequent observation. No ranking or Lighthouse score is inferred from
a successful local build.

## Artwork and animation

The hero uses the original 745 × 905 portrait, rather than the small avatar.
The original kit and nine-state pet remain separate from the additional occasion
kit. `scripts/build_occasions.py` builds three occasion poses and two web-only
12-cel actions. The website's asset-preparation script copies their exports and
generates typed data for the shared components.

Occasion actions play once and settle back into their first drawing. They can
be replayed with their buttons or by clicking Nery. Reduced motion shows a static
representative pose. Playback pauses while the page is hidden.

Speech appears in response to interaction, normally disappears after twelve
seconds, and remains visible while hovered or focused. It can be closed or
disabled. The speech preference is stored locally when browser
storage is available. Speech strings are plain local text; no chat service or
remote requests are involved.

Useful local review routes:

- `/pt-br#kit`: original and occasion artwork.
- `/pt-br#pet`: original and new animation panels, with speech controls.
- `/occasions-review.html`: the two exported GIFs at actual playback timing.
- `/walk-review.html`: the previously approved walking comparison.

Asset checks: `python scripts/test_occasions.py` and
`python scripts/test_walk_scope.py` (Pillow and NumPy required).

The images in `website/preview/` record local browser checks; they are not used
by the site. The production deployment is a separate step.
