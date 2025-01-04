<script lang="ts">
	import Card from '$components/Card.svelte';
</script>

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
