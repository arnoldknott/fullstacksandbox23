<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { slide } from 'svelte/transition';

	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import AddEntityCard from '$components/AddEntityCard.svelte';
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';
	import JsonData from '$components/JsonData.svelte';
	import { EntityType } from '$lib/entities';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { NumberExtended } from '$lib/types';

	import TextsSection from '../../../../text/(protected)/setup/TextsSection.svelte';
	import NumberForm from '../NumberForm.svelte';
	import NumbersSection from '../NumbersSection.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	let numberSocketio: SocketIO<NumberExtended> = $state()!;
	let number = $derived(numberSocketio?.entities.find((entity) => entity.id === page.params.id));

	onMount(() => {
		numberSocketio = new SocketIO<NumberExtended>(
			{
				namespace: '/number',
				sessionId: page.data.session.sessionId,
				queryParams: { 'request-access-data': true }
			},
			{
				snapshot: { entities: [data.payload.number], cursor: data.payload.numberCursor }
			}
		);
		numberSocketio.identities = data.payload.identities;
		numberSocketio.client.on('deleted', (deletedId) => {
			if (deletedId === page.params.id) {
				goto(resolve('/(layout)/number/(protected)/setup'));
			}
		});
	});

	onDestroy(() => {
		numberSocketio?.client.disconnect();
	});
</script>

<Display id="number-value">{number?.value ?? number?.id ?? 'Number'}</Display>
<div class="flex flex-col gap-2 md:flex-row">
	<a
		href={resolve('/(layout)/number/(protected)/setup')}
		class="btn btn-primary btn-gradient shadow-outline mx-4 rounded-full"
	>
		<span class="icon-[tabler--chevron-left]"></span>
		Go to all numbers
	</a>
</div>

{#if numberSocketio?.entities?.length}
	<AddEntityCard
		socketio={numberSocketio}
		entityType={EntityType.NUMBER}
		entityId={data.payload.number.id}
		title={(entity) => String(entity.value)}
	>
		{#snippet form(entity, shareOptions)}
			<NumberForm number={entity} {shareOptions} socketio={numberSocketio} />
		{/snippet}
	</AddEntityCard>
{:else}
	<div class="label text-error" transition:slide={{ duration: 600 }}>
		<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
	</div>
{/if}

<Heading id="texts" sideBarEntry="Texts">Texts</Heading>
<TextsSection
	parentId={data.payload.number.id}
	texts={data.payload.texts}
	cursor={data.payload.textsCursor}
	identities={data.payload.identities}
/>

<Heading id="numbers" sideBarEntry="Numbers">Numbers</Heading>
<NumbersSection
	parentId={data.payload.number.id}
	numbers={data.payload.numbers}
	cursor={data.payload.numbersCursor}
	identities={data.payload.identities}
	excludeId={page.params.id}
/>

{#if page.url.searchParams.get('debug') === 'true'}
	<JsonData data={numberSocketio?.entities ?? []} />
{/if}
