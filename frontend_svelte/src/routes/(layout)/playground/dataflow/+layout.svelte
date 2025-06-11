<script lang="ts">
	import JsonData from '$components/JsonData.svelte';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	console.log('=== playground - dataflow - +layout.svelte ===');
	const cleanedData = Object.fromEntries(
		Object.entries(data).filter(
			([key]) =>
				key.startsWith('layoutServerTs') ||
				key.startsWith('layoutTs') ||
				key.startsWith('pageServerTs') ||
				key.startsWith('pageTs')
		)
	);
	console.log(cleanedData); // { layoutServerTs: 1, layout.ts: 2  }
</script>

<div class="grid grid-cols-3 gap-2">
	<div>
		<p class="title">+layout.svelte</p>
		<JsonData data={cleanedData} />
	</div>
	{@render children()}
</div>
