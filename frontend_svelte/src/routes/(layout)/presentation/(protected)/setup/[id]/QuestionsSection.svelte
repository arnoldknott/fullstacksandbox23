<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { fade, slide } from 'svelte/transition';

	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import Card from '$components/Card.svelte';
	import JsonData from '$components/JsonData.svelte';
	import Title from '$components/Title.svelte';
	import { AccessHandler, Action } from '$lib/accessHandler';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { AccessShareOption, Identity, Question } from '$lib/types';
	import { initTabs } from '$lib/userInterface';

	import IdBadge from '../../../../(protected)/IdBadge.svelte';
	import ShareItem from '../../../../playground/components/ShareItem.svelte';
	import ActionButtons from '../ActionButtons.svelte';
	import FormElement from '../FormElement.svelte';

	let {
		parentId,
		questions = [],
		identities = []
	}: { parentId?: string; questions: Question[]; identities: Identity[] } = $props();

	// uses the one, that gets set in sidebar and communicated
	// through the search params of the url
	let debug = $derived(page.url.searchParams.get('debug') === 'true' ? true : false);
	let hideNewQuestionCard: boolean = $derived(
		!(page.url.searchParams.get('add-question') === 'true')
	);

	$effect(() => {
		debug = page.url.searchParams.get('debug') === 'true';
		hideNewQuestionCard = page.url.searchParams.get('add-question') !== 'true';
	});

	let socketioQuestions: SocketIO<Question> = $state()!;
	let linkedQuestions = $derived<Question[]>(
		socketioQuestions?.getSelectedEntities('linkedToPresentation') || []
	);
	let notLinkedQuestions = $derived<Question[]>(
		socketioQuestions?.getSelectedEntities('notLinkedToPresentation') || []
	);
	let inheritPending = $state(true);

	let shareOptionsForNewQuestion: AccessShareOption[] = $derived(
		AccessHandler.createShareOptions(
			socketioQuestions.identities,
			socketioQuestions.accessPolicies[socketioQuestions.pendingEntities[0].id]
		) || []
	);

	let multiplePending = $state(false);
	let multipleSuffixes = $state({ start: 1, end: 2 });
	let newSuffix = $derived(
		multiplePending ? '_[' + multipleSuffixes.start + ':' + multipleSuffixes.end + ']' : null
	);
	$effect(() => {
		if (multipleSuffixes.end <= multipleSuffixes.start) {
			multipleSuffixes.end = multipleSuffixes.start + 1;
		}
	});

	onMount(() => {
		socketioQuestions = new SocketIO<Question>(
			{
				namespace: '/question',
				sessionId: page.data.session.sessionId,
				parentId: parentId,
				queryParams: { 'request-access-data': true }
			},
			{
				inherit: inheritPending,
				template: {
					question: '',
					language: 'en'
				}
			}
		);
		socketioQuestions.identities = identities;
		socketioQuestions.createLinkedSelection('linkedToPresentation');
		socketioQuestions.createLinkedSelection('notLinkedToPresentation', true);
		// emiting a "read" to trigger a "get_all on the server,
		// which transmits all data also for the unlinked questions.
		socketioQuestions.client.emit('read');
	});

	$effect(() => {
		socketioQuestions.entities = questions ?? [];
	});
	onDestroy(() => {
		socketioQuestions?.client.disconnect();
	});

	let viewMode = $state<'grid' | 'list'>('list');
</script>

<!-- TBD: potentially move into existing questions Card, same way as the add new presentation, then no slide transition is necessary any more. -->
<!--
The `slide` transition does not work correctly for elements with `display: inline-flex`
https://svelte.dev/e/transition_slide_display 

=> Ignore for now, as this button anyways will be replaced by the buutton inside the Existing Question Card (see existing presentations)!
-->

