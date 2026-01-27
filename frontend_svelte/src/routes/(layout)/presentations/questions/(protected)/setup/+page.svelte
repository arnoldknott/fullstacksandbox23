<script lang="ts">
	import type { PageData } from './$types';
	import { SocketIO, type SocketioConnection, type SocketioStatus } from '$lib/socketio';
	import type { MessageExtended } from '$lib/types';
	import { flip } from 'svelte/animate';
	import JsonData from '$components/JsonData.svelte';
	import Heading from '$components/Heading.svelte';

	let { data }: { data: PageData } = $props();
	let intentionAnswers: MessageExtended[] = $state(data.questionsData?.intention.messages || []);
	let questionId = data.questionsData?.intention.id || '';

	let intentionAnswersSorted: MessageExtended[] = $derived(
		intentionAnswers.toSorted((a, b) => {
			if (!a.creation_date) return 1;
			if (!b.creation_date) return 1;
			return a.creation_date < b.creation_date ? 1 : -1;
		})
	);

	const connection: SocketioConnection = {
		namespace: '/message',
		cookie_session_id: data?.session?.sessionId || '',
		query_params: { 'parent-id': questionId, 'request-access-data': true }
	};
	const socketio = new SocketIO(connection, () => intentionAnswers);

	socketio.client.on('transferred', (data: MessageExtended) => {
		// if (debug) {
		// 	console.log(
		// 		'=== 🧦 dashboard - backend-demo-resource - socketio - +page.svelte - received DemoResources ==='
		// 	);
		// 	console.log(data);
		// }
		socketio.handleTransferred(data);
	});

	socketio.client.on('status', (data: SocketioStatus) => {
		// if (debug) {
		console.log(
			'=== 🧦 dashboard - backend-demo-resource - socketio - +page.svelte - received status update ==='
		);
		console.log('Status update:', data);
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
</script>

{#snippet intentionAnswer(text: string, id: string, index: number)}
	<div class="chat chat-receiver">
		<div class="chat-bubble text-left {index % 2 ? 'chat-bubble-accent' : 'chat-bubble-primary'}">
			<div class="flex flex-col">
				<button
					type="button"
					class="btn btn-sm btn-error-container text-error-container-content"
					aria-label="Close"
					data-combo-box-close=""
					onclick={() => !id || socketio?.deleteEntity(id)}
				>
					Delete <span class="icon-[tabler--trash] size-4 shrink-0"></span>
				</button>
				<div class="title-small">{text}</div>
				<span class="label-small badge rounded-full px-4">{id.slice(0, 8)}...</span>
			</div>
		</div>
	</div>
{/snippet}

<Heading id="intentionAnswers">Intention Answers</Heading>
<p>Add id as query string (for now)!</p>

<div class="mx-2 grid w-full grid-cols-5 gap-2">
	{#each intentionAnswersSorted as answer, index (index)}
		<div animate:flip>
			{@render intentionAnswer(answer.content, answer.id, index)}
		</div>
	{/each}
</div>

<JsonData data={data.questionsData} />
