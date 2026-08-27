<script lang="ts">
	// import { Hct, hexFromArgb } from '@material/material-color-utilities';

	import { Action } from '$lib/accessHandler';
	import { createHeatMapColors } from '$lib/heatMapColors.svelte';
	import { SocketIO } from '$lib/socketio.svelte';

	type ColorSet = {
		background: string;
		text: string;
	};
	let {
		questionId,
		socketio,
		averageMotivation,
		averageColors = $bindable()
	}: {
		questionId: string;
		socketio: SocketIO;
		averageMotivation: number;
		averageColors: ColorSet;
	} = $props();

	let motivationId = $state('new_' + Math.random().toString(36).substring(2, 9));

	const sendMotvationNumerical = (value: number) => {
		// console.log('=== Sending motivation value ===');
		// console.log(value);
		// socketio?.addEntity({ id: motivationId, value: value });
		socketio?.addPendingAccessPolicy(motivationId, { public: true, action: Action.READ });
		socketio?.submitEntity({ id: motivationId, value: value }, questionId, true);
		motivationId = 'new_' + Math.random().toString(36).substring(2, 9);
	};

	// Static coloring the motivation buttons:
	// let motivation = $state([0, 25, 50, 75, 100]);
	let motivation = $state(Array.from({ length: 13 }, (_, i) => (i * 100) / 12));
	let motivationColors = $derived.by(() => createHeatMapColors(motivation, 1, 0.9));

	// calculate background color from average motivation value:
	$effect(() => {
		averageColors = createHeatMapColors([averageMotivation], 1, 0.9, 'rgb')[0];
	});
</script>

<!-- style="background: linear-gradient(to right, {motivationColors[0].background}, {motivationColors[0].background}, {motivationColors[1].background}); color: {motivationColors[0].text};" -->

