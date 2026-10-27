<script lang="ts">
	import Icon from '@iconify/svelte';
	import { onDestroy, onMount, untrack } from 'svelte';
	import { flip } from 'svelte/animate';
	import { fly } from 'svelte/transition';

	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { Action } from '$lib/accessHandler';
	import { SocketIO, type SocketioStatus } from '$lib/socketio.svelte';
	import type { MessageExtended, QuestionExtended } from '$lib/types';

	import CardOverlay from '../CardOverlay.svelte';
	import CommentAnswer from '../CommentAnswer.svelte';
	import CommentInput from '../CommentInput.svelte';
	import {
		currentInput,
		inputEnabled,
		inputOptions,
		type InputQuestion,
		selectedInput
	} from '../inputs';
	import { providedBooks } from '../Library.svelte';
	import Map, { type Place } from '../Map.svelte';
	import NameInput from '../NameInput.svelte';
	import Notification from '../Notification.svelte';
	import PlaceForm from '../PlaceForm.svelte';
	import TermsAndConditions from '../TermsAndConditions.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	let stateSocket = $state<SocketIO<QuestionExtended>>();
	let answerSocket = $state<SocketIO<MessageExtended>>();
	let questionsCommentsSocket = $state<SocketIO<MessageExtended>>();
	let name = $state('');
	let showQuestionInput = $state(false);
	let showNameInput = $state(true);
	let ownPlaces = $state<Place[]>([]);
	let comment = $state('');
	let bookComment = $state('');
	let bookIndex = $state(0);
	let bookDirection = $state(1);
	let direction = $state(1);
	let notice = $state('');
	let failed = $state(false);
	let previousCurrent: string | undefined;
	let submittedName: string | undefined;
	let hideTermsAndConditions = $state(true);

	let stateQuestion = $derived(
		stateSocket?.entities.find((question) => question.id === data.stateSnapshot.entities[0]?.id) ??
			(stateSocket ? undefined : data.stateSnapshot.entities[0])
	);
	let current = $derived(currentInput(stateQuestion?.question));
	let selected = $derived(selectedInput(page.url.searchParams.get('input'), current));
	let selectedIndex = $derived(inputOptions.findIndex((option) => option.question === selected));
	let book = $derived(providedBooks[bookIndex]);
	let previous = $derived(
		inputOptions
			.slice(0, Math.max(0, selectedIndex))
			.findLast((option) => inputEnabled(option.question, current))
	);
	let next = $derived(
		inputEnabled(inputOptions[selectedIndex + 1]?.question ?? '', current)
			? inputOptions[selectedIndex + 1]
			: undefined
	);

	const choose = (question: InputQuestion) => {
		if (!inputEnabled(question, current)) return;
		const nextIndex = inputOptions.findIndex((option) => option.question === question);
		direction = nextIndex < selectedIndex ? -1 : 1;
		const url = new URL(page.url);
		url.searchParams.set('input', question);
		if (url.href !== page.url.href)
			void goto(url, { replaceState: true, noScroll: true, keepFocus: true });
	};

	$effect(() => {
		const question = current ?? '';
		const requested = page.url.searchParams.get('input');
		const active = selected;
		if (previousCurrent !== undefined && previousCurrent !== question && current) {
			previousCurrent = question;
			untrack(() => choose(current!));
		} else {
			previousCurrent = question;
			if (active && active !== requested) untrack(() => choose(active));
		}
	});

	const receiveStatus = (status: SocketioStatus) => {
		if ('error' in status) {
			submittedName = undefined;
			failed = true;
			notice = 'Your contribution could not be sent. Please try again.';
		} else if (status.success === 'created') {
			failed = false;
			notice = 'Thank you for your contribution.';
		}
	};
	const submitting = () => {
		failed = false;
		notice = 'Sending...';
	};
	const submitName = () => {
		const confidentialName = name.trim();
		if (confidentialName && confidentialName !== submittedName) {
			const pending = answerSocket?.pendingEntities[0];
			const parentId = data.inputQuestions['cbs-names'];
			if (!answerSocket || !pending || !parentId) {
				failed = true;
				notice = 'The name input is unavailable. Please try again.';
				return;
			}
			pending.content = '';
			pending.confidential = confidentialName;
			answerSocket.addPendingAccessPolicy(pending.id, { public: true, action: Action.READ });
			answerSocket.submitEntity(pending, parentId, true);
			answerSocket.createPending();
			submittedName = confidentialName;
			submitting();
		}
		showNameInput = false;
	};
	const moveBook = (offset: number) => {
		bookDirection = offset;
		bookIndex = (bookIndex + offset + providedBooks.length) % providedBooks.length;
	};

	onMount(() => {
		if (data.stateSnapshot.entities.length)
			stateSocket = new SocketIO<QuestionExtended>(
				{ namespace: '/question' },
				{ snapshot: data.stateSnapshot }
			);
		answerSocket = new SocketIO<MessageExtended>(
			{ namespace: '/message' },
			{
				submitOnly: true,
				template: { content: '', confidential: '', language: 'en' },
				status: receiveStatus
			}
		);
		answerSocket.client.on('connect_error', () => {
			failed = true;
			notice = 'Connection unavailable. Please try again.';
		});
		questionsCommentsSocket = new SocketIO<MessageExtended>(
			{
				namespace: '/message',
				parentId: data.inputQuestions['cbs-comments'],
				queryParams: { 'request-access-data': true }
			},
			{
				snapshot: data.commentsSnapshot,
				template: { content: '', language: 'en' }
			}
		);
		questionsCommentsSocket.createSortedSelection('sortedCommentsAnswers', 'creation_date', false);
	});

	onDestroy(() => {
		stateSocket?.client.disconnect();
		answerSocket?.client.disconnect();
		questionsCommentsSocket?.client.disconnect();
	});

	let commentsAnswersSorted = $derived(
		questionsCommentsSocket?.getSelectedEntities('sortedCommentsAnswers') ?? []
	);
