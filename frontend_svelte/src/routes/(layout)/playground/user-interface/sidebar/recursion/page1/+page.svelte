<script lang="ts">
	import Loreum from '../../Loreum.svelte';
	import Display from '$components/Display.svelte';
</script>

<div class="bg-success-container/70 rounded-xl p-4">
	<Display>Page 1</Display>

	<p>Page 1 has no hierarchy and id's, just content</p>

	<Loreum repetition={60} />
</div>
