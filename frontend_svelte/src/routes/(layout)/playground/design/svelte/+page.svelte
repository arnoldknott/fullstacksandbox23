<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import Box from './Box.svelte';
	import Slider from './Slider.svelte';
	import { blur, crossfade, draw, fade, fly, scale, slide } from 'svelte/transition';
	import { flip } from 'svelte/animate';

	let blurParameters = $state({
		delay: 0,
		duration: 300,
		// easing: (t: number) => t, // Easing function not implemented in this demo
		amount: 5,
		opacity: 0.5
	});
	let newBlur = $state<string>('');
	let blurItems = $state<string[]>([]);

	let crossfadeParameters = $state({
		delay: 0,
		duration: 300
		// easing: (t: number) => t, // Easing function not implemented in this demo
	});
	const [sendCrossfade, receiveCrossfade] = crossfade({ ...crossfadeParameters });
	let left = $state([
		{ name: 'Item 1' },
		{ name: 'Item 2' },
		{ name: 'Item 3' },
		{ name: 'Item 4' },
		{ name: 'Item 5' }
	]);
	let right = $state([
		{ name: 'Item A' },
		{ name: 'Item B' },
		{ name: 'Item C' },
		{ name: 'Item D' },
		{ name: 'Item E' }
	]);

	let drawParameters = $state({
		delay: 0,
		speed: 0.1,
		duration: 300 as number | undefined
		// easing: (t: number) => t, // Easing function not implemented in this demo
	});
	let useDrawDuration = $state(true);
	$effect(() => {
		if (!useDrawDuration) {
			drawParameters.duration = undefined;
		} else {
			drawParameters.duration = 300;
		}
	});
	let drawShow = $state(false);

	let fadeParameters = $state({
		delay: 0,
		duration: 300
		// easing: (t: number) => t, // Easing function not implemented in this demo
	});
	let newFade = $state<string>('');
	let fadeItems = $state<string[]>([]);

	let newFly = $state<string>('');
	let flyItems = $state<string[]>([]);

	let newScale = $state<string>('');
	let scaleItems = $state<string[]>([]);

	let newSlide = $state<string>('');
	let slideItems = $state<string[]>([]);

	const pushItem = (newItem: string, list: string[]) => {
		if (newItem.trim() !== '') {
			list.push(newItem);
		}
	};
</script>

<Heading>Transitions</Heading>

