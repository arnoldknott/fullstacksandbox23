<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../Loreum.svelte';
	import Display from '$components/Display.svelte';
	import Section from '$components/Section.svelte';
</script>

<div class="bg-info-container/50 rounded-xl p-4">
	<Display>Page 5</Display>

	<p>Page 5 has no children - only links within page</p>

	<Section id="loreum1">
		<Heading id="loreum1title">
			<span class="italic">First</span> Lorem ipsum dolor sit amet...
		</Heading>
		<Loreum />
	</Section>
	<Section id="loreum2">
		<Heading id="loreum2title">
			<span class="italic">Second</span> Lorem ipsum dolor sit amet...
		</Heading>
		<Loreum />
	</Section>
</div>
