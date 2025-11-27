<script lang="ts">
	import Title from '$components/Title.svelte';
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../Loreum.svelte';
	import Display from '$components/Display.svelte';
	import NavigationCard from '$components/NavigationCard.svelte';
</script>

<div class="bg-info-container/70 rounded-xl p-4">
	<Display>Page 4</Display>

	<p>
		Page 4 has hierarchial content and id's which are linked in main sidebar as well as subpages
	</p>

	<Heading id="loreum1"><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum />

	<Heading id="loreum2"><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum />

	<Heading id="sub-category-page4">Sub Category</Heading>

	<Title id="loreum3"><span class="italic">Third</span> Lorem ipsum dolor sit amet...</Title>
	<Loreum />

	<Title id="loreum4"><span class="italic">Fourth</span> Lorem ipsum dolor sit amet...</Title>
	<Loreum />

	<Heading id="page4-sub-pages-section"
		><span class="italic">Subpages</span> linking to further content</Heading
	>
	<Loreum repetition={2} />
	<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
		<NavigationCard title="Page 4.1" href="./page4/page4-1">Go to Page 4.1</NavigationCard>
		<NavigationCard title="Page 4.2" href="./page4/page4-2">Go to Page 4.2</NavigationCard>
	</div>

	<Heading id="loreum6"><span class="italic">Sixth</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum />
</div>

<!-- TBD: add parameterized routes -->
