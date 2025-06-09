<script lang="ts">
	import JsonData from '$components/JsonData.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	console.log('=== playground - dataflow - +page.svelte ===');
	console.log(data); // { layoutServerTs: 1, layout.ts: 2, pageserverTs: 3  }
</script>

<div>
	+page.svelte
	<JsonData {data} />
</div>
