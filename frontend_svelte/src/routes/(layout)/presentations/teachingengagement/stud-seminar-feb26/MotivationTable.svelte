<script lang="ts">
	import { themeStore } from '$lib/stores';
	import type { AppTheme } from '$lib/theming';
	import { Hct, hexFromArgb } from '@material/material-color-utilities';
	// import { Theming } from '$lib/theming';
	import { onDestroy } from 'svelte';
	// import { SocketIO } from '$lib/socketio';
	// import { Action } from '$lib/accessHandler';

	// type ColorSet = {
	// 	background: string;
	// 	text: string;
	// };
	let {
		color
		// 	questionId,
		// 	socketio,
		// 	averageMotivation,
		// 	averageColors = $bindable()
	}: {
		color?: string;
		// 	questionId: string;
		// 	socketio: SocketIO;
		// 	averageMotivation: number;
		// 	averageColors: ColorSet;
	} = $props();

	// let motivationId = $state('new_' + Math.random().toString(36).substring(2, 9));

	// const sendMotvationNumerical = (value: number) => {
	// 	// console.log('=== Sending motivation value ===');
	// 	// console.log(value);
	// 	// socketio?.addEntity({ id: motivationId, value: value });
	// 	socketio?.submitEntity({ id: motivationId, value: value }, questionId, true, true, Action.READ);
	// 	motivationId = 'new_' + Math.random().toString(36).substring(2, 9);
	// };

	// Static coloring the motivation buttons:
	let theme = $state({} as AppTheme);
	const unsbscribeThemeStore = themeStore.subscribe((value) => {
		theme = value;
	});

	onDestroy(() => {
		unsbscribeThemeStore();
	});

	let errorHct = $derived.by(() => {
		if (!theme.currentMode) {
			return Hct.from(25, 80, 30);
		} else {
			return Hct.fromInt(theme[theme.currentMode].colors['error']);
		}
	});
	let onErrorHct = $derived.by(() => {
		if (!theme.currentMode) {
			return Hct.from(24, 13, 90);
		} else {
			return Hct.fromInt(theme[theme.currentMode].colors['onError']);
		}
	});

	// let motivation = $state([0, 25, 50, 75, 100]);
	let motivation = $state(Array.from({ length: 13 }, (_, i) => (i * 100) / 12));
	let motivationColorsHue = $derived(
		motivation.map((s) => ({
			background: s * 1.05 + 25,
			text: s * 1.05 + 25
		}))
	);
	let motivationColors = $derived(
		motivationColorsHue.map((hue) => ({
			background: hexFromArgb(Hct.from(hue.background, errorHct.chroma, errorHct.tone).toInt()),
			text: hexFromArgb(Hct.from(hue.text, onErrorHct.chroma, onErrorHct.tone).toInt())
		}))
	);

	// // calculate background color from average motivation value:
	// $effect(() => {
	// 	// calculate Hct from material design:
	// 	const backgroundHct = Hct.from(averageMotivation * 1.05 + 25, errorHct.chroma, errorHct.tone);
	// 	const textHct = Hct.from(averageMotivation * 1.05 + 25, onErrorHct.chroma, onErrorHct.tone);
	// 	// console.log('=== motivationAverageColorHue - backgroundHct ===');
	// 	// console.log(backgroundHct);
	// 	// console.log('=== motivationAverageColorHue - textHct ===');
	// 	// console.log(textHct);
	// 	averageColors = {
	// 		background: Theming.rgbFromHex(hexFromArgb(backgroundHct.toInt())),
	// 		text: Theming.rgbFromHex(hexFromArgb(textHct.toInt()))
	// 	};
	// });
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

