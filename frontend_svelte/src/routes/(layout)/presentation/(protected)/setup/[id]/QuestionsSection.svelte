<script lang="ts">
	import { onDestroy, onMount } from 'svelte';

	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import ActionButtons from '$components/ActionButtons.svelte';
	import AddEntityCard from '$components/AddEntityCard.svelte';
	import Card from '$components/Card.svelte';
	import EntitySection from '$components/EntitySection.svelte';
	import JsonData from '$components/JsonData.svelte';
	import SelectionActionButtons from '$components/SelectionActionButtons.svelte';
	import Table, { countIcon, icon, snippet, text, value } from '$components/Table.svelte';
	import { EntityType, getLanguageFlag } from '$lib/entities';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { Identity, QuestionExtended } from '$lib/types';

	import IdBadge from '../../../../(protected)/IdBadge.svelte';
	import QuestionForm from './QuestionForm.svelte';

	let {
		parentId,
		questions,
		cursor,
		identities
	}: {
		parentId: string;
		questions: QuestionExtended[];
		cursor: number;
		identities: Identity[];
	} = $props();

	let debug = $derived(page.url.searchParams.get('debug') === 'true');
	let hideNew = $derived(page.url.searchParams.get('add-question') !== 'true');
	let viewMode = $state<'grid' | 'list' | 'table'>('table');
	let inheritPending = $state(true);

	let socketio: SocketIO<QuestionExtended> = $state()!;
	let linkedQuestions = $derived(socketio?.getSelectedEntities('linkedToPresentation') ?? []);
	let notLinkedQuestions = $derived(socketio?.getSelectedEntities('notLinkedToPresentation') ?? []);

	onMount(() => {
		socketio = new SocketIO<QuestionExtended>(
			{
				namespace: '/question',
				sessionId: page.data.session.sessionId,
				parentId,
				queryParams: {
					'identity-ids': identities.map((identity) => identity.id).join(','),
					'request-access-data': true
				}
			},
			{
				snapshot: { entities: questions, cursor },
				inherit: inheritPending,
				template: { question: '', language: 'en' }
			}
		);
		socketio.identities = identities;
		socketio.createLinkedSelection('linkedToPresentation', false, parentId);
		socketio.createLinkedSelection('notLinkedToPresentation', true, parentId);
	});

	onDestroy(() => {
		socketio?.client.disconnect();
	});
</script>

{#snippet warning()}
	<span class="icon-[fluent-color--warning-24] size-4"></span>
{/snippet}

<AddEntityCard
	{socketio}
	entityType={EntityType.QUESTION}
	{parentId}
	bind:inheritPending
	bind:hidden={hideNew}
>
	{#snippet form(question, shareOptions)}
		<QuestionForm {question} {shareOptions} {socketio} {parentId} bind:inheritPending />
	{/snippet}
	{#snippet existing()}
		{#each notLinkedQuestions as question (question.id)}
			<p>Q: {question.question}</p>
		{/each}
	{/snippet}
</AddEntityCard>

<EntitySection
	id="linked-questions"
	title="Linked Questions"
	entityLabel="question"
	bind:hideNew
	bind:viewMode
	hasPending={Boolean(socketio?.pendingEntities[0])}
>
	<div class="label">
		{@render warning()} Link questions to this presentation or create a copy without its answers.
	</div>
	{#snippet grid()}
		<p class="bg-warning text-warning-content rounded-lg p-4">
			Grid view mode is not developed yet
		</p>
	{/snippet}
	{#snippet list()}
		<p class="bg-warning text-warning-content rounded-lg p-4">
			List view mode is not developed yet
		</p>
	{/snippet}
	{#snippet table()}
		{#snippet questionIdCell(question: QuestionExtended)}
			<IdBadge id={question.id} />
			<a
				href={resolve('/(layout)/question/(protected)/setup/[id]', { id: question.id })}
				aria-label={`Setup question ${question.question || question.id}`}
				class="link link-primary link-animated block truncate"
			>
				{question.question || question.id}
			</a>
		{/snippet}
		{#snippet languageCell(question: QuestionExtended)}
			<span
				class="{getLanguageFlag(question.language) ?? 'icon-[twemoji--flag-united-kingdom]'} size-5"
			></span>
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
					cell: value<QuestionExtended>((entity) => entity.messages?.length ?? 0),
					headerClass: 'text-center'
				},
				{
					header: countIcon('tabler:number'),
					cell: value<QuestionExtended>((entity) => entity.numericals?.length ?? 0),
					headerClass: 'text-center'
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
	{/snippet}
</EntitySection>

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
				<JsonData data={socketio?.selections?.selected ?? []} />
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
