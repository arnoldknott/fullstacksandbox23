<script lang="ts">
	import { initDropdown, initOverlay, initCollapse, initScrollspy } from '$lib/userInterface';
	import { type Snippet } from 'svelte';
	let { children }: { children: Snippet } = $props();

	let sidebar: HTMLElement;

	// const toggleSidebar = () => {
	// 	if (sidebar) {
	// 		const sideBarInstance = window.HSOverlay.getInstance(sidebar, true);
	// 		// console.log('=== playground - collapse - sidebar instance');
	// 		// console.log(sideBarInstance);
	// 		const isOpen = 'open' in sideBarInstance.element.el.className.split(' ');
	// 		console.log('=== sidebar isOpen: ' + isOpen);
	// 		const isClosed = 'hidden' in sideBarInstance.element.el.className.split(' ');
	// 		console.log('=== sidebar isClosed: ' + isClosed);
	// 		const isMinified = 'minified' in sideBarInstance.element.el.className.split(' ');
	// 		console.log('=== sidebar isMinified: ' + isMinified);
	// 		if (isOpen) {
	// 			console.log('=== playground - collapse - sidebar is open');
	// 			window.HSOverlay.close(sidebar);
	// 			// } else if (isMinified) {
	// 			// 	console.log('=== playground - collapse - sidebar is minified');
	// 			// 	window.HSOverlay.open(sidebar);
	// 		} else {
	// 			console.log('=== playground - collapse - sidebar is closed');
	// 			window.HSOverlay.open(sidebar);
	// 		}
	// 		// if (isClosed || isMinified) {
	// 		// 	console.log('=== playground - collapse - sidebar is closed or minified');
	// 		// 	window.HSOverlay.open(sidebar);
	// 		// 	// } else if (isMinified) {
	// 		// 	// 	console.log('=== playground - collapse - sidebar is minified');
	// 		// 	// 	window.HSOverlay.open(sidebar);
	// 		// } else {
	// 		// 	console.log('=== playground - collapse - sidebar is open');
	// 		// 	window.HSOverlay.close(sidebar);
	// 		// }
	// 	}
	// };

	// const toggleSidebar = () => {
	// 	if (sidebar) {
	// 		const sideBarInstance = window.HSOverlay.getInstance(sidebar, true);
	// 		const isClosed = 'hidden' in sideBarInstance.element.el.className.split(' ');
	// 		if (isClosed) {
	// 			window.HSOverlay.open(sidebar);
	// 		} else {
	// 			window.HSOverlay.close(sidebar);
	// 		}
	// 	}
	// };

	const openSidebar = () => {
		const { element } = window.HSOverlay.getInstance('#collapsible-mini-sidebar', true);
		element.open();
		window.HSStaticMethods.autoInit();
	};
</script>

<nav
	class="navbar bg-base-100 max-sm:rounded-box border-base-content/25 relative max-sm:shadow-sm sm:z-1 sm:border-b"
