<script lang="ts" module>
	import type { Snippet } from 'svelte';

	import type { AnyEntityExtended } from '$lib/types';

	/** Content displayed in a table column header. Use {@link text}, {@link snippet}, {@link icon}, or {@link countIcon}. */
	export type TableHeader =
		{ text: string } | { snippet: Snippet } | { icon: string; count?: boolean };
	/** Content displayed in a table cell for an entity of type `T`. */
	export type TableCell<T extends AnyEntityExtended> =
		| { snippet: Snippet<[T]> }
		| { field: keyof T }
		| { value: (entity: T) => string | number | null | undefined };
	/** Defines one table column, including its header, cell content, and optional Tailwind CSS classes. */
	export type TableColumn<T extends AnyEntityExtended> = {
		header: TableHeader;
		cell: TableCell<T>;
		headerClass?: string;
		cellClass?: string;
	};

	/**
	 * Creates a text header configuration.
	 * @param text Header label, for example `text('Source')`.
	 */
	export const text = (text: string): TableHeader => ({ text });
	/**
	 * Creates an Iconify icon header configuration.
	 * @param icon Iconify icon name, for example `icon('tabler:file')`.
	 */
	export const icon = (icon: string): TableHeader => ({ icon });
	/**
	 * Creates an Iconify header with a `#` count marker.
	 * @param icon Iconify icon name, for example `countIcon('codicon:question')`.
	 */
	export const countIcon = (icon: string): TableHeader => ({ icon, count: true });

	type SnippetArguments<T extends AnyEntityExtended | undefined> = T extends AnyEntityExtended
		? [T]
		: [];

	/**
	 * Wraps a Svelte snippet for a header or cell.
	 * @param snippet A no-argument header snippet or a cell snippet that receives the current entity.
	 */
	export const snippet = <T extends AnyEntityExtended | undefined = undefined>(
		snippet: Snippet<SnippetArguments<T>>
	) => ({ snippet });

	/**
	 * Creates a cell configuration that displays a direct entity field.
	 * @param field Key of the entity to display, for example `field<PresentationExtended>('path')`.
	 */
	export const field = <T extends AnyEntityExtended>(field: keyof T): TableCell<T> => ({ field });
	/**
	 * Creates a cell configuration from a value-producing callback.
	 * @param value Receives the current entity and returns the text or number to display.
	 */
	export const value = <T extends AnyEntityExtended>(
		value: (entity: T) => string | number | null | undefined
	): TableCell<T> => ({ value });
</script>

<script lang="ts" generics="T extends AnyEntityExtended">
	import Icon from '@iconify/svelte';
	import { onDestroy, onMount } from 'svelte';
	import { flip } from 'svelte/animate';
	import { fade } from 'svelte/transition';

	import type { EntityContainerInterface } from '$lib/entityContainer.svelte';

	let {
		columns,
		entityContainer,
		selectionBoxes = true
	}: {
		columns: TableColumn<T>[];
		entityContainer: EntityContainerInterface<T>;
		selectionBoxes?: boolean;
	} = $props();

	let selectAll = $state(false);

	onMount(() => {
		if (selectionBoxes) entityContainer?.addSelection('selected');
	});
	onDestroy(() => {
		if (selectionBoxes) entityContainer?.removeSelection('selected');
	});
</script>

