<script lang="ts">
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';

	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	const apiLink = $derived(data.payload);
</script>

<Display>Admin dashboard</Display>

<Heading id="env">Environment Variables</Heading>

<form method="POST">
	<button data-sveltekit-preload-data="false">Reread</button>
</form>

<Heading id="api-docs">REST-API Documentation Backend</Heading>
<a
	href={apiLink}
	class="hover:text-primary-600 focus:text-primary-600 active:text-primary-700 dark:text-primary-400 dark:hover:text-primary-500 dark:focus:text-primary-500 dark:active:text-primary-600 text-primary transition duration-150 ease-in-out"
	>Link</a
>
