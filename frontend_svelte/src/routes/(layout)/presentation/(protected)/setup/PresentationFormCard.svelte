<script lang="ts">
	import { page } from '$app/state';
	import Card from '$components/Card.svelte';
	import { AccessHandler, Action } from '$lib/accessHandler';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { AccessShareOption, Presentation, PresentationExtended } from '$lib/types';

	import IdBadge from '../../../(protected)/IdBadge.svelte';
	import ShareItem from '../../../playground/components/ShareItem.svelte';
	import FormElement from './FormElement.svelte';
	let {
		socketio,
		presentationId = socketio.pendingEntities[0].id,
		hidden = $bindable()
	}: {
		socketio: SocketIO<PresentationExtended>;
		presentationId?: string;
		hidden: boolean;
	} = $props();

	let presentation: Presentation = $derived(
		presentationId === socketio.pendingEntities[0].id
			? socketio.pendingEntities[0]
			: socketio.entities.find((entity) => entity.id === presentationId)!
	);

	const submitPresentation = () => {
		const newPath = presentation.path?.trim() ?? '';
		presentation.path = newPath && !newPath.startsWith('/') ? `/${newPath}` : newPath;
		socketio.submitEntity(presentation);
		socketio.createPending();
		hidden = true;
	};

	// TBD: move this calculation to EntityContainer (or AccessHandler) class!
	// Is it moved already or shold the caller be simplified to a new caller:
	// entityContainer.shareOptions(presentationId)?
	let shareOptions: AccessShareOption[] = $derived(
		AccessHandler.createShareOptions(
			socketio.identities,
			socketio.accessPolicies[presentationId]
		) || []
	);
</script>

{#snippet warning()}
	<span class="icon-[fluent-color--warning-24] size-4"></span>
{/snippet}

<Card
	id={presentation.id}
	title={presentation.path ? presentation.path : 'New presentation'}
	closeButton
	bind:hidden
>
	<div class="flex w-full flex-wrap gap-6">
		<div class="grow">
			<FormElement title="Slug" extraClasses="w-full">
				{#snippet description()}
					This is the endpoint added for user access. It is not mandatory, as the presentation is
					always accessible via its id in place of the slug. <span class="text-accent"
						>Add a few words on allowed characters and uniqueness.</span
					>
				{/snippet}
				<div class="md:flex-cols-2 wrap flex gap-2">
					<code class="mt-5 shrink">{page.url.origin}/presentation/</code>
					<div class="input-filled input-primary w-full">
						<input
							type="text"
							placeholder=""
							class="input"
							id="slugInput"
							bind:value={presentation.path}
						/>
						<label class="input-filled-label" for="slugInput"
							>[add the path to your presentation here]</label
						>
					</div>
				</div>
			</FormElement>
			<FormElement title="Source" extraClasses="max-w-300">
				{#snippet description()}
					Where is the source code for this presentation stored? For example, intern - as part of
					the source code of this platform - a github or gitlab repository. <span
						class="text-accent">Consider adding the option for a staging environemnt.</span
					>
				{/snippet}
				{@render warning()} For now, all presentations are <IdBadge id="intern" />, e.g. hosted with
				the source code of this platform. ON the long run, <IdBadge id="Github" />, <IdBadge
					id="Gitlab"
				/>, <IdBadge id="OneDrive" />, <IdBadge id="GoogleDrive" /> and other sources should be supported
				as well.
			</FormElement>
			<FormElement title="Questions" extraClasses="max-w-300">
				{@render warning()} Link interactive questions to your presentation, so they can be answered while
				going through the presentation. Linking exisiting questions, also links their answers, copying
				existing questions creates a new question without any answers.
			</FormElement>
			<FormElement title="Links" extraClasses="max-w-300">
				{@render warning()} Maybe there's a need to add related links and / or embeddings. The service
				to the user could be to check the aliveness of the links - if a link returns a 404, the user gets
				a notification.
			</FormElement>
			<FormElement title="Files" extraClasses="max-w-300">
				{@render warning()}Select existing files or drop new files into a container to upload and
				make available to the presentation. This is the place to store binaries, so they can be
				accessed via the presentation api and used in the presentation.
			</FormElement>
		</div>

		<FormElement title="Access" extraClasses="max-w-100">
			{#snippet description()}
				Who has which access to this presentation?
				<br />
				Default is public <span class="icon-[gis--globe-earth-alt] size-4"></span>
				and have read
				<span
					class={`${AccessHandler.rightsIcon(Action.READ)} ${AccessHandler.rightsIconColor(Action.READ)} size-4`}
				></span>
				access.
			{/snippet}
			<ul class="bg-base-150 shadow-base-shadow overflow-y-auto rounded-lg p-2 shadow-inner">
				{#each shareOptions, i (i)}
					<ShareItem
						resourceId={presentationId}
						// No need to bind, as it is anyways handled through the entityContainer's methods and the socketio's submitEntity method.
						shareOption={shareOptions[i]}
						{socketio}
						// share={socketioPresentations?.shareEntity.bind(socketioPresentations)}
						wide
					/>
				{/each}
			</ul>
		</FormElement>
	</div>
	{#snippet footer()}
		<div class="ml-5 flex flex-row justify-end gap-4">
			<button
				class="btn btn-secondary-container btn-gradient shadow-outline rounded-full shadow"
				aria-label="Cancel"
				onclick={() => {
					hidden = true;
				}}><span class="icon-[tabler--x] size-5"></span>Cancel</button
			>
			<button
				class="btn btn-primary-container btn-gradient shadow-outline rounded-full shadow"
				aria-label="Save new presentation"
				onclick={() => submitPresentation()}
				><span class="icon-[tabler--send-2] size-5"></span>Save</button
			>
		</div>
	{/snippet}
</Card>
