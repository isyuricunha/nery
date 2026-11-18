<script lang="ts">
import { resolve } from '$app/paths';
import PageHead from '../layouts/PageHead.svelte';
import { messages } from '../i18n/messages';
const c = messages.en;
const pt = messages['pt-br'];
</script>

<PageHead locale="en" notFound />
<a class="skip" href="#main">{c.skip}</a>
  <main id="main" tabindex="-1" class="error-page wrap">
    <p class="eyebrow">404 / NERY MIZUKI</p>
    <h1>{c.notFoundTitle}</h1><p>{c.notFoundText}</p><a class="button primary" href={resolve('/')}>{c.returnHome}</a>
    <div lang="pt-BR"><h2>{pt.notFoundTitle}</h2><p>{pt.notFoundText}</p><a class="text-link" href={resolve('/pt-br')}>{pt.returnHome} <span aria-hidden="true">→</span></a></div>
  </main>
