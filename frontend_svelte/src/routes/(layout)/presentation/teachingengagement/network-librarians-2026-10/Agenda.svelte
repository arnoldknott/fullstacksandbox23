<script lang="ts">
	let { items }: { items: { part: string; icon: string; title: string }[] } = $props();
	console.log(items);
</script>

<div
	class="r-stretch my-50 grid grid-cols-[1fr_max-content_1fr] items-center justify-between justify-items-start gap-12 text-7xl"
	// class="r-stretch mx-auto my-20 grid w-fit grid-cols-[auto_max-content_auto] items-center gap-12 text-7xl"
>
	<a href="#motivation" class="justify-self-end" aria-label="Motivation"
		><span class="icon-[vaadin--thumbs-up-o] bg-primary"></span></a
	>
	<a href="#motivation" aria-label="Motivation"
		><div class="text-primary font-bold">Motivation</div></a
	>
	<div></div>
	<a href="#diversity" aria-label="Diversity" class="justify-self-end"
		><span class="icon-[material-symbols--diversity-1-rounded] bg-primary"></span></a
	>
	<a href="#diversity" aria-label="Diversity"><div class="text-primary font-bold">Diversity</div></a
	>
	<div></div>
	<a href="#overview" aria-label="Overview" class="justify-self-end"
		><span class="icon-[grommet-icons--overview] bg-primary"></span></a
	>
	<a href="#overview" aria-label="Overview"><div class="text-primary font-bold">Overview</div></a>
	<div></div>
</div>
