<script lang="ts">
	let { title, description, href } = $props();
</script>

<div class="card">
	<div class="card-body rounded-2xl bg-base-300">
		<h5 class="text-title-large card-title mb-2.5 text-primary">{title}</h5>
		<p class="text-body text-body-small mb-2.5 text-primary-container-content">
			{description}
		</p>
		<div class="card-actions text-center">
			<a {href}
				><button
					class="text-label-small btn btn-primary rounded-full px-3 text-primary-content shadow-primary"
					>Link to {title.toLowerCase()}</button
				></a
			>
		</div>
	</div>
</div>

<!--
<div class="block rounded-lg bg-white text-left shadow-lg dark:bg-neutral-600">
	<div class="p-6">
		<a
			{href}
			class="mt-3 inline-block rounded bg-blue-500 px-6 pb-2 pt-2.5 text-xs font-medium uppercase leading-normal text-white shadow-[0_4px_9px_-4px_#3b71ca] transition duration-150 ease-in-out hover:bg-blue-600 hover:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] focus:bg-blue-600 focus:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] focus:outline-none focus:ring-0 active:bg-blue-700 active:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] dark:shadow-[0_4px_9px_-4px_rgba(59,113,202,0.5)] dark:hover:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)] dark:focus:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)] dark:active:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)]"
		>
			<h5 class="mb-2 text-xl font-bold tracking-wide text-neutral-800 dark:text-neutral-50">
				{title}
			</h5>
		</a>

		<p class="mb-2 text-base text-neutral-500 dark:text-neutral-300">
			{description}
		</p>
	</div>
</div>
-->
<!-- Card -->
