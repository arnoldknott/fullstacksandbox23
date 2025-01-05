<div class="flex flex-row">
	<div class="flex grow flex-col gap-4">
		<div class="relative min-w-56">
			<input
				type="text"
				placeholder="Add your input here"
				class="input input-filled peer border-primary"
				id="primaryInput"
			/>
			<label
				class="text-label-small md:text-label input-filled-label input-filled-label-primary"
				style="color: oklch(var(--p));"
				for="primaryInput">Full Name</label
			>
			<span class="input-filled-focused" style="background-color: oklch(var(--p));"></span>
		</div>
		<div class="relative min-w-56">
			<input type="text" placeholder="John Doe" class="input input-floating peer" id="floatingInput" />
			<label class="input-floating-label input-floating-label-primary" for="floatingInput">Full name</label>
		</div>
		<button
			class="text-label-small md:text-label btn btn-primary max-w-52 rounded-full bg-primary text-primary-content"
			>Primary</button
		>
		<button
			class="btn-primary-container text-label-small lg:text-label btn max-w-52 rounded-3xl max-lg:h-16 lg:rounded-full"
			>Primary Container</button
		>
	</div>
	<div class="divider-outline-variant divider divider-horizontal"></div>
	<div class="flex grow flex-col gap-4">
		<div class="relative min-w-56">
			<input
				type="text"
				placeholder="Add your input here"
				class="input input-filled peer border-secondary"
				id="secondaryInput"
			/>
			<label
				class="text-label-small md:text-label input-filled-label"
				style="color: oklch(var(--s));"
				for="secondaryInput">Full Name</label
			>
			<span class="input-filled-focused" style="background-color: oklch(var(--s));"></span>
		</div>
		<button
			class="text-label-small md:text-label btn btn-secondary max-w-52 rounded-full bg-secondary text-secondary-content"
			>Secondary</button
		>
		<button
			class="btn-secondary-container text-label-small lg:text-label btn max-w-52 rounded-3xl max-lg:h-16 lg:rounded-full"
			>Secondary Container</button
		>
	</div>
	<div class="divider-outline-variant divider divider-horizontal"></div>
	<div class="flex grow flex-col gap-4">
		<div class="relative min-w-56">
			<input
				type="text"
				placeholder="Add your input here"
				class="input input-filled peer border-accent"
				id="accentInput"
			/>
			<label
				class="text-label-small md:text-label input-filled-label input-filled-label-accent"
				style="color: oklch(var(--a));"
				for="accentInput">Full Name</label
			>
			<span class="input-filled-focused" style="background-color: oklch(var(--a));"></span>
		</div>
		<div class="relative min-w-56">
			<input type="text" placeholder="John Doe" class="input input-floating input-floating-accent peer border-accent" id="floatingInput" />
			<label class="input-floating-label input-floating-label-accent" style="color: oklch(var(--a));" for="floatingInput">Full name</label>
		</div>
		<button
			class="text-label-small md:text-label btn btn-accent max-w-52 rounded-full bg-accent text-accent-content"
			>Accent</button
		>
		<button
			class="btn-accent-container text-label-small lg:text-label btn max-w-52 rounded-3xl max-lg:h-16 lg:rounded-full"
			>Accent Container</button
		>
	</div>
	<div class="divider-outline-variant divider divider-horizontal"></div>
	<div class="flex grow flex-col gap-4">
		<div class="relative min-w-56">
			<input
				type="text"
				placeholder="Add your input here"
				class="input input-filled peer border-neutral"
				id="accentInput"
			/>
			<label
				class="text-label-small md:text-label input-filled-label text-neutral"
				style="color: oklch(var(--n));"
				for="accentInput">Full Name</label
			>
			<span class="input-filled-focused" style="background-color: oklch(var(--n));"></span>
		</div>
		<button
			class="btn-neutral text-label-small md:text-label btn max-w-52 rounded-full bg-neutral text-neutral-content"
			>Neutral</button
		>
		<button
			class="btn-neutral-container text-label-small lg:text-label btn max-w-52 rounded-3xl max-lg:h-16 lg:rounded-full"
			>Neutral Container</button
		>
	</div>
</div>
