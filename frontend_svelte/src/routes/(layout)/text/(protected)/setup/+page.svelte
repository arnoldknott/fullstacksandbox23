<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { fade, slide } from 'svelte/transition';

	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import ActionButtons from '$components/ActionButtons.svelte';
	import AddEntityCard from '$components/AddEntityCard.svelte';
	import Card from '$components/Card.svelte';
	import Display from '$components/Display.svelte';
	import JsonData from '$components/JsonData.svelte';
	import Table, { countIcon, field, icon, snippet, text, value } from '$components/Table.svelte';
	import Title from '$components/Title.svelte';
	import { Action } from '$lib/accessHandler';
	import { EntityType, getLanguageFlag } from '$lib/entities';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { TextExtended } from '$lib/types';

	import IdBadge from '../../../(protected)/IdBadge.svelte';
	import type { PageData } from './$types';
	import TextForm from './TextForm.svelte';

	let { data }: { data: PageData } = $props();

	// uses the one, that gets set in sidebar and communicated
	// through the search params of the url
	let debug = $derived(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		debug = page.url.searchParams.get('debug') === 'true';
	});

	let socketioTexts: SocketIO<TextExtended> = $state()!;
	onMount(() => {
		socketioTexts = new SocketIO<TextExtended>(
			{
				namespace: '/text',
				sessionId: data?.session?.sessionId || '',
				queryParams: {
					'request-access-data': true,
					'identity-ids': data.payload.identities.map((identity) => identity.id).join(',')
				}
			},
			{
				snapshot: {
					entities: data.payload.texts,
					cursor: data.payload.cursor
				},
				template: {
					content: '',
					language: 'en',
					access_right: Action.OWN
					// creation_date: new Date(Date.now()) // TBD: Check if this is necessary?
				}
			}
		);

		socketioTexts.identities = data.payload.identities;
	});

	onDestroy(() => {
		socketioTexts?.client.disconnect();
	});

	let hideNewTextCard: boolean = $state(!(page.url.searchParams.get('new') === 'true'));
	let inheritPending = $state(true);

	// For showing existing texts:
	let viewMode = $state<'grid' | 'list' | 'table'>('table');
</script>

<Display id="overview-texts">Texts</Display>

<!-- <JsonData data={data.payload.identities} /> -->

{#if socketioTexts?.pendingEntities[0]}
	<AddEntityCard
		socketio={socketioTexts}
		entityType={EntityType.TEXT}
		bind:inheritPending
		bind:hidden={hideNewTextCard}
	>
		{#snippet form(text, shareOptions)}
			<TextForm {text} {shareOptions} socketio={socketioTexts} bind:inheritPending />
		{/snippet}
	</AddEntityCard>
{:else if !socketioTexts?.pendingEntities[0] && !hideNewTextCard}
	<div class="label text-error" transition:slide={{ duration: 600 }}>
		<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
	</div>
{/if}

<Card id="existing-texts" extraClasses="mt-6">
	{#snippet header()}
		<div class="flex justify-between">
			<Title id="existingTexts" class="grow">Overview</Title>
			<div class="flex flex-row items-center justify-center">
				{#if hideNewTextCard || !socketioTexts?.pendingEntities[0]}
					<button
						transition:fade={{ duration: 600 }}
						class="btn btn-primary-container btn-gradient label btn shadow-outline mx-4 rounded-full shadow-sm"
						aria-label="Add new text"
						onclick={() => (hideNewTextCard = false)}
					>
						<span class="icon-[fa6-solid--plus] size-5"></span>
						<!-- <span class="hidden ">Add</span> -->
						<span class="hidden sm:inline">Add new</span>
						<span class="hidden md:inline">text</span>
					</button>
				{/if}
				<div class="join shadow-outline rounded-full shadow-sm">
					<!-- <button
						aria-label="Preview"
						class="btn join-item btn-secondary btn-gradient btn-sm rounded-l-full py-4 {viewMode !==
						'preview'
							? 'opacity-60'
							: ''}"
						onclick={() => (viewMode = 'preview')}
					>
						<span class="icon-[material-symbols--preview-outline] size-5"></span>
					</button> -->
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
	<!-- <div class="w-full overflow-x-auto {viewMode !== 'preview' ? 'hidden' : ''}">
		<p class="bg-warning text-warning-content rounded-lg p-4">Preview mode is not developed yet</p>
	</div> -->
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
	<div class="w-full {viewMode !== 'table' ? 'hidden' : ''}">
		{#snippet textIdCell(text: TextExtended)}
			<IdBadge id={text.id} />
			<a
				href={resolve('/(layout)/text/(protected)/setup/[id]', {
					id: text.id
				})}
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

		{#snippet textActionsCell(text: TextExtended)}
			<ActionButtons
				resourceId={text.id}
				accessRight={socketioTexts?.accessRights[text.id]}
				socketio={socketioTexts}
				entityType="text"
			/>
		{/snippet}
		<Table
			columns={[
				{
					header: text('Id / Slug'),
					cell: snippet(textIdCell),
					headerClass: 'w-3/5',
					cellClass: 'max-w-0'
				},
				{
					header: text('Confidential'),
					cell: field<TextExtended>('confidential'),
					headerClass: 'text-left',
					cellClass: 'text-left'
				},
				{
					header: icon('tabler:language'),
					cell: snippet(languageCell),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: text('Category'),
					cell: field<TextExtended>('category'),
					headerClass: 'text-left',
					cellClass: 'text-left'
				},
				{
					header: text('Access'),
					cell: value(() => '[Access]'),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: countIcon('andrsrxn:text-decrease-size'),
					cell: value<TextExtended>((text) => text.texts?.length ?? 0),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: countIcon('andrsrxn:text-increase-size'),
					cell: value<TextExtended>((text) => text.text_parents?.length ?? 0),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},

				{
					header: text('Actions'),
					cell: snippet(textActionsCell),
					headerClass: 'w-px text-center whitespace-nowrap',
					cellClass: 'w-px py-1 text-center align-middle whitespace-nowrap'
				}
			]}
			entityContainer={socketioTexts}
		/>
	</div>
</Card>

{#if debug}
	<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
		<div>
			<Title id="pendingEntities">Pending Entities</Title>
			<JsonData data={socketioTexts?.pendingEntities ?? []} />
			<Title id="entities">Entities</Title>
			<JsonData data={socketioTexts?.entities ?? []} />
		</div>
		<div>
			<Title id="identities">Selected</Title>
			<JsonData data={socketioTexts?.selections['selected'] ?? []} />
			<Title id="identities">Identities</Title>
			<JsonData data={socketioTexts?.identities ?? []} />
		</div>
		<div>
			<Title id="accessRights">Access Rights</Title>
			<JsonData data={socketioTexts?.accessRights ?? []} />
			<Title id="accessPolicies">Access Policies</Title>
			<JsonData data={socketioTexts?.accessPolicies ?? []} />
		</div>
	</div>
{/if}
