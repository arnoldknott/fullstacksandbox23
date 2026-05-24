<script lang="ts">
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';

	import Loreum from '../../../Loreum.svelte';
</script>

<div class="bg-primary-container/70 rounded-xl p-4">
	<Display>Page 4.1</Display>

	<p>Page 4.1 is a subpage to page 4</p>

	<Heading id="loreum1"><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum repetition={30} />

	<Heading id="loreum2"><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum repetition={30} />
</div>
