<script lang="ts">
	import { initScrollspy } from '$lib/userInterface';
	import Loreum from './(layout)/Loreum.svelte';
	import { scrollY } from 'svelte/reactivity/window';
</script>

<div class="grid min-h-screen grid-cols-5">
	<div
		class="border-base-content/20 sticky top-0 col-span-2 h-screen overflow-y-auto border-r sm:col-span-1"
	>
		<ul class="p-4 text-sm leading-6" data-scrollspy="#scrollspy" {@attach initScrollspy}>
			<li class="text-base-content text-xl font-medium">Index</li>
			<li data-scrollspy-group="">
				<a
					href="#chapter-1"
					class="text-base-content/80 hover:text-base-content scrollspy-active:italic active block py-0.5 font-medium"
				>
					Chapter 1
				</a>
				<ul>
					<li class="ms-0.5 sm:ms-4">
						<a
							href="#chapter-1-1"
							class="text-base-content/80 hover:text-base-content scrollspy-active:italic flex items-center gap-x-2 py-0.5"
						>
							<span class="icon-[tabler--point] size-4"></span>
							Chapter 1-1
						</a>
					</li>
					<li class="ms-0.5 sm:ms-4">
						<a
							href="#chapter-1-2"
							class="text-base-content/80 hover:text-base-content scrollspy-active:italic flex items-center gap-x-2 py-0.5"
						>
							<span class="icon-[tabler--point] size-4"></span>
							Chapter 1-2
						</a>
					</li>
				</ul>
			</li>
			<li>
				<a
					href="#chapter-2"
					class="text-base-content/80 hover:text-base-content scrollspy-active:italic block py-0.5 font-medium"
				>
					Chapter 2
				</a>
			</li>
			<li data-scrollspy-group="">
				<a
					href="#chapter-3"
					class="text-base-content/80 hover:text-base-content scrollspy-active:italic block py-0.5 font-medium"
				>
					Chapter 3
				</a>
				<ul>
					<li class="ms-0.5 sm:ms-4">
						<a
							href="#chapter-3-1"
							class="text-base-content/80 hover:text-base-content scrollspy-active:italic flex items-center gap-x-2 py-0.5"
						>
							<span class="icon-[tabler--point] size-4"></span>
							Chapter 3-1
						</a>
					</li>
					<li class="ms-0.5 sm:ms-4">
						<a
							href="#chapter-3-2"
							class="text-base-content/80 hover:text-base-content scrollspy-active:italic flex items-center gap-x-2 py-0.5"
						>
							<span class="icon-[tabler--point] size-4"></span>
							Chapter 3-2
						</a>
					</li>
				</ul>
			</li>
			<!-- {#each Array(50) as _, index}
				<li>Filler Item {index + 1}</li>
			{/each} -->
			<li>scrollY: {scrollY.current}</li>
		</ul>
	</div>
	<div class="col-span-3 sm:col-span-4">
		<div id="scrollspy" class="space-y-4 p-4 pe-1">
			<div id="chapter-1" class="bg-primary/80 text-primary-content">
				<p class="text-lg font-semibold">Chapter 1</p>
				<Loreum repetition={5} />
			</div>
			<div id="chapter-1-1" class="bg-primary/60 text-primary-content">
				<p class="text-lg font-semibold">Chapter 1-1</p>
				<Loreum repetition={9} />
			</div>
			<div id="chapter-1-2" class="bg-primary/40 text-primary-content">
				<p class="text-lg font-semibold">Chapter 1-2</p>
				<Loreum repetition={11} />
			</div>
			<div id="chapter-2" class="bg-secondary text-secondary-content">
				<p class="text-lg font-semibold">Chapter 2</p>
				<Loreum repetition={5} />
			</div>
			<div id="chapter-3" class="bg-accent/80 text-accent-content">
				<p class="text-lg font-semibold">Chapter 3</p>
				<Loreum repetition={4} />
			</div>
			<div id="chapter-3-1" class="bg-accent/60 text-accent-content">
				<p class="text-lg font-semibold">Chapter 3-1</p>
				<Loreum repetition={7} />
			</div>
			<div id="chapter-3-2" class="bg-accent/40 text-accent-content">
				<p class="text-lg font-semibold">Chapter 3-2</p>
				<Loreum repetition={9} />
			</div>
		</div>
	</div>
</div>
