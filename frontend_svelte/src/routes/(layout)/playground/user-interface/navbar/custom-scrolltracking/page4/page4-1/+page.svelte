<script lang="ts">
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';
	import Section from '$components/Section.svelte';

	import Loreum from '../../../Loreum.svelte';
</script>

<div class="bg-primary-container/70 rounded-xl p-4">
	<Display>Page 4.1</Display>

	<p>Page 4.1 is a subpage to page 4</p>

	<Section id="loreum1">
		<!-- {#snippet header()}{/snippet} -->
		<Heading id="loreum1heading"
			><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum repetition={30} />
	</Section>
	<Section id="loreum2">
		<!-- {#snippet header()}{/snippet} -->
		<Heading id="loreum2heading"
			><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum repetition={30} />
	</Section>
</div>
