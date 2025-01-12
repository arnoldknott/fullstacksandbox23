<script lang="ts">
	// import { enhance } from '$app/forms';
	import Card from '$components/Card.svelte';
	import { type SubmitFunction } from '@sveltejs/kit';
	import type { DemoResourceWithCreationDate } from '$lib/types';
	// import { deserialize } from '$app/forms';
	import { enhance } from '$app/forms';

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
	let { demoResource }: { demoResource?: DemoResourceWithCreationDate } = $props();
	let id = $state(
		demoResource?.id || 'new_' + Math.random().toString(36).substring(2, 9)
	);
	let name = $state(demoResource?.name || undefined);
	let description = $state(demoResource?.description || undefined);
	let language = $state(demoResource?.language || undefined);
	let category = $state(demoResource?.category);
	let categoryId = $state(demoResource?.category_id || undefined);
	let tags = $state(demoResource?.tags || []);
	// let creation_date = $state<Date | undefined>(undefined);
	// if (demoResource && 'creation_date' in demoResource) {
	// 	creation_date = demoResource.creation_date;
	// }
	let creation_date = $state<Date |undefined>(demoResource?.creation_date);

	let edit = $state(demoResource ? false : true);

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

	const formAction = $derived(id.slice(0, 4) === 'new_' ? '?/post' : '?/put');

	const triggerSubmit = async () => {
		createUpdateForm?.requestSubmit();
	};

	const createOrUpdateResource: SubmitFunction = async ({ formData }) => {
		console.log('=== createOrUpdateResource triggered ===');

		if (id.slice(0, 4) !== 'new_') {
			formData.append('id', id);
		}
		// TBD: add validation here - if not all required fields are filled, otherwise cancel
		// and mark the missing fields invalid

		return async ({ result }) => {
			console.log('=== callback in submit function triggered ===');
			if (result.type === 'success') {
				if (id.slice(0, 4) === 'new_') {
					id = result.data?.id;
					console.log('=== result.data? ===');
					console.log(result.data);
					creation_date = result.data?.creationDate;
				}
			}
			// await applyAction(result);
			// update()
		};
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
					{creation_date?.toLocaleString('da-DK', { timeZone: 'CET' }) }
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
					id={categoryId}
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
								formaction="?/delete"><span class="icon-[tabler--trash]"></span>Delete</button
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
		<form
			method="POST"
			use:enhance={createOrUpdateResource}
			bind:this={createUpdateForm}
			id="form_{id}"
			action={formAction}
		>
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
		<!-- {#if form?.status == 'created'}
			Successfully created resource - remove this message again
		{/if} -->
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
{/snippet}
