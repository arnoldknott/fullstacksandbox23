<script lang="ts">
	// import RevealJs from './RevealJS.svelte';
	import type { Snippet } from 'svelte';

	import Card from '$components/Card.svelte';

	import Title from './Title.svelte';
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
	<Title id={title}><a href={link}>{title}</a></Title>
	{@render children?.()}
</Card>
