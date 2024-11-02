<script lang="ts">
	type Props = {
		url: string;
		link: string;
		invert?: boolean;
		pre_load?: boolean;
	};
	let { url, link, invert = false, pre_load = false }: Props = $props();

	/*
	// Typing props from https://github.com/sveltejs/svelte/issues/9241#issuecomment-2299188014
// 	<!-- Input.svelte -->
//   add script tags here!
//   type Props = { type: 'text'; value: string } | { type: 'number'; value: number };
//   let { type, value }: Props = $props();

// add script tags here!
//   import Input from './Input.svelte';

// <!-- cool -->
// <Input type="text" value="a string" />
// <Input type="number" value={42} />

// <!-- type error -->
// <Input type="number" value="a string" />
// <Input type="text" value={42} />
*/

	const formatButton = () => {
		if (invert) {
			return 'bg-white hover:bg-blue-700 text-blue-400 font-bold my-2 py-2 px-4 rounded border border-blue-400';
		} else {
			return 'bg-blue-400 hover:bg-blue-700 hover:text-white text-white font-bold my-2 py-2 px-4 rounded';
		}
	};
</script>

<a data-sveltekit-preload-data={pre_load} href={url}>
	<button type="button" class={formatButton()}>
		{link}
	</button>
</a>
