<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../../../Loreum.svelte';
	import Display from '$components/Display.svelte';
</script>

<div class="bg-info-container/50 rounded-xl p-4">
	<Display>Page 4.1.1</Display>

	<p>Page 4.1.1 is a subpage to page 4.1</p>

	<Heading><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum repetition={30} />
</div>
