<script lang="ts">
	import { initDropdown, initOverlay, initCollapse, initScrollspy } from '$lib/userInterface';
	import { type Snippet } from 'svelte';
	let { children }: { children: Snippet } = $props();

	const openSidebar = () => {
		const { element } = window.HSOverlay.getInstance('#collapsible-mini-sidebar', true);
		element.open();
		window.HSStaticMethods.autoInit();
	};

	// for theme picker:
	let mode: 'light' | 'dark' = $state('dark');
	const toggleMode = () => {
		mode = mode === 'dark' ? 'light' : 'dark';
	};
	let sourceColor = $state('#769CDF');
	let variant = $state('TONAL_SPOT');
	const contrastMin = -1.0;
	const contrastMax = 1.0;
	const contrastStep = 0.2;
	let contrast = $state(0.0);
</script>

{#snippet sidebarToggleButton(classes: string, overlayModifier: object)}
	<button
		type="button"
		class="btn btn-square btn-sm btn-outline btn-primary {classes}"
		aria-haspopup="dialog"
		aria-expanded="false"
		aria-controls="collapsible-mini-sidebar"
		aria-label="Toggle Sidebar"
		{...overlayModifier}
	>
		<span
			class="icon-[material-symbols--menu-open-rounded] overlay-minified:hidden flex size-6 max-sm:hidden"
		></span>
		<span class="icon-[material-symbols--menu] overlay-minified:flex hidden size-6 max-sm:flex"
		></span>
	</button>
{/snippet}

<nav
	class="navbar rounded-box bg-base-100 shadow-shadow border-outline-variant relative sticky start-0 top-0 z-1 justify-between border-b shadow-sm md:flex md:items-center"
>
	<!-- <div class="navbar-start">
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
	</div> -->
	<div class="navbar-start">
		{@render sidebarToggleButton('hidden sm:flex', {
			'data-overlay-minifier': '#collapsible-mini-sidebar'
		})}
		{@render sidebarToggleButton('sm:hidden', {
			'data-overlay': '#collapsible-mini-sidebar'
		})}
		<ul class="menu-horizontal ml-4 hidden items-center md:flex md:gap-4">
			<!-- <li>
				<a href="/" aria-label="Home"
					><span class="icon-[material-symbols--home-outline-rounded] bg-neutral size-6"></span></a
				>
			</li> -->
			<li class="text-primary flex items-center gap-1">
				<span class="icon-[mdi--feature-highlight] size-5"></span>
				<a href="/features">Features</a>
			</li>
			<li class="text-primary flex items-center gap-1">
				<span class="icon-[tabler--apps] size-5"></span>
				<a href="/apps">Apps</a>
			</li>
			<li class="text-primary">
				<a href="/construction" class="flex items-center gap-1" aria-label="Contruction"
					><span class="icon-[maki--construction] size-5"></span>
					<span class="hidden lg:block">Construction</span>
				</a>
			</li>
		</ul>
	</div>
	<div class="navbar-center flex flex-row max-sm:scale-50">
		<div class="flex flex-col justify-center">
			<div class="title-small text-primary italic" style="line-height: 1;">Fullstack</div>
			<div class="title-small text-secondary font-bold tracking-wide" style="line-height: 1">
				Platform
			</div>
		</div>
		<div class="heading-large navbar-center text-accent ml-1 flex items-center">23</div>
	</div>
	<div class="navbar-end">
		<button
			class="btn btn-sm btn-text btn-circle text-primary size-8.5 md:hidden"
			aria-label="Search"
		>
			<span class="icon-[tabler--search] size-5.5"></span>
		</button>
		<div class="input mx-2 max-w-56 rounded-full max-md:hidden">
			<span class="icon-[tabler--search] text-base-content/80 my-auto me-3 size-5 shrink-0"></span>
			<label class="sr-only" for="searchInput">Full Name</label>
			<input type="search" class="grow" placeholder="Search" id="searchInput" />
		</div>
		<div
			class="dropdown flex items-center [--auto-close:inside] rtl:[--placement:bottom-end]"
			{@attach initDropdown}
		>
			<span
				id="dropdown-menu-icon-user"
				class="dropdown-toggle icon-[fa6-solid--user] size-6"
				role="button"
				aria-haspopup="menu"
				aria-expanded="false"
				aria-label="User Menu"
			></span>
			<ul
				class="dropdown-menu bg-base-200 text-secondary shadow-outline dropdown-open:opacity-100 hidden shadow-md"
				role="menu"
				aria-orientation="vertical"
				aria-labelledby="dropdown-menu-icon-user"
			>
				<li class="flex items-center gap-2">
					<span class="icon-[material-symbols--palette-outline] size-6"></span>
					<span class="grow"> Theming</span>
					<button aria-label="modeToggler">
						<label id="modeToggler" class="swap swap-rotate">
							<input type="checkbox" onclick={toggleMode} />
							<span class="icon-[tabler--sun] swap-on size-6"></span>
							<span class="icon-[tabler--moon] swap-off size-6"></span>
						</label>
					</button>
				</li>
				<li>
					<div class="w-48">
						<label class="label label-text flex" for="colorPicker">
							<span class="grow">Source color:</span>
							<code>{sourceColor}</code>
						</label>
						<input
							class="w-full"
							type="color"
							id="colorPicker"
							name="color-picker"
							bind:value={sourceColor}
						/>
					</div>
				</li>
				<li>
					<div class="relative w-48">
						<label class="label label-text" for="themeVariant">Variant</label>
						<select
							class="select select-floating max-w-sm"
							aria-label="Select variant"
							id="themeVariant"
							bind:value={variant}
						>
							<option value="TONAL_SPOT">Tonal Spot</option>
							<option value="MONOCHROME">Monochrome</option>
							<option value="NEUTRAL">Neutral</option>
							<option value="VIBRANT">Vibrant</option>
							<option value="EXPRESSIVE">Expressive</option>
							<option value="FIDELITY">Fidelity</option>
							<option value="CONTENT">Content</option>
							<option value="RAINBOW">Rainbow</option>
							<option value="FRUIT_SALAD">Fruit Salad</option>
						</select>
					</div>
				</li>
				<li>
					<div class="w-48">
						<label class="label label-text flex" for="contrast">
							<span class="grow">Contrast: </span>
							<code>{contrast}</code>
						</label>

						<input
							type="range"
							min={contrastMin}
							max={contrastMax}
							step={contrastStep}
							class="range w-full"
							aria-label="contrast"
							id="contrast"
							bind:value={contrast}
						/>
						<!-- <div class="flex w-full justify-between px-2 text-xs">
							{#each allContrasts as _}
								<span>|</span>
							{/each}
						</div> -->
					</div>
				</li>
				<li>
					<hr class="border-outline -mx-2 my-5" />
				</li>
				<li class="flex items-center gap-2">
					<span class="icon-[tabler--settings] size-6"></span>
					<span class="grow"> Settings</span>
				</li>
			</ul>
		</div>
		<div class="flex items-center md:ml-2">
			<button
				class="btn btn-primary btn-outline shadow-primary ml-2 rounded-full shadow-sm"
				aria-label="LogInOut"
			>
				<a href="#top">LogInOut</a>
			</button>
		</div>
	</div>
</nav>

<div id="scrollspy-scrollable-parent" class="grid h-screen overflow-y-auto">
	<aside
		id="collapsible-mini-sidebar"
		class="overlay overlay-minified:w-19 overlay-open:translate-x-0 drawer drawer-start border-base-content/20 hidden w-66 border-e pt-50 [--auto-close:sm] sm:absolute sm:z-0 sm:flex sm:translate-x-0 sm:shadow-none"
		tabindex="-1"
		{@attach initOverlay}
	>
		<div class="drawer-body px-2 pt-4">
			<ul class="menu p-0">
				<li class="text-primary">
					<a href="/">
						<span class="icon-[material-symbols--home-outline-rounded] size-5"></span>
						<span class="overlay-minified:hidden">Home</span>
					</a>
				</li>
				<li class="text-primary md:hidden">
					<a href="/features">
						<span class="icon-[mdi--feature-highlight] size-5"></span>
						<span class="overlay-minified:hidden">Features</span>
					</a>
				</li>
				<li class="text-primary md:hidden">
					<a href="/apps">
						<span class="icon-[tabler--apps] size-5"></span>
						<span class="overlay-minified:hidden">Apps</span>
					</a>
				</li>
				<li class="text-primary md:hidden">
					<a href="/construction">
						<span class="icon-[maki--construction] size-5"></span>
						<span class="overlay-minified:hidden">Construction</span>
					</a>
				</li>
			</ul>
			<div class="divider"></div>
			<ul class="menu p-0">
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
						<span class="icon-[icon-park-outline--page] size-5"></span>
						<span class="overlay-minified:hidden">This page</span>
						<span
							class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:hidden size-4 transition-all duration-300"
						></span>
						<span
							class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:block overlay-minified:rotate-270 hidden size-4 transition-all duration-300"
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
						{@attach initCollapse}
					>
						<span class="icon-[tabler--apps] size-5"></span>
						<span class="overlay-minified:hidden">Page on Apps</span>
						<span
							class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:hidden size-4 transition-all duration-300"
						></span>
						<span
							class="icon-[tabler--chevron-down] collapse-open:rotate-180 overlay-minified:block overlay-minified:rotate-270 hidden size-4 transition-all duration-300"
							role="button"
							tabindex="0"
							onclick={() => openSidebar()}
							onkeydown={() => openSidebar()}
						></span>
					</a>
					<ul
						id="menu-app-collapse"
						class="collapse hidden w-auto space-y-0.5 overflow-hidden transition-[height] duration-300"
						aria-labelledby="menu-app"
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
	<div class="sm:overlay-minified:ps-19 bg-base-100 ps-64 transition-all duration-300 max-sm:ps-0">
		<div class=" bg-base-100 transition-all duration-300">
			<div id="scrollspy" class="space-y-4 pe-1">
				{@render children?.()}
			</div>
		</div>
	</div>
</div>
