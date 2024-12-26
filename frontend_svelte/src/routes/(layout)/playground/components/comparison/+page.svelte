<script lang="ts">
	import Title from '$components/Title.svelte';
</script>

<div class="w-full grid grid-cols-1 gap-4 xl:grid-cols-2">
	<div class="col-span-2">
		<Title>Colors</Title>
		<p class="text-center text-2xl">Color matching Material Design => FlyonUI:</p>
		<div class="grid grid-cols-2 gap-2 xl:grid-cols-4">
			<div>
				<div
					class="w-84 skeleton flex h-24 items-center justify-center"
					style="background-color: var(--md-sys-color-primary);"
				>
					<p class="text-center text-xl" style="color: var(--md-sys-color-on-primary);">primary</p>
				</div>
			</div>
			<div class="w-84 skeleton flex h-24 items-center justify-center bg-primary">
				<p class="text-center text-xl text-primary-content">primary</p>
			</div>
		</div>
		<div class="grid grid-cols-2 gap-2 xl:grid-cols-4">
			<div>
				<div
					class="w-84 skeleton flex h-24 items-center justify-center"
					style="background-color: var(--md-sys-color-on-primary);"
				>
					<p class="text-center text-xl" style="color: var(--md-sys-color-primary);">onPrimary</p>
				</div>
			</div>
			<div class="w-84 skeleton flex h-24 items-center justify-center bg-primary-content">
				<p class="text-center text-xl text-primary">primary-content</p>
			</div>
		</div>
	</div>
</div>
