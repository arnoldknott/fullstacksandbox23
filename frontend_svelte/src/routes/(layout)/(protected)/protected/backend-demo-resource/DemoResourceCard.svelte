<script lang="ts">
	import Card from '$components/Card.svelte';
	import { unmount } from 'svelte';
	// type DemoResource = {
	//     id: string;
	//     name: string;
	//     description?: string;
	//     language?: string;
	// }
	let {
		id,
		name,
		description,
		language,
		category,
		category_id,
		tags
	}: {
		id: string;
		name: string;
		description?: string;
		language: string;
		category?: string;
		category_id?: string;
		tags: string[];
	} = $props();
	// let { id, name, description, language, category, category_id, tags }: { id: string, name: string; description: string, language: string; category?: string, category_id?: string, tags: string[] } = $props();
	let flag = $state(
		language === 'en-US'
			? 'united-states'
			: language === 'da-DK'
				? 'denmark'
				: language === 'de-DE'
					? 'germany'
					: false
	);
	let card: Card;

    const deleteResource = () => {
        card.remove()
    }

</script>

{#snippet header()}
	<div class="flex justify-between">
		<div>
			<h5 class="text-title-small md:text-title lg:text-title-large base-content card-title">
				{name}
			</h5>
		</div>
		<div>
			{#if category}
				<span
					id={category_id}
					class="text-label-small md:text-label lg:text-label-large badge badge-secondary shadow-sm shadow-secondary"
				>
					{category}
				</span>
			{/if}
			{#if flag}
				<span class={`icon-[twemoji--flag-${flag}] size-6`}></span>
			{/if}
		</div>
	</div>
{/snippet}

{#snippet footer()}
	<div class="card-actions flex justify-between">
		<div>
			{#each tags as tag}
				<span
					class="text-label-small md:text-label lg:text-label-large badge badge-neutral shadow-sm shadow-neutral"
					>{tag}</span
				>
			{/each}
		</div>
		<div class="flex gap-2">
			<button class="btn-info-container btn btn-circle btn-gradient" aria-label="Edit Button">
				<span class="icon-[material-symbols--edit-outline-rounded]"></span>
			</button>
            <button
                class="btn-success-container btn btn-circle btn-gradient"
                aria-label="Share Button"
            >
                <span class="icon-[tabler--share-2]"></span>
            </button>
            <form action="?/delete" method="POST"> 
                <button 
                    class="btn-error-container btn btn-circle btn-gradient"
                    type="submit"
                    aria-label="Delete Button"
                    
                >
                    <span class="icon-[tabler--trash]"></span>
                </button>
            </form>
		</div>
	</div>
{/snippet}


<Card bind:this={card} {id} {header} {footer}>
	<p class="text-body-small md:text-body text-primary-container-content">
		{description || 'No description available'}
	</p>
</Card>
