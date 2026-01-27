<script lang="ts">
	import type { PageData } from './$types';
	import { SocketIO, type SocketioConnection, type SocketioStatus } from '$lib/socketio';
	import type { MessageExtended } from '$lib/types';
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

	let intentionAnswers: MessageExtended[] = $state(data.questionsData?.intention.messages || []);
	let questionId = data.questionsData?.intention.id || '';

	let intentionAnswersSorted: MessageExtended[] = $derived(
		intentionAnswers.toSorted((a, b) => {
			if (!a.creation_date || !b.creation_date) {
				return 1;
			} else {
				return !a.creation_date > !b.creation_date ? 1 : -1;
			}
		})
	);

	const connection: SocketioConnection = {
		namespace: '/message',
		query_params: { 'parent-id': questionId, 'request-access-data': true }
	};
	const socketio = new SocketIO(connection, () => intentionAnswers);

	socketio.client.on('transferred', (data: MessageExtended) => {
		// if (debug) {
		// console.log(
		// 	'=== 🧦 dashboard - backend-demo-resource - socketio - +page.svelte - received DemoResources ==='
		// );
		// console.log(data);
		// }
		socketio.handleTransferred(data);
	});

	socketio.client.on('status', (data: SocketioStatus) => {
		// if (debug) {
		// console.log(
		// 	'=== 🧦 dashboard - backend-demo-resource - socketio - +page.svelte - received status update ==='
		// );
		// console.log('Status update:', data);
		// }
		socketio.handleStatus(data);
	});

	socketio.client.on('deleted', (message_id: string) => {
		// if (debug) {
		// 	console.log(
		// 		'=== dashboard - backend-demo-resource - socketio - +page.svelte - deleted DemoResources ==='
		// 	);
		// 	console.log(resource_id);
		// }
		socketio.handleDeleted(message_id);
	});

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

	let addColorToMotivationTable = $state(true);

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


	const backgroundColor = false
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

<RevealJS bind:reveal={revealInstance}>
	<section>
		<h1>Welcome</h1>
	</section>
	<section>
		<div class="relative">
			<div class="absolute top-2 right-10">Some absolut text</div>
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
						class="heading placeholder:title w-full border border-2 p-2 shadow-inner placeholder:italic"
						placeholder="The sharing is publically available on the internet for everyone, who has a link to this presentation. Sharing is caring 🫶"
						id="sharing"
						bind:value={mySharing.content}
						onkeydown={(event) => {
							if (event.key === 'Enter' && !event.shiftKey) {
								event.preventDefault();
								intentionAnswers = [mySharing, ...intentionAnswers];
								socketio.addEntity(mySharing);
								socketio.submitEntity(mySharing, questionId, true, true, Action.READ);
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
				<div class="mx-5 grid max-h-[500px] grid-cols-3 gap-4 overflow-y-auto">
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
	<section data-background-color={backgroundColor || 'rgb(var(--md-rgb-color-primary-container))'}>
		<SlideTitle>Motivation</SlideTitle>
		<p class="heading-large text-primary">Self determination theory - Ryan and Deci / Ib Ravn</p>

		<p class="text-error">Consider removing?</p>
		<ul>
			<li>Autonomy</li>
			<li>Competence</li>
			<li>Sense of Belonging</li>
			<li>(Meaning)</li>
		</ul>
	</section>
	<!-- <section data-background-color={addColorToMotivationTable || 'rgb(var(--md-rgb-color-primary-container))'}> -->
	<section class="h-80% p-2 rounded-lg {addColorToMotivationTable ? 'bg-green-300/30 ' : ''}">
		<div >
			<SlideTitle>Motivation</SlideTitle>
			<MotivationTable />
			{addColorToMotivationTable}
		</div>
	</section>
	<section>
		<SlideTitle>Inclusion</SlideTitle>
	</section>
	<section>
		<SlideTitle>My motivation</SlideTitle>
		<p class="text-error">Consider removing?</p>
	</section>
	<section>
		<SlideTitle>To pass the course...</SlideTitle>
	</section>
</RevealJS>
