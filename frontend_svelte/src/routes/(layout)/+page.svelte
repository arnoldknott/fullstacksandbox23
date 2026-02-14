<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import JsonData from '$components/JsonData.svelte';
	import { page } from '$app/state';
	import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();
</script>

<div class="flex w-full justify-center">
	<div class="flex flex-col justify-center">
		<div class="heading-large md:display-small text-primary italic" style="line-height: 1;">
			Fullstack
		</div>
		<div
			class="heading-large text-secondary font-bold tracking-wide md:tracking-widest"
			style="line-height: 1"
		>
			Platform
		</div>
	</div>
	<div class="text-accent ml-3 flex items-center text-[116px]">23</div>
</div>

<Heading id="data-session">data.session</Heading>
<JsonData {data} />