>
	<button
		type="button"
		class="btn btn-text btn-square hidden sm:block"
		aria-haspopup="dialog"
		aria-expanded="false"
		aria-controls="collapsible-mini-sidebar"
		data-overlay-minifier="#collapsible-mini-sidebar"
		aria-label="Toggle Sidebar"
	>
		<span
			class="icon-[material-symbols--menu-open-rounded] overlay-minified:hidden size-6 max-sm:hidden"
		></span>
		<span class="icon-[material-symbols--menu] overlay-minified:block hidden size-6 max-sm:block"
		></span>
	</button>
	<button
		type="button"
		class="btn btn-text btn-square sm:hidden"
		aria-haspopup="dialog"
		aria-expanded="false"
		aria-controls="collapsible-mini-sidebar"
		data-overlay="#collapsible-mini-sidebar"
		aria-label="Toggle Sidebar"
	>
		<span
			class="icon-[material-symbols--menu-open-rounded] overlay-minified:hidden size-6 max-sm:hidden"
		></span>
		<span class="icon-[material-symbols--menu] overlay-minified:block hidden size-6 max-sm:block"
		></span>
	</button>
	<div class="flex flex-1 items-center">
		<a class="link text-base-content link-neutral text-xl font-semibold no-underline" href="/">
			Fullstack Platform
		</a>
	</div>
	<div class="navbar-end flex items-center gap-4">
		<div
			class="dropdown relative inline-flex [--auto-close:inside] [--offset:8] [--placement:bottom-end]"
			{@attach initDropdown}
		>
			<button
				id="dropdown-notifications"
				type="button"
				class="dropdown-toggle btn btn-text btn-circle dropdown-open:bg-base-content/10 size-10"
				aria-haspopup="menu"
				aria-expanded="false"
				aria-label="Notifications Dropdown"
			>
				<div class="indicator">
					<span class="indicator-item bg-error size-2 rounded-full"></span>
					<span class="icon-[tabler--bell] text-base-content size-5.5"></span>
				</div>
			</button>
			<div
				class="dropdown-menu dropdown-open:opacity-100 hidden"
				role="menu"
				aria-orientation="vertical"
				aria-labelledby="dropdown-notifications"
			>
				<div class="dropdown-header justify-center">
					<h6 class="text-base-content text-base">Notifications</h6>
				</div>
				<div
					class="text-base-content/80 max-h-56 overflow-auto overflow-x-auto overflow-y-auto max-md:max-w-60"
				>
					<div class="dropdown-item">
						<div class="avatar avatar-away-bottom">
							<div class="w-10 rounded-full">
								<img src="https://cdn.flyonui.com/fy-assets/avatar/avatar-1.png" alt="avatar 1" />
							</div>
						</div>
						<div class="w-60">
							<h6 class="truncate text-base">Charles Franklin</h6>
							<small class="text-base-content/50 truncate">Accepted your connection</small>
						</div>
					</div>
					<div class="dropdown-item">
						<div class="avatar">
							<div class="w-10 rounded-full">
								<img src="https://cdn.flyonui.com/fy-assets/avatar/avatar-2.png" alt="avatar 2" />
							</div>
						</div>
						<div class="w-60">
							<h6 class="truncate text-base">
								Martian added moved Charts & Maps task to the done board.
							</h6>
							<small class="text-base-content/50 truncate">Today 10:00 AM</small>
						</div>
					</div>
					<div class="dropdown-item">
						<div class="avatar avatar-online-bottom">
							<div class="w-10 rounded-full">
								<img src="https://cdn.flyonui.com/fy-assets/avatar/avatar-8.png" alt="avatar 8" />
							</div>
						</div>
						<div class="w-60">
							<h6 class="truncate text-base">New Message</h6>
							<small class="text-base-content/50 truncate">You have new message from Natalie</small>
						</div>
					</div>
					<div class="dropdown-item">
						<div class="avatar avatar-placeholder">
							<div class="bg-neutral text-neutral-content w-10 rounded-full p-2">
								<span class="icon-[tabler--user] size-full"></span>
							</div>
						</div>
						<div class="w-60">
							<h6 class="truncate text-base">Application has been approved 🚀</h6>
							<small class="text-base-content/50 text-wrap"
								>Your ABC project application has been approved.</small
							>
						</div>
					</div>
					<div class="dropdown-item">
						<div class="avatar">
							<div class="w-10 rounded-full">
								<img src="https://cdn.flyonui.com/fy-assets/avatar/avatar-10.png" alt="avatar 10" />
							</div>
						</div>
						<div class="w-60">
							<h6 class="truncate text-base">New message from Jane</h6>
							<small class="text-base-content/50 text-wrap">Your have new message from Jane</small>
						</div>
					</div>
					<div class="dropdown-item">
						<div class="avatar">
							<div class="w-10 rounded-full">
								<img src="https://cdn.flyonui.com/fy-assets/avatar/avatar-3.png" alt="avatar 3" />
							</div>
						</div>
						<div class="w-60">
							<h6 class="truncate text-base">Barry Commented on App review task.</h6>
							<small class="text-base-content/50 truncate">Today 8:32 AM</small>
						</div>
					</div>
				</div>
				<a href="#top" class="dropdown-footer justify-center gap-1">
					<span class="icon-[tabler--eye] size-4"></span>
					View all
				</a>
			</div>
		</div>
		<div
			class="dropdown relative inline-flex [--auto-close:inside] [--offset:8] [--placement:bottom-end]"
			{@attach initDropdown}
		>
			<button
				id="dropdown-avatar"
				type="button"
				class="dropdown-toggle flex items-center"
				aria-haspopup="menu"
				aria-expanded="false"
				aria-label="Avatar Dropdown"
			>
				<div class="avatar">
					<div class="size-9.5 rounded-full">
						<img src="https://cdn.flyonui.com/fy-assets/avatar/avatar-1.png" alt="avatar 1" />
					</div>
				</div>
			</button>
			<ul
				class="dropdown-menu dropdown-open:opacity-100 hidden min-w-60"
				role="menu"
				aria-orientation="vertical"
				aria-labelledby="dropdown-avatar"
			>
				<li class="dropdown-header gap-2">
					<div class="avatar">
						<div class="w-10 rounded-full">
							<img src="https://cdn.flyonui.com/fy-assets/avatar/avatar-1.png" alt="avatar" />
						</div>
					</div>
					<div>
						<h6 class="text-base-content text-base font-semibold">John Doe</h6>
						<small class="text-base-content/50">Admin</small>
					</div>
				</li>
				<li>
					<a class="dropdown-item" href="#top">
						<span class="icon-[tabler--user]"></span>
						My Profile
					</a>
				</li>
				<li>
					<a class="dropdown-item" href="#top">
						<span class="icon-[tabler--settings]"></span>
						Settings
					</a>
				</li>
				<li>
					<a class="dropdown-item" href="#top">
						<span class="icon-[tabler--receipt-rupee]"></span>
						Billing
					</a>
				</li>
				<li>
					<a class="dropdown-item" href="#top">
						<span class="icon-[tabler--help-triangle]"></span>
						FAQs
					</a>
				</li>
				<li class="dropdown-footer gap-2">
					<a class="btn btn-error btn-soft btn-block" href="#top">
						<span class="icon-[tabler--logout]"></span>
						Sign out
					</a>
				</li>
			</ul>
		</div>
	</div>
