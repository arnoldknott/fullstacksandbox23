<script lang="ts">
	let { id }: { id?: string } = $props();
</script>

<div class="badge badge-xs badge-secondary label-small shadow-outline shadow">
	{id ? id.slice(0, 8) : 'IDmissing'}
</div>
