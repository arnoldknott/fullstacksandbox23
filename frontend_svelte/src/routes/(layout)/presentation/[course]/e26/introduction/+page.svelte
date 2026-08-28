<script lang="ts">
	import type { RevealApi } from 'reveal.js';
	import { onDestroy, onMount } from 'svelte';
	import { flip } from 'svelte/animate';
	import type { Attachment } from 'svelte/attachments';

	import { page } from '$app/state';
	import Card from '$components/Card.svelte';
	import ChatBubble from '$components/ChatBubble.svelte';
	import RevealJs from '$components/RevealJS.svelte';
	import { Action } from '$lib/accessHandler';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended, NumericalExtended } from '$lib/types';

	import type { PageData } from './$types';
	import Badge from './Badge.svelte';
	import CardOverlay from './CardOverlay.svelte';
	import FramedSlide from './FramedSlide.svelte';
	import Map from './Map.svelte';
	import MotivationTable from './MotivationTable.svelte';
	import Team from './Team.svelte';

	let { data }: { data: PageData } = $props();

	let preview = $derived(page.url.searchParams.get('preview') === 'true' ? true : false);

	let returnToSlide = $state<string | undefined>(undefined);

	$effect(() => {
		preview = page.url.searchParams.get('preview') === 'true';
	});

	let revealInstance = $state<RevealApi | undefined>(undefined);

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

	interface RevealFragmentEvent extends Event {
		fragment: HTMLElement;
		fragments: HTMLElement[];
	}

	/** Reveal.js adds `.fragment` and `.fragments` to the `fragmentshown` / `fragmenthidden` events. */
	type FragmentEvent = Event & { fragment?: HTMLElement; fragments?: HTMLElement[] };

	// TBD: move the logic into $lib/userInterface.svelte.ts
	// and import it here, so that it can be reused in other presentations
	/**
	 * Attachment for a Reveal.js fragment (the trigger). While that fragment is
	 * shown the given classes are added to the target element; when it is hidden
	 * they are removed again. The target is resolved from a CSS selector, so no
	 * `bind:this` on the target is required.
	 *
	 * Usage:
	 * ```svelte
	 * <div id="goal" class="transition-all duration-1000">Some Text</div>
	 * <div class="fragment fade-in" {@attach toggleOnFragment(reveal, '#goal', 'text-error', 'mr-100')}>
	 *   Some more Text
	 * </div>
	 * ```
	 */
	const toggleOnFragment = (
		targetElement: HTMLElement,
		classes: string,
		invert = false
	): Attachment<HTMLElement> => {
		return (node) => {
			const show = (event: FragmentEvent) => {
				if (event.fragment === node) targetElement?.classList.add(...classes.split(' '));
			};
			const hide = (event: FragmentEvent) => {
				if (event.fragment === node) targetElement?.classList.remove(...classes.split(' '));
			};

			revealInstance?.on(
				'fragmentshown',
				!invert ? (show as EventListener) : (hide as EventListener)
			);
			revealInstance?.on(
				'fragmenthidden',
				!invert ? (hide as EventListener) : (show as EventListener)
			);

			return () => {
				revealInstance?.off(
					'fragmentshown',
					!invert ? (show as EventListener) : (hide as EventListener)
				);
				revealInstance?.off(
					'fragmenthidden',
					!invert ? (hide as EventListener) : (show as EventListener)
				);
			};
		};
	};

	// const hideAllModulesOnFramework = (): Attachment<HTMLElement> => {
	// 	return (node) => {
	// 		const currentHiddenModules = hideModules;
	// 		revealInstance?.on('fragmentshown', (event: FragmentEvent) => {
	// 			if (event.fragment === node) {
	// 				hideModules = {
	// 					passives: true,
	// 					emc: true,
	// 					pcb: true,
	// 					environment: true
	// 				};
	// 			}
	// 		});
	// 		revealInstance?.on('fragmenthidden', (event: FragmentEvent) => {
	// 			if (event.fragment === node) {
	// 				hideModules = currentHiddenModules;
	// 			}
	// 		});

	// 		return () => {
	// 			hideModules = currentHiddenModules;
	// 		};
	// 	};
	// };

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

	let modulesContentColumn: HTMLDivElement | undefined = $state();
	let frameworkColumn: HTMLDivElement | undefined = $state();
	let roomColumn: HTMLDivElement | undefined = $state();
	let roomImageFlipped = $state(false);

	let hideModules = $state({
		passives: true,
		emc: true,
		pcb: true,
		environment: true
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

	let commentsAnswersSorted = $derived(
		socketioComments?.getSelectedEntities('sortedCommentsAnswers') ?? []
	);
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
				: { background: '', text: 'var(--color-base-content)' }}
		>
			{#if motivationQuestion}
				<MotivationTable
					questionId={motivationQuestion?.id}
					socketio={socketioMotivation}
					averageMotivation={motivationAnswersAverage}
					bind:averageColors={averageMotivationColors}
				/>
			{:else}
				{@render interactiveElementNotAvailable('motivation table')}
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
			<div class="absolute top-40 left-30">
				<ChatBubble variant="secondary" tailAngle={50} shadow={true}>
					<div class="heading-large">12 different study lines</div>
				</ChatBubble>
			</div>
			<div class="absolute top-60 right-5">
				<ChatBubble variant="secondary" tailAngle={120} shadow={true}>
					<div class="heading-large">Various different universities</div>
				</ChatBubble>
			</div>
			<div class="absolute top-120 left-0">
				<ChatBubble variant="secondary" tailAngle={30} shadow={true}>
					<div class="heading-large">With and without Printed Circuit Board (PCB) experience</div>
				</ChatBubble>
			</div>
			<div class="absolute top-170 right-0 w-200">
				<ChatBubble variant="secondary" tailAngle={280} shadow={true}>
					<div class="heading-large">All of you are welcome! 🫶</div>
				</ChatBubble>
			</div>
		</FramedSlide>
		<FramedSlide part="diversity" section="map" color="primary">
			{#if placesQuestion}
				<Map {revealInstance} socketio={socketioPlaces} />
			{:else}
				{@render interactiveElementNotAvailable('map')}
			{/if}
		</FramedSlide>
		<FramedSlide part="overview" color="primary">
			<Team />
		</FramedSlide>
		<FramedSlide part="overview" section="content" color="primary">
			<div class="grid grid-cols-2 gap-10">
				<div class="flex flex-col gap-10">
					<div class="text-secondary absolute top-2/12 left-70 -mt-10 text-7xl font-bold">
						Modules
					</div>
					<button
						class="btn btn-xl btn-gradient btn-secondary absolute top-3/12 left-30 h-30 w-150 justify-center rounded-full p-10 text-5xl font-semibold shadow-inner"
						onclick={() => hideAllToggleOne('passives')}
					>
						Passives
					</button>
					<button
						class="btn btn-xl btn-gradient btn-secondary absolute top-5/12 left-30 h-30 w-150 justify-center rounded-full p-10 text-5xl font-semibold shadow-inner"
						onclick={() => hideAllToggleOne('emc')}
					>
						Electromagnetic Compatibility
					</button>
					<button
						class="btn btn-xl btn-gradient btn-secondary absolute top-7/12 left-30 h-30 w-150 justify-center rounded-full p-10 text-5xl font-semibold shadow-inner"
						onclick={() => hideAllToggleOne('pcb')}
					>
						Printed Circuit Boards
					</button>
					<button
						class="btn btn-xl btn-gradient btn-secondary absolute top-9/12 left-30 h-30 w-150 justify-center rounded-full p-10 text-5xl font-semibold shadow-inner"
						onclick={() => hideAllToggleOne('environment')}
					>
						Environment
					</button>
					<!-- <NodeButton
						class="btn-secondary top-3/12 left-30 h-30 w-150 rounded-full"
						bind:toggleVariable={hideModules.passives}
						aria-label="Modules"
						>Passives
					</NodeButton> -->
					<!-- <NodeOverlay
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
					</NodeOverlay> -->
					<!-- <NodeOverlay
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
					</NodeOverlay> -->
					<!-- <NodeOverlay
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
					</NodeOverlay> -->
				</div>
				<div>
					<div class="flex flex-col items-center gap-10" bind:this={modulesContentColumn}>
						<CardOverlay
							class="bg-secondary-container text-secondary-container-content z-50 pt-6 text-4xl"
							bind:hidden={hideModules.passives}
						>
							{#snippet header()}
								<div class="text-5xl font-bold">Passives</div>
							{/snippet}
							<dl>
								<dt>Content</dt>
								<dd>Resisters, Capacitors, and Inductors</dd>
							</dl>
							<div class="grid grid-cols-6 gap-2">
								<div class="col-span-3 text-left">
									<dl class="pt-5">
										<dt>Activities</dt>
										<dd>Lecture</dd>
										<dd>Simulation <br />& hands-on</dd>
									</dl>
									<dl class="pt-5">
										<dt>Timeframe</dt>
										<dd>Week 1 & 2</dd>
									</dl>
								</div>
								<img
									src="/flower.jpg"
									alt="flower"
									class="col-span-3 self-center mask-y-from-75% mask-y-to-100% mask-x-from-85% mask-x-to-100% object-cover opacity-70"
								/>
							</div>
						</CardOverlay>
						<CardOverlay
							class="bg-secondary-container text-secondary-container-content z-50 pt-6 text-4xl"
							bind:hidden={hideModules.emc}
						>
							{#snippet header()}
								<div class="text-5xl font-bold">Electromagnetic Compatibility</div>
							{/snippet}
							<dl>
								<dt>Content</dt>
								<dd>Introduction & test setups</dd>
								<dd>Physical phenomena & examples</dd>
								<dd>Industrial examples</dd>
								<dd>Standardization</dd>
							</dl>
							<div class="grid grid-cols-6 gap-2">
								<div class="col-span-3 text-left">
									<dl class="pt-5">
										<dt>Activities</dt>
										<dd>Flipped classroom</dd>
										<dd>Guest lectures</dd>
										<dd>Analysis, design, implementation, and experimental verification</dd>
									</dl>
									<dl class="pt-5">
										<dt>Timeframe</dt>
										<dd>Week 3 - 6</dd>
									</dl>
								</div>
								<img
									src="/snow-lake.jpg"
									alt="snow lake"
									class="col-span-3 self-end mask-y-from-75% mask-y-to-100% mask-x-from-85% mask-x-to-100% object-cover opacity-70"
								/>
							</div>
						</CardOverlay>
						<CardOverlay
							class="bg-secondary-container text-secondary-container-content z-50 pt-6 text-4xl"
							bind:hidden={hideModules.pcb}
						>
							{#snippet header()}
								<div class="text-5xl font-bold">Printed Circuit Boards</div>
							{/snippet}
							<div class="grid grid-cols-6 gap-2">
								<div class="col-span-3 text-left">
									<dl>
										<dt>Content</dt>
										<dd>Design workflow</dd>
										<dd>Computer Aided Design</dd>
										<dd>Implementation</dd>
										<dd>Design review</dd>
										<dd>Finish design</dd>
									</dl>
								</div>
								<img
									src="/besseggen.jpg"
									alt="Besseggen"
									class="col-span-3 self-end mask-y-from-75% mask-y-to-100% mask-x-from-85% mask-x-to-100% object-cover opacity-70"
								/>
							</div>
							<dl class="pt-5">
								<dt>Activities</dt>
								<dd>Lecture & Guest lecture</dd>
								<dd>Design, implementation, and-over, design review, and finalization</dd>
							</dl>
							<dl class="pt-5">
								<dt>Timeframe</dt>
								<dd>Week 7 - 11</dd>
							</dl>
						</CardOverlay>
						<CardOverlay
							class="bg-secondary-container text-secondary-container-content z-50 pt-6 text-4xl"
							bind:hidden={hideModules.environment}
						>
							{#snippet header()}
								<div class="text-5xl font-bold">Environment</div>
							{/snippet}
							<dl>
								<dt>Content</dt>
								<dd>Thermal impact</dd>
								<dd>Radiation from space</dd>
							</dl>
							<div class="grid grid-cols-6 gap-2">
								<div class="col-span-2 text-left">
									<dl class="pt-5">
										<dt>Activities</dt>
										<dd>Lecture</dd>
										<dd>Guest lecture</dd>
										<dd>Hands-on</dd>
									</dl>
									<dl class="pt-5">
										<dt>Timeframe</dt>
										<dd>Week 12 & 13</dd>
									</dl>
								</div>
								<img
									src="/sunset-vejlesoen.jpg"
									alt="Sunset Vejlesøen"
									class="col-span-4 self-end mask-y-from-75% mask-y-to-100% mask-x-from-85% mask-x-to-100% object-cover opacity-70"
								/>
							</div>
						</CardOverlay>
					</div>
					<div
						bind:this={frameworkColumn}
						class="fragment fade-in flex hidden flex-col gap-10"
						{@attach toggleOnFragment(modulesContentColumn, 'hidden')}
						{@attach toggleOnFragment(frameworkColumn!, 'hidden', true)}
					>
						<div class="text-secondary absolute top-2/12 right-70 -mt-10 text-7xl font-bold">
							Assessment
						</div>
						<!-- <Card
							id="activities"
							extraClasses="bg-secondary-container bg- text-secondary-container-content text-4xl mt-10"
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
						</Card> -->
						<Card
							id="assessment"
							extraClasses="bg-secondary-container text-secondary-container-content text-4xl mt-10"
						>
							<div class="grid grid-cols-6 gap-2">
								<div class="col-span-4 text-left">
									<dl>
										<dt>Grading</dt>
										<dd>Pass / Fail</dd>
									</dl>
									<dl class="pt-5">
										<dt>Learning Reflections</dt>
										<dd>
											Per module, we ask you <b>one</b> mandatory question via Microsoft Forms:
											<i>"What have you learned ...?"</i>
										</dd>
										<dd>
											Hand in 3 out of those 4 learning reflections to pass. As long as your answer
											is addressing the module, we accept it.
										</dd>
									</dl>
								</div>
								<img
									src="/bonfire.jpg"
									alt="bonfire"
									class="col-span-2 h-fit self-center mask-y-from-75% mask-y-to-100% mask-x-from-85% mask-x-to-100% object-cover opacity-70"
								/>
							</div>
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
					<div
						bind:this={roomColumn}
						class="fragment fade-in flex hidden flex-col gap-10"
						{@attach toggleOnFragment(frameworkColumn, 'hidden')}
						{@attach toggleOnFragment(roomColumn!, 'hidden', true)}
					>
						<div class="text-secondary absolute top-2/12 right-70 -mt-10 text-7xl font-bold">
							Room
						</div>
						<!-- <Card
							id="activities"
							extraClasses="bg-secondary-container bg- text-secondary-container-content text-4xl mt-10"
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
						</Card> -->
						<Card
							id="room"
							extraClasses="bg-secondary-container text-secondary-container-content text-4xl mt-10"
						>
							<div class="text-5xl font-semibold">building 329A, room 020</div>
							<div class="relative h-[500px] w-[730px]" style="perspective: 1800px;">
								<button
									type="button"
									class="absolute inset-0 block cursor-pointer rounded-4xl"
									onclick={() => {
										roomImageFlipped = !roomImageFlipped;
									}}
									aria-pressed={roomImageFlipped}
									aria-label={roomImageFlipped
										? 'Show room teaching image'
										: 'Show room experimental image'}
								>
									<div
										class="relative h-full w-full rounded-4xl text-center transition-transform duration-700 ease-in-out [transform-style:preserve-3d]"
										class:[transform:rotateY(180deg)]={roomImageFlipped}
									>
										<img
											src="/room-teaching.jpg"
											alt="Room Teaching"
											class="shadow-secondary absolute inset-0 h-full w-full rounded-4xl object-cover shadow-lg [backface-visibility:hidden]"
										/>
										<img
											src="/room-experimental.jpg"
											alt="Room Experimental"
											class="shadow-secondary absolute inset-0 h-full w-full [transform:rotateY(180deg)] rounded-4xl object-cover shadow-lg [backface-visibility:hidden]"
										/>
									</div>
								</button>
							</div>
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
				</div>
			</div>
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
		<section id="comments-and-questions">
			{#if commentsQuestion}
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
										socketioComments.addPendingAccessPolicy(
											socketioComments.pendingEntities[0].id,
											{
												public: true,
												action: Action.READ
											}
										);
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
				<div class="col-span-12 mr-20 text-right text-xl">
					By entering your text here, you agree to the <a
						href="#terms-and-conditions"
						class="link link-animated">terms and conditions</a
					>.
				</div>
			{:else}
				{@render interactiveElementNotAvailable('comments and questions dialog')}
			{/if}
		</section>

		<section>
			<div class="text-base-content-variant text-[200px] font-bold">Thank you! 🙏</div>
		</section>
		<FramedSlide part="terms-and-conditions" color="secondary">
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
					In case you want any of your data deleted, please send a screenshot of you want to have
					deleted to Arnold.
				</dd>
			</dl>
			{#if returnToSlide}
				<div>
					<span class="icon-[fa-regular--hand-point-right] mr-4 size-7"></span>Back to
					<a href="#{returnToSlide}" class="link link-animated">{returnToSlide.replace('-', ' ')}</a
					>.
				</div>
			{/if}
		</FramedSlide>
	{/if}
</RevealJs>
