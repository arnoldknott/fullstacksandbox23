<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import '@material/web/slider/slider.js';
	import '@material/web/labs/card/filled-card.js';
	import '@material/web/tabs/tabs.js';
	import '@material/web/tabs/primary-tab.js';
	import '@material/web/tabs/secondary-tab.js';
	import Tabs from './Tabs.svelte';
	import type { Tab } from '$lib/types';
	import VerticalTabs from './VerticalTabs.svelte';
	import UserForm from './UserForm.svelte';
	import Card from '$components/Card.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';

	const tabs: Tab[] = [
		{
			header: 'Left Tab',
			content: 'Some content in the left tab.'
		},
		{
			header: 'Right Tag',
			content: 'The tab, that is activated by default is the one on the right side.',
			active: true
		}
	];

	let sliderValue = $state(0);
	const color = $derived(`hsl(${sliderValue * 1.2}, 80%, 80%)`);

	let sliders = $state([0, 0, 0, 0]);
	const colors = $derived([
		`hsl(${sliders[0] * 1.2}, 80%, 80%)`,
		`hsl(${sliders[1] * 1.2}, 80%, 80%)`,
		`hsl(${sliders[2] * 1.2}, 80%, 80%)`,
		`hsl(${sliders[3] * 1.2}, 80%, 80%)`
	]);

	interface TabChangeEventTarget extends EventTarget {
		activeTabIndex: number;
	}

	let activeTab = $state(1);
	const tabChange = (event: Event) => {
		const target = event.target as unknown as TabChangeEventTarget;
		console.log(`Primary tab changed to ${target.activeTabIndex}`);
		// console.log("=== playground - user-interface - tabChange - event ===");
		// console.log(event)
		activeTab = target.activeTabIndex;
	};

	const tabContent = ['Tab content 1', 'Tab content 2', 'Tab content 3'];

	const cardContent = $derived(tabContent[activeTab]);
</script>

<!-- <div class="px-10">
    <label
        for="customRange1"
        class="mb-2 inline-block text-primary-700 dark:text-primary-300"
        >Status</label
    >
    <input
        type="range"
        data-te-tooltip="true"
        class="transparent h-[4px] w-full cursor-pointer appearance-none border-transparent bg-neutral-200 dark:bg-neutral-600"
        id="customRange1" />
</div> -->

<div>
	<Heading>Card</Heading>
	<div class="card sm:max-w-sm">
		<div class="card-text-body bg-primary-container text-primary-container-content shadow-primary">
			<h5 class="card-title mb-2.5">Body of a Card here</h5>
			<p class="mb-4">
				Soe text to fill in the body fo the card. This could be anything here. But for now just text
				filling in here.
			</p>
			<div class="card-actions">
				<button class="btn btn-primary">Card button</button>
			</div>
		</div>
	</div>
</div>
<HorizontalRule />

<Heading>Tabs</Heading>
<Tabs {tabs}>Some Text common to all tabs</Tabs>
<HorizontalRule />

<Heading>Card with tabs</Heading>
<md-filled-card class="w-100 m-10 p-10">
	<md-tabs onchange={tabChange}>
		<md-primary-tab active={activeTab == 0}>Tab 1</md-primary-tab>
		<md-primary-tab active={activeTab == 1}>Tab 2</md-primary-tab>
		<md-primary-tab active={activeTab == 2}>Tab 3</md-primary-tab>
	</md-tabs>
	<md-tabs>
		<md-secondary-tab>Tab A</md-secondary-tab>
		<md-secondary-tab>Tab B</md-secondary-tab>
	</md-tabs>
	<div class="text-2xl"><Heading>{cardContent}</Heading></div>
</md-filled-card>
<HorizontalRule />

<Heading>Vertical Tabs</Heading>
<VerticalTabs />
<HorizontalRule />

<Heading>User Form</Heading>
<div class="flex justify-center">
	<UserForm type="signup" />
	<UserForm type="login" />
</div>
<HorizontalRule />

<Heading>Card</Heading>
<Card
	title="Title of Card"
	description="Some text inside the card to describe what's going on here. The button links to this page."
	href=""
></Card>
<HorizontalRule />

<Heading>Status slider</Heading>
<p class="text-center text-2xl">Status: {sliderValue}</p>
<!-- TBD refactor into bindable prop! -->
<md-slider
	class="w-full p-10"
	value={sliderValue}
	oninput={(e: Event) => (sliderValue = parseInt((e.target as HTMLInputElement).value))}
