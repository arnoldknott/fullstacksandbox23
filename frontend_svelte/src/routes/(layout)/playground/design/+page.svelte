<script lang="ts">
	import Card from '$components/Card.svelte';
	import Heading from '$components/Heading.svelte';
	import AccordionItem from './AccordionItem.svelte';
	import ContentText from './ContentText.svelte';
	import AppText from './AppText.svelte';
	import ContentButtons from './ContentButtons.svelte';
</script>

<Heading>🚧 Construction sites for design experiments 🚧</Heading>

<div class="grid grid-cols-1 gap-8 md:grid-cols-3">
	<Card
		title="FlyonUI 1"
		description="Playground and showcase for flyonUI components and design"
		href={`/playground/design/flyonui`}
	></Card>
	<Card
		title="Material Design 3"
		description="Playground and showcase for Material Design 3 components and design"
		href={`/playground/design/materialdesign`}
	></Card>
	<Card
		title="TailwindCSS 3"
		description="Formating playground for styling with TailwindCSS utility classes"
		href={`/playground/design/tailwindcss`}
	></Card>
	<Card
		title="Comparison"
		description="Directly putting components right next to each other to compare them"
		href={`/playground/design/comparison`}
	></Card>
</div>

<Heading>👍 Results, ready for use 👍</Heading>

<div class="accordion accordion-bordered divide-y" data-accordion-always-open="">
	<AccordionItem title="Backgrounds">
		<div class="grid h-screen w-full grid-cols-6 bg-background text-base-content">
			<div class="bg-background p-4 text-center">Background</div>
			<div class="h-2/6 min-h-fit bg-base-100 p-4 text-center">base-100</div>
			<div class="h-3/6 min-h-fit bg-base-150 p-4 text-center">base-150</div>
			<div class="h-4/6 min-h-fit bg-base-200 p-4 text-center">base-200</div>
			<div class="h-5/6 min-h-fit bg-base-200 p-4 text-center">base-250</div>
			<div class="h-6/6 min-h-fit bg-base-300 p-4 text-center">base-300</div>
		</div>
	</AccordionItem>
	<AccordionItem title="Text and colors for content">
		<div class="grid h-screen min-h-fit w-full grid-cols-6 bg-background text-base-content">
			<div class="p-4">
				Background
				<ContentText />
			</div>
			<div class="h-2/6 min-h-fit bg-base-100 p-4">
				base-100
				<ContentText />
			</div>
			<div class="h-3/6 min-h-fit bg-base-150 p-4">
				base-150
				<ContentText />
			</div>
			<div class="h-4/6 min-h-fit bg-base-200 p-4">
				base-200
				<ContentText />
			</div>
			<div class="h-5/6 min-h-fit bg-base-250 p-4">
				base-250
				<ContentText />
			</div>
			<div class="h-6/6 min-h-fit bg-base-300 p-4">
				base-300
				<ContentText />
			</div>
		</div>
	</AccordionItem>
	<AccordionItem title="Text and colors for app functionality">
		<div class="grid h-screen min-h-fit w-full grid-cols-6 bg-background text-base-content">
			<div class="p-4">
				Background
				<AppText />
			</div>
			<div class="h-2/6 min-h-fit bg-base-100 p-4">
				base-100
				<AppText />
			</div>
			<div class="h-3/6 min-h-fit bg-base-150 p-4">
				base-150
				<AppText />
			</div>
			<div class="h-4/6 min-h-fit bg-base-200 p-4">
				base-200
				<AppText />
			</div>
			<div class="h-5/6 min-h-fit bg-base-250 p-4">
				base-250
				<AppText />
			</div>
			<div class="h-6/6 min-h-fit bg-base-300 p-4">
				base-300
				<AppText />
			</div>
		</div>
	</AccordionItem>
	<AccordionItem title="Buttons for content control">
		<div class="grid h-screen min-h-fit w-full grid-cols-3 md:grid-cols-6 bg-background text-base-content">
			<div class="p-4">
				Background
				<ContentButtons />
			</div>
			<div class="h-2/6 min-h-fit bg-base-100 p-4">
				base-100
				<ContentButtons />
			</div>
			<div class="h-3/6 min-h-fit bg-base-150 p-4">
				base-150
				<ContentButtons />
			</div>
			<div class="h-4/6 min-h-fit bg-base-200 p-4">
				base-200
				<ContentButtons />
			</div>
			<div class="h-5/6 min-h-fit bg-base-250 p-4">
				base-250
				<ContentButtons />
			</div>
			<div class="h-6/6 min-h-fit bg-base-300 p-4">
				base-300
				<ContentButtons />
			</div>
		</div>
		
	</AccordionItem>
	<AccordionItem title="Buttons for app functionality">
		<div class="grid h-screen min-h-fit w-full grid-cols-3 sm:grid-cols-6 bg-background text-base-content">
			<div class="p-4">
				Background
				
			</div>
			<div class="h-2/6 min-h-fit bg-base-100 p-4">
				base-100
				
			</div>
			<div class="h-3/6 min-h-fit bg-base-150 p-4">
				base-150
				
			</div>
			<div class="h-4/6 min-h-fit bg-base-200 p-4">
				base-200
				
			</div>
			<div class="h-5/6 min-h-fit bg-base-250 p-4">
				base-250
				
			</div>
			<div class="h-6/6 min-h-fit bg-base-300 p-4">
				base-300
				
			</div>
			<div class="skeleton h-screen w-full bg-base-100 text-base-content">
				<div class="flex flex-col gap-2 p-4">
					<p class="body-small">Base-100 background with base-content text</p>
					<div class="flex flex-row flex-wrap gap-4 pl-6">
						
					</div>
					<div class="flex flex-row flex-wrap gap-4 pl-6">
						<div class="flex flex-col gap-2">
							<button class="btn btn-info rounded-full bg-info text-info-content">Info</button>
							<button class="btn-info-container btn rounded-full">Info Container</button>
						</div>
						<div class="flex flex-col gap-2">
							<button class="btn btn-success rounded-full bg-success text-success-content"
								>Success</button
							>
							<button class="btn-success-container btn rounded-full">Success Container</button>
						</div>
						<div class="flex flex-col gap-2">
							<button class="btn btn-warning rounded-full bg-warning text-warning-content"
								>Warning</button
							>
							<button class="btn-warning-container btn rounded-full">Warning Container</button>
						</div>
						<div class="flex flex-col gap-2">
							<button class="btn btn-error rounded-full bg-error text-error-content">Error</button>
							<button class="btn-error-container btn rounded-full">Error Container</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</AccordionItem>
</div>
