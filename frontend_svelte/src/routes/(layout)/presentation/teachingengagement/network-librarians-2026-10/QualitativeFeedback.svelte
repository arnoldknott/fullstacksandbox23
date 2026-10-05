<script lang="ts">
	import { marked } from 'marked';

	import CardOverlay from './CardOverlay.svelte';

	let { content }: { content: string } = $props();
</script>

<CardOverlay
	class="bg-primary  markdown-comment   text-primary-content z-50 pt-6 text-6xl "
	hidden={false}
	// bind:hidden={hideModules.openQuestions}
>
	<!-- eslint-disable-next-line svelte/no-at-html-tags -->
	{@html marked.parse(content, {
		async: false
	})}
</CardOverlay>

<style>
	:global(.reveal .markdown-comment h1),
	:global(.reveal .markdown-comment h2),
	:global(.reveal .markdown-comment h3),
	:global(.reveal .markdown-comment h4),
	:global(.reveal .markdown-comment h5),
	:global(.reveal .markdown-comment h6) {
		color: currentColor;
		font-size: inherit;
		font-weight: 700;
		text-wrap: balance;
		line-height: 1.2;
		margin: 0 0 0.75rem 0;
	}
</style>
