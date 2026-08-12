<script lang="ts">
	// import type { Question } from '$lib/types';
	import { resolve } from '$app/paths';
	import Heading from '$components/Heading.svelte';

	import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();

	// const allQuestions: Question[] = $derived(data.questionsData || []);
	// const allQuestions: Question[] = data.questionsData || [];
	// const allQuestions = (): Question[] => data.questionsData || [];
</script>

<Heading id="overview-presentations">Overview of existing questions</Heading>

<div class="w-full overflow-x-auto">
	<table class="table">
		<thead>
			<tr>
				<th>Question</th>
				<th>Id</th>
			</tr>
		</thead>
		<tbody>
			{#each data.questionsData as question (question.id)}
				<!-- {#each allQuestions as question (question.id)} -->
				<!-- {#each allQuestions() as question (question.id)} -->
				<tr>
					<td>
						<a href={resolve(`/question/setup/${question.id}`)}>
							<!-- <a href={resolve(`/question/setup`) + `?question-id=${question.id}`}> -->
							<button class="btn btn-primary-container btn-gradient shadow-outline shadow-sm">
								<span class="icon-[codicon--question]"></span>
								{question.question}
							</button></a
						>
					</td>
					<td>{question.id}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
