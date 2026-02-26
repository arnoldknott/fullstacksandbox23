<script lang="ts">
	import type { PageData } from './$types';
	import { SocketIO, type SocketioConnection, type SocketioStatus } from '$lib/socketio';
	import type { MessageExtended, NumericalExtended } from '$lib/types';
	import { Action } from '$lib/accessHandler';
	import { flip } from 'svelte/animate';
	import JsonData from '$components/JsonData.svelte';
	import Heading from '$components/Heading.svelte';
	import Title from '$components/Title.svelte';
	import Display from '$components/Display.svelte';
	import { onDestroy, onMount } from 'svelte';

	let { data }: { data: PageData } = $props();

	let messageMetaData = $state('');
	let metadataError = $state('');
	let myMessage: MessageExtended = $state({
		id: 'new_' + Math.random().toString(36).substring(2, 9),
		content: '',
		language: 'en'
	});
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

	const parseMetadataInput = (raw: string): Record<string, unknown> | null => {
		if (!raw.trim()) {
			return {};
		}

		try {
			const parsed = JSON.parse(raw);
			if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
				return parsed as Record<string, unknown>;
			}
			metadataError = 'Metadata must be a JSON object, e.g. {"course":"dev2","year":2023}';
			return null;
		} catch {
			metadataError = 'Invalid JSON metadata. Example: {"course":"dev2","year":2023}';
			return null;
		}
	};

	const buildMessageContent = (metadata: Record<string, unknown>, body: string): string => {
		if (!Object.keys(metadata).length) {
			return body;
		}

		const metadataLines = Object.entries(metadata).map(
			([key, value]) => `${key}: ${String(value)}`
		);
		return `---\n${metadataLines.join('\n')}\n---\n\n${body}`;
	};

	const submitMessage = () => {
		metadataError = '';
		const parsedMetadata = parseMetadataInput(messageMetaData);
		if (parsedMetadata === null) {
			return;
		}

		const body = myMessage.content.trim();
		if (!body) {
			metadataError = 'Message body is empty.';
			return;
		}

		const outgoingMessage: MessageExtended = {
			...myMessage,
			content: buildMessageContent(parsedMetadata, myMessage.content)
		};

		messageAnswers = [outgoingMessage, ...messageAnswers];
		messageSocketio.submitEntity(outgoingMessage, questionId, true, true, Action.READ);
		myMessage = {
			id: 'new_' + Math.random().toString(36).substring(2, 9),
			content: '',
			language: 'en'
		};
		// messageMetaData = '';
	};
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
				<div class="title-small break-words whitespace-pre-wrap">{text}</div>
				<span class="label-small badge rounded-full px-4">{id.slice(0, 8)}...</span>
			</div>
		</div>
	</div>
{/snippet}

<Display>{data.questionsData?.questions.question || 'No question selected.'}</Display>
{#if !data.questionsData?.questions.question}
	<Title id="note-on-query-string-question-id">Add id to question as query string (for now)!</Title>
{/if}
<Heading id="messageAnswers">Add an answer</Heading>

<div class="grid grid-cols-2 gap-2">
	<div class="flex gap-1 text-left">
		<div class="grow-1">
			<label class="label-text" for="sharing">
				<div class="heading-large">Message Answer</div>
				<div class="label">(currently inherit=true and public=true and publicAccess=read)</div>
			</label>
			<input
				type="text"
				bind:value={messageMetaData}
				placeholder={'Metadata JSON, e.g. {"course":"dev2","year":2023}'}
				class="input mb-2 w-full"
			/>
			{#if metadataError}
				<div class="label text-error mb-2">{metadataError}</div>
			{/if}

			<!-- <div class="flex items-end gap-3 "> -->
			<textarea
				class="textarea w-full border border-2 p-2 shadow-inner placeholder:italic"
				rows="8"
				placeholder="Add an answer here. Use Enter for a new line."
				id="sharing"
				bind:value={myMessage.content}
			></textarea>
			<!-- </div> -->
		</div>
		<button
			type="button"
			class="btn-secondary-container btn btn-circle btn-gradient shrink-0 self-end"
			aria-label="Add Icon Button"
			onclick={submitMessage}
		>
			<span class="icon-[tabler--send-2]"></span>
		</button>
	</div>
</div>

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
