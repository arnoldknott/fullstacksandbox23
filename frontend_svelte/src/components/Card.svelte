<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		id,
		extraClasses,
		header,
		children,
		footer
	}: { id: string; extraClasses?: string; header?: Snippet; children: Snippet; footer?: Snippet } =
		$props();

	let showCard = $state(true);

	export const remove = () => {
		showCard = false;
	};
</script>

{#if showCard}
	<div
		class="card border-outline-variant bg-base-250 shadow-outline-variant w-full rounded-xl border-[1px] shadow-md {extraClasses}"
		{id}
	>
		{#if header}
			<div class="card-header">
				{@render header()}
			</div>
		{/if}
		<div class="card-body">
			{@render children()}
		</div>
		{#if footer}
			<div class="card-footer">
				{@render footer()}
			</div>
		{/if}
	</div>
{/if}

<!--
<div class="block rounded-lg bg-white text-left shadow-lg dark:bg-neutral-600">
	<div class="p-6">
		<a
			{href}
			class="mt-3 inline-block rounded-sm bg-blue-500 px-6 pb-2 pt-2.5 text-xs font-medium uppercase leading-normal text-white shadow-[0_4px_9px_-4px_#3b71ca] transition duration-150 ease-in-out hover:bg-blue-600 hover:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] focus:bg-blue-600 focus:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] focus:outline-hidden focus:ring-0 active:bg-blue-700 active:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] dark:shadow-[0_4px_9px_-4px_rgba(59,113,202,0.5)] dark:hover:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)] dark:focus:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)] dark:active:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)]"
		>
			<h5 class="mb-2 text-xl font-bold tracking-wide text-neutral-800 dark:text-neutral-50">
				{title}
			</h5>
		</a>

		<p class="mb-2 text-base text-neutral-500 dark:text-neutral-300">
			{description}
		</p>
	</div>
</div>
-->
<!-- Card -->
