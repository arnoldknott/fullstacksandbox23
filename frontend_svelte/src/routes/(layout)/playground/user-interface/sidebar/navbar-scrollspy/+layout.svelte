<script lang="ts">
	import { initCollapse, initOverlay, initScrollspy } from '$lib/userInterface';
	import Display from '$components/Display.svelte';
	import type { Snippet } from 'svelte';
	import { resolve } from '$app/paths';
	let { children }: { children: Snippet } = $props();
</script>

<nav
	class="navbar bg-base-100 max-sm:rounded-box border-base-content/25 relative max-sm:shadow-sm sm:z-1 sm:border-b"
>
	<button
		type="button"
		class="btn btn-text max-sm:btn-square me-2"
		aria-haspopup="dialog"
		aria-expanded="false"
		aria-controls="with-navbar-sidebar"
		data-overlay="#with-navbar-sidebar"
		aria-label="Toggle Sidebar"
	>
		<span class="icon-[tabler--menu-2] overlay-layout-open:hidden size-5"></span>
		<span class="icon-[tabler--menu-3] overlay-layout-open:block hidden size-5"></span>
	</button>
	<div class="flex flex-1 items-center">
		<a
			class="link text-base-content link-neutral text-xl font-semibold no-underline"
			href="./navbar/#"
		>
			Fullstack Sandbox
		</a>
	</div>
	<div class="navbar-end flex items-center gap-4">
		<div
			class="dropdown relative inline-flex [--auto-close:inside] [--offset:8] [--placement:bottom-end]"
		>
			<button
				id="dropdown-scrollable"
				type="button"
				class="dropdown-toggle btn btn-text btn-circle dropdown-open:bg-base-content/10 size-10"
				aria-haspopup="menu"
				aria-expanded="false"
				aria-label="Dropdown"
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
				aria-labelledby="dropdown-scrollable"
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
				<a href="#" class="dropdown-footer justify-center gap-1">
					<span class="icon-[tabler--eye] size-4"></span>
					View all
				</a>
			</div>
		</div>
		<div
			class="dropdown relative inline-flex [--auto-close:inside] [--offset:8] [--placement:bottom-end]"
		>
			<button
				id="dropdown-scrollable"
				type="button"
				class="dropdown-toggle flex items-center"
				aria-haspopup="menu"
				aria-expanded="false"
				aria-label="Dropdown"
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
					<a class="dropdown-item" href="#">
						<span class="icon-[tabler--user]"></span>
						My Profile
					</a>
				</li>
				<li>
					<a class="dropdown-item" href="#">
						<span class="icon-[tabler--settings]"></span>
						Settings
					</a>
				</li>
				<li>
					<a class="dropdown-item" href="#">
						<span class="icon-[tabler--receipt-rupee]"></span>
						Billing
					</a>
				</li>
				<li>
					<a class="dropdown-item" href="#">
						<span class="icon-[tabler--help-triangle]"></span>
						FAQs
					</a>
				</li>
				<li class="dropdown-footer gap-2">
					<a class="btn btn-error btn-soft btn-block" href="#">
						<span class="icon-[tabler--logout]"></span>
						Sign out
					</a>
				</li>
			</ul>
		</div>
	</div>
</nav>

