<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import { blur, crossfade, draw, fade, fly, scale, slide  } from 'svelte/transition';
    const [send, receive] = crossfade({});


	let newBlur = $state<string>('');
	let blurItems = $state<string[]>([]);

	let left = $state([ 'Item 1', 'Item 2', 'Item 3' ]);
    let right = $state([ 'Item A', 'Item B', 'Item C' ]);

    let newDraw = $state<string>('');
    let drawItems = $state<string[]>([]);

    let newFade = $state<string>('');
    let fadeItems = $state<string[]>([]);

    let newFly = $state<string>('');
    let flyItems = $state<string[]>([]);

    let newScale = $state<string>('');
    let scaleItems = $state<string[]>([]);

    let newSlide = $state<string>('');
    let slideItems = $state<string[]>([]);

	const pushItem = (newItem: string, list: string[]) => {
        console.log('Pushing item:', newItem, 'to list:', list);
		if (newItem.trim() !== '') {
			list.push(newItem);
			newBlur = '';
		}
	};
</script>

<Heading>Transitions</Heading>

<div class="w-full md:grid sm md:grid-cols-4 md:gap-4">
	<div class="w-full">
		<div class="title-large text-center">Blur</div>
		<div class="bg-base-150 shadow-outline h-100 w-full rounded-lg p-2 shadow-inner">
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

	<div class="w-full">
		<div class="title-large text-center">Crossfade</div>
        <div class="bg-base-150 shadow-outline h-100 w-full rounded-lg p-2 shadow-inner">
            <div class="title-small italic">Crossfade Lists</div>
			<div class="divider divider-outline"></div>
            <div class="grid grid-cols-2 gap-8">
                <ul class="h-85 list-inside overflow-y-scroll">
                    {#each left as item, idx (idx)}
                        <li class="title">
                        <button
                            onclick={() => {
                            left = left.filter((i) => i !== item);
                            right.push(item)
                            }}
							in:receive={{ key: item, duration: 300 }}
							out:send={{ key: item, duration: 300 }}>
							{item}
						</button>
					</li>
                    {/each}
                </ul>
                <ul class="h-85 list-inside overflow-y-scroll">
                    {#each right as item, idx (idx)}
                    <li class="title">
                        <button
                            onclick={() => {
                            right = right.filter((i) => i !== item);
                            left.push(item)
                            }}
							in:receive={{ key: item, duration: 300 }}
							out:send={{ key: item, duration: 300 }}>
							{item}
						</button>
					</li>
                    {/each}
                </ul>
            </div>
			
		</div>
	</div>
</div>
