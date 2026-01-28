<script lang="ts">
	import type { PageData } from './$types';
	import { SocketIO, type SocketioConnection, type SocketioStatus } from '$lib/socketio';
	import type { MessageExtended, Numerical } from '$lib/types';
	import RevealJS from '$components/RevealJS.svelte';
	import type { Api } from 'reveal.js';
	import MotivationTable from './MotivationTable.svelte';
	import SlideTitle from './SlideTitle.svelte';
	import { flip } from 'svelte/animate';
	import { Action } from '$lib/accessHandler';

	interface RevealFragmentEvent extends Event {
		fragment: HTMLElement;
		fragments: HTMLElement[];
	}

	let { data }: { data: PageData } = $props();

	let revealInstance = $state<Api | undefined>(undefined);

	// TBD: catch gracefully, if no intention or motivation question is available
	let intentionAnswers: MessageExtended[] = $state(data.questionsData?.intention.messages || []);
	let intentionQuestionId = data.questionsData?.intention.id || '';

	let motivationAnswers: Numerical[] = $state(data.questionsData?.motivation.numericals || []);
	let motivationQuestionId = data.questionsData?.motivation.id || '';

	let intentionAnswersSorted: MessageExtended[] = $derived(
		intentionAnswers.toSorted((a, b) => {
			if (!a.creation_date || !b.creation_date) {
				return 1;
			} else {
				return !a.creation_date > !b.creation_date ? 1 : -1;
			}
		})
	);

	const intentionConnection: SocketioConnection = {
		namespace: '/message',
		query_params: { 'parent-id': intentionQuestionId, 'request-access-data': true }
	};
	const socketioMessages = new SocketIO(intentionConnection, () => intentionAnswers);
	socketioMessages.client.on('transferred', (data: MessageExtended) => {
		// if (debug) {
		// console.log(
		// 	'=== 🧦 dashboard - backend-demo-resource - socketio - +page.svelte - received DemoResources ==='
		// );
		// console.log(data);
		// }
		socketioMessages.handleTransferred(data);
	});

	socketioMessages.client.on('status', (data: SocketioStatus) => {
		// if (debug) {
		// console.log(
		// 	'=== 🧦 dashboard - backend-demo-resource - socketio - +page.svelte - received status update ==='
		// );
		// console.log('Status update:', data);
		// }
		socketioMessages.handleStatus(data);
	});

	socketioMessages.client.on('deleted', (message_id: string) => {
		// if (debug) {
		// 	console.log(
		// 		'=== dashboard - backend-demo-resource - socketio - +page.svelte - deleted DemoResources ==='
		// 	);
		// 	console.log(resource_id);
		// }
		socketioMessages.handleDeleted(message_id);
	});

	const connectionNumericals: SocketioConnection = {
		namespace: '/numerical',
		query_params: { 'parent-id': motivationQuestionId }
	};

	let motivationAnswersAverage: number = $derived.by(() => {
		if (motivationAnswers.length <= 5) {
			// if (motivationAnswers.length <= 1) {
			return 50;
		} else {
			const sum = motivationAnswers.reduce((acc, curr) => acc + curr.value, 0);
			return Math.round(sum / motivationAnswers.length);
		}
	});

	let averageMotivationColors = $state({ background: '0 0 0', text: '0  0 0' });

	// $effect(() => {
	// 	console.log('=== dev2 / F23 - Motivation Answers Average ===');
	// 	console.log($state.snapshot(motivationAnswersAverage));
	// 	console.log('=== dev2 / F23 - Motivation Answers Average Colors ===');
	// 	console.log($state.snapshot(averageMotivationColors));
	// });

	const socketioNumericals = new SocketIO(connectionNumericals, () => motivationAnswers);

	// let sharing = $state('');
	// let intentionAnswers: string[] = $state([
	// 	'A short answer!',
	// 	'A longer answer, someone had something to share in the session. We are grateful for all inputs!',
	// 	'At some point we gotta flip over here, right?!',
	// 	'Another answer - might be a reaction to the first or a stand alone! What happens if this answer exceeds a certain length? Will it wrap around correctly and still be readable?',
	// 	'Another Answer of someone, who has something to share. Going deep inside and make that share a bit longer, so it wraps around correctly and is still readable.',
	// 	'SingleWord',
	// 	'One more short',
	// 	'Another answer - might be a reaction to the first or a stand alone! What happens if this answer exceeds a certain length? Will it wrap around correctly and still be readable?',
	// 	'A medium length answer to see how that looks like in the sharing round section of the presentation slide.',
	// 	'Another answer - might be a reaction to the first or a stand alone! What happens if this answer exceeds a certain length? Will it wrap around correctly and still be readable?'
	// ]);
	let mySharing: MessageExtended = $state({
		id: 'new_' + Math.random().toString(36).substring(2, 9),
		content: '',
		language: 'en'
	});

	let addColorToMotivationTable = $state(false);

	$effect(() => {
		if (revealInstance) {
			revealInstance.on('fragmentshown', (event: Event) => {
				const fragmentEvent = event as RevealFragmentEvent;
				// console.log('=== fragment shown and captured in presentation ===');
				// console.log(fragmentEvent);

				if (fragmentEvent.fragment?.innerText === 'Dummy to trigger color event') {
					addColorToMotivationTable = true;
				}
			});
			revealInstance.on('fragmenthidden', (event: Event) => {
				const fragmentEvent = event as RevealFragmentEvent;
				// console.log('=== fragment shown and captured in presentation ===');
				// console.log(fragmentEvent);

				if (fragmentEvent.fragment?.innerText === 'Dummy to trigger color event') {
					addColorToMotivationTable = false;
				}
			});
		}
		// updates background color on the slides, where addColorToMotivationTable changes
		if (revealInstance && averageMotivationColors && addColorToMotivationTable !== undefined) {
			const currentSlide = revealInstance.getCurrentSlide();
			console.log('=== synchronizing slide to update background color ===');
			console.log(averageMotivationColors);
			if (currentSlide) {
				revealInstance.syncSlide(currentSlide);
			}
		}
	});

	// let revealFragmentShownEvent = $derived.by(() => {
	// 	return revealInstance?.on('fragmentshown', (event) => {
	// 		console.log('=== fragment shown and captures in presentation ===');
	// 		console.log(event);
	// 		// if (event?.fragment?.innerText === 'Dummy to trigger event') {
	// 		// 	addColorToMotivationTable = true;
	// 		// }
	// 		return event;})
	// // works returtning the event, but cannot access it outside of this function
	// 	});

	// $effect(() => {
	// 	if (revealFragmentShownEvent?.fragment?.innerText === 'Dummy to trigger event') {
	// 		addColorToMotivationTable = true;
	// 	}
	// });

	// let addColorToMotivationTable = $derived( revealFragmentShownEvent?.fragment?.innerText === 'Dummy to trigger event' ? true : false)

	// $effect(() => console.log($state.snapshot(revealFragmentShownEvent)))
	// const backgroundColor = true

	// const backgroundColor = false;
