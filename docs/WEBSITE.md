# Website development

The site has two static language routes: `/` for English and `/pt-br` for
Brazilian Portuguese. Both use `website/src/components/NerySite.astro` and the
catalogs in `website/src/i18n/`. The language switch retains the current section.
Page titles, metadata, accessibility labels, animation labels and speech are
localized. Canonical and alternate-language URLs are rendered at build time.

From `website/`, run `pnpm install` and `pnpm dev --host 127.0.0.1`.
The development server normally uses `http://127.0.0.1:4321`; it reloads local
changes. This does not update the published site.

`pnpm build` creates `website/dist/`; `pnpm preview --host 127.0.0.1` serves that
build. Run `pnpm lint`, `pnpm check` and `pnpm test` before committing.

## Artwork and animation

The hero uses the original 745 × 905 portrait, rather than the small avatar.
The original kit and nine-state pet remain separate from the additional occasion
kit. `scripts/build_occasions.py` builds three occasion poses and two web-only
12-cel actions. The website's asset-preparation script copies their exports and
generates typed data for the shared components.

Occasion actions play once and settle back into their first drawing. They can
be replayed with their buttons or by clicking Nery. Reduced motion shows a static
representative pose. Playback pauses while the page is hidden.

Speech appears in response to interaction, disappears after eight seconds, and
can be closed or disabled. The speech preference is stored locally when browser
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
