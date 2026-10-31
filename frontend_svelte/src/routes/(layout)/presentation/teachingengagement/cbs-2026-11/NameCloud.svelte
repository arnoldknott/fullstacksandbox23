<script lang="ts">
	import type { Attachment } from 'svelte/attachments';

	let {
		text,
		excludeWidth = 0,
		excludeHeight = 0
	}: { text: string; excludeWidth?: number; excludeHeight?: number } = $props();

	const randomPosition: Attachment<HTMLDivElement> = (node) => {
		const container = node.parentElement;
		if (!container) return;

		let frame = 0;

		const place = () => {
			frame = 0;
			const maxLeft = Math.max(0, container.clientWidth - node.offsetWidth);
			const maxTop = Math.max(0, container.clientHeight - node.offsetHeight);

			let regions = [{ left: 0, top: 0, width: maxLeft, height: maxTop }];
			if (excludeWidth > 0 && excludeHeight > 0) {
				const left = (container.clientWidth - excludeWidth) / 2 - 16 - node.offsetWidth;
				const right = (container.clientWidth + excludeWidth) / 2 + 16;
				const top = (container.clientHeight - excludeHeight) / 2 - 16 - node.offsetHeight;
				const bottom = (container.clientHeight + excludeHeight) / 2 + 16;
				const middleTop = Math.max(0, top);
				const middleBottom = Math.min(maxTop, bottom);
				regions = [
					{ left: 0, top: 0, width: maxLeft, height: Math.min(maxTop, top) },
					{
						left: 0,
						top: Math.max(0, bottom),
						width: maxLeft,
						height: maxTop - Math.max(0, bottom)
					},
					{
						left: 0,
						top: middleTop,
						width: Math.min(maxLeft, left),
						height: middleBottom - middleTop
					},
					{
						left: Math.max(0, right),
						top: middleTop,
						width: maxLeft - Math.max(0, right),
						height: middleBottom - middleTop
					}
				].filter((region) => region.width > 0 && region.height > 0);
			}
			if (!regions.length) {
				console.error('🔥 NameCloud - no space outside the reserved heading', text);
				node.style.visibility = 'hidden';
				return;
			}
			node.style.visibility = '';
			const totalArea = regions.reduce((sum, region) => sum + region.width * region.height, 0);
			let choice = Math.random() * totalArea;
			const region =
				regions.find((region) => {
					choice -= region.width * region.height;
					return choice <= 0;
				}) ?? regions[regions.length - 1];
			node.style.left = `${region.left + Math.random() * region.width}px`;
			node.style.top = `${region.top + Math.random() * region.height}px`;
		};

		const schedulePlace = () => {
			cancelAnimationFrame(frame);
			frame = requestAnimationFrame(place);
		};

		const observer = new ResizeObserver(schedulePlace);
		observer.observe(container);
		observer.observe(node);
		$effect(() => {
			void excludeWidth;
			void excludeHeight;
			schedulePlace();
		});

		return () => {
			cancelAnimationFrame(frame);
			observer.disconnect();
		};
	};
</script>

<div
	class="absolute h-fit max-w-[min(24rem,calc(100%-1rem))] text-4xl break-words opacity-60"
	{@attach randomPosition}
>
	{text}
</div>
