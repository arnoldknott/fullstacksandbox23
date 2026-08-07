<script lang="ts">
	// /** @type {import('./$types').PageData} */
	import Heading from '$components/Heading.svelte';

	import type { PageData } from './$types';
	export let data: PageData;
	const schema = data.body;
</script>

<div class="mx-5">
	<Heading id="getting-schema-from-backend">Getting schema from backend</Heading>
</div>

<code><pre>{JSON.stringify(schema, null, ' ')}</pre></code>