<!-- {#snippet countIconHeader(icon: string)}
	# <span class="{icon} size-4"></span>
{/snippet} -->

<div class="overflow-x-auto">
	<table class="table w-full overflow-hidden rounded-2xl">
		<thead>
			<tr
				class="shadow-base-shadow bg-base-300 inset-ring-outline-variant rounded-t-2xl shadow inset-ring *:first:rounded-tl-2xl *:last:rounded-tr-2xl"
			>
				{#if selectionBoxes}
					<th>
						<input
							id="select-all-presentations"
							type="checkbox"
							class="checkbox checkbox-sm checkbox-secondary"
							bind:checked={selectAll}
							onchange={(event) => {
								if ((event.target as HTMLInputElement).checked) {
									selectAll = true;
									entityContainer?.entities?.forEach((presentation) => {
										entityContainer?.selections['selected']?.push(presentation.id);
									});
								} else {
									selectAll = false;
									entityContainer?.selections['selected']?.splice(0);
								}
							}}
						/>
					</th>
				{/if}
				{#each columns as column (column.header)}
					<th class={`title text-base-content font-medium normal-case ${column.headerClass ?? ''}`}>
						{#if 'snippet' in column.header}
							{@render column.header.snippet()}
						{:else if 'icon' in column.header}
							<span class="inline-flex items-center gap-2 whitespace-nowrap">
								{#if column.header.count}#{/if}<Icon
									icon={column.header.icon}
									class="ml-0 size-5"
									inline
								/>
							</span>
						{:else}
							{column.header.text}
						{/if}
					</th>
				{/each}
				<!-- <th class="title text-base-content w-3/5 font-medium normal-case">Id / Slug</th>
				<th class="title text-base-content text-center font-medium normal-case">Source</th>
				<th class="title text-base-content text-center font-medium normal-case">Access</th>
				<th class="title text-base-content text-center font-medium normal-case"
					># <span class="icon-[codicon--question] size-4"></span></th
				>
				<th class="title text-base-content text-center font-medium normal-case"
					># <span class="icon-[line-md--link] size-4"></span></th
				>
				<th class="title text-base-content text-center font-medium normal-case"
					># <span class="icon-[tabler--file] size-4"></span></th
				>
				<th class="title text-base-content text-center font-medium normal-case"
					><span class="icon-[fluent-mdl2--offline-storage] size-4 text-center"></span></th
				>
				<th
					class="title text-base-content w-px text-center font-medium whitespace-nowrap normal-case"
					>Actions</th
				> -->
			</tr>
			{#if entityContainer?.selections['selected']?.length > 1}
				<tr
					// transition:slide={{ duration: 300 }}
					class="label bg-base-300 inset-ring-outline-variant font-medium normal-case inset-ring"
				>
					<th></th>
					<th colspan={8}>
						add sort, search, filter, actions for multiple selected presentations</th
					>
				</tr>
			{/if}
		</thead>
		<tbody class="bg-base-150 shadow-base-shadow rounded-b-2xl shadow shadow-inner">
			{#if (entityContainer?.entities?.length ?? 0) === 0}
				<tr>
					<td colspan={9} class="text-center">
						No presentations yet. Create one by sending a POST request to the /presentation
						endpoint.
					</td>
				</tr>
			{:else}
				{#each entityContainer.entities as entity (entity.id)}
					<tr
						animate:flip={{ duration: 300 }}
						transition:fade={{ duration: 300 }}
						class="hover:bg-base-250 last:hover:rounded-b-2xl"
					>
						{#if selectionBoxes}
							<td>
								<input
									id="select-all-presentations"
									type="checkbox"
									class="checkbox checkbox-sm checkbox-secondary"
									onchange={(event) => {
										if ((event.target as HTMLInputElement).checked) {
											entityContainer?.addToSelection('selected', [entity.id]);
										} else {
											selectAll = false;
											entityContainer?.removeFromSelection('selected', [entity.id]);
										}
									}}
									checked={entityContainer?.selections['selected']?.includes(entity.id) ?? false}
								/>
							</td>
						{/if}
						{#each columns as column (column.cell)}
							<td class={`text-base-content ${column.cellClass ?? ''}`}>
								{#if 'snippet' in column.cell}
									{@render column.cell.snippet(entity)}
								{:else if 'field' in column.cell}
									{String(entity[column.cell.field] ?? '')}
								{:else}
									{column.cell.value(entity) ?? ''}
								{/if}
							</td>
						{/each}
						<!-- <td class="max-w-0">
							<IdBadge id={presentation.id} />
							<a
								href={resolve('/(layout)/presentation/[slug]', {
									slug: presentation?.path?.substring(1) || presentation.id
								})}
								aria-label={`Setup presentation ${presentation.path || presentation.id}`}
								class="link link-primary link-animated block truncate"
							>
								{presentation.path || presentation.id}
							</a>
						</td>
						<td class="text-center"><IdBadge id="intern" /></td>
						<td class="text-center">[Access]</td>
						<td class="text-center">{presentation.questions?.length ?? 0}</td>
						<td class="text-center">[Num]</td>
						<td class="text-center">[Num]</td>
						<td class="text-center">[Size]</td>
						<td class="w-px py-1 text-center align-middle whitespace-nowrap">
							<ActionButtons
								resourceId={presentation.id}
								accessRight={socketioPresentations?.accessRights[presentation.id]}
								socketio={socketioPresentations}
							/>
						</td> -->
					</tr>
				{/each}
			{/if}
		</tbody>
	</table>
</div>
