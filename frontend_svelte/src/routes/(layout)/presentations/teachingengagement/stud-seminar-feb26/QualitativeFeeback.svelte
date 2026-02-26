<script lang="ts">
	import ChatBubble from '$components/ChatBubble.svelte';
	// import CourseSelector from './CourseSelector.svelte';
	import { marked } from 'marked';
	import { onDestroy } from 'svelte';

	type FeedbackColor =
		| 'primary'
		| 'secondary'
		| 'accent'
		| 'neutral'
		| 'info'
		| 'success'
		| 'warning'
		| 'error';

	type FeedbackMessage = {
		id: string;
		content: string;
		language?: string;
		questions?: unknown[];
	};

	// type ParsedFeedbackMessage = FeedbackMessage & {
	// 	course: string;
	// 	year: string;
	// 	number: number;
	// 	markdown: string;
	// };

	// const badgeClasses: Record<FeedbackColor, { solid: string; container: string }> = {
	// 	primary: {
	// 		solid: 'badge badge-sm badge-primary label-small shadow-outline shadow-inner',
	// 		container: 'badge badge-sm badge-primary-container label-small shadow-outline shadow-inner'
	// 	},
	// 	secondary: {
	// 		solid: 'badge badge-sm badge-secondary label-small shadow-outline shadow-inner',
	// 		container: 'badge badge-sm badge-secondary-container label-small shadow-outline shadow-inner'
	// 	},
	// 	accent: {
	// 		solid: 'badge badge-sm badge-accent label-small shadow-outline shadow-inner',
	// 		container: 'badge badge-sm badge-accent-container label-small shadow-outline shadow-inner'
	// 	},
	// 	neutral: {
	// 		solid: 'badge badge-sm badge-neutral label-small shadow-outline shadow-inner',
	// 		container: 'badge badge-sm badge-neutral-container label-small shadow-outline shadow-inner'
	// 	},
	// 	info: {
	// 		solid: 'badge badge-sm badge-info label-small shadow-outline shadow-inner',
	// 		container: 'badge badge-sm badge-info-container label-small shadow-outline shadow-inner'
	// 	},
	// 	success: {
	// 		solid: 'badge badge-sm badge-success label-small shadow-outline shadow-inner',
	// 		container: 'badge badge-sm badge-success-container label-small shadow-outline shadow-inner'
	// 	},
	// 	warning: {
	// 		solid: 'badge badge-sm badge-warning label-small shadow-outline shadow-inner',
	// 		container: 'badge badge-sm badge-warning-container label-small shadow-outline shadow-inner'
	// 	},
	// 	error: {
	// 		solid: 'badge badge-sm badge-error label-small shadow-outline shadow-inner',
	// 		container: 'badge badge-sm badge-error-container label-small shadow-outline shadow-inner'
	// 	}
	// };

	let {
		color = 'accent',
		messages = []
	}: {
		color?: FeedbackColor;
		messages?: FeedbackMessage[];
	} = $props();

	// function parseFeedbackContent(
	// 	content: string
	// ): Pick<ParsedFeedbackMessage, 'course' | 'year' | 'number' | 'markdown'> {
	// 	const frontmatterMatch = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n?/);

	// 	if (!frontmatterMatch) {
	// 		return {
	// 			course: 'COURSE',
	// 			year: 'YEAR',
	// 			number: NaN,
	// 			markdown: content.trim()
	// 		};
	// 	}

	// 	// const frontmatter = frontmatterMatch[1];
	// 	// const markdown = content.slice(frontmatterMatch[0].length).trim();

	// 	// let course = 'COURSE';
	// 	// let year = 'YEAR';
	// 	// let number = NaN;

	// 	// for (const line of frontmatter.split('\n')) {
	// 	// 	const [rawKey, ...rawValue] = line.split(':');
	// 	// 	if (!rawKey || rawValue.length === 0) {
	// 	// 		continue;
	// 	// 	}

	// 	// 	const key = rawKey.trim().toLowerCase();
	// 	// 	const value = rawValue.join(':').trim();

	// 	// 	if (key === 'course' && value) {
	// 	// 		course = value;
	// 	// 	}

	// 	// 	if (key === 'year' && value) {
	// 	// 		year = value;
	// 	// 	}
	// 	// 	if (key === 'number' && value) {
	// 	// 		number = Number(value);
	// 	// 	}
	// 	// }

	// 	return { course, year, number, markdown };
	// }

	function renderMarkdown(markdown: string): string {
		return marked.parse(markdown, { async: false });
	}

	// const parsedMessages = $derived(
	// 	messages.map((message) => ({
	// 		...message,
	// 		...parseFeedbackContent(message.content)
	// 	}))
	// );

	// let courses = $derived(
	// 	[
	// 		...new Set(
	// 			parsedMessages
	// 				.map((message) => message.course)
	// 				.filter((course): course is string => Boolean(course))
	// 		)
	// 	].sort()
	// );

	// let years = $derived(
	// 	[
	// 		...new Set(
	// 			parsedMessages
	// 				.map((message) => message.year)
	// 				.filter((year): year is string => Boolean(year))
	// 		)
	// 	].sort((left, right) => Number(left) - Number(right))
	// );

	// let courseSelection: Record<string, boolean> = $state({});
	// let yearSelection: Record<string, boolean> = $state({});

	// $effect(() => {
	// 	for (const course of courses) {
	// 		if (!(course in courseSelection)) {
	// 			courseSelection[course] = true;
	// 		}
	// 	}
	// });

	// $effect(() => {
	// 	for (const year of years) {
	// 		if (!(year in yearSelection)) {
	// 			yearSelection[year] = true;
	// 		}
	// 	}
	// });

	// let selectedCourses = $derived(courses.filter((course) => courseSelection[course] === true));
	// let selectedYears = $derived(years.filter((year) => yearSelection[year] === true));

	// function selectAllCourses() {
	// 	for (const course of courses) {
	// 		courseSelection[course] = true;
	// 	}
	// }

	// function selectNoCourses() {
	// 	for (const course of courses) {
	// 		courseSelection[course] = false;
	// 	}
	// }

	// function toggleCourse(course: string) {
	// 	courseSelection[course] = !courseSelection[course];
	// }

	// function selectAllYears() {
	// 	for (const year of years) {
	// 		yearSelection[year] = true;
	// 	}
	// }

	// function selectNoYears() {
	// 	for (const year of years) {
	// 		yearSelection[year] = false;
	// 	}
	// }

	// function toggleYear(year: string) {
	// 	yearSelection[year] = !yearSelection[year];
	// }

	// const filteredMessages = $derived(
	// 	parsedMessages.filter(
	// 		(message) =>
	// 			courseSelection[message.course] !== false && yearSelection[message.year] !== false
	// 	)
	// );

	let activeIndex = $state(0);
	let isCardVisible = $state(true);
	let transitionTimer: ReturnType<typeof setTimeout> | null = null;

	// $effect(() => {
	// 	if (filteredMessages.length === 0) {
	// 		activeIndex = 0;
	// 		return;
	// 	}

	// 	if (activeIndex >= filteredMessages.length) {
	// 		activeIndex = filteredMessages.length - 1;
	// 	}

	// 	if (activeIndex < 0) {
	// 		activeIndex = 0;
	// 	}
	// });

	const activeMessage = $derived(messages[activeIndex]);

	function navigateToIndex(nextIndex: number) {
		if (messages.length === 0) {
			return;
		}

		if (transitionTimer) {
			clearTimeout(transitionTimer);
		}

		isCardVisible = false;
		transitionTimer = setTimeout(() => {
			activeIndex = nextIndex;
			isCardVisible = true;
			transitionTimer = null;
		}, 150);
	}

	function showPrevious() {
		if (messages.length === 0) {
			return;
		}

		navigateToIndex((activeIndex - 1 + messages.length) % messages.length);
	}

	function showNext() {
		if (messages.length === 0) {
			return;
		}

		navigateToIndex((activeIndex + 1) % messages.length);
	}

	onDestroy(() => {
		if (transitionTimer) {
			clearTimeout(transitionTimer);
		}
	});
