<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { slide } from 'svelte/transition';

	// import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Card from '$components/Card.svelte';
	import JsonData from '$components/JsonData.svelte';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { Identity, Question } from '$lib/types';
	import { initTabs } from '$lib/userInterface';

	import FormElement from '../FormElement.svelte';

	let {
		parentId,
		questions = [],
		identities = []
	}: { parentId?: string; questions: Question[]; identities: Identity[] } = $props();

	// uses the one, that gets set in sidebar and communicated
	// through the search params of the url
	let debug = $derived(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		debug = page.url.searchParams.get('debug') === 'true';
	});

	let socketioQuestions: SocketIO<Question> = $state()!;

	onMount(() => {
		socketioQuestions = new SocketIO<Question>({
			namespace: '/question',
			sessionId: page.data?.session?.sessionId || '',
			parentId: parentId,
			queryParams: { 'request-access-data': true }
		});
		socketioQuestions.identities = identities;
		socketioQuestions.createLinkedSelection('linkedToPresentation');
		socketioQuestions.createLinkedSelection('notLinkedToPresentation', true);
	});

	$effect(() => {
		socketioQuestions.entities = questions ?? [];
	});
	onDestroy(() => {
		socketioQuestions?.client.disconnect();
	});

	let hideNewQuestionCard: boolean = $state(
		!(page.url.searchParams.get('add-question') === 'true')
	);

	// TBD: debug why this si scrolling - solution is probably already in +layout.svelte
	// $effect(() => {
	// 	const currentUrl = new URL(page.url.toString());

	// 	if (!hideNewQuestionCard) {
	// 		currentUrl.searchParams.set('add-question', 'true');
	// 	} else {
	// 		currentUrl.searchParams.delete('add-question');
	// 	}

	// 	if (currentUrl.search !== page.url.search) {
	// 		goto(`${currentUrl.pathname}${currentUrl.search}${currentUrl.hash}`, {
	// 			replaceState: true,
	// 			noScroll: true,
	// 			keepFocus: true
	// 		});
	// 	}
	// });
	// let hideNewLinkCard: boolean = $state(!(page.url.searchParams.get('new-link') === 'true'));
	// let hideNewDrawingCard: boolean = $state(!(page.url.searchParams.get('new-drawing') === 'true'));
	// let hideNewFileCard: boolean = $state(!(page.url.searchParams.get('new-file') === 'true'));
</script>

<!-- TBD: potentially move into existing questions Card, same way as the add new presentation, then no slide transition is necessary any more. -->
<!--
The `slide` transition does not work correctly for elements with `display: inline-flex`
https://svelte.dev/e/transition_slide_display 

=> Ignore for now, as this button anyways will be replaced by the buutton inside the Existing Question Card (see existing presentations)!
-->

