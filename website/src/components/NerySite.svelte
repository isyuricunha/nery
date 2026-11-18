<script lang="ts">
import { resolve } from '$app/paths';
import { onMount } from "svelte";
import PageHead from "../layouts/PageHead.svelte";
import { heroImages } from "../generated/web-art";
import { messages, type Locale } from '../i18n/messages';
import ArtworkGallery from './site/ArtworkGallery.svelte';
import AnimationStudio from './site/AnimationStudio.svelte';
import SpeechBubble from './site/SpeechBubble.svelte';
import arrow from 'lucide-static/icons/arrow-up-right.svg?raw';
import sliders from 'lucide-static/icons/sliders-horizontal.svg?raw';
const { locale }: { locale: Locale } = $props();
const c = $derived(messages[locale]);
const repo = 'https://github.com/isyuricunha/nery';
const heroSizes = '(max-width: 760px) 80vw, (max-width: 1200px) 42vw, 490px';

onMount(() => {
  // Each locale is a full document navigation, so these modules initialize once.
  void import('../scripts/site');
  void import('../scripts/gallery');
  void import('../scripts/pet');
  void import('../scripts/occasions');
});
</script>

<PageHead {locale} />
<a class="skip" href="#main">{c.skip}</a>
  <header class="site-header">
    <div class="header-inner wrap">
      <a class="brand" href="#main"><span class="brand-mark" aria-hidden="true">N<span>/</span>M</span><span>Nery Mizuki<small>{c.footerMascot}</small></span></a>
      <nav class="main-nav" aria-label={c.navigation}>
        <a href="#identity">{c.identity}</a><a href="#pet">{c.pet}</a><a href="#kit">{c.kit}</a><a href="#usage">{c.usage}</a>
      </nav>
      <div class="header-actions">
        <details class="preferences" id="preferences">
          <summary>
            <span class="icon" aria-hidden="true"><!-- eslint-disable-next-line svelte/no-at-html-tags -- Trusted Lucide SVG. -->
              {@html sliders}</span>
            <span>{c.settings}</span>
          </summary>
          <div class="preferences-panel">
            <h2>{c.settings}</h2>
            <nav class="language-settings" aria-labelledby="language-heading" aria-describedby="language-help">
              <h3 id="language-heading">{c.language}</h3>
              <p id="language-help">{c.languageHelp}</p>
              <div class="language-options">
                <a href={resolve('/?lang=auto')} data-language="auto">{c.languageAuto}</a>
                <a href={resolve('/?lang=en')} data-language="en" lang="en" hreflang="en" aria-current={locale === 'en' ? 'true' : undefined}>English</a>
                <a href={resolve('/pt-br')} data-language="pt-br" lang="pt-BR" hreflang="pt-BR" aria-current={locale === 'pt-br' ? 'true' : undefined}>Português (Brasil)</a>
              </div>
            </nav>
            <label class="setting-row"><span>{c.motionSetting}</span><input type="checkbox" id="motion-enabled" checked disabled aria-describedby="motion-help" /></label>
            <p id="motion-help">{c.motionHelp}</p>
            <label class="setting-row"><span>{c.walkerSetting}</span><input type="checkbox" id="walker-enabled" checked disabled aria-describedby="walker-help" /></label>
            <p id="walker-help">{c.walkerHelp}</p>
            <label class="setting-row"><span>{c.speechSetting}</span><input type="checkbox" id="speech-toggle" checked disabled aria-describedby="speech-help" /></label>
            <p id="speech-help">{c.speechHelp}</p>
          </div>
        </details>
      </div>
    </div>
  </header>
  <main id="main" tabindex="-1">
    <section class="hero wrap" aria-labelledby="hero-title">
      <div class="hero-copy">
        <p class="eyebrow"><span class="small-star" aria-hidden="true">✦</span> {c.eyebrow}</p>
        <h1 id="hero-title">Nery<br /><span>Mizuki.</span></h1>
        <p class="tagline">{c.yuri} <em>{c.mascot}</em></p>
        <p class="hero-description">{c.intro} {c.introEnd}</p>
        <div class="hero-actions"><a class="button primary" href="#pet">{c.hello}<span aria-hidden="true">↗</span></a><a class="text-link" href="#kit">{c.explore}<span aria-hidden="true">→</span></a></div>
        <div class="hero-signature"><span class="signature-line" aria-hidden="true"></span><p>{c.heroNote}</p></div>
      </div>
      <figure class="hero-art">
        <div class="portrait-frame">
          <span class="portrait-orbit" aria-hidden="true"></span><span class="portrait-star" aria-hidden="true">✦</span>
          <picture>
            <source srcset={heroImages.avif} type="image/avif" sizes={heroSizes} />
            <source srcset={heroImages.webp} type="image/webp" sizes={heroSizes} />
            <img src={heroImages.fallback} srcset={heroImages.png} sizes={heroSizes} alt={c.portraitAlt} width="745" height="905" loading="eager" fetchpriority="high" decoding="async" />
          </picture>
          <span class="portrait-badge"><span aria-hidden="true">✦</span> {c.heroBadge}</span>
        </div>
        <figcaption>{c.heroCaption}</figcaption>
      </figure>
    </section>
    <section id="identity" class="identity-section section wrap" aria-labelledby="identity-heading">
      <div class="identity-intro"><p class="eyebrow">{c.identityNumber}</p><h2 id="identity-heading">{c.identityHeading}</h2><p>{c.identityShort}</p><a class="text-link" href="https://yuricunha.com">{c.meetYuri}<span aria-hidden="true">↗</span></a></div>
      <div class="traits">{#each c.traits as trait, i (trait)}<article class="trait"><span aria-hidden="true">{['✦','♡','⌂'][i]}</span><div><h3>{trait}</h3><p>{c.traitDescriptions[i]}</p></div></article>{/each}</div>
    </section>
    <AnimationStudio locale={locale} />
    <ArtworkGallery locale={locale} />
    <section id="usage" class="section details-section wrap" aria-labelledby="details-heading">
      <div class="section-heading"><div><p class="eyebrow">{c.usageNumber}</p><h2 id="details-heading">{c.detailsTitle}</h2></div><p>{c.detailsDescription}</p></div>
      <div class="details-grid">
        <div class="identity-details">
          <details open><summary>{c.appearanceTitle}</summary><div class="detail-content"><p>{c.appearance}</p><p>{c.style}</p><ul class="swatches" aria-label={c.canonical}>{#each [['#211915','Charcoal'],['#2A211D','Warm'],['#CC785C','Terracotta'],['#F0E9E3','Cream'],['#B9A195','Muted']] as [color, label] (color)}<li><span class="swatch" style={`--swatch:${color}`} aria-hidden="true"></span><span>{c.palette[label as keyof typeof c.palette]}<small>{color}</small></span></li>{/each}</ul></div></details>
          <details><summary>{c.rulesTitle}</summary><div class="detail-content"><ul class="rules">{#each [c.ruleHair,c.rulePurple,c.ruleRobot,c.ruleLogo,c.ruleRedraw,c.ruleLicense] as rule (rule)}<li>{rule}</li>{/each}</ul></div></details>
          <details><summary>{c.expressionsTitle}</summary><div class="detail-content table-wrap"><table><caption class="sr-only">{c.expressionGuide}</caption><thead><tr><th scope="col">{c.context}</th><th scope="col">{c.suggestion}</th></tr></thead><tbody>{#each c.expressions as [context, expression] (context)}<tr><td>{context}</td><td>{expression}</td></tr>{/each}</tbody></table></div></details>
          <details><summary>{c.integrationTitle}</summary><div class="detail-content"><p>{c.usageDescription}</p><p>{c.surfaceText} <a href="https://github.com/isyuricunha/nery/blob/main/docs/IDENTITY.md">{c.identityRules}</a>{c.surfaceEnd}</p></div></details>
        </div>
        <aside id="license" class="license-card" aria-labelledby="license-title"><p class="eyebrow">© 2026 YURI CUNHA</p><h3 id="license-title">{c.licenseSummary}</h3><p>{c.licenseDetail}</p><a class="button" href="https://github.com/isyuricunha/nery/blob/main/assets/mascot/LICENSE.md">{c.fullLicense}<span class="icon" aria-hidden="true"><!-- eslint-disable-next-line svelte/no-at-html-tags -- Trusted Lucide SVG. -->
            {@html arrow}</span></a><p class="license-separation">{c.licenseSeparation}</p></aside>
      </div>
      <div class="faq"><h3>{c.faqTitle}</h3><div>{#each c.faqQuestions as question, i (question)}<details><summary>{question}</summary><div class="detail-content"><p>{c.faqAnswers[i]}</p></div></details>{/each}</div></div>
    </section>
  </main>
  <footer class="site-footer"><div class="wrap"><div class="footer-top"><div><a class="footer-name" href="#main">Nery Mizuki<span aria-hidden="true">✦</span></a><p>{c.footerNote}</p></div><a class="text-link" href="#main">{c.backTop}<span aria-hidden="true">↑</span></a></div><div class="footer-bottom"><p>© 2026 <a href="https://yuricunha.com">Yuri Cunha</a> · {c.rights}</p><nav aria-label={c.elsewhere}><a href={repo}>GitHub</a><a href="https://gitlab.com/isyuricunha/nery">GitLab</a><a href="https://git.yuricunha.com/isyuricunha/nery">YuGit</a></nav></div></div></footer>
  <div class="walker-shell"><SpeechBubble id="walker-speech" closeLabel={c.dismiss} /><button id="walker-hit" type="button" aria-label={c.walkerHello} disabled><canvas id="pet-walker" width="96" height="104" aria-hidden="true"></canvas></button></div>
