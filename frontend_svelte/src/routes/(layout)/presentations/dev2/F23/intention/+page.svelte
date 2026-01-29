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
	import Heading from '$components/Heading.svelte';
	import { onDestroy } from 'svelte';

	interface RevealFragmentEvent extends Event {
		fragment: HTMLElement;
		fragments: HTMLElement[];
	}

	let { data }: { data: PageData } = $props();

	let revealInstance = $state<Api | undefined>(undefined);

	// TBD: catch gracefully, if no intention or motivation question is available
	let intentionAnswers = $state(data.questionsData?.intention?.messages || []);
	let intentionQuestionId = data.questionsData?.intention?.id || '';

	let motivationAnswers = $state(data.questionsData?.motivation?.numericals || []);
	let motivationQuestionId = data.questionsData?.motivation?.id || '';

	let commentsAnswers = $state(data.questionsData?.comments?.messages || []);
	let commentsQuestionId = data.questionsData?.comments?.id || '';

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
	const socketioIntention = new SocketIO(intentionConnection, () => intentionAnswers);
	socketioIntention.client.on('transferred', (data: MessageExtended) => {
		// if (debug) {
		// console.log(
		// 	'=== 🧦 presentation - devF23 - INTENTION - received transferred update ==='
		// );
		// console.log(data);
		// }
		socketioIntention.handleTransferred(data);
	});

	socketioIntention.client.on('status', (data: SocketioStatus) => {
		// if (debug) {
		// console.log(
		// 	'=== 🧦 presentation - devF23 - INTENTION - received status update ==='
		// );
		// console.log('Status update:', data);
		// }
		socketioIntention.handleStatus(data);
	});

	socketioIntention.client.on('deleted', (message_id: string) => {
		// if (debug) {
		// 	console.log(
		// 		'=== presentation - devF23 - INTENTION - deleted messages ==='
		// 	);
		// 	console.log(message_id);
		// }
		socketioIntention.handleDeleted(message_id);
	});

	let myIntention: MessageExtended = $state({
		id: 'new_' + Math.random().toString(36).substring(2, 9),
		content: '',
		language: 'en'
	});

	// SocketIO for motivation numericals
	const connectionMotivation: SocketioConnection = {
		namespace: '/numerical',
		query_params: { 'parent-id': motivationQuestionId }
	};
	const socketioMotivation = new SocketIO(connectionMotivation, () => motivationAnswers);

	let motivationAnswersAverage: number = $derived.by(() => {
		if (motivationAnswers.length <= 5) {
			// if (motivationAnswers.length <= 1) {
			return 50;
		} else {
			const sum = motivationAnswers.reduce((acc, curr) => acc + curr.value, 0);
			return Math.round(sum / motivationAnswers.length);
		}
	});

	socketioMotivation.client.on('transferred', (data: Numerical) => {
		// if (debug) {
		// console.log(
		// 	'=== 🧦 presentation - devF23 - MOTIVATION - received transferred update ==='
		// );
		// console.log(data);
		// }
		socketioMotivation.handleTransferred(data);
	});

	socketioMotivation.client.on('status', (data: SocketioStatus) => {
		// if (debug) {
		console.log('=== 🧦 presentation - devF23 - MOTIVATION - received status update ===');
		// console.log('Status update:', data);
		// }
		socketioMotivation.handleStatus(data);
	});

	socketioMotivation.client.on('deleted', (message_id: string) => {
		// if (debug) {
		// 	console.log(
		// 		'=== presentation - devF23 - MOTIVATION - deleted messages ==='
		// 	);
		// 	console.log(message_id);
		// }
		socketioMotivation.handleDeleted(message_id);
	});

	let averageMotivationColors = $state({ background: '0 0 0', text: '0  0 0' });

	// $effect(() => {
	// 	console.log('=== dev2 / F23 - Motivation Answers Average ===');
	// 	console.log($state.snapshot(motivationAnswersAverage));
	// 	console.log('=== dev2 / F23 - Motivation Answers Average Colors ===');
	// 	console.log($state.snapshot(averageMotivationColors));
	// });

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
		// console.log('=== dev2 / F23 - Motivation Average Color ===');
		// console.log($state.snapshot(averageMotivationColors));
		// updates background color on the slides, where addColorToMotivationTable changes
		// if (revealInstance && averageMotivationColors && addColorToMotivationTable !== undefined) {
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

	let commentsAnswersSorted: MessageExtended[] = $derived(
		commentsAnswers.toSorted((a, b) => {
			if (!a.creation_date || !b.creation_date) {
				return 1;
			} else {
				return !a.creation_date > !b.creation_date ? 1 : -1;
			}
		})
	);

	const commentConnection: SocketioConnection = {
		namespace: '/message',
		query_params: { 'parent-id': commentsQuestionId, 'request-access-data': true }
	};
	const socketioComment = new SocketIO(commentConnection, () => commentsAnswers);
	socketioComment.client.on('transferred', (data: MessageExtended) => {
		// if (debug) {
		// console.log(
		// 	'=== 🧦 presentation - devF23 - COMMENT - received transferred update ==='
		// );
		// console.log(data);
		// }
		socketioComment.handleTransferred(data);
	});

	socketioComment.client.on('status', (data: SocketioStatus) => {
		// if (debug) {
		// console.log(
		// 	'=== 🧦 presentation - devF23 - COMMENT - received status update ==='
		// );
		// console.log('Status update:', data);
		// }
		socketioComment.handleStatus(data);
	});

	socketioComment.client.on('deleted', (message_id: string) => {
		// if (debug) {
		// 	console.log(
		// 		'=== presentation - devF23 - COMMENT - deleted messages ==='
		// 	);
		// 	console.log(message_id);
		// }
		socketioComment.handleDeleted(message_id);
	});

	let myComment: MessageExtended = $state({
		id: 'new_' + Math.random().toString(36).substring(2, 9),
		content: '',
		language: 'en'
	});

	onDestroy(() => {
		socketioIntention.client.disconnect();
		socketioMotivation.client.disconnect();
		socketioComment.client.disconnect();
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

{#snippet messageAnswer(text: string, date: Date | undefined, index: number)}
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
		<SlideTitle>Sharing Round</SlideTitle>
		<div class="mx-10 mt-8">
			<div class="text-left">
				<label class="heading" for="sharing"
					>What is your intention for your studies, your course, this lecture? 🤔</label
				>
				<textarea
					class="heading placeholder:title-large w-full border border-2 p-2 shadow-inner placeholder:italic"
					placeholder="The sharing is publically available on the internet for everyone, who has a link to this presentation. Sharing is caring 🫶 Press Enter to send."
					id="sharing"
					bind:value={myIntention.content}
					onkeydown={(event) => {
						if (event.key === 'Enter' && !event.shiftKey) {
							event.preventDefault();
							intentionAnswers = [myIntention, ...intentionAnswers];
							socketioIntention.addEntity(myIntention);
							socketioIntention.submitEntity(
								myIntention,
								intentionQuestionId,
								true,
								true,
								Action.READ
							);
							myIntention = {
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
			<div class="mx-5 grid max-h-[400px] grid-cols-3 gap-6 overflow-y-auto">
				{#each intentionAnswersSorted as answer, index (index)}
					<div animate:flip>
						{@render messageAnswer(answer.content, answer.creation_date, index)}
					</div>
				{/each}
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
				socketio={socketioMotivation}
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
	<section>
		<SlideTitle>Inclusion</SlideTitle>
		<Heading>We have diversity on this course...</Heading>
		<ul>
			<li>About 10 different study lines,</li>
			<li>More than 100 students,</li>
			<li>Online and physical attendance,</li>
		</ul>
		<div class="fragment">
			<p>and everyone has their own</p>
			<ul>
				<li>individual learning preferences</li>
				<li>technical background</li>
				<li>life situation</li>
				<li>intentions,</li>
			</ul>
		</div>
		<p
			class="btn btn-gradient btn-primary-container heading fragment mx-5 mt-5 h-fit rounded-xl p-4 px-5"
		>
			What can you do, to make this a pleasureable learning environment where everyone feels
			included and can strive?
		</p>
	</section>
	<!-- <section>
		<SlideTitle>My motivation</SlideTitle>
		<p class="text-error">Consider removing?</p>
	</section> -->
	<section>
		<SlideTitle>Thank you for joining and participating!</SlideTitle>
		<!-- <Heading>Do you have comments or questions?</Heading> -->
		<div class="mx-10 mt-8">
			<div class="text-left">
				<label class="heading" for="sharing"> Do you have comments or questions? 🤔 </label>
				<textarea
					class="heading placeholder:title-large w-full border border-2 p-2 shadow-inner placeholder:italic"
					placeholder="These questions and comments are publically available on the internet for everyone, who has a link to this presentation. Sharing is caring 🫶 Press Enter to send."
					id="sharing"
					bind:value={myComment.content}
					onkeydown={(event) => {
						if (event.key === 'Enter' && !event.shiftKey) {
							event.preventDefault();
							commentsAnswers = [myComment, ...commentsAnswers];
							socketioComment.addEntity(myComment);
							socketioComment.submitEntity(myComment, commentsQuestionId, true, true, Action.READ);
							myComment = {
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
			<div class="mx-5 grid max-h-[400px] grid-cols-3 gap-6 overflow-y-auto">
				{#each commentsAnswersSorted as answer, index (index)}
					<div animate:flip>
						{@render messageAnswer(answer.content, answer.creation_date, index)}
					</div>
				{/each}
			</div>
		</div>
	</section>
	<!-- <section>
		<SlideTitle>To pass the course...</SlideTitle>
		<Heading>Hand in the four assignments</Heading>
	</section> -->
</RevealJS>
