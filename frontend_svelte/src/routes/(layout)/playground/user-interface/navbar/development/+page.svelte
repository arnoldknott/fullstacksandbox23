<script lang="ts">
	import { initDropdown } from '$lib/userInterface';
	let mode: 'light' | 'dark' = $state('dark');
	const toggleMode = () => {
		mode = mode === 'dark' ? 'light' : 'dark';
	};
	// for theme picker:
	let sourceColor = $state('#769CDF');
	let variant = $state('TONAL_SPOT');
	const contrastMin = -1.0;
	const contrastMax = 1.0;
	const contrastStep = 0.2;
	// const allContrasts = Array.from(
	// 	{ length: (contrastMax - contrastMin) / contrastStep + 1 },
	// 	(_, i) => contrastMin + i * contrastStep
	// );
	let contrast = $state(0.0);
</script>

<nav
	class="navbar rounded-box bg-base-100 sticky start-0 top-[0px] z-1 shadow-sm md:flex md:items-stretch"
>
	<div class="navbar-start">A</div>
	<div class="navbar-center">B</div>
	<div class="navbar-end">C</div>
</nav>

<div class="h-4"></div>

<nav
	class="navbar rounded-box bg-base-100 shadow-shadow border-outline-variant sticky start-0 top-[50px] z-1 border-b shadow-sm md:flex md:items-stretch"
>
	<div class="w-full md:flex md:items-center md:gap-2">
		<div class="flex items-center justify-between">
			<div class="navbar-start items-center justify-between max-md:w-full">
				<div class="md:hidden">
					<button
						type="button"
						class="btn btn-square btn-neutral btn-outline collapse-toggle btn-sm"
						data-collapse="#default-navbar-menu-collapse"
						aria-controls="default-navbar-menu-collapse"
						aria-label="Toggle navigation"
					>
						<span class="icon-[tabler--menu-2] bg-neutral collapse-open:hidden size-4"></span>
						<span class="icon-[tabler--x] bg-neutral collapse-open:block hidden size-4"></span>
					</button>
				</div>
			</div>
		</div>

		<div
			id="default-navbar-menu-collapse"
			class="md:navbar-start collapse hidden grow basis-full overflow-hidden transition-[height] duration-300 max-md:w-full"
		>
			<ul class="menu md:menu-horizontal text-neutral p-0 max-md:mt-2">
				<li>
					<a href="#top" aria-label="Home"
						><span class="icon-[material-symbols--home-outline-rounded] bg-neutral size-6"
						></span></a
					>
				</li>
				<li><a href="#top" class="text-neutral">Docs</a></li>
				<li><a href="#top" class="text-neutral">Playground</a></li>
				<hr class="border-outline -mx-2 my-3" />
				<li><a href="#top" class="text-neutral">Dashboard</a></li>
			</ul>
		</div>
	</div>
	<div class="navbar-center flex flex-col justify-center">
		<div class="title-small text-primary italic" style="line-height: 1;">Fullstack</div>
		<div class="title-small text-secondary font-bold tracking-wide" style="line-height: 1">
			Platform
		</div>
	</div>
	<div class="heading-large navbar-center text-accent ml-1 flex items-center">23</div>
	<div
		class="dropdown navbar-end flex items-center [--auto-close:inside] rtl:[--placement:bottom-end]"
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
			class="dropdown-menu bg-base-200 text-neutral shadow-outline dropdown-open:opacity-100 hidden shadow-md"
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
	<div class="navabar-end flex items-center md:ml-2">
		<button
			class="btn btn-neutral btn-outline shadow-neutral ml-2 rounded-full shadow-sm"
			aria-label="LogInOut"
		>
			<a href="#top">LogInOut</a>
		</button>
	</div>

	<!-- <div class="self-start pt-2">
		<a
			class="link link-neutral text-xl font-semibold text-base-content no-underline"
			href="#top"
			aria-label="User"
		>
			<span class="icon-[fa6-solid--user] size-6"></span>
		</a>
	</div> -->
</nav>

<div class="h-96"></div>

<nav
	class="navbar rounded-box bg-base-100 shadow-shadow border-outline-variant sticky start-0 top-[800px] z-1 justify-between border-b shadow-sm md:flex md:items-stretch"
