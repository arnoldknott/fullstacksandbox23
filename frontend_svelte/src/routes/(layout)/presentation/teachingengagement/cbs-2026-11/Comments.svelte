<script module lang="ts">
	import type { SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended } from '$lib/types';

	export function updateVotes(
		socketio: SocketIO<MessageExtended> | undefined,
		answer: MessageExtended,
		comment: string,
		votes: number
	) {
		if (!comment) return;
		if (!socketio?.parentId) return;
		socketio.submitEntity(
			{ ...answer, content: JSON.stringify({ votes, comment }) },
			socketio.parentId
		);
	}
</script>

<script lang="ts">
	import Icon from '@iconify/svelte';
	import { flip } from 'svelte/animate';
	import { slide } from 'svelte/transition';

	import CommentAnswer from './CommentAnswer.svelte';
	import CommentInput from './CommentInput.svelte';
	let {
		socketio,
		presenterMode
	}: { socketio?: SocketIO<MessageExtended>; presenterMode?: boolean } = $props();

	let showInputs = $state(true);
	let commentsAnswersSorted = $derived(
		socketio?.getSelectedEntities('sortedCommentsAnswers') ?? []
	);
	let name = $state('');
</script>

<div class="flex min-h-0 w-full flex-1 flex-col px-5">
	<div class="w-full shrink-0 text-left">
		<div class="heading mb-6 flex w-full justify-between text-6xl">
			<div class="flex flex-col">
				<span class="mb-5">⁉️ Do you have comments or questions?</span>
				<span>📚 Which books do you want me to read?</span>
			</div>
			{#if presenterMode}
				<button
					type="button"
					class="btn btn-circle btn-lg btn-gradient btn-base-300 collapse-toggle"
					aria-label="Toggle inputs"
					onclick={() => (showInputs = !showInputs)}
					onkeydown={() => (showInputs = !showInputs)}
				>
					<Icon
						icon="tabler:chevron-down"
						class="{showInputs ? 'rotate-180' : ''} size-6 transition-all duration-300"
					/>
					<Icon
						icon="tabler:chevron-down"
						class="{!showInputs ? 'rotate-180' : ''} hidden size-6 transition-all duration-300"
						role="button"
					/>
				</button>
			{/if}
		</div>
		{#if showInputs}
			<div transition:slide={{ duration: 600 }}>
				<CommentInput {socketio} bind:name />
			</div>
		{/if}
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
	<div class="heading mt-4 min-h-0 flex-1 overflow-y-auto">
		<div class="grid grid-cols-3 gap-6 pr-5">
			{#each commentsAnswersSorted as answer, index (answer.id)}
				{@const content = JSON.parse(answer.content)}
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
						bind:votes={
							() => content.votes, (votes) => updateVotes(socketio, answer, content.comment, votes)
						}
						{index}
					>
						{content.comment}
					</CommentAnswer>
				</div>
			{/each}
		</div>
	</div>
	<div class="mr-20 shrink-0 text-right text-xl">
		By entering your text here, you agree to the <a
			href="#terms-and-conditions"
			class="link link-animated">terms and conditions</a
		>.
	</div>
</div>
