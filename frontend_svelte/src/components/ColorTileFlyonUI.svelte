<script lang="ts">
	let { background, content }: { background: string; content: string } = $props();
	const text = background.replaceAll('-', ' ');
</script>

<div class="flex h-24 grow p-2 bg-{background}">
	<p class="text-left text-base md:text-xl text-{content}">
		{text}
	</p>
</div>

<style>
	.bg-primary-container {
		background-color: var(--md-sys-color-primary-container);
	}
	.text-primary-container {
		color: var(--md-sys-color-primary-container);
	}
	.bg-primary-container-content {
		background-color: var(--md-sys-color-on-primary-container);
	}
	.text-primary-container-content {
		color: var(--md-sys-color-on-primary-container);
	}
	.bg-secondary-container {
		background-color: var(--md-sys-color-secondary-container);
	}
	.text-secondary-container {
		color: var(--md-sys-color-secondary-container);
	}
	.bg-secondary-container-content {
		background-color: var(--md-sys-color-on-secondary-container);
	}
	.text-secondary-container-content {
		color: var(--md-sys-color-on-secondary-container);
	}
	.bg-accent-container {
		background-color: var(--md-sys-color-tertiary-container);
	}
	.text-accent-container {
		color: var(--md-sys-color-tertiary-container);
	}
	.bg-accent-container-content {
		background-color: var(--md-sys-color-on-tertiary-container);
	}
	.text-accent-container-content {
		color: var(--md-sys-color-on-tertiary-container);
	}
	.bg-neutral-container {
		background-color: var(--md-sys-color-neutral-container);
	}
	.text-neutral-container {
		color: var(--md-sys-color-neutral-container);
	}
	.bg-neutral-container-content {
		background-color: var(--md-sys-color-on-neutral-container);
	}
	.text-neutral-container-content {
		color: var(--md-sys-color-on-neutral-container);
	}
</style>