<div class="sm w-full md:grid md:grid-cols-4 md:gap-4">
	<Box title="Blur">
		<div class="flex flex-col">
			<div class="title-small italic">Parameters:</div>
			<Slider
				name="Delay"
				id="blurDelay"
				bind:value={blurParameters.delay}
				min={0}
				max={3000}
				step={100}
			/>
			<Slider
				name="Duration"
				id="blurDuration"
				bind:value={blurParameters.duration}
				min={0}
				max={3000}
				step={100}
			/>
			<Slider
				name="Amount"
				id="blurAmount"
				bind:value={blurParameters.amount}
				min={0}
				max={20}
				step={1}
			/>
			<Slider
				name="Opacity"
				id="blurOpacity"
				bind:value={blurParameters.opacity}
				min={0}
				max={1}
				step={0.1}
			/>
			<div class="divider divider-outline py-2"></div>
			<div class="title-small italic">Notes:</div>
			<div class="body-small">- <code>easing</code> not implemented.</div>
			<div class="divider divider-outline py-2"></div>
			<div class="title-small italic">Playground:</div>
			<div class="input-filled">
				<input
					type="text"
					placeholder="New blur item"
					bind:value={newBlur}
					onblur={() => {
						pushItem(newBlur, blurItems);
						newBlur = '';
					}}
					onkeydown={(e) => {
						if (e.key === 'Enter') {
							pushItem(newBlur, blurItems);
							newBlur = '';
						}
					}}
					class="input"
					id="blurItem"
				/>
				<label class="input-filled-label" for="blurItem">Add some text</label>
			</div>
		</div>
		<ul class="h-38 list-inside overflow-y-scroll py-2">
			{#each blurItems as item, idx (idx)}
				<li class="title" transition:blur={blurParameters}>
					<div class="flex flex-row justify-between">
						{item}
						<button
							class="btn btn-error-container btn-circle btn-gradient btn-sm"
							aria-label="Remove Item"
							onclick={() => blurItems.splice(idx, 1)}
						>
							<span class="icon-[fa6-solid--minus] size-4"></span>
						</button>
					</div>
				</li>
			{/each}
		</ul>
	</Box>

	<Box title="Crossfade">
		<div class="flex flex-col">
			<div class="title-small italic">Parameters:</div>
			<Slider
				name="Delay"
				id="crossfadeDelay"
				bind:value={crossfadeParameters.delay}
				min={0}
				max={3000}
				step={100}
			/>
			<Slider
				name="Duration"
				id="crossfadeDuration"
				bind:value={crossfadeParameters.duration}
				min={0}
				max={3000}
				step={100}
			/>
		</div>
		<div class="divider divider-outline py-2"></div>
		<div class="title-small italic">Notes:</div>
		<div class="body-small">- <code>easing</code> not implemented.</div>
		<div class="body-small">- Also uses <code>animate:flip</code>.</div>
		<div class="divider divider-outline py-2"></div>
		<div class="title-small italic">Playground:</div>
		<div class="grid grid-cols-2">
			<ul class="h-85 w-full list-inside overflow-y-scroll">
				{#each left as item (item)}
					<li class="title" animate:flip={crossfadeParameters}>
						<button
							onclick={() => {
								left = left.filter((i) => i !== item);
								right.push(item);
							}}
							in:receiveCrossfade={{ key: item, ...crossfadeParameters }}
							out:sendCrossfade={{ key: item, ...crossfadeParameters }}
						>
							{item.name}
						</button>
					</li>
				{/each}
			</ul>
			<ul class="h-85 w-full list-inside overflow-y-scroll">
				{#each right as item (item)}
					<li class="title" animate:flip={crossfadeParameters}>
						<button
							onclick={() => {
								right = right.filter((i) => i !== item);
								left.push(item);
							}}
							in:receiveCrossfade={{ key: item, ...crossfadeParameters }}
							out:sendCrossfade={{ key: item, ...crossfadeParameters }}
						>
							{item.name}
						</button>
					</li>
				{/each}
			</ul>
		</div>
	</Box>

	{#snippet durationCheckbox()}
		<div class="flex items-center pr-2">
			<input
				type="checkbox"
				id="useDrawDuration"
				bind:checked={useDrawDuration}
				class="checkbox checkbox-sm"
			/>
		</div>
	{/snippet}

	<Box title="Draw">
		<div class="title-small italic">Parameters:</div>
		<Slider
			name="Delay"
			id="drawDelay"
			bind:value={drawParameters.delay}
			min={0}
			max={3000}
			step={100}
		/>
		<Slider
			name="Speed"
			id="drawSpeed"
			bind:value={drawParameters.speed}
			min={0.01}
			max={0.1}
			step={0.01}
		/>

		<Slider
			preName={durationCheckbox}
			name="Duration"
			id="drawDuration"
			bind:value={drawParameters.duration}
			min={0}
			max={3000}
			step={100}
		/>
		<div class="divider divider-outline py-2"></div>
		<div class="title-small italic">Notes:</div>
		<div class="body-small">
			- drawing from <a
				href="https://svelte.dev/playground/149a5c35040343daa9477e0d54412398?version=3.31.0">here</a
			>.
		</div>
		<div class="body-small">- <code>duration</code> takes precedence over <code>speed</code>.</div>
		<div class="body-small">- <code>speed</code> uses stroke length to calculate duration.</div>
		<div class="body-small">- <code>easing</code> not implemented.</div>
		<div class="divider divider-outline py-2"></div>
		<div class="title-small italic">Playground:</div>
		<button
			class="btn w-full rounded-full px-2"
			onclick={() => {
				drawShow = !drawShow;
			}}
		>
			{drawShow ? 'Hide' : 'Show'} drawing
		</button>
		{#if drawShow}
			<div class="flex justify-center">
				<svg width={110} height={110} viewBox="0 0 12 12" class="stroke-primary">
					<g transform="translate(0 12) scale(1 -1)">
						<path
							transition:draw={drawParameters}
							d="M 2 5 v-4 h3 v3 h2 v-3 h3 v4 h-9 l 5 4 l 5 -4 h-1"
							fill="none"
							stroke-width="0.3px"
						/>
					</g>
				</svg>
			</div>
		{/if}
	</Box>

	<Box title="Fade">
		<div class="flex flex-col">
			<div class="title-small italic">Parameters:</div>
			<Slider
				name="Delay"
				id="fadeDelay"
				bind:value={fadeParameters.delay}
				min={0}
				max={3000}
				step={100}
			/>
			<Slider
				name="Duration"
				id="fadeDuration"
				bind:value={fadeParameters.duration}
				min={0}
				max={3000}
				step={100}
			/>
		</div>
		<div class="divider divider-outline py-2"></div>
		<div class="title-small italic">Notes:</div>
		<div class="body-small">- <code>easing</code> not implemented.</div>
		<div class="divider divider-outline py-2"></div>
		<div class="input-filled">
			<input
				type="text"
				placeholder="New fade item"
				bind:value={newFade}
				onblur={() => {
					pushItem(newFade, fadeItems);
					newFade = '';
				}}
				onkeydown={(e) => {
					if (e.key === 'Enter') {
						pushItem(newFade, fadeItems);
						newFade = '';
					}
				}}
				class="input"
				id="fadeItem"
			/>
			<label class="input-filled-label" for="fadeItem">Add some text</label>
		</div>
		<ul class="h-85 list-inside overflow-y-scroll">
			{#each fadeItems as item, idx (idx)}
				<li class="title" transition:fade={fadeParameters}>
					<div class="flex flex-row justify-between">
						{item}
						<button
							class="btn btn-error-container btn-circle btn-gradient btn-sm"
							aria-label="Remove Item"
							onclick={() => fadeItems.splice(idx, 1)}
						>
							<span class="icon-[fa6-solid--minus] size-4"></span>
						</button>
					</div>
				</li>
			{/each}
		</ul>
	</Box>
</div>
