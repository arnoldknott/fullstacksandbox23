<script lang="ts">
	import Card from '$components/Card.svelte';
	import { v4 } from 'uuid';
	import type { Snippet } from 'svelte';
	let { title, href, children }: { title: string; href: string; children: Snippet } = $props();
</script>

{#snippet header()}
	<h5 class="text-title-small md:text-title lg:text-title-large base-content card-title">
		{title}
	</h5>
{/snippet}

{#snippet footer()}
	<div class="card-actions text-center">
		<a {href}
			><button
				class="text-label-small btn btn-primary rounded-full px-3 text-primary-content shadow-primary"
				>Link to {title.toLowerCase()}</button
			></a
		>
	</div>
{/snippet}

<Card id={v4()} {header} {footer}>
	<p class="text-body-small md:text-body text-primary">
		{@render children?.()}
	</p>
</Card>
