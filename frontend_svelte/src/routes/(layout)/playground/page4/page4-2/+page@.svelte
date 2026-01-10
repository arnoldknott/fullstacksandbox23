<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../../Loreum.svelte';
	import Display from '$components/Display.svelte';
	import Section from '$components/Section.svelte';
</script>

<div class="bg-secondary-container/70 rounded-xl p-4">
	<Display>Page 4.2</Display>

	<p>Page 4.2 is a subpage to page 4</p>

	<Section id="loreum1">
		<Heading><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading>
		<Loreum repetition={30} />
	</Section>

	<Section id="loreum2">
		<Heading><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading>
		<Loreum repetition={30} />
	</Section>
</div>
