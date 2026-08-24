<script lang="ts">
	import type { RevealApi } from 'reveal.js';

	import RevealJs from '$components/RevealJS.svelte';

	let revealInstance = $state<RevealApi | undefined>(undefined);
</script>

<RevealJs bind:reveal={revealInstance}>
	<section>
		<div class="text-[200px] font-bold">Welcome</div>
	</section>
</RevealJs>
