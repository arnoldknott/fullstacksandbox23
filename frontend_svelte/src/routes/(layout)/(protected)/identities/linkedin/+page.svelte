<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import JsonData from '$components/JsonData.svelte';

	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const userProfile = $derived(data.session?.linkedinProfile);
	const authentication = $derived({
		identityProvider: data.session?.identityProvider,
		subject: data.session?.linkedinProfile?.sub
	});
</script>

<Heading id="my-user-data-in-linkedin">My user data in LinkedIn</Heading>

{#if userProfile}
	{#if userProfile.picture}
		<div class="mb-5 flex max-w-sm flex-col gap-3">
			<img
				class="aspect-square w-40 rounded-full object-cover"
				src={userProfile.picture}
				alt={userProfile.name ? userProfile.name + "'s LinkedIn profile" : 'LinkedIn profile'}
			/>
			<p class="body-large">This picture comes from LinkedIn UserInfo.</p>
		</div>
	{/if}

	<Heading id="linkedin-userinfo">LinkedIn UserInfo</Heading>
	<JsonData data={userProfile} />
{:else}
	<p class="body-large">
		No LinkedIn UserInfo is available for the active identity-provider session.
	</p>
{/if}

<Heading id="linkedin-login">LinkedIn login</Heading>
<code><pre>{JSON.stringify(authentication, null, ' ')}</pre></code>
