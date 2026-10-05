<script lang="ts">
	import type { BookType } from './Library.svelte';
	let { book, showModal = $bindable() }: { book: BookType; showModal: string } = $props();
</script>

<button
	class="btn btn-secondary-container shadow-base-shadow h-90 w-65 overflow-hidden rounded-3xl p-0 shadow-lg"
	onclick={() => {
		showModal = book.id;
	}}
>
	{#if book.image !== '#'}
		<img src={book.image} alt={book.alt} class="book-cover h-full w-full rounded-3xl object-fill" />
	{:else}
		<div class="text-wrap">{book.title}</div>
		<div class="text-3xl text-wrap">{book.author}</div>
	{/if}
</button>

<style>
	.book-cover {
		max-width: none;
		max-height: none;
		margin: 0;
		border: 0;
		display: block;
	}
</style>
