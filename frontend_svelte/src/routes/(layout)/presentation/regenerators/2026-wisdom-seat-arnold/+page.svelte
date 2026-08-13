<script lang="ts">
	import type { RevealApi } from 'reveal.js';
	import type { Attachment } from 'svelte/attachments';

	import ChatBubble from '$components/ChatBubble.svelte';
	import RevealJs from '$components/RevealJS.svelte';

	// import { initOverlay } from '$lib/userInterface';
	import Badge from './Badge.svelte';
	import CardOverlay from './CardOverlay.svelte';
	import FeedbackCaroussel from './FeedbackCaroussel.svelte';
	// import DivergingStackedChart from './DivergingStackedChart.svelte';
	import FramedSlide from './FramedSlide.svelte';
	import MotivationTable from './MotivationTable.svelte';
	import NodeOverlay from './NodeOverlay.svelte';
	import Question from './Question.svelte';
	import Tension from './Tension.svelte';

	let revealInstance = $state<RevealApi | undefined>(undefined);

	/** Reveal.js adds `.fragment` and `.fragments` to the `fragmentshown` / `fragmenthidden` events. */
	type FragmentEvent = Event & { fragment?: HTMLElement; fragments?: HTMLElement[] };

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
		// targetSelector: string,
		targetElement: HTMLElement,
		classes: string,
		invert = false
	): Attachment<HTMLElement> => {
		return (node) => {
			// const target = (): HTMLElement | null =>
			// 	node.closest('.reveal')?.querySelector<HTMLElement>(targetSelector) ??
			// 	document.querySelector<HTMLElement>(targetSelector);

			const show = (event: FragmentEvent) => {
				// if (event.fragment === node) target()?.classList.add(...classes);
				if (event.fragment === node) targetElement?.classList.add(...classes.split(' '));
			};
			const hide = (event: FragmentEvent) => {
				// if (event.fragment === node) target()?.classList.remove(...classes);
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

	// $effect(() => {
	// 	// revealInstance?.on('slidechanged', (event) => {
	// 	// 	console.log('=== presentations - regenerators - wisdom seat - slide changed - event ===');
	// 	// 	console.log(event);
	// 	// });
	// 	revealInstance?.on('fragmentshown', (event) => {
	// 		console.log('=== presentations - regenerators - wisdom seat - fragment shown - event ===');
	// 		console.log(event);
	// 		// firstTextElement?.classList.add('text-error', 'mr-100');
	// 		// if (firstTextElement && event.fragment === ) {
	// 		// 	firstTextElement.classList.add('text-error');
	// 		// }
	// 	});
	// 	revealInstance?.on('fragmenthidden', (event) => {
	// 		console.log('=== presentations - regenerators - wisdom seat - fragment hidden - event ===');
	// 		console.log(event);
	// 		// firstTextElement?.classList.remove('text-error', 'mr-100');
	// 		// if (firstTextElement && event.fragment === ) {
	// 		// 	firstTextElement.classList.add('text-error');
	// 		// }
	// 	});
	// });

	let ecoSystemMapContext: HTMLElement | null = $state(null);
	let roomImageFlipped = $state(false);
	let hideMeditation = $state(true);
	let hideInvitation = $state(true);
	let hideMotivation = $state(true);
	let hideDeadlines = $state(true);
	let hideStartUps = $state(true);
	let hideConstruction = $state(true);
	let hideResources = $state(true);
	let dnaWheel: HTMLElement | null = $state(null);

	// const categoriesMeditation: [string, string, string] = ['yes', 'maybe', 'no'];

	// const feedbackData = [
	// 	{
	// 		year: 2024,
	// 		course: '34654',
	// 		learnedMore: [4, 9, 33, 11, 9],
	// 		takeMoreResponsibility: [1, 7, 13, 28, 17],
	// 		moreMotivated: [4, 15, 16, 18, 13],
	// 		moreMeditation: [0, 0, 0]
	// 	},
	// 	{
	// 		year: 2025,
	// 		course: '34601',
	// 		learnedMore: [5, 29, 45, 22, 8],
	// 		takeMoreResponsibility: [3, 23, 37, 30, 15],
	// 		moreMotivated: [7, 28, 37, 23, 14]
	// 	},
	// 	{
	// 		year: 2025,
	// 		course: '34620',
	// 		learnedMore: [7, 37, 58, 26, 9],
	// 		takeMoreResponsibility: [6, 24, 34, 52, 21],
	// 		moreMotivated: [7, 31, 46, 38, 14]
	// 	},
	// 	{
	// 		year: 2025,
	// 		course: '34654',
	// 		learnedMore: [1, 6, 28, 13, 9],
	// 		takeMoreResponsibility: [1, 4, 17, 22, 13],
	// 		moreMotivated: [2, 10, 18, 19, 8],
	// 		moreMeditation: [31, 0, 18]
	// 	},
	// 	{
	// 		year: 2026,
	// 		course: '34601',
	// 		// learnedMore:
	// 		// takeMoreResponsibility:
	// 		// moreMotivated:
	// 		moreMeditation: [46, 28, 24]
	// 	},
	// 	{
	// 		year: 2026,
	// 		course: '34620',
	// 		// learnedMore: ,
	// 		// takeMoreResponsibility: ,
	// 		// moreMotivated: ,
	// 		moreMeditation: [57, 41, 25]
	// 	}
	// ];

	// const moreMeditationData = feedbackData
	// 	.map((entry) => {
	// 		if (entry.moreMeditation) {
	// 			return {
	// 				year: entry.year,
	// 				course: entry.course,
	// 				values: entry.moreMeditation
	// 			};
	// 		}
	// 	})
	// 	.filter((entry) => entry !== undefined);

	// const sentimentColors = {
	// 	yes: 'bg-success',
	// 	maybe: 'bg-warning',
	// 	no: 'bg-error'
	// };

	let ecoSystemMapStories: HTMLElement | null = $state(null);
</script>

<RevealJs bind:reveal={revealInstance}>
	<section>
		<div class="text-[200px] font-bold">Welcome</div>
	</section>
	<!-- <section>
		<div class="display text-primary pb-20 text-9xl font-bold">
			Wisdom Seat
			<br />
			Teaching Engagement without Exams
		</div>
		<div class="display text-secondary pb-10 font-semibold">Presenter: Arnold Knott</div>
		<div class="display text-secondary pb-10 font-semibold">Facilitator: Pukhraj Ranjan</div>
		<div class="display-small text-secondary pb-10 font-semibold">2026-08-13</div>
	</section> -->
	<section>
		<div
			class="r-stretch my-20 grid grid-cols-[1fr_max-content_1fr] items-center justify-between justify-items-start gap-12 text-7xl"
			// class="r-stretch mx-auto my-20 grid w-fit grid-cols-[auto_max-content_auto] items-center gap-12 text-7xl"
		>
			<span class="icon-[ic--round-question-mark] bg-secondary justify-self-end"></span>
			<Badge title="Question 1" color="secondary" />
			<div></div>
			<a href="#context" class="justify-self-end" aria-label="Context"
				><span class="icon-[stash--circle-dot] bg-primary"></span></a
			>
			<a href="#context" aria-label="Context"><div class="text-primary font-bold">Context</div></a>
			<div></div>
			<a href="#tension" aria-label="Tension" class="justify-self-end"
				><span class="icon-[mingcute--lightning-fill] bg-primary"></span></a
			>
			<a href="#tension" aria-label="Tension"><div class="text-primary font-bold">Tension</div></a>
			<div></div>
			<a href="#stories" aria-label="Stories" class="justify-self-end"
				><span class="icon-[f7--chat-bubble-2-fill] bg-primary"></span></a
			>
			<a href="#stories" aria-label="Stories"><div class="text-primary font-bold">Stories</div></a>
			<div></div>
			<span class="icon-[ic--round-question-mark] bg-secondary justify-self-end"></span>
			<Badge title="Questions 1 & 2" color="secondary" />
			<div></div>
		</div>
	</section>
	<section>
		<div class="r-stretch flex flex-col items-center justify-center">
			<Question title="Question 1" color="secondary">
				What are you hearing,<br /> sensing, feeling, observing, <br /> that I have
				<span class="italic">not</span> said or shown?
			</Question>
		</div>
	</section>
	<FramedSlide part="context" color="primary">
		<img
			bind:this={ecoSystemMapContext}
			src="/regenerators/2026-wisdom-seat-arnold/eco-system-mapping.jpg"
			alt="Eco System Mapping"
			class="shadow-primary absolute h-fit w-fit rounded-4xl object-contain shadow-lg"
		/>
		<div
			class="fragment fade-in static"
			{@attach toggleOnFragment(ecoSystemMapContext, 'opacity-30')}
		>
			{#snippet leadershipTitle()}Leadership{/snippet}
			<NodeOverlay
				buttonText={leadershipTitle}
				buttonExtraClasses="btn-secondary top-1/10 right-3/10 -mt-5 mr-30"
				cardExtraClasses="bg-secondary-container text-secondary-container-content"
			>
				<div class="flex flex-col gap-8 p-8 px-16 text-5xl">
					<p class="col-span-3 font-semibold">Conversation with Dean in 2024</p>
					<ChatBubble variant="secondary" tailAngle={140} shadow={true}>
						<div class="text-5xl">Let's get rid of exams!</div>
					</ChatBubble>
					<div class="text-right">
						<ChatBubble variant="secondary" tailAngle={30} shadow={true}>
							<div class="text-5xl">Ok! <br /> Let's do it!</div>
						</ChatBubble>
					</div>
				</div>
			</NodeOverlay>
			{#snippet roomTitle()}Room{/snippet}
			<NodeOverlay
				buttonText={roomTitle}
				buttonExtraClasses="btn-secondary top-2/10 right-3/10"
				cardExtraClasses="bg-secondary-container text-secondary-container-content"
			>
				<p class=" text-5xl font-semibold">Facilites</p>
				<div class=" relative -mt-8 h-[600px] w-[800px]" style="perspective: 1800px;">
					<button
						type="button"
						class="absolute inset-0 block cursor-pointer rounded-4xl text-left"
						onclick={() => {
							roomImageFlipped = !roomImageFlipped;
						}}
						aria-pressed={roomImageFlipped}
						aria-label={roomImageFlipped
							? 'Show room teaching image'
							: 'Show room experimental image'}
					>
						<div
							class="relative h-full w-full rounded-4xl transition-transform duration-700 ease-in-out [transform-style:preserve-3d]"
							class:[transform:rotateY(180deg)]={roomImageFlipped}
						>
							<img
								src="/regenerators/2026-wisdom-seat-arnold/room-teaching.jpg"
								alt="Room Teaching"
								class="shadow-secondary absolute inset-0 h-full w-full rounded-4xl object-cover shadow-lg [backface-visibility:hidden]"
							/>
							<img
								src="/regenerators/2026-wisdom-seat-arnold/room-experimental.jpg"
								alt="Room Experimental"
								class="shadow-secondary absolute inset-0 h-full w-full [transform:rotateY(180deg)] rounded-4xl object-cover shadow-lg [backface-visibility:hidden]"
							/>
						</div>
					</button>
				</div>
			</NodeOverlay>
			{#snippet participantsTitle()}Participants{/snippet}
			<NodeOverlay
				buttonText={participantsTitle}
				buttonExtraClasses="btn-warning top-2/10 right-5/10"
				cardExtraClasses="bg-warning-container text-warning-container-content"
			>
				<div class="grid grid-cols-3 gap-4 text-5xl">
					<p class="col-span-3 font-semibold">Students</p>
					<div
						class="bg-warning text-warning-content col-span-3 flex flex-col gap-4 rounded-2xl p-4 shadow-md"
					>
						<p>from ~10 study lines</p>
						<p>predominately male</p>
						<p>ambitious, competitive, playful, helpful, "safe-the-world-attitude"</p>
					</div>
					<div
						class="bg-warning text-warning-content flex flex-col gap-4 rounded-2xl p-4 shadow-md"
					>
						<p>mostly Danish</p>
					</div>
					<div
						class="bg-warning text-warning-content flex flex-col gap-4 rounded-2xl p-4 shadow-md"
					>
						<p>Danish / international</p>
					</div>
					<div
						class="bg-warning text-warning-content flex flex-col gap-4 rounded-2xl p-4 shadow-md"
					>
						<p>mostly international</p>
					</div>
				</div>
			</NodeOverlay>
			<!-- <NodeButton class="btn-info-container top-4/10 right-6/10 -my-10">other courses</NodeButton> -->
			{#snippet coursesTitle()}Courses{/snippet}
			<NodeOverlay
				buttonText={coursesTitle}
				buttonExtraClasses="btn-info top-4/10 right-4/10 mr-10"
				cardExtraClasses="bg-info-container text-info-container-content"
			>
				<div class="grid grid-cols-3 gap-4 text-5xl">
					<p class="col-span-3 font-semibold">
						3 Courses in Electrical Engineering <br /><span class="text-3xl"
							>at Technical University of Denmark</span
						>
					</p>
					<div class="bg-info text-info-content flex flex-col gap-2 rounded-2xl shadow-md">
						<p>undergraduate <br />Bachelor</p>
						<p>2nd semester</p>
						<p>mostly mandatory</p>
						<p>~120 participants</p>
					</div>
					<div class="bg-info text-info-content flex flex-col gap-2 rounded-2xl shadow-md">
						<p>undergraduate <br />Bachelor</p>
						<p>4th semester</p>
						<p>elective</p>
						<p>~100 participants</p>
					</div>
					<div class="bg-info text-info-content flex flex-col gap-2 rounded-2xl shadow-md">
						<p>graduate <br />Master</p>
						<p>6-8th semester</p>
						<p>elective</p>
						<p>~90 participants</p>
					</div>
				</div>
			</NodeOverlay>
		</div>
	</FramedSlide>
	<FramedSlide part="tension" color="primary">
		<Tension strategy initiatives leadership />
	</FramedSlide>
	<FramedSlide part="tension" section="initiatives" color="primary">
		<!-- {#snippet motivationTitle()}
			<ChatBubble variant="success" tailAngle={130} shadow={true}>
				<div class="heading-large">No ambitions on other peoples behalf!</div>
			</ChatBubble>{/snippet}
		<NodeOverlay -->
		<!-- 	buttonText={motivationTitle}
			defaultButton={false}
			buttonExtraClasses="btn-success top-1/10 right-3/10 -mt-5 mr-30"
			cardExtraClasses="bg-success-container text-success-container-content"
		>
			some content goes here
		</NodeOverlay> -->
		<Tension initiatives />

		<button onclick={() => (hideInvitation = !hideInvitation)} class="absolute top-0 right-6/10">
			<ChatBubble variant="success" tailAngle={130} shadow={true}>
				<div class="heading-large">Everything is an invitation.</div>
			</ChatBubble>
		</button>
		<button onclick={() => (hideMeditation = !hideMeditation)} class="absolute top-1/10 left-3/10">
			<ChatBubble variant="success" tailAngle={10} shadow={true}>
				<div class="heading-large">Starting Lectures with guided meditation</div>
			</ChatBubble>
		</button>
		<button onclick={() => (hideMotivation = !hideMotivation)} class="absolute top-4/10 right-0/10">
			<ChatBubble variant="success" tailAngle={30} shadow={true}>
				<div class="heading-large">No ambitions on other peoples behalf!</div>
			</ChatBubble>
		</button>
		<button onclick={() => (hideDeadlines = !hideDeadlines)} class="absolute top-7/10 right-1/10">
			<ChatBubble variant="success" tailAngle={190} shadow={true}>
				<div class="heading-large">No "deadlines" ☠️ only "life lines" 🌱.</div>
			</ChatBubble>
		</button>
		<CardOverlay
			hidden={hideMeditation}
			class="bg-success-container text-success-container-content z-50 pt-6"
		>
			<p class=" text-7xl font-semibold">Would you like to have more meditations?</p>
			<p class=" text-5xl">(250 answers)</p>
			<!-- <div class="relative -mt-8 w-fit" style="perspective: 1800px;">
                    <button
                        type="button"
                        class="absolute inset-0 block cursor-pointer rounded-4xl text-left"
                        onclick={() => {
                            roomImageFlipped = !roomImageFlipped;
                        }}
                        aria-pressed={roomImageFlipped}
                        aria-label={roomImageFlipped
                            ? 'Show room teaching image'
                            : 'Show room experimental image'}
                    >
                        <div
                            class="relative h-full w-full rounded-4xl transition-transform duration-700 ease-in-out [transform-style:preserve-3d]"
                            class:[transform:rotateY(180deg)]={roomImageFlipped}
                        > -->
			<div class="grid grid-cols-2 gap-2">
				<img
					src="/regenerators/2026-wisdom-seat-arnold/more-meditations-2nd-semester.jpg"
					alt="More Meditation 2nd Semester"
					class="shadow-secondary h-fit w-fit rounded-4xl shadow-lg"
				/>
				<img
					src="/regenerators/2026-wisdom-seat-arnold/more-meditations-4th-semester.jpg"
					alt="Room Experimental"
					class="shadow-secondary h-fit w-fit rounded-4xl shadow-lg"
				/>
			</div>
			<!-- </div>
				</button>
			</div> -->
			<!-- <DivergingStackedChart
				data={moreMeditationData}
				categories={categoriesMeditation}
				colorClasses={sentimentColors}
				color="accent"
			/> -->
		</CardOverlay>
		<CardOverlay
			hidden={hideInvitation}
			class="bg-success-container text-success-container-content z-50 pt-6"
		>
			<div class="flex flex-col items-center justify-center">
				<p class=" text-7xl font-semibold">Course opening</p>
				<div class="flex flex-col gap-2 text-5xl">
					<img
						src="/regenerators/2026-wisdom-seat-arnold/invitation.jpg"
						alt="The Great Acceleration"
						class="shadow-error w-[900px] rounded-4xl shadow-lg"
					/>
				</div>
			</div>
		</CardOverlay>
		<CardOverlay
			hidden={hideMotivation}
			class="bg-success-container text-success-container-content z-50 pt-6"
		>
			<p class=" text-7xl font-semibold">📖 Self Determination Theory, Ib Ravn</p>
			<MotivationTable color="success" />
		</CardOverlay>
		<CardOverlay
			hidden={hideDeadlines}
			class="bg-success-container text-success-container-content z-50 pt-6"
		>
			<div class="flex flex-col items-center justify-center">
				<p class=" text-7xl font-semibold">Learning reflections:</p>
				<div class="flex flex-col gap-2 text-5xl">
					<p class="text-5xl">"What have you learned about ...?"</p>
					<p class="text-5xl">
						Plenty of open questions and votes about well-being, motivation, needs, feedback,
						discipline,,...
					</p>
				</div>
			</div></CardOverlay
		>
	</FramedSlide>
	<FramedSlide part="tension" section="strategy" color="primary">
		{#snippet footer()}
			<a
				href="https://www.dtu.dk/english/about/strategy-policy/strategy-2026-2031"
				class="link link-animated mt-30"
			>
				🌐 DTU Strategy 2026 - 2031
			</a>
		{/snippet}
		<Tension strategy />
		<div class="absolute grid grid-cols-2 items-center justify-center gap-2">
			<p class="text-warning-container-content col-span-2 text-7xl font-semibold">
				"Educating Europe´s most competent engineers..."
			</p>
			<ChatBubble variant="warning" tailAngle={10} shadow={true}>
				<div class="heading">"...experimenting with alternatives to traditional exam forms."</div>
			</ChatBubble>
			<ChatBubble variant="warning" tailAngle={130} shadow={true}>
				<div class="heading">"...learning innovation through hands-on business creation.""</div>
			</ChatBubble>
		</div>
	</FramedSlide>
	<FramedSlide part="tension" section="leadership" color="primary">
		<Tension leadership />
		<button onclick={() => (hideStartUps = !hideStartUps)} class="absolute top-1/10 left-5/10">
			<ChatBubble variant="error" tailAngle={10} shadow={true}>
				<div class="heading-large">
					Last year: 100 startup's <br /> 2026: 200 start-ups expected
				</div>
			</ChatBubble>
		</button>
		<button
			onclick={() => (hideConstruction = !hideConstruction)}
			class="absolute top-2/10 right-5/10"
		>
			<ChatBubble variant="error" tailAngle={130} shadow={true}>
				<div class="heading-large">
					"We are a rich university <br /> - our wealth is invested in bricks."
				</div>
			</ChatBubble>
		</button>
		<button onclick={() => (hideResources = !hideResources)} class="absolute top-7/10 left-2/10">
			<ChatBubble variant="error" tailAngle={330} shadow={true}>
				<div class="heading-large">Motivation of "no exams"</div>
			</ChatBubble>
		</button>
		<CardOverlay
			hidden={hideStartUps}
			class="bg-error-container text-error-container-content z-50 pt-6"
		>
			<div class="flex flex-col items-center justify-center">
				<p class=" text-7xl font-semibold">The Great Acceleration</p>
				<img
					src="/regenerators/2026-wisdom-seat-arnold/the-great-acceleration.jpg"
					alt="The Great Acceleration"
					class="shadow-error h-fit w-fit rounded-4xl shadow-lg"
				/>
			</div>
		</CardOverlay>
		<CardOverlay
			hidden={hideConstruction}
			class="bg-error-container text-error-container-content z-50 pt-6"
		>
			<div class="flex flex-col items-center justify-center">
				<p class=" text-7xl font-semibold">Constructions</p>
				<p class="text-5xl">Campus is 3rd biggest construction site in country</p>
				<p class="text-5xl">23 construction projects ongoing</p>
				<img
					src="/regenerators/2026-wisdom-seat-arnold/construction.jpg"
					alt="Constructions"
					class="shadow-error w-[500px] rounded-4xl shadow-lg"
				/>
			</div>
		</CardOverlay>
		<CardOverlay
			hidden={hideResources}
			class="bg-error-container text-error-container-content z-50 pt-6"
		>
			<p class=" text-7xl font-semibold">No exam</p>
			<div class="flex flex-col gap-2 text-5xl">
				<p>to safe resources</p>
				<p>to prevent students from cheating with Artificial Intelligence</p>
			</div>
		</CardOverlay>
	</FramedSlide>
	<!-- <FramedSlide part="tension" section="strategy" color="primary">content here</FramedSlide>
	<FramedSlide part="tension" section="leadership" color="primary">content here</FramedSlide> -->
	<FramedSlide part="tension" section="dna-wheel" color="primary">
		{#snippet footer()}
			<div>📖 G. Hutchins & L. Storm: Regenerative Leadership</div>
		{/snippet}
		<img
			bind:this={dnaWheel}
			src="/regenerators/2026-wisdom-seat-arnold/dna-wheel.jpg"
			alt="Eco System Mapping"
			class="shadow-primary absolute h-[80%] w-fit rounded-4xl object-contain shadow-lg"
		/>
	</FramedSlide>
	<!-- <FramedSlide part="tension" section="different-teaching" color="primary">
		<ChatBubble variant="secondary" tailAngle={190} shadow={true}>
			<div class="heading-large">No "deadlines" ☠️, <br /> only "life lines" 🌱.</div>
		</ChatBubble>
	</FramedSlide> -->
	<FramedSlide part="stories" color="primary">
		<!-- <div class="relative flex h-full w-full items-center justify-center"> -->
		<img
			bind:this={ecoSystemMapStories}
			src="/regenerators/2026-wisdom-seat-arnold/eco-system-mapping.jpg"
			alt="Eco System Mapping"
			class="shadow-primary absolute h-fit w-fit rounded-4xl object-contain shadow-lg"
		/>
		<div
			// class="fragment fade-in static"
			{@attach toggleOnFragment(ecoSystemMapStories, 'opacity-30')}
		>
			<!-- <NodeButton class="btn-info-container top-4/10 right-6/10 -my-10">other courses</NodeButton> -->
			{#snippet coursesTitle()}Courses{/snippet}
			<NodeOverlay
				buttonText={coursesTitle}
				buttonExtraClasses="btn-info top-4/10 right-4/10 mr-10"
				cardExtraClasses="bg-info-container text-info-container-content"
			>
				<p class="text-7xl font-semibold">
					500+ students have participated <br /> in "no exam" courses
				</p>
				<p class="text-5xl">
					<span class="icon-[tabler--plus] align-center"> </span> Significantly reduced stress<br />
					<span class="text-3xl">about 2/3 report lower stress in open-ended questions</span>
				</p>
				<p class="text-5xl">
					<span class="icon-[tabler--plus] align-center"> </span> Deeper learning
				</p>
				<p class="text-5xl">
					<span class="icon-[tabler--plus] align-center"> </span> More responsibility
				</p>
				<p class="text-5xl">
					<span class="icon-[tabler--minus] align-center"> </span> Focus goes, where the pressure is:
					other courses
				</p>
			</NodeOverlay>
			{#snippet colleaguesTitle()}Colleagues{/snippet}
			<NodeOverlay
				buttonText={colleaguesTitle}
				buttonExtraClasses="btn-success top-3/10 right-2/10 mt-5 mr-8"
				cardExtraClasses="bg-success-container text-success-container-content"
			>
				<p class="text-7xl">One colleague went to press:</p>
				<p class="text-5xl">"University drops exams"</p>
				<p class="text-5xl">judges teaching material:</p>
				<p class="text-5xl">"bad videos"</p>
				<p class="text-5xl">"incomprehensible exercise"</p>
				<div class="align-right text-3xl">🗞️ Ingeniøren: DTU drops exams</div>
			</NodeOverlay>
			{#snippet feedbackTitle()}Feedback{/snippet}
			<NodeOverlay
				buttonText={feedbackTitle}
				buttonExtraClasses="btn-neutral top-8/10 right-3/10 mt-5 mr-20"
				cardExtraClasses="bg-neutral-container text-neutral-container-content"
			>
				<p class="text-7xl font-semibold">Quantitative Feedback</p>
				<FeedbackCaroussel />
				<!-- <p class="text-7xl font-semibold">From open question answers:</p>
				<p class="text-5xl">
					<span class="icon-[tabler--plus] align-center"> </span> Significantly reduced stress
				</p>
				<p class="text-5xl">
					<span class="icon-[tabler--plus] align-center"> </span> Deeper learning
				</p>
				<p class="text-5xl">
					<span class="icon-[tabler--plus] align-center"> </span> More responsibility
				</p>
				<p class="text-5xl">
					<span class="icon-[tabler--plus] align-center"> </span> Higher motivation
				</p>
				<p class="text-5xl">
					<span class="icon-[tabler--minus] align-center"> </span> Focus goes, where the pressure is:
					other courses
				</p> -->
			</NodeOverlay>
			{#snippet legalTitle()}Legal{/snippet}
			<NodeOverlay
				buttonText={legalTitle}
				buttonExtraClasses="btn-error top-8/10 right-2/10 -mt-5 mr-8"
				cardExtraClasses="bg-error-container text-error-container-content"
			>
				<p class="text-5xl">
					Legal requirement <br />
					<span class="text-3xl">Teacher needs to ensure, that student learns</span>
				</p>

				<p class="text-5xl">
					Honours Codex <br /> <span class="text-3xl">Full back up from leadership</span>
				</p>

				<p class="text-5xl">
					Attention from ministry <br /> <span class="text-3xl">Course description censored</span>
				</p>
			</NodeOverlay>
			{#snippet interestTitle()}Interest{/snippet}
			<NodeOverlay
				buttonText={interestTitle}
				buttonExtraClasses="btn-secondary top-6/10 right-6/10"
				cardExtraClasses="bg-secondary-container text-secondary-container-content"
			>
				<p class="text-7xl font-semibold">External Interest</p>
				<p class="text-5xl">Colleague: seminar for group</p>
				<p class="text-5xl">Copenhagen Business School: evening lecture</p>
				<p class="text-5xl">Danish university librarians: invited talk</p>
			</NodeOverlay>
		</div>
		<!-- </div> -->
	</FramedSlide>
	<section>
		<div class="r-stretch flex flex-col items-center justify-center gap-12">
			<!-- <Badge title="Question 1" color="secondary" /> -->
			<!-- <div class="text-secondary mt-8 mb-16 text-8xl font-semibold"></div> -->
			<!-- <div
				class="text-secondary-content bg-secondary shadow-base-shadow shadow-large mt-8 rounded-full p-10 px-40 text-7xl font-semibold shadow-inner"
			>
				<Badge title="Question 1" color="secondary" />
				<br />
				What are you hearing,<br /> sensing, feeling, observing, <br /> that I have not said or shown?
			</div> -->
			<Question title="Question 1" color="secondary">
				What are you hearing,<br /> sensing, feeling, observing, <br /> that I have
				<span class="italic">not</span> said or shown?
			</Question>
			<Question title="Question 2" color="secondary">
				How can I communicate <br /> across the gap between <br />
				<span class="italic">regenerative</span>
				and <span class="italic">corporate</span>?
			</Question>
			<!-- <div
				class="text-secondary-content bg-secondary shadow-base-shadow shadow-large mt-8 rounded-full p-10 px-40 text-7xl font-semibold shadow-inner"
			>
				<Badge title="Question 2" color="secondary" />
				<br />
				How can I communicate <br /> across the gap between <br />
				<span class="italic">regenerative</span>
				and <span class="italic">corporate</span>?
			</div> -->
		</div>
	</section>
	<section>
		<div class="flex items-center justify-center text-[200px] font-bold">
			<span class="icon-[ic--round-question-mark] rotate-180 transform"></span> Questions
			<span class="icon-[ic--round-question-mark]"></span>
		</div>
	</section>
</RevealJs>
