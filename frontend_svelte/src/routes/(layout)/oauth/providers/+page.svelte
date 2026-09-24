<script lang="ts">
	import { page } from '$app/state';
	import Title from '$components/Title.svelte';
	import { IdentityProvider } from '$lib/identityProvider';

	import LoginOutButton from '../../LoginOutButton.svelte';
	const session = page.data.session;
</script>

<Title id="microsoft">Microsoft</Title>

<LoginOutButton
	loggedIn={session?.loggedIn === true && session.identityProvider === IdentityProvider.MICROSOFT}
	provider={IdentityProvider.MICROSOFT}
/>

<Title id="linkedIn">LinkedIn</Title>

<LoginOutButton
	loggedIn={session?.loggedIn === true && session.identityProvider === IdentityProvider.LINKEDIN}
	provider={IdentityProvider.LINKEDIN}
/>
