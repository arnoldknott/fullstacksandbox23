<script lang="ts">
	import { page } from '$app/state';
	import Title from '$components/Title.svelte';
	import { IdentityProvider } from '$lib/identityProvider';

	import LoginOutButton from '../../LoginOutButton.svelte';
	const session = page.data.session;
	const authentication = page.data.providerAuthentication;
</script>

<section class="mb-8">
	<Title id="microsoft">Microsoft</Title>
	<div class="flex items-center gap-3">
		<LoginOutButton loggedIn={authentication.microsoft} provider={IdentityProvider.MICROSOFT} />
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
		<LoginOutButton loggedIn={authentication.linkedin} provider={IdentityProvider.LINKEDIN} />
		{#if authentication.linkedin && page.data.preferredProvider === IdentityProvider.LINKEDIN}
			<span
				class="icon-[hugeicons--token-circle] text-primary size-6"
				role="img"
				aria-label="Active authentication provider"
				title="Active authentication provider"
			></span>
		{/if}
		{#if session?.currentUser?.linkedin_user_id}
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
	</div>
</section>
