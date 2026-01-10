<script lang="ts">
	import Title from '$components/Title.svelte';
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../Loreum.svelte';
	import Display from '$components/Display.svelte';
	import Section from '$components/Section.svelte';
</script>

<div class="bg-warning-container/70 rounded-xl p-4">
	<Display>Page 2</Display>

	<p>Page 2 has hierarchial content and id's linked in main sidebar</p>

	<!-- <Heading id="pg2loreum1"><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum />

	<Heading id="pg2loreum2"><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading
	>
	<Loreum />

	<Heading id="pg2sub-category">Sub Category</Heading>

	<Title id="pg2loreum3"><span class="italic">Third</span> Lorem ipsum dolor sit amet...</Title>
	<Loreum />

	<Title id="pg2loreum4"><span class="italic">Fourth</span> Lorem ipsum dolor sit amet...</Title>
	<Loreum />

	<Heading id="pg2loreum5"><span class="italic">Fifth</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum />

	<Heading id="pg2loreum6"><span class="italic">Sixth</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum repetition={20} /> -->

	<Section id="pg2loreum1">
		{#snippet header()}
			<Heading>
				<span class="italic">First</span> Lorem ipsum dolor sit amet...
			</Heading>
		{/snippet}
		<Loreum />
	</Section>

	<Section id="pg2loreum2">
		{#snippet header()}
			<Heading>
				<span class="italic">Second</span> Lorem ipsum dolor sit amet...
			</Heading>
		{/snippet}
		<Loreum repetition={4} />
	</Section>

	<Section id="pg2sub-category">
		<Heading>Sub Category</Heading>
	</Section>

	<Section id="pg2loreum3">
		{#snippet header()}
			<Title id="pg2loreum3title">
				<span class="italic">Third</span> Lorem ipsum dolor sit amet...
			</Title>
		{/snippet}
		<Loreum />
	</Section>

	<Section id="pg2loreum4">
		{#snippet header()}
			<Title id="pg2loreum4title">
				<span class="italic">Fourth</span> Lorem ipsum dolor sit amet...
			</Title>
		{/snippet}
		<Loreum />
	</Section>

	<Section id="pg2loreum5">
		{#snippet header()}
			<Heading id="pg2loreum5title">
				<span class="italic">Fifth</span> Lorem ipsum dolor sit amet...
			</Heading>
		{/snippet}
		<Loreum />
	</Section>

	<Section id="pg2loreum6">
		{#snippet header()}
			<Heading id="pg2loreum6title">
				<span class="italic">Sixth</span> Lorem ipsum dolor sit amet...
			</Heading>
		{/snippet}
		<Loreum repetition={20} />
	</Section>
</div>
