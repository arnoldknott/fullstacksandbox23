<script lang="ts">
	export let url: string;
	export let link: string;
	export let invert: boolean = false;

	const formatButton = () => {
		if (invert) {
			return 'bg-white hover:bg-blue-700 text-blue-400 font-bold my-2 py-2 px-4 rounded border border-blue-400';
		} else {
			return 'bg-blue-400 hover:bg-blue-700 hover:text-white text-white font-bold my-2 py-2 px-4 rounded';
		}
	};
</script>

<a href={url}>
	<button type="button" class={formatButton()}>
		{link}
	</button>
</a>
