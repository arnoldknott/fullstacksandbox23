<script lang="ts">
	import '../../app.css';
	import { SessionStatus } from '$lib/session';
	import type { Snippet } from 'svelte';
	import type { LayoutData } from './$types';
	import { goto } from '$app/navigation';
	let { data, children }: { data: LayoutData; children: Snippet } = $props();

	if (data.session?.status === SessionStatus.REGISTRATION_PENDING) {
		goto('/(layout)/index');
	}
</script>

<main>
	{@render children?.()}
</main>