<!-- {#snippet exampleButton(colorNumber: number, examples: string[])}
	<div
		class="btn btn-gradient shadow-outline rounded-4xl shadow-md h-200 flex flex-col gap-3 heading-small "
		style="
			background: linear-gradient(
					to right,
					{colorNumber === 0 ? motivationColors[0].background : motivationColors[colorNumber-1].background}, {motivationColors[colorNumber].background}, {motivationColors[colorNumber+1].background}
				);
			color: {motivationColors[0].text};"
	>
		{#each examples as example}
			<p>{example}</p>
		{/each}
	</div>
{/snippet } -->

<div class="grid h-fit grid-cols-6 gap-3">
	<div>Amotivation</div>
	<div class="col-span-4">Extrinsic</div>
	<div>Intrinsic</div>

	<div class="heading fragment flex flex-col">
		<div class="invisible">dummy</div>
		<!-- onclick={() => socketio?.submitEntity(0)}
		onkeydown={(e: KeyboardEvent) => e.key === 'Enter' && socketio?.submitEntity(0)} -->
		<button
			class="btn shadow-outline title-large border-outline flex h-full flex-col rounded-4xl border-2 shadow-md"
			style="background: linear-gradient(to right, {motivationColors[0]
				.background}, {motivationColors[1].background}, {motivationColors[2]
				.background}); color: {motivationColors[1].text};"
			onclick={() => {
				sendMotvationNumerical(0);
				// socketio?.addEntity({ id: motivationId, value: 0 });
				// socketio?.submitEntity({ id: motivationId, value: 0 }, questionId, true, true, Action.READ);
				// motivationId = 'new_' + Math.random().toString(36).substring(2, 9);
			}}
		>
			<span class="my-2">"I can’t be bothered at all.”</span>
			<span class="my-2">"What’s the point?”</span>
			<span class="my-2">"It won’t make a difference anyway.”</span>
			<span class="my-2">"I don’t know why I’m even doing this.”</span>
		</button>
	</div>
	<div class="heading fragment flex flex-col">
		<div>External</div>
		<button
			class="btn shadow-outline title-large border-outline flex h-full flex-col gap-1 rounded-4xl border-2 shadow-md"
			style="background: linear-gradient(to right, {motivationColors[2]
				.background}, {motivationColors[3].background}, {motivationColors[4]
				.background}); color: {motivationColors[3].text};"
			onclick={() => {
				sendMotvationNumerical(20);
			}}
		>
			<span class="my-2">"I'm doing it because I have to."</span>
			<span class="my-2">"So I don't get in trouble."</span>
			<span class="my-2">"Because I'll get paid / a grade."</span>
			<span class="my-2">"Because they told me to."</span>
		</button>
	</div>
	<div class="heading fragment flex flex-col">
		<div>Introjected</div>
		<button
			class="btn shadow-outline title-large border-outline flex h-full flex-col gap-1 rounded-4xl border-2 shadow-md"
			style="background: linear-gradient(to right, {motivationColors[4]
				.background}, {motivationColors[5].background}, {motivationColors[6]
				.background}); color: {motivationColors[5].text};"
			onclick={() => {
				sendMotvationNumerical(40);
			}}
		>
			<span class="my-2">"I’d feel guilty if I didn’t.”</span>
			<span class="my-2">"I don’t want to disappoint anyone.”</span>
			<span class="my-2">"I need to prove I’m good enough.”</span>
			<span class="my-2">"I’ll feel ashamed if I fail.”</span>
		</button>
	</div>
	<div class="heading fragment flex flex-col">
		<div>Identified</div>
		<button
			class="btn shadow-outline title-large border-outline flex h-full flex-col gap-1 rounded-4xl border-2 shadow-md"
			style="background: linear-gradient(to right, {motivationColors[6]
				.background}, {motivationColors[7].background}, {motivationColors[8]
				.background}); color: {motivationColors[7].text};"
			onclick={() => {
				sendMotvationNumerical(60);
			}}
		>
			<span class="my-2">"It’s important to me.”</span>
			<span class="my-2">"I’m doing it because it’s good for my future.”</span>
			<span class="my-2">"It helps me reach my goals.”</span>
			<span class="my-2">"I don’t love it, but I believe it’s worth it.”</span>
		</button>
	</div>
	<div class="heading fragment flex flex-col">
		<div>Integrated</div>
		<button
			class="btn shadow-outline title-large border-outline flex h-full flex-col gap-1 rounded-4xl border-2 shadow-md"
			style="background: linear-gradient(to right, {motivationColors[8]
				.background}, {motivationColors[9].background}, {motivationColors[10]
				.background}); color: {motivationColors[9].text};"
			onclick={() => {
				sendMotvationNumerical(80);
			}}
		>
			<span class="my-2">"This fits who I am.”</span>
			<span class="my-2">"It matches my values.”</span>
			<span class="my-2">"This is part of the kind of person I want to be.”</span>
			<span class="my-2">"Doing this is just how I live my life.”</span>
		</button>
	</div>
	<div class="heading fragment flex flex-col">
		<div class="invisible">dummy</div>
		<button
			class="btn shadow-outline title-large border-outline flex h-full flex-col gap-1 rounded-4xl border-2 shadow-md"
			style="background: linear-gradient(to right, {motivationColors[10]
				.background}, {motivationColors[11].background}, {motivationColors[12]
				.background}); color: {motivationColors[11].text};"
			onclick={() => {
				sendMotvationNumerical(100);
			}}
		>
			<span class="my-2">"I’m here because it’s fun.”</span>
			<span class="my-2">"I’m doing it because I enjoy it.”</span>
			<span class="my-2">"I’m curious — I want to learn more.”</span>
			<span class="my-2">"I like the challenge.”</span>
		</button>
	</div>
	<div class="fragment hidden">Dummy to trigger color event</div>
</div>

<!--
Examples:

Amotivation:
"I can’t be bothered.”
“What’s the point?”
“It won’t make a difference anyway.”
“I don’t know why I’m even doing this.”

Extrinsic - External:
“I’m doing it because I have to.”
“So I don’t get in trouble.”
“Because I’ll get paid / a grade.”
“Because they told me to.”

Extrinsic - Introjected:
“I’d feel guilty if I didn’t.”
“I don’t want to disappoint anyone.”
“I need to prove I’m good enough.”
“I’ll feel ashamed if I fail.”

Extrinsic - Identified:
“It’s important to me.”
“I’m doing it because it’s good for my future.”
“It helps me reach my goals.”
“I don’t love it, but I believe it’s worth it.”

Extrinsic - Integrated:
“This fits who I am.”
“It matches my values.”
“This is part of the kind of person I want to be.”
“Doing this is just how I live my life.”

Intrinsic:
“I’m here because it’s fun.”
“I’m doing it because I enjoy it.”
“I’m curious — I want to learn more.”
“I like the challenge.”
-->