</script>

<svelte:head><title>Presentation inputs</title></svelte:head>

<div class="bg-base-100 text-base-content mx-auto flex min-h-dvh w-full max-w-2xl flex-col">
	<header
		class="border-base-content/15 flex min-h-20 items-center justify-between gap-2 border-b px-4 py-3"
	>
		<button
			class="btn btn-secondary btn-circle btn-sm btn-gradient shadow-base-shadow shadow"
			aria-label="Previous input"
			title="Previous input"
			disabled={!previous}
			onclick={() => previous && choose(previous.question)}
		>
			<Icon icon="tabler:chevron-left" class="size-6" />
		</button>
		<div class="title min-w-0 flex-1 text-center">
			{inputOptions.find((option) => option.question === selected)?.label ?? 'Welcome'}
		</div>
		<button
			class="btn btn-secondary btn-circle btn-sm btn-gradient shadow-base-shadow shadow"
			aria-label="Next input"
			title="Next input"
			disabled={!next}
			onclick={() => next && choose(next.question)}
		>
			<Icon icon="tabler:chevron-right" class="size-6" />
		</button>
		<button
			class="btn btn-text btn-circle text-secondary btn-sm"
			aria-label="Ask a question or leave a comment"
			title="Ask a question or leave a comment"
			onclick={() => (showQuestionInput = !showQuestionInput)}
		>
			<Icon icon="fluent-emoji-high-contrast:exclamation-question-mark" class="size-6" />
		</button>
		<button
			class="btn btn-text btn-circle text-secondary btn-sm mr-2"
			aria-label="Change your name"
			title="Change your name"
			onclick={() => (showNameInput = !showNameInput)}
		>
			<Icon icon="fa6-solid:user" class="size-6" />
		</button>
	</header>

	{#snippet questionsComments(closeButton: boolean = false)}
		<div class="flex-between flex gap-2">
			<h2 class="mb-4 text-lg font-semibold">
				⁉️ Do you have comments or questions?
				<!-- <br /> -->
				<!-- 📖 Which books would you recommend? -->
			</h2>
			<!-- {#if closeButton}
				<button
					class="btn btn-circle btn-text btn-sm absolute end-3 top-3"
					aria-label="Close"
					title="Close"
					onclick={() => (showQuestionInput = false)}
				>
					<Icon icon="tabler:x" class="size-5" />
				</button>
			{/if} -->
		</div>
		{#if data.inputQuestions['cbs-comments']}<CommentInput
				socketio={answerSocket}
				parentId={data.inputQuestions['cbs-comments']}
				bind:name
				bind:text={comment}
				onsubmit={submitting}
				oncancel={closeButton ? () => (showQuestionInput = false) : undefined}
			/>
		{:else}
			<p>This input is unavailable.</p>
		{/if}
		<div class="mt-8 max-h-[600px] w-full gap-4 overflow-y-auto">
			{#each commentsAnswersSorted as answer, index (answer.id)}
				<div animate:flip={{ duration: 300 }}>
					<CommentAnswer
						name={answer.confidential || 'Anonymous'}
						// date={answer.creation_date}
						{index}
					>
						{answer.content}
					</CommentAnswer>
					<!-- <div class="border-base-content/15 border-b p-4">
					<div class="font-semibold">{answer.confidential || 'Anonymous'}</div>
					<div>{answer.content}</div>
					<div class="text-base-content/60 text-sm">index {index}</div>
				</div> -->
				</div>
			{/each}
		</div>
	{/snippet}

	{#if showNameInput}
		<form
			class="border-base-content/15 grid gap-4 border-b p-4"
			onsubmit={(event) => {
				event.preventDefault();
				submitName();
			}}
		>
			<div class="text-xl font-semibold">How shall we call you?</div>
			<NameInput bind:name />
			<Notification>
				If you leave it empty, you participate as "Anonymous".<br /> You can change your name at any
				time clicking the
				<Icon icon="fa6-solid:user" class="inline size-3" /> button in the upper right corner.
			</Notification>
			<!-- <p
				class="text-base-content-variant label-small bg-base-300 shadow-base-shadow rounded-xl p-2 shadow"
			>
				If you leave it empty, you participate as "Anonymous".<br /> You can change your name at any
				time clicking the
				<Icon icon="fa6-solid:user" class="inline size-3" /> button in the upper right corner.
			</p> -->
			<button
				class="btn btn-primary-container btn-gradient justify-self-end rounded-full"
				type="submit">Continue</button
			>
		</form>
	{:else if showQuestionInput}
		{@render questionsComments(true)}
	{:else}
		<main class="relative flex-1 overflow-x-clip p-4">
			{#key selected}
				<div in:fly={{ x: direction * 48, duration: 180 }}>
					{#snippet waitingForPresenter()}
						<div class="display-small break-words">Welcome {name.trim() || 'Anonymous'}</div>
						<div class="label-small">
							<Icon icon="svg-spinners:12-dots-scale-rotate" class="inline size-3" /> Stay tuned, this
							page will change during the presenation!
						</div>
					{/snippet}
					{#if selected === 'cbs-names'}
						{@render waitingForPresenter()}
					{:else if selected === 'cbs-places'}
						<h2 class="mb-4 text-lg font-semibold">
							What places do you have a special relation to?
						</h2>
						{#if data.inputQuestions['cbs-places']}
							<div class="h-[60dvh] min-h-80 w-full">
								<Map mobile places={ownPlaces}>
									{#snippet popup(coords, close)}
										{#key coords}<PlaceForm
												socketio={answerSocket}
												parentId={data.inputQuestions['cbs-places']}
												{coords}
												bind:name
												onclose={close}
												onsubmit={(place) => {
													ownPlaces.push(place);
													submitting();
												}}
											/>{/key}
									{/snippet}
								</Map>
							</div>
						{:else}<p>This input is unavailable.</p>{/if}
					{:else if selected === 'cbs-books'}
						<h2 class="mb-4 text-lg font-semibold">What's your take on these books?</h2>
						<div class="mb-3 grid grid-cols-[3rem_minmax(0,1fr)_3rem] items-center gap-2">
							<button
								class="btn btn-primary btn-circle btn-gradient shadow-base-shadow shadow"
								aria-label="Previous book"
								title="Previous book"
								onclick={() => moveBook(-1)}
								><Icon icon="tabler:chevron-left" class="size-6" /></button
							>
							<div class="relative h-64 overflow-hidden">
								{#key book.id}<img
										src={book.image}
										alt={book.alt}
										class="h-full w-full object-contain"
										in:fly={{ x: bookDirection * 48, duration: 180 }}
									/>{/key}
							</div>
							<button
								class="btn btn-primary btn-circle btn-gradient shadow-base-shadow shadow"
								aria-label="Next book"
								title="Next book"
								onclick={() => moveBook(1)}
								><Icon icon="tabler:chevron-right" class="size-6" /></button
							>
						</div>
						<!-- <h3 class="mt-3 text-center text-lg font-semibold">{book.title}</h3>
						<p class="mb-4 text-center">{book.author}</p> -->
						{#if data.inputQuestions['cbs-books']}<CommentInput
								socketio={answerSocket}
								parentId={data.inputQuestions['cbs-books']}
								bookId={book.id}
								bind:name
								bind:text={bookComment}
								label="What's your take on this book?"
								onsubmit={submitting}
							/>{:else}<p>This input is unavailable.</p>{/if}
						<label class="label" for="selected-book">Other Books</label>
						<select id="selected-book" class="select mb-4 w-full" bind:value={bookIndex}>
							{#each providedBooks as option, index (option.id)}<option value={index}
									>{option.title}</option
								>{/each}
						</select>
						<details class="mb-5">
							<summary class="cursor-pointer font-medium">Reference</summary>
							<p class="mt-2 break-words">{book.alt}</p>
							<a
								class="link link-animated"
								href={book.link}
								target="_blank"
								rel="noopener noreferrer">Source</a
							>
						</details>
					{:else if selected === 'cbs-comments'}
						{@render questionsComments()}
						<!-- <h2 class="mb-4 text-lg font-semibold">
							⁉️ Do you have comments or questions? <br />
							📖 Which books would you recommend?
						</h2>
						{#if data.inputQuestions['cbs-comments']}<CommentInput
								socketio={answerSocket}
								parentId={data.inputQuestions['cbs-comments']}
								bind:name
								bind:text={comment}
								onsubmit={submitting}
							/>{:else}<p>This input is unavailable.</p>{/if} -->
					{:else}
						{@render waitingForPresenter()}
					{/if}
				</div>
			{/key}
		</main>
	{/if}
	<p class="label-small min-h-6 px-4 py-2" class:text-error={failed} role="status">{notice}</p>
	<CardOverlay bind:hidden={hideTermsAndConditions}>
		<TermsAndConditions />
	</CardOverlay>
	<footer
		class="border-base-content/15 mt-auto flex flex-col flex-wrap justify-items-center gap-x-6 gap-y-2 border-t p-4 text-sm"
	>
		<button class="link link-animated w-fit" onclick={() => (hideTermsAndConditions = false)}>
			<span class="code mr-2 ml-1">§</span>Terms and Conditions
		</button>
		<div>
			<Icon icon="system-uicons:projector" class=" inline size-4" />
			<a class="link link-animated w-fit" href={data.presentationUrl}
				>Presentation (not mobile-friendly!)</a
			>
		</div>
	</footer>
</div>
