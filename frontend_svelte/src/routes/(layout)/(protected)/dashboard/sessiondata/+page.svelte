<script lang="ts">
	import { goto } from '$app/navigation';
	import Heading from '$components/Heading.svelte';
	import JsonData from '$components/JsonData.svelte';
	import { page } from '$app/state';
	import HorizontalRule from '$components/HorizontalRule.svelte';
	import type { PageData } from './$types';
	import { onMount } from 'svelte';
	let { data }: { data: PageData } = $props();
	let navigatorData = $state<Record<string, any> | null>(null);

	onMount(() => {
		navigatorData = {
			userAgent: navigator.userAgent,
			language: navigator.language,
			languages: navigator.languages,
			onLine: navigator.onLine,
			platform: navigator.platform,
			cookieEnabled: navigator.cookieEnabled,
			hardwareConcurrency: navigator.hardwareConcurrency,
			maxTouchPoints: (navigator as any).maxTouchPoints
			// Add more if needed; keep only enumerable primitives/functions you care about
		};
	});
	const logSessionData = (data: object | undefined) => {
		console.log('=== routes - playground - sessiondata===');
		console.log(data);
	};
</script>

<div class="flex gap-2 py-4">
	<button
		class="btn btn-accent-container btn-gradient shadow-outline rounded-full shadow-sm"
		onclick={() => goto('#data-session')}
		><span class="icon-[tabler--chevron-right]"></span> data.session</button
	>
	<button
		class="btn btn-accent-container btn-gradient shadow-outline rounded-full shadow-sm"
		onclick={() => goto('#page')}><span class="icon-[tabler--chevron-right]"></span> page</button
	>
	<button
		class="btn btn-accent-container btn-gradient shadow-outline rounded-full shadow-sm"
		onclick={() => goto('#navigator')}
		><span class="icon-[tabler--chevron-right]"></span> navigator</button
	>
</div>

<button class="m-4 rounded-sm bg-blue-400 p-2" onclick={() => logSessionData(data.session)}
	>Current data.session -> console</button
>

<Heading id="data-session">data.session</Heading>
<JsonData data={data.session} />

<HorizontalRule />

<button class="m-4 rounded-sm bg-blue-400 p-2" onclick={() => logSessionData(page)}
	>Current page store -> console</button
>

<Heading id="page">Page</Heading>
<JsonData data={page} />

<HorizontalRule />

<button class="m-4 rounded-sm bg-blue-400 p-2" onclick={() => logSessionData(navigator)}
	>Current navigator -> console</button
>

<Heading id="navigator">navigator</Heading>
<JsonData data={navigatorData} />

<HorizontalRule />
