<script lang="ts">
	import ShareItem from '$components/ShareItem.svelte';
	import { AccessHandler, Action } from '$lib/accessHandler';
	import type { SocketIO } from '$lib/socketio.svelte';
	import type { AccessShareOption, QuestionExtended } from '$lib/types';

	import FormElement from '../FormElement.svelte';

	let {
		socketio,
		parentId,
		inheritPending = $bindable()
	}: {
		socketio: SocketIO<QuestionExtended>;
		parentId?: string;
		inheritPending: boolean;
	} = $props();

	let shareOptionsForNewQuestion: AccessShareOption[] = $derived(
		AccessHandler.createShareOptions(
			socketio.identities,
			socketio.accessPolicies[socketio.pendingEntities[0].id]
		) || []
	);

	let multiplePending = $state(false);
	let multipleSuffixes = $state({ start: 1, end: 2 });
	$effect(() => {
		if (multipleSuffixes.end <= multipleSuffixes.start) {
			multipleSuffixes.end = multipleSuffixes.start + 1;
		}
	});
	let newSuffix = $derived(
		multiplePending ? '_[' + multipleSuffixes.start + ':' + multipleSuffixes.end + ']' : null
	);
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
		<input
			type="text"
			placeholder=""
			class="input"
			id="slugInput"
			bind:value={socketio.pendingEntities[0].question}
		/>
		<label class="input-filled-label" for="slugInput"
			>[use this label to identify the question in your presentation]{newSuffix}</label
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
		{#each shareOptionsForNewQuestion, i (i)}
			<ShareItem
				// TBD: adopt for multiple new!
				resourceId={socketio.pendingEntities[0].id}
				// No need to bind, as it is anyways handled through the entityContainer's methods and the socketio's submitEntity method.
				shareOption={shareOptionsForNewQuestion[i]}
				{socketio}
				actions={[Action.OWN, Action.WRITE, Action.CONNECT, Action.READ, undefined]}
				// share={socketio?.shareEntity.bind(socketio)}
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
