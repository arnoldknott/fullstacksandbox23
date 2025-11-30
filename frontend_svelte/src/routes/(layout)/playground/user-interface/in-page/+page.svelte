<script lang="ts">
	import Display from '$components/Display.svelte';
	import NavigationCard from '$components/NavigationCard.svelte';
</script>

<Display>Page A</Display>

<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
	<NavigationCard title="Subpage 1" href="in-page/subpage1">Go to subpage 1</NavigationCard>
	<NavigationCard title="Subpage 2" href="in-page/subpage2">Go to subpage 2</NavigationCard>
	<div class="divider md:col-span-2"></div>
	<NavigationCard title="Subpage 1" href="in-page/subpage1#loreum1"
		>Go to subpage 1 - Loreum1</NavigationCard
	>
	<NavigationCard title="Subpage 2" href="in-page/subpage2#loreum1"
		>Go to subpage 2 - Loreum1</NavigationCard
	>
	<NavigationCard title="Subpage 1" href="in-page/subpage1#loreum2"
		>Go to subpage 1 - Loreum2</NavigationCard
	>
	<NavigationCard title="Subpage 2" href="in-page/subpage2#loreum2"
		>Go to subpage 2 - Loreum2</NavigationCard
	>
</div>
