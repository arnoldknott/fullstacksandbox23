<script lang="ts">
	import type { PageData } from './$types';
	import { SocketIO, type SocketioConnection } from '$lib/socketio';
	import type { Message } from '$lib/types';
	import RevealJS from '$components/RevealJS.svelte';
	import MotivationTable from './MotivationTable.svelte';
	import SlideTitle from './SlideTitle.svelte';
	import { flip } from 'svelte/animate';

	let { data }: { data: PageData } = $props();

	let intentionAnswers = $state<Message[]>(data.questionsData?.intention.messages || []);

	const connection: SocketioConnection = {
		namespace: '/message',
		query_params: {
			'parent-id': data.questionsData?.intention.id || ''
		}
	};
	const socketio = new SocketIO(connection, () => intentionAnswers);

	socketio.client.on('transferred', (data: Message) => {
		// if (debug) {
		// 	console.log(
		// 		'=== dashboard - backend-demo-resource - socketio - +page.svelte - received DemoResources ==='
		// 	);
		// 	console.log(data);
		// }
		socketio.handleTransferred(data);
	});

	console.log('=== Page Data in +page.svelte for intention slide ===');
	console.log(data.questionsData);
	let sharing = $state('');
	let intentionAnwers: string[] = $state([
		'A short answer!',
		'A longer answer, someone had something to share in the session. We are grateful for all inputs!',
		'At some point we gotta flip over here, right?!',
		'Another answer - might be a reaction to the first or a stand alone! What happens if this answer exceeds a certain length? Will it wrap around correctly and still be readable?',
		'Another Answer of someone, who has something to share. Going deep inside and make that share a bit longer, so it wraps around correctly and is still readable.',
		'SingleWord',
		'One more short',
		'Another answer - might be a reaction to the first or a stand alone! What happens if this answer exceeds a certain length? Will it wrap around correctly and still be readable?',
		'A medium length answer to see how that looks like in the sharing round section of the presentation slide.',
		'Another answer - might be a reaction to the first or a stand alone! What happens if this answer exceeds a certain length? Will it wrap around correctly and still be readable?'
	]);
</script>

{#snippet intentionAnswer(text: string, index: number)}
	<div class="chat chat-receiver">
		<div class="chat-bubble text-left {index % 2 ? 'chat-bubble-accent' : 'chat-bubble-primary'}">
			{text}
		</div>
	</div>
{/snippet}

<RevealJS>
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
						bind:value={sharing}
						onkeydown={(event) => {
							if (event.key === 'Enter' && !event.shiftKey) {
								event.preventDefault();
								intentionAnwers = [sharing, ...intentionAnwers];
								sharing = '';
							}
						}}
					></textarea>
				</div>
			</div>
			<div class="heading mt-8">
				<div class="mx-5 grid max-h-[700px] grid-cols-3 overflow-y-auto">
					<div class="mx-2 flex w-full flex-col gap-4">
						{#each intentionAnwers as answer, index (index)}
							<div animate:flip>
								{#if index % 3 === 0}
									{@render intentionAnswer(answer, index)}
								{/if}
							</div>
						{/each}
					</div>
					<div class="mx-2 flex flex-col gap-4">
						{#each intentionAnwers as answer, index (index)}
							<div animate:flip>
								{#if index % 3 === 1}
									{@render intentionAnswer(answer, index)}
								{/if}
							</div>
						{/each}
					</div>
					<div class="mx-2 flex flex-col gap-4">
						{#each intentionAnwers as answer, index (index)}
							<div animate:flip>
								{#if index % 3 === 2}
									{@render intentionAnswer(answer, index)}
								{/if}
							</div>
						{/each}
					</div>
				</div>
			</div>
		</div>
	</section>
	<section>
		<SlideTitle>Motivation</SlideTitle>
		<p>Self determination theory:</p>
		<p class="text-error">Consider removing?</p>
		<ul>
			<li>Autonomy</li>
			<li>Competence</li>
			<li>Sense of Belonging</li>
			<li>(Meaning)</li>
		</ul>
	</section>
	<section>
		<section>
			<SlideTitle>Motivation</SlideTitle>
			<MotivationTable />
		</section>
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
