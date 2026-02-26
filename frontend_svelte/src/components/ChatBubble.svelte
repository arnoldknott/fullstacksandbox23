<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';
	import type { Snippet } from 'svelte';

	type ColorVariant =
		| 'primary'
		| 'secondary'
		| 'accent'
		| 'warning'
		| 'error'
		| 'success'
		| 'info'
		| 'neutral';

	interface ChatBubbleProps extends HTMLAttributes<HTMLDivElement> {
		children: Snippet;
		variant?: ColorVariant;
		tailAngle?: number;
		showTail?: boolean;
		shadow?: boolean;
		tailLength?: number;
		tailBase?: number;
		maxWidth?: string;
	}

	let {
		children,
		variant = 'primary',
		tailAngle = 120,
		showTail = true,
		shadow = true,
		tailLength = 72,
		tailBase = 84,
		maxWidth = '72%',
		...rest
	}: ChatBubbleProps = $props();

	// const variantColors: Record<ColorVariant, { bg: string; text: string }> = {
	// 	primary: { bg: 'var(--color-primary)', text: 'var(--color-primary-content)' },
	// 	secondary: { bg: 'var(--color-secondary)', text: 'var(--color-secondary-content)' },
	// 	accent: { bg: 'var(--color-accent)', text: 'var(--color-accent-content)' },
	// 	warning: { bg: 'var(--color-warning)', text: 'var(--color-warning-content)' },
	// 	error: { bg: 'var(--color-error)', text: 'var(--color-error-content)' },
	// 	success: { bg: 'var(--color-success)', text: 'var(--color-success-content)' },
	// 	info: { bg: 'var(--color-info)', text: 'var(--color-info-content)' },
	// 	neutral: { bg: 'var(--color-neutral)', text: 'var(--color-neutral-content)' }
	// };

	// const bgColor = customBgColor || variantColors[variant].bg;
	// const textColor = customTextColor || variantColors[variant].text;

	// Tailwind safelist: shadow-primary shadow-secondary shadow-accent shadow-warning shadow-error shadow-success shadow-info shadow-neutral
	// Tailwind safelist: fill-primary fill-secondary fill-accent fill-warning fill-error fill-success fill-info fill-neutral

	let ovalWidth = $state(0);
	let ovalHeight = $state(0);

	function normalizeDegrees(value: number): number {
		const wrapped = value % 360;
		return wrapped < 0 ? wrapped + 360 : wrapped;
	}

	function pointOnEllipse(theta: number, cx: number, cy: number, rx: number, ry: number) {
		return { x: cx + rx * Math.cos(theta), y: cy + ry * Math.sin(theta) };
	}

	let tail = $derived.by(() => {
		if (!showTail || ovalWidth <= 0 || ovalHeight <= 0) return null;

		const cx = ovalWidth / 2;
		const cy = ovalHeight / 2;
		const rx = ovalWidth / 2;
		const ry = ovalHeight / 2;

		const angleRad = (normalizeDegrees(tailAngle) * Math.PI) / 180;
		const spreadRad = Math.max(0.1, Math.min(0.45, (tailBase / Math.max(rx, ry)) * 0.8));
		const base1 = pointOnEllipse(angleRad - spreadRad, cx, cy, rx, ry);
		const base2 = pointOnEllipse(angleRad + spreadRad, cx, cy, rx, ry);
		const anchor = pointOnEllipse(angleRad, cx, cy, rx, ry);
		const tip = {
			x: anchor.x + tailLength * Math.cos(angleRad),
			y: anchor.y + tailLength * Math.sin(angleRad)
		};

		const allX = [base1.x, base2.x, tip.x];
		const allY = [base1.y, base2.y, tip.y];
		const minX = Math.min(...allX) - 2;
		const minY = Math.min(...allY) - 2;
		const w = Math.max(...allX) - minX + 4;
		const h = Math.max(...allY) - minY + 4;

		const path = [
			`M ${base1.x - minX} ${base1.y - minY}`,
			`L ${tip.x - minX} ${tip.y - minY}`,
			`L ${base2.x - minX} ${base2.y - minY}`,
			'Z'
		].join(' ');

		return { path, style: `left:${minX}px;top:${minY}px;width:${w}px;height:${h}px;` };
	});
</script>

<div class="chat-bubble-wrapper" style="--bubble-max-width: {maxWidth};" {...rest}>
	<div
		class={`bubble-oval ${shadow ? `shadow-${variant} shadow-lg` : ''} ` +
			`bg-${variant} text-${variant}-content`}
		bind:clientWidth={ovalWidth}
		bind:clientHeight={ovalHeight}
	>
		<div class="bubble-text">
			{@render children()}
		</div>
	</div>
	{#if tail}
		<svg class="tail-svg" style={tail.style} aria-hidden="true">
			<!-- <path d={tail.path} fill={bgColor}></path> -->
			<path d={tail.path} class={`fill-${variant}`.toString()}></path>
		</svg>
	{/if}
</div>

<style>
	.chat-bubble-wrapper {
		position: relative;
		display: inline-block;
		max-width: min(var(--bubble-max-width), calc(100% - 2rem));
		width: fit-content;
	}

	.bubble-oval {
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		text-align: center;
		padding: 2rem 3rem;
		min-height: 10rem;
		font-size: 2rem;
		line-height: 1.25;
		font-weight: 500;
	}

	.bubble-text {
		width: 100%;
		margin: 0;
		text-wrap: balance;
	}

	.tail-svg {
		position: absolute;
		pointer-events: none;
		overflow: visible;
	}
</style>
