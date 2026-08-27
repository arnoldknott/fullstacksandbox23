<script lang="ts">
	import type { RevealApi } from 'reveal.js';
	import { onDestroy, onMount } from 'svelte';
	import { flip } from 'svelte/animate';

	import { page } from '$app/state';
	import Card from '$components/Card.svelte';
	import ChatBubble from '$components/ChatBubble.svelte';
	import RevealJs from '$components/RevealJS.svelte';
	import { Action } from '$lib/accessHandler';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended, NumericalExtended } from '$lib/types';

	import type { PageData } from './$types';
	import Badge from './Badge.svelte';
	import FramedSlide from './FramedSlide.svelte';
	import Map from './Map.svelte';
	import MotivationTable from './MotivationTable.svelte';
	import NodeOverlay from './NodeOverlay.svelte';
	import Team from './Team.svelte';

	let { data }: { data: PageData } = $props();

	let preview = $derived(page.url.searchParams.get('preview') === 'true' ? true : false);

	$effect(() => {
		preview = page.url.searchParams.get('preview') === 'true';
	});

	let revealInstance = $state<RevealApi | undefined>(undefined);

	interface RevealFragmentEvent extends Event {
		fragment: HTMLElement;
		fragments: HTMLElement[];
	}

	// hard coding the selection of a specific question here
	// it needs to exist in the payload.questions array
	// and the selection here needs to find a unique result
	// this might differ from presentation to presentation
	// => up to the creator of the presentation
	let motivationQuestion = $derived(
		data.payload.questions.find((question) => question.question.includes('motivation'))
	);
	let placesQuestion = $derived(
		data.payload.questions.find((question) => question.question.includes('places'))
	);
	let commentsQuestion = $derived(
		data.payload.questions.find((question) => question.question.includes('comments'))
	);
	let socketioMotivation: SocketIO<NumericalExtended> = $state()!;
	let socketioPlaces: SocketIO<MessageExtended> = $state()!;
	let socketioComments: SocketIO<MessageExtended> = $state()!;
	let motivationAnswers = $derived(socketioMotivation?.entities ?? []);

	onMount(() => {
		socketioMotivation = new SocketIO<NumericalExtended>(
			{
				namespace: '/numerical',
				parentId: motivationQuestion?.id
			},
			{}
		);
		console.log('=== 🧦 Map.svelte - onMount - placesQuestion.id ===');
		console.log(placesQuestion?.id);
		socketioPlaces = new SocketIO<MessageExtended>(
			{
				namespace: '/message',
				parentId: placesQuestion?.id,
				queryParams: { 'request-access-data': true }
			},
			{
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
		socketioComments = new SocketIO<MessageExtended>(
			{
				namespace: '/message',
				parentId: commentsQuestion?.id,
				queryParams: { 'request-access-data': true }
			},
			{ template: { content: '', language: 'en' } }
		);
		socketioComments.createSortedSelection('sortedCommentsAnswers', 'creation_date', false);
	});

	$effect(() => {
		// Preseed data:
		// TBD: update to preseed with numbers coming from server-side via REST-API
		socketioMotivation.entities = motivationQuestion?.numericals ?? [];
		socketioPlaces.entities = placesQuestion?.messages ?? [];
		socketioComments.entities = commentsQuestion?.messages ?? [];
	});

	onDestroy(() => {
		socketioMotivation?.client.disconnect();
		socketioPlaces?.client.disconnect();
		socketioComments?.client.disconnect();
	});

	let motivationAnswersAverage: number = $derived.by(() => {
		if (motivationAnswers.length <= 5) {
			// if (motivationAnswers.length <= 1) {
			return 50;
		} else {
			const sum = motivationAnswers.reduce((acc, curr) => acc + curr.value, 0);
			return Math.round(sum / motivationAnswers.length);
		}
	});

	let averageMotivationColors = $state({ background: '0 0 0', text: '255 255 255' });
	let addColorToMotivationTable = $state(false);

	$effect(() => {
		if (revealInstance) {
			revealInstance.on('fragmentshown', (event: Event) => {
				const fragmentEvent = event as RevealFragmentEvent;
				if (fragmentEvent.fragment?.innerText === 'Dummy to trigger color event') {
					addColorToMotivationTable = true;
				}
			});
			revealInstance.on('fragmenthidden', (event: Event) => {
				const fragmentEvent = event as RevealFragmentEvent;

				if (fragmentEvent.fragment?.innerText === 'Dummy to trigger color event') {
					addColorToMotivationTable = false;
				}
			});
		}
		// updates background color on the slides, where addColorToMotivationTable changes
		if (
			revealInstance &&
			(motivationAnswersAverage || motivationAnswers.length === 6) &&
			addColorToMotivationTable !== undefined
		) {
			const currentSlide = revealInstance.getCurrentSlide();
			// console.log('=== synchronizing slide to update background color ===');
			// console.log($state.snapshot(averageMotivationColors));
			if (currentSlide) {
				revealInstance.syncSlide(currentSlide);
			}
		}
	});

	let commentsAnswersSorted = $derived(
		socketioComments?.getSelectedEntities('sortedCommentsAnswers') ?? []
	);
</script>

<RevealJs bind:reveal={revealInstance}>
	<section>
		<div class="text-[200px] font-bold">Welcome</div>
	</section>
	{#if preview}
		<section>
			<div
				class="r-stretch my-20 grid grid-cols-[1fr_max-content_1fr] items-center justify-between justify-items-start gap-12 text-7xl"
				// class="r-stretch mx-auto my-20 grid w-fit grid-cols-[auto_max-content_auto] items-center gap-12 text-7xl"
			>
				<a href="#motivation" class="justify-self-end" aria-label="Motivation"
					><span class="icon-[stash--circle-dot] bg-primary"></span></a
				>
				<a href="#motivation" aria-label="Motivation"
					><div class="text-primary font-bold">Motivation</div></a
				>
				<div></div>
				<a href="#diversity" aria-label="Diversity" class="justify-self-end"
					><span class="icon-[mingcute--lightning-fill] bg-primary"></span></a
				>
				<a href="#diversity" aria-label="Diversity"
					><div class="text-primary font-bold">Diversity</div></a
				>
				<div></div>
				<a href="#overview" aria-label="Overview" class="justify-self-end"
					><span class="icon-[f7--chat-bubble-2-fill] bg-primary"></span></a
				>
				<a href="#overview" aria-label="Overview"
					><div class="text-primary font-bold">Overview</div></a
				>
				<div></div>
			</div>
		</section>
		<FramedSlide part="motivation" color="primary">
			{#snippet footer()}
				<div>📖 Ib Ravn: Selvbestemmelsesteorien</div>
			{/snippet}
			<div class="mx-5 grid grid-cols-3 gap-10">
				<div
					class="text-secondary-content bg-secondary shadow-base-shadow shadow-large rounded-4xl p-7 font-semibold shadow-inner"
				>
					<Badge title="Relatedness" color="secondary" />
					<div class="mt-4">
						Your sense of belonging to a community and connection with other people to care for and
						feeling cared for.
					</div>
				</div>
				<div
					class="text-secondary-content bg-secondary shadow-base-shadow shadow-large rounded-4xl p-7 font-semibold shadow-inner"
				>
					<Badge title="Autonomy" color="secondary" />
					<div class="mt-4">
						Making your own decisions about your own life behaviours and goals.
					</div>
				</div>
				<div
					class="text-secondary-content bg-secondary shadow-base-shadow shadow-large rounded-4xl p-7 font-semibold shadow-inner"
				>
					<Badge title="Competence" color="secondary" />
					<div class="mt-4">
						Gaining mastery of your own life and environment to build self-esteem.
					</div>
				</div>
			</div>
		</FramedSlide>
		<FramedSlide
			part="motivation"
			section="table"
			color={addColorToMotivationTable ? 'neutral-container' : 'primary'}
			coloring={addColorToMotivationTable
				? {
						background: `rgb(${averageMotivationColors.background})`,
						text: `rgb(${averageMotivationColors.text})`
					}
				: { background: '', text: '' }}
		>
			{#if motivationQuestion}
				<MotivationTable
					questionId={motivationQuestion?.id}
					socketio={socketioMotivation}
					averageMotivation={motivationAnswersAverage}
					bind:averageColors={averageMotivationColors}
				/>
			{/if}
			{#snippet footer()}
				<div class="relative mt-5">
					<div class="absolute top-0 right-0 mt-20 flex flex-row gap-2">
						<span class="badge badge-lg badge-secondary shadow-outline shadow">
							{motivationAnswersAverage}
						</span>
						<span class="badge badge-lg badge-info shadow-outline shadow">
							{motivationAnswers.length}
						</span>
						<span class="text-base-300 text-lg"> {addColorToMotivationTable}</span>
					</div>
				</div>
			{/snippet}
		</FramedSlide>
		<FramedSlide part="diversity" color="primary">
			Diversity content here: stating how we are diverse in the course;
		</FramedSlide>
		<FramedSlide part="diversity" section="map" color="primary">
			<Map {revealInstance} socketio={socketioPlaces} />
		</FramedSlide>
		<FramedSlide part="overview" color="primary">
			<div class="grid grid-cols-2 gap-10">
				<div class="flex flex-col gap-10">
					<div class="text-secondary absolute top-2/12 left-70 -mt-10 text-7xl font-bold">
						Modules
					</div>
					<NodeOverlay
						buttonExtraClasses="btn-secondary rounded-full top-3/12 left-30 w-150 h-30"
						cardExtraClasses="bg-secondary-container text-secondary-container-content text-4xl"
					>
						{#snippet buttonText()}
							Passives
						{/snippet}
						{#snippet header()}
							Passives
						{/snippet}
						<ul>
							<li>Resisters, Capacitors, and Inductors</li>
							<li>Simulation & hands-on</li>
						</ul>
					</NodeOverlay>
					<NodeOverlay
						buttonExtraClasses="btn-secondary  rounded-full top-5/12 left-30 w-150 h-30"
						cardExtraClasses="bg-secondary-container text-secondary-container-content text-4xl"
					>
						{#snippet buttonText()}
							Electromagnetic Compatibility
						{/snippet}
						{#snippet header()}
							Electromagnetic Compatibility
						{/snippet}
						<ul>
							<li>Introduction & test setups</li>
							<li>Physical phenomena & examples</li>
							<li>Industrial examples</li>
							<li>Standardization</li>
						</ul>
					</NodeOverlay>
					<NodeOverlay
						buttonExtraClasses="btn-secondary rounded-full top-7/12 left-30 w-150 h-30"
						cardExtraClasses="bg-secondary-container text-secondary-container-content text-4xl"
					>
						{#snippet buttonText()}
							Printed Circuit Boards
						{/snippet}
						{#snippet header()}
							<div class="text-5xl font-bold">Printed Circuit Boards</div>
						{/snippet}
						<ul>
							<li>Design workflow</li>
							<li>Computer Aided Design</li>
							<li>Implementation</li>
							<li>Design review</li>
							<li>Finish design</li>
						</ul>
					</NodeOverlay>
					<NodeOverlay
						buttonExtraClasses="btn-secondary rounded-full top-9/12 left-30 w-150 h-30"
						cardExtraClasses="bg-secondary-container text-secondary-container-content text-4xl"
					>
						{#snippet buttonText()}
							Environment
						{/snippet}
						{#snippet header()}
							Environment
						{/snippet}
						<ul>
							<li>Thermal impact</li>
							<li>Radiation from space</li>
						</ul>
					</NodeOverlay>
				</div>
				<!-- fragment fade-in -->
				<div class=" flex flex-col gap-10">
					<div class="text-secondary absolute top-2/12 right-70 -mt-10 text-7xl font-bold">
						Framework
					</div>
					<Card
						id="activities"
						extraClasses="bg-secondary-container text-secondary-container-content text-4xl mt-10"
					>
						{#snippet header()}
							<div class="text-5xl font-bold">Activities</div>
						{/snippet}
						<ul>
							<li>Lectures</li>
							<li>Flipped classroom</li>
							<li>Laboratory Exercises</li>
							<li>Group work</li>
						</ul>
					</Card>
					<Card
						id="activities"
						extraClasses="bg-secondary-container text-secondary-container-content text-4xl mt-10"
					>
						{#snippet header()}
							<div class="text-5xl font-bold">Assessment</div>
						{/snippet}
						<ul>
							<li>Pass/Fail</li>
							<li>One individual learning reflection per module</li>
							<li>Hand in the first question in 3 out of 4 learning reflections to pass</li>
						</ul>
					</Card>
					<dl>
						<!-- <dt>Activities</dt>
					<ul>
						<li>Lectures</li>
						<li>Flipped classroom</li>
						<li>Laboratory Exercises</li>
						<li>Group work</li>
					</ul> -->
						<!-- <dt>Assessment</dt>
					<ul>
						<li>Pass/Fail</li>
						<li>One individual learning reflection per module</li>
						<li>Hand in the first question in 3 out of 4 learning reflections to pass</li>
					</ul> -->
					</dl>
				</div>
			</div></FramedSlide
		>
		<FramedSlide part="overview" section="team" color="primary">
			<Team />
		</FramedSlide>
		<FramedSlide part="overview" section="bubbles" color="success">
			<div class="absolute top-30 left-0">
				<ChatBubble variant="success" tailAngle={150} shadow={true}>
					<div class="heading-large">Everything in the course is an invitation.</div>
				</ChatBubble>
			</div>
			<div class="fragment fade-in absolute top-60 right-5">
				<ChatBubble variant="success" tailAngle={50} shadow={true}>
					<div class="heading-large">You never disturb, you always contribute.</div>
				</ChatBubble>
			</div>
			<div class="fragment fade-in absolute top-90 left-0">
				<ChatBubble variant="success" tailAngle={30} shadow={true}>
					<div class="heading-large">There's no cheating: use what's available.</div>
				</ChatBubble>
			</div>
			<div class="fragment fade-in absolute top-130 right-15">
				<ChatBubble variant="success" tailAngle={190} shadow={true}>
					<div class="heading-large">No "deadlines" ☠️ only "life lines" 🌱.</div>
				</ChatBubble>
			</div>
			<div class="fragment fade-in absolute top-150 left-20 w-200">
				<ChatBubble variant="success" tailAngle={310} shadow={true}>
					<div class="heading-large">
						No ambitions on other peoples behalf. <br />
						Only support intrinsic motivation.
					</div>
				</ChatBubble>
			</div>
		</FramedSlide>
		<section>
			<div class="r-stretch mx-10 mt-10">
				<div class="text-left">
					{#if socketioComments?.pendingEntities[0]}
						<label class="heading text-6xl" for="sharing">
							Do you have comments or questions? 🤔
						</label>
						<textarea
							class="heading placeholder:title-large w-[90%] border border-2 p-2 shadow-inner placeholder:italic"
							placeholder="These questions and comments are publically available on the internet for everyone, who has a link to this presentation. Sharing is caring 🫶 Press Enter to send."
							id="sharing"
							bind:value={socketioComments.pendingEntities[0].content}
							onkeydown={(event) => {
								if (event.key === 'Enter' && !event.shiftKey) {
									event.preventDefault();
									socketioComments.addPendingAccessPolicy(socketioComments.pendingEntities[0].id, {
										public: true,
										action: Action.READ
									});
									socketioComments.submitEntity(
										socketioComments.pendingEntities[0],
										commentsQuestion?.id,
										true
									);
									socketioComments.createPending();
								}
							}}></textarea>
					{:else}
						<div class="label text-error">
							<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
						</div>
					{/if}
				</div>

				{#snippet messageAnswer(text: string, date: Date | undefined, index: number)}
					<div class="chat chat-receiver">
						<div
							class="chat-bubble text-left text-wrap break-words {index % 2
								? 'chat-bubble-accent'
								: 'chat-bubble-primary'}"
						>
							{text}
							<div class="label text-right">
								{date
									? new Date(date).toLocaleString(undefined, {
											dateStyle: 'short',
											timeStyle: 'short'
										})
									: 'Thanks for your contribution 🙏'}
							</div>
						</div>
					</div>
				{/snippet}
				<div class="heading mt-8">
					<div class="mx-5 grid max-h-[600px] grid-cols-3 gap-6 overflow-y-auto">
						{#each commentsAnswersSorted as answer, index (answer.id)}
							<div animate:flip={{ duration: 300 }}>
								{@render messageAnswer(answer.content, answer.creation_date, index)}
							</div>
						{/each}
					</div>
				</div>
			</div>
		</section>

		<section>
			<div class="text-[200px] font-bold">Thank you! 🙏</div>
		</section>
	{/if}
</RevealJs>
