<script lang="ts">
	// /** @type {import('./$types').PageData} */
	import Title from '$components/Title.svelte';
	import type { PageData } from './$types';
	export let data: PageData;
	const schema = data.body;
</script>

<div class="mx-5">
	<Title>Getting schema from backend</Title>
</div>

<code><pre>{JSON.stringify(schema, null, ' ')}</pre></code>
