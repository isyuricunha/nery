<script lang="ts">
interface Props { id: string; closeLabel: string }
const { id, closeLabel }: Props = $props();
</script>

<div class="speech-bubble" id={id} hidden>
  <p role="status" aria-live="polite" aria-atomic="true"></p>
  <button type="button" class="speech-close" aria-label={closeLabel}>×</button>
</div>
