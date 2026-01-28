<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import type { PageData } from './$types';
	import type { Question } from '$lib/types';
	import { resolve } from '$app/paths';
	let { data }: { data: PageData } = $props();

	const allQuestions: Question[] = data.questionsData || [];
</script>

<Heading id="overview-presentations">Overview of existing questions</Heading>

<div class="w-full overflow-x-auto">
	<table class="table">
		<thead>
			<tr>
				<th>Question</th>
				<th>Id</th>
				<th>Link</th>
			</tr>
		</thead>
		<tbody>
			{#each allQuestions as question (question.id)}
				<tr>
					<td>{question.question}</td>
					<td>{question.id}</td>
					<td
						><a href={resolve(`/presentations/questions/setup`) + `?question-id=${question.id}`}
							>Link</a
						></td
					>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
