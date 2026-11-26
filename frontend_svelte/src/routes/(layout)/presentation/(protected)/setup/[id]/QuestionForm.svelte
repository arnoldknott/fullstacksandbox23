<script lang="ts">
	import FormElement from '$components/FormElement.svelte';
	import FormMultipleSuffix from '$components/FormMultipleSuffix.svelte';
	import ShareItem from '$components/ShareItem.svelte';
	import { AccessHandler, Action } from '$lib/accessHandler';
	import type { SocketIO } from '$lib/socketio.svelte';
	import type { AccessShareOption, QuestionExtended } from '$lib/types';

	let {
		question,
		shareOptions,
		socketio,
		parentId,
		inheritPending = $bindable()
	}: {
		question: QuestionExtended;
		shareOptions: AccessShareOption[];
		socketio: SocketIO<QuestionExtended>;
		parentId?: string;
		inheritPending: boolean;
	} = $props();

	let suffix = $state('');
</script>

{#snippet warning()}
	<span class="icon-[fluent-color--warning-24] size-4"></span>
{/snippet}

<div class="label">
	{@render warning()} Forms to add new questions, with the ability to add multiple questions at once and
	inherit access rights - default: true - from presentation.
</div>
<FormElement title="Label" mandatory extraClasses="max-w-300">
	{#snippet description()}
		This label is the way to identify this particular quesion in the code of the presentation. It is
		mandatory.
	{/snippet}
	<div class="input-filled input-primary w-full">
		<input type="text" placeholder="" class="input" id="slugInput" bind:value={question.question} />
		<label class="input-filled-label" for="slugInput"
			>[use this label to identify the question in your presentation]{suffix}</label
		>
	</div>
</FormElement>
<FormElement title="Language" extraClasses="max-w-300">
	{#snippet description()}
		Giving the language of the question text in the code. To allow automatic translation the
		algorithm needs to know from what language to translate into all the others, so this is the
		language of the source.
	{/snippet}
	<div class="label">
		{@render warning()} A drop-down field to select the language for the question, with a default value
		of the presentation's language.
	</div>
</FormElement>
<FormElement title="Access" extraClasses="max-w-130">
	{#snippet description()}
		Who has which access to this question?
		<br />
		Default is public <span class="icon-[gis--globe-earth-alt] size-4"></span>
		and have read
		<span
			class={`${AccessHandler.rightsIcon(Action.READ)} ${AccessHandler.rightsIconColor(Action.READ)} size-4`}
		></span>
		access.
	{/snippet}
	{#if parentId}
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
	{/if}
	<ul class="bg-base-150 shadow-base-shadow overflow-y-auto rounded-lg p-2 shadow-inner">
		{#each shareOptions, i (i)}
			<ShareItem
				// TBD: adopt for multiple new!
				resourceId={question.id}
				// No need to bind, as it is anyways handled through the entityContainer's methods and the socketio's submitEntity method.
				shareOption={shareOptions[i]}
				{socketio}
				actions={[Action.OWN, Action.WRITE, Action.CONNECT, Action.READ, undefined]}
				// share={socketio?.shareEntity.bind(socketio)}
				wide
			/>
		{/each}
	</ul>
</FormElement>
<FormMultipleSuffix entityLabel="question" bind:suffix />
