<script lang="ts">
	import type { RevealApi } from 'reveal.js';
	import { onDestroy, onMount } from 'svelte';

	import RevealJs from '$components/RevealJS.svelte';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended } from '$lib/types';

	import type { PageData } from './$types';
	import Comments from './Comments.svelte';
	import FramedSlide from './FramedSlide.svelte';
	import Library from './Library.svelte';
	import Map from './Map.svelte';
	import Overview from './Overview.svelte';

	let { data }: { data: PageData } = $props();

	let revealInstance = $state<RevealApi | undefined>(undefined);

	let returnToSlide = $state<string | undefined>(undefined);

	// $effect(() => {
	// 	preview = page.url.searchParams.get('preview') === 'true';
	// });

	$effect(() => {
		const handleSlideChanged = (event: Event) => {
			const { currentSlide, previousSlide } = event as Event & {
				currentSlide?: HTMLElement;
				previousSlide?: HTMLElement;
			};
			if (currentSlide?.id === 'terms-and-conditions' && previousSlide?.id) {
				returnToSlide = previousSlide.id;
			}
		};
		revealInstance?.on('slidechanged', (event: Event) => handleSlideChanged(event));
		return () => revealInstance?.off('slidechanged', handleSlideChanged);
	});

	// let motivationQuestion = $derived(
	// 	data.payload.questions.find((question) => question.question.includes('motivation'))
	// );
	let placesQuestion = $derived(
		data.payload.questions.find((question) => question.question.includes('places'))
	);
	let booksQuestion = $derived(
		data.payload.questions.find((question) => question.question.includes('books'))
	);
	let commentsQuestion = $derived(
		data.payload.questions.find((question) => question.question.includes('comments'))
	);
	console.log(commentsQuestion?.id);
	// let socketioMotivation: SocketIO<NumericalExtended> = $state()!;
	let socketioPlaces: SocketIO<MessageExtended> = $state()!;
	let socketioBooks: SocketIO<MessageExtended> = $state()!;
	let socketioComments: SocketIO<MessageExtended> = $state()!;
	// let motivationAnswers = $derived(socketioMotivation?.entities ?? []);

	onMount(() => {
		// socketioMotivation = new SocketIO<NumericalExtended>(
		// 	{
		// 		namespace: '/numerical',
		// 		parentId: motivationQuestion?.id
		// 	},
		// 	{
		// 		snapshot: data.payload.motivationSnapshot
		// 	}
		// );
		socketioPlaces = new SocketIO<MessageExtended>(
			{
				namespace: '/message',
				parentId: placesQuestion?.id,
				queryParams: { 'request-access-data': true }
			},
			{
				snapshot: data.payload.placesSnapshot,
				template: {
					content: JSON.stringify({
						emoji: '📍',
						name: '',
						text: '',
						coords: { lat: 0, lng: 0 },
						marker: undefined
					}),
					language: 'en'
				}
			}
		);
		socketioPlaces.createSortedSelection('sortedPlacesAnswers', 'creation_date', false);
		socketioBooks = new SocketIO<MessageExtended>(
			{
				namespace: '/message',
				parentId: booksQuestion?.id,
				queryParams: { 'request-access-data': true }
			},
			{
				snapshot: data.payload.booksSnapshot,
				template: { content: '', language: 'en' }
			}
		);
		socketioBooks.createSortedSelection('sortedBooksAnswers', 'creation_date', false);
		socketioComments = new SocketIO<MessageExtended>(
			{
				namespace: '/message',
				parentId: commentsQuestion?.id,
				queryParams: { 'request-access-data': true }
			},
			{
				snapshot: data.payload.commentsSnapshot,
				template: { content: '', language: 'en' }
			}
		);
		socketioComments.createSortedSelection('sortedCommentsAnswers', 'creation_date', false);
	});

	onDestroy(() => {
		// socketioMotivation?.client.disconnect();
		socketioPlaces?.client.disconnect();
		socketioBooks?.client.disconnect();
		socketioComments?.client.disconnect();
	});
</script>

