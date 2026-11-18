<script lang="ts">
  import { microIcons } from '../../generated/web-art';
  import { messages, type Locale } from '../../i18n/messages';

  const { locale }: { locale: Locale } = $props();
  const c = $derived(messages[locale]);
</script>

<section id="micro-icons" aria-labelledby="micro-icons-title">
  <header>
    <div>
      <h3 id="micro-icons-title">{c.microKitTitle}</h3>
      <p>{c.microKitDescription}</p>
    </div>
    <a class="text-link" href="https://github.com/isyuricunha/nery/tree/main/assets/icons/micro">
      {c.microKitSource} <span aria-hidden="true">↗</span>
    </a>
  </header>
  <div class="micro-grid">
    {#each microIcons as { size, src } (size)}
      <figure>
        <div class="enlarged"><img {src} alt="" width="96" height="96" loading="lazy" decoding="async" /></div>
        <figcaption>
          <img {src} alt="" width={size} height={size} loading="lazy" decoding="async" />
          <span>{size} px</span>
        </figcaption>
      </figure>
    {/each}
  </div>
  <p class="scale-note">{c.microKitScale}</p>
</section>

<style>
  section {
    margin-top: clamp(32px, 5vw, 64px);
  }
  header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: end;
    gap: 8px 24px;
    margin-bottom: 18px;
  }
  h3 {
    font-size: clamp(1.5rem, 2.6vw, 2.25rem);
  }
  header p {
    max-width: 56ch;
    margin-top: 8px;
  }
  .micro-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 8rem), 1fr));
    gap: clamp(8px, 2vw, 20px);
  }
  figure {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 16px;
    overflow: hidden;
  }
  .enlarged {
    display: grid;
    place-items: center;
    padding: 16px 8px;
  }
  .enlarged img {
    image-rendering: pixelated;
  }
  figcaption {
    min-height: 62px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    background: #17191c;
    border-top: 1px solid var(--line);
    font-size: .875rem;
    font-variant-numeric: tabular-nums;
  }
  .scale-note {
    margin-top: 8px;
    font-size: .8125rem;
  }
</style>
