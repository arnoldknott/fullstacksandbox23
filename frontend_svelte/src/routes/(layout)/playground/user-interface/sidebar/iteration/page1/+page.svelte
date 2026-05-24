<script lang="ts">
	import Display from '$components/Display.svelte';

	import Loreum from '../../Loreum.svelte';
</script>

<div class="bg-success-container/70 rounded-xl p-4">
	<Display>Page 1</Display>

	<p>Page 1 has no hierarchy and id's, just content</p>

	<Loreum repetition={20} />
</div>
