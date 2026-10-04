<script lang="ts">
	import CourseSelector from './CourseSelector.svelte';

	type ChartEntry = {
		year: number;
		values: number[];
		course?: string;
	};

	type YearAggregate = {
		year: number;
		values: number[];
	};

	let {
		data,
		categories,
		colorClasses,
		color = 'info'
	}: {
		data: ChartEntry[];
		categories: [string, string, string, string, string] | [string, string, string];
		colorClasses: Record<string, string>;
		color?: string;
	} = $props();

	const toValue = (entry: ChartEntry, index: number) => entry.values[index] ?? 0;

	let courses = $derived(
		[
			...new Set(
				data.map((entry) => entry.course).filter((course): course is string => Boolean(course))
			)
		].sort()
	);

	// Use a plain object to track user's course selections reactively
	// Keys are course strings, values are booleans (selected or not)
	let courseSelection: Record<string, boolean> = $state({});

	// Initialize new courses as selected when data changes
	$effect(() => {
		for (const course of courses) {
			if (!(course in courseSelection)) {
				courseSelection[course] = true;
			}
		}
	});

	let selectedCourses = $derived(courses.filter((course) => courseSelection[course] === true));

	let filteredData = $derived(
		courses.length === 0
			? data
			: data.filter((entry) => entry.course && courseSelection[entry.course] === true)
	);

	let aggregatedByYear = $derived(
		(() => {
			const grouped = new Map<number, YearAggregate>();

			for (const entry of filteredData) {
				let current = grouped.get(entry.year);
				if (!current) {
					current = { year: entry.year, values: categories.map(() => 0) };
					grouped.set(entry.year, current);
				}

				for (let index = 0; index < categories.length; index++) {
					current.values[index] += entry.values[index] ?? 0;
				}
			}

			return [...grouped.values()]
				.filter((entry) => totalReplies(entry) > 0)
				.sort((a, b) => a.year - b.year);
		})()
	);

	let scaleMode: 'absolute' | 'relative' = $state('relative');

	function selectAllCourses() {
		for (const course of courses) {
			courseSelection[course] = true;
		}
	}

	function selectNoCourses() {
		for (const course of courses) {
			courseSelection[course] = false;
		}
	}

	function toggleCourse(course: string) {
		courseSelection[course] = !courseSelection[course];
	}

	function leftTotal(entry: ChartEntry) {
		const middle = Math.floor(categories.length / 2);
		const beforeMiddle = entry.values
			.slice(0, middle)
			.reduce((total, value) => total + (value ?? 0), 0);
		return beforeMiddle + (categories.length % 2 === 1 ? toValue(entry, middle) / 2 : 0);
	}

	function getSegments(entry: ChartEntry) {
		const left = leftTotal(entry);
		let preceding = 0;
		return categories
			.map((_, index) => {
				const segment = { index, absoluteLeft: preceding - left, relativeLeft: preceding };
				preceding += toValue(entry, index);
				return segment;
			})
			.reverse();
	}

	let maxSide = $derived(
		Math.max(
			...aggregatedByYear.map((entry) => {
				const left = leftTotal(entry);
				return Math.max(totalReplies(entry) - left, left);
			}),
			1
		)
	);

	let scalePercent = $derived(48 / maxSide);
	const toWidth = (value: number) => `${value * scalePercent}%`;
	const toLeft = (value: number) => `${50 + value * scalePercent}%`;
	const toWidthRelative = (value: number, total: number) =>
		total > 0 ? `${(value / total) * 100}%` : '0%';
	const toLeftRelative = (value: number, total: number) =>
		total > 0 ? `${(value / total) * 100}%` : '0%';
	function totalReplies(entry: ChartEntry) {
		return entry.values.reduce((total, value) => total + (value ?? 0), 0);
	}

	let legendMiddle = $derived((categories.length - 1) / 2);
	let legendColumns = $derived(
		categories
			.map((_, index) => (index === legendMiddle ? 'max-content' : 'minmax(0, 1fr)'))
			.join(' ')
	);
</script>

