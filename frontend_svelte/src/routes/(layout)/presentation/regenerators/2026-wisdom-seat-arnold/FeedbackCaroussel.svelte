<script lang="ts">
	import { initCarousel } from '$lib/userInterface';
</script>

<div id="vertical-thumbnails" data-carousel class="relative w-[1200px]">
	<div class="carousel flex space-x-2 rounded-none" {@attach initCarousel}>
		<div class="flex-none">
			<div
				class="carousel-pagination flex h-full w-[250px] flex-col justify-between gap-y-1 overflow-hidden max-sm:w-8"
			>
				<div
					class="carousel-pagination-item carousel-active:opacity-100 text-neutral-container-content flex grow items-center rounded-lg object-cover text-4xl opacity-30"
				>
					Learning
				</div>
				<div
					class="carousel-pagination-item carousel-active:opacity-100 text-neutral-container-content flex grow items-center rounded-lg object-cover text-4xl opacity-30"
				>
					Responsibility
				</div>
				<div
					class="carousel-pagination-item carousel-active:opacity-100 text-neutral-container-content flex grow items-center rounded-lg object-cover text-4xl opacity-30"
				>
					Motivation
				</div>
			</div>
		</div>
		<div class="relative grow overflow-hidden rounded-2xl">
			<div class="carousel-body h-120 opacity-0">
				<!-- Slide 1 -->
				<div class="carousel-slide">
					<div class="flex size-full">
						<img
							src="/regenerators/2026-wisdom-seat-arnold/feedback-learning.jpg"
							class="size-fit rounded-3xl object-cover"
							alt="Feedback on learning"
						/>
					</div>
				</div>
				<!-- Slide 2 -->
				<div class="carousel-slide">
					<div class="flex size-full">
						<img
							src="/regenerators/2026-wisdom-seat-arnold/feedback-responsibility.jpg"
							class="size-fit rounded-3xl object-cover"
							alt="Feedback on responsibility"
						/>
					</div>
				</div>
				<!-- Slide 3 -->
				<div class="carousel-slide">
					<div class="flex size-full">
						<img
							src="/regenerators/2026-wisdom-seat-arnold/feedback-motivation.jpg"
							class="size-fit rounded-3xl object-cover"
							alt="Feedback on motivation"
						/>
					</div>
				</div>
			</div>
			<!-- Previous Slide -->
			<!-- <button
				type="button"
				class="carousel-prev carousel-disabled:opacity-50 bg-base-100 shadow-base-300/20 start-5 flex size-9.5 items-center justify-center rounded-full shadow-sm max-sm:start-3"
			>
				<span class="icon-[tabler--chevron-left] size-5 cursor-pointer"></span>
				<span class="sr-only">Previous</span>
			</button> -->
			<!-- Next Slide -->
			<!-- <button
				type="button"
				class="carousel-next carousel-disabled:opacity-50 bg-base-100 shadow-base-300/20 end-5 flex size-9.5 items-center justify-center rounded-full shadow-sm max-sm:end-3"
			>
				<span class="icon-[tabler--chevron-right] size-5"></span>
				<span class="sr-only">Next</span>
			</button> -->
		</div>
	</div>
</div>
