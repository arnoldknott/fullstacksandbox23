<script lang="ts">
	import { onMount } from 'svelte';
	onMount(async () => {
		const te = await import('tw-elements');
		te.initTE(
			{ Input: te.Input, Ripple: te.Ripple },
			{ allowReinits: true, checkOtherImports: true }
		);
	});

	export let type = 'login';
	export let button = type === 'signup' ? 'Sign up' : 'Log in';
</script>

<section class="flex h-full w-full justify-center">
	<div class="center py-12 md:w-8/12 lg:ml-6 lg:w-5/12">
		<div class="rounded-2xl border-4 border-primary-400 bg-blue-50 p-6">
			<form method="POST">
				<!-- Name input -->
				{#if type === 'signup'}
					<div class="relative mb-6" data-te-input-wrapper-init>
						<input
							type="text"
							class="peer block min-h-[auto] w-full rounded bg-transparent px-3 py-[0.32rem] text-lg leading-[2.15] outline-none transition-all duration-200 ease-linear focus:placeholder:opacity-100 data-[te-input-state-active]:placeholder:opacity-100 motion-reduce:transition-none dark:text-neutral-800 dark:placeholder:text-neutral-200 [&:not([data-te-input-placeholder-active])]:placeholder:opacity-0"
							id="nameField"
							name="name"
							placeholder="Full name"
						/>
						<label
							for="nameField"
							class="pointer-events-none absolute left-3 top-0 mb-0 max-w-[90%] origin-[0_0] truncate pt-[0.37rem] leading-[2.15] text-neutral-500 transition-all duration-200 ease-out peer-focus:-translate-y-[1.15rem] peer-focus:scale-[0.8] peer-focus:text-primary peer-data-[te-input-state-active]:-translate-y-[1.15rem] peer-data-[te-input-state-active]:scale-[0.8] motion-reduce:transition-none dark:text-neutral-400 dark:peer-focus:text-primary"
							>Full name
						</label>
					</div>
				{/if}

				<!-- Email input -->
				<div class="relative mb-6" data-te-input-wrapper-init>
					<input
						type="email"
						class="peer block min-h-[auto] w-full rounded bg-transparent px-3 py-[0.32rem] text-lg leading-[2.15] outline-none transition-all duration-200 ease-linear focus:placeholder:opacity-100 data-[te-input-state-active]:placeholder:opacity-100 motion-reduce:transition-none dark:text-neutral-800 dark:placeholder:text-neutral-200 [&:not([data-te-input-placeholder-active])]:placeholder:opacity-0"
						id="emailField"
						name="email"
						placeholder="Email address"
					/>
					<label
						for="emailField"
						class="pointer-events-none absolute left-3 top-0 mb-0 max-w-[90%] origin-[0_0] truncate pt-[0.37rem] leading-[2.15] text-neutral-500 transition-all duration-200 ease-out peer-focus:-translate-y-[1.15rem] peer-focus:scale-[0.8] peer-focus:text-primary peer-data-[te-input-state-active]:-translate-y-[1.15rem] peer-data-[te-input-state-active]:scale-[0.8] motion-reduce:transition-none dark:text-neutral-400 dark:peer-focus:text-primary"
						>Email address
					</label>
				</div>

				<!-- Password input -->
				<div class="relative mb-6" data-te-input-wrapper-init>
					<input
						type="password"
						class="peer block min-h-[auto] w-full rounded bg-transparent px-3 py-[0.32rem] text-lg leading-[2.15] outline-none transition-all duration-200 ease-linear focus:placeholder:opacity-100 data-[te-input-state-active]:placeholder:opacity-100 motion-reduce:transition-none dark:text-neutral-800 dark:placeholder:text-neutral-200 [&:not([data-te-input-placeholder-active])]:placeholder:opacity-0"
						id="passwordField"
						name="password"
						placeholder="Password"
					/>
					<label
						for="passwordField"
						class="pointer-events-none absolute left-3 top-0 mb-0 max-w-[90%] origin-[0_0] truncate pt-[0.37rem] leading-[2.15] text-neutral-500 transition-all duration-200 ease-out peer-focus:-translate-y-[1.15rem] peer-focus:scale-[0.8] peer-focus:text-primary peer-data-[te-input-state-active]:-translate-y-[1.15rem] peer-data-[te-input-state-active]:scale-[0.8] motion-reduce:transition-none dark:text-neutral-400 dark:peer-focus:text-primary"
						>Password
					</label>
				</div>

				<!-- Submit button -->
				<div class="text-center">
					<button
						type="submit"
						class="inline-block w-5/6 rounded bg-blue-400 px-7 pb-2.5 pt-3 uppercase leading-normal text-white shadow-[0_4px_9px_-4px_#3b71ca] transition duration-150 ease-in-out hover:bg-blue-700 hover:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] focus:bg-blue-600 focus:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] focus:outline-none focus:ring-0 active:bg-blue-700 active:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] dark:shadow-[0_4px_9px_-4px_rgba(59,113,202,0.5)] dark:hover:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)] dark:focus:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)] dark:active:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)]"
						data-te-ripple-init
						data-te-ripple-color="light"
					>
						{button}
					</button>
				</div>
			</form>
		</div>
	</div>
</section>
