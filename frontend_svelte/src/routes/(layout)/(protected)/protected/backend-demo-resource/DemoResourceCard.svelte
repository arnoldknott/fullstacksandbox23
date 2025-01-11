<script lang="ts">
	// import { enhance } from '$app/forms';
	import Card from '$components/Card.svelte';
	import { error, type SubmitFunction } from '@sveltejs/kit';
	import type { DemoResource, DemoResourceWithCreationDate } from '$lib/types';
	import { deserialize } from '$app/forms';
	import { enhance } from '$app/forms';
	import type { ActionData } from './$types';

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
	let {
		demoResource,
		edit = false,
		form
	}: { demoResource: DemoResource | DemoResourceWithCreationDate; edit?: boolean, form?: ActionData } = $props();
	let id = $state(demoResource.id || form?.id ||  'new_' + Math.random().toString(36).substring(2, 9));
	let name = $state(demoResource.name);
	let description = $state(demoResource.description);
	let language = $state(demoResource.language);
	let category = $state(demoResource?.category);
	let category_id = $state(demoResource.category_id);
	let tags = $state(demoResource.tags || []);
	let creation_date = $state<Date | undefined>(undefined);
	if ('creation_date' in demoResource) {
		creation_date = demoResource.creation_date;
	}

	// use "ready" when the data is loaded
	// use "loading" when the data is being fetched - TBD
	// use "pending" when the data is being saved or not all required fields are filled
	// use "deleted" when the data is deleted
	// use "error" when the data is in an error state
	let status = $state('ready');

	// let edit = $state(false);
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
	let createUpdateForm = $state<HTMLFormElement | null>(null);

	const createResource = async () => {
		// check if all required fields are filled
		if (name) {
			//  === All of this worked - without form, but seems overkill to do in JavaScript, if Form actions are available and can do the job.
			const formData = new FormData();
			formData.append('name', name);
			if (description) {
				formData.append('description', description);
			}
			if (language) {
				formData.append('language', language);
			}
			if (category_id) {
				formData.append('category_id', category_id);
			}
			const response = await fetch(`?/post`, {
				method: 'POST',
				body: formData
			});
			// if (response.status === 200) {
			// console.log('=== response ===');
			// console.log(response);
			const result = deserialize(await response.text());
			if (result.type === 'success') {
				// console.log('=== result.data?.id ===');
				// console.log(result.data?.id);
				// console.log('=== typeof result.data?.id ===');
				// console.log(typeof result.data?.id);
				id = result.data?.id as string;

				// result.data?.id ? id = result.data.id : null;
			} else {
				card.remove();
				throw error(response.status || 404, 'Failed to create resource');
			}
			// === end of what worked without form
			

		}
	};

	const formAction = $derived(id.slice(0,4) === "new_" ? "?/post" : "?/put")

	const triggerSubmit = async () => {
		createUpdateForm?.requestSubmit();
	};

	const createOrUpdateResource: SubmitFunction = async ({formElement, formData}) => {
		console.log("=== createOrUpdateResource triggered ===");
		if (id.slice(0,4) !== "new_") {
			formData.append('id', id);
		}
		// add validation here - if not all required fields are filled, otherwise cancel and mark the missing fields invalid
		// const submitButton = document.createElement('button');
        // submitButton.type = 'submit';
        // // submitButton.style.display = 'none';
		// submitButton.classList.add('hidden');
		// submitButton.setAttribute('form', `form_${id}`);


		// if (id.slice(0,4) === "new_") {
		// 	submitButton.formAction = `?/post`;

		// 	// createResource();
		// } else {
		// 	submitButton.formAction = `?/put`;
		// 	submitButton.name = 'id';
		// 	submitButton.value = id;
		// }
		// formElement.appendChild(submitButton);
		// formElement.requestSubmit(submitButton);
		// formElement.removeChild(submitButton);

		return async ({result, update}) => {
			console.log("=== callback in submit function triggered ===");
			console.log("=== result ===");
			console.log(result);
			// if result.status=
			// console.log('=== result.data ===');
			// console.log(result.data.status);
			if (id.slice(0,4) === "new_") {
				id = result.data.id;
			}
			// update()
		}
		// if (id.slice(0,4) === "new_") {

		// }


			// This code could be shared with createResource, but should be removed anyways, when form actions are available.

			//  === All of this worked - without form, but seems overkill to do in JavaScript, if Form actions are available and can do the job.
			// const formData = new FormData();
			// formData.append('id', id);
			// formData.append('name', name);
			// if (description) {
			// 	formData.append('description', description);
			// }
			// if (language) {
			// 	formData.append('language', language);
			// }
			// if (category_id) formData.append('category_id', category_id);
			// const response = await fetch(`?/put`, {
			// 	method: 'POST',
			// 	body: formData
			// });
			// if (response.status === 200) {
			// 	// console.log('=== response ===');
			// 	// console.log(response);
			// 	// await update();
			// } else {
			// 	throw error(response.status || 404, 'Failed to update resource');
			// }
			// === end of what worked without form
		// }
	};

	// const deleteResource = ( ) => {
	//     card.remove();
	// }
	const deleteResource = async () => {
		// TBD: check if successfully deleted"
		// const formData = new FormData();
		// if (!id || id.slice(0,3) == "new_") {
		// 	throw error(404, 'No id available');
		// } else {
		// 	formData.append('id', id);
		// 	const response = await fetch(`?/delete`, {
		// 		method: 'POST',
		// 		body: formData
		// 	});
		// 	if (response.status === 200) {
		// 		card.remove();
		// 	} else {
		// 		throw error(response.status || 404, 'Failed to delete resource');
		// 	}
		// }
	};