<div class="grid h-180 grid-cols-6 gap-3 text-{color || 'primary'}">
	<div>Amotivation</div>
	<div class="col-span-4">Extrinsic</div>
	<div>Intrinsic</div>

	<div class="heading fragment flex flex-col">
		<div class="invisible">dummy</div>
		<!-- onclick={() => socketio?.submitEntity(0)}
		onkeydown={(e: KeyboardEvent) => e.key === 'Enter' && socketio?.submitEntity(0)} -->
		<button
			class="btn btn-gradient shadow-outline title-large flex h-[90%] flex-col gap-1 rounded-4xl shadow-sm"
			style="background: linear-gradient(to right, {motivationColors[0]
				.background}, {motivationColors[1].background}, {motivationColors[2]
				.background}); color: {motivationColors[1].text};"
			onclick={() => {
				// sendMotvationNumerical(0);
				// socketio?.addEntity({ id: motivationId, value: 0 });
				// socketio?.submitEntity({ id: motivationId, value: 0 }, questionId, true, true, Action.READ);
				// motivationId = 'new_' + Math.random().toString(36).substring(2, 9);
			}}
		>
			<p>"I can’t be bothered.”</p>
			<p>"What’s the point?”</p>
			<p>"It won’t make a difference anyway.”</p>
			<p>"I don’t know why I’m even doing this.”</p>
		</button>
	</div>
	<div class="heading fragment flex flex-col">
		<div>External</div>
		<button
			class="btn btn-gradient shadow-outline title-large flex h-[90%] flex-col gap-1 rounded-4xl shadow-md"
			style="background: linear-gradient(to right, {motivationColors[2]
				.background}, {motivationColors[3].background}, {motivationColors[4]
				.background}); color: {motivationColors[3].text};"
			onclick={() => {
				// sendMotvationNumerical(20);
			}}
		>
			<p>"I'm doing it because I have to."</p>
			<p>"So I don't get in trouble."</p>
			<p>"Because I'll get paid / a grade."</p>
			<p>"Because they told me to."</p>
		</button>
	</div>
	<div class="heading fragment flex flex-col">
		<div>Introjected</div>
		<button
			class="btn btn-gradient shadow-outline title-large flex h-[90%] flex-col gap-1 rounded-4xl shadow-md"
			style="background: linear-gradient(to right, {motivationColors[4]
				.background}, {motivationColors[5].background}, {motivationColors[6]
				.background}); color: {motivationColors[5].text};"
			onclick={() => {
				// sendMotvationNumerical(40);
			}}
		>
			<p>"I’d feel guilty if I didn’t.”</p>
			<p>"I don’t want to disappoint anyone.”</p>
			<p>"I need to prove I’m good enough.”</p>
			<p>"I’ll feel ashamed if I fail.”</p>
		</button>
	</div>
	<div class="heading fragment flex flex-col">
		<div>Identified</div>
		<button
			class="btn btn-gradient shadow-outline title-large flex h-[90%] flex-col gap-1 rounded-4xl shadow-md"
			style="background: linear-gradient(to right, {motivationColors[6]
				.background}, {motivationColors[7].background}, {motivationColors[8]
				.background}); color: {motivationColors[7].text};"
			onclick={() => {
				// sendMotvationNumerical(60);
			}}
		>
			<p>"It’s important to me.”</p>
			<p>"I’m doing it because it’s good for my future.”</p>
			<p>"It helps me reach my goals.”</p>
			<p>"I don’t love it, but I believe it’s worth it.”</p>
		</button>
	</div>
	<div class="heading fragment flex flex-col">
		<div>Integrated</div>
		<button
			class="btn btn-gradient shadow-outline title-large flex h-[90%] flex-col gap-1 rounded-4xl shadow-md"
			style="background: linear-gradient(to right, {motivationColors[8]
				.background}, {motivationColors[9].background}, {motivationColors[10]
				.background}); color: {motivationColors[9].text};"
			onclick={() => {
				// sendMotvationNumerical(80);
			}}
		>
			<p>"This fits who I am.”</p>
			<p>"It matches my values.”</p>
			<p>"This is part of the kind of person I want to be.”</p>
			<p>"Doing this is just how I live my life.”</p>
		</button>
	</div>
	<div class="heading fragment flex flex-col">
		<div class="invisible">dummy</div>
		<button
			class="btn btn-gradient shadow-outline title-large flex h-[90%] flex-col gap-1 rounded-4xl shadow-md"
			style="background: linear-gradient(to right, {motivationColors[10]
				.background}, {motivationColors[11].background}, {motivationColors[12]
				.background}); color: {motivationColors[11].text};"
			onclick={() => {
				// sendMotvationNumerical(100);
			}}
		>
			<p>"I’m here because it’s fun.”</p>
			<p>"I’m doing it because I enjoy it.”</p>
			<p>"I’m curious — I want to learn more.”</p>
			<p>"I like the challenge.”</p>
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