></md-slider>

<div class="w-100 m-10 p-10" style="background-color: {color};">
	STATUS: {sliderValue}
</div>
<hr class="mx-5 my-12 h-2 bg-neutral-500 opacity-100 dark:opacity-50" />
<HorizontalRule />

<Heading>Multiple status sliders</Heading>

<table class="w-full">
	<thead>
		<tr>
			<th>Left of Topic 1</th>
			<th>Between topic 1 and 2</th>
			<th>Between topic 2 and 3</th>
			<th>Right of topic 3</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td class="px-10 text-center">
				<md-slider
					class="w-full p-1"
					value={sliders[0]}
					oninput={(e: Event) => (sliders[0] = parseInt((e.target as HTMLInputElement).value))}
				></md-slider>
				{sliders[0]}
			</td>
			<td class="px-10 text-center">
				<md-slider
					class="w-full p-1"
					value={sliders[1]}
					oninput={(e: Event) => (sliders[1] = parseInt((e.target as HTMLInputElement).value))}
				></md-slider>
				{sliders[1]}
			</td>
			<td class="px-10 text-center">
				<md-slider
					class="w-full p-1"
					value={sliders[2]}
					oninput={(e: Event) => (sliders[2] = parseInt((e.target as HTMLInputElement).value))}
				></md-slider>
				{sliders[2]}
			</td>
			<td class="px-10 text-center">
				<md-slider
					class="w-full p-1"
					value={sliders[3]}
					oninput={(e: Event) => (sliders[3] = parseInt((e.target as HTMLInputElement).value))}
				></md-slider>
				{sliders[3]}
			</td>
		</tr>
	</tbody>
</table>

<!-- <div class="p-10">Left of Topic 1:
<md-slider class="p-1" value={sliders[0]} on:input={(e:Event) => sliders[0] = e.target?.value}></md-slider>
{sliders[0]}
<md-slider class="p-1" value={sliders[1]} on:input={(e:Event) => sliders[1] = e.target?.value}></md-slider>
{sliders[1]}
</div> -->
<!-- <div
	data-twe-multi-range-slider-init
	data-twe-tooltip="true"
	data-twe-number-of-ranges="1"
	on:valueChanged.te.multiRangeSlider={(e) => (sliders[1] = e.values.rounded)}
	class="p-10"
>
	Between topic 1 and 2: {sliders[1]}
</div> -->

<!-- <div
	data-twe-multi-range-slider-init
	data-twe-tooltip="true"
	data-twe-number-of-ranges="1"
	on:valueChanged.te.multiRangeSlider={(e) => (sliders[2] = e.values.rounded)}
	class="p-10"
>
	Between topic 2 and 3: {sliders[2]}
</div>

<div
	data-twe-multi-range-slider-init
	data-twe-tooltip="true"
	data-twe-number-of-ranges="1"
	on:valueChanged.te.multiRangeSlider={(e) => (sliders[3] = e.values.rounded)}
	class="p-10"
>
	Right of topic 3: {sliders[3]}
</div> -->

<!-- {#each colors as color, i}
    <div class="w-100 m-10 p-10" style="background-color: {color};">
        STATUS: {sliders[i]}
    </div>
{/each} -->

<!-- TBD: change to Tailwind rows and columns -->
<!-- TBD: change to Tailwind gradients: https://tailwindcss.com/docs/gradient-color-stops#starting-color ?-->
<div class="w-100 m-10 flex">
	<div
		class="flex h-20 w-1/3 items-center justify-center text-2xl"
		style="background: linear-gradient(to right, {colors[0]}, {colors[1]});"
	>
		Topic 1
	</div>
	<div
		class="flex h-20 w-1/3 items-center justify-center text-2xl"
		style="background: linear-gradient(to right, {colors[1]}, {colors[2]});"
	>
		Topic 2
	</div>
	<div
		class="flex h-20 w-1/3 items-center justify-center text-2xl"
		style="background: linear-gradient(to right, {colors[2]}, {colors[3]});"
	>
		Topic 3
	</div>
</div>

<HorizontalRule />

<Heading>Tailwind CSS gradient</Heading>

<div class="w-100 m-10 bg-gradient-to-r from-cyan-500 to-blue-500 p-10">STATUS:</div>

<HorizontalRule />
