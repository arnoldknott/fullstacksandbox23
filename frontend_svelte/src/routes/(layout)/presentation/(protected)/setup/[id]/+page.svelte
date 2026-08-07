<script lang="ts">
	import { onDestroy, onMount } from 'svelte';

	import { page } from '$app/state';
	import Card from '$components/Card.svelte';
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';
	// import JsonData from '$components/JsonData.svelte';
	import { SocketIO, type SocketioConnection } from '$lib/socketio.svelte';
	import type { Presentation } from '$lib/types';

	import type { PageData } from './$types';
	import QuestionDrawer from './QuestionDrawer.svelte';

	let { data }: { data: PageData } = $props();

	let socketioPresentation: SocketIO<Presentation> = $state()!;
	let presentation = $derived(
		socketioPresentation?.entities.filter((entity) => entity.id === page.params.id)[0]
	);
	const socketioPresentationConnection: SocketioConnection = {
		namespace: '/presentation',
		sessionId: page.data?.session?.sessionId || '',
		queryParams: { 'request-access-data': true }
	};
	onMount(() => {
		socketioPresentation = new SocketIO<Presentation>(socketioPresentationConnection);
	});
	$effect(() => {
		socketioPresentation.entities = [data.payload.presentation];
	});
	onDestroy(() => {
		socketioPresentation?.client.disconnect();
	});
</script>

<!-- <JsonData data={socketioPresentation?.entities} /> -->

<Display id="presentation-name">{presentation?.path || presentation?.id}</Display>
<a href="/presentation/setup" class="btn btn-primary btn-gradient shadow-outline mx-4 rounded-full">
	<span class="icon-[tabler--chevron-left]"></span>
	Go to all presentations
</a>

<Heading id="source">Source</Heading>
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

<Heading id="access">Access</Heading>
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

<Heading id="questions">Questions</Heading>
<QuestionDrawer />

<Card id="link-questions" title="Linked Questions" extraClasses="label-large">
	<p>
		Potentially as an accordion with the answers in the panel? Adding a question and opening sidebar
		to select existing questions - for mode copy (don't keep the original answers and don't keep in
		sync) or link (keeps answers in sync)
	</p>
</Card>

<Heading id="links">Links</Heading>
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

<Heading id="drawings">Drawings?</Heading>
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

<Heading id="files">Files</Heading>
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

<Heading id="misc">Miscellaneous</Heading>
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