<div class="flex min-h-0 w-full grow flex-col gap-4 px-2 pt-1 pb-2">
	<!-- <div class={`text-${color} text-center text-6xl font-bold`}>{title}</div> -->
	<div class="grid grid-cols-[14rem_1fr] gap-6">
		<div></div>
		<div class="flex flex-wrap items-center justify-between gap-4">
			{#if courses.length > 0}
				<CourseSelector
					label="Courses"
					options={courses}
					selectedOptions={selectedCourses}
					{color}
					onSelectAll={selectAllCourses}
					onSelectNone={selectNoCourses}
					onToggle={toggleCourse}
				/>
			{/if}
			<div class="ml-auto flex items-center gap-3">
				<button
					type="button"
					class={`btn btn-lg shadow-base-shadow rounded-full text-2xl font-bold ${scaleMode === 'absolute' ? `btn-${color}-container btn-gradient` : `btn-outline btn-${color}`}`}
					onclick={(event) => {
						event.stopPropagation();
						scaleMode = 'absolute';
					}}
				>
					Absolute
				</button>
				<button
					type="button"
					class={`btn btn-lg shadow-base-shadow rounded-full text-2xl font-bold ${scaleMode === 'relative' ? `btn-${color}-container btn-gradient` : `btn-outline btn-${color}`}`}
					onclick={(event) => {
						event.stopPropagation();
						scaleMode = 'relative';
					}}
				>
					Relative
				</button>
			</div>
		</div>
	</div>
	<div
		class="shadow-base-color border-outline bg-base-200 flex max-h-full min-h-0 grow flex-col gap-2 rounded-4xl border object-contain p-4 shadow-lg"
	>
		<div class="grid grid-cols-[14rem_1fr] gap-6">
			<div></div>
			<div
				class="text-base-content grid items-center gap-x-4 text-3xl font-semibold"
				style:grid-template-columns={legendColumns}
			>
				{#each categories as category, index (category)}
					<div
						class={`items-center gap-3 ${index === legendMiddle ? 'grid grid-cols-[1fr_1.5rem_1fr]' : 'flex'} ${index < legendMiddle ? 'justify-self-end' : 'justify-self-center'}`}
					>
						{#if index === legendMiddle}
							<span class="invisible" aria-hidden="true">{category}</span>
						{/if}
						<span class={`h-6 w-6 shrink-0 rounded ${colorClasses[category] ?? 'bg-base-content'}`}
						></span>
						<span>{category}</span>
					</div>
				{/each}
			</div>
		</div>
		<div class="relative min-h-0 grow">
			{#if scaleMode === 'absolute'}
				<div
					class="bg-base-content/20 pointer-events-none absolute top-0 bottom-0 left-[calc(50%+7.75rem)] z-[1] w-[4px]"
				></div>
			{/if}
			<div class="absolute inset-0 flex flex-col justify-evenly gap-4">
				{#if aggregatedByYear.length === 0}
					<div class="text-base-content/70 text-center text-3xl font-semibold">
						{courses.length > 0 && selectedCourses.length === 0 ? 'No courses selected' : 'No data'}
					</div>
				{:else}
					{#each aggregatedByYear as entry (entry.year)}
						{@const total = totalReplies(entry)}
						{@const segments = getSegments(entry)}

						<div class="grid h-24 grid-cols-[14rem_1fr] items-center gap-6">
							<div class="text-base-content text-center">
								<div class="text-6xl font-bold">{entry.year}</div>
								<div class="text-4xl font-semibold opacity-80">({totalReplies(entry)})</div>
							</div>
							<div class="relative h-16">
								{#each segments as { index, absoluteLeft, relativeLeft } (index)}
									<div
										class={`group absolute right-0 left-0 ${colorClasses[categories[index]] ?? 'bg-base-content'}`}
										style={`left: ${scaleMode === 'absolute' ? toLeft(absoluteLeft) : toLeftRelative(relativeLeft, total)}; width: ${scaleMode === 'absolute' ? toWidth(toValue(entry, index)) : toWidthRelative(toValue(entry, index), total)}; top: 0; bottom: 0;`}
									>
										<span
											class="rounded-box bg-base-100 pointer-events-none absolute top-1/2 left-1/2 z-10 -translate-x-1/2 -translate-y-1/2 px-4 py-2 text-3xl font-bold opacity-0 shadow-xl transition group-hover:opacity-100"
										>
											{toValue(entry, index)}
										</span>
									</div>
								{/each}
							</div>
						</div>
					{/each}
				{/if}
			</div>
		</div>
	</div>
</div>
