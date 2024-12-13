<script lang="ts">
	import Title from '$components/Title.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	const apiLink = data.body;
</script>

<Title>Admin dashboard</Title>

<h3 class="mb-2 mt-0 text-3xl font-medium leading-tight text-primary">
	Update environmental variables
</h3>

<form method="POST">
	<button data-sveltekit-preload-data="false">Now</button>
</form>

<h3 class="mb-2 mt-0 text-3xl font-medium leading-tight text-primary">API Documentation Backend</h3>
<a
	href={apiLink}
	class="hover:text-primary-600 focus:text-primary-600 active:text-primary-700 dark:text-primary-400 dark:hover:text-primary-500 dark:focus:text-primary-500 dark:active:text-primary-600 text-primary transition duration-150 ease-in-out"
	>Link</a
>
