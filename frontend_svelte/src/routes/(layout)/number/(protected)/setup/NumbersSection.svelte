<script lang="ts">
	import { onDestroy, onMount } from 'svelte';

	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import ActionButtons from '$components/ActionButtons.svelte';
	import AddEntityCard from '$components/AddEntityCard.svelte';
	import EntitySection from '$components/EntitySection.svelte';
	import JsonData from '$components/JsonData.svelte';
	import SelectionActionButtons from '$components/SelectionActionButtons.svelte';
	import Table, { countIcon, field, snippet, text, value } from '$components/Table.svelte';
	import Title from '$components/Title.svelte';
	import { Action } from '$lib/accessHandler';
	import { EntityType } from '$lib/entities';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { Identity, NumberExtended } from '$lib/types';

	import IdBadge from '../../../(protected)/IdBadge.svelte';
	import NumberForm from './NumberForm.svelte';

	let {
		parentId,
		numbers,
		cursor,
		identities,
		excludeId
	}: {
		parentId: string;
		numbers: NumberExtended[];
		cursor: number;
		identities: Identity[];
		excludeId?: string;
	} = $props();

	let debug = $derived(page.url.searchParams.get('debug') === 'true');
	let socketio: SocketIO<NumberExtended> = $state()!;
	let hideNew = $derived(page.url.searchParams.get('add-number') !== 'true');
	let viewMode = $state<'table' | 'grid' | 'list'>('table');
	let inheritPending = $state(true);
	let labelPending = $state('');
	let notLinkedNumbers = $derived(
		(socketio?.getSelectedEntities('notLinkedToParent') ?? []).filter(
			(number) => number.id !== excludeId
		)
	);

	onMount(() => {
		socketio = new SocketIO<NumberExtended>(
			{
				namespace: '/number',
				sessionId: page.data.session.sessionId,
				parentId,
				queryParams: {
					'identity-ids': identities.map((identity) => identity.id).join(','),
					'request-access-data': true
				}
			},
			{
				snapshot: { entities: numbers, cursor },
				inherit: inheritPending,
				template: { value: 0, access_right: Action.OWN }
			}
		);
		socketio.identities = identities;
		socketio.createLinkedSelection('linkedToParent', false, parentId);
		socketio.createLinkedSelection('notLinkedToParent', true, parentId);
	});

	onDestroy(() => {
		socketio?.client.disconnect();
	});
</script>

<AddEntityCard
	{socketio}
	entityType={EntityType.NUMBER}
	{parentId}
	bind:inheritPending
	bind:labelPending
	bind:hidden={hideNew}
>
	{#snippet form(number, shareOptions)}
		<NumberForm
			{number}
			{shareOptions}
			{socketio}
			{parentId}
			bind:inheritPending
			bind:labelPending
		/>
	{/snippet}
	{#snippet existing()}
		{#each notLinkedNumbers as existingNumber (existingNumber.id)}
			<p>{existingNumber.value}</p>
		{/each}
	{/snippet}
</AddEntityCard>

<EntitySection
	id="linked-numbers"
	title="Linked Numbers"
	entityLabel="number"
	bind:hideNew
	bind:viewMode
	hasPending={!!socketio?.pendingEntities[0]}
>
	<div class="label">Numbers can be linked to presentations, texts and other numbers.</div>
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
		{#snippet numberIdCell(number: NumberExtended)}
			<IdBadge id={number.id} />
			<a
				href={resolve('/(layout)/number/(protected)/setup/[id]', { id: number.id })}
				aria-label={`Setup number ${number.value}`}
				class="link link-primary link-animated block truncate"
			>
				{number.value}
			</a>
		{/snippet}
		{#snippet actionsCell(number: NumberExtended)}
			<ActionButtons
				resourceId={number.id}
				accessRight={socketio?.accessRights[number.id]}
				{socketio}
				entityType="number"
			/>
		{/snippet}
		<Table
			columns={[
				{
					header: text('Value'),
					cell: snippet(numberIdCell),
					headerClass: 'w-3/5',
					cellClass: 'max-w-0'
				},
				{ header: text('Category'), cell: field<NumberExtended>('category') },
				{
					header: text('Access'),
					cell: value(() => '[Access]'),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: countIcon('andrsrxn:text-decrease-size'),
					cell: value<NumberExtended>((entity) => entity.texts?.length ?? 0)
				},
				{
					header: countIcon('andrsrxn:text-increase-size'),
					cell: value<NumberExtended>((entity) => entity.number_parents?.length ?? 0)
				},
				{
					header: text('Actions'),
					cell: snippet(actionsCell),
					headerClass: 'w-px text-center whitespace-nowrap',
					cellClass: 'w-px py-1 text-center align-middle whitespace-nowrap'
				}
			]}
			entityContainer={socketio}
			displaySelection="linkedToParent"
		>
			{#snippet menu()}
				<th colspan={5}></th>
				<th class="text-end"><SelectionActionButtons {socketio} /></th>
			{/snippet}
		</Table>
	{/snippet}
</EntitySection>

{#if debug}
	<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
		<div>
			<Title id="linkedNumberEntities">Entities</Title>
			<JsonData data={socketio?.entities ?? []} />
			<Title id="linkedNumberPending">Pending Entities</Title>
			<JsonData data={socketio?.pendingEntities ?? []} />
		</div>
		<div>
			<Title id="linkedNumberSelections">Linked / not linked</Title>
			<JsonData
				data={{
					linked: socketio?.getSelectedEntities('linkedToParent'),
					notLinked: notLinkedNumbers
				}}
			/>
		</div>
		<div>
			<Title id="linkedNumberAccess">Access</Title>
			<JsonData data={{ rights: socketio?.accessRights, policies: socketio?.accessPolicies }} />
		</div>
	</div>
{/if}
