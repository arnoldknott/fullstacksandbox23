<script lang="ts">
	// let { background, content="" }: { background: string; content?: string } = $props();
	// const text = background.replaceAll('-', ' ');
	import { type Snippet } from 'svelte';
	let { children, classes = "" }: { children: Snippet, classes?: string } = $props();
</script>

<!-- <div class="flex h-18 md:h-20 xl:24 grow p-2 bg-{background}">
    <p class="text-left text-xs md:text-lg xl:text-xl {content ? 'text-' + content : "" } ">
		{text}
	</p>
</div> -->

<!-- <p class="text-left text-base md:text-xl text-{content}"> -->

<div class="h-18 xl:24 flex grow md:h-20 {classes}">
	{@render children?.()}
</div>

<!-- <style scoped>
	/* .bg-primary-container {
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
	}*/
</style> -->