</nav>

<div id="scrollspy-scrollable-parent" class="grid h-screen overflow-y-auto">
	<!-- <aside
		id="collapsible-mini-sidebar"
		class="overlay overlay-minified:w-17 overlay-open:translate-x-0 drawer drawer-start border-base-content/20 hidden w-66 border-e pt-50 [--auto-close:sm] sm:absolute sm:z-0 sm:flex sm:translate-x-0 sm:shadow-none"
		{@attach initOverlay}
		tabindex="-1"
		bind:this={sidebar}
	>
		<div class="drawer-body px-2 pt-4">
			<ul class="menu p-0">
				<li>
					<a href="#">
						<span class="icon-[tabler--home] size-5"></span>
						<span class="overlay-minified:hidden">Home</span>
					</a>
				</li>
				<li>
					<a href="#">
						<span class="icon-[tabler--user] size-5"></span>
						<span class="overlay-minified:hidden">Account</span>
					</a>
				</li>
				<li>
					<a href="#">
						<span class="icon-[tabler--message] size-5"></span>
						<span class="overlay-minified:hidden">Notifications</span>
					</a>
				</li>
				<li
					class="dropdown overlay-minified:[--adaptive:adaptive] overlay-minified:[--strategy:fixed] overlay-minified:[--offset:15] overlay-minified:[--trigger:hover] overlay-minified:[--placement:right-start] relative [--adaptive:none] [--strategy:static]"
				>
					<button
						id="dropdown-default"
						type="button"
						class="dropdown-toggle"
						aria-haspopup="menu"
						aria-expanded="false"
						aria-label="Dropdown"
					>
						<span class="icon-[tabler--apps] size-5"></span>
						<span class="overlay-minified:hidden">Apps</span>
						<span
							class="icon-[tabler--chevron-down] dropdown-open:rotate-180 overlay-minified:hidden size-4"
						></span>
					</button>
					<ul
						class="dropdown-menu overlay-minified:shadow-md overlay-minified:shadow-base-300/20 dropdown-open:opacity-100 overlay-minified:before:absolute overlay-minified:before:-start-4 overlay-minified:before:top-0 overlay-minified:before:h-full overlay-minified:before:w-4 mt-0 hidden min-w-60 shadow-none before:bg-transparent"
						role="menu"
						aria-orientation="vertical"
						aria-labelledby="dropdown-default"
					>
						<li>
							<a href="#">
								<span class="icon-[tabler--mail] size-5"></span>
								Email
							</a>
						</li>
						<li>
							<a href="#">
								<span class="icon-[tabler--calendar] size-5"></span>
								Calendar
							</a>
						</li>
					</ul>
				</li>
				<li>
					<a href="#">
						<span class="icon-[tabler--shopping-bag] size-5"></span>
						<span class="overlay-minified:hidden">Product</span>
					</a>
				</li>
				<li>
					<a href="#">
						<span class="icon-[tabler--login] size-5"></span>
						<span class="overlay-minified:hidden">Sign In</span>
					</a>
				</li>
				<li>
					<a href="#">
						<span class="icon-[tabler--logout-2] size-5"></span>
						<span class="overlay-minified:hidden">Sign Out</span>
					</a>
				</li>
			</ul>
		</div>
	</aside> -->
	<aside
		id="collapsible-mini-sidebar"
		class="overlay overlay-minified:w-17 overlay-open:translate-x-0 drawer drawer-start border-base-content/20 hidden w-66 border-e pt-50 [--auto-close:sm] sm:absolute sm:z-0 sm:flex sm:translate-x-0 sm:shadow-none"
		tabindex="-1"
		{@attach initOverlay}
		bind:this={sidebar}
	>
		<div class="drawer-body px-2 pt-4">
			<ul class="menu p-0">
				<li>
					<a href="/">
						<span class="icon-[tabler--home] size-5"></span>
						<span class="overlay-minified:hidden">Home</span>
					</a>
				</li>
				<li>
					<a href="./scrollspy/">
						<span class="icon-[tabler--user] size-5"></span>
						<span class="overlay-minified:hidden">Other page</span>
					</a>
				</li>
				<li class="space-y-0.5">
					<a
						class="collapse-toggle collapse-open:bg-base-content/10"
						id="menu-this-page"
						data-collapse="#menu-this-page-collapse"
						{@attach initCollapse}
					>
						<!-- aria-controls="collapsible-mini-sidebar"
						data-overlay-minifier="#collapsible-mini-sidebar"
                        role="button"
						tabindex="0"
						onclick={() => openSidebar()}
						onkeydown={() => openSidebar()} -->
						<span class="icon-[icon-park-outline--page] size-5"></span>
						<span class="overlay-minified:hidden">This page</span>
						<span
							class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:rotate-270 size-4 transition-all duration-300"
							role="button"
							tabindex="0"
							onclick={() => openSidebar()}
							onkeydown={() => openSidebar()}
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
							<a
								class="collapse-toggle collapse-open:bg-base-content/10 scrollspy-active:italic group"
								id="sub-menu-category"
								data-collapse="#sub-menu-category-collapse"
								href="#sub-category"
								{@attach initCollapse}
							>
								<span
									class="icon-[tabler--hand-finger-right] hidden size-5 group-[.active]:inline group-[.scrollspy-active]:inline"
								></span>
								<span
									class="icon-[icon-park-outline--page] size-5 group-[.active]:hidden group-[.scrollspy-active]:hidden"
								></span>
								Sub Category
								<span class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4"></span>
							</a>
							<ul
								id="sub-menu-category-collapse"
								class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
								aria-labelledby="sub-menu-category"
							>
								<li>
									<a
										href="#loreum3"
										class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
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
										class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
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
								class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
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
								class="group text-base-content/80 scrollspy-active:italic flex items-center gap-x-2 py-0.5 hover:opacity-100"
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
						<span class="overlay-minified:hidden">Page on Apps</span>
						<span
							class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 transition-all duration-300"
						></span>
					</a>
					<ul
						id="menu-app-collapse"
						class="overlay-minified:hidden collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
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
												Intentions
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
						<span class="overlay-minified:hidden">Further Page</span>
					</a>
				</li>

				<li>
					<a href="./scrollspy/#">
						<span class="icon-[tabler--shopping-bag] size-5"></span>
						<span class="overlay-minified:hidden">About</span>
					</a>
				</li>
			</ul>
		</div>
	</aside>
	<div class="sm:overlay-minified:ps-17 bg-base-100 ps-64 transition-all duration-300 max-sm:ps-0">
		<div class=" bg-base-100 transition-all duration-300">
			<div id="scrollspy" class="space-y-4 pe-1">
				{@render children?.()}
			</div>
		</div>
	</div>