</script>

{#snippet header()}
	<div class="flex justify-between">
		<div>
			{#if edit}
				<div class="relative">
					<input
						type="text"
						class="border-content text-title-small md:text-title base-content card-title input input-filled peer"
						id="name_{id}"
						form="form_{id}"
						name="name"
						onblur={() => triggerSubmit()}	
						bind:value={name}
						placeholder="Name the demo resource"
					/>
					<label
						class="text-label-small md:text-label input-filled-label"
						style="color: oklch(var(--bc));"
						for="name_{id}">Name</label
					>
					<span class="input-filled-focused" style="background-color: oklch(var(--bc));"></span>
				</div>
			{:else}
				<h5 class="text-title-small md:text-title lg:text-title-large base-content card-title">
					{name}
				</h5>
				<p class="text-label-small md:text-label text-secondary">
					{creation_date?.toLocaleString('da-DK', { timeZone: 'CET' })}
				</p>
			{/if}
			<!-- <h5
				class="text-title-small md:text-title lg:text-title-large base-content card-title {edit
					? `ring-2 ring-info`
					: ``}"
				contenteditable="true"
				oninput={(event: Event) => (name = (event.target as HTMLElement).innerText)}
				onblur={() => createOrUpdateResource()}
			>
				{name}
			</h5> -->
		</div>
		<div class="flex flex-row items-start gap-4">
			{#if category}
				<span
					id={category_id}
					class="text-label-small md:text-label lg:text-label-large badge badge-secondary shadow-sm shadow-secondary"
				>
					{category}
				</span>
			{/if}
			{#if flag}
				<span class="icon-[twemoji--flag-{flag}] size-6"></span>
			{/if}
			<div class="dropdown relative inline-flex rtl:[--placement:bottom-end]">
				<span
					id="dropdown-menu-icon"
					class="dropdown-toggle icon-[tabler--dots-vertical] size-6"
					role="button"
					aria-haspopup="menu"
					aria-expanded="false"
					aria-label="Dropdown"
				></span>
				<!-- <button id="dropdown-menu-icon" type="button" class="dropdown-toggle btn btn-square btn-text btn-secondary" aria-haspopup="menu" aria-expanded="false" aria-label="Dropdown">
					<span class="icon-[tabler--dots-vertical] size-6"></span>
				</button> -->
				<ul
					class="dropdown-menu hidden bg-base-300 shadow-sm shadow-outline dropdown-open:opacity-100"
					role="menu"
					aria-orientation="vertical"
					aria-labelledby="dropdown-menu-icon"
				>
					<li class=" items-center">
						<button
							class="btn dropdown-item btn-text justify-start"
							aria-label="Edit Button"
							onclick={() => (edit ? (edit = false) : (edit = true))}
							><span class="icon-[material-symbols--edit-outline-rounded]"></span> Edit</button
						>
					</li>
					<li class="items-center">
						<button class="btn dropdown-item btn-text justify-start"
							><span class="icon-[tabler--share-2]"></span>Share</button
						>
					</li>
					<li class="dropdown-footer gap-2">
						<form method="POST" use:enhance={() => card.remove()}>
							<button
								class="btn dropdown-item btn-error btn-text justify-start"
								aria-label="Delete Button"
								name="id"
								value={id}
								formaction="?/delete"
								><span class="icon-[tabler--trash]"></span>Delete</button
							>
						</form>
						<!-- onclick={deleteResource} -->
					</li>
				</ul>
			</div>
		</div>
	</div>
{/snippet}

<Card bind:this={card} {id} {header} {footer}>
	{#if edit}
		<form method="POST" use:enhance={createOrUpdateResource} bind:this={createUpdateForm} id="form_{id}" action={formAction}>
			<div class="relative">
				<textarea
					class="text-body-small md:text-body textarea peer textarea-filled border-primary text-primary-container-content"
					id="description_{id}"
					onblur={() => triggerSubmit()}
					name="description"
					bind:value={description}
					placeholder="Describe the demo resource here."
				></textarea>
				
				<label
					class="text-label-small md:text-label textarea-filled-label"
					style="color: oklch(var(--p));"
					for="description_{id}">Description</label
				>
				<span class="textarea-filled-focused" style="background-color: oklch(var(--p));"></span>
			</div>
		</form>
	{:else}
		{#if form?.status == "created"}
			Successfully created resource - remove this message again
		{/if}
		<p class="text-body-small md:text-body text-primary-container-content">
			{description || 'No description available'}
		</p>
	{/if}
</Card>

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
			<!-- <button
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
			<button class="btn-success-container btn btn-circle btn-gradient" aria-label="Share Button">
				<span class="icon-[tabler--share-2]"></span>
			</button> -->
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
			<!-- <button
				class="btn-error-container btn btn-circle btn-gradient"
				aria-label="Delete Button"
				onclick={deleteResource}
			>
				<span class="icon-[tabler--trash]"></span>
			</button> -->
			{#if edit}
				<button
					class="btn-success-container btn btn-circle btn-gradient"
					onclick={() => (edit = false)}
					aria-label="Done"
				>
					<span class="icon-[mingcute--check-2-fill]"></span>
				</button>
			{/if}
		</div>
	</div>
{/snippet}
