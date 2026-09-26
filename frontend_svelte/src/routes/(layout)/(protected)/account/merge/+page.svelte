<script lang="ts">
	import Card from '$components/Card.svelte';
	import Heading from '$components/Heading.svelte';

	import type { ActionData, PageData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();
	const labels: Record<string, string> = {
		ai_enabled: 'Artificial intelligence enabled',
		theme_color: 'Theme color',
		theme_variant: 'Theme variant',
		contrast: 'Contrast'
	};
</script>

<Heading id="merge-accounts">Merge accounts</Heading>

<Card
	id="merge-warning"
	title="Merge Warning"
	extraClasses="bg-warning-container/30 text-warning-container-content/80  label-large border-warning-container"
>
	<span class="icon-[tabler--alert-triangle] size-6"></span> These provider identities belong to different
	application users. Confirming permanently merges them into the account that initiated linking and removes
	the other internal user.
</Card>

{#if form?.error}<div class="alert alert-error mb-4">{form.error}</div>{/if}

<form method="POST" action="?/confirm" class="flex max-w-full flex-col gap-5">
	{#each Object.entries(data.merge.settings) as [key, values] (key)}
		<fieldset class="fieldset rounded-box border-base-300 border p-4">
			<legend class="fieldset-legend">{labels[key] ?? key}</legend>
			<label class="label cursor-pointer justify-start gap-3">
				<input
					type="radio"
					class="radio"
					name={key}
					value="survivor"
					required
					checked={data.merge.defaults[key] === 'survivor'}
				/>
				<span>Current account: {JSON.stringify(values.survivor)}</span>
			</label>
			<div class="my-2"></div>
			<label class="label cursor-pointer justify-start gap-3">
				<input
					type="radio"
					class="radio"
					name={key}
					value="source"
					checked={data.merge.defaults[key] === 'source'}
				/>
				<span>Linked account: {JSON.stringify(values.source)}</span>
			</label>
		</fieldset>
	{/each}
	{#if Object.keys(data.merge.settings).length === 0}
		<p>No settings conflict. Memberships and access grants from both accounts will be preserved.</p>
	{/if}
	<div class="flex">
		<button
			class="btn btn-warning-container btn-gradient label btn shadow-outline mx-4 rounded-full shadow-sm"
			aria-label="Merge accounts"
			type="submit"
		>
			<span class="icon-[tabler--link] size-5"></span>
			Confirm permanent merge
		</button>
		<button
			class="btn btn-secondary-container btn-gradient label btn shadow-outline mx-4 rounded-full shadow-sm"
			aria-label="Merge accounts"
			type="submit"
			formaction="?/abandon"
		>
			<span class="icon-[tabler--x] size-5"></span>
			Cancel
		</button>
	</div>
</form>
