<script lang="ts">
	import Icon from '@iconify/svelte';

	let { items }: { items: { icon: string; title: string }[] } = $props();
	$effect(() => {
		console.log(items);
	});
</script>

{#snippet itemLine(item: { icon: string; title: string })}
	<a href={`#${item.title.toLowerCase()}`} class="justify-self-end" aria-label={item.title}>
		<Icon icon={item.icon} class="text-primary" />
	</a>
	<a href={`#${item.title.toLowerCase()}`} aria-label={item.title}
		><div class="text-primary font-bold">{item.title}</div></a
	>
	<div></div>
{/snippet}

<div
	class="r-stretch my-50 grid grid-cols-[1fr_max-content_1fr] items-center justify-between justify-items-start gap-16 text-7xl"
>
	{#each items as item, index (index)}
		{@render itemLine(item)}
	{/each}
</div>
