<script lang="ts">
	import Icon from '@iconify/svelte';
	import { onDestroy, onMount } from 'svelte';
	import { fade } from 'svelte/transition';

	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import ActionButtons from '$components/ActionButtons.svelte';
	import AddDataCard from '$components/AddDataCard.svelte';
	import Card from '$components/Card.svelte';
	import JsonData from '$components/JsonData.svelte';
	import Table, { countIcon, icon, snippet, text, value } from '$components/Table.svelte';
	import Title from '$components/Title.svelte';
	import { EntityType } from '$lib/entityContainer.svelte';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { Identity, Question, QuestionExtended } from '$lib/types';

	import IdBadge from '../../../../(protected)/IdBadge.svelte';
	import SelectionActionButtons from '../SelectionActionButtons.svelte';
	import QuestionForm from './QuestionForm.svelte';

	let {
		parentId,
		questions = [],
		cursor,
		identities = []
	}: {
		parentId?: string;
		questions: QuestionExtended[];
		cursor: number;
		identities: Identity[];
	} = $props();

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

	let socketio: SocketIO<QuestionExtended> = $state()!;
	let linkedQuestions = $derived<Question[]>(
		socketio?.getSelectedEntities('linkedToPresentation') || []
	);
	let notLinkedQuestions = $derived<Question[]>(
		socketio?.getSelectedEntities('notLinkedToPresentation') || []
	);
	let inheritPending = $state(true);

	onMount(() => {
		socketio = new SocketIO<QuestionExtended>(
			{
				namespace: '/question',
				sessionId: page.data.session.sessionId,
				parentId: parentId,
				queryParams: {
					'identity-ids': identities.map((identity) => identity.id).join(','),
					'request-access-data': true
				}
			},
			{
				snapshot: { entities: questions, cursor },
				inherit: inheritPending,
				template: {
					question: '',
					language: 'en'
				}
			}
		);
		socketio.identities = identities;
		socketio.createLinkedSelection('linkedToPresentation');
		socketio.createLinkedSelection('notLinkedToPresentation', true);
	});
	onDestroy(() => {
		socketio?.client.disconnect();
	});

	let viewMode = $state<'grid' | 'list' | 'table'>('table');

	const flag = (language: string) =>
		language === 'en-US'
			? 'flagpack:us'
			: language === 'da-DK'
				? 'flagpack:dk'
				: language === 'de-DE'
					? 'flagpack:de'
					: 'flagpack:gb-ukm';
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

<!-- <p class="label">
	{@render warning()} Add questions with tabs for new and existing, where the existing questions get
	the button to copy and link. Also a copy all selected and link all selected.
</p> -->
<AddDataCard
	{socketio}
	entityType={EntityType.QUESTION}
	{parentId}
	{inheritPending}
	bind:hidden={hideNewQuestionCard}
>
	{#snippet form(question, shareOptions)}
		<QuestionForm {question} {shareOptions} {socketio} {parentId} bind:inheritPending />
	{/snippet}
	{#snippet existing()}
		{#each notLinkedQuestions as linkedQuestion, idx (idx)}
			<div class="linked-question">
				<p>Q: {linkedQuestion.question}</p>
			</div>
		{/each}
	{/snippet}
</AddDataCard>

<Card id="linked-questions" title="Linked Questions" extraClasses="label-large">
	<!-- TBD: consider turning into a component, as it is very similar to the existing presentations section. -->
	{#snippet header()}
		<div class="flex justify-between">
			<Title id="existingQuestions" class="grow">Overview</Title>
			<div class="flex flex-row items-center justify-center">
				{#if hideNewQuestionCard || !socketio?.pendingEntities[0]}
					<button
						transition:fade={{ duration: 600 }}
						class="btn btn-primary-container btn-gradient label btn shadow-outline mx-4 rounded-full shadow-sm"
						aria-label="Add new question"
						onclick={() => (hideNewQuestionCard = false)}
					>
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
						class="btn join-item btn-secondary btn-gradient btn-sm shadow-outline py-4 shadow {viewMode !==
						'list'
							? 'opacity-60'
							: ''}"
						onclick={() => (viewMode = 'list')}
					>
						<span class="icon-[material-symbols--view-list-outline] size-5"></span>
					</button>
					<button
						aria-label="Table"
						class="btn join-item btn-secondary btn-gradient btn-sm shadow-outline rounded-r-full py-4 shadow {viewMode !==
						'table'
							? 'opacity-60'
							: ''}"
						onclick={() => (viewMode = 'table')}
					>
						<span class="icon-[material-symbols--table-outline] size-5"></span>
					</button>
				</div>
			</div>
		</div>
	{/snippet}
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
		<p class="bg-warning text-warning-content rounded-lg p-4">
			List view mode is not developed yet
		</p>
	</div>
	<div class="w-full overflow-x-auto {viewMode !== 'table' ? 'hidden' : ''}">
		{#snippet questionIdCell(question: Question)}
			<IdBadge id={question.id} />
			<a
				href={resolve('/(layout)/question/(protected)/setup/[id]', {
					id: question.id
				})}
				aria-label={`Setup question ${question.question || question.id}`}
				class="link link-primary link-animated block truncate"
			>
				{question.question || question.id}
			</a>
		{/snippet}
		{#snippet languageCell(question: QuestionExtended)}
			<Icon icon={flag(question.language)} class="size-5" inline />
		{/snippet}
		{#snippet questionActionsCell(question: QuestionExtended)}
			<ActionButtons
				resourceId={question.id}
				accessRight={socketio?.accessRights[question.id]}
				{socketio}
				entityType="question"
			/>
		{/snippet}
		<Table
			columns={[
				{
					header: text('Id / Label'),
					cell: snippet(questionIdCell),
					headerClass: 'w-3/5',
					cellClass: 'max-w-0'
				},
				{
					header: icon('tabler:language'),
					cell: snippet(languageCell),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: text('Access'),
					cell: value(() => '[Access]'),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: countIcon('mdi:text'),
					cell: value<Question>((entity) => entity.messages?.length ?? 0),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: countIcon('tabler:number'),
					cell: value<Question>((entity) => entity.numericals?.length ?? 0),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: icon('fluent-mdl2:offline-storage'),
					cell: value(() => '[Size]'),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: text('Actions'),
					cell: snippet(questionActionsCell),
					headerClass: 'w-px text-center whitespace-nowrap',
					cellClass: 'w-px py-1 text-center align-middle whitespace-nowrap'
				}
			]}
			entityContainer={socketio}
			displaySelection="linkedToPresentation"
		>
			{#snippet menu()}
				<th colspan={6}></th>
				<th class="text-end"><SelectionActionButtons {socketio} /></th>
			{/snippet}
		</Table>
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
				<JsonData data={socketio?.entities ?? []} />
			</div>
			<div>
				<p class="label-prominent">Pending Entities</p>
				<JsonData data={socketio?.pendingEntities ?? []} />
				<p class="label-prominent">Selected Entities</p>
				<JsonData data={socketio?.selections?.['selected'] ?? []} />
				<p class="label-prominent">Linked Entities</p>
				<JsonData data={linkedQuestions} />
				<p class="label-prominent">Not Linked Entities</p>
				<JsonData data={notLinkedQuestions} />
			</div>
			<div>
				<p class="label-prominent">Access Policies</p>
				<JsonData data={socketio?.accessPolicies ?? []} />
				<p class="label-prominent">Access Rights</p>
				<JsonData data={socketio?.accessRights ?? []} />
				<p class="label-prominent">Identities</p>
				<JsonData data={socketio?.identities ?? []} />
			</div>
		</div>
	</Card>
{/if}
