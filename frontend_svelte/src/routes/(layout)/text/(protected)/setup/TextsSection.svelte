<script lang="ts">
	import { onDestroy, onMount } from 'svelte';

	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import ActionButtons from '$components/ActionButtons.svelte';
	import AddEntityCard from '$components/AddEntityCard.svelte';
	import EntitySection from '$components/EntitySection.svelte';
	import JsonData from '$components/JsonData.svelte';
	import SelectionActionButtons from '$components/SelectionActionButtons.svelte';
	import Table, { countIcon, field, icon, snippet, text, value } from '$components/Table.svelte';
	import Title from '$components/Title.svelte';
	import { Action } from '$lib/accessHandler';
	import { EntityType, getLanguageFlag } from '$lib/entities';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { Identity, TextExtended } from '$lib/types';

	import IdBadge from '../../../(protected)/IdBadge.svelte';
	import TextForm from './TextForm.svelte';

	let {
		parentId,
		texts,
		cursor,
		identities,
		excludeId
	}: {
		parentId: string;
		texts: TextExtended[];
		cursor: number;
		identities: Identity[];
		excludeId?: string;
	} = $props();

	let debug = $derived(page.url.searchParams.get('debug') === 'true');
	let socketio: SocketIO<TextExtended> = $state()!;
	let hideNew = $derived(page.url.searchParams.get('add-text') !== 'true');
	let viewMode = $state<'table' | 'grid' | 'list'>('table');
	let inheritPending = $state(true);
	let labelPending = $state('');
	let notLinkedTexts = $derived(
		(socketio?.getSelectedEntities('notLinkedToParent') ?? []).filter(
			(text) => text.id !== excludeId
		)
	);

	onMount(() => {
		socketio = new SocketIO<TextExtended>(
			{
				namespace: '/text',
				sessionId: page.data.session.sessionId,
				parentId,
				queryParams: {
					'identity-ids': identities.map((identity) => identity.id).join(','),
					'request-access-data': true
				}
			},
			{
				snapshot: { entities: texts, cursor },
				inherit: inheritPending,
				template: { content: '', language: 'en', access_right: Action.OWN }
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
	entityType={EntityType.TEXT}
	{parentId}
	bind:inheritPending
	bind:labelPending
	bind:hidden={hideNew}
>
	{#snippet form(text, shareOptions)}
		<TextForm {text} {shareOptions} {socketio} {parentId} bind:inheritPending bind:labelPending />
	{/snippet}
	{#snippet existing()}
		{#each notLinkedTexts as existingText (existingText.id)}
			<p>{existingText.content || existingText.id}</p>
		{/each}
	{/snippet}
</AddEntityCard>

<EntitySection
	id="linked-texts"
	title="Linked Texts"
	entityLabel="text"
	bind:hideNew
	bind:viewMode
	hasPending={!!socketio?.pendingEntities[0]}
>
	<div class="label">Texts can be linked to presentations, texts and numbers.</div>
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
		{#snippet textIdCell(text: TextExtended)}
			<IdBadge id={text.id} />
			<a
				href={resolve('/(layout)/text/(protected)/setup/[id]', { id: text.id })}
				aria-label={`Setup text ${text.content || text.id}`}
				class="link link-primary link-animated block truncate"
			>
				{text.content || text.id}
			</a>
		{/snippet}
		{#snippet languageCell(text: TextExtended)}
			<span class="{getLanguageFlag(text.language) ?? 'icon-[twemoji--flag-united-kingdom]'} size-5"
			></span>
		{/snippet}
		{#snippet actionsCell(text: TextExtended)}
			<ActionButtons
				resourceId={text.id}
				accessRight={socketio?.accessRights[text.id]}
				{socketio}
				entityType="text"
			/>
		{/snippet}
		<Table
			columns={[
				{
					header: text('Content'),
					cell: snippet(textIdCell),
					headerClass: 'w-3/5',
					cellClass: 'max-w-0'
				},
				{ header: text('Category'), cell: field<TextExtended>('category') },
				{ header: icon('tabler:language'), cell: snippet(languageCell) },
				{
					header: text('Access'),
					cell: value(() => '[Access]'),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: countIcon('andrsrxn:text-decrease-size'),
					cell: value<TextExtended>((entity) => entity.texts?.length ?? 0)
				},
				{
					header: countIcon('andrsrxn:text-increase-size'),
					cell: value<TextExtended>((entity) => entity.text_parents?.length ?? 0)
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
				<th colspan={6}></th>
				<th class="text-end"><SelectionActionButtons {socketio} /></th>
			{/snippet}
		</Table>
	{/snippet}
</EntitySection>

{#if debug}
	<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
		<div>
			<Title id="linkedTextEntities">Entities</Title>
			<JsonData data={socketio?.entities ?? []} />
			<Title id="linkedTextPending">Pending Entities</Title>
			<JsonData data={socketio?.pendingEntities ?? []} />
		</div>
		<div>
			<Title id="linkedTextSelections">Linked / not linked</Title>
			<JsonData
				data={{
					linked: socketio?.getSelectedEntities('linkedToParent'),
					notLinked: notLinkedTexts
				}}
			/>
		</div>
		<div>
			<Title id="linkedTextAccess">Access</Title>
			<JsonData data={{ rights: socketio?.accessRights, policies: socketio?.accessPolicies }} />
		</div>
	</div>
{/if}
