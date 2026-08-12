<script lang="ts">
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';
	import Section from '$components/Section.svelte';
	import Title from '$components/Title.svelte';

	import Loreum from '../../Loreum.svelte';
</script>

<div class="bg-accent-container/70 rounded-xl p-4">
	<Display>Page 5</Display>

	<p>Page 5 has hierarchial contnent and id's which are linked in main sidebar - same as page2</p>

	<Section id="loreum1">
		<Heading id="loreum1heading"
			><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum />
	</Section>

	<Section id="loreum2">
		<Heading id="loreum2heading"
			><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum />
	</Section>
	<Heading id="sub-categoryheading">Sub Category</Heading>

	<Section id="loreum3">
		<Title id="loreum3title"><span class="italic">Third</span> Lorem ipsum dolor sit amet...</Title>
		<Loreum />
	</Section>

	<Section id="loreum4">
		<Title id="loreum4title"><span class="italic">Fourth</span> Lorem ipsum dolor sit amet...</Title
		>
		<Loreum />
	</Section>

	<Section id="loreum5">
		<Heading id="loreum5heading"
			><span class="italic">Fifth</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum />
	</Section>

	<Section id="loreum6">
		<Heading id="loreum6heading"
			><span class="italic">Sixth</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum />
	</Section>
</div>