</div>

<!-- <button
	type="button"
	class="btn btn-text max-sm:btn-square sm:hidden"
	aria-haspopup="dialog"
	aria-expanded="false"
	aria-controls="collapsible-mini-sidebar"
	data-overlay="#collapsible-mini-sidebar"
	aria-label="Toggle Sidebar"
>
	<span class="icon-[tabler--menu-2] size-5"></span>
</button> -->

<!-- <aside
	id="collapsible-mini-sidebar"
	class="overlay overlay-minified:w-17 overlay-open:translate-x-0 drawer drawer-start border-base-content/20 hidden w-66 border-e pt-50 [--auto-close:sm] sm:absolute sm:z-0 sm:flex sm:translate-x-0 sm:shadow-none"
	{@attach initOverlay}
	tabindex="-1"
	bind:this={sidebar}
>
	<div class="drawer-body px-2 pt-4">
		<ul class="menu p-0">
			<li>
				<a href="#">
					<span class="icon-[tabler--home] size-5"></span>
					<span class="overlay-minified:hidden">Home</span>
				</a>
			</li>
			<li>
				<a href="#">
					<span class="icon-[tabler--user] size-5"></span>
					<span class="overlay-minified:hidden">Account</span>
				</a>
			</li>
			<li>
				<a href="#">
					<span class="icon-[tabler--message] size-5"></span>
					<span class="overlay-minified:hidden">Notifications</span>
				</a>
			</li>
			<li
				class="dropdown overlay-minified:[--adaptive:adaptive] overlay-minified:[--strategy:fixed] overlay-minified:[--offset:15] overlay-minified:[--trigger:hover] overlay-minified:[--placement:right-start] relative [--adaptive:none] [--strategy:static]"
			>
				<button
					id="dropdown-default"
					type="button"
					class="dropdown-toggle"
					aria-haspopup="menu"
					aria-expanded="false"
					aria-label="Dropdown"
				>
					<span class="icon-[tabler--apps] size-5"></span>
					<span class="overlay-minified:hidden">Apps</span>
					<span
						class="icon-[tabler--chevron-down] dropdown-open:rotate-180 overlay-minified:hidden size-4"
					></span>
				</button>
				<ul
					class="dropdown-menu overlay-minified:shadow-md overlay-minified:shadow-base-300/20 dropdown-open:opacity-100 overlay-minified:before:absolute overlay-minified:before:-start-4 overlay-minified:before:top-0 overlay-minified:before:h-full overlay-minified:before:w-4 mt-0 hidden min-w-60 shadow-none before:bg-transparent"
					role="menu"
					aria-orientation="vertical"
					aria-labelledby="dropdown-default"
				>
					<li>
						<a href="#">
							<span class="icon-[tabler--mail] size-5"></span>
							Email
						</a>
					</li>
					<li>
						<a href="#">
							<span class="icon-[tabler--calendar] size-5"></span>
							Calendar
						</a>
					</li>
				</ul>
			</li>
			<li>
				<a href="#">
					<span class="icon-[tabler--shopping-bag] size-5"></span>
					<span class="overlay-minified:hidden">Product</span>
				</a>
			</li>
			<li>
				<a href="#">
					<span class="icon-[tabler--login] size-5"></span>
					<span class="overlay-minified:hidden">Sign In</span>
				</a>
			</li>
			<li>
				<a href="#">
					<span class="icon-[tabler--logout-2] size-5"></span>
					<span class="overlay-minified:hidden">Sign Out</span>
				</a>
			</li>
		</ul>
	</div>
</aside> -->
