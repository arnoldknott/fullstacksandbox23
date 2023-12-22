<script lang="ts">
	import { count } from '$lib/stores';

	const add = () => {
		count.update((n) => n + 1);
	};
	const subtract = () => {
		count.update((n) => n - 1);
	};
	const reset = () => {
		count.set(0);
	};
</script>

<p class="m-10 text-8xl">{$count}</p>
<br />
<button class="m-4 bg-blue-400 p-2" on:click={add}>+</button>
<button class="m-4 bg-blue-400 p-2" on:click={subtract}>-</button>
<button class="m-4 bg-blue-400 p-2" on:click={reset}>reset</button>
