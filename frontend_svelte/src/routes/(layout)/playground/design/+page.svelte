<script lang="ts">
	import Card from '$components/Card.svelte';
	import Heading from '$components/Heading.svelte';
	import AccordionItem from './AccordionItem.svelte';
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
<AccordionItem title="🎨 Colors 🎨">
		<div class="skeleton bg-base-00 text-base-content w-full h-screen">
			<div class="flex flex-col gap-2 p-4">
				<p>Base-100 background with base-content text</p>
				<div class="flex flex-row flex-wrap gap-4  pl-6">
					<div class="flex flex-col gap-2 border rounded-md p-4">
						<button class="btn btn-primary rounded-full bg-primary text-primary-content">Primary</button>
						<button class="btn btn-primary-container rounded-full ">Primary Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn btn-secondary rounded-full bg-secondary text-secondary-content">Secondary</button>
						<button class="btn btn-secondary-container rounded-full ">Secondary Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn btn-accent rounded-full bg-accent text-accent-content">Accent</button>
						<button class="btn btn-accent-container rounded-full ">Accent Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn btn-neutral rounded-full bg-neutral text-neutral-content">Neutral</button>
						<button class="btn btn-neutral-container rounded-full ">Neutral Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn btn-info rounded-full bg-info text-info-content">Info</button>
						<button class="btn btn-info-container rounded-full ">Info Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn btn-success rounded-full bg-success text-success-content">Success</button>
						<button class="btn btn-success-container rounded-full ">Success Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn btn-warning rounded-full bg-warning text-warning-content">Warning</button>
						<button class="btn btn-warning-container rounded-full ">Warning Container</button>
					</div>
					<div class="flex flex-col gap-2">
						<button class="btn btn-error rounded-full bg-error text-error-content">Error</button>
						<button class="btn btn-error-container rounded-full ">Error Container</button>
					</div>
				</div>
			</div>
		</div>
	</AccordionItem>
</div>