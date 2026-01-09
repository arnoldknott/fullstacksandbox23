<script lang="ts">
	import Title from '$components/Title.svelte';
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../Loreum.svelte';
	import Display from '$components/Display.svelte';
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

	<div id="pg2loreum1">
		<Heading id="pg2loreum1title"
			><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum />
	</div>

	<div id="pg2loreum2">
		<Heading id="pg2loreum2title"
			><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum repetition={4} />
	</div>

	<Heading id="pg2sub-category">Sub Category</Heading>

	<div id="pg2loreum3">
		<Title id="pg2loreum3title"
			><span class="italic">Third</span> Lorem ipsum dolor sit amet...</Title
		>
		<Loreum />
	</div>

	<div id="pg2loreum4">
		<Title id="pg2loreum4title"
			><span class="italic">Fourth</span> Lorem ipsum dolor sit amet...</Title
		>
		<Loreum />
	</div>

	<div id="pg2loreum5">
		<Heading id="pg2loreum5title"
			><span class="italic">Fifth</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum />
	</div>

	<div id="pg2loreum6">
		<Heading id="pg2loreum6title"
			><span class="italic">Sixth</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum repetition={20} />
	</div>
</div>
