<script lang="ts">
	import { initCollapse, initOverlay, initScrollspy } from '$lib/userInterface';
	import type { Snippet } from 'svelte';
	let { children }: { children: Snippet } = $props();
</script>

<div id="scrollspy-scrollable-parent" class="relative">
	<dialog
		id="collapsible-sidebar"
		class="overlay border-base-content/20 overlay-open:translate-x-0 drawer drawer-start sm:overlay-layout-open:translate-x-0 hidden w-64 border-e [--auto-close:sm] [--body-scroll:true] [--is-layout-affect:true] [--opened:lg] sm:absolute sm:z-0 sm:flex sm:shadow-none lg:[--overlay-backdrop:false]"
		tabindex="-1"
		{@attach initOverlay}
	>
		<div class="drawer-body px-2 pt-4">
			<ul
				class="menu sticky p-0"
				data-scrollspy="#scrollspy"
				data-scrollspy-scrollable-parent="#scrollspy-scrollable-parent"
				{@attach initScrollspy}
			>
				<li class="scrollspy-active:text-primary">
					<a href="#loreum1">
						<span class="icon-[tabler--home] size-5"></span>
						Home
					</a>
				</li>
				<li class="scrollspy-active:text-primary">
					<a href="#loreum2">
						<span class="icon-[tabler--user] size-5"></span>
						Account
					</a>
				</li>
				<li data-scrollspy-group="" class="space-y-0.5">
					<a
						class="collapse-toggle collapse-open:bg-base-content/10"
						id="menu-app"
						data-collapse="#menu-app-collapse"
						{@attach initCollapse}
					>
						<span class="icon-[tabler--apps] size-5"></span>
						Apps
						<span
							class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
						></span>
					</a>
					<ul
						id="menu-app-collapse"
						class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
						aria-labelledby="menu-app"
					>
						<li class="scrollspy-active:text-primary">
							<a href="#loreum3">
								<span class="icon-[tabler--message] size-5"></span>
								Chat
							</a>
						</li>
						<li class="scrollspy-active:text-primary">
							<a href="#loreum4">
								<span class="icon-[tabler--calendar] size-5"></span>
								Calendar
							</a>
						</li>
						<li class="space-y-0.5">
							<a
								class="collapse-toggle collapse-open:bg-base-content/10"
								id="sub-menu-academy"
								data-collapse="#sub-menu-academy-collapse"
								{@attach initCollapse}
							>
								<span class="icon-[tabler--book] size-5"></span>
								Academy
								<span class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4"></span>
							</a>
							<ul
								id="sub-menu-academy-collapse"
								class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
								aria-labelledby="sub-menu-academy"
							>
								<li>
									<a href="#loreum5">
										<span class="icon-[tabler--books] size-5"></span>
										Courses
									</a>
								</li>
								<li>
									<a href="#loreum6">
										<span class="icon-[tabler--list-details] size-5"></span>
										Course details
									</a>
								</li>
								<li class="space-y-0.5">
									<a
										class="collapse-toggle collapse-open:bg-base-content/10"
										id="sub-menu-academy-stats"
										data-collapse="#sub-menu-academy-stats-collapse"
										{@attach initCollapse}
									>
										<span class="icon-[tabler--chart-bar] size-5"></span>
										Stats
										<span class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4"
										></span>
									</a>
									<ul
										id="sub-menu-academy-stats-collapse"
										class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
										aria-labelledby="sub-menu-academy-stats"
									>
										<li>
											<a href="#loreum7">
												<span class="icon-[tabler--chart-donut] size-5"></span>
												Goals
											</a>
										</li>
									</ul>
								</li>
							</ul>
						</li>
					</ul>
				</li>
				<li>
					<a href="#loreum8">
						<span class="icon-[tabler--mail] size-5"></span>
						Email
					</a>
				</li>

				<li>
					<a href="#loreum9">
						<span class="icon-[tabler--shopping-bag] size-5"></span>
						Product
					</a>
				</li>
			</ul>
		</div>
	</dialog>

	<div class="sm:overlay-layout-open:ps-64 bg-base-100 min-h-full transition-all duration-300">
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
		<p class="text-base-content/50 label label-large px-2 py-1">
			Note, for demonstration of the sidebar, it is not all the way left in the window, but relative
			to the content of this page.
		</p>
		{@render children?.()}
	</div>
</div>