</script>

{#snippet intentionAnswer(text: string, date: Date | undefined, index: number)}
	<div class="chat chat-receiver">
		<div class="chat-bubble text-left {index % 2 ? 'chat-bubble-accent' : 'chat-bubble-primary'}">
			{text}
			<div class="label text-right">
				{date ? new Date(date).toLocaleString() : 'Thanks for your contribution 🙏'}
			</div>
		</div>
	</div>
{/snippet}

<!-- Allows covering the whole screen - but needs to be responsive in sizes to adapt to projectors  -->
<!-- <RevealJS bind:reveal={revealInstance} options={{disableLayout: true}}> -->
<RevealJS bind:reveal={revealInstance}>
	<section>
		<h1>Welcome</h1>
	</section>
	<section>
		<div class="relative">
			<!-- <div class="absolute top-2 right-10">Some absolut text</div> -->
			<SlideTitle>Sharing Round</SlideTitle>
			<div class="mx-10 mt-8">
				<div class="text-left">
					<!-- <textarea
						class="textarea textarea-xl display-large"
						placeholder="Sharing is caring"
						id="sharing"
						bind:value={sharing}
						onkeydown={(event) => {
							if (event.key === 'Enter' && !event.shiftKey) {
								event.preventDefault();
								intentionAnwers = [sharing, ...intentionAnwers];
								sharing = '';
							}
						}}
					></textarea> -->
					<label class="heading" for="sharing"
						>What is your intention for your studies, your course, this lecture? 🤔</label
					>
					<textarea
						class="heading placeholder:title-large w-full border border-2 p-2 shadow-inner placeholder:italic"
						placeholder="The sharing is publically available on the internet for everyone, who has a link to this presentation. Sharing is caring 🫶 Press Enter to send."
						id="sharing"
						bind:value={mySharing.content}
						onkeydown={(event) => {
							if (event.key === 'Enter' && !event.shiftKey) {
								event.preventDefault();
								intentionAnswers = [mySharing, ...intentionAnswers];
								socketioMessages.addEntity(mySharing);
								socketioMessages.submitEntity(
									mySharing,
									intentionQuestionId,
									true,
									true,
									Action.READ
								);
								mySharing = {
									id: 'new_' + Math.random().toString(36).substring(2, 9),
									content: '',
									language: 'en'
								};
							}
						}}
					></textarea>
				</div>
			</div>
			<div class="heading mt-8">
				<div class="mx-5 grid max-h-[500px] grid-cols-3 gap-6 overflow-y-auto">
					{#each intentionAnswersSorted as answer, index (index)}
						<div animate:flip>
							{@render intentionAnswer(answer.content, answer.creation_date, index)}
						</div>
					{/each}
					<!-- <div class="mx-2 flex w-full flex-col gap-4">
						{#each intentionAnswersSorted as answer, index (index)}
							<div animate:flip>
								{#if index % 3 === 0}
									{@render intentionAnswer(answer.content, index)}
								{/if}
							</div>
						{/each}
					</div>
					<div class="mx-2 flex flex-col gap-4">
						{#each intentionAnswersSorted as answer, index (index)}
							<div animate:flip>
								{#if index % 3 === 1}
									{@render intentionAnswer(answer.content, index)}
								{/if}
							</div>
						{/each}
					</div>
					<div class="mx-2 flex flex-col gap-4">
						{#each intentionAnswersSorted as answer, index (index)}
							<div animate:flip>
								{#if index % 3 === 2}
									{@render intentionAnswer(answer.content, index)}
								{/if}
							</div>
						{/each}
					</div> -->
				</div>
			</div>
		</div>
	</section>
	<!-- <section data-background-color={backgroundColor || 'rgb(var(--md-rgb-color-primary-container))'}> -->
	<section data-background-color="rgb(var(--md-rgb-color-primary-container))">
		<SlideTitle>Motivation</SlideTitle>
		<h2 class="heading-large text-primary-container-content">Self determination theory</h2>
		<h3>
			Ryan and Deci / Ib Ravn - <a
				href="https://opentextbc.ca/peersupport/chapter/self-determination-theory/"
				target="_blank"
				class="title-large link text-secondary-content pb-5">Source of Definitions</a
			>
		</h3>
		<div class="mx-5 grid h-120 grid-cols-4 gap-4">
			<div class="heading fragment flex flex-col">
				<div>Autonomy</div>
				<div
					class="btn btn-primary btn-gradient shadow-outline heading-small flex h-full flex-col rounded-4xl shadow-sm"
				>
					Humans need to feel in control of their own life behaviours and goals.
				</div>
			</div>
			<div class="heading-large fragment flex flex-col">
				<div>Competence</div>
				<div
					class="btn btn-secondary btn-gradient shadow-outline heading-small flex h-full flex-col rounded-4xl shadow-sm"
				>
					Humans need to gain mastery and control of their own lives & their environment. Essential
					for self-esteem.
				</div>
			</div>
			<div class="heading-large fragment flex flex-col">
				<div>Relatedness</div>
				<div
					class="btn btn-accent btn-gradient shadow-outline heading-small flex h-full flex-col rounded-4xl shadow-sm"
				>
					Humans need to experince a sense of belonging and connection with other people. Feeling
					cared for by others and to care for others
				</div>
			</div>
			<div class="heading-large fragment flex flex-col">
				<div>Meaning</div>
				<div
					class="btn btn-info btn-gradient shadow-outline heading-small flex h-full flex-col rounded-4xl shadow-sm"
				>
					Humans need to feel theri positive impact on others and their influence on improving
					welfare to contribute to a better society.
				</div>
			</div>
		</div>

		<!-- <ul>
			<li>Autonomy</li>
			<li>Competence</li>
			<li>Sense of Belonging</li>
			<li>(Meaning)</li>
		</ul> -->
	</section>
	<!-- <section
		data-background-color={addColorToMotivationTable
			? 'rgb(var(--md-rgb-color-primary-container))'
			: ''}
	> -->
	<!-- <section class="h-screen rounded-lg p-2 {addColorToMotivationTable ? 'bg-green-300/30 ' : ''}"> -->
	<!-- <section class="h-screen rounded-lg p-2" style={addColorToMotivationTable ? 'background-color: rgb(var(--md-rgb-color-primary-container))' : ''}> -->
	<section
		data-background-color={addColorToMotivationTable
			? `rgb(${averageMotivationColors.background})`
			: ''}
	>
		<div>
			<SlideTitle>Motivation</SlideTitle>
			<MotivationTable
				questionId={motivationQuestionId}
				socketio={socketioNumericals}
				averageMotivation={motivationAnswersAverage}
				bind:averageColors={averageMotivationColors}
			/>
		</div>
		<div class="relative mt-5">
			<div class="absolute top-0 right-0 mt-20">
				<span class="badge badge-lg badge-secondary shadow-outline shadow">
					{motivationAnswersAverage}
				</span>
				<span class="badge badge-lg badge-info shadow-outline shadow">
					{motivationAnswers.length}
				</span>
				<span class="text-base-300"> {addColorToMotivationTable}</span>
			</div>
		</div>
	</section>
	<!-- <div>{addColorToMotivationTable} {motivationAnswersAverage}</div> -->
	<!-- <section>
		<SlideTitle>Inclusion</SlideTitle>
	</section> -->
	<!-- <section>
		<SlideTitle>My motivation</SlideTitle>
		<p class="text-error">Consider removing?</p>
	</section> -->
	<section>
		<SlideTitle>To pass the course...</SlideTitle>
	</section>
</RevealJS>
