<script lang="ts">
    import JsonData from '$components/JsonData.svelte';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

    console.log('=== playground - dataflow - +layout.svelte ===');
    console.log(data);// { layoutServerTs: 1, layout.ts: 2, pageserverTs: 3  }
</script>

<div>
    +layout.svelte
    Data: <JsonData {data} />
    {@render children()}
</div>