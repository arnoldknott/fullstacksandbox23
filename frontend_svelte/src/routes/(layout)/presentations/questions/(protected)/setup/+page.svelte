<script lang="ts">
	import type { PageData } from './$types';
	import { SocketIO, type SocketioConnection, type SocketioStatus } from '$lib/socketio';
	import type { MessageExtended, NumericalExtended } from '$lib/types';
	import { flip } from 'svelte/animate';
	import JsonData from '$components/JsonData.svelte';
	import Heading from '$components/Heading.svelte';
	import Title from '$components/Title.svelte';
	import Display from '$components/Display.svelte';
	import { onDestroy, onMount } from 'svelte';

	let { data }: { data: PageData } = $props();
	let questionId = data.questionsData?.questions.id || '';
	let messageAnswers: MessageExtended[] = $state(data.questionsData?.questions.messages || []);
	let numericalAnswers: NumericalExtended[] = $state(
		data.questionsData?.questions.numericals || []
	);

	let messageAnswersSorted: MessageExtended[] = $derived(
		messageAnswers.toSorted((a, b) => {
			if (!a.creation_date) return 1;
			if (!b.creation_date) return 1;
			return a.creation_date < b.creation_date ? 1 : -1;
		})
	);

	let numericalAnswersSorted: NumericalExtended[] = $derived(
		numericalAnswers.toSorted((a, b) => {
			if (!a.creation_date) return 1;
			if (!b.creation_date) return 1;
			return a.creation_date < b.creation_date ? 1 : -1;
		})
	);

	const messageConnection: SocketioConnection = {
		namespace: '/message',
		cookie_session_id: data?.session?.sessionId || '',
		query_params: { 'parent-id': questionId, 'request-access-data': true }
	};
	const numericalConnection: SocketioConnection = {
		namespace: '/numerical',
		cookie_session_id: data?.session?.sessionId || '',
		query_params: { 'parent-id': questionId, 'request-access-data': true }
	};
	let messageSocketio: SocketIO = $state(undefined as unknown as SocketIO);
	let numericalSocketio: SocketIO = $state(undefined as unknown as SocketIO);
	onMount(() => {
		messageSocketio = new SocketIO(messageConnection, () => messageAnswers);
		numericalSocketio = new SocketIO(numericalConnection, () => numericalAnswers);

		messageSocketio.client.on('transferred', (data: MessageExtended) => {
			// if (debug) {
			// 	console.log(
			// 		'=== 🧦 dashboard - backend-demo-resource - socketio - +page.svelte - received DemoResources ==='
			// 	);
			// 	console.log(data);
			// }
			messageSocketio.handleTransferred(data);
		});

		messageSocketio.client.on('status', (data: SocketioStatus) => {
			// if (debug) {
			console.log(
				'=== 🧦 dashboard - backend-demo-resource - socketio - +page.svelte - received status update ==='
			);
			console.log('Status update:', data);
			// }
			messageSocketio.handleStatus(data);
		});

		messageSocketio.client.on('deleted', (message_id: string) => {
			// if (debug) {
			// 	console.log(
			// 		'=== dashboard - backend-demo-resource - socketio - +page.svelte - deleted DemoResources ==='
			// 	);
			// 	console.log(resource_id);
			// }
			messageSocketio.handleDeleted(message_id);
		});

		// TBD: put in onMount!

		numericalSocketio.client.on('transferred', (data: MessageExtended) => {
			// if (debug) {
			// 	console.log(
			// 		'=== 🧦 dashboard - backend-demo-resource - socketio - +page.svelte - received DemoResources ==='
			// 	);
			// 	console.log(data);
			// }
			numericalSocketio.handleTransferred(data);
		});

		numericalSocketio.client.on('status', (data: SocketioStatus) => {
			// if (debug) {
			console.log(
				'=== 🧦 dashboard - backend-demo-resource - socketio - +page.svelte - received status update ==='
			);
			console.log('Status update:', data);
			// }
			numericalSocketio.handleStatus(data);
		});

		numericalSocketio.client.on('deleted', (message_id: string) => {
			// if (debug) {
			// 	console.log(
			// 		'=== dashboard - backend-demo-resource - socketio - +page.svelte - deleted DemoResources ==='
			// 	);
			// 	console.log(resource_id);
			// }
			numericalSocketio.handleDeleted(message_id);
		});
	});
	onDestroy(() => {
		messageSocketio?.client.disconnect();
		numericalSocketio?.client.disconnect();
	});
</script>

{#snippet answerBubble(text: string | number, id: string, index: number)}
	<div class="chat chat-receiver">
		<div class="chat-bubble text-left {index % 2 ? 'chat-bubble-accent' : 'chat-bubble-primary'}">
			<div class="flex flex-col">
				<button
					type="button"
					class="btn btn-sm btn-error-container text-error-container-content"
					aria-label="Close"
					data-combo-box-close=""
					onclick={() => {
						if (id) {
							if (typeof text === 'string') {
								messageSocketio?.deleteEntity(id);
							} else {
								numericalSocketio?.deleteEntity(id);
							}
						}
					}}
				>
					Delete <span class="icon-[tabler--trash] size-4 shrink-0"></span>
				</button>
				<div class="title-small">{text}</div>
				<span class="label-small badge rounded-full px-4">{id.slice(0, 8)}...</span>
			</div>
		</div>
	</div>
{/snippet}

<Display>{data.questionsData?.questions.question || 'No question selected.'}</Display>
{#if !data.questionsData?.questions.question}
	<Title id="note-on-query-string-question-id">Add id to question as query string (for now)!</Title>
{/if}
<Heading id="messageAnswers">Message Answers:</Heading>

<div class="mx-2 grid w-full grid-cols-5 gap-2">
	{#each messageAnswersSorted as answer, index (index)}
		<div animate:flip>
			{@render answerBubble(answer.content, answer.id, index)}
		</div>
	{/each}
</div>

<Heading id="numericalAnswers">Numerical Answers:</Heading>

<div class="mx-2 grid w-full grid-cols-5 gap-2">
	{#each numericalAnswersSorted as answer, index (index)}
		<div animate:flip>
			{@render answerBubble(answer.value, answer.id, index)}
		</div>
	{/each}
</div>

<Heading id="numericalAnswers">JSONdata:</Heading>

<JsonData data={data.questionsData} />
