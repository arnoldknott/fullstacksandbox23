<script lang="ts">
	import '/src/app.css';

	import type { Snippet } from 'svelte';

	import ThemeApplier from '../../ThemeApplier.svelte';

	let { children }: { children: Snippet } = $props();
</script>

<div class="h-screen">
	<ThemeApplier>
		{@render children?.()}
	</ThemeApplier>
</div>
