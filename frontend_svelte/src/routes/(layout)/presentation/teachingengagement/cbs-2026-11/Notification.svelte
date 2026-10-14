<script lang="ts">
	import { type Snippet } from 'svelte';
	let { children }: { children: Snippet } = $props();
</script>

<p
	class="text-base-content-variant label-small bg-base-300 shadow-base-shadow rounded-xl p-2 shadow"
>
	{@render children()}
</p>