</script>

<!-- <div class="mx-auto mb-4 grid w-full max-w-[90rem] grid-cols-1 gap-3 xl:grid-cols-2">
	{#if courses.length > 0}
		<div class="min-w-0">
			<CourseSelector
				label="Courses"
				options={courses}
				selectedOptions={selectedCourses}
				{color}
				compact={false}
				onSelectAll={selectAllCourses}
				onSelectNone={selectNoCourses}
				onToggle={toggleCourse}
			/>
		</div>
	{/if}
	{#if years.length > 0}
		<div class="min-w-0 xl:justify-self-end">
			<CourseSelector
				label="Years"
				options={years}
				selectedOptions={selectedYears}
				{color}
				compact={false}
				onSelectAll={selectAllYears}
				onSelectNone={selectNoYears}
				onToggle={toggleYear}
			/>
		</div>
	{/if}
</div> -->

<div class="relative flex h-full w-full items-center justify-center">
	{#if messages.length === 0}
		<div class="flex min-h-[16rem] w-full items-center justify-center p-6">
			<div class="text-base-content/70 text-center text-3xl font-semibold">
				No comments selected
			</div>
		</div>
	{:else if activeMessage}
		{@const badgeScheme = activeIndex % 2 === 0 ? 'container' : 'solid'}
		{@const boxScheme = badgeScheme === 'solid' ? 'container' : 'solid'}
		<div class="w-3/4">
			<div
				class={`flex h-full w-full items-start justify-center transition-opacity duration-300 ease-out ${isCardVisible ? 'opacity-100' : 'opacity-0'}`}
			>
				<ChatBubble
					variant={color}
					showTail={false}
					shadow={false}
					maxWidth="100%"
					class={`feedback-chat-bubble feedback-box-${color}-${boxScheme} w-full`}
				>
					<div class="markdown-comment feedback-content px-4">
						<!-- <div class="flex gap-2">
							<div class={badgeClasses[color][badgeScheme]}>{activeMessage.course}</div>
							<div class={badgeClasses[color][badgeScheme]}>{activeMessage.year}</div>
							<div class="grow"></div>
							{#if !isNaN(Number(activeMessage.number))}
								<div class={badgeClasses[color][badgeScheme]}>
									based on {activeMessage.number} answers
								</div>
							{/if}
						</div>
						<hr /> -->
						<!-- eslint-disable-next-line svelte/no-at-html-tags -->
						{@html renderMarkdown(activeMessage.content)}
					</div>
				</ChatBubble>
			</div>
		</div>
	{/if}

	<button
		type="button"
		class="bg-base-100 shadow-base-300/20 absolute start-5 top-1/2 z-10 flex size-9.5 -translate-y-1/2 items-center justify-center rounded-full shadow-sm max-sm:start-3"
		class:opacity-50={messages.length <= 1}
		onclick={showPrevious}
		disabled={messages.length <= 1}
	>
		<span class="icon-[tabler--chevron-left] size-5 cursor-pointer"></span>
		<span class="sr-only">Previous</span>
	</button>

	<button
		type="button"
		class="bg-base-100 shadow-base-300/20 absolute end-5 top-1/2 z-10 flex size-9.5 -translate-y-1/2 items-center justify-center rounded-full shadow-sm max-sm:end-3"
		class:opacity-50={messages.length <= 1}
		onclick={showNext}
		disabled={messages.length <= 1}
	>
		<span class="icon-[tabler--chevron-right] size-5"></span>
		<span class="sr-only">Next</span>
	</button>
</div>

<style>
	:global(.feedback-chat-bubble) {
		display: block;
		width: 100%;
		max-width: 100% !important;
	}

	:global(.feedback-chat-bubble .bubble-oval) {
		border-radius: 1rem;
		min-height: 0;
		padding: 1rem 1.25rem;
		text-align: left;
		font-size: inherit;
		line-height: inherit;
		align-items: stretch;
		justify-content: flex-start;
	}

	:global(.feedback-chat-bubble .bubble-text) {
		text-align: left;
		text-wrap: wrap;
	}

	:global(.feedback-chat-bubble.feedback-box-primary-solid .bubble-oval) {
		background-color: var(--color-primary);
		color: var(--color-primary-content);
	}

	:global(.feedback-chat-bubble.feedback-box-primary-container .bubble-oval) {
		background-color: var(--color-primary-container);
		color: var(--color-primary-container-content);
	}

	:global(.feedback-chat-bubble.feedback-box-secondary-solid .bubble-oval) {
		background-color: var(--color-secondary);
		color: var(--color-secondary-content);
	}

	:global(.feedback-chat-bubble.feedback-box-secondary-container .bubble-oval) {
		background-color: var(--color-secondary-container);
		color: var(--color-secondary-container-content);
	}

	:global(.feedback-chat-bubble.feedback-box-accent-solid .bubble-oval) {
		background-color: var(--color-accent);
		color: var(--color-accent-content);
	}

	:global(.feedback-chat-bubble.feedback-box-accent-container .bubble-oval) {
		background-color: var(--color-accent-container);
		color: var(--color-accent-container-content);
	}

	:global(.feedback-chat-bubble.feedback-box-neutral-solid .bubble-oval) {
		background-color: var(--color-neutral);
		color: var(--color-neutral-content);
	}

	:global(.feedback-chat-bubble.feedback-box-neutral-container .bubble-oval) {
		background-color: var(--color-neutral-container);
		color: var(--color-neutral-container-content);
	}

	:global(.feedback-chat-bubble.feedback-box-info-solid .bubble-oval) {
		background-color: var(--color-info);
		color: var(--color-info-content);
	}

	:global(.feedback-chat-bubble.feedback-box-info-container .bubble-oval) {
		background-color: var(--color-info-container);
		color: var(--color-info-container-content);
	}

	:global(.feedback-chat-bubble.feedback-box-success-solid .bubble-oval) {
		background-color: var(--color-success);
		color: var(--color-success-content);
	}

	:global(.feedback-chat-bubble.feedback-box-success-container .bubble-oval) {
		background-color: var(--color-success-container);
		color: var(--color-success-container-content);
	}

	:global(.feedback-chat-bubble.feedback-box-warning-solid .bubble-oval) {
		background-color: var(--color-warning);
		color: var(--color-warning-content);
	}

	:global(.feedback-chat-bubble.feedback-box-warning-container .bubble-oval) {
		background-color: var(--color-warning-container);
		color: var(--color-warning-container-content);
	}

	:global(.feedback-chat-bubble.feedback-box-error-solid .bubble-oval) {
		background-color: var(--color-error);
		color: var(--color-error-content);
	}

	:global(.feedback-chat-bubble.feedback-box-error-container .bubble-oval) {
		background-color: var(--color-error-container);
		color: var(--color-error-container-content);
	}

	:global(.markdown-comment .feedback-content) {
		max-width: 68ch;
		margin-inline: auto;
	}

	:global(.markdown-comment .feedback-meta) {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-bottom: 0.5rem;
	}

	:global(.markdown-comment h1),
	:global(.markdown-comment h2),
	:global(.markdown-comment h3),
	:global(.markdown-comment h4),
	:global(.markdown-comment h5),
	:global(.markdown-comment h6) {
		color: currentColor;
		font-size: inherit;
		font-weight: 700;
		text-wrap: balance;
		line-height: 1.2;
		margin: 0 0 0.75rem 0;
	}

	:global(.markdown-comment p) {
		text-wrap: pretty;
		overflow-wrap: anywhere;
		margin: 0 0 0.75rem 0;
	}

	:global(.markdown-comment ul) {
		list-style: disc;
		margin: 0 0 0.75rem 1.25rem;
		text-wrap: pretty;
		overflow-wrap: anywhere;
	}

	:global(.markdown-comment li) {
		text-wrap: pretty;
		overflow-wrap: anywhere;
	}

	:global(.markdown-comment a) {
		text-decoration: underline;
	}

	:global(.markdown-comment > :last-child) {
		margin-bottom: 0;
	}
</style>
