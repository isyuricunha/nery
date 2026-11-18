<script lang="ts">
import { animationAtlases } from "../../generated/web-art";
import SpeechBubble from './SpeechBubble.svelte';
import { messages, type Locale } from '../../i18n/messages';
const { locale }: { locale: Locale } = $props();
const c = $derived(messages[locale]);
</script>

<section id="pet" class="section studio-section" aria-labelledby="studio-heading">
  <div class="wrap">
    <div class="section-heading">
      <div><p class="eyebrow">{c.petNumber}</p><h2 id="studio-heading">{c.petTitle}</h2></div>
      <p>{c.petDescription}</p>
    </div>
    <div class="studio-grid">
      <article class="studio-card" aria-labelledby="everyday-title">
        <div class="studio-card-heading"><span class="live-dot" aria-hidden="true"></span><h3 id="everyday-title">{c.everyday}</h3></div>
        <div class="pet-stage">
          <button type="button" class="pet-hit" id="preview-hit" aria-label={c.hello} disabled><canvas id="pet-preview" data-atlas={animationAtlases.motion} width="192" height="208" aria-hidden="true"></canvas></button>
          <SpeechBubble id="preview-speech" closeLabel={c.dismiss} />
          <span class="stage-ground" aria-hidden="true"></span><p id="pet-state" role="status" aria-live="polite">{c.states[0]}</p>
        </div>
        <div class="pet-controls" role="group" aria-label={c.petControls}>{#each c.states as state, i (state)}<button type="button" data-state={i} aria-pressed={i === 0} disabled>{state}</button>{/each}</div>
        <p class="studio-card-hint">{c.everydayHint}</p>
      </article>
      <article class="studio-card occasion-card" aria-labelledby="occasion-title">
        <div class="studio-card-heading"><span class="star-mark" aria-hidden="true">✦</span><h3 id="occasion-title">{c.special}</h3></div>
        <div class="pet-stage occasion-stage">
          <button type="button" class="pet-hit" id="occasion-hit" aria-label={c.occasionPlay} disabled><canvas id="occasion-preview" data-atlas={animationAtlases.occasions} width="256" height="277" aria-hidden="true"></canvas></button>
          <SpeechBubble id="occasion-speech" closeLabel={c.dismiss} />
          <span class="stage-ground" aria-hidden="true"></span><p id="occasion-state" role="status" aria-live="polite">{c.occasionStates[0]}</p>
        </div>
        <div class="pet-controls occasions-controls" role="group" aria-label={c.occasionControls}>{#each c.occasionStates as state, i (state)}<button type="button" data-occasion={i} aria-pressed={i === 0} disabled>{state}</button>{/each}</div>
        <p class="studio-card-hint">{c.specialHint}</p>
        <div class="speech-tools"><button id="speech-another" type="button">{c.saySomething} <span aria-hidden="true">↗</span></button></div>
      </article>
    </div>
    <p class="studio-note">{c.studioNote}</p>
    <noscript><p class="notice">{c.noScript}</p></noscript>
  </div>
</section>