<div class="h-screen w-screen pt-50">
	<div id="scrollspy-scrollable-parent" class="max-h-96 overflow-y-auto">
		<aside
			id="with-navbar-sidebar"
			class="overlay border-base-content/20 overlay-open:translate-x-0 drawer drawer-start sm:overlay-layout-open:translate-x-0 hidden w-64 border-e pt-50 [--auto-close:sm] [--body-scroll:true] [--is-layout-affect:true] [--opened:lg] sm:absolute sm:z-0 sm:flex sm:shadow-none lg:[--overlay-backdrop:false]"
			{@attach initOverlay}
			tabindex="-1"
		>
			<div class="drawer-body px-2 pt-4">
				<ul
					class="sticky top-0 text-sm leading-6"
					data-scrollspy="#scrollspy"
					data-scrollspy-scrollable-parent="#scrollspy-scrollable-parent"
					{@attach initScrollspy}
				>
					<li class="text-base-content text-xl font-medium">Index</li>
					<li data-scrollspy-group="">
						<a
							href="#loreum1"
							class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content active block py-0.5 font-medium"
						>
							Loreum 1
						</a>
						<ul>
							<li class="ms-0.5 sm:ms-4">
								<a
									href="#loreum2"
									class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
								>
									<span class="icon-[tabler--point] size-4"></span>
									Loreum 2
								</a>
							</li>
							<li class="ms-0.5 sm:ms-4">
								<a
									href="#loreum3"
									class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
								>
									<span class="icon-[tabler--point] size-4"></span>
									Loreum 3
								</a>
							</li>
						</ul>
					</li>
				</ul>
				<ul
					class="menu p-0"
					data-scrollspy="#scrollspy"
					data-scrollspy-scrollable-parent="#scrollspy-scrollable-parent"
					{@attach initScrollspy}
				>
					<li class="text-base-content text-xl font-medium">Index</li>
					<li data-scrollspy-group="">
						<a
							href="#loreum1"
							class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content active block py-0.5 font-medium"
						>
							Loreum 1
						</a>
						<ul>
							<li class="ms-0.5 sm:ms-4">
								<a
									href="#loreum2"
									class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
								>
									<span class="icon-[tabler--point] size-4"></span>
									Loreum 2
								</a>
							</li>
							<li class="ms-0.5 sm:ms-4">
								<a
									href="#loreum3"
									class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
								>
									<span class="icon-[tabler--point] size-4"></span>
									Loreum 3
								</a>
							</li>
						</ul>
					</li>
					<!-- <li>
						<a href={resolve('/')}>
							<span class="icon-[tabler--home] size-5"></span>
							Home
						</a>
					</li> -->
					<!-- <li>
						<a href="#">
							<span class="icon-[tabler--user] size-5"></span>
							Account
						</a>
					</li>
					<li>
						<a href="#">
							<span class="icon-[tabler--message] size-5"></span>
							Notifications
						</a>
					</li>
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
					<li>
						<a href="#">
							<span class="icon-[tabler--shopping-bag] size-5"></span>
							Product
						</a>
					</li>
					<li>
						<a href="#">
							<span class="icon-[tabler--login] size-5"></span>
							Sign In
						</a>
					</li>
					<li>
						<a href="#">
							<span class="icon-[tabler--logout-2] size-5"></span>
							Sign Out
						</a>
					</li> -->
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
						<!-- <ul
							id="menu-this-page-collapse"
							class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
							aria-labelledby="menu-this-page"
							data-scrollspy="#scrollspy"
							data-scrollspy-scrollable-parent="#scrollspy-scrollable-parent"
							{@attach initScrollspy}
						>
							<li data-scrollspy-group="">
								<a
									href="#loreum1"
									class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content active block py-0.5 font-medium"
								>
									Loreum 1
								</a>
								<ul>
									<li class="ms-0.5 sm:ms-4">
										<a
											href="#loreum2"
											class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
										>
											<span class="icon-[tabler--point] size-4"></span>
											Loreum 2
										</a>
									</li>
									<li class="ms-0.5 sm:ms-4">
										<a
											href="#loreum3"
											class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
										>
											<span class="icon-[tabler--point] size-4"></span>
											Loreum 3
										</a>
									</li>
								</ul>
							</li>
						</ul> -->
						<ul
							id="menu-this-page-collapse"
							class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
							aria-labelledby="menu-this-page"
							data-scrollspy="#scrollspy"
							data-scrollspy-scrollable-parent="#scrollspy-scrollable-parent"
							{@attach initScrollspy}
						>
							<li data-scrollspy-group="">
								<a
									href="#loreum1"
									class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content active block py-0.5 font-medium"
								>
									Loreum 1
								</a>
								<ul>
									<li class="ms-0.5 sm:ms-4">
										<a
											href="#loreum2"
											class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
										>
											<span class="icon-[tabler--point] size-4"></span>
											Loreum 2
										</a>
									</li>
									<li class="ms-0.5 sm:ms-4">
										<a
											href="#loreum3"
											class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
										>
											<span class="icon-[tabler--point] size-4"></span>
											Loreum 3
										</a>
									</li>
								</ul>
							</li>
							<!-- </ul>
						<ul
							id="menu-this-page-collapse"
							class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
							aria-labelledby="menu-this-page"
							data-scrollspy="#scrollspy"
							data-scrollspy-scrollable-parent="#scrollspy-scrollable-parent"
							{@attach initScrollspy}
						>
							<li
								data-scrollspy-group=""
								class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content active block py-0.5 font-medium"
							>
								<a href="#loreum1">
									<span class="icon-[mdi--text] size-5"></span>
									Loreum 1
								</a>
							</li>
							<li
								data-scrollspy-group=""
								class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content block py-0.5 font-medium"
							>
								<a href="#loreum2">
									<span class="icon-[mdi--text] size-5"></span>
									Loreum 2
								</a>
							</li> -->
							<!-- In <li>: -->
							<!-- class="scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content active" -->
							<!-- class="scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content" -->
							<li data-scrollspy-group="" class="space-y-0.5">
								<a
									class="collapse-toggle collapse-open:bg-base-content/10"
									id="sub-menu-academy"
									data-collapse="#sub-menu-academy-collapse"
									{@attach initCollapse}
								>
									<span class="icon-[tabler--book] size-5"></span>
									Sub category
									<span class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4"></span>
								</a>
								<ul
									id="sub-menu-academy-collapse"
									class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
									aria-labelledby="sub-menu-academy"
								>
									<li class="scrollspy-active:text-primary">
										<a
											href="#loreum3"
											class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
										>
											<span class="icon-[mdi--text] size-5"></span>
											Loreum 3
										</a>
									</li>
									<li>
										<a
											href="#loreum4"
											class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
										>
											<span class="icon-[mdi--text] size-5"></span>
											Loreum 4
										</a>
									</li>
								</ul>
							</li>
							<li>
								<a
									href="#loreum5"
									class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
								>
									<span class="icon-[mdi--text] size-5"></span>
									Loreum 5
								</a>
							</li>
							<li>
								<a
									href="#loreum6"
									class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
								>
									<span class="icon-[mdi--text] size-5"></span>
									Loreum 6
								</a>
							</li>
						</ul>
					</li>
				</ul>
			</div>

			<div class="drawer-body px-2 pt-4">
				<ul
					class="sticky top-0 text-sm leading-6"
					data-scrollspy="#scrollspy"
					data-scrollspy-scrollable-parent="#scrollspy-scrollable-parent"
					{@attach initScrollspy}
				>
					<li class="text-base-content text-xl font-medium">Index</li>
					<li data-scrollspy-group="">
						<a
							href="#loreum1"
							class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content active block py-0.5 font-medium"
						>
							Loreum 1
						</a>
						<ul>
							<li class="ms-0.5 sm:ms-4">
								<a
									href="#loreum2"
									class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
								>
									<span class="icon-[tabler--point] size-4"></span>
									Loreum 2
								</a>
							</li>
							<li class="ms-0.5 sm:ms-4">
								<a
									href="#loreum3"
									class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
								>
									<span class="icon-[tabler--point] size-4"></span>
									Loreum 3
								</a>
							</li>
						</ul>
					</li>
					<li>
						<a
							href="#loreum4"
							class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content block py-0.5 font-medium"
						>
							Loreum 4
						</a>
					</li>
					<li data-scrollspy-group="">
						<a
							href="#loreum5"
							class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content block py-0.5 font-medium"
						>
							Loreum 5
						</a>
						<ul>
							<li class="ms-0.5 sm:ms-4">
								<a
									href="#loreum6"
									class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
								>
									<span class="icon-[tabler--point] size-4"></span>
									Loreum 6
								</a>
							</li>
							<li class="ms-0.5 sm:ms-4">
								<a
									href="#loreum7"
									class="text-base-content/80 hover:text-base-content scrollspy-active:bg-accent-container scrollspy-active:text-accent-container-content flex items-center gap-x-2 py-0.5"
								>
									<span class="icon-[tabler--point] size-4"></span>
									Loreum 7
								</a>
							</li>
						</ul>
					</li>
				</ul>
			</div>
		</aside>

		<!-- <div class="sm:overlay-layout-open:ps-64 bg-base-100 min-h-full transition-all duration-300">
	<div class="px-2">
		<button
			type="button"
			class="btn btn-text btn-square"
			aria-haspopup="dialog"
			aria-expanded="false"
			aria-controls="with-navbar-sidebar"
			data-overlay="#with-navbar-sidebar"
			aria-label="Toggle Sidebar"
		>
			<span class="icon-[tabler--menu-2] size-5"></span>
		</button>
	</div>
</div> -->

		<div class="sm:overlay-layout-open:ps-64">
			<Display>Navbar and Sidebar and Scrollspy</Display>
			<div id="scrollspy" class="max-w-lg space-y-4 pe-1">
				{@render children?.()}
			</div>
		</div>
	</div>
</div>