{#if hideNewQuestionCard}
	<button
		transition:slide={{ duration: 600 }}
		class="btn btn-primary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm transition-all duration-600"
		aria-label="Add new question"
		onclick={() => (hideNewQuestionCard = false)}
	>
		<span class="icon-[fa6-solid--plus] size-4"></span>Add
	</button>
{/if}

{#snippet warning()}
	<span class="icon-[fluent-color--warning-24] size-4"></span>
{/snippet}

<Card
	id="add-questions"
	title="Add Questions"
	closeButton
	extraClasses="label-large"
	bind:hidden={hideNewQuestionCard}
>
	<p class="label">
		{@render warning()} Add questions with tabs for new and existing, where the existing questions get
		the button to copy and link. Also a copy all selected and link all selected.
	</p>
	<div class="bg-base-150 shadow-base-shadow overflow-y-auto rounded-lg shadow-inner">
		<div
			class="tabs tabs-lifted tabs-secondary m-1"
			// class="tabs tabs-lifted to-secondary m-1 rounded-lg bg-linear-to-b from-transparent"
			// class="tabs tabs-lifted to-secondary m-1 bg-linear-to-b from-transparent"
			aria-label="Tabs"
			role="tablist"
			aria-orientation="horizontal"
			{@attach initTabs}
		>
			<button
				type="button"
				// class="tab tab-secondary active w-full"
				class="tab active w-full"
				id="new-question-head"
				data-tab="#new-question-tab"
				aria-controls="new-question-tab"
				role="tab"
				aria-selected="true"
			>
				<span class="icon-[fa6-solid--plus] mr-2 size-4"></span>
				<span class="hidden md:inline">Add</span>
				<span class="hidden sm:inline">&nbsp;new</span>
			</button>
			<button
				type="button"
				// class="tab tab-secondary w-full"
				class="tab w-full"
				id="existing-question-head"
				data-tab="#existing-question-tab"
				aria-controls="existing-question-tab"
				role="tab"
				aria-selected="false"
			>
				<span class="icon-[tabler--copy] mr-2 size-4"></span>
				<span class="hidden md:inline">Copy </span>
				&nbsp;or&nbsp;
				<span class="icon-[tabler--link] mx-2 size-4"></span>
				<span class="hidden md:inline">link </span>
				<span class="hidden sm:inline">&nbsp;existing</span>
			</button>
		</div>
		<div class="h-fit p-2">
			<div
				id="new-question-tab"
				class="h-full max-h-100 overflow-scroll"
				role="tabpanel"
				aria-labelledby="new-question-head"
			>
				<div class="label">
					{@render warning()} Forms to add new questions, with the ability to add multiple questions at
					once and inherit access rights - default: true - from presentation.
				</div>
				{#snippet labelDescription()}
					This label is the way to identify this particular quesion in the code of the presentation.
					It is mandatory.
				{/snippet}
				<FormElement title="Label" description={labelDescription} extraClasses="max-w-300">
					<div class="input-filled input-primary w-full">
						<input type="text" placeholder="" class="input" id="slugInput" />
						<!-- bind:value={socketioPresentations.pendingEntities[0].path} -->
						<label class="input-filled-label" for="slugInput"
							>[use this label to identify the question in your presentation]</label
						>
					</div>
					<div class="label">
						{@render warning()} Add a red asterix to the label in FormElement to indicate that this is
						a mandatory field
					</div>
				</FormElement>
				{#snippet languageDescription()}
					Giving the language of the question text in the code. To allow automatic translation the
					algorithm needs to know from what language to translate into all the others, so this is
					the language of the source.
				{/snippet}
				<FormElement title="Language" description={languageDescription} extraClasses="max-w-300">
					<div class="label">
						{@render warning()} A drop-down field to select the language for the question, with a default
						value of the presentation's language.
					</div>
				</FormElement>
			</div>
			<div
				id="existing-question-tab"
				class="hidden h-full max-h-100 overflow-scroll"
				role="tabpanel"
				aria-labelledby="existing-question-head"
			>
				<div class="label">
					{@render warning()} Table of existing questions and functionality to link or copy them into
					this presentation.
				</div>
			</div>
		</div>
	</div>
</Card>

<Card id="linked-questions" title="Linked Questions" extraClasses="label-large">
	{#each socketioQuestions?.getSelectedEntities('linkedToPresentation') || [] as linkedQuestion, idx (idx)}
		<div class="linked-question">
			<p>{linkedQuestion.question}</p>
		</div>
	{/each}
	<p>
		Potentially as an accordion with the answers in the panel? Adding a question and opening sidebar
		to select existing questions - for mode copy (don't keep the original answers and don't keep in
		sync) or link (keeps answers in sync)
	</p>
</Card>

{#if debug}
	<Card
		id="debugQuestions"
		title="Debug Questions"
		extraClasses="label-large bg-warning-container/30 text-warning-container-content/80 border-warning-container"
	>
		<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
			<div>
				<p class="label-prominent">Entities</p>
				<JsonData data={socketioQuestions?.entities ?? []} />
			</div>
			<div>
				<p class="label-prominent">Pending Entities</p>
				<JsonData data={socketioQuestions?.pendingEntities ?? []} />
				<p class="label-prominent">Linked Entities</p>
				<JsonData data={socketioQuestions?.getSelectedEntities('linkedToPresentation') ?? []} />
				<p class="label-prominent">Not Linked Entities</p>
				<JsonData data={socketioQuestions?.getSelectedEntities('notLinkedToPresentation') ?? []} />
			</div>
			<div>
				<p class="label-prominent">Access Policies</p>
				<JsonData data={socketioQuestions?.accessPolicies ?? []} />
				<p class="label-prominent">Access Rights</p>
				<JsonData data={socketioQuestions?.accessRights ?? []} />
				<p class="label-prominent">Identities</p>
				<JsonData data={socketioQuestions?.identities ?? []} />
			</div>
		</div>
	</Card>
{/if}
