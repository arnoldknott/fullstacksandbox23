<script lang="ts">
	import type { Attachment } from 'svelte/attachments';

	const randomPosition: Attachment<HTMLDivElement> = (node) => {
		const container = node.parentElement;
		if (!container) return;

		let frame = 0;

		const place = () => {
			frame = 0;
			const maxLeft = Math.max(0, container.clientWidth - node.offsetWidth);
			const maxTop = Math.max(0, container.clientHeight - node.offsetHeight);

			node.style.left = `${Math.random() * maxLeft}px`;
			node.style.top = `${Math.random() * maxTop}px`;
		};

		const schedulePlace = () => {
			cancelAnimationFrame(frame);
			frame = requestAnimationFrame(place);
		};

		const observer = new ResizeObserver(schedulePlace);
		observer.observe(container);
		observer.observe(node);
		schedulePlace();

		return () => {
			cancelAnimationFrame(frame);
			observer.disconnect();
		};
	};

	let { text }: { text: string } = $props();
</script>

<div
	class="absolute h-fit max-w-[min(24rem,calc(100%-1rem))] text-5xl break-words opacity-60"
	{@attach randomPosition}
>
	{text}
</div>
