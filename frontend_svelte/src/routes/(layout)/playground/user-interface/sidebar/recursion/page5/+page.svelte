<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../Loreum.svelte';
	import Display from '$components/Display.svelte';
</script>

<div class="bg-info-container/70 rounded-xl p-4">
	<Display>Page 5</Display>

	<p>Page 5 has no children - only links within page</p>

	<Heading id="loreum1"><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum />

	<Heading id="loreum2"><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum />
</div>
