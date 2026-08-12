<script lang="ts">
	import CourseSelector from './CourseSelector.svelte';

	type ChartEntry = {
		year: number;
		values: number[];
		course?: string;
	};

	type YearAggregate = {
		year: number;
		values: [number, number, number, number, number];
	};

	let {
		data,
		categories,
		colorClasses,
		color = 'info'
	}: {
		data: ChartEntry[];
		categories: [string, string, string, string, string];
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
					current = { year: entry.year, values: [0, 0, 0, 0, 0] };
					grouped.set(entry.year, current);
				}

				for (let index = 0; index < 5; index++) {
					current.values[index] += entry.values[index] ?? 0;
				}
			}

			return [...grouped.values()].sort((a, b) => a.year - b.year);
		})()
	);

	let scaleMode: 'absolute' | 'relative' = $state('absolute');

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

	let leftFarCategory = $derived(categories[0]);
	let leftNearCategory = $derived(categories[1]);
	let centerCategory = $derived(categories[2]);
	let rightNearCategory = $derived(categories[3]);
	let rightFarCategory = $derived(categories[4]);

	let maxSide = $derived(
		Math.max(
			...aggregatedByYear.map((entry) => {
				const centered = toValue(entry, 2) / 2;
				const right = centered + toValue(entry, 3) + toValue(entry, 4);
				const left = centered + toValue(entry, 1) + toValue(entry, 0);
				return Math.max(right, left);
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
	const totalReplies = (entry: ChartEntry) =>
		entry.values.reduce((total, value) => total + (value ?? 0), 0);

	// Legend split: keep category order left -> right and pin "same" to center
	let legendLeft = $derived([categories[0], categories[1]]);
	let legendCenter = $derived(categories[2]);
	let legendRight = $derived([categories[3], categories[4]]);
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
					class={`btn btn-lg text-2xl font-bold ${scaleMode === 'absolute' ? `btn-${color}` : `btn-outline btn-${color}`}`}
					onclick={(event) => {
						event.stopPropagation();
						scaleMode = 'absolute';
					}}
				>
					Absolute
				</button>
				<button
					type="button"
					class={`btn btn-lg text-2xl font-bold ${scaleMode === 'relative' ? `btn-${color}` : `btn-outline btn-${color}`}`}
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
		class={`shadow-${color} border-base-300 bg-base-200 flex max-h-full min-h-0 grow flex-col gap-2 rounded-4xl border object-contain p-4 shadow-lg`}
	>
		<div class="grid grid-cols-[14rem_1fr] gap-6">
			<div></div>
			<div
				class="text-base-content grid translate-x-[2.5rem] transform grid-cols-[1fr_max-content_1fr] items-center text-3xl font-semibold"
			>
				<div class="flex items-center justify-end gap-x-10">
					{#each legendLeft as category (category)}
						<div class="flex items-center gap-3">
							<span class={`h-6 w-6 rounded ${colorClasses[category] ?? 'bg-base-content'}`}></span>
							{category}
						</div>
					{/each}
				</div>
				<div class="flex items-center gap-3 px-10">
					<span class={`h-6 w-6 rounded ${colorClasses[legendCenter] ?? 'bg-base-content'}`}></span>
					{legendCenter}
				</div>
				<div class="flex items-center justify-start gap-x-10">
					{#each legendRight as category (category)}
						<div class="flex items-center gap-3">
							<span class={`h-6 w-6 rounded ${colorClasses[category] ?? 'bg-base-content'}`}></span>
							{category}
						</div>
					{/each}
				</div>
			</div>
		</div>
		<div class="relative min-h-0 grow">
			{#if scaleMode === 'absolute'}
				<div
					class="bg-base-content/20 pointer-events-none absolute top-0 bottom-0 left-[calc(50%+7.75rem)] z-[1] w-[2px]"
				></div>
			{/if}
			<div class="absolute inset-0 flex flex-col justify-evenly gap-4">
				{#if aggregatedByYear.length === 0}
					<div class="text-base-content/70 text-center text-3xl font-semibold">
						No courses selected
					</div>
				{:else}
					{#each aggregatedByYear as entry (entry.year)}
						{@const centered = toValue(entry, 2) / 2}
						{@const total = totalReplies(entry)}
						{@const rightFarLeft = centered + toValue(entry, 3)}
						{@const rightNearLeft = centered}
						{@const centerLeft = -centered}
						{@const leftNearLeft = -centered - toValue(entry, 1)}
						{@const leftFarLeft = -centered - toValue(entry, 1) - toValue(entry, 0)}

						<div class="grid h-24 grid-cols-[14rem_1fr] items-center gap-6">
							<div class="text-base-content text-center">
								<div class="text-6xl font-bold">{entry.year}</div>
								<div class="text-4xl font-semibold opacity-80">({totalReplies(entry)})</div>
							</div>
							<div class="relative h-16">
								<div
									class={`group absolute right-0 left-0 ${colorClasses[rightFarCategory] ?? 'bg-base-content'}`}
									style={`left: ${scaleMode === 'absolute' ? toLeft(rightFarLeft) : toLeftRelative(toValue(entry, 0) + toValue(entry, 1) + toValue(entry, 2) + toValue(entry, 3), total)}; width: ${scaleMode === 'absolute' ? toWidth(toValue(entry, 4)) : toWidthRelative(toValue(entry, 4), total)}; top: 0; bottom: 0;`}
								>
									<span
										class="rounded-box bg-base-100 pointer-events-none absolute top-1/2 left-1/2 z-10 -translate-x-1/2 -translate-y-1/2 px-4 py-2 text-3xl font-bold opacity-0 shadow-xl transition group-hover:opacity-100"
									>
										{toValue(entry, 4)}
									</span>
								</div>

								<div
									class={`group absolute right-0 left-0 ${colorClasses[rightNearCategory] ?? 'bg-base-content'}`}
									style={`left: ${scaleMode === 'absolute' ? toLeft(rightNearLeft) : toLeftRelative(toValue(entry, 0) + toValue(entry, 1) + toValue(entry, 2), total)}; width: ${scaleMode === 'absolute' ? toWidth(toValue(entry, 3)) : toWidthRelative(toValue(entry, 3), total)}; top: 0; bottom: 0;`}
								>
									<span
										class="rounded-box bg-base-100 pointer-events-none absolute top-1/2 left-1/2 z-10 -translate-x-1/2 -translate-y-1/2 px-4 py-2 text-3xl font-bold opacity-0 shadow-xl transition group-hover:opacity-100"
									>
										{toValue(entry, 3)}
									</span>
								</div>

								<div
									class={`group absolute right-0 left-0 ${colorClasses[centerCategory] ?? 'bg-base-content'}`}
									style={`left: ${scaleMode === 'absolute' ? toLeft(centerLeft) : toLeftRelative(toValue(entry, 0) + toValue(entry, 1), total)}; width: ${scaleMode === 'absolute' ? toWidth(toValue(entry, 2)) : toWidthRelative(toValue(entry, 2), total)}; top: 0; bottom: 0;`}
								>
									<span
										class="rounded-box bg-base-100 pointer-events-none absolute top-1/2 left-1/2 z-10 -translate-x-1/2 -translate-y-1/2 px-4 py-2 text-3xl font-bold opacity-0 shadow-xl transition group-hover:opacity-100"
									>
										{toValue(entry, 2)}
									</span>
								</div>

								<div
									class={`group absolute right-0 left-0 ${colorClasses[leftNearCategory] ?? 'bg-base-content'}`}
									style={`left: ${scaleMode === 'absolute' ? toLeft(leftNearLeft) : toLeftRelative(toValue(entry, 0), total)}; width: ${scaleMode === 'absolute' ? toWidth(toValue(entry, 1)) : toWidthRelative(toValue(entry, 1), total)}; top: 0; bottom: 0;`}
								>
									<span
										class="rounded-box bg-base-100 pointer-events-none absolute top-1/2 left-1/2 z-10 -translate-x-1/2 -translate-y-1/2 px-4 py-2 text-3xl font-bold opacity-0 shadow-xl transition group-hover:opacity-100"
									>
										{toValue(entry, 1)}
									</span>
								</div>

								<div
									class={`group absolute right-0 left-0 ${colorClasses[leftFarCategory] ?? 'bg-base-content'}`}
									style={`left: ${scaleMode === 'absolute' ? toLeft(leftFarLeft) : '0%'}; width: ${scaleMode === 'absolute' ? toWidth(toValue(entry, 0)) : toWidthRelative(toValue(entry, 0), total)}; top: 0; bottom: 0;`}
								>
									<span
										class="rounded-box bg-base-100 pointer-events-none absolute top-1/2 left-1/2 z-10 -translate-x-1/2 -translate-y-1/2 px-4 py-2 text-3xl font-bold opacity-0 shadow-xl transition group-hover:opacity-100"
									>
										{toValue(entry, 0)}
									</span>
								</div>
							</div>
						</div>
					{/each}
				{/if}
			</div>
		</div>
	</div>
</div>