<!-- {#if hideNewQuestionCard}
	<button
		transition:slide={{ duration: 600 }}
		class="btn btn-primary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm transition-all duration-600"
		aria-label="Add new question"
		onclick={() => (hideNewQuestionCard = false)}
	>
		<span class="icon-[fa6-solid--plus] size-4"></span>Add
	</button>
{/if} -->

{#snippet warning()}
	<span class="icon-[fluent-color--warning-24] size-4"></span>
{/snippet}

<!-- Very similar to the new presentation footer - consider putting into component -->
{#snippet cancelSaveFooter()}
	<div class="ml-5 flex flex-row justify-end gap-4">
		<button
			class="btn btn-secondary-container btn-gradient shadow-outline rounded-full shadow"
			aria-label="Cancel"
			onclick={() => {
				hideNewQuestionCard = true;
			}}><span class="icon-[tabler--x] size-5"></span>Cancel</button
		>
		<button
			class="btn btn-primary-container btn-gradient shadow-outline rounded-full shadow"
			aria-label="Save new presentation"
			onclick={() => {
				socketioQuestions.submitBulk(parentId, inheritPending);
				hideNewQuestionCard = true;
				// For buld submit the new pending needs manual creation:
				socketioQuestions.createPending();
			}}><span class="icon-[tabler--send-2] size-5"></span>Save</button
		>
	</div>
{/snippet}

{#if socketioQuestions?.pendingEntities[0]}
	<Card
		id="add-questions"
		title="Add Questions"
		closeButton
		extraClasses="label-large"
		bind:hidden={hideNewQuestionCard}
		footer={cancelSaveFooter}
	>
		<!-- <p class="label">
		{@render warning()} Add questions with tabs for new and existing, where the existing questions get
		the button to copy and link. Also a copy all selected and link all selected.
	</p> -->
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
					class="h-full max-h-120 overflow-scroll"
					role="tabpanel"
					aria-labelledby="new-question-head"
				>
					<div class="label">
						{@render warning()} Forms to add new questions, with the ability to add multiple questions
						at once and inherit access rights - default: true - from presentation.
					</div>
					{#snippet labelDescription()}
						This label is the way to identify this particular quesion in the code of the
						presentation. It is mandatory.
					{/snippet}
					<FormElement
						title="Label"
						mandatory
						description={labelDescription}
						extraClasses="max-w-300"
					>
						<div class="input-filled input-primary w-full">
							<input
								type="text"
								placeholder=""
								class="input"
								id="slugInput"
								bind:value={socketioQuestions.pendingEntities[0].question}
							/>
							<label class="input-filled-label" for="slugInput"
								>[use this label to identify the question in your presentation]{newSuffix}</label
							>
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
					{#snippet accessDescription()}
						Who has which access to this presentation?
						<br />
						Default is public <span class="icon-[gis--globe-earth-alt] size-4"></span>
						and have read
						<span
							class={`${AccessHandler.rightsIcon(Action.READ)} ${AccessHandler.rightsIconColor(Action.READ)} size-4`}
						></span>
						access.
					{/snippet}
					<FormElement title="Access" description={accessDescription} extraClasses="max-w-130">
						<div class="label mb-2 flex flex-1 items-center gap-1">
							<label class="label label-text text-base-content" for="new-question-inherit">
								<input
									id="new-question-inherit"
									type="checkbox"
									class="checkbox checkbox-primary"
									bind:checked={inheritPending}
								/>
							</label>
							inherit from {parentId}
						</div>
						<ul class="bg-base-150 shadow-base-shadow overflow-y-auto rounded-lg p-2 shadow-inner">
							{#each shareOptionsForNewQuestion, i (i)}
								<ShareItem
									// TBD: adopt for multiple new!
									resourceId={socketioQuestions.pendingEntities[0].id}
									// No need to bind, as it is anyways handled through the entityContainer's methods and the socketio's submitEntity method.
									shareOption={shareOptionsForNewQuestion[i]}
									socketio={socketioQuestions}
									// share={socketioQuestions?.shareEntity.bind(socketioQuestions)}
									wide
								/>
							{/each}
						</ul>
					</FormElement>
					<FormElement title="Add multiple questions">
						<div class="mb-2 flex flex-1 flex-row items-center gap-1">
							<label class="label label-text text-base-content" for="new-question-multiple">
								<input
									id="new-question-multiple"
									type="checkbox"
									disabled
									// TBD: remove disabled, when functionality is implemented!
									class="checkbox checkbox-primary"
									bind:checked={multiplePending}
								/>
							</label>
							with suffixes
							<input
								id="multiple-groups-start"
								type="number"
								placeholder={multipleSuffixes.start.toString()}
								class="input shadow-shadow flex-2 shadow-inner"
								name="multiple-groups-suffix-start"
								disabled={!multiplePending}
								bind:value={multipleSuffixes.start}
							/>
							<span class="label flex-1"> to</span>
							<input
								id="multiple-groups-end"
								type="number"
								placeholder={multipleSuffixes.end.toString()}
								class="input shadow-shadow flex-2 shadow-inner"
								name="multiple-groups-suffix-end"
								disabled={!multiplePending}
								bind:value={multipleSuffixes.end}
							/>
						</div>
						<div class="label">
							{@render warning()} Creation of multiple not functional yet
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
					{#each notLinkedQuestions as linkedQuestion, idx (idx)}
						<div class="linked-question">
							<p>Q: {linkedQuestion.question}</p>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</Card>
{:else if !socketioQuestions?.pendingEntities[0] && !hideNewQuestionCard}
	<div class="label text-error" transition:slide={{ duration: 600 }}>
		<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
	</div>
{/if}

<!-- TBD: consider turning into a component, as it is very similar to the existing presentations section. -->
{#snippet existingQuestionsHeader()}
	<div class="flex justify-between">
		<Title id="existingQuestions" class="grow">Overview</Title>
		<div class="flex flex-row items-center justify-center">
			{#if hideNewQuestionCard || !socketioQuestions?.pendingEntities[0]}
				<button
					transition:fade={{ duration: 600 }}
					class="btn btn-primary-container btn-gradient label btn shadow-outline mx-4 rounded-full shadow-sm"
					aria-label="Add new question"
					onclick={() => (hideNewQuestionCard = false)}
				>
					<!-- onclick={() => goto(resolve('/(layout)/presentation/(protected)/setup/new'))} -->
					<span class="icon-[fa6-solid--plus] size-5"></span>
					<!-- <span class="hidden ">Add</span> -->
					<span class="hidden sm:inline">Add new</span>
					<span class="hidden md:inline">question</span>
				</button>
			{/if}
			<div class="join shadow-outline rounded-full shadow-sm">
				<button
					aria-label="Grid"
					class="btn join-item btn-secondary btn-gradient btn-sm shadow-outline rounded-l-full py-4 shadow {viewMode !==
					'grid'
						? 'opacity-60'
						: ''}"
					onclick={() => (viewMode = 'grid')}
				>
					<span class="icon-[gridicons--grid] size-5"></span>
				</button>
				<button
					aria-label="List"
					class="btn join-item btn-secondary btn-gradient btn-sm shadow-outline rounded-r-full py-4 shadow {viewMode !==
					'list'
						? 'opacity-60'
						: ''}"
					onclick={() => (viewMode = 'list')}
				>
					<span class="icon-[material-symbols-light--table-outline] size-5"></span>
				</button>
			</div>
		</div>
	</div>
{/snippet}

<Card
	id="linked-questions"
	title="Linked Questions"
	header={existingQuestionsHeader}
	extraClasses="label-large"
>
	<!-- {#each linkedQuestions as linkedQuestion, idx (idx)}
		<div class="linked-question">
			<p>Q: {linkedQuestion.question}</p>
		</div>
	{/each} -->
	<div class="label">
		{@render warning()} Potentially as an accordion with the answers in the panel? Adding a question and
		opening sidebar to select existing questions - for mode copy (don't keep the original answers and
		don't keep in sync) or link (keeps answers in sync)
	</div>
	<div class="w-full overflow-x-auto {viewMode !== 'grid' ? 'hidden' : ''}">
		<p class="bg-warning text-warning-content rounded-lg p-4">
			Grid view mode is not developed yet
		</p>
	</div>
	<div class="w-full overflow-x-auto {viewMode !== 'list' ? 'hidden' : ''}">
		<table class="table w-full">
			<thead>
				<tr>
					<th class="title text-base-content w-3/5 font-medium normal-case">Id / Label</th>
					<th class="title text-base-content font-medium normal-case">Access</th>
					<th class="title text-base-content font-medium normal-case">
						# <span class="icon-[mdi--text] size-4"></span>
					</th>
					<th class="title text-base-content font-medium normal-case">
						# <span class="icon-[tabler-number] size-4"></span>
					</th>
					<th class="title text-base-content font-medium normal-case">
						<span class="icon-[fluent-mdl2--offline-storage] size-4"></span>
					</th>
					<th class="title text-base-content w-px pr-0 font-medium whitespace-nowrap normal-case">
						Actions
					</th>
				</tr>
			</thead>
			<tbody>
				{#if (linkedQuestions.length ?? 0) === 0}
					<tr>
						<td colspan={8} class="text-center">
							No presentations yet. Create one by sending a POST request to the /presentation
							endpoint.
						</td>
					</tr>
				{:else}
					{#each linkedQuestions as question (question.id)}
						<tr class="hover:bg-base-300">
							<td class="max-w-0">
								<IdBadge id={question.id} />
								<a
									href={resolve('/(layout)/presentation/[slug]', {
										slug: question?.question?.substring(1) || question.id
									})}
									aria-label={`Setup presentation ${question.question || question.id}`}
									class="link link-primary link-animated block truncate"
								>
									{question.question || question.id}
								</a>
							</td>
							<td>[Access]</td>
							<td>{question.messages?.length ?? 0}</td>
							<td>{question.numericals?.length ?? 0}</td>
							<td>[Size]</td>
							<td class="w-px px-0 py-1 text-left align-middle whitespace-nowrap">
								<ActionButtons
									resourceId={question.id}
									accessRight={socketioQuestions?.accessRights[question.id]}
									socketio={socketioQuestions}
								/>
							</td>
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</div>
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
				<JsonData data={linkedQuestions} />
				<p class="label-prominent">Not Linked Entities</p>
				<JsonData data={notLinkedQuestions} />
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
