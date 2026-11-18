<script lang="ts">
  import { profileCopy, profileImages as images } from '../../generated/web-art';
  import { messages, type Locale } from '../../i18n/messages';

  const { locale }: { locale: Locale } = $props();
  const c = $derived(messages[locale]);
  const profile = $derived(profileCopy[locale]);
</script>

<section id="profile-kit" aria-labelledby="profile-kit-title">
  <header>
    <div>
      <h3 id="profile-kit-title">{c.profileKitTitle}</h3>
      <p>{c.profileKitDescription}</p>
    </div>
    <a class="text-link" href="https://github.com/isyuricunha/nery/tree/main/assets/profile">
      {c.profileKitSource} <span aria-hidden="true">↗</span>
    </a>
  </header>
  <article class="profile-card">
    <picture class="profile-banner">
      <source media="(max-width: 640px)" srcset={images.compact.src} />
      <img src={images.banner.src} width={images.banner.width} height={images.banner.height}
        alt={c.profileKitBannerAlt} loading="lazy" decoding="async" />
    </picture>
    <div class="profile-details">
      <img class="profile-avatar" src={images.avatar.src} width="96" height="96"
        alt={c.profileKitAvatarAlt} loading="lazy" decoding="async" />
      <h4>{profile.name}</h4>
      <p class="profile-tagline">{profile.tagline}</p>
      <p>{profile.bio}</p>
    </div>
  </article>
  <div class="profile-extras">
    <figure>
      <div class="alternate-avatar">
        <img src={images.friendly.src} width="96" height="96" alt={c.profileKitFriendlyAlt}
          loading="lazy" decoding="async" />
      </div>
      <figcaption>{c.profileKitFriendly}</figcaption>
    </figure>
    <figure>
      <img class="background-preview" src={images.background.src} width={images.background.width}
        height={images.background.height} alt={c.profileKitBackgroundAlt} loading="lazy" decoding="async" />
      <figcaption>{c.profileKitBackground}</figcaption>
    </figure>
  </div>
</section>

<style>
  section {
    margin-top: clamp(32px, 5vw, 64px);
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
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
  article, figure {
    min-width: 0;
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: 16px;
    background: var(--surface);
  }
  .profile-banner {
    display: block;
    aspect-ratio: 3 / 1;
    background: var(--surface-raised);
  }
  .profile-banner img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .profile-details {
    position: relative;
    padding: 0 clamp(16px, 4vw, 36px) 24px;
  }
  .profile-avatar {
    position: relative;
    margin-top: -44px;
    margin-bottom: 12px;
    border: 4px solid var(--surface);
    border-radius: 50%;
    background: var(--surface-raised);
  }
  h4 {
    margin: 0;
    font-size: 1.375rem;
    line-height: 1.2;
  }
  .profile-tagline {
    color: var(--accent);
    margin: 4px 0 8px;
  }
  .profile-details p {
    max-width: 64ch;
  }
  .profile-extras {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 2fr);
    gap: 12px;
    margin-top: 12px;
  }
  .profile-extras figure {
    display: grid;
    grid-template-rows: 1fr auto;
  }
  .alternate-avatar {
    display: grid;
    place-items: center;
    min-height: 128px;
    padding: 12px;
  }
  .background-preview {
    height: clamp(128px, 21vw, 180px);
    width: 100%;
    object-fit: cover;
  }
  figcaption {
    border-top: 1px solid var(--line);
    padding: 8px 12px;
    font-size: .875rem;
  }
  @media (max-width: 640px) {
    .profile-banner { aspect-ratio: 5 / 2; }
    .profile-avatar { width: 72px; height: 72px; margin-top: -31px; }
    .profile-extras { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }
</style>
