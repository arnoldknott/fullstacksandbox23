<script lang="ts">
	// /** @type {import('./$types').PageData} */
	import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();
	const schema = data.schema;
</script>

<div class="mx-5">
	<h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">
		Return from on_behalf_of:
	</h1>
</div>

<code><pre>{JSON.stringify(schema, null, ' ')}</pre></code>
