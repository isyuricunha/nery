<script lang="ts">
import { galleryImages } from "../../generated/web-art";
import MicroIconKit from './MicroIconKit.svelte';
import { artworkFilters, artworks } from '../../data/artworks';
import { messages, type Locale } from '../../i18n/messages';
import expand from 'lucide-static/icons/expand.svg?raw';
const { locale }: { locale: Locale } = $props();
const c = $derived(messages[locale]);
const pieces = $derived(artworks(locale));
</script>

<section id="kit" class="section gallery-section" aria-labelledby="gallery-heading">
  <div class="wrap">
    <div class="section-heading">
      <div><p class="eyebrow">{c.kitNumber}</p><h2 id="gallery-heading">{c.galleryTitle}</h2></div>
      <p>{c.galleryDescription}</p>
    </div>
    <div class="gallery-toolbar">
      <div class="filter-group" role="group" aria-label={c.filterLabel} hidden>
        {#each artworkFilters as filter, i (filter)}<button type="button" data-filter={filter} aria-pressed={i === 0}>{c.filters[i]}</button>{/each}
      </div>
      <div class="gallery-links">
        <p id="gallery-result" role="status" aria-live="polite">{c.artworkCount.replace('{count}', String(pieces.length))}</p>
        <a href="#micro-icons">{c.microKitTitle} <span aria-hidden="true">↓</span></a>
      </div>
    </div>
    <div class="artwork-grid">
      {#each pieces as piece, i (piece.id)}
        {@const image = galleryImages[piece.id]}
        <figure class={['artwork-card', { 'artwork-card-portrait': i === 0 }]} data-artwork={i} data-group={piece.group}>
          <button type="button" class="artwork-open" data-art-index={i} disabled
            data-src={piece.src} data-width={piece.width} data-height={piece.height}
            data-title={piece.title} data-description={piece.description}
            aria-label={c.viewArtwork.replace('{title}', piece.title)}>
            <span class="artwork-image"><img src={image.src} alt={`Nery Mizuki — ${piece.title}`} width={image.width} height={image.height} loading="lazy" decoding="async" style={`--native-width:${piece.width}px`} /></span>
            <span class="expand-icon icon" aria-hidden="true"><!-- eslint-disable-next-line svelte/no-at-html-tags -- Trusted Lucide SVG. -->
              {@html expand}</span>
          </button>
          <figcaption><span>{piece.title}</span><small>{c.filters[artworkFilters.findIndex(filter => filter === piece.group)]}</small></figcaption>
        </figure>
      {/each}
    </div>
    <MicroIconKit {locale} />
    <p class="artwork-notice">{c.artworkRights} <a href="#license">{c.fullLicense} <span aria-hidden="true">↗</span></a></p>
  </div>
</section>
<dialog id="artwork-dialog" aria-labelledby="artwork-title" aria-describedby="artwork-description">
  <div class="dialog-top"><span>Nery Mizuki</span><form method="dialog"><button class="icon-button" aria-label={c.closeArtwork}>×</button></form></div>
  <div class="dialog-image"><img id="artwork-large" alt="" /></div>
  <div class="dialog-caption" aria-live="polite" aria-atomic="true"><h2 id="artwork-title">{c.galleryTitle}</h2><p id="artwork-description"></p></div>
  <div class="dialog-navigation"><button type="button" id="artwork-previous"><span aria-hidden="true">←</span> {c.previousArtwork}</button><button type="button" id="artwork-next">{c.nextArtwork} <span aria-hidden="true">→</span></button></div>
  <p class="dialog-rights">© 2026 Yuri Cunha · {c.rights}</p>
</dialog>

<style>
  .gallery-links {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px 20px;
    font-size: .8125rem;
  }
</style>
