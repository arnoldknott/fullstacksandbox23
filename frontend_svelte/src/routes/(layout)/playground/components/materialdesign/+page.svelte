<script lang="ts">
	import '@material/web/dialog/dialog.js';
	import type { Dialog } from '@material/web/dialog/internal/dialog';
	import '@material/web/textfield/filled-text-field.js';
	import '@material/web/button/filled-button.js';
	import '@material/web/button/filled-tonal-button.js';
	import '@material/web/select/filled-select.js';
	import '@material/web/select/select-option.js';
	import '@material/web/list/list.js';
	import '@material/web/list/list-item.js';
	import '@material/web/labs/card/elevated-card.js';
	import '@material/web/labs/card/filled-card.js';
	import '@material/web/labs/card/outlined-card.js';
	import Title from '$components/Title.svelte';
	import HorizontalRule from '$components/HorizontalRule.svelte';

	let demoResourceDialog: Dialog;
	// let name = $state('');
	// let description = $state('');
	// let language = $state('en-US');
	const cancelForm = (event: Event) => {
		event.preventDefault();
		demoResourceDialog.close();
	};

	type Props = { type: 'login' | 'signup' };
	let { type }: Props = $props();
	const button = type === 'signup' ? 'Sign up' : 'Log in'; // untested!
</script>

<div class="mx-5 grid grid-cols-1 gap-4 xl:grid-cols-2">
	<div>
		<Title>Colors</Title>
		<div class="grid grid-cols-12 gap-4">
			<p class="col-span-12">Sys color primary:</p>
			<div
				class="flex h-12 w-12 items-center justify-center"
				style="background-color: var(--md-sys-color-primary);"
			>
				<p class="text-center text-xl">1</p>
			</div>
			<div
				class="flex h-12 w-12 items-center justify-center"
				style="background-color: var(--md-sys-color-surface-tint);"
			>
				<p class="text-center text-xl">2</p>
			</div>
			<div
				class="flex h-12 w-12 items-center justify-center"
				style="background-color: var(--md-sys-color-on-primary);"
			>
				<p class="text-center text-xl">3</p>
			</div>
			<div
				class="flex h-12 w-12 items-center justify-center"
				style="background-color: var(--md-sys-color-primary-container);"
			>
				<p class="text-center text-xl">4</p>
			</div>
			<div
				class="flex h-12 w-12 items-center justify-center"
				style="background-color: var(--md-sys-color-on-primary-container);"
			>
				<p class="text-center text-xl">5</p>
			</div>
		</div>
	</div>

	<div>
		<Title>Open Modal with dialog</Title>
		<md-filled-button
			onclick={() => demoResourceDialog.show()}
			role="button"
			tabindex="0"
			onkeydown={(event: KeyboardEvent) => event.key === 'Enter' && demoResourceDialog.show()}
			>New</md-filled-button
		>

		<md-dialog id="demoResourceDialog" bind:this={demoResourceDialog} class="w-fill">
			<div slot="headline" class="w-64">Demo Resource</div>
			<form slot="content" id="post-demo-resource" method="POST" class="flex flex-col">
				<md-filled-text-field label="Name" name="name" class="w-full"> </md-filled-text-field>
				<br />
				<md-filled-text-field
					label="Description"
					name="description"
					type="textarea"
					rows="3"
					class="my-3 w-full"
				>
				</md-filled-text-field>
				<md-filled-select label="Language" name="language" class="w-full">
					<md-select-option value="en-US">
						<div slot="headline">en-US</div>
					</md-select-option>
					<md-select-option value="dk-DK">
						<div slot="headline">dk-DK</div>
					</md-select-option>
					<md-select-option value="de-DE">
						<div slot="headline">de-DE</div>
					</md-select-option>
				</md-filled-select>
				<!-- <button>Submit</button> -->
				<!-- <md-filled-button type="submit" role="button" tabindex="0">OK</md-filled-button> -->
				<div slot="actions" class="ml-auto py-4">
					<md-filled-button type="submit" role="button" tabindex="0">OK</md-filled-button>
					<md-filled-tonal-button
						role="button"
						tabindex="0"
						onclick={(event: Event) => cancelForm(event)}
						onkeydown={(event: KeyboardEvent) => event.key === 'Enter' && cancelForm(event)}
						>Cancel</md-filled-tonal-button
					>
				</div>
			</form>
		</md-dialog>

		<HorizontalRule />
	</div>

	<div>
		<Title>User Form</Title>
		<!-- Applying TailwindCSS classes formats the following paragraph: -->
		<p class="text-center text-2xl">
			(Only the text fields are material design - the div's around are tailwind CSS)
		</p>

		<section class="flex h-full w-full justify-center">
			<div class="center py-12 md:w-8/12 lg:ml-6 lg:w-5/12">
				<div class="border-primary-400 rounded-2xl border-4 bg-blue-50 p-6">
					<form method="POST">
						<!-- Name input -->
						{#if type === 'signup'}
							<div class="relative mb-6">
								<md-filled-text-field
									label="Full name"
									type="input"
									name="name"
									role="textbox"
									tabindex="0"
									class="mr-2 w-full"
								>
								</md-filled-text-field>
							</div>
						{/if}

						<!-- Email input -->
						<div class="relative mb-6">
							<md-filled-text-field
								label="Email address"
								type="email"
								name="email"
								role="textbox"
								tabindex="0"
								class="mr-2 w-full"
							>
							</md-filled-text-field>
						</div>

						<!-- Password input -->
						<div class="relative mb-6">
							<md-filled-text-field
								label="Password"
								type="password"
								name="password"
								role="textbox"
								tabindex="0"
								class="mr-2 w-full"
							>
							</md-filled-text-field>
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

		<HorizontalRule />
	</div>

	<div>
		<Title>Card</Title>

		<div class="grid grid-cols-3 gap-4">
			<md-elevated-card>
				<Title>Elevated Card</Title>
				<p class="text-center text-2xl">Not implemented yet in Material Design 3</p>
			</md-elevated-card>
			<md-filled-card>
				<Title>Filled Card</Title>
				<p class="text-center text-2xl">Not implemented yet in Material Design 3</p>
			</md-filled-card>
			<md-outlined-card>
				<Title>Filled Card</Title>
				<p class="text-center text-2xl">Not implemented yet in Material Design 3</p>
			</md-outlined-card>
		</div>

		<HorizontalRule />
	</div>
</div>

<style>
	/* Local override works:  */
	/* #demoResourceDialog {
		--md-dialog-headline-color: #e4a112;
		--md-dialog-container-color: #e5deb9;
	} */
	#post-demo-resource {
		display: flex;
		flex-direction: column;
	}
	#post-demo-resource md-filled-text-field {
		margin-bottom: 1rem;
	}
	#post-demo-resource md-filled-select {
		margin-bottom: 1rem;
	}
	#post-demo-resource md-filled-button {
		margin-top: 1rem;
	}
	#post-demo-resource md-filled-tonal-button {
		margin-top: 1rem;
	}
</style>
