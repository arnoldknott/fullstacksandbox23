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
	import Table, { countIcon, field, snippet, text, value } from '$components/Table.svelte';
	import Title from '$components/Title.svelte';
	import { Action } from '$lib/accessHandler';
	import { EntityType } from '$lib/entities';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { NumberExtended } from '$lib/types';

	import IdBadge from '../../../(protected)/IdBadge.svelte';
	import type { PageData } from './$types';
	import NumberForm from './NumberForm.svelte';

	let { data }: { data: PageData } = $props();

	// uses the one, that gets set in sidebar and communicated
	// through the search params of the url
	let debug = $derived(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		debug = page.url.searchParams.get('debug') === 'true';
	});

	let socketioNumbers: SocketIO<NumberExtended> = $state()!;
	onMount(() => {
		socketioNumbers = new SocketIO<NumberExtended>(
			{
				namespace: '/number',
				sessionId: data?.session?.sessionId || '',
				queryParams: {
					'request-access-data': true,
					'identity-ids': data.payload.identities.map((identity) => identity.id).join(',')
				}
			},
			{
				snapshot: {
					entities: data.payload.numbers,
					cursor: data.payload.cursor
				},
				template: {
					value: 0,
					access_right: Action.OWN
					// creation_date: new Date(Date.now()) // TBD: Check if this is necessary?
				}
			}
		);

		socketioNumbers.identities = data.payload.identities;
	});

	onDestroy(() => {
		socketioNumbers?.client.disconnect();
	});

	let hideNewNumberCard: boolean = $state(!(page.url.searchParams.get('new') === 'true'));
	let inheritPending = $state(true);

	// For showing existing numbers:
	let viewMode = $state<'grid' | 'list' | 'table'>('table');
</script>

<Display id="overview-numbers">Numbers</Display>

<!-- <JsonData data={data.payload.identities} /> -->

{#if socketioNumbers?.pendingEntities[0]}
	<AddEntityCard
		socketio={socketioNumbers}
		entityType={EntityType.NUMBER}
		bind:inheritPending
		bind:hidden={hideNewNumberCard}
	>
		{#snippet form(number, shareOptions)}
			<NumberForm {number} {shareOptions} socketio={socketioNumbers} bind:inheritPending />
		{/snippet}
	</AddEntityCard>
{:else if !socketioNumbers?.pendingEntities[0] && !hideNewNumberCard}
	<div class="label text-error" transition:slide={{ duration: 600 }}>
		<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
	</div>
{/if}

<Card id="existing-numbers" extraClasses="mt-6">
	{#snippet header()}
		<div class="flex justify-between">
			<Title id="existingNumbers" class="grow">Overview</Title>
			<div class="flex flex-row items-center justify-center">
				{#if hideNewNumberCard || !socketioNumbers?.pendingEntities[0]}
					<button
						transition:fade={{ duration: 600 }}
						class="btn btn-primary-container btn-gradient label btn shadow-outline mx-4 rounded-full shadow-sm"
						aria-label="Add new number"
						onclick={() => (hideNewNumberCard = false)}
					>
						<span class="icon-[fa6-solid--plus] size-5"></span>
						<!-- <span class="hidden ">Add</span> -->
						<span class="hidden sm:inline">Add new</span>
						<span class="hidden md:inline">number</span>
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
		{#snippet numberIdCell(number: NumberExtended)}
			<IdBadge id={number.id} />
			<a
				href={resolve('/(layout)/number/(protected)/setup/[id]', {
					id: number.id
				})}
				aria-label={`Setup number ${number.value ?? number.id}`}
				class="link link-primary link-animated block truncate"
			>
				{number.value ?? number.id}
			</a>
		{/snippet}
		{#snippet numberActionsCell(number: NumberExtended)}
			<ActionButtons
				resourceId={number.id}
				accessRight={socketioNumbers?.accessRights[number.id]}
				socketio={socketioNumbers}
				entityType="number"
			/>
		{/snippet}
		<Table
			columns={[
				{
					header: text('Value / Id'),
					cell: snippet(numberIdCell),
					headerClass: 'w-3/5',
					cellClass: 'max-w-0'
				},
				{
					header: text('Category'),
					cell: field<NumberExtended>('category'),
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
					cell: value<NumberExtended>((entity) => entity.texts?.length ?? 0),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: countIcon('andrsrxn:text-increase-size'),
					cell: value<NumberExtended>((entity) => entity.numbers?.length ?? 0),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},

				{
					header: text('Actions'),
					cell: snippet(numberActionsCell),
					headerClass: 'w-px text-center whitespace-nowrap',
					cellClass: 'w-px py-1 text-center align-middle whitespace-nowrap'
				}
			]}
			entityContainer={socketioNumbers}
		/>
	</div>
</Card>

{#if debug}
	<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
		<div>
			<Title id="pendingEntities">Pending Entities</Title>
			<JsonData data={socketioNumbers?.pendingEntities ?? []} />
			<Title id="entities">Entities</Title>
			<JsonData data={socketioNumbers?.entities ?? []} />
		</div>
		<div>
			<Title id="identities">Selected</Title>
			<JsonData data={socketioNumbers?.selections['selected'] ?? []} />
			<Title id="identities">Identities</Title>
			<JsonData data={socketioNumbers?.identities ?? []} />
		</div>
		<div>
			<Title id="accessRights">Access Rights</Title>
			<JsonData data={socketioNumbers?.accessRights ?? []} />
			<Title id="accessPolicies">Access Policies</Title>
			<JsonData data={socketioNumbers?.accessPolicies ?? []} />
		</div>
	</div>
{/if}
