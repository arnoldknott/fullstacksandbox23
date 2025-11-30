<script lang="ts">
	import type { Session } from '$lib/types';
	import { type SubmitFunction } from '@sveltejs/kit';
	import { SessionStatus } from '$lib/session';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { enhance } from '$app/forms';
	import { type ArtificialIntelligenceConfig } from '$lib/artificialIntelligence';
	import { Theming, type ColorConfig } from '$lib/theming';
	import ArtificialIntelligencePicker from './playground/components/ArtificialIntelligencePicker.svelte';
	import ThemePicker from './playground/components/ThemePicker.svelte';
	let {
		session = $bindable(),
		artificialIntelligenceConfiguration = $bindable(),
		themeConfiguration = $bindable(),
		mode = $bindable(),
		updateProfileAccount,
		saveProfileAccount
	}: {
		session: Session | undefined;
		artificialIntelligenceConfiguration: ArtificialIntelligenceConfig;
		themeConfiguration: ColorConfig;
		mode: 'light' | 'dark';
		updateProfileAccount: SubmitFunction;
		saveProfileAccount: () => void;
	} = $props();

	let welcomeModal: HTMLDivElement | null = $state(null);

	let userUnregistered = $derived(
		!session?.loggedIn ? false : session.status === SessionStatus.REGISTERED ? false : true
	);

	onMount(() => {
		if (userUnregistered) {
			window.HSOverlay.open(welcomeModal);
		}
	});

	let artificialIntelligenceForm = $state<HTMLFormElement | null>(null);

	const theming = $state(new Theming());

	// TBD: consider using onMount here!
	$effect(() => {
		if (session?.currentUser?.user_profile) {
			session.currentUser.user_profile.theme_color = themeConfiguration.sourceColor;
			session.currentUser.user_profile.theme_variant = themeConfiguration.variant;
			session.currentUser.user_profile.contrast = themeConfiguration.contrast;
		}
	});

	// Write theming to database:
	let themeForm = $state<HTMLFormElement | null>(null);

	// const saveProfileAccount = async () => {
	// 	if (page.data.session?.loggedIn) {
	// 		themeForm?.requestSubmit();
	// 		console.log('=== layout - saveProfileAccount - themeConfiguration ===');
	// 		console.log($state.snapshot(themeConfiguration));
	// 	}
	// };

	// const updateProfileAccount: SubmitFunction = async () => {
	// 	// console.log('=== layout - updateProfileAccount - formData ===');
	// 	// console.log(formData);

	// 	return () => {};
	// };
</script>

<div
	id="welcome-modal"
	class="overlay modal overlay-open:opacity-100 overlay-open:duration-300 modal-middle hidden [--body-scroll:true] [--overlay-backdrop:static]"
	data-overlay-keyboard="false"
	role="dialog"
	tabindex="-1"
	bind:this={welcomeModal}
