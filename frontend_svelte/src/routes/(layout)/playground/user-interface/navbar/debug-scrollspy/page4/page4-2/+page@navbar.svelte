<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../../Loreum.svelte';
	import Display from '$components/Display.svelte';
</script>

<div class="bg-secondary-container/70 rounded-xl p-4">
	<Display>Page 4.2</Display>

	<p>Page 4.2 is a subpage to page 4</p>

	<Heading id="loreum1"><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum repetition={30} />

	<Heading id="loreum2"><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum repetition={30} />
</div>
