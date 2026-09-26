<script lang="ts">
	import type { RevealApi } from 'reveal.js';

	import RevealJs from '$components/RevealJS.svelte';

	import FramedSlide from './FramedSlide.svelte';

	let revealInstance = $state<RevealApi | undefined>(undefined);
</script>

<RevealJs bind:reveal={revealInstance}>
	<section>
		<div class="text-base-content-variant text-[200px] font-bold">Welcome</div>
	</section>
	<!-- <FramedSlide>
			<div
			class="r-stretch my-50 grid grid-cols-[1fr_max-content_1fr] items-center justify-between justify-items-start gap-12 text-7xl"
			// class="r-stretch mx-auto my-20 grid w-fit grid-cols-[auto_max-content_auto] items-center gap-12 text-7xl"
		>
			<a href="#motivation" class="justify-self-end" aria-label="Motivation"
				><span class="icon-[vaadin--thumbs-up-o] bg-primary"></span></a
			>
			<a href="#motivation" aria-label="Motivation"
				><div class="text-primary font-bold">Motivation</div></a
			>
			<div></div>
			<a href="#diversity" aria-label="Diversity" class="justify-self-end"
				><span class="icon-[material-symbols--diversity-1-rounded] bg-primary"></span></a
			>
			<a href="#diversity" aria-label="Diversity"
				><div class="text-primary font-bold">Diversity</div></a
			>
			<div></div>
			<a href="#overview" aria-label="Overview" class="justify-self-end"
				><span class="icon-[grommet-icons--overview] bg-primary"></span></a
			>
			<a href="#overview" aria-label="Overview"
				><div class="text-primary font-bold">Overview</div></a
			>
			<div></div>
		</div>
	</FramedSlide> -->
	<FramedSlide>Allan Watts - Chinese Farmer</FramedSlide>
	<FramedSlide>Drawing from BusinessIllustrator - closed box</FramedSlide>
	<FramedSlide>Course 2nd semester -> linearising</FramedSlide>
	<FramedSlide>Course 2nd semester -> a bit closer to reality</FramedSlide>
	<FramedSlide>
		Master level -> closely related to product design -> linearized models ain't no good any more
	</FramedSlide>
	<FramedSlide>Drawing from BusinessIllustrator - box opened</FramedSlide>
</RevealJs>
