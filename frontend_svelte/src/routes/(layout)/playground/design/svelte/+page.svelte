<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import Box from './Box.svelte';
	import Slider from './Slider.svelte';
	import { blur, crossfade, draw, fade, fly, scale, slide } from 'svelte/transition';
	import { flip } from 'svelte/animate';
	import { list } from 'postcss';

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

	let flyParameters = $state({
		delay: 0,
		duration: 500,
		x: -25,
		y: -25,
		opacity: 0.2
		// easing: (t: number) => t, // Easing function not implemented in this demo
	});
	let flyShow = $state<boolean>(false);

	let scaleParameters = $state({
		delay: 0,
		duration: 500,
		start: 0.3,
		opacity: 0.2
		// easing: (t: number) => t, // Easing function not implemented in this demo
	});
	let scaleShow = $state<boolean>(false);

	const listItems = [
		{ name: 'Item 1' },
		{ name: 'Item 2' },
		{ name: 'Item 3' },
		{ name: 'Item 4' },
		{ name: 'Item 5' }
	];
	let slideParameters = $state({
		delay: 0,
		duration: 500,
		axis: 'y' as 'x' | 'y'
		// easing: (t: number) => t, // Easing function not implemented in this demo
	});
	let slideShow = $state<boolean>(false);
	let slideShowItems = $state<number>(3); // Number of items to show in the slide transition

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

	<Box title="Fly">
		<div class="flex flex-col">
			<div class="title-small italic">Parameters:</div>
			<Slider
				name="Delay"
				id="flyDelay"
				bind:value={flyParameters.delay}
				min={0}
				max={3000}
				step={100}
			/>
			<Slider
				name="Duration"
				id="flyDuration"
				bind:value={flyParameters.duration}
				min={0}
				max={3000}
				step={100}
			/>
			<Slider
				name="X Offset"
				id="flyXOffset"
				bind:value={flyParameters.x}
				min={-50}
				max={50}
				step={10}
			/>
			<Slider
				name="Y Offset"
				id="flyYOffset"
				bind:value={flyParameters.y}
				min={-50}
				max={50}
				step={5}
			/>
			<Slider
				name="Opacity"
				id="flyZOpacity"
				bind:value={flyParameters.opacity}
				min={0}
				max={1}
				step={0.1}
			/>
		</div>
		<div class="divider divider-outline py-2"></div>
		<div class="title-small italic">Notes:</div>
		<div class="body-small">- <code>easing</code> not implemented.</div>
		<div class="divider divider-outline py-2"></div>
		<div class="title-small italic">Playground:</div>
		<button
			class="btn w-full rounded-full px-2"
			onclick={() => {
				flyShow = !flyShow;
			}}
		>
			{flyShow ? 'Hide' : 'Show'} icon
		</button>
		{#if flyShow}
			<div class="flex justify-center p-5">
				<span class="icon-[devicon--svelte] size-12" transition:fly={flyParameters}></span>
			</div>
		{/if}
	</Box>

	<Box title="Scale">
		<div class="flex flex-col">
			<div class="title-small italic">Parameters:</div>
			<Slider
				name="Delay"
				id="scaleDelay"
				bind:value={scaleParameters.delay}
				min={0}
				max={3000}
				step={100}
			/>
			<Slider
				name="Duration"
				id="scaleDuration"
				bind:value={scaleParameters.duration}
				min={0}
				max={3000}
				step={100}
			/>
			<Slider
				name="Start Scale"
				id="scaleStart"
				bind:value={scaleParameters.start}
				min={0}
				max={2}
				step={0.1}
			/>
			<Slider
				name="Opacity"
				id="scaleOpacity"
				bind:value={scaleParameters.opacity}
				min={0}
				max={1}
				step={0.1}
			/>
		</div>
		<div class="divider divider-outline py-2"></div>
		<div class="title-small italic">Notes:</div>
		<div class="body-small">- <code>easing</code> not implemented.</div>
		<div class="divider divider-outline py-2"></div>
		<div class="title-small italic">Playground:</div>
		<button
			class="btn w-full rounded-full px-2"
			onclick={() => {
				scaleShow = !scaleShow;
			}}
		>
			{scaleShow ? 'Hide' : 'Show'} icon
		</button>
		{#if scaleShow}
			<div class="flex justify-center p-5">
				<span class="icon-[devicon--svelte] size-25" transition:scale={scaleParameters}></span>
			</div>
		{/if}
	</Box>

	<Box title="Slide">
		<div class="flex flex-col">
			<div class="title-small italic">Parameters:</div>
			<Slider
				name="Delay"
				id="slideDelay"
				bind:value={slideParameters.delay}
				min={0}
				max={3000}
				step={100}
			/>
			<Slider
				name="Duration"
				id="slideDuration"
				bind:value={slideParameters.duration}
				min={0}
				max={3000}
				step={100}
			/>
			<div>
				<label class="label label-text flex justify-between" for="axisSwitcher">Axis: </label>
				x
				<input
					type="checkbox"
					class="switch"
					id="axisSwitcher"
					checked={slideParameters.axis === 'y'}
					onchange={() => {
						slideParameters.axis = slideParameters.axis === 'x' ? 'y' : 'x';
					}}
				/>
				y
			</div>
			<div class="divider divider-outline py-2"></div>
			<div class="title-small italic">Notes:</div>
			<div class="body-small">- <code>easing</code> not implemented.</div>
			<div class="body-small">- Uses <code>global</code> to apply 2 conditions</div>
			<div class="title-small italic">Playground:</div>
			<button
				class="btn w-full rounded-full px-2"
				onclick={() => {
					slideShow = !slideShow;
				}}
			>
				{slideShow ? 'Hide' : 'Show'} list
			</button>
			<Slider
				name="Show items"
				id="showSlideItems"
				bind:value={slideShowItems}
				min={0}
				max={5}
				step={1}
			/>
			{#if slideShow}
				<ul>
					{#each listItems.slice(0, slideShowItems) as item}
						<li transition:slide|global={slideParameters}>
							{item.name}
							<div class="divider divider-outline"></div>
						</li>
					{/each}
				</ul>
			{/if}
		</div></Box
	>
</div>