>
	<div class="modal-dialog modal-dialog-md">
		<div class="modal-content bg-base-300 shadow-outline ring-outline-variant shadow-lg ring">
			<div class="modal-header">
				<span class="icon-[ph--smiley] size-6"></span>
				<h3 class="modal-title grow pl-2">Welcome</h3>
				<div class="align-center flex grow flex-row justify-center">
					{page.data.session?.microsoftProfile.displayName}
				</div>

				<button
					type="button"
					class="btn btn-text btn-circle btn-sm absolute end-3 top-3"
					aria-label="Close"
					data-overlay="#welcome-modal"
				>
					<!-- onclick={() => welcomeModal?.close()} -->
					<span class="icon-[tabler--x] size-4"></span>
				</button>
			</div>
			<div class="modal-body flex flex-wrap justify-between">
				<!-- <div class="w-full"> -->
				<!-- <div
							class="m-1 h-full w-full bg-[url(/starnberger-see-unset-20230807.jpg)] mask-y-from-75% mask-y-to-100% mask-x-from-95% mask-x-to-100% bg-cover bg-center p-4 opacity-40"
						></div> -->

				<div class="align-center flex grow flex-row justify-center">
					<div class="flex flex-col justify-center">
						<div class="title-small text-primary italic" style="line-height: 1;">Fullstack</div>
						<div class="title-small text-secondary font-bold tracking-wide" style="line-height: 1">
							Platform
						</div>
					</div>
					<div class="heading-large navbar-center text-accent ml-1 flex items-center">23</div>
				</div>
				<img
					src="/starnberger-see-unset-20230807.jpg"
					class="w-full rounded-lg mask-y-from-75% mask-y-to-100% mask-x-from-95% mask-x-to-100% opacity-70"
					alt="Bavarian lake Starnberger See in sunset"
				/>
				<div class="m-1 h-full w-full content-center p-4 text-justify font-semibold">
					Adjust your settings for Artificial Intelligence and Theme configuration now or later by
					clicking at your user icon in the top right corner.
					<!-- <p
								class="from-primary via-secondary to-accent text-label w-fit bg-linear-to-b bg-clip-text px-5 text-justify font-semibold text-transparent"
							>
								Adjust your settings for Artificial Intelligence and Theme configuration in the tabs
								now or later by clicking at your user icon in the top right corner.
							</p> -->
				</div>
				<!-- </div> -->
				<div class="grid grid-cols-1 gap-2 max-sm:w-full sm:grid-cols-2">
					<ul
						class="shadow-outline bg-base-250 m-1 h-[257px] w-full rounded rounded-xl p-4 shadow-inner"
						role="menu"
						aria-orientation="vertical"
						aria-labelledby="dropdown-menu-icon-user"
					>
						<ArtificialIntelligencePicker
							{updateProfileAccount}
							{saveProfileAccount}
							bind:artificialIntelligenceForm
							bind:artificialIntelligenceConfiguration
						/>
					</ul>
					<ul
						class="shadow-outline bg-base-250 m-1 h-[257px] w-full rounded rounded-xl p-4 shadow-inner"
						role="menu"
						aria-orientation="vertical"
						aria-labelledby="dropdown-menu-icon-user"
					>
						<ThemePicker
							{updateProfileAccount}
							{saveProfileAccount}
							bind:themeForm
							bind:mode
							bind:themeConfiguration
						/>
					</ul>
				</div>
				<!-- <div
						class="tabs tabs-bordered tabs-vertical w-[130px]"
						aria-label="Tabs"
						role="tablist"
						data-tabs-vertical="true"
						aria-orientation="horizontal"
					>
						<button
							type="button"
							class="tab active-tab:tab-active active py-14 text-left"
							id="welcome-item-ai"
							data-tab="#welcome-ai"
							aria-controls="welcome-ai"
							role="tab"
							aria-selected="false"
						>
							Artificial Intelligence
						</button>
						<button
							type="button"
							class="tab active-tab:tab-active py-14 text-left"
							id="welcome-item-theme"
							data-tab="#welcome-theme"
							aria-controls="welcome-theme"
							role="tab"
							aria-selected="false"
						>
							Theme Configuration
						</button>
					</div>

					<div class="h-[245px] w-[264px]">
						<div id="welcome-ai" role="tabpanel" aria-labelledby="welcome-item-ai">
							<ul
								class="m-1 h-full w-full p-4"
								role="menu"
								aria-orientation="vertical"
								aria-labelledby="dropdown-menu-icon-user"
							>
								<ArtificialIntelligencePicker
									{saveProfileAccount}
									bind:artificialIntelligenceForm
									bind:artificialIntelligenceConfiguration
								/>
							</ul>
						</div>
						<div
							id="welcome-theme"
							class="hidden"
							role="tabpanel"
							aria-labelledby="welcome-item-theme"
						>
							<ul
								class="m-1 w-fit p-4"
								role="menu"
								aria-orientation="vertical"
								aria-labelledby="dropdown-menu-icon-user"
							>
								<ThemePicker
									{saveProfileAccount}
									bind:themeForm
									bind:mode
									bind:themeConfiguration
								/>
							</ul>
						</div>
					</div> -->
			</div>
			<div class="modal-footer">
				<form
					method="POST"
					action="/?/putme"
					use:enhance={async (input) => {
						input.formData.append(
							'ai-enabled',
							artificialIntelligenceConfiguration.enabled.toString()
						);
						input.formData.append('model-picker', artificialIntelligenceConfiguration.model);
						input.formData.append(
							'ai-temperature',
							artificialIntelligenceConfiguration.temperature.toString()
						);
						input.formData.append('color-picker', themeConfiguration.sourceColor);
						input.formData.append('variant-picker', themeConfiguration.variant);
						input.formData.append('contrast', themeConfiguration.contrast.toString());
					}}
				>
					<button
						type="submit"
						onclick={() => (userUnregistered = false)}
						data-overlay="#welcome-modal"
						aria-label="Save profile"
						class="btn btn-primary-container btn-gradient shadow-outline rounded-full shadow-sm"
					>
						<span class="icon-[tabler--send-2]"></span>Save profile
					</button>
				</form>
			</div>
		</div>
	</div>
</div>
