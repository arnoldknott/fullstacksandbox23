<script module lang="ts">
	import type { PresentationExtended } from '$lib/types';

	export const normalizePresentationPath = (presentation: PresentationExtended) => {
		const newPath = presentation.path?.trim() ?? '';
		presentation.path = newPath && !newPath.startsWith('/') ? `/${newPath}` : newPath;
	};
</script>

<script lang="ts">
	import { page } from '$app/state';
	import FormElement from '$components/FormElement.svelte';
	import ShareItem from '$components/ShareItem.svelte';
	import { AccessHandler, Action } from '$lib/accessHandler';
	import type { SocketIO } from '$lib/socketio.svelte';
	import type { AccessShareOption } from '$lib/types';

	import IdBadge from '../../../(protected)/IdBadge.svelte';

	let {
		presentation,
		shareOptions,
		socketio
	}: {
		presentation: PresentationExtended;
		shareOptions: AccessShareOption[];
		socketio: SocketIO<PresentationExtended>;
	} = $props();
</script>

{#snippet warning()}
	<span class="icon-[fluent-color--warning-24] size-4"></span>
{/snippet}

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
				Where is the source code for this presentation stored? For example, intern - as part of the
				source code of this platform - a github or gitlab repository. <span class="text-accent"
					>Consider adding the option for a staging environemnt.</span
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
			going through the presentation. Linking exisiting questions, also links their answers, copying existing
			questions creates a new question without any answers.
		</FormElement>
		<FormElement title="Links" extraClasses="max-w-300">
			{@render warning()} Maybe there's a need to add related links and / or embeddings. The service to
			the user could be to check the aliveness of the links - if a link returns a 404, the user gets a
			notification.
		</FormElement>
		<FormElement title="Files" extraClasses="max-w-300">
			{@render warning()} Select existing files or drop new files into a container to upload and make
			available to the presentation. This is the place to store binaries, so they can be accessed via
			the presentation api and used in the presentation.
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
				<ShareItem resourceId={presentation.id} shareOption={shareOptions[i]} {socketio} wide />
			{/each}
		</ul>
	</FormElement>
</div>
