<script lang="ts">
	import Title from '$components/Title.svelte';
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../Loreum.svelte';
	import Display from '$components/Display.svelte';
	import Section from '$components/Section.svelte';
</script>

<div class="bg-accent-container/70 rounded-xl p-4">
	<Display>Page 5</Display>

	<p>Page 5 has hierarchial contnent and id's which are linked in main sidebar - same as page2</p>

	<Section id="loreum1">
		<Heading><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading>
		<Loreum />
	</Section>

	<Section id="loreum2">
		<Heading><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading>
		<Loreum />
	</Section>
	<Heading id="sub-category">Sub Category</Heading>

	<Section id="loreum3">
		<Title id="loreum3"><span class="italic">Third</span> Lorem ipsum dolor sit amet...</Title>
		<Loreum />
	</Section>

	<Section id="loreum4">
		<Title id="loreum4"><span class="italic">Fourth</span> Lorem ipsum dolor sit amet...</Title>
		<Loreum />
	</Section>

	<Section id="loreum5">
		<Heading id="loreum5"><span class="italic">Fifth</span> Lorem ipsum dolor sit amet...</Heading>
		<Loreum />
	</Section>

	<Section id="loreum6">
		<Heading><span class="italic">Sixth</span> Lorem ipsum dolor sit amet...</Heading>
		<Loreum />
	</Section>
</div>
