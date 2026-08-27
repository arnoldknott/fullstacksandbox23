<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { Attachment } from 'svelte/attachments';
	import type { HTMLAttributes } from 'svelte/elements';
	import { on } from 'svelte/events';

	import Card from '$components/Card.svelte';

	let {
		hidden = $bindable(true),
		children,
		header,
		...props
	}: {
		hidden?: boolean;
		header?: Snippet;
		children: Snippet;
	} & HTMLAttributes<HTMLElement> = $props();

	const closeOnEscape = (close: () => void): Attachment<HTMLElement> => {
		return () => {
			const onKeyDown = (event: KeyboardEvent) => {
				if (event.key === 'Escape') {
					event.preventDefault();
					event.stopPropagation();
					event.stopImmediatePropagation();
					close();
				}
			};
			return on(document, 'keydown', onKeyDown, { capture: true });
		};
	};
</script>

<Card
	id="courses-card"
	closeButton
	extraClasses={props.class?.toString() ?? ''}
	{header}
	bind:hidden
	{@attach closeOnEscape(() => {
		hidden = true;
	})}
>
	{@render children()}
</Card>
