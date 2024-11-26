<script lang="ts">
	import JsonData from '$components/JsonData.svelte';
	import Title from '$components/Title.svelte';
	import type { PageData } from '../$types';
	// export let user: PageData;
	let { data }: { data: PageData } = $props();
	const user = data.user;
</script>

<Title>Page</Title>
<JsonData data={user} />
