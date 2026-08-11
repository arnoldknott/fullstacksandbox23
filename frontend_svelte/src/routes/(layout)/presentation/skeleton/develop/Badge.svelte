<script lang="ts">
	let { title, color = 'secondary' }: { title: string; color?: string } = $props();
</script>

<div
	class="badge badge-{color}-container label shadow-outline h-20 rounded-full p-8 text-5xl shadow-inner"
>
	{title}
</div>
