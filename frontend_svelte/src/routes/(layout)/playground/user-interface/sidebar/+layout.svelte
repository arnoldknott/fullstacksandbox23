<script lang="ts">
	import { initOverlay } from '$lib/userInterface';
	import type { Snippet } from 'svelte';
	let { children }: { children: Snippet } = $props();
</script>

<aside
	id="collapsible-sidebar"
	class="overlay border-base-content/20 overlay-open:translate-x-0 drawer drawer-start sm:overlay-layout-open:translate-x-0 hidden w-64 border-e [--auto-close:sm] [--body-scroll:true] [--is-layout-affect:true] [--opened:lg] sm:absolute sm:z-0 sm:flex sm:shadow-none lg:[--overlay-backdrop:false]"
	tabindex="-1"
	{@attach initOverlay}
>
	<div class="drawer-body px-2 pt-4">
		<ul class="menu p-0">
			<li>
				<a href="./sidebar#loreum1">
					<span class="icon-[tabler--home] size-5"></span>
					Home
				</a>
			</li>
			<li>
				<a href="./sidebar#loreum2">
					<span class="icon-[tabler--user] size-5"></span>
					Account
				</a>
			</li>
			<li>
				<a href="./sidebar#loreum3">
					<span class="icon-[tabler--message] size-5"></span>
					Notifications
				</a>
			</li>
			<li>
				<a href="./sidebar#loreum4">
					<span class="icon-[tabler--mail] size-5"></span>
					Email
				</a>
			</li>
			<li>
				<a href="./sidebar#loreum5">
					<span class="icon-[tabler--calendar] size-5"></span>
					Calendar
				</a>
			</li>
			<li>
				<a href="./sidebar#loreum6">
					<span class="icon-[tabler--shopping-bag] size-5"></span>
					Product
				</a>
			</li>
			<li>
				<a href="./sidebar#loreum7">
					<span class="icon-[tabler--login] size-5"></span>
					Sign In
				</a>
			</li>
			<li>
				<a href="./sidebar#loreum8">
					<span class="icon-[tabler--logout-2] size-5"></span>
					Sign Out
				</a>
			</li>
		</ul>
	</div>
</aside>

<div class="sm:overlay-layout-open:ps-64 bg-base-100 min-h-full transition-all duration-300">
	<!-- Navigation Toggle -->
	<div class="px-2">
		<button
			type="button"
			class="btn btn-text btn-square"
			aria-haspopup="dialog"
			aria-expanded="false"
			aria-controls="collapsible-sidebar"
			data-overlay="#collapsible-sidebar"
			aria-label="Toggle Sidebar"
		>
			<span class="icon-[tabler--menu-2] size-5"></span>
		</button>
	</div>
</div>

<div class="overlay-layout-open:ps-64 transition-all duration-300">
	{@render children?.()}
</div>
