<script lang="ts">
	import { initOverlay, initScrollspy, initCollapse } from '$lib/userInterface';
	import type { Snippet } from 'svelte';
	let { children }: { children: Snippet } = $props();
</script>

<div class="h-screen w-screen">
	<div id="scrollspy-scrollable-parent" class="grid h-screen grid-cols-5 overflow-y-auto">
		<aside
			id="collapsible-sidebar"
			class="overlay border-base-content/20 overlay-open:translate-x-0 drawer drawer-start sm:overlay-layout-open:translate-x-0 col-span-2 hidden w-64 border-e pt-20 [--auto-close:sm] [--body-scroll:true] [--is-layout-affect:true] [--opened:lg] sm:absolute sm:z-0 sm:col-span-1 sm:flex sm:shadow-none lg:[--overlay-backdrop:false]"
			tabindex="-1"
			{@attach initOverlay}
		>
			<div class="drawer-body px-2 pt-4">
				<ul class="menu p-0">
					<li>
						<a href="/">
							<span class="icon-[tabler--home] size-5"></span>
							Home
						</a>
					</li>
					<li>
						<a href="./scrollspy/">
							<span class="icon-[tabler--user] size-5"></span>
							Other page
						</a>
					</li>
					<li class="space-y-0.5">
						<a
							class="collapse-toggle collapse-open:bg-base-content/10"
							id="menu-this-page"
							data-collapse="#menu-this-page-collapse"
							{@attach initCollapse}
						>
							<span class="icon-[icon-park-outline--page] size-5"></span>
							This page
							<span
								class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
							></span>
						</a>
						<ul
							id="menu-this-page-collapse"
							class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
							aria-labelledby="menu-this-page"
							data-scrollspy="#scrollspy"
							data-scrollspy-scrollable-parent="#scrollspy-scrollable-parent"
							{@attach initScrollspy}
						>
							<li>
								<a
									href="#loreum1"
									class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									Loreum 1
								</a>
							</li>
							<li>
								<a
									href="#loreum2"
									class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									Loreum 2
								</a>
							</li>
							<li data-scrollspy-group="" class="space-y-0.5">
								<div class="join w-full">
									<!-- <a
									class="collapse-toggle collapse-open:bg-base-content/10"
									id="sub-menu-category"
									data-collapse="#sub-menu-category-collapse"
									{@attach initCollapse}
								>
									<span class="icon-[icon-park-outline--page] size-5"></span>
									Sub Category
									<span
										class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
									></span>
								</a> -->
									<a
										class="scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content join-item"
										href="#sub-category"
										id="sub-menu-category"
										{@attach initCollapse}
									>
										<span class="icon-[tabler--book] size-5"></span>
										Sub category
									</a>
									<button
										class="collapse-toggle collapse-open:bg-base-content/10 join-item"
										data-collapse="#sub-menu-category-collapse"
										aria-label="Sub category menu"
									>
										<span class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4"
										></span>
									</button>
								</div>
								<ul
									id="sub-menu-category-collapse"
									class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
									aria-labelledby="sub-menu-category"
								>
									<li>
										<a
											href="#loreum3"
											class="group text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
										>
											<span
												class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
											></span>
											<span
												class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
											></span>
											Loreum 3
										</a>
									</li>
									<li>
										<a
											href="#loreum4"
											class="group text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
										>
											<span
												class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
											></span>
											<span
												class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
											></span>
											Loreum 4
										</a>
									</li>
								</ul>
							</li>
							<li>
								<a
									href="#loreum5"
									class="group text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									Loreum 5
								</a>
							</li>
							<li>
								<a
									href="#loreum6"
									class="group text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
								>
									<span
										class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
									></span>
									<span
										class="icon-[mdi--text] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
									></span>
									Loreum 6
								</a>
							</li>
						</ul>
					</li>
					<li class="space-y-0.5">
						<a
							class="collapse-toggle collapse-open:bg-base-content/10"
							id="menu-app"
							data-collapse="#menu-app-collapse"
						>
							<span class="icon-[tabler--apps] size-5"></span>
							Page on Apps
							<span
								class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
							></span>
						</a>
						<ul
							id="menu-app-collapse"
							class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
							aria-labelledby="menu-app"
							{@attach initCollapse}
						>
							<li>
								<a href="./scrollspy/#">
									<span class="icon-[tabler--message] size-5"></span>
									App1
								</a>
							</li>
							<li>
								<a href="#loreum4">
									<span class="icon-[tabler--calendar] size-5"></span>
									App2
								</a>
							</li>
							<li class="space-y-0.5">
								<a
									class="collapse-toggle collapse-open:bg-base-content/10"
									id="sub-menu-academy"
									data-collapse="#sub-menu-academy-collapse"
								>
									<span class="icon-[tabler--book] size-5"></span>
									Academy
									<span class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4"></span>
								</a>
								<ul
									id="sub-menu-academy-collapse"
									class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
									aria-labelledby="sub-menu-academy"
									{@attach initCollapse}
								>
									<li>
										<a href="./scrollspy/#">
											<span class="icon-[tabler--books] size-5"></span>
											Courses
										</a>
									</li>
									<li>
										<a href="./scrollspy/#">
											<span class="icon-[tabler--list-details] size-5"></span>
											Course details
										</a>
									</li>
									<li class="space-y-0.5">
										<a
											class="collapse-toggle collapse-open:bg-base-content/10"
											id="sub-menu-academy-stats"
											data-collapse="#sub-menu-academy-stats-collapse"
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
												<a href="./scrollspy/#">
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
						<a href="./scrollspy/#">
							<span class="icon-[tabler--mail] size-5"></span>
							Further Page
						</a>
					</li>

					<li>
						<a href="./scrollspy/#">
							<span class="icon-[tabler--shopping-bag] size-5"></span>
							About
						</a>
					</li>
				</ul>
			</div>
		</aside>
		<div
			class="sm:overlay-layout-open:ps-64 bg-base-100 col-span-3 transition-all duration-300 sm:col-span-4"
		>
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
			<div class=" bg-base-100 transition-all duration-300">
				<div id="scrollspy" class="space-y-4 pe-1">
					{@render children?.()}
				</div>
			</div>
		</div>
	</div>
</div>

<!-- <div id="scrollspy-scrollable-parent" class="relative">
	<div class="grid grid-cols-4">
		<div class="col-span-2 sm:col-span-1">
			<aside
				id="collapsible-sidebar"
				class="overlay border-base-content/20 overlay-open:translate-x-0 drawer drawer-start sm:overlay-layout-open:translate-x-0 hidden w-64 border-e [--auto-close:sm] [--body-scroll:true] [--is-layout-affect:true] [--opened:lg] sm:absolute sm:z-0 sm:flex sm:shadow-none lg:[--overlay-backdrop:false]"
				tabindex="-1"
				{@attach initOverlay}
			>
				<div class="drawer-body px-2 pt-4">
					
				</div>
			</aside>
		</div>

		<div id="scrollspy" class="col-span-3 sm:col-span-4">
			<div class="sm:overlay-layout-open:ps-64 bg-base-100 transition-all duration-300">
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
					Note, for demonstration of the sidebar,
					it is not all the way top in the window,
					but relative to the content of this page.
				</p>
				{@render children?.()}
			</div>
		</div>
	</div>
</div> -->
