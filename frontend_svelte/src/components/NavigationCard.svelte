<script lang="ts">
	import Card from '$components/Card.svelte';
	import { v4 } from 'uuid';
	import type { Snippet } from 'svelte';
	let { title, href, children }: { title: string; href: string; children: Snippet } = $props();
</script>

{#snippet header()}
	<a {href} class="link link-animated link-base-content">
		<h5 class="title-small md:title lg:title-large text-base-content card-title">
			{title}
		</h5>
	</a>
{/snippet}

<!-- {#snippet footer()}
	<div class="card-actions text-center">
		<a {href}
			><button
				class="label-small btn btn-primary text-primary-content shadow-primary rounded-full px-3 shadow-sm hover:shadow-none"
				>Link to {title.toLowerCase()}</button
			></a
		>
	</div>
{/snippet} -->

<Card id={v4()} {header}>
	<p class="body-small md:body text-base-content-variant">
		{@render children?.()}
	</p>
</Card>
