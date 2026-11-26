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
	import type { TextExtended } from '$lib/types';

	import NumbersSection from '../../../../number/(protected)/setup/NumbersSection.svelte';
	import TextForm from '../TextForm.svelte';
	import TextsSection from '../TextsSection.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	let textSocketio: SocketIO<TextExtended> = $state()!;
	let text = $derived(textSocketio?.entities.find((entity) => entity.id === page.params.id));

	onMount(() => {
		textSocketio = new SocketIO<TextExtended>(
			{
				namespace: '/text',
				sessionId: page.data.session.sessionId,
				queryParams: { 'request-access-data': true }
			},
			{
				snapshot: { entities: [data.payload.text], cursor: data.payload.textCursor }
			}
		);
		textSocketio.identities = data.payload.identities;
		textSocketio.client.on('deleted', (deletedId) => {
			if (deletedId === page.params.id) {
				goto(resolve('/(layout)/text/(protected)/setup'));
			}
		});
	});

	onDestroy(() => {
		textSocketio?.client.disconnect();
	});
</script>

<Display id="text-content">{text?.content || text?.id || 'Text'}</Display>
<div class="flex flex-col gap-2 md:flex-row">
	<a
		href={resolve('/(layout)/text/(protected)/setup')}
		class="btn btn-primary btn-gradient shadow-outline mx-4 rounded-full"
	>
		<span class="icon-[tabler--chevron-left]"></span>
		Go to all texts
	</a>
</div>

{#if textSocketio?.entities?.length}
	<AddEntityCard
		socketio={textSocketio}
		entityType={EntityType.TEXT}
		entityId={data.payload.text.id}
		title={(entity) => entity.content}
	>
		{#snippet form(entity, shareOptions)}
			<TextForm text={entity} {shareOptions} socketio={textSocketio} />
		{/snippet}
	</AddEntityCard>
{:else}
	<div class="label text-error" transition:slide={{ duration: 600 }}>
		<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
	</div>
{/if}

<Heading id="texts" sideBarEntry="Texts">Texts</Heading>
<TextsSection
	parentId={data.payload.text.id}
	texts={data.payload.texts}
	cursor={data.payload.textsCursor}
	identities={data.payload.identities}
	excludeId={page.params.id}
/>

<Heading id="numbers" sideBarEntry="Numbers">Numbers</Heading>
<NumbersSection
	parentId={data.payload.text.id}
	numbers={data.payload.numbers}
	cursor={data.payload.numbersCursor}
	identities={data.payload.identities}
	excludeId={page.params.id}
/>

{#if page.url.searchParams.get('debug') === 'true'}
	<JsonData data={textSocketio?.entities ?? []} />
{/if}
