<script lang="ts">
	let { children } = $props();
</script>

<div class="mx-5">
	<h1 class="mx-5 mb-2 mt-0 text-5xl font-medium leading-tight text-primary">
		{@render children?.()}
	</h1>
</div>