>
	<div class="dropdown navbar-start relative inline-flex md:hidden rtl:[--placement:bottom-end]">
		<button
			type="button"
			class="dropdown-toggle btn btn-square btn-neutral btn-outline btn-sm"
			data-collapse="#default-navbar-dropdown"
			aria-controls="default-navbar-dropdown"
			aria-label="Toggle navigation"
		>
			<span class="icon-[tabler--menu-2] bg-neutral dropdown-open:hidden size-4"></span>
			<span class="icon-[tabler--x] bg-neutral dropdown-open:block hidden size-4"></span>
		</button>
		<!-- <div
			id="default-navbar-dropdown"
			class="collapse hidden grow basis-full overflow-hidden transition-[height] duration-300 w-full md:flex md:items-center"
		> -->
		<ul
			class="dropdown-menu bg-base-200 shadow-outline dropdown-open:opacity-100 hidden text-base shadow-md"
			aria-labelledby="default-navbar-dropdown"
		>
			<li class="dropdown-item">
				<a href="#top" aria-label="Home"
					><span class="icon-[material-symbols--home-outline-rounded] bg-neutral size-6"></span></a
				>
			</li>
			<li class="dropdown-item"><a href="#top" class="text-neutral">Docs</a></li>
			<li class="dropdown-item"><a href="#top" class="text-neutral">Playground</a></li>
			<hr class="border-outline -mx-2 my-3" />
			<li class="dropdown-item"><a href="#top" class="text-neutral">Dashboard</a></li>
		</ul>
		<!-- </div> -->
	</div>
	<div class="navbar-start hidden items-center md:flex">
		<ul class="menu-horizontal flex items-center md:gap-4">
			<li>
				<a href="#top" aria-label="Home"
					><span class="icon-[material-symbols--home-outline-rounded] bg-neutral size-6"></span></a
				>
			</li>
			<li><a href="#top" class="text-neutral">Docs</a></li>
			<li><a href="#top" class="text-neutral">Playground</a></li>
			<hr class="border-outline -mx-2 my-3" />
			<li><a href="#top" class="text-neutral">Dashboard</a></li>
		</ul>
	</div>
	<!-- <div class="w-full md:flex md:items-center md:gap-2">
		<div class="flex items-center justify-between">
			<div class="navbar-start items-center justify-between max-md:w-full">
				<div class="md:hidden">
					<button
						type="button"
						class="btn btn-square btn-secondary btn-outline collapse-toggle btn-sm"
						data-collapse="#default-navbar-collapse"
						aria-controls="default-navbar-collapse"
						aria-label="Toggle navigation"
					>
						<span class="icon-[tabler--menu-2] size-4 collapse-open:hidden"></span>
						<span class="icon-[tabler--x] hidden size-4 collapse-open:block"></span>
					</button>
				</div>
			</div>
		</div>

		<div
			id="default-navbar-collapse"
			class="collapse hidden grow basis-full overflow-hidden transition-[height] duration-300 md:navbar-start max-md:w-full"
		>
			<ul class="menu p-0 text-base md:menu-horizontal max-md:mt-2">
				<li>
					<a href="#top" aria-label="Home"
						><span class="bg-primary icon-[material-symbols--home-outline-rounded] size-6"></span></a
					>
				</li>
				<li><a href="#top" class="text-primary">Docs</a></li>
				<li><a href="#top" class="text-primary">Playground</a></li>
				<hr class="-mx-2 my-3 border-outline" />
				<li><a href="#top" class="text-primary">Dashboard</a></li>
			</ul>
		</div>
	</div> -->
	<div class="navbar-center flex flex-row">
		<div class="flex flex-col justify-center">
			<div class="title-small text-primary italic" style="line-height: 1;">Fullstack</div>
			<div class="title-small text-secondary font-bold tracking-wide" style="line-height: 1">
				Platform
			</div>
		</div>
		<div class="heading-large navbar-center text-accent ml-1 flex items-center">23</div>
	</div>
	<div class="navbar-end">
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
				class="dropdown-menu bg-base-200 text-neutral shadow-outline dropdown-open:opacity-100 hidden shadow-md"
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
				class="btn btn-neutral btn-outline shadow-neutral ml-2 rounded-full shadow-sm"
				aria-label="LogInOut"
			>
				<a href="#top">LogInOut</a>
			</button>
		</div>
	</div>

	<!-- <div class="self-start pt-2">
		<a
			class="link link-neutral text-xl font-semibold text-base-content no-underline"
			href="#top"
			aria-label="User"
		>
			<span class="icon-[fa6-solid--user] size-6"></span>
		</a>
	</div> -->
</nav>
