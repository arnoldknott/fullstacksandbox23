<script lang="ts">
	import { resolve } from '$app/paths';
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';
	import { Button } from '$components/shadcn/button';
	import { Card, CardContent, CardHeader, CardTitle } from '$components/shadcn/card';
	import Title from '$components/Title.svelte';
</script>

<Display>Shadcn/ui 1</Display>

<Heading id="integration" class="link"
	><a href={resolve('/(layout)/playground/design/shadcn/integration')}>Integration</a></Heading
>
<p class="m-4">
	Shadcn comes itself with plenty of design configuration. Prior to shadcn, the project contained
	FlyonUI, which is integrated with Material Design 3 design tokens and philospphy. The
	<a class="link" href={resolve('/(layout)/playground/design/shadcn/integration')}
		>integration page</a
	>
	adopts the previously developed features and designs to shadcn.
</p>

<Heading id="design-variables">Design Variables</Heading>

<Heading id="button">Button</Heading>

<Card>
	<CardHeader>
		<CardTitle><Title id="color">Color</Title></CardTitle>
	</CardHeader>
	<CardContent>
		<div class="grid grid-cols-2 justify-between gap-4 md:grid-cols-4 lg:grid-cols-8">
			<Button class="text-primary-content hover:bg-primary/80">Primary</Button>
			<Button class="bg-secondary text-secondary-content hover:bg-secondary/80">Secondary</Button>
			<Button class="bg-accent text-accent-content hover:bg-accent/80">Accent</Button>
			<Button class="bg-neutral text-neutral-content hover:bg-neutral/80">Neutral</Button>
			<Button class="bg-info text-info-content hover:bg-info/80">Info</Button>
			<Button class="bg-success text-success-content hover:bg-success/80">Success</Button>
			<Button class="bg-warning text-warning-content hover:bg-warning/80">Warning</Button>
			<Button class="bg-error text-error-content hover:bg-error/80">Error</Button>
			<Button
				class="bg-primary-container text-primary-container-content hover:bg-primary-container/80"
				>Primary</Button
			>
			<Button
				class="bg-secondary-container text-secondary-container-content hover:bg-secondary-container/80"
				>Secondary</Button
			>
			<Button class="bg-accent-container text-accent-container-content hover:bg-accent-container/80"
				>Accent</Button
			>
			<Button
				class="bg-neutral-container text-neutral-container-content hover:bg-neutral-container/80"
				>Neutral</Button
			>
			<Button class="bg-info-container text-info-container-content hover:bg-info-container/80"
				>Info</Button
			>
			<Button
				class="bg-success-container text-success-container-content hover:bg-success-container/80"
				>Success</Button
			>
			<Button
				class="bg-warning-container text-warning-container-content hover:bg-warning-container/80"
				>Warning</Button
			>
			<Button class="bg-error-container text-error-container-content hover:bg-error-container/80"
				>Error</Button
			>
		</div>
	</CardContent>
</Card>
<Card>
	<CardHeader>
		<CardTitle><Title id="size">Size</Title></CardTitle>
	</CardHeader>
	<CardContent>
		<div class="grid grid-cols-2 justify-between gap-4 md:grid-cols-4 lg:grid-cols-8">
			<Button size="xs">Extra Small</Button>
			<Button size="sm">Small</Button>
			<Button size="default">Default</Button>
			<Button size="lg">Large</Button>
			<div class="col-span-4">
				Icons missing - replace icons from FlyonUI with direct use of Iconify?
			</div>
			<!-- <Button size="icon">Icon</Button>
			<Button size="icon-xs">Icon XS</Button>
			<Button size="icon-sm">Icon SM</Button>
			<Button size="icon-lg">Icon LG</Button> -->
		</div>
	</CardContent>
</Card>
<Card>
	<CardHeader>
		<CardTitle><Title id="variants">Variants</Title></CardTitle>
	</CardHeader>
	<CardContent>
		<div class="grid grid-cols-2 justify-between gap-4 md:grid-cols-4 lg:grid-cols-8">
			<Button variant="default">Default</Button>
			<Button variant="outline">Outline</Button>
			<Button variant="secondary">Secondary</Button>
			<Button variant="ghost">Ghost</Button>
			<Button variant="destructive">Destructive</Button>
			<Button variant="link">Link</Button>
			<Button href="#">Converted</Button>
			<Button disabled>Disabled</Button>
		</div>
	</CardContent>
</Card>
