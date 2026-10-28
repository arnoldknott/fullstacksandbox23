<script lang="ts">
	import Icon from '@iconify/svelte';
	import type { RevealApi } from 'reveal.js';
	import { untrack } from 'svelte';

	import { page } from '$app/state';
	import { Action } from '$lib/accessHandler';
	import type { SocketIO, SocketioStatus } from '$lib/socketio.svelte';
	import type { QuestionExtended } from '$lib/types';

	import LoginOutButton from '../../../LoginOutButton.svelte';
	import { currentInput, type InputQuestion, presentationStatePrefix } from './inputs';

	let {
		revealInstance,
		socketio
	}: { revealInstance?: RevealApi; socketio?: SocketIO<QuestionExtended> } = $props();
	let loggedIn = $derived(Boolean(page.data.session?.loggedIn && page.data.session.sessionId));
	let question = $derived(socketio?.entities[0]);
	let canPublish = $derived(
		loggedIn && (question?.access_right === Action.WRITE || question?.access_right === Action.OWN)
	);
	let lastRequestedState: string | undefined;

	const slideInputs: Record<string, InputQuestion> = {
		'context-map': 'cbs-places',
		'inspiration-books': 'cbs-books',
		'comments-and-questions': 'cbs-comments'
	};

	const setPresentationState = (inputQuestion: InputQuestion | null) => {
		if (!canPublish || !socketio || !question) return;
		const nextState = inputQuestion
			? inputQuestion.replace('cbs-', presentationStatePrefix)
			: presentationStatePrefix;
		if (
			nextState === lastRequestedState ||
			(!lastRequestedState && nextState === question.question)
		)
			return;
		lastRequestedState = nextState;
		socketio.submitEntity({ ...question, question: nextState });
	};

	$effect(() => {
		const socket = socketio?.client;
		if (!socket) return;
		const transferred = (entity: QuestionExtended) => {
			if (entity.id === question?.id) lastRequestedState = undefined;
		};
		const status = (event: SocketioStatus) => {
			if ('error' in event) lastRequestedState = undefined;
		};
		socket.on('transferred', transferred);
		socket.on('status', status);
		return () => {
			socket.off('transferred', transferred);
			socket.off('status', status);
		};
	});

	$effect(() => {
		const reveal = revealInstance;
		if (!reveal || !canPublish) return;
		const publishCurrentSlide = (event?: Event) => {
			const slide =
				(event as (Event & { currentSlide?: HTMLElement }) | undefined)?.currentSlide ??
				reveal.getCurrentSlide();
			const inputQuestion = slideInputs[slide?.id ?? ''];
			if (inputQuestion) setPresentationState(inputQuestion);
		};
		reveal.on('ready', publishCurrentSlide);
		reveal.on('slidechanged', publishCurrentSlide);
		if (reveal.isReady()) untrack(() => publishCurrentSlide());
		return () => {
			reveal.off('ready', publishCurrentSlide);
			reveal.off('slidechanged', publishCurrentSlide);
		};
	});
</script>

{#if !loggedIn || canPublish}
	{#if currentInput(question?.question) && question?.question !== presentationStatePrefix}
		<button
			class="btn btn-warning-container shadow-base-shadow ml-2 rounded-full shadow"
			disabled={!canPublish}
			onclick={() => setPresentationState(null)}
		>
			<Icon icon="tabler:rotate-counterclockwise" class="size-5" />Reset
		</button>
	{/if}
	{#if !loggedIn}
		<LoginOutButton
			loggedIn={false}
			targetUrl={`${page.url.pathname}${page.url.search}${page.url.hash}`}
		/>
	{/if}
{/if}
