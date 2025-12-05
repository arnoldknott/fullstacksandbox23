<script lang="ts">
	// Recreates scrolling from 6b33032 and adds sidebar
	import Loreum from '../../Loreum.svelte';
	import { initOverlay } from '$lib/userInterface';
</script>

{#snippet sidebarToggleButton(classes: string, overlayModifier: object)}
	<button
		type="button"
		class="btn btn-square btn-sm btn-outline btn-primary {classes}"
		aria-haspopup="dialog"
		aria-expanded="false"
		aria-controls="collapsible-mini-sidebar"
		aria-label="Toggle Sidebar"
		{...overlayModifier}
	>
		<span
			class="icon-[material-symbols--menu-open-rounded] overlay-minified:hidden flex size-6 max-sm:hidden"
		></span>
		<span class="icon-[material-symbols--menu] overlay-minified:flex hidden size-6 max-sm:flex"
		></span>
	</button>
{/snippet}

<main data-theme="light" class="h-screen overflow-scroll">
	<div id="mainContent" class="mx-5 mt-5 h-full">
		<nav
			class="navbar rounded-box bg-base-100 shadow-shadow border-outline-variant sticky start-0 top-0 z-1 justify-between border-b shadow-sm md:flex md:items-center"
		>
			<div class="navbar-start">
				<div class="navbar-start rtl:[--placement:bottom-end]">
					<ul class="menu menu-horizontal flex flex-nowrap items-center">
						{@render sidebarToggleButton('hidden sm:flex', {
							'data-overlay-minifier': '#collapsible-mini-sidebar'
						})}
						{@render sidebarToggleButton('sm:hidden', {
							'data-overlay': '#collapsible-mini-sidebar'
						})}
						<li>LEFT</li>
					</ul>
				</div>
			</div>
			<div class="navbar-center">NAVBAR</div>
			<div class="navbar-end">RIGHT</div>
		</nav>

		<aside
			id="collapsible-mini-sidebar"
			class="overlay overlay-minified:w-19 overlay-open:translate-x-0 drawer drawer-start border-base-content/20 hidden w-66 border-e pt-26 [--auto-close:sm] sm:absolute sm:z-0 sm:flex sm:translate-x-0 sm:shadow-none"
			tabindex="-1"
			{@attach initOverlay}
		>
			<div class="drawer-body px-2 pt-4">
				<ul class="menu p-0">
					<li>Sidebar Item 1</li>
					<li>Sidebar Item 2</li>
					<li>Sidebar Item 3</li>
					<Loreum repetition={2} />
					<li>Sidebar Item 4</li>
				</ul>
			</div>
		</aside>

		<div class="sm:overlay-minified:ps-19 overlay-open:ps-0 mt-5 ps-0 sm:ps-66">
			<Loreum />
		</div>
	</div>
</main>
