<script lang="ts">
	// Recreates scrolling from 6b33032
	import Loreum from '../../Loreum.svelte';
</script>

<main class="h-screen overflow-scroll">
	<div id="mainContent" class="mx-5 mt-5 h-full">
		<nav
			class="navbar rounded-box bg-base-100 shadow-shadow border-outline-variant sticky start-0 top-0 z-1 justify-between border-b shadow-sm md:flex md:items-center"
		>
			<div class="navbar-start">LEFT</div>
			<div class="navbar-center">NAVBAR</div>
			<div class="navbar-end">RIGHT</div>
		</nav>

		<div class="mt-5">
			<Loreum />
		</div>
	</div>
</main>
