<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		children,
		name,
		date,
		index
	}: { children: Snippet; name: string; date: Date | undefined; index: number } = $props();
</script>

<div class="chat chat-receiver w-full">
	<div
		class="chat-bubble w-full! max-w-full! text-left text-wrap break-words {index % 2
			? 'chat-bubble-accent'
			: 'chat-bubble-primary'}"
	>
		<dl class="ml-2!">
			<dt class="font-semibold italic">{name || 'Anonymous'}:</dt>
			<dd>{@render children()}</dd>
		</dl>
		<div class="label text-right">
			{date
				? new Date(date).toLocaleString(undefined, {
						dateStyle: 'short',
						timeStyle: 'short'
					})
				: 'Thanks for your contribution 🙏'}
		</div>
	</div>
</div>
