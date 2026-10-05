<script lang="ts">
	import type { BookType } from './Library.svelte';
	let {
		book,
		commentCount = 0,
		showModal = $bindable()
	}: { book: BookType; commentCount?: number; showModal: string } = $props();
</script>

<div class="indicator">
	{#if commentCount > 0}
		<span
			class="indicator-item badge badge-accent h-9 w-9 rounded-full text-xl shadow-sm"
			aria-label={`${commentCount} ${commentCount === 1 ? 'comment' : 'comments'}`}
		>
			{commentCount}
		</span>
	{/if}
	<button
		class="btn btn-secondary-container shadow-base-shadow h-90 w-65 overflow-hidden rounded-3xl p-0 shadow-lg"
		onclick={() => {
			showModal = book.id;
		}}
	>
		{#if book.image !== '#'}
			<img
				src={book.image}
				alt={book.alt}
				class="book-cover h-full w-full rounded-3xl object-fill"
			/>
		{:else}
			<div class="text-wrap">{book.title}</div>
			<div class="text-3xl text-wrap">{book.author}</div>
		{/if}
	</button>
</div>

<style>
	.book-cover {
		max-width: none;
		max-height: none;
		margin: 0;
		border: 0;
		display: block;
	}
</style>
