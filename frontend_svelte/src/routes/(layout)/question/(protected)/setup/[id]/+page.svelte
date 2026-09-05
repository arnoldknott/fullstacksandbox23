<script lang="ts">
	import Icon from '@iconify/svelte';
	import { onDestroy, onMount } from 'svelte';
	import { flip } from 'svelte/animate';
	import { fade, slide } from 'svelte/transition';

	import Card from '$components/Card.svelte';
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';
	import JsonData from '$components/JsonData.svelte';
	import Table, {
		field,
		icon,
		snippet,
		type TableColumn,
		text,
		value
	} from '$components/Table.svelte';
	import Title from '$components/Title.svelte';
	import { Action } from '$lib/accessHandler';
	import { SocketIO, type SocketioConnection } from '$lib/socketio.svelte';
	import type { MessageExtended, NumericalExtended } from '$lib/types';
	import { initTabs } from '$lib/userInterface';

	import ActionButtons from '../../../../presentation/(protected)/setup/ActionButtons.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	// let messageMetaData = $state('{"course":"dev2","year":2023,"number": NaN}');
	let messageMetaData = $state('');
	let metadataError = $state('');
	let questionId = $derived(data.questionsData?.questions.id || '');
	let messageSocketio: SocketIO<MessageExtended> = $state()!;
	let numericalSocketio: SocketIO<NumericalExtended> = $state()!;
	// let messageAnswers = $derived(messageSocketio?.entities ?? []);
	// let numericalAnswers = $derived(numericalSocketio?.entities ?? []);

	// let messageAnswersSorted: MessageExtended[] = $derived(
	// 	messageAnswers.toSorted((a, b) => {
	// 		if (!a.creation_date) return 1;
	// 		if (!b.creation_date) return 1;
	// 		return a.creation_date < b.creation_date ? 1 : -1;
	// 	})
	// );
	// let numericalAnswersSorted: NumericalExtended[] = $derived(
	// 	numericalAnswers.toSorted((a, b) => {
	// 		if (!a.creation_date) return 1;
	// 		if (!b.creation_date) return 1;
	// 		return a.creation_date < b.creation_date ? 1 : -1;
	// 	})
	// );

	// let messageAnswersSorted: MessageExtended[] = $derived(
	// 	messageSocketio?.getSelectedEntities('sortedMessageAnswers') ?? []
	// );
	let numericalAnswersSorted: NumericalExtended[] = $derived(
		numericalSocketio?.getSelectedEntities('sortedNumericalAnswers') ?? []
	);

	const messageConnection: SocketioConnection = $derived({
		namespace: '/message',
		sessionId: data?.session?.sessionId || '',
		parentId: questionId,
		queryParams: { 'request-access-data': true }
	});

	const numericalConnection: SocketioConnection = $derived({
		namespace: '/numerical',
		sessionId: data?.session?.sessionId || '',
		parentId: questionId,
		queryParams: { 'request-access-data': true }
	});
	onMount(() => {
		messageSocketio = new SocketIO<MessageExtended>(messageConnection, {
			template: { content: '', language: 'en' }
		});
		messageSocketio.createSortedSelection('sortedMessageAnswers', 'creation_date', false);
		numericalSocketio = new SocketIO<NumericalExtended>(numericalConnection);
		numericalSocketio.createSortedSelection('sortedNumericalAnswers', 'creation_date', false);
		// messageSocketio.createPending();
	});

	$effect(() => {
		messageSocketio.entities = data.questionsData?.questions.messages || [];
		numericalSocketio.entities = data.questionsData?.questions.numericals || [];
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
			metadataError =
				'Metadata must be a JSON object, e.g. {"course":"dev2","year":2023,"number": 42}';
			return null;
		} catch {
			metadataError = 'Invalid JSON metadata. Example: {"course":"dev2","year":2023,"number": 42}';
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

		const body = messageSocketio.pendingEntities[0].content.trim();
		if (!body) {
			metadataError = 'Message body is empty.';
			return;
		}

		const outgoingMessage: MessageExtended = {
			...messageSocketio.pendingEntities[0],
			content: buildMessageContent(parsedMetadata, messageSocketio.pendingEntities[0].content)
		};
		// TBD: add true access control selection and not just default public read access!
		messageSocketio.addPendingAccessPolicy(outgoingMessage.id, {
			public: true,
			action: Action.READ
		});
		messageSocketio.submitEntity(outgoingMessage, questionId, true);
		messageSocketio.createPending();
		// messageMetaData = '';
	};

	let hideNewMessageAnswerCard = $state(true);
	let messageViewMode = $state<'grid' | 'list' | 'table'>('table');

	const flag = (language: string) =>
		language === 'en-US'
			? 'flagpack:us'
			: language === 'da-DK'
				? 'flagpack:dk'
				: language === 'de-DE'
					? 'flagpack:de'
					: 'flagpack:gb-ukm';
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
<Heading id="add-an-answer">Add an answer</Heading>

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
				placeholder={'Metadata JSON, e.g. {"course":"dev2","year":2023,"number": 42}'}
				class="input mb-2 w-full"
			/>
			{#if metadataError}
				<div class="label text-error mb-2">{metadataError}</div>
			{/if}

			<!-- <div class="flex items-end gap-3 "> -->
			{#if messageSocketio?.pendingEntities[0]}
				<textarea
					class="textarea w-full border border-2 p-2 shadow-inner placeholder:italic"
					rows="8"
					placeholder="Add an answer here. Use Enter for a new line."
					id="sharing"
					bind:value={messageSocketio.pendingEntities[0].content}></textarea>
			{:else}
				<div class="label text-error">
					<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
				</div>
			{/if}
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
	<!-- <JsonData data={messageSocketio?.getSelectedEntities('sortedMessageAnswers')} /> -->
</div>

<Heading id="message-answers">Message Answers:</Heading>

{#if messageSocketio?.pendingEntities[0]}
	<Card
		id="add-questions"
		title="Add Questions"
		closeButton
		extraClasses="label-large"
		bind:hidden={hideNewMessageAnswerCard}
	>
		<!-- <p class="label">
		{@render warning()} Add questions with tabs for new and existing, where the existing questions get
		the button to copy and link. Also a copy all selected and link all selected.
	</p> -->
		<div class="bg-base-150 shadow-base-shadow overflow-y-auto rounded-lg shadow-inner">
			<div
				class="tabs tabs-lifted tabs-secondary m-1"
				// class="tabs tabs-lifted to-secondary m-1 rounded-lg bg-linear-to-b from-transparent"
				// class="tabs tabs-lifted to-secondary m-1 bg-linear-to-b from-transparent"
				aria-label="Tabs"
				role="tablist"
				aria-orientation="horizontal"
				{@attach initTabs}
			>
				<button
					type="button"
					// class="tab tab-secondary active w-full"
					class="tab active w-full"
					id="new-question-head"
					data-tab="#new-question-tab"
					aria-controls="new-question-tab"
					role="tab"
					aria-selected="true"
				>
					<span class="icon-[fa6-solid--plus] mr-2 size-4"></span>
					<span class="hidden md:inline">Add</span>
					<span class="hidden sm:inline">&nbsp;new</span>
				</button>
				<button
					type="button"
					// class="tab tab-secondary w-full"
					class="tab w-full"
					id="existing-question-head"
					data-tab="#existing-question-tab"
					aria-controls="existing-question-tab"
					role="tab"
					aria-selected="false"
				>
					<span class="icon-[tabler--copy] mr-2 size-4"></span>
					<span class="hidden md:inline">Copy </span>
					&nbsp;or&nbsp;
					<span class="icon-[tabler--link] mx-2 size-4"></span>
					<span class="hidden md:inline">link </span>
					<span class="hidden sm:inline">&nbsp;existing</span>
				</button>
			</div>
			<div class="h-fit p-2">
				<!--
				<div
					id="new-question-tab"
					class="h-full max-h-120 overflow-scroll"
					role="tabpanel"
					aria-labelledby="new-question-head"
				>
					<div class="label">
						{@render warning()} Forms to add new questions, with the ability to add multiple questions
						at once and inherit access rights - default: true - from presentation.
					</div>
					 {#snippet labelDescription()}
						This label is the way to identify this particular quesion in the code of the
						presentation. It is mandatory.
					{/snippet}
					<FormElement
						title="Label"
						mandatory
						description={labelDescription}
						extraClasses="max-w-300"
					>
						<div class="input-filled input-primary w-full">
							<input
								type="text"
								placeholder=""
								class="input"
								id="slugInput"
								bind:value={socketioQuestions.pendingEntities[0].question}
							/>
							<label class="input-filled-label" for="slugInput"
								>[use this label to identify the question in your presentation]{newSuffix}</label
							>
						</div>
					</FormElement>
					{#snippet languageDescription()}
						Giving the language of the question text in the code. To allow automatic translation the
						algorithm needs to know from what language to translate into all the others, so this is
						the language of the source.
					{/snippet}
					<FormElement title="Language" description={languageDescription} extraClasses="max-w-300">
						<div class="label">
							{@render warning()} A drop-down field to select the language for the question, with a default
							value of the presentation's language.
						</div>
					</FormElement>
					{#snippet accessDescription()}
						Who has which access to this presentation?
						<br />
						Default is public <span class="icon-[gis--globe-earth-alt] size-4"></span>
						and have read
						<span
							class={`${AccessHandler.rightsIcon(Action.READ)} ${AccessHandler.rightsIconColor(Action.READ)} size-4`}
						></span>
						access.
					{/snippet}
					<FormElement title="Access" description={accessDescription} extraClasses="max-w-130">
						<div class="label mb-2 flex flex-1 items-center gap-1">
							<label class="label label-text text-base-content" for="new-question-inherit">
								<input
									id="new-question-inherit"
									type="checkbox"
									class="checkbox checkbox-primary"
									bind:checked={inheritPending}
								/>
							</label>
							inherit from {parentId}
						</div>
						<ul class="bg-base-150 shadow-base-shadow overflow-y-auto rounded-lg p-2 shadow-inner">
							{#each shareOptionsForNewQuestion, i (i)}
								<ShareItem
									// TBD: adopt for multiple new!
									resourceId={socketioQuestions.pendingEntities[0].id}
									// No need to bind, as it is anyways handled through the entityContainer's methods and the socketio's submitEntity method.
									shareOption={shareOptionsForNewQuestion[i]}
									socketio={socketioQuestions}
									actions={[Action.OWN, Action.WRITE, Action.CONNECT, Action.READ, undefined]}
									// share={socketioQuestions?.shareEntity.bind(socketioQuestions)}
									wide
								/>
							{/each}
						</ul>
					</FormElement>
					<FormElement title="Add multiple questions">
						<div class="mb-2 flex flex-1 flex-row items-center gap-1">
							<label class="label label-text text-base-content" for="new-question-multiple">
								<input
									id="new-question-multiple"
									type="checkbox"
									disabled
									// TBD: remove disabled, when functionality is implemented!
									class="checkbox checkbox-primary"
									bind:checked={multiplePending}
								/>
							</label>
							with suffixes
							<input
								id="multiple-groups-start"
								type="number"
								placeholder={multipleSuffixes.start.toString()}
								class="input shadow-shadow flex-2 shadow-inner"
								name="multiple-groups-suffix-start"
								disabled={!multiplePending}
								bind:value={multipleSuffixes.start}
							/>
							<span class="label flex-1"> to</span>
							<input
								id="multiple-groups-end"
								type="number"
								placeholder={multipleSuffixes.end.toString()}
								class="input shadow-shadow flex-2 shadow-inner"
								name="multiple-groups-suffix-end"
								disabled={!multiplePending}
								bind:value={multipleSuffixes.end}
							/>
						</div>
						<div class="label">
							{@render warning()} Creation of multiple not functional yet
						</div>
					</FormElement> 
				</div> -->
				<!-- <div
					id="existing-question-tab"
					class="hidden h-full max-h-100 overflow-scroll"
					role="tabpanel"
					aria-labelledby="existing-question-head"
				>
					<div class="label">
						{@render warning()} Table of existing questions and functionality to link or copy them into
						this presentation.
					</div>
					{#each notLinkedQuestions as linkedQuestion, idx (idx)}
						<div class="linked-question">
							<p>Q: {linkedQuestion.question}</p>
						</div>
					{/each}
				</div> -->
			</div>
		</div>
		{#snippet footer()}
			<div class="ml-5 flex flex-row justify-end gap-4">
				<button
					class="btn btn-secondary-container btn-gradient shadow-outline rounded-full shadow"
					aria-label="Cancel"
					onclick={() => {
						hideNewMessageAnswerCard = true;
					}}><span class="icon-[tabler--x] size-5"></span>Cancel</button
				>
				<!-- <button
					class="btn btn-primary-container btn-gradient shadow-outline rounded-full shadow"
					aria-label="Save new presentation"
					onclick={() => {
						messageSocketio.submitBulk(parentId, inheritPending);
						hideNewMessageAnswerCard = true;
						// For buld submit the new pending needs manual creation:
						messageSocketio.createPending();
					}}><span class="icon-[tabler--send-2] size-5"></span>
					Save
				</button> -->
			</div>
		{/snippet}
	</Card>
{:else if !messageSocketio?.pendingEntities[0] && !hideNewMessageAnswerCard}
	<div class="label text-error" transition:slide={{ duration: 600 }}>
		<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
	</div>
{/if}

<Card id="linked-messages" title="Linked message (text) answers" extraClasses="label-large">
	{#snippet header()}
		<div class="flex justify-between">
			<Title id="existingQuestions" class="grow">Overview</Title>
			<div class="flex flex-row items-center justify-center">
				{#if hideNewMessageAnswerCard || !messageSocketio?.pendingEntities[0]}
					<button
						transition:fade={{ duration: 600 }}
						class="btn btn-primary-container btn-gradient label btn shadow-outline mx-4 rounded-full shadow-sm"
						aria-label="Add new question"
						onclick={() => (hideNewMessageAnswerCard = false)}
					>
						<!-- onclick={() => goto(resolve('/(layout)/presentation/(protected)/setup/new'))} -->
						<span class="icon-[fa6-solid--plus] size-5"></span>
						<!-- <span class="hidden ">Add</span> -->
						<span class="hidden sm:inline">Add new</span>
						<span class="hidden md:inline">message</span>
					</button>
				{/if}
				<div class="join shadow-outline rounded-full shadow-sm">
					<button
						aria-label="Grid"
						class="btn join-item btn-secondary btn-gradient btn-sm shadow-outline rounded-l-full py-4 shadow {messageViewMode !==
						'grid'
							? 'opacity-60'
							: ''}"
						onclick={() => (messageViewMode = 'grid')}
					>
						<span class="icon-[gridicons--grid] size-5"></span>
					</button>
					<button
						aria-label="List"
						class="btn join-item btn-secondary btn-gradient btn-sm shadow-outline py-4 shadow {messageViewMode !==
						'list'
							? 'opacity-60'
							: ''}"
						onclick={() => (messageViewMode = 'list')}
					>
						<span class="icon-[material-symbols--view-list-outline] size-5"></span>
					</button>
					<button
						aria-label="Table"
						class="btn join-item btn-secondary btn-gradient btn-sm shadow-outline rounded-r-full py-4 shadow {messageViewMode !==
						'table'
							? 'opacity-60'
							: ''}"
						onclick={() => (messageViewMode = 'table')}
					>
						<span class="icon-[material-symbols--table-outline] size-5"></span>
					</button>
				</div>
			</div>
		</div>
	{/snippet}
	<div class="w-full overflow-x-auto {messageViewMode !== 'grid' ? 'hidden' : ''}">
		<p class="bg-warning text-warning-content rounded-lg p-4">
			Grid view mode is not developed yet
		</p>
	</div>
	<div class="w-full overflow-x-auto {messageViewMode !== 'list' ? 'hidden' : ''}">
		<p class="bg-warning text-warning-content rounded-lg p-4">
			List view mode is not developed yet
		</p>
	</div>
	<div class="w-full overflow-x-auto {messageViewMode !== 'table' ? 'hidden' : ''}">
		{#snippet languageCell(message: MessageExtended)}
			<Icon icon={flag(message.language)} class="size-5" inline />
		{/snippet}
		<!-- TBD: move ActionButtons to components -->
		{#snippet messageActionsCell(answer: MessageExtended)}
			<ActionButtons
				resourceId={answer.id}
				accessRight={messageSocketio?.accessRights[answer.id]}
				socketio={messageSocketio}
			/>
		{/snippet}
		<Table
			columns={[
				{
					header: text('Content'),
					cell: field<MessageExtended>('content'),
					headerClass: 'w-3/5',
					cellClass: 'max-w-0'
				},
				{
					header: icon('tabler:language'),
					cell: snippet(languageCell),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: text('Access'),
					cell: value(() => '[Access]'),
					headerClass: 'text-center',
					cellClass: 'text-center'
				},
				{
					header: text('Actions'),
					cell: snippet(messageActionsCell),
					headerClass: 'w-px text-center whitespace-nowrap',
					cellClass: 'w-px py-1 text-center align-middle whitespace-nowrap'
				}
			] satisfies TableColumn<MessageExtended>[]}
			entityContainer={messageSocketio}
			displaySelection="sortedMessageAnswers"
		/>
	</div>
</Card>

<!-- <div class="mx-2 grid w-full grid-cols-5 gap-2">
	{#each messageAnswersSorted as answer, index (answer.id)}
		<div animate:flip={{ duration: 300 }}>
			{@render answerBubble(answer.content, answer.id, index)}
		</div>
	{/each}
</div> -->

<Heading id="numerical-answers">Numerical Answers:</Heading>

<div class="mx-2 grid w-full grid-cols-5 gap-2">
	{#each numericalAnswersSorted as answer, index (answer.id)}
		<div animate:flip={{ duration: 300 }}>
			{@render answerBubble(answer.value, answer.id, index)}
		</div>
	{/each}
</div>

<Heading id="json-data">JSONdata:</Heading>

<div class="grid grid-cols-3">
	<div>
		<Title id="debug-server-data">Server Data</Title>
		<JsonData data={data.questionsData} />
	</div>
	<div>
		<Title id="debug-socketio-messages">SocketIO Messages</Title>
		<JsonData data={messageSocketio?.entities} />
	</div>
	<div>
		<Title id="debug-socketio-numericals">SocketIO Numericals</Title>
		<JsonData data={numericalSocketio?.entities} />
	</div>
</div>
