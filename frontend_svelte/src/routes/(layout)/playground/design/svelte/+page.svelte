<script lang="ts">
	import Heading from '$components/Heading.svelte';
	// import { blur, crossfade, draw, fade, fly, scale, slide } from 'svelte/transition';
    import { blur } from 'svelte/transition';

	let newBlur = $state<string>('');
	let blurItems = $state<string[]>([]);

	const pushItem = (newItem: string, list: string[]) => {
		if (newItem.trim() !== '') {
			list.push(newItem);
			newBlur = '';
		}
	};
</script>

{#snippet box()}{/snippet}

<div class="w-full md:grid md:grid-cols-4 xl:gap-4">
	<div>
		<Heading>Blur</Heading>
		<div class="bg-base-150 shadow-outline h-100 w-80 rounded-lg p-2 shadow-inner">
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

	<div>
		<Heading>Crossfade</Heading>
	</div>
</div>
