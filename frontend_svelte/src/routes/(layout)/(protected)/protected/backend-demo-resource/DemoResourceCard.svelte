<script lang="ts">
	// import { enhance } from '$app/forms';
	import Card from '$components/Card.svelte';
	import { error } from '@sveltejs/kit';
	type DemoResource = {
		id: string;
		name: string;
		description?: string;
		language: string;
		category?: string;
		category_id?: string;
		tags: string[];
	};
	// let {
	// 	id,
	// 	name,
	// 	description,
	// 	language,
	// 	category,
	// 	category_id,
	// 	tags
	// }: {
	// 	id: string;
	// 	name: string;
	// 	description?: string;
	// 	language: string;
	// 	category?: string;
	// 	category_id?: string;
	// 	tags: string[];
	// } = $props();
	let { demoResource }: { demoResource: DemoResource } = $props();
	let id = $state(demoResource.id);
	let name = $state(demoResource.name);
	let description = $state(demoResource.description);
	let language = $state(demoResource.language);
	let category = $state(demoResource.category);
	let category_id = $state(demoResource.category_id);
	let tags = $state(demoResource.tags);

	let edit = $state(false);
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

	const updateResource = async () => {
		console.log('=== updateResource ===');
		console.log(name);
		const formData = new FormData();
		formData.append('id', id);
		formData.append('name', name);
		description ? formData.append('description', description) : null;
		formData.append('language', language);
		const response = await fetch(`?/put`, {
			method: 'POST',
			body: formData
		});
		if (response.status === 200) {
			console.log('=== response ===');
			console.log(response);
			// await update();
		} else {
			throw error(response.status || 404, 'Failed to update resource');
		}
	};

	// const deleteResource = ( ) => {
	//     card.remove();
	// }
	const deleteResource = async () => {
		const formData = new FormData();
		formData.append('id', id);
		const response = await fetch(`?/delete`, {
			method: 'POST',
			body: formData
		});
		if (response.status === 200) {
			card.remove();
		} else {
			throw error(response.status || 404, 'Failed to delete resource');
		}
	};
</script>

{#snippet header()}
	<div class="flex justify-between">
		<div>
			<h5
				class="text-title-small md:text-title lg:text-title-large base-content card-title {edit
					? `ring-2 ring-info`
					: ``}"
				contenteditable="true"
				oninput={(event: Event) => (name = (event.target as HTMLElement).innerText)}
				onblur={() => updateResource()}
			>
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
			<!-- <form
				action="?/put"
				method="POST"
				use:enhance={() => {
					return async ({ result, update }) => {
						console.log('=== result ===');
						console.log(result);
						if (result.status === 204) {
							await update();
						} else {
							throw error(result.status || 404, 'Failed to update resource');
						}
					};
				}}
			>
				<input type="hidden" name="id" value={id} />
				<button
					class="btn-info-container btn btn-circle btn-gradient"
					onclick={() => (edit ? (edit = false) : (edit = true))}
					aria-label="Edit Button"
				>
					<span class="grid place-items-center">
						<span class="icon-[material-symbols--edit-outline-rounded] col-start-1 row-start-1"
						></span>
						<span class="icon-[fe--disabled] col-start-1 row-start-1 size-6 {edit ? '' : 'hidden'}"
						></span>
					</span>
				</button>
			</form> -->
			<button
				class="btn-info-container btn btn-circle btn-gradient"
				onclick={() => (edit ? (edit = false) : (edit = true))}
				aria-label="Edit Button"
			>
				<span class="grid place-items-center">
					<span class="icon-[material-symbols--edit-outline-rounded] col-start-1 row-start-1"
					></span>
					<span class="icon-[fe--disabled] col-start-1 row-start-1 size-6 {edit ? '' : 'hidden'}"
					></span>
				</span>
			</button>
			<button
				class="btn-success-container btn btn-circle btn-gradient"
				aria-label="Share Button"
			>
				<span class="icon-[tabler--share-2]"></span>
			</button>
			<!-- <form action="?/delete" method="POST" use:enhance={() => 
                    {
                        return async ({result, update}) => {
                            if (result.status === 204){
                                deleteResource()
                                await update()
                            } else {
                                throw  error(result.status || 404, 'Failed to delete resource')
                            }
                        }
                    }
                }>
                <input type="hidden" name="id" value={id} /> 
                <button 
                    class="btn-error-container btn btn-circle btn-gradient"
                    type="submit"
                    aria-label="Delete Button"
                    formaction="?/delete"
                >
                    <span class="icon-[tabler--trash]"></span>
                </button>
            </form> -->
			<button
				class="btn-error-container btn btn-circle btn-gradient"
				aria-label="Delete Button"
				onclick={deleteResource}
			>
				<span class="icon-[tabler--trash]"></span>
			</button>
		</div>
	</div>
{/snippet}

<Card bind:this={card} {id} {header} {footer}>
	<p
		class="text-body-small md:text-body text-primary-container-content {edit
			? `ring-2 ring-info`
			: ``}"
		contenteditable={edit}
	>
		{description || 'No description available'}
	</p>
</Card>
