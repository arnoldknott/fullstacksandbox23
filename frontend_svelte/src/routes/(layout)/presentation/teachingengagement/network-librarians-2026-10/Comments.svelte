<script lang="ts">
	import { flip } from 'svelte/animate';

	import { Action } from '$lib/accessHandler';
	import { type SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended, QuestionExtended } from '$lib/types';
	let {
		socketio,
		question
	}: { socketio?: SocketIO<MessageExtended>; question?: QuestionExtended } = $props();

	let commentsAnswersSorted = $derived(
		socketio?.getSelectedEntities('sortedCommentsAnswers') ?? []
	);
</script>

<div class="r-stretch mx-10 mt-10">
	<div class="text-left">
		{#if socketio?.pendingEntities[0]}
			<label class="heading text-6xl" for="sharing"> Do you have comments or questions? 🤔 </label>
			<textarea
				class="heading placeholder:title-large w-[90%] resize-none border border-2 p-2 shadow-inner placeholder:italic"
				placeholder="Please type here - sharing is caring 🫶 - Press Enter to send."
				id="sharing"
				bind:value={socketio.pendingEntities[0].content}
				onkeydown={(event) => {
					if (event.key === 'Enter' && !event.shiftKey) {
						event.preventDefault();
						socketio.addPendingAccessPolicy(socketio.pendingEntities[0].id, {
							public: true,
							action: Action.READ
						});
						socketio.submitEntity(socketio.pendingEntities[0], question?.id, true);
						socketio.createPending();
					}
				}}></textarea>
		{:else}
			<div class="label text-error">
				<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
			</div>
		{/if}
	</div>

	{#snippet messageAnswer(text: string, date: Date | undefined, index: number)}
		<div class="chat chat-receiver">
			<div
				class="chat-bubble text-left text-wrap break-words {index % 2
					? 'chat-bubble-accent'
					: 'chat-bubble-primary'}"
			>
				{text}
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
	{/snippet}
	<div class="heading mt-8">
		<div class="mx-5 grid max-h-[600px] grid-cols-3 gap-6 overflow-y-auto">
			{#each commentsAnswersSorted as answer, index (answer.id)}
				<div animate:flip={{ duration: 300 }}>
					{@render messageAnswer(answer.content, answer.creation_date, index)}
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
