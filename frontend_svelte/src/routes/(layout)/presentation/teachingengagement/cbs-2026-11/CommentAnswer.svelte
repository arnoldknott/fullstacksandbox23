<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		children,
		name,
		// date,
		votes = $bindable(0),
		index
	}: {
		children: Snippet;
		name: string; // date: Date | undefined;
		votes?: number;
		index: number;
	} = $props();

	let voted = $state(false);
</script>

<div class="indicator mt-5 w-full">
	<span
		class="indicator-item badge badge-neutral mr-12 h-9 w-9 rounded-full text-xl shadow-sm"
		aria-label={voted ? 'Vote down' : 'Vote up'}
	>
		<button
			class="btn btn-gradient btn-circle btn-neutral-container"
			onclick={() => {
				voted = !voted;
				votes += voted ? 1 : -1;
			}}
		>
			{voted ? '-1' : '+1'}
		</button>
	</span>
	{#if votes > -1}
		<span
			class="indicator-item badge badge-neutral h-9 w-9 rounded-full text-xl shadow-sm"
			aria-label={`${votes} ${votes === 1 ? 'vote' : 'votes'}`}
		>
			{votes}
		</span>
	{/if}
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
			<!-- <div class="label text-right">
			{date
				? new Date(date).toLocaleString(undefined, {
						dateStyle: 'short',
						timeStyle: 'short'
					})
				: 'Thanks for your contribution 🙏'}
		</div> -->
		</div>
	</div>
</div>
