<script lang="ts">
	import { type Snippet } from 'svelte';
	let { children }: { children?: Snippet } = $props();
</script>

<div class="bg-background text-base-content flex h-screen min-h-fit w-full flex-col">
	<div class="bg-background h-1/6 min-h-fit p-4">Background<br />{@render children?.()}</div>
	<div class="bg-base-100 h-1/6 min-h-fit p-4">base-100<br />{@render children?.()}</div>
	<div class="bg-base-150 h-1/6 min-h-fit p-4">base-150<br />{@render children?.()}</div>
	<div class="bg-base-200 h-1/6 min-h-fit p-4">base-200<br />{@render children?.()}</div>
	<div class="bg-base-250 h-1/6 min-h-fit p-4">base-250<br />{@render children?.()}</div>
	<div class="bg-base-300 h-1/6 min-h-fit p-4">base-300<br />{@render children?.()}</div>
</div>
