<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import { blur, crossfade, draw, fade, fly, scale, slide, type BlurParams,  } from 'svelte/transition';
    // import { blur } from 'svelte/transition';

    const data = $state([
        {
            name: 'Blur',
            animation: blur,
            newItem: '',
            itemList: [] as string[],
        },
        {
            name: 'Crossfade',
            animation: crossfade,
            newItem: '',
            itemList: [] as string[],
        },
        {
            name: 'Draw',
            animation: draw,
            newItem: '',
            itemList: [] as string[],
        },
        {
            name: 'Fade',
            animation: fade,
            newItem: '',
            itemList: [] as string[],
        },
        {
            name: 'Fly',
            animation: fly,
            newItem: '',
            itemList: [] as string[],
        },
        {
            name: 'Scale',
            animation: scale,
            newItem: '',
            itemList: [] as string[],
        },
        {
            name: 'Slide',
            animation: slide,
            newItem: '',
            itemList: [] as string[],
        }
    ])

    const blurData = $state(
        {
            name: 'Blur',
            animation: blur,
            newItem: '',
            itemList: [] as string[],
        }
    )

	let newBlur = $state<string>('');
	let blurItems = $state<string[]>([]);

	const pushItem = (newItem: string, list: string[]) => {
        console.log('Pushing item:', newItem, 'to list:', list);
		if (newItem.trim() !== '') {
			list.push(newItem);
			newBlur = '';
		}
	};
</script>

{#snippet box(name: string, animation: (node: Element, { delay, duration, easing, amount, opacity }?: BlurParams | undefined) => TransitionConfig, newItem: string, itemList: string[])}
    <div>
		<Heading>{name}</Heading>
		<div class="bg-base-150 shadow-outline h-100 w-90% rounded-lg p-2 shadow-inner">
			<div class="flex flex-row">
				<div class="title-small italic">{name} list</div>
				<div class="input-filled">
					<input
						type="text"
						placeholder="New blur item"
						value={newItem}
						onblur={() => pushItem(newItem, itemList)}
						onkeydown={(e) => {
							if (e.key === 'Enter') {
								pushItem(newItem, itemList);
							}
						}}
						class="input"
						id="blurItem"
					/>
					<label class="input-filled-label" for="blurItem">Add some text</label>
				</div>
				<!-- <button
                class="btn-neutral-container btn btn-circle btn-gradient"
                onclick={() => {pushItem(newBlur, blurItems)}}
                aria-label="Add"
            >
                <span class="icon-[fa6-solid--plus]"></span>
            </button> -->
			</div>
			<div class="divider divider-outline"></div>
			<ul class="h-85 list-inside overflow-y-scroll">
				{#each itemList as item, idx (idx)}
					<li class="title" transition:animation>
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
		</div>
	</div>
{/snippet}

<div class="w-full md:grid md:grid-cols-4 xl:gap-4">
	<div>
		<Heading>Blur</Heading>
		<div class="bg-base-150 shadow-outline h-100 w-90% rounded-lg p-2 shadow-inner">
			<div class="flex flex-row">
				<div class="title-small italic">Blur list</div>
				<div class="input-filled">
					<input
						type="text"
						placeholder="New blur item"
						bind:value={newBlur}
						onblur={() => pushItem(newBlur, blurItems)}
						onkeydown={(e) => {
							if (e.key === 'Enter') {
								pushItem(newBlur, blurItems);
							}
						}}
						class="input"
						id="blurItem"
					/>
					<label class="input-filled-label" for="blurItem">Add some text</label>
				</div>
				<!-- <button
                class="btn-neutral-container btn btn-circle btn-gradient"
                onclick={() => {pushItem(newBlur, blurItems)}}
                aria-label="Add"
            >
                <span class="icon-[fa6-solid--plus]"></span>
            </button> -->
			</div>
			<div class="divider divider-outline"></div>
			<ul class="h-85 list-inside overflow-y-scroll">
				{#each blurItems as item, idx (idx)}
					<li class="title" transition:blur>
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
		</div>
	</div>

    {@render box(blurData.name, blurData.animation, blurData.newItem, blurData.itemList)}
    {#each data as animation, idx   (idx)}
        {@render box(animation.name, animation.animation, animation.newItem, animation.itemList)}
    {/each}
	<div>
		<Heading>Crossfade</Heading>
	</div>
</div>
