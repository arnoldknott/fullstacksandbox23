<script lang="ts">
	import Heading from '$components/Heading.svelte';
</script>

<div class="mx-5 grid grid-cols-1 gap-4 xl:grid-cols-2">
	<div>
		<Heading>Colors</Heading>
		<div class="grid grid-cols-4 gap-4 xl:grid-cols-8">
			<div>
				<div class="skeleton flex h-36 w-36 items-center justify-center bg-orange-500">
					<p class="text-center text-xl text-green-800">bg-orange-500, text-green-800</p>
				</div>
				<div class="skeleton flex h-12 w-36 items-center justify-center bg-sky-500">
					<p class="text-center text-xl text-black">bg-sky-500</p>
				</div>
				<div class="skeleton flex h-12 w-36 items-center justify-center bg-sky-500/50">
					<p class="text-center text-xl text-black">bg-sky-500/50</p>
				</div>
			</div>
		</div>
	</div>

	<div>
		<Heading>Responsive utilities</Heading>
		<div>
			<div class="input-filled w-full mt-4">
				<input
					type="text"
					placeholder="John Doe"
					class="input input-xs md:input-md md:input-xl text-error md:text-warning lg:text-success label md:heading lg:display"
					id="filledInputResponsive"
				/>
				<label class="input-filled-label" for="filledInputResponsive"
					>Full name - responsive</label
				>
			</div>
			<div class="input-floating w-full mt-4">
				<input
					type="text"
					placeholder="John Doe"
					class="input input-xs md:input-md md:input-xl text-error md:text-warning lg:text-success label md:heading lg:display"
					id="floatingInputResponsive"
				/>
				<label class="input-floating-label" for="floatingInputResponsive"
					>Full name - responsive</label
				>
			</div>
			<div class="label md:heading lg:display text-error md:text-warning lg:text-success">Checking responsibility with size and color in regular div</div>
		</div>
	</div>
</div>
