<script lang="ts">
	import '../../app.css';
	// import { SessionStatus } from '$lib/session';
	// import { onMount, type Snippet } from 'svelte';
	import type { Snippet } from 'svelte';
	// import type { LayoutData } from './$types';
	// import { resolve } from '$app/paths';
	// import { goto } from '$app/navigation';
	// let { data, children }: { data: LayoutData; children: Snippet } = $props();
	let { children }: { children: Snippet } = $props();

	// TBD: show welcome modal as overlay - not a redirect!
	// onMount(() => {
	// 	if (data.session?.status === SessionStatus.REGISTRATION_PENDING) {
	// 		goto(resolve('/'));
	// 	}
	// });
</script>

<main>
	{@render children?.()}
</main>
