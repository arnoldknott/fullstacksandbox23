<script lang="ts">
	let {
		strategy = false,
		initiatives = false,
		leadership = false
	}: { strategy?: boolean; initiatives?: boolean; leadership?: boolean } = $props();
	const all = $derived(strategy && initiatives && leadership);
</script>

<div class="pointer-events-none absolute inset-0">
	<div class="relative h-full w-full">
		<div
			class="border-border absolute inset-x-[10%] top-[12%] bottom-[12%] rounded-[50%] border-8 bg-transparent {all
				? ''
				: 'hidden'}"
		></div>
		<div
			class="pointer-events-auto absolute top-[12%] left-[50%] -translate-x-1/2 -translate-y-1/2 {strategy
				? ''
				: 'hidden'}"
		>
			<a href="#tension-strategy">
				<button
					class="link link-hover bg-warning text-warning-content h-fit w-fit rounded-[50%] p-20 text-5xl"
					>Strategy
				</button>
			</a>
		</div>
		<div
			class="pointer-events-auto absolute top-[70%] right-[60%] -translate-x-1/2 -translate-y-1/2 {initiatives
				? ''
				: 'hidden'}"
		>
			<a href="#tension-initiatives">
				<button
					class="link link-hover bg-success text-success-content h-fit w-fit rounded-[50%] p-20 text-5xl"
					>Initiatives
				</button>
			</a>
		</div>
		<div
			class="pointer-events-auto absolute top-[70%] left-[80%] -translate-x-1/2 -translate-y-1/2 {leadership
				? ''
				: 'hidden'}"
		>
			<a href="#tension-leadership">
				<button
					class="link link-hover bg-error text-error-content h-fit w-fit rounded-[50%] p-20 text-5xl"
					>Leadership
				</button>
			</a>
		</div>
	</div>
</div>
