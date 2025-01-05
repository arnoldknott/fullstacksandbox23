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
</div>
