<nav class="navbar rounded-box bg-base-100 shadow">
	<div class="w-full md:flex md:items-center md:gap-2">
		<div class="flex items-center justify-between">
			<div class="navbar-start items-center justify-between max-md:w-full">
				<a class="link link-neutral text-xl font-semibold text-base-content no-underline" href="#top"
					>FullStackSandbox23</a
				>
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
			class="collapse hidden grow basis-full overflow-hidden transition-[height] duration-300 md:navbar-end max-md:w-full"
		>
			<ul class="menu gap-2 p-0 text-base md:menu-horizontal max-md:mt-2">
				<li><a href="#top">Home</a></li>
				<li><a href="#top">Docs</a></li>
				<li><a href="#top">Playground</a></li>
			</ul>
		</div>
	</div>
</nav>
