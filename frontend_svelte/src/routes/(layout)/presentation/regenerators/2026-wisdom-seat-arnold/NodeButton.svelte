<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLAttributes } from 'svelte/elements';
	let {
		children,
		// modalId,
		// toggleElement,
		toggleVariable = $bindable(true),
		standard = true,
		...rest
	}: {
		children: Snippet;
		toggleVariable?: boolean;
		standard?: boolean;
	} & HTMLAttributes<HTMLElement> = $props();
</script>

<button
	class={standard
		? 'btn btn-xl btn-gradient absolute justify-center rounded-full p-10 text-5xl font-semibold shadow-inner ' +
			(rest.class ?? '')
		: (rest.class ?? '')}
	onclick={() => {
		if (toggleVariable !== undefined) {
			toggleVariable = !toggleVariable;
		}
	}}
	// aria-haspopup={modalId ? 'dialog' : undefined}
	// aria-expanded={modalId ? 'false' : undefined}
	// aria-controls={modalId || undefined}
	// data-overlay={modalId ? '#' + modalId : undefined}
>
	{@render children()}
</button>
