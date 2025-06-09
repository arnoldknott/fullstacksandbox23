<script lang="ts">
	import Card from '$components/Card.svelte';
	import Heading from './Heading.svelte';
	// import RevealJs from './RevealJS.svelte';
	import type { Snippet } from 'svelte';
	let { title, link, children }: { title: string; link: string; children: Snippet } = $props();
</script>

<!-- <md-filled-card class="w-80">
    {#if type === "revealJS"}
        <RevealJs>
            {@render children?.()}
        </RevealJs>
    {:else}
        {@render children?.()}
    {/if}
    {@render children?.()}
</md-filled-card> -->

<Card id={link}>
	<Heading><a href={link}>{title}</a></Heading>
	{@render children?.()}
</Card>
