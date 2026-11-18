<script lang="ts">
  import '../styles/site.css';
  import type { Snippet } from 'svelte';

  const { children }: { children: Snippet } = $props();
</script>

{@render children()}
