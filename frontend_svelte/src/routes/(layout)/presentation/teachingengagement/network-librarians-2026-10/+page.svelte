<script lang="ts">
	import Icon from '@iconify/svelte';
	import type { RevealApi } from 'reveal.js';
	import { onDestroy, onMount } from 'svelte';

	import ChatBubble from '$components/ChatBubble.svelte';
	import RevealJs from '$components/RevealJS.svelte';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended } from '$lib/types';

	import type { PageData } from './$types';
	import CardOverlay from './CardOverlay.svelte';
	import Comments from './Comments.svelte';
	import FramedSlide from './FramedSlide.svelte';
	import Library from './Library.svelte';
	import Map from './Map.svelte';
	import Overview from './Overview.svelte';

	let { data }: { data: PageData } = $props();

	let revealInstance = $state<RevealApi | undefined>(undefined);

	// $effect(() => {
	// 	preview = page.url.searchParams.get('preview') === 'true';
	// });

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

	let returnToSlide = $state<string | undefined>(undefined);
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

	let modulesContentColumn: HTMLDivElement | undefined = $state();

	let hideModules = $state({
		reflections: true,
		closedQuestions: true,
		openQuestions: true
	});

	const hideAllToggleOne = (toggleKey: string) => {
		Object.keys(hideModules).forEach((key) => {
			if (key !== toggleKey) {
				hideModules[key as keyof typeof hideModules] = true;
			} else {
				hideModules[key as keyof typeof hideModules] =
					!hideModules[key as keyof typeof hideModules];
			}
		});
	};
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
	<FramedSlide part="overview" hideProgressBar={true}>
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
		<!-- <div class="absolute top-0 right-0 h-[100px] w-[800px]">
			<div class="h-full w-full border-4 border-red-400">progress</div>
		</div> -->
	</FramedSlide>

	<FramedSlide part="context" section="2nd-semester" title="Course: 2nd semester">
		<div class="grid grid-cols-2 gap-6">
			<div
				class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-6 shadow-inner"
			>
				<div class="text-center text-5xl font-bold">Outer Ecosystem</div>
				<ul class="list-disc">
					<li>core competences in<br />electrical engineering</li>
					<li>mandatory for two study lines</li>
					<li>~ 10 different study lines</li>
					<li>~ 120 participants</li>
					<li>fundamental and mathematical</li>
					<li>intense and challenging content</li>
					<li>in parallel with 3 other tough and intense courses: math, physics and programming</li>
				</ul>
			</div>
			<div
				class="bg-primary fragment text-primary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-6 shadow-inner"
			>
				<div class="text-center text-5xl font-bold">Inner Ecosystem</div>

				<div class="flex justify-between gap-4 py-4">
					<div class="w-full">
						<iframe
							title="Electric circuits slides"
							src="/teachingengagement/presentation-electric-circuits.pdf"
							class="shadow-base-shadow m-0! h-full w-full rounded-4xl object-contain shadow-lg"
						>
						</iframe>
					</div>
					<a
						href="https://www.saxo.com/dk/the-analysis-and-design-of-linear-circuits_bog_9781119913023?srsltid=AU7gw4UBKmyh8Tol04cqWmnOr-5fRqaOctZY3i1baqk6wsAwpZfHKPj2"
						target="_blank"
						rel="noopener noreferrer"
						class="h-full"
					>
						<img
							src="https://imgcdn.saxo.com/_9781119913023"
							alt="The analysis and design of linear circuits - book cover"
							class="shadow-base-shadow mt-0! h-full w-fit rounded-4xl object-contain shadow-lg"
						/>
					</a>
				</div>
				<div class="flex justify-between gap-4 py-4">
					<a
						class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
						href="https://www.youtube.com/@electriccircuitswithaltern7204"
					>
						<Icon icon="fa6-brands:youtube" /> YouTube
					</a>
					<a
						class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
						href="https://chatgpt.com/g/g-69774f07058c8191bd88f547d1c740c9-electric-circuits-with-alternating-currents"
					>
						<Icon icon="bi:openai" /> ChatGPT
					</a>
					<a
						class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
						href="https://gemini.google.com/gem/1j9s5Oe6boPCqdOAGOUMKZmFWr5O6cWuT?usp=sharing"
					>
						<Icon icon="codicon:google-gemini" /> Gemini
					</a>
				</div>
				<ul class="list-disc">
					<li>3 x laboratory group work</li>
					<li>~50 calculation exercises</li>
					<li>~30 knowledge checks (former exam)</li>
				</ul>
			</div>
		</div>
	</FramedSlide>
	<FramedSlide part="context" section="4th-semester" title="Course: 4th semester">
		<div class="grid grid-cols-2 gap-6">
			<div
				class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-6 shadow-inner"
			>
				<div class="text-center text-5xl font-bold">Outer Ecosystem</div>
				<ul class="list-disc">
					<li>introduction to<br />specialisation</li>
					<li>recommended / electable course</li>
					<li>online and physical</li>
					<li>remote participants</li>
					<li>~10 different study lines</li>
					<li>~100 participants</li>
					<li>closes to applications</li>
				</ul>
			</div>
			<div
				class="bg-primary fragment text-primary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-6 shadow-inner"
			>
				<div class="text-center text-5xl font-bold">Inner Ecosystem</div>

				<div class="flex justify-between gap-4 py-4">
					<div class="w-full">
						<iframe
							title="Basic Power Electronics slides"
							src="/teachingengagement/presentation-basic-power.pdf"
							class="shadow-base-shadow m-0! h-full w-full rounded-4xl object-contain shadow-lg"
						>
						</iframe>
					</div>
					<a
						href="https://www.amazon.com/Power-Electronics-Course-Ned-Mohan/dp/1118074807"
						target="_blank"
						rel="noopener noreferrer"
						class="h-full"
					>
						<img
							src="https://m.media-amazon.com/images/I/61+7f4Xr0DL._SY425_.jpg"
							alt="Power Electronics: A first course - book cover"
							class="shadow-base-shadow mt-0! h-full w-fit rounded-4xl object-contain shadow-lg"
						/>
					</a>
				</div>
				<div class="flex justify-between gap-4 py-4">
					<a
						class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
						href="https://www.youtube.com/@basicpowerelectronics3928"
					>
						<Icon icon="fa6-brands:youtube" /> YouTube
					</a>
					<a
						class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
						href="https://chatgpt.com/g/g-69776f22b96481918cfa94db0b1e1a7b-basic-power-electronics"
					>
						<Icon icon="bi:openai" /> ChatGPT
					</a>
					<a
						class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
						href="https://gemini.google.com/gem/18nuFlRpN0CqvK7etCPk8mS3qKdFFcfCk?usp=sharing"
					>
						<Icon icon="codicon:google-gemini" /> Gemini
					</a>
				</div>
				<ul class="list-disc">
					<li>6 x laboratory group work</li>
					<li>2 x industry guest lecture</li>
					<li>~30 calculation exercises</li>
					<li>~30 knowledge checks (former exam)</li>
				</ul>
			</div>
		</div>
	</FramedSlide>
	<FramedSlide part="context" section="master-level" title="Course: Master level">
		<div class="grid grid-cols-2 gap-6">
			<div
				class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-6 shadow-inner"
			>
				<div class="text-center text-5xl font-bold">Outer Ecosystem</div>
				<ul class="list-disc">
					<li>electable course</li>
					<li>
						high diversity
						<ul>
							<li>Danish / international</li>
							<li>Bachelor / Master</li>
							<li>Different backgrounds</li>
						</ul>
					</li>
					<li>remote participants</li>
					<li>~12 different study lines</li>
					<li>~100 participants</li>
					<li>close to industrial work experience</li>
				</ul>
			</div>
			<div
				class="bg-primary fragment text-primary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-6 shadow-inner"
			>
				<div class="text-center text-5xl font-bold">Inner Ecosystem</div>
				<div class="flex justify-between gap-4 py-4">
					<a
						class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
						href="https://www.youtube.com/@circuittechnologyandemc7315"
					>
						<Icon icon="fa6-brands:youtube" /> YouTube
					</a>
				</div>
				<ul class="list-disc">
					<li>3 teachers</li>
					<li>
						methods
						<ul>
							<li>lectures</li>
							<li>flipped classroom</li>
							<li>group work</li>
						</ul>
					</li>
					<li>4 x projects as group work</li>
					<li>4 x industry guest lecture</li>
				</ul>
			</div>
		</div>
	</FramedSlide>
	<FramedSlide part="context" section="complexity">
		<img
			src="https://www.businessillustrator.com/wp-content/uploads/2025/12/complexity-outside-linear-cube-cartoon_businessillustrator.com_1200px-600x314.png.webp"
			alt="Reality strikes back - cartoon"
			class="shadow-base-shadow h-fit w-3/5 self-center rounded-4xl shadow-lg"
		/>
		{#snippet footer()}
			Cartoon by
			<a href="mailto:Virpi@businessillustrator.com" class="link link-animated mt-30">
				📧 Virpi@businessillustrator.com
			</a><br />
			<a href="https://www.businessillustrator.com/blog" class="link link-animated">
				🌐 www.businessillustrator.com/blog
			</a>
		{/snippet}
	</FramedSlide>
	<FramedSlide>Allan Watts - Chinese Farmer? and/or Sir Francis Bacon</FramedSlide>
	<FramedSlide>
		<img
			src="/flower.jpg"
			alt="Flower"
			class="shadow-base-shadow h-fit w-3/4 self-center rounded-4xl shadow-lg"
		/>
	</FramedSlide>
	<FramedSlide part="inspiration">
		<Library />
	</FramedSlide>
	<FramedSlide>Motivation?</FramedSlide>
	<FramedSlide>
		<img
			src="/snow-lake.jpg"
			alt="Snow Lake"
			class="shadow-base-shadow h-fit w-3/4 self-center rounded-4xl shadow-lg"
		/>
	</FramedSlide>
	<FramedSlide part="implementation" title="Inner change">
		<div class="flex flex-wrap justify-center gap-8">
			<ChatBubble variant="secondary" tailAngle={100} tailLength={20} tailBase={10}>
				<div class="text-4xl font-bold">Trust based on<br />DTU's Honours Codex</div>
			</ChatBubble>
			<ChatBubble variant="secondary" tailAngle={130} tailLength={25} tailBase={10}>
				<div class="text-4xl font-bold">Everything is an invitation.</div>
			</ChatBubble>
			<ChatBubble variant="secondary" tailAngle={50} tailLength={20} tailBase={10}>
				<div class="text-4xl font-bold">Starting Lectures with <br />guided meditation</div>
			</ChatBubble>
			<div class="w-[300px]"></div>
			<ChatBubble variant="secondary" tailAngle={130} tailLength={20} tailBase={10}>
				<div class="text-4xl font-bold">No ambitions on <br />other peoples behalf!</div>
			</ChatBubble>
			<ChatBubble variant="secondary" tailAngle={160} tailLength={20} tailBase={10}>
				<div class="text-4xl font-bold">No "deadlines" ☠️<br />only "life lines" 🌱.</div>
			</ChatBubble>
			<div class="w-[300px]"></div>
			<ChatBubble variant="secondary" tailAngle={130} tailLength={20} tailBase={10}>
				<div class="text-4xl font-bold">You never disturb,<br />you always contribute.</div>
			</ChatBubble>
			<ChatBubble variant="secondary" tailAngle={305} tailLength={20} tailBase={10}>
				<div class="text-4xl font-bold">
					There's no way you can cheat<br />use, what's available to you.
				</div>
			</ChatBubble>
		</div>
	</FramedSlide>
	<FramedSlide part="implementation" section="practical" title="Outer change">
		<div class="mt-10 grid h-full grid-cols-2 gap-10">
			<div class="flex flex-col items-center gap-15">
				<button
					class="btn btn-xl btn-gradient btn-secondary h-30 w-150 justify-center rounded-full p-10 text-5xl font-semibold shadow-inner"
					onclick={() => hideAllToggleOne('reflections')}
				>
					Learning Reflections
				</button>
				<button
					class="btn btn-xl btn-gradient btn-secondary h-30 w-150 justify-center rounded-full p-10 text-5xl font-semibold shadow-inner"
					onclick={() => hideAllToggleOne('closedQuestions')}
				>
					Quantitative Questions
				</button>
				<button
					class="btn btn-xl btn-gradient btn-secondary h-30 w-150 justify-center rounded-full p-10 text-5xl font-semibold shadow-inner"
					onclick={() => hideAllToggleOne('openQuestions')}
				>
					Qualitative Questions
				</button>
			</div>
			<div class="flex flex-col items-center gap-10" bind:this={modulesContentColumn}>
				<CardOverlay
					class="bg-primary-container text-primary-container-content z-50 pt-6 text-4xl"
					bind:hidden={hideModules.reflections}
				>
					{#snippet header()}
						<div class="text-5xl font-bold">Learning Reflections</div>
					{/snippet}
					<dl>
						<dt>Course segementation</dt>
						<dd>4 Modules in each course</dd>
						<dd>~ 2 - 4 weeks per module</dd>
					</dl>
					<dl class="pt-5">
						<dt>Question</dt>
						<dd>What have you learned in the last module?</dd>
						<dd>only mandatory sharing from the students</dd>
					</dl>

					<dl class="pt-5">
						<dt>Implementation</dt>
						<dd>via Microsoft Forms</dd>
						<dd>logged in user transferred automatically</dd>
						<dd>multiple hand-ins possible</dd>
					</dl>
				</CardOverlay>
				<CardOverlay
					class="bg-primary-container text-primary-container-content z-50 pt-6 text-4xl"
					bind:hidden={hideModules.closedQuestions}
				>
					{#snippet header()}
						<div class="text-5xl font-bold">Quantitative Questions</div>
					{/snippet}
					<dl>
						<dt>Course segementation</dt>
						<dd>4 Modules in each course</dd>
						<dd>~ 2 - 4 weeks per module</dd>
					</dl>
					<dl class="pt-5">
						<dt>Question</dt>
						<dd>What have you learned in the last module?</dd>
						<dd>only mandatory sharing from the students</dd>
					</dl>

					<dl class="pt-5">
						<dt>Implementation</dt>
						<dd>via Microsoft Forms</dd>
						<dd>logged in user transferred automatically</dd>
						<dd>multiple hand-ins possible</dd>
					</dl>
				</CardOverlay>
				<CardOverlay
					class="bg-primary-container text-primary-container-content z-50 pt-6 text-4xl"
					bind:hidden={hideModules.openQuestions}
				>
					{#snippet header()}
						<div class="text-5xl font-bold">Qualitative Questions</div>
					{/snippet}
					<dl>
						<dt>Course segementation</dt>
						<dd>4 Modules in each course</dd>
						<dd>~ 2 - 4 weeks per module</dd>
					</dl>
					<dl class="pt-5">
						<dt>Question</dt>
						<dd>What have you learned in the last module?</dd>
						<dd>only mandatory sharing from the students</dd>
					</dl>

					<dl class="pt-5">
						<dt>Implementation</dt>
						<dd>via Microsoft Forms</dd>
						<dd>logged in user transferred automatically</dd>
						<dd>multiple hand-ins possible</dd>
					</dl>
				</CardOverlay>
			</div>
		</div>
	</FramedSlide>
	<FramedSlide>
		<img
			src="/besseggen.jpg"
			alt="Besseggen"
			class="shadow-base-shadow h-fit w-3/4 self-center rounded-4xl shadow-lg"
		/>
	</FramedSlide>
	<FramedSlide part="results">Overview of results? So far anchor page only</FramedSlide>
	<FramedSlide part="results" section="master-course">Results from 34654 - E25</FramedSlide>
	<FramedSlide part="results" section="quantitative">
		Quantitative results: learning, responsibility, meditation, sharing comments
	</FramedSlide>
	<FramedSlide part="results" section="qualitative">Qualitative results</FramedSlide>
	<FramedSlide part="results" section="qualitative">Emotional results</FramedSlide>
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
	<FramedSlide>
		<img
			src="/sunset-vejlesoen.jpg"
			alt="Sunset Vejlesøen"
			class="shadow-base-shadow h-fit w-3/4 self-center rounded-4xl shadow-lg"
		/>
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
