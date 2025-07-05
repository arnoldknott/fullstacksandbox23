<script lang="ts">
	import Heading from '$components/Heading.svelte';
    import Box from './Box.svelte'
    import Slider from './Slider.svelte';
	import { blur, crossfade, draw, fade, fly, scale, slide  } from 'svelte/transition';
    import {flip} from 'svelte/animate';
    


    let blurParameters = $state({
        delay: 0,
        duration: 300,
        // easing: (t: number) => t, // Easing function not implemented in this demo
        amount: 5,
        opacity: 0.5,
    });
	let newBlur = $state<string>('');
	let blurItems = $state<string[]>([]);

    let crossfadeParameters = $state({
        delay: 0,
        duration: 300,
        // easing: (t: number) => t, // Easing function not implemented in this demo
    })
    const [sendCrossfade, receiveCrossfade] = crossfade({...crossfadeParameters});
	let left = $state([ {name: 'Item 1'}, {name: 'Item 2'}, {name: 'Item 3'}, {name: 'Item 4'}, {name: 'Item 5'} ]);
    let right = $state([ {name: 'Item A'}, {name: 'Item B'}, {name: 'Item C'}, {name: 'Item D'}, {name: 'Item E'} ]);

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
    {#snippet blurHeader()}
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
    <div class="body-small"><code>easing</code> not implemented.</div>
    <div class="divider divider-outline py-2"></div>
    <div class="title-small italic">Playground:</div>
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
</div>
{/snippet}
    <Box title="Blur" header={blurHeader}>
        <ul class="h-38 py-2 list-inside overflow-y-scroll">
            {#each blurItems as item, idx (idx)}
                <li class="title" transition:blur={{...blurParameters}}>
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

    {#snippet crossfadeHeader()}
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
    <div class="body-small"><code>easing</code> not implemented.</div>
    <div class="body-small">also uses <code>animate:flip</code>.</div>
    <div class="divider divider-outline py-2"></div>
    <div class="title-small italic">Playground:</div>
    {/snippet}

    <Box title="Crossfade" header={crossfadeHeader}>
        <div class="grid grid-cols-2">
            <ul class="h-85 w-full list-inside overflow-y-scroll">
                {#each left as item (item)}
                <li class="title" animate:flip={{ ...crossfadeParameters }}>
                    <button
                        onclick={() => {
                        left = left.filter((i) => i !== item);
                        right.push(item)
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
                <li class="title" animate:flip={{ ...crossfadeParameters }}>
                    <button
                        onclick={() => {
                        right = right.filter((i) => i !== item);
                        left.push(item)
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

    <Box title="Draw">
        TBD
    </Box>

    <Box title="Fade">
        <div class="input-filled">
            <input
                type="text"
                placeholder="New fade item"
                bind:value={newFade}
                onblur={() => pushItem(newFade, fadeItems)}
                onkeydown={(e) => {
                    if (e.key === 'Enter') {
                        pushItem(newFade, fadeItems);
                    }
                }}
                class="input"
                id="fadeItem"
            />
            <label class="input-filled-label" for="fadeItem">Add some text</label>
        </div>
        <ul class="h-85 list-inside overflow-y-scroll">
            {#each fadeItems as item, idx (idx)}
                <li class="title" transition:fade>
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