{#snippet interactiveElementNotAvailable(elementName: string)}
	<div class="flex h-full w-full flex-col items-center justify-center gap-5 text-center">
		<div class="text-6xl font-bold">⚠️</div>
		<div class="text-2xl font-semibold">Interactive {elementName} is not available.</div>
		<div class="text-base-content/70 text-lg">
			This interactive element is not available in the current context.<br />
			Please inform the presenter about it.
		</div>
	</div>
{/snippet}

<RevealJs bind:reveal={revealInstance}>
	<section>
		<div class="text-base-content-variant text-[200px] font-bold">Welcome</div>
	</section>
	<FramedSlide part="checkin" section="map" hideProgressBar={true}>
		{#if placesQuestion}
			<!-- <div class="text-secondary text-center text-7xl font-bold">Check in</div> -->
			<Map {revealInstance} socketio={socketioPlaces} />
		{:else}
			{@render interactiveElementNotAvailable('map')}
		{/if}
	</FramedSlide>
	<FramedSlide part="overview">
		<Overview
			items={[
				{
					icon: 'stash:circle-dot',
					title: 'Context'
				},
				// {
				// 	icon: 'vaadin:thumbs-up-o',
				// 	title: 'Motivation'
				// },
				{
					icon: 'glyphs:books-bold',
					title: 'Inspiration'
				},
				{
					icon: 'carbon:development',
					title: 'Implementation'
				},
				{
					icon: 'bi:bar-chart',
					title: 'Results'
				}
			]}
		/>
	</FramedSlide>

	<FramedSlide part="context">Course 2nd semester -> linearising</FramedSlide>
	<FramedSlide>Course 2nd semester -> a bit closer to reality</FramedSlide>
	<FramedSlide>
		Master level -> closely related to product design -> linearized models ain't no good any more
	</FramedSlide>
	<FramedSlide>Drawing from BusinessIllustrator - closed box -> open box</FramedSlide>
	<FramedSlide>Allan Watts - Chinese Farmer ?</FramedSlide>
	<FramedSlide part="inspiration">
		<Library />
	</FramedSlide>
	<FramedSlide>Start with nature pictures here</FramedSlide>
	<FramedSlide part="implementation">Principles - see wisdom seat</FramedSlide>
	<FramedSlide>Learning reflections</FramedSlide>
	<FramedSlide part="results">Overview of results</FramedSlide>
	<FramedSlide part="results" section="quantitative">
		Quantitative results: learning, responsibility, meditation, sharing comments
	</FramedSlide>
	<FramedSlide part="results" section="qualitative">Qualitative results:</FramedSlide>
	<FramedSlide part="comments-and-questions" hideProgressBar>
		{#if commentsQuestion}
			<Comments socketio={socketioComments} question={commentsQuestion} />
		{:else}
			{@render interactiveElementNotAvailable('comments and questions dialog')}
		{/if}
	</FramedSlide>
	<FramedSlide>
		planetary boundaries -> inner work -> trust<br />
		stressed people -> stressed systems -> stressed planet (from regenerative leadership)
	</FramedSlide>

	<FramedSlide part="terms-and-conditions">
		<div class="text-5xl font-bold">Terms & Conditions</div>
		<dl>
			<dt>Data storage</dt>
			<dd>
				By entering your data, you acknowledge, that your data is stored in a database on the
				Technical University of Denmark's tenant in Microsoft Azure.
			</dd>
		</dl>
		<dl>
			<dt>Visibility of data</dt>
			<dd>
				Currently these slides are under development, there is no login and hence everyone on the
				internet with the link to the presentation can see what you have entered.
			</dd>
		</dl>
		<dl>
			<dt>Deletion of data</dt>
			<dd>
				In case you want any of your data deleted, please send a screenshot of what you want to have
				deleted to Arnold.
			</dd>
		</dl>
		{#if returnToSlide}
			<div>
				<span class="icon-[fa-regular--hand-point-right] mr-4 size-7"></span>Back to
				<a href="#{returnToSlide}" class="link link-animated"
					>{returnToSlide.replaceAll('-', ' ')}</a
				>.
			</div>
		{/if}
	</FramedSlide>
</RevealJs>
