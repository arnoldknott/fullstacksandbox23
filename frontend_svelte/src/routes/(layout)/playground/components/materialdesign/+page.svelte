<script lang="ts">
	import '@material/web/list/list.js';
	import '@material/web/list/list-item.js';
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
	<div class="col-span-2">
		<Title>Colors</Title>
		<p class="text-center text-2xl">Dynamic colors Material Color Utilities:</p>
		<div class="grid grid-cols-4 gap-4 m-2 w-full">
			<div>
				<div
					class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
					style="background-color: var(--md-sys-color-primary);"
					>
                    <p
						class="text-center text-xl"
						style="color: var(--md-sys-color-on-primary);"
					>
						primary
					</p>
                </div>
                <div
					class="skeleton flex h-12 w-36 xl:w-64 items-center justify-center"
					style="background-color: var(--md-sys-color-on-primary);"
				>
					<p 
						class="text-center text-xl"
						style="color: var(--md-sys-color-primary);"
					>
						on primary
					</p>
                </div>
				<div
					class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
					style="background-color: var(--md-sys-color-primary-container);"
				>
					<p 
						class="text-center text-xl"
						style="color: var(--md-sys-color-on-primary-container);"
					>
						primary container
					</p>
                </div>
				<div
					class="skeleton flex h-12 w-36 xl:w-64 items-center justify-center"
					style="background-color: var(--md-sys-color-on-primary-container);"
				>
					<p 
						class="text-center text-xl"
						style="color: var(--md-sys-color-primary-container);"
					>
						on primary container
					</p>
                </div>
            </div>
            <div>
                <div
					class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
					style="background-color: var(--md-sys-color-secondary);"
					>
                    <p
						class="text-center text-xl"
						style="color: var(--md-sys-color-on-secondary);"
					>
					secondary
					</p>
                </div>
                <div
					class="skeleton flex h-12 w-36 xl:w-64 items-center justify-center"
					style="background-color: var(--md-sys-color-on-secondary);"
				>
					<p 
						class="text-center text-xl"
						style="color: var(--md-sys-color-secondary);"
					>
						on secondary
					</p>
                </div>
				<div
					class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
					style="background-color: var(--md-sys-color-on-secondary-container);"
				>
					<p 
						class="text-center text-xl"
						style="color: var(--md-sys-color-secondary-container);"
					>
					secondary container
					</p>
                </div>
				<div
					class="skeleton flex h-12 w-36 xl:w-64 items-center justify-center"
					style="background-color: var(--md-sys-color-secondary-container);"
				>
					<p 
						class="text-center text-xl"
						style="color: var(--md-sys-color-on-secondary-container);"
					>
						on secondary container
					</p>
                </div>
			</div>
            <div>
                <div
					class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
					style="background-color: var(--md-sys-color-tertiary);"
					>
                    <p
						class="text-center text-xl"
						style="color: var(--md-sys-color-on-tertiary);"
					>
					tertiary
					</p>
                </div>
                <div
					class="skeleton flex h-12 w-36 xl:w-64 items-center justify-center"
					style="background-color: var(--md-sys-color-on-tertiary);"
				>
					<p 
						class="text-center text-xl"
						style="color: var(--md-sys-color-tertiary);"
					>
						on tertiary
					</p>
                </div>
				<div
					class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
					style="background-color: var(--md-sys-color-on-tertiary-container);"
				>
					<p 
						class="text-center text-xl"
						style="color: var(--md-sys-color-tertiary-container);"
					>
					tertiary container
					</p>
                </div>
				<div
					class="skeleton flex h-12 w-36 xl:w-64 items-center justify-center"
					style="background-color: var(--md-sys-color-tertiary-container);"
				>
					<p 
						class="text-center text-xl"
						style="color: var(--md-sys-color-on-tertiary-container);"
					>
						on tertiary container
					</p>
                </div>
			</div>
			<div>
				<div>
					<div
						class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
						style="background-color: var(--md-sys-color-error);"
						>
						<p
							class="text-center text-xl"
							style="color: var(--md-sys-color-on-error);"
						>
							error
						</p>
					</div>
					<div
						class="skeleton flex h-12 w-36 xl:w-64 items-center justify-center"
						style="background-color: var(--md-sys-color-on-error);"
					>
						<p 
							class="text-center text-xl"
							style="color: var(--md-sys-color-error);"
						>
							on error
						</p>
					</div>
					<div
						class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
						style="background-color: var(--md-sys-color-on-error-container);"
					>
						<p 
							class="text-center text-xl"
							style="color: var(--md-sys-color-error-container);"
						>
							error container
						</p>
					</div>
					<div
						class="skeleton flex h-12 w-36 xl:w-64 items-center justify-center"
						style="background-color: var(--md-sys-color-error-container);"
					>
						<p 
							class="text-center text-xl"
							style="color: var(--md-sys-color-on-error-container);"
						>
							on error container
						</p>
					</div>
				</div>
			</div>
        </div>
		<div class="grid grid-cols-5 gap-4 m-2 w-full">
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-surface-container-lowest);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-on-surface);"
				>
					surface container lowest
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-surface-container-low);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-on-surface);"
				>
					surface container low
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-surface-container);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-on-surface);"
				>
					surface container
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-surface-container-high);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-on-surface);"
				>
					surface container high
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-surface-container-highest);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-on-surface);"
				>
					surface container highest
				</p>
			</div>
		</div>
		<div class="grid grid-cols-4 gap-4 m-2 w-full">
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-on-surface);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-inverse-on-surface);"
				>
					on surface
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-surface-variant);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-on-surface);"
				>
					on surface variant
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-outline);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-inverse-on-surface);"
				>
					outline
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-outline-variant);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-inverse-on-surface);"
				>
					outline variant
				</p>
			</div>
		</div>
		<div class="grid grid-cols-5 gap-4 m-2 w-full">
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-inverse-surface);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-inverse-on-surface);"
				>
					inverse surface
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-inverse-on-surface);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-on-surface);"
				>
					inverse on surface variant
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-inverse-primary);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-on-surface);"
				>
					inverse primary
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-scrim);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-on-surface);"
				>
					scrim
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-shadow);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-on-surface);"
				>
					shadow
				</p>
			</div>
		</div>
		<div class="grid grid-cols-4 gap-4 m-2 w-full">
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-background);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-on-background);"
				>
					background
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-on-background);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-background);"
				>
					on background
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-neutral-palette-key-color);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-inverse-on-surface);"
				>
					neutral palette key color
				</p>
			</div>
			<div
				class="skeleton flex h-24 w-36 xl:w-64 items-center justify-center"
				style="background-color: var(--md-sys-color-neutral-variant-palette-key-color);"
				>
				<p
					class="text-center text-xl"
					style="color: var(--md-sys-color-inverse-on-surface);"
				>
					neutral variant palette key color
				</p>
			</div>
		</div>
		<HorizontalRule />
	</div>

	<!-- <div class="staticMaterialThemeBuilder">
		<Title>Colors</Title>
		<p class="text-center text-2xl">
			(static generated on Material Theme Builder homepage and exported as css variables)
		</p>
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
		<HorizontalRule />
	</div> -->

	<div>
		<Title>List</Title>
		<md-list style="max-width: 300px;">
			<md-list-item> Fruits </md-list-item>
			<md-divider></md-divider>
			<md-list-item> Apple </md-list-item>
			<md-list-item> Banana </md-list-item>
			<md-list-item>
				<div slot="headline">Cucumber</div>
				<div slot="supporting-text">
					Cucumbers are long green fruits that are just as long as this multi-line description
				</div>
			</md-list-item>
			<md-list-item
				type="link"
				href="https://google.com/search?q=buy+kiwis&tbm=shop"
				target="_blank"
			>
				<div slot="headline">Shop for Kiwis</div>
				<div slot="supporting-text">This will link you out in a new tab</div>
				<md-icon slot="end">open_in_new</md-icon>
			</md-list-item>
		</md-list>
		<HorizontalRule />
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
	/* .staticMaterialThemeBuilder {
		@import './dark.css';
		@import './dark-hc.css';
		@import './dark-mc.css';
		@import './light.css';
		@import './light-hc.css';
		@import './light-mc.css';
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
