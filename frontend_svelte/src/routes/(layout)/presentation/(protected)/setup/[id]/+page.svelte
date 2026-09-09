<script lang="ts">
	import { onDestroy, onMount } from 'svelte';

	import { page } from '$app/state';
	import Card from '$components/Card.svelte';
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';
	import JsonData from '$components/JsonData.svelte';
	import Title from '$components/Title.svelte';
	import { SocketIO } from '$lib/socketio.svelte';
	import type { Presentation } from '$lib/types';

	import type { PageData } from './$types';
	import QuestionSection from './QuestionsSection.svelte';

	let { data }: { data: PageData } = $props();

	let debug = $derived(page.url.searchParams.get('debug') === 'true' ? true : false);

	$effect(() => {
		debug = page.url.searchParams.get('debug') === 'true';
	});

	let socketioPresentation: SocketIO<Presentation> = $state()!;
	// TBD: should presentations really return the get_all in the callback,
	// or should it be controllable through resource_id's and / or other query parameters?
	let presentation = $derived(
		socketioPresentation?.entities.filter((entity) => entity.id === page.params.id)[0]
	);
	onMount(() => {
		socketioPresentation = new SocketIO<Presentation>(
			{
				namespace: '/presentation',
				sessionId: page.data?.session?.sessionId || '',
				queryParams: { 'request-access-data': true }
			},
			{
				snapshot: {
					entities: [data.payload.presentation],
					cursor: data.payload.cursor
				}
			}
		);
	});
	onDestroy(() => {
		socketioPresentation?.client.disconnect();
	});
</script>

<!-- <JsonData data={socketioPresentation?.entities} /> -->

<Display id="presentation-name">{presentation?.path || presentation?.id}</Display>
<div class="flex flex-col gap-2 md:flex-row">
	<a
		href="/presentation/setup"
		class="btn btn-primary btn-gradient shadow-outline mx-4 rounded-full"
	>
		<span class="icon-[tabler--chevron-left]"></span>
		Go to all presentations
	</a>
	<div class="label text-warning">
		Maybe this should be left to the sidebar? Potentially with the dropdown from the sidebar open to
		quickly allow access to all presentations link?
	</div>
</div>

<Card
	id="presentation-parameters"
	title="🚧 This presentation's parameters 🚧"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	<p>
		Pretty much the same as all the parameters when adding a new presentation in the all
		presentations setup view. Here all fields are pre-filled with this presentation's parameters.
	</p>
	<p>
		Add a little accordion/dropdown (by default hidden) copy-and-paste-able command for testing the
		loading of this presentation, is user is Admin, for example:
		<code
			>bun run test:stage:load -- --users=200 --hold=30 /numerical,(uuid) /message,(uuid),data
			/message,(uuid),data</code
		>
	</p>
</Card>

<Heading id="source" sideBarEntry="Source">Source</Heading>
<Card
	id="code-location"
	title="🚧 Code location for this presentation 🚧"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	<p>
		A card to set the source of the code for the presentation, like "intern", "github", which
		branch, and or commit, and so on
	</p>
</Card>

<Heading id="access" sideBarEntry="Access">Access</Heading>
<Card
	id="managing-access"
	title="🚧 Managing the accessibility of the presentation 🚧"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	<p>
		Setting the access for the presentation, like "public", "private", "shared with specific users
		or groups", that is access policies.
	</p>
</Card>

<Heading id="questions" sideBarEntry="Questions">Questions</Heading>
<QuestionSection
	parentId={page.params.id}
	questions={data.payload.questions}
	cursor={data.payload.cursor}
	identities={data.payload.identities}
/>

<Heading id="links" sideBarEntry="Links">Links</Heading>
<Card
	id="link-checking"
	title="🚧 Status of links 🚧"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	<p>
		Links, that are under continuous check for 200 responses that are used inside the presentation
		and marking them, if they are broken or not. Can also open a side drawer for managing existing
		links.
	</p>
</Card>

<Heading id="drawings" sideBarEntry="Drawings?">Drawings?</Heading>
<Card
	id="drawings"
	title="🚧 Draw.io and Excalibut embedded here 🚧"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	<p class="title text-center">
		Draw.io and Excalibur, that are linked and used inside the presentation. Add anew, modify linked
		or open side drawer for linking / copying existing. Maybe work with templates?
	</p>
</Card>

<Heading id="files" sideBarEntry="Files">Files</Heading>
<Card
	id="attaching-files"
	title="🚧 Uploading, updating, deleting files🚧"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	<p class="title text-center">
		The files are referenced in the presentation for example for embedding images, videos,
		backgrounds, code, and anything else. Can also open a side drawer for managing existing files.
	</p>
</Card>

<Heading id="misc" sideBarEntry="Miscellaneous">Miscellaneous</Heading>
<Card
	id="languages"
	title="🚧 Languages 🚧"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	Setting the original language(s) of the presentation and enabling auto-translate. Potentially
	manual override for errors in automatic translation?
</Card>
<Card
	id="ai-activation"
	title="🚧 AI Activation 🚧"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	Allowing AI inside the presentation, set the models, skills, model context protocol (MCP),
	retrieval augmented generation (RAG), temperature and so on
</Card>
<Card
	id="other-settings"
	title="🚧 Other Settings 🚧"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	Whatever might be missing for now?
</Card>

{#if debug}
	<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
		<div>
			<Title id="pendingEntities">Presentation</Title>
			<JsonData data={presentation ?? {}} />
		</div>
		<div>
			<Title id="identities">Identities</Title>
			<JsonData data={data.payload.identities ?? []} />
		</div>
	</div>
{/if}
