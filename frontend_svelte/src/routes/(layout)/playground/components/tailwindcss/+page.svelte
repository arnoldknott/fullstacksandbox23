<script lang="ts">
	import Title from '$components/Title.svelte';
</script>

<div class="mx-5 grid grid-cols-1 gap-4 xl:grid-cols-2">
	<div>
		<Title>Colors</Title>
		<div class="grid grid-cols-4 xl:grid-cols-8 gap-4">
            <div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-primary">
                    <p class="text-center text-xl text-primary-content">primary</p>
                </div>
                <div class="skeleton flex h-12 w-36 items-center justify-center bg-primary-content">
                    <p class="text-center text-xl text-primary">primary-content</p>
                </div>
            </div>
		</div>
	</div>
</div>
