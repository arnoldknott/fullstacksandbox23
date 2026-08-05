<script lang="ts">
	import { onDestroy, onMount } from 'svelte';

	import { page } from '$app/state';
	import Card from '$components/Card.svelte';
	import Display from '$components/Display.svelte';
	import Drawer from '$components/Drawer.svelte';
	import Heading from '$components/Heading.svelte';
	// import JsonData from '$components/JsonData.svelte';
	import { SocketIO, type SocketioConnection } from '$lib/socketio.svelte';
	import type { Presentation } from '$lib/types';

	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	let socketioPresentation: SocketIO<Presentation> = $state()!;
	let presentation = $derived(
		socketioPresentation?.entities.filter((entity) => entity.id === page.params.id)[0]
	);
	const socketioPresentationConnection: SocketioConnection = {
		namespace: '/presentation',
		sessionId: page.data.session.sessionId,
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

<Display id="presentation">Presentation</Display>
<Heading id="presentation-title">{presentation?.path || presentation?.id}</Heading>

<Card
	id="source"
	title="Source"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	<p>
		A card to set the source of the code for the presentation, like "intern", "github", which
		branch, and or commit, and so on
	</p>
</Card>

<Card
	id="access"
	title="Access"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	<p>
		Setting the access for the presentation, like "public", "private", "shared with specific users
		or groups", that is access policies.
	</p>
</Card>
<Card id="questions" title="Questions" extraClasses="label-large">
	<p>
		Linked questions. Adding a question and opening sidebar to select existing questions - for mode
		copy (don't keep the original answers and don't keep in sync) or link (keeps answers in sync)
	</p>
	<Drawer id="copy-questions" title="Copy Questions">
		<p class="title text-center">
			Opening a side drawer to select existing questions - for mode copy (don't keep the original
			answers and don't keep in sync)
		</p>
	</Drawer>
	<Drawer id="link-questions" title="Link Questions">
		<p class="title text-center">
			Opening a side drawer to select existing questions - for mode link (keeps answers in sync)
		</p>
	</Drawer>
</Card>
<Card
	id="links"
	title="Links"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	<p>
		Links, that are under continuous check for 200 responses that are used inside the presentation.
	</p>
</Card>
<Card
	id="drawings"
	title="(Drawings)"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	<p class="title text-center">
		Draw.io and Excalibur, that are linked and used inside the presentation. Add anew, modify linked
		or open side drawer for linking / copying existing. Maybe work with templates?
	</p>
</Card>
<Card
	id="files"
	title="Files"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	<p class="title text-center">
		Uploading, updating, deleting files, that are referenced in the presentation. Can also open a
		side drawer for managing existing files.
	</p>
</Card>
<Card
	id="misc"
	title="Miscellaneous"
	extraClasses="bg-warning-container/30 text-warning-container-content/80 label-large border-warning-container"
>
	(Maybe languages?, AI activation?, ...)
</Card>
