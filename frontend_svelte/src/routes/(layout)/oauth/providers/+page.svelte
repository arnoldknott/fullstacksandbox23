<script lang="ts">
	import { type SubmitFunction } from '@sveltejs/kit';

	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { page } from '$app/state';
	import Title from '$components/Title.svelte';
	import { IdentityProvider } from '$lib/identityProvider';

	import LoginOutButton from '../../LoginOutButton.svelte';
	const session = $derived(page.data.session);
	const authentication = $derived(page.data.providerAuthentication);
	const canUnlinkLinkedIn = $derived(
		Boolean(
			session?.currentUser?.azure_user_id &&
			session.currentUser.linkedin_user_id &&
			authentication.microsoft
		)
	);

	const unlinkLinkedIn: SubmitFunction = ({ cancel }) => {
		if (!confirm('Remove the linked LinkedIn account?')) {
			cancel();
			return;
		}
		return async ({ result, update }) => {
			await update({ reset: false });
			if (result.type === 'success') await invalidateAll();
		};
	};
</script>

<section class="mb-8">
	<Title id="microsoft">Microsoft</Title>
	<div class="flex items-center gap-3">
		<LoginOutButton
			loggedIn={authentication.microsoft}
			linkAccount={Boolean(session?.loggedIn && !session.currentUser?.azure_user_id)}
			provider={IdentityProvider.MICROSOFT}
		/>
		{#if authentication.microsoft && page.data.preferredProvider === IdentityProvider.MICROSOFT}
			<span
				class="icon-[hugeicons--token-circle] text-primary size-6"
				role="img"
				aria-label="Active authentication provider"
				title="Active authentication provider"
			></span>
		{/if}
		{#if session?.currentUser?.azure_user_id}
			<span
				class:text-secondary={authentication.microsoft}
				class:text-base-content={!authentication.microsoft}
				class:opacity-40={!authentication.microsoft}
				class="icon-[material-symbols--link] size-6"
				role="img"
				aria-label={authentication.microsoft
					? 'Linked and authenticated Microsoft account'
					: 'Linked Microsoft account without a valid credential'}
				title={authentication.microsoft
					? 'Linked and authenticated'
					: 'Linked, authentication required'}
			></span>
		{/if}
	</div>
</section>

<section>
	<Title id="linkedIn">LinkedIn</Title>
	<div class="flex items-center gap-3">
		<LoginOutButton
			loggedIn={authentication.linkedin}
			linkAccount={Boolean(session?.loggedIn && !session.currentUser?.linkedin_user_id)}
			provider={IdentityProvider.LINKEDIN}
		/>
		{#if authentication.linkedin && page.data.preferredProvider === IdentityProvider.LINKEDIN}
			<span
				class="icon-[hugeicons--token-circle] text-primary size-6"
				role="img"
				aria-label="Active authentication provider"
				title="Active authentication provider"
			></span>
		{/if}
		{#if session?.currentUser?.linkedin_user_id}
			{#if canUnlinkLinkedIn}
				<form method="POST" action="/?/unlinkaccount" use:enhance={unlinkLinkedIn}>
					<input type="hidden" name="provider" value={IdentityProvider.LINKEDIN} />
					<button
						type="submit"
						class="btn btn-outline btn-secondary btn-circle shadow-neutral shadow-sm"
						aria-label="Unlink LinkedIn account"
						title="Unlink LinkedIn account"
					>
						<span
							class:text-secondary={authentication.linkedin}
							class:text-base-content={!authentication.linkedin}
							class:opacity-40={!authentication.linkedin}
							class="icon-[material-symbols--link] size-6"
						></span>
					</button>
				</form>
			{:else}
				<span
					class:text-secondary={authentication.linkedin}
					class:text-base-content={!authentication.linkedin}
					class:opacity-40={!authentication.linkedin}
					class="icon-[material-symbols--link] size-6"
					role="img"
					aria-label={authentication.linkedin
						? 'Linked and authenticated LinkedIn account'
						: 'Linked LinkedIn account without a valid credential'}
					title={authentication.linkedin
						? 'Linked and authenticated'
						: 'Linked, authentication required'}
				></span>
			{/if}
		{/if}
	</div>
</section>
