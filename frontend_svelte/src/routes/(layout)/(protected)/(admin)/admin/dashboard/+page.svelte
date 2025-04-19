<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	const apiLink = data.body;
</script>

<Heading>Admin dashboard</Heading>

<h3 class="text-primary mt-0 mb-2 text-3xl leading-tight font-medium">
	Update environmental variables
</h3>

<form method="POST">
	<button data-sveltekit-preload-data="false">Now</button>
</form>

<h3 class="text-primary mt-0 mb-2 text-3xl leading-tight font-medium">API Documentation Backend</h3>
<a
	href={apiLink}
	class="hover:text-primary-600 focus:text-primary-600 active:text-primary-700 dark:text-primary-400 dark:hover:text-primary-500 dark:focus:text-primary-500 dark:active:text-primary-600 text-primary transition duration-150 ease-in-out"
	>Link</a
>
