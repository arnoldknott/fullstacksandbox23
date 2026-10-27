<script lang="ts">
	import { flip } from 'svelte/animate';

	import { type SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended } from '$lib/types';

	import CommentAnswer from './CommentAnswer.svelte';
	import CommentInput from './CommentInput.svelte';
	let { socketio }: { socketio?: SocketIO<MessageExtended> } = $props();

	let commentsAnswersSorted = $derived(
		socketio?.getSelectedEntities('sortedCommentsAnswers') ?? []
	);
	let name = $state('');
</script>

<div class="r-stretch mx-10 mt-10">
	<div class="text-left">
		<div class="heading mb-6 text-6xl">
			⁉️ Do you have comments or questions? <br />📚 Which books do you want me to read?
		</div>
		<CommentInput {socketio} bind:name />
	</div>

	<!-- {#snippet messageAnswer(name: string, text: string, date: Date | undefined, index: number)}
		<div class="chat chat-receiver">
			<div
				class="chat-bubble text-left text-wrap break-words {index % 2
					? 'chat-bubble-accent'
					: 'chat-bubble-primary'}"
			>
				<dl>
					<dt class="italic">{name || 'Anonymous'}:</dt>
					<dd>{text}</dd>
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
	{/snippet} -->
	<div class="heading mt-8">
		<div class="mx-5 grid max-h-[600px] grid-cols-3 gap-6 overflow-y-auto">
			{#each commentsAnswersSorted as answer, index (answer.id)}
				<div animate:flip={{ duration: 300 }}>
					<!-- {@render messageAnswer(
						answer.confidential || 'Anonymous',
						answer.content,
						answer.creation_date,
						index
					)} -->
					<CommentAnswer
						name={answer.confidential || 'Anonymous'}
						// date={answer.creation_date}
						{index}
					>
						{answer.content}
					</CommentAnswer>
				</div>
			{/each}
		</div>
	</div>
</div>
<div class="col-span-12 mr-20 text-right text-xl">
	By entering your text here, you agree to the <a
		href="#terms-and-conditions"
		class="link link-animated">terms and conditions</a
	>.
</div>
