<script lang="ts">
	import { type Snippet } from 'svelte';
	let { children }: { children?: Snippet } = $props();
</script>

<div class="flex h-screen min-h-fit w-full flex-col bg-background text-base-content">
	<div class="h-1/6 min-h-fit bg-background p-4">Background<br />{@render children?.()}</div>
	<div class="h-1/6 min-h-fit bg-base-100 p-4">base-100<br />{@render children?.()}</div>
	<div class="h-1/6 min-h-fit bg-base-150 p-4">base-150<br />{@render children?.()}</div>
	<div class="h-1/6 min-h-fit bg-base-200 p-4">base-200<br />{@render children?.()}</div>
	<div class="h-1/6 min-h-fit bg-base-250 p-4">base-250<br />{@render children?.()}</div>
	<div class="h-1/6 min-h-fit bg-base-300 p-4">base-300<br />{@render children?.()}</div>
</div>
