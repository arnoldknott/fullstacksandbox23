<script lang="ts">
	import { slide } from 'svelte/transition';

	import { page } from '$app/state';
	import Card from '$components/Card.svelte';

	let hideNewQuestionCard: boolean = $state(
		!(page.url.searchParams.get('new-question') === 'true')
	);
	// let hideNewLinkCard: boolean = $state(!(page.url.searchParams.get('new-link') === 'true'));
	// let hideNewDrawingCard: boolean = $state(!(page.url.searchParams.get('new-drawing') === 'true'));
	// let hideNewFileCard: boolean = $state(!(page.url.searchParams.get('new-file') === 'true'));
</script>

{#if hideNewQuestionCard}
	<button
		transition:slide={{ duration: 600 }}
		class="btn btn-primary-container btn-gradient btn-sm shadow-outline rounded-full shadow-sm transition-all duration-600"
		aria-label="Add new question"
		onclick={() => (hideNewQuestionCard = false)}
	>
		<span class="icon-[fa6-solid--plus] size-4"></span>Add
	</button>
{/if}

<Card
	id="add-questions"
	title="Add Questions"
	closeButton
	extraClasses="label-large"
	bind:hidden={hideNewQuestionCard}
>
	Add questions drawer with tabs for new and existing, where the existing questions get the button
	to copy and link. Also a copy all selected and link all selected.
</Card>

<Card id="linked-questions" title="Linked Questions" extraClasses="label-large">
	<p>
		Potentially as an accordion with the answers in the panel? Adding a question and opening sidebar
		to select existing questions - for mode copy (don't keep the original answers and don't keep in
		sync) or link (keeps answers in sync)
	</p>
</Card>
