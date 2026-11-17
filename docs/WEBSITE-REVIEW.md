# Website redesign review — 2026-11-17

Scope: the two locale pages, original and occasion artwork, animation controls,
preferences, native gallery dialog, search metadata and build output.

## Automated checks

- Astro diagnostics: zero errors, warnings or hints.
- ESLint: passed.
- Seven unit checks: animation timing, locale parity and ownership, text and
  non-text contrast.
- Four exported-site checks: language, canonical/alternate URLs, connected
  structured data, social-image dimensions, unique IDs, sitemap and noindex pages.
- Local production build completed successfully.

Browser audits used the installed axe-core 4.14.0 with WCAG 2 A/AA, WCAG 2.1,
WCAG 2.2 AA and best-practice tags. English and PT-BR pages and the open gallery
dialog had zero reported violations in the reviewed states. The engine deferred
13 color checks, largely decorative marks and text over backgrounds. Decorative
marks are hidden from assistive technology; the remaining text colors were
checked against the lightest relevant surface by the contrast tests.

## Interaction and responsive review

- Skip link is the first keyboard destination and moves focus to main content.
- The artwork filter reports the matching count; all three occasion pieces open.
- Arrow keys navigate the dialog; Escape closes it and restores the opener.
- Settings pause motion, hide the walker and preserve preferences locally.
- Device reduced motion selects representative still poses.
- Reflow checked at 320 CSS pixels, including 200% text and enlarged text spacing;
  no page-level horizontal overflow in that reviewed state.
- Sticky header height remains stable across animation frames and reflow.

The local browser captures and machine-readable audit summary are in
`website/preview/`. These are scoped checks, not a complete manual screen-reader
evaluation. Search indexing and field performance remain post-publication checks.

## References

- [Google Search: SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [Google Search: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [W3C: WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/)
- [W3C: Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html)
- [W3C: Target Size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
