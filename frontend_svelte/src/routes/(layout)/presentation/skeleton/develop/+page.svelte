<script lang="ts">
	import type { RevealApi } from 'reveal.js';
	import { onDestroy, onMount } from 'svelte';
	import type { Attachment } from 'svelte/attachments';

	import ChatBubble from '$components/ChatBubble.svelte';
	import RevealJs from '$components/RevealJS.svelte';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended } from '$lib/types';

	import type { PageData } from './$types';
	import Badge from './Badge.svelte';
	import FramedSlide from './FramedSlide.svelte';
	import Map from './Map.svelte';
	import Question from './Question.svelte';

	let { data }: { data: PageData } = $props();

	let revealInstance = $state<RevealApi | undefined>(undefined);

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

	let mapQuestion = $derived(
		data.payload.questions.find((question) => question.question.includes('map'))
	);
	let socketioMap: SocketIO<MessageExtended> = $state()!;

	onMount(() => {
		socketioMap = new SocketIO<MessageExtended>(
			{
				namespace: '/message',
				parentId: mapQuestion?.id,
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
		socketioMap.createSortedSelection('sortedPlacesAnswers', 'creation_date', false);
	});

	$effect(() => {
		// Preseed data:
		// TBD: update to preseed with numbers coming from server-side via REST-API
		socketioMap.entities = mapQuestion?.messages ?? [];
	});

	onDestroy(() => {
		socketioMap?.client.disconnect();
	});

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

	$effect(() => {
		// revealInstance?.on('slidechanged', (event) => {
		// 	console.log('=== presentations - skeleton - develop - slide changed - event ===');
		// 	console.log(event);
		// });
		revealInstance?.on('fragmentshown', (_event) => {
			// console.log('=== presentations - skeleton - develop - fragment shown - event ===');
			// console.log(event);
		});
		revealInstance?.on('fragmenthidden', (_event) => {
			// console.log('=== presentations - skeleton - develop - fragment hidden - event ===');
			// console.log(event);
		});
	});

	let firstTextElement: HTMLElement | null = $state(null);
	let fifthTextElement: HTMLElement | null = $state(null);
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
		<div class="base-content-variant text-[200px] font-bold">Welcome</div>
	</section>
	<!-- <section>
		<div class="display text-primary pb-20 text-9xl font-bold">
			Title
			<br />
			More title
		</div>
		<div class="display text-secondary pb-10 font-semibold">Presenter: Name</div>
		<div class="display text-secondary pb-10 font-semibold">Place: Location</div>
		<div class="display-small text-secondary pb-10 font-semibold">Date: today!</div>
	</section> -->
	<section>
		<div
			class="r-stretch my-20 grid grid-cols-[1fr_max-content_1fr] items-center justify-between justify-items-start gap-12 text-7xl"
			// class="r-stretch mx-auto my-20 grid w-fit grid-cols-[auto_max-content_auto] items-center gap-12 text-7xl"
		>
			<span class="icon-[ic--round-question-mark] bg-secondary justify-self-end"></span>
			<Badge title="Question 1" color="secondary" />
			<div></div>
			<a href="#intro" class="justify-self-end" aria-label="Intro"
				><span class="icon-[stash--circle-dot] bg-primary"></span></a
			>
			<a href="#intro" aria-label="Context"
				><div class="text-primary font-bold">Introduction</div></a
			>
			<div></div>
			<a href="#main" aria-label="Main" class="justify-self-end"
				><span class="icon-[mingcute--lightning-fill] bg-primary"></span></a
			>
			<a href="#main" aria-label="Main"><div class="text-primary font-bold">Main Part</div></a>
			<div></div>
			<a href="#conclusion" aria-label="Conclusion" class="justify-self-end"
				><span class="icon-[f7--chat-bubble-2-fill] bg-primary"></span></a
			>
			<a href="#conclusion" aria-label="Conclusion"
				><div class="text-primary font-bold">Conclusion</div></a
			>
			<div></div>
			<span class="icon-[ic--round-question-mark] bg-secondary justify-self-end"></span>
			<Badge title="Questions 1 & 2" color="secondary" />
			<div></div>
		</div>
	</section>
	<section>
		<div class="r-stretch flex flex-col items-center justify-center">
			<Question title="Question 1" color="secondary">
				What are you <br />
				<span class="italic">interested</span> in today?
			</Question>
		</div>
	</section>
	<FramedSlide part="intro" color="primary">
		<ChatBubble variant="accent" tailAngle={130} shadow={true}>
			<div class="heading-large">Some introduction citation</div>
		</ChatBubble>
	</FramedSlide>
	<FramedSlide part="intro" section="sub-slide" color="primary">
		<div class="">Part of Introduction</div>
		<div class="">Content goes here</div>
	</FramedSlide>
	<FramedSlide part="main" color="primary">
		<div class="h-full">Content Main</div>
	</FramedSlide>
	<FramedSlide part="main" section="goals" color="primary">
		<div class="display">Adds toggle</div>

		<div bind:this={firstTextElement} id="goals-first-text" class="transition-all duration-3000">
			Some Text
		</div>
		<div
			class="fragment fade-in-then-out"
			{@attach toggleOnFragment(firstTextElement, 'text-error mr-100')}
		>
			<span
				class="fragment fade-out"
				{@attach toggleOnFragment(firstTextElement, 'text-success ml-200')}
			>
				Some more Text
			</span>
		</div>
		<div class="fragment fade-in">Another fragment</div>
		<div class="fragment fade-in">And one more fragment</div>
		<div bind:this={fifthTextElement} class="fragment fade-in">Fifth fragment</div>
		<div class="fragment fade-in" {@attach toggleOnFragment(fifthTextElement, 'text-7xl')}>
			<span
				class="fragment fade-out"
				{@attach toggleOnFragment(fifthTextElement, 'text-7xl', true)}
			>
				6th fragment
			</span>
		</div>
		<div class="fragment fade-in">7th fragment</div>
	</FramedSlide>
	<FramedSlide part="main" section="map" color="primary">
		{#if mapQuestion}
			<Map {revealInstance} socketio={socketioMap} />
		{:else}
			{@render interactiveElementNotAvailable('map')}
		{/if}
	</FramedSlide>
	<FramedSlide part="conclusion" color="primary">
		<div class="h-full">Content Conclusion</div>
	</FramedSlide>
	<section>
		<div class="r-stretch flex flex-col items-center justify-center gap-12">
			<Question title="Question 1" color="secondary">
				What are you <br />
				<span class="italic">interested</span> in today?
			</Question>
			<Question title="Question 2" color="secondary">
				What is your <span class="italic">best</span> <br />
				and your <span class="italic">worst</span> <br />
				takeaway from today?
			</Question>
		</div>
	</section>
	<section>
		<div class="flex items-center justify-center text-[200px] font-bold">
			<span class="icon-[ic--round-question-mark] rotate-180 transform"></span> Questions
			<span class="icon-[ic--round-question-mark]"></span>
		</div>
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
				<a href="#{returnToSlide}" class="link link-animated">{returnToSlide.replace('-', ' ')}</a>.
			</div>
		{/if}
	</FramedSlide>
</RevealJs>
